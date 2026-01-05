import numpy as np
import subprocess
import time
import statistics
import requests
import csv
import os
import json # <--- Importante
from datetime import datetime

# --- CONFIGURAZIONE INIZIALE ---
MINIKUBE_IP = os.getenv("MINIKUBE_IP", "192.168.49.2")
URL = f"http://{MINIKUBE_IP}:30080/"
CONFIG_FILE = "autoscaler_config.json"

MIN_PODS = 1
MAX_PODS = 4
ACTIONS = [0, 1, 2]  # 0=giù, 1=stop, 2=su

# Valori di default (verranno sovrascritti dalla dashboard)
CURRENT_LOW_THR = 0.08
CURRENT_HIGH_THR = 0.20

def get_replicas():
    try:
        out = subprocess.check_output(
            ["kubectl", "get", "deploy", "edge-app", "-o", "jsonpath={.spec.replicas}"]
        )
        return int(out.decode())
    except:
        return 1

def set_replicas(n):
    n = max(MIN_PODS, min(MAX_PODS, n))
    subprocess.run(
        ["kubectl", "scale", "deploy/edge-app", f"--replicas={n}"],
        check=True
    )
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

def measure_latency(num_requests=30):
    latencies = []
    for _ in range(num_requests):
        start = time.time()
        try:
            r = requests.get(URL, timeout=2)
            r.raise_for_status()
            latencies.append(time.time() - start)
        except Exception:
            latencies.append(2.0)
    return statistics.mean(latencies)

# Le funzioni ora accettano le soglie come parametri!
def latency_bucket(lat, low_t, high_t):
    if lat < low_t:
        return 0  # Bassa
    elif lat < high_t:
        return 1  # Media
    else:
        return 2  # Alta (SCALARE!)

def reward_function(lat, replicas, low_t, high_t):
    r = 0.0
    if lat < low_t:
        r += 5
    elif lat < high_t:
        r += 2
    else:
        r -= 5  # Penalità forte
    
    r -= (replicas - 1) * 1.0
    return r

if __name__ == "__main__":
    n_latency_states = 3
    n_replica_states = MAX_PODS 
    n_states = n_latency_states * n_replica_states
    n_actions = len(ACTIONS)

    Q = np.zeros((n_states, n_actions))

    alpha = 0.1
    gamma = 0.9
    epsilon = 0.2 

    current_replicas = set_replicas(1)
    wait_for_deployment_ready()
    
    log_file = "results/rl_log.csv"
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "episode", "latency", "replicas", "reward"])

    def state_index(lat_bucket, replicas):
        return lat_bucket * n_replica_states + (replicas - 1)

    print(f"🚀 Avvio RL Autoscaler con Configurazione Dinamica")
    
    episode = 0
    while True:
        # --- LEGGI CONFIGURAZIONE DALLA DASHBOARD ---
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    conf = json.load(f)
                    CURRENT_LOW_THR = conf.get("low", 0.08)
                    CURRENT_HIGH_THR = conf.get("high", 0.20)
            except:
                pass # Se il file è bloccato o corrotto, usa i vecchi valori

        # 1. Misura
        lat = measure_latency(num_requests=40)
        
        # Passiamo le soglie dinamiche!
        lb = latency_bucket(lat, CURRENT_LOW_THR, CURRENT_HIGH_THR)
        s = state_index(lb, current_replicas)

        # 2. Azione
        if np.random.rand() < epsilon:
            a = np.random.choice(n_actions)
        else:
            a = np.argmax(Q[s])

        # 3. Attuazione
        delta = [-1, 0, 1][a]
        new_replicas = current_replicas + delta
        new_replicas = max(MIN_PODS, min(MAX_PODS, new_replicas))

        if new_replicas != current_replicas:
            print(f"🔄 Scaling: {current_replicas} -> {new_replicas} (Soglie: {CURRENT_LOW_THR}/{CURRENT_HIGH_THR})")
            set_replicas(new_replicas)
            wait_for_deployment_ready()

        # 4. Nuovo stato
        lat2 = measure_latency(num_requests=40)
        lb2 = latency_bucket(lat2, CURRENT_LOW_THR, CURRENT_HIGH_THR)
        s2 = state_index(lb2, new_replicas)
        r = reward_function(lat2, new_replicas, CURRENT_LOW_THR, CURRENT_HIGH_THR)

        # 5. Update Q
        Q[s, a] = Q[s, a] + alpha * (r + gamma * np.max(Q[s2]) - Q[s, a])

        current_replicas = new_replicas

        # Stampa log con le soglie attuali per debug
        print(f"Ep {episode}: Lat={lat2:.3f}s | Thr={CURRENT_HIGH_THR}s | Reward={r:.2f}")
        
        with open(log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), episode, lat2, current_replicas, r])
            
        episode += 1