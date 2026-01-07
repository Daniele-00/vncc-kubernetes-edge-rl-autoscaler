import subprocess
import time
import requests
import csv  
import os
import json
from datetime import datetime
from reward_utils import reward_function

# --- CONFIGURAZIONE ---
MINIKUBE_IP = os.getenv("MINIKUBE_IP", "192.168.49.2")
URL = f"http://{MINIKUBE_IP}:30080/"
CONFIG_FILE = "autoscaler_config.json"

LOG_FILE = "results/baseline_log.csv" 

MIN_PODS = 1
MAX_PODS = 10

# Soglie di default (verranno sovrascritte dalla Dashboard se attiva)
CURRENT_LOW_THR = 0.20
CURRENT_HIGH_THR = 0.30

def set_replicas(n):
    n = max(MIN_PODS, min(MAX_PODS, n))
    subprocess.run(["kubectl", "scale", "deploy/edge-app", f"--replicas={n}"], check=True)
    return n

def wait_for_deployment_ready():
    """Attende che i pod siano pronti per evitare letture sporche"""
    try:
        subprocess.run(["kubectl", "rollout", "status", "deployment/edge-app", "--timeout=30s"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
    except:
        pass
    
def measure_latency(num_requests=10):
    latencies = []
    for _ in range(num_requests):
        start = time.time()
        try:
            requests.get(URL, timeout=1.0)
            latencies.append(time.time() - start)
        except:
            latencies.append(1.0)
        
        # Pausa per non intasare il server e avere dati puliti (0.20s)
        time.sleep(0.05)
            
    return sum(latencies) / len(latencies) if latencies else 1.0

if __name__ == "__main__":
    print(" Avvio BASELINE Autoscaler (RESET: File log pulito)")
    
    # --- RESET FORZATO (MODALITÀ "w") ---
    # Questo assicura che l'header ci sia SEMPRE.
    with open(LOG_FILE, "w", newline="") as f:
        csv.writer(f).writerow(["timestamp", "episode", "latency", "replicas", "reward"])

    current_replicas = set_replicas(1)
    wait_for_deployment_ready()
    
    episode = 0 # Si riparte sempre da 0 per pulizia
    
    while True:
        # 1. LEGGI CONFIG DASHBOARD
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    conf = json.load(f)
                    CURRENT_LOW_THR = conf.get("low", 0.08)
                    CURRENT_HIGH_THR = conf.get("high", 0.20)
            except:
                pass

        # 2. MISURA
        lat = measure_latency(num_requests=30)
        
        # 3. LOGICA BASELINE
        new_replicas = current_replicas
        if lat > CURRENT_HIGH_THR and current_replicas < MAX_PODS:
            print(f"⚠️ Lat {lat:.3f}s > {CURRENT_HIGH_THR}s -> UP")
            new_replicas += 1
        elif lat < CURRENT_LOW_THR and current_replicas > MIN_PODS:
            print(f"✅ Lat {lat:.3f}s < {CURRENT_LOW_THR}s -> DOWN")
            new_replicas -= 1
        else:
            print(f"➡️ Lat {lat:.3f}s OK.")

        # 4. ATTUAZIONE
        if new_replicas != current_replicas:
            set_replicas(new_replicas)
            wait_for_deployment_ready()
            current_replicas = new_replicas
        
        # 5. LOG
        lat_post = measure_latency(num_requests=20)
        # Usiamo la funzione definita sopra
        rew = reward_function(lat_post, current_replicas, CURRENT_LOW_THR, CURRENT_HIGH_THR)

        # Qui usiamo "a" (append) per aggiungere sotto l'header
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), episode, lat_post, current_replicas, rew])
        
        episode += 1