import subprocess
import time
import requests
import csv  # <--- Questo mancava!
import os
import json
from datetime import datetime

# --- CONFIGURAZIONE ---
MINIKUBE_IP = os.getenv("MINIKUBE_IP", "192.168.49.2")
URL = f"http://{MINIKUBE_IP}:30080/"
CONFIG_FILE = "autoscaler_config.json"
# Nota: Puoi cambiare questo nome se vuoi salvare un file separato per la tesi
# es. "results/dati_baseline.csv", altrimenti usa "results/rl_log.csv" per vederlo live nella dashboard
LOG_FILE = "results/rl_log.csv" 

MIN_PODS = 1
MAX_PODS = 4

# Soglie di default (verranno sovrascritte dalla Dashboard se attiva)
CURRENT_LOW_THR = 0.08
CURRENT_HIGH_THR = 0.20

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

def measure_latency(num_requests=20):
    latencies = []
    for _ in range(num_requests):
        start = time.time()
        try:
            requests.get(URL, timeout=1)
            latencies.append(time.time() - start)
        except:
            latencies.append(1.0) # Penalità timeout
    return sum(latencies) / len(latencies) if latencies else 1.0

# Calcolo Reward "Fittizio" (solo per mostrarlo nel grafico insieme all'RL)
def calculate_dummy_reward(lat, replicas, low, high):
    r = 0.0
    if lat < low: r += 5
    elif lat < high: r += 2
    else: r -= 5
    r -= (replicas - 1) * 1.0
    return r

if __name__ == "__main__":
    print("📉 Avvio BASELINE Autoscaler (Controllo da Dashboard attivo)")
    
    # Se il file non esiste, crea l'intestazione
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow(["timestamp", "episode", "latency", "replicas", "reward"])

    # Cerca di capire l'ultimo numero di episodio per continuare il grafico
    episode = 0
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            if len(lines) > 1:
                last_line = lines[-1]
                parts = last_line.split(",")
                if len(parts) >= 2 and parts[1].isdigit():
                     episode = int(parts[1]) + 1
    except Exception as e:
        print(f"Info: Impossibile leggere ultimo episodio ({e}). Parto da 0.")

    current_replicas = set_replicas(1)
    wait_for_deployment_ready()
    
    while True:
        # 1. LEGGI CONFIGURAZIONE DALLA DASHBOARD
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    conf = json.load(f)
                    CURRENT_LOW_THR = conf.get("low", 0.08)
                    CURRENT_HIGH_THR = conf.get("high", 0.20)
            except:
                pass

        # 2. Misura
        lat = measure_latency(num_requests=30)
        
        # 3. Logica BASELINE (Rule-Based: IF/ELSE)
        new_replicas = current_replicas
        
        if lat > CURRENT_HIGH_THR and current_replicas < MAX_PODS:
            print(f"⚠️ Lat {lat:.3f}s > {CURRENT_HIGH_THR}s -> Scaling UP")
            new_replicas += 1
        elif lat < CURRENT_LOW_THR and current_replicas > MIN_PODS:
            print(f"✅ Lat {lat:.3f}s < {CURRENT_LOW_THR}s -> Scaling DOWN")
            new_replicas -= 1
        else:
            print(f"➡️ Lat {lat:.3f}s OK. (Target: {CURRENT_LOW_THR}-{CURRENT_HIGH_THR})")

        # 4. Attuazione
        if new_replicas != current_replicas:
            set_replicas(new_replicas)
            wait_for_deployment_ready()
            current_replicas = new_replicas
        
        # 5. Log (con reward calcolato solo per confronto visivo)
        lat_post = measure_latency(num_requests=20)
        rew = calculate_dummy_reward(lat_post, current_replicas, CURRENT_LOW_THR, CURRENT_HIGH_THR)

        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), episode, lat_post, current_replicas, rew])
        
        episode += 1