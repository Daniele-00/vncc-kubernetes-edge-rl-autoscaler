import subprocess
import time
import requests
import csv
import os
import json
import numpy as np
from datetime import datetime
from reward_utils import reward_function # Importa la funzione di reward

# --- CONFIGURAZIONE ---
MINIKUBE_IP = os.getenv("MINIKUBE_IP", "192.168.49.2")
URL = f"http://{MINIKUBE_IP}:30080/"
CONFIG_FILE = "autoscaler_config.json"

# Questi verranno eventualmente sovrascritti in base alla modalità (train/eval)
LOG_FILE = "results/rl_log.csv"

# Nuovo: modalità RL e percorso Q-table
RL_MODE = os.getenv("RL_MODE", "train").lower()   # "train" oppure "eval"
QTABLE_PATH = os.getenv("QTABLE_PATH", "results/qtable.npy")


# LIMITI
MIN_PODS = 1
MAX_PODS = 5 
NUM_REQ = 20

# AZIONI: -1 (Down), 0 (Hold), +1 (Up)
ACTIONS = [-1, 0, 1] 

# --- PARAMETRI RL AVANZATI (Decay) ---
alpha = 0.1    
gamma = 0.9    

# Epsilon-Greedy parameters
EPSILON_START = 0.9
EPSILON_MIN   = 0.1
EPSILON_DECAY = 0.985
# Inizializza epsilon
epsilon      = EPSILON_START
epsilon_min  = EPSILON_MIN
epsilon_decay = EPSILON_DECAY


def get_replicas():
    try:
        out = subprocess.check_output(["kubectl", "get", "deploy", "edge-app", "-o", "jsonpath={.spec.replicas}"])
        return int(out.decode())
    except:
        return 1

def set_replicas(n):
    n = max(MIN_PODS, min(MAX_PODS, n))
    subprocess.run(["kubectl", "scale", "deploy/edge-app", f"--replicas={n}"], check=True, stdout=subprocess.DEVNULL)
    return n

def wait_for_deployment_ready():
    try:
        subprocess.run(
            ["kubectl", "rollout", "status", "deployment/edge-app", "--timeout=30s"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        time.sleep(2)
    except:
        pass

def measure_latency(num_requests=NUM_REQ):
    latencies = []
    for _ in range(num_requests):
        start = time.time()
        try:
            requests.get(URL, timeout=1.0)
            latencies.append(time.time() - start)
        except:
            latencies.append(1.0)
        time.sleep(0.05) 
    return sum(latencies) / len(latencies) if latencies else 1.0

def latency_bucket(lat, low, high):
    if lat < low: return 0 
    elif lat < high: return 1 
    else: return 2 


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)

    # Scegliamo il file di log in base alla modalità
    if RL_MODE == "train":
        LOG_FILE = "results/rl_train_log.csv"
    else:
        LOG_FILE = "results/rl_eval_log.csv"

    # Spazio di stati / azioni
    n_latency_states = 3
    n_replica_states = MAX_PODS
    n_states = n_latency_states * n_replica_states
    n_actions = len(ACTIONS)

    # Inizializza Q-table
    Q = np.zeros((n_states, n_actions))

    # Se esiste già una Q-table, la carichiamo (utile per continuare il training o per eval)
    if os.path.exists(QTABLE_PATH):
        try:
            Q_loaded = np.load(QTABLE_PATH)
            if Q_loaded.shape == Q.shape:
                Q = Q_loaded
                print(f"📂 Caricata Q-table da {QTABLE_PATH} con shape {Q.shape}")
            else:
                print(f"⚠️ Q-table su disco ha shape {Q_loaded.shape}, mi aspettavo {Q.shape}: la ignoro.")
        except Exception as e:
            print(f"⚠️ Impossibile caricare Q-table ({e}), parto da zero.")

    # Header file di log
    with open(LOG_FILE, "w", newline="") as f:
        csv.writer(f).writerow(["timestamp", "episode", "latency", "replicas", "reward", "epsilon"])

    def state_index(lat_bucket, replicas):
        return lat_bucket * n_replica_states + (replicas - 1)

    # Configura epsilon in base alla modalità
    if RL_MODE == "train":
        print(f" Avvio RL Autoscaler in modalità TRAIN (epsilon {epsilon:.2f} → {epsilon_min:.2f})")
    else:
        epsilon = 0.0
        epsilon_min = 0.0
        epsilon_decay = 1.0
        print(f" Avvio RL Autoscaler in modalità EVAL (epsilon fisso {epsilon:.2f})")

    # Repliche iniziali
    current_replicas = get_replicas()
    if current_replicas < MIN_PODS:
        current_replicas = set_replicas(MIN_PODS)

    episode = 0

    while True:
        # 1. Config (soglie da dashboard, se presente)
        CURRENT_LOW_THR = 0.25
        CURRENT_HIGH_THR = 0.35
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    conf = json.load(f)
                    CURRENT_LOW_THR = conf.get("low", 0.25)
                    CURRENT_HIGH_THR = conf.get("high", 0.35)
            except:
                pass

        # 2. Stato corrente
        lat = measure_latency(num_requests=10)
        lb = latency_bucket(lat, CURRENT_LOW_THR, CURRENT_HIGH_THR)
        s = state_index(lb, current_replicas)

        # 3. Scelta azione (epsilon-greedy)
        if np.random.rand() < epsilon:
            a_idx = np.random.randint(n_actions)
            action_type = "explore"
        else:
            a_idx = np.argmax(Q[s])
            action_type = "exploit"

        action_val = ACTIONS[a_idx]

        # 4. Applica scaling
        new_replicas = current_replicas + action_val
        new_replicas = max(MIN_PODS, min(MAX_PODS, new_replicas))

        if new_replicas != current_replicas:
            print(f"🔄 Scaling: {current_replicas} -> {new_replicas}")
            set_replicas(new_replicas)
            time.sleep(2)
            current_replicas = new_replicas

        # 5. Osserva nuovo stato + reward
        lat2 = measure_latency(num_requests=10)
        lb2 = latency_bucket(lat2, CURRENT_LOW_THR, CURRENT_HIGH_THR)
        s2 = state_index(lb2, current_replicas)
        r = reward_function(lat2, current_replicas, CURRENT_LOW_THR, CURRENT_HIGH_THR, action_val)

        # 6. Aggiornamento Q-table SOLO in TRAIN
        if RL_MODE == "train":
            Q[s, a_idx] = Q[s, a_idx] + alpha * (r + gamma * np.max(Q[s2]) - Q[s, a_idx])

            epsilon = max(epsilon_min, epsilon * epsilon_decay)


            # Salva periodicamente la Q-table
            if episode % 10 == 0:
                np.save(QTABLE_PATH, Q)
        # In eval non modifichiamo Q (policy fissa)

        print(f"Ep {episode}: Lat={lat2:.3f}s | Rep={current_replicas} | Rew={r:.2f} | Eps={epsilon:.2f} ({action_type})")

        # 7. Log
        with open(LOG_FILE, "a", newline="") as f:
            csv.writer(f).writerow([datetime.now(), episode, lat2, current_replicas, r, epsilon])

        episode += 1
        
        print("⏳ ...", end="\r")
        time.sleep(3)  # Sincronizzazione Loop
