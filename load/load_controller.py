import time
import requests
import os
import math
import threading

# Setup IP
MINIKUBE_IP = os.getenv("MINIKUBE_IP", "192.168.49.2")
URL = f"http://{MINIKUBE_IP}:30080/"
CMD_FILE = "current_scenario.txt"

# Variabili condivise tra i thread
CURRENT_MODE = "calma"
CURRENT_SLEEP = 0.5
RUNNING = True

def generate_request():
    try:
        # Timeout basso: se il server è intasato, stacca subito
        requests.get(URL, timeout=1.0)
    except:
        pass

# Funzione eseguita da ogni "Worker" (Thread)
def worker_task(worker_id):
    while RUNNING:
        if CURRENT_MODE == "stop":
            time.sleep(1)
            continue
            
        # Esegue la richiesta
        generate_request()
        
        # Dorme quanto dice il cervello centrale
        # Aggiungiamo un pizzico di casualità per non farli andare identici
        time.sleep(CURRENT_SLEEP)

# --- CERVELLO CENTRALE ---
if __name__ == "__main__":
    print(f"🔥 MULTI-THREAD Load Controller (10 Workers) verso: {URL}")
    print(f"In attesa di comandi in '{CMD_FILE}'...")

    # 1. Avvia 10 Thread paralleli (come avere 10 terminali aperti)
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker_task, args=(i,))
        t.daemon = True # Muoiono se chiudi lo script principale
        t.start()
        threads.append(t)
        print(f" -> Worker {i+1} avviato.")

    start_time = time.time()

    # 2. Loop principale: Calcola solo quanto devono dormire i worker
    while True:
        # Leggi comando
        if os.path.exists(CMD_FILE):
            with open(CMD_FILE, "r") as f:
                CURRENT_MODE = f.read().strip().lower()
        else:
            CURRENT_MODE = "calma"

        # Calcola Logica
        if CURRENT_MODE == "calma":
            CURRENT_SLEEP = 0.5  # 10 thread * 2 req/s = 20 req/s totali (Gestibile)

        elif CURRENT_MODE == "spike":
            CURRENT_SLEEP = 0.05 # 10 thread * 20 req/s = 200 req/s (BOMBARDAMENTO)

        elif CURRENT_MODE == "onda":
            # Onda sinusoidale
            factor = (math.sin(time.time() * 0.2) + 1) / 2
            # Sleep varia da 0.05 (veloce) a 1.0 (lento)
            CURRENT_SLEEP = 0.05 + (0.95 * (1 - factor))
            
            if int(time.time()) % 2 == 0:
                print(f"🌊 Onda: intensità {factor:.2f} -> Sleep {CURRENT_SLEEP:.3f}s", end="\r")
        
        elif CURRENT_MODE == "stop":
            print("🛑 STOP", end="\r")

        # Il main thread aggiorna la logica ogni 0.1s
        time.sleep(0.1)