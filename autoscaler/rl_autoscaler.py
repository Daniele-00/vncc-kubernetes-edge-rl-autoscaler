import numpy as np
import subprocess
import time
import statistics
import requests
import csv
from datetime import datetime
import os


MIN_PODS = 1
MAX_PODS = 4
ACTIONS = [0, 1, 2]  # 0=giù, 1=stop, 2=su

# Deinfizione dell'URL del servizio
MINIKUBE_IP = os.getenv("MINIKUBE_IP", "192.168.49.2") # Per test sostituire con IP minikube corretto
URL = f"http://{MINIKUBE_IP}:30080/"

def get_replicas():
    out = subprocess.check_output(
        ["kubectl", "get", "deploy", "edge-app",
         "-o", "jsonpath={.spec.replicas}"]
    )
    return int(out.decode())

def set_replicas(n):
    n = max(MIN_PODS, min(MAX_PODS, n))
    subprocess.run(
        ["kubectl", "scale", f"deploy/edge-app", f"--replicas={n}"],
        check=True
    )
    return n

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

def latency_bucket(lat):
    if lat < 0.08:
        return 0  # bassa
    elif lat < 0.2:
        return 1  # media
    else:
        return 2  # alta

def reward_function(lat, replicas):
    r = 0.0
    if lat < 0.08:
        r += 5
    elif lat < 0.2:
        r += 2
    else:
        r -= 5
    r -= (replicas - 1) * 1.0
    return r

def wait_for_deployment_ready():
    """
    Blocca l'esecuzione finché tutti i pod del deployment non sono
    nello stato 'Ready'.
    """
    print("Attendo stabilizzazione dei Pod...")
    try:
        # kubectl rollout status esce solo quando il deployment è completato
        subprocess.run(
            ["kubectl", "rollout", "status", "deployment/edge-app", "--timeout=30s"],
            check=True,
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        # Piccola pausa extra per sicurezza
        time.sleep(2)
    except subprocess.CalledProcessError:
        print("⚠️ Warning: Il deployment ci sta mettendo troppo tempo!")

if __name__ == "__main__":
    n_latency_states = 3
    n_replica_states = MAX_PODS  # 1..MAX_PODS
    n_states = n_latency_states * n_replica_states
    n_actions = len(ACTIONS)

    Q = np.zeros((n_states, n_actions))

    alpha = 0.1
    gamma = 0.9
    epsilon = 0.2

    current_replicas = set_replicas(1)
    time.sleep(5)
    log_file = "results/rl_log.csv"
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "episode", "latency", "replicas", "reward"])

    def state_index(lat_bucket, replicas):
        return lat_bucket * n_replica_states + (replicas - 1)

    for episode in range(50):
        lat = measure_latency(num_requests=40)
        lb = latency_bucket(lat)
        s = state_index(lb, current_replicas)

        if np.random.rand() < epsilon:
            a = np.random.choice(n_actions)
        else:
            a = np.argmax(Q[s])

        delta = [-1, 0, 1][a]
        new_replicas = current_replicas + delta
        new_replicas = max(MIN_PODS, min(MAX_PODS, new_replicas))

        if new_replicas != current_replicas:
            print(f"Scaling: {current_replicas} -> {new_replicas} repliche")
            set_replicas(new_replicas)
            
            # Chiamata alla funzione di attesa
            wait_for_deployment_ready() 
            
        # Misuazione della latenza dopo il cambiamento
        lat2 = measure_latency(num_requests=40)
            

        lat2 = measure_latency(num_requests=40)
        lb2 = latency_bucket(lat2)
        s2 = state_index(lb2, new_replicas)
        r = reward_function(lat2, new_replicas)

        Q[s, a] = Q[s, a] + alpha * (r + gamma * np.max(Q[s2]) - Q[s, a])

        current_replicas = new_replicas

        print(f"Episode {episode}: lat={lat2:.3f}s, replicas={current_replicas}, reward={r:.2f}")
        with open(log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), episode, lat2, current_replicas, r])

