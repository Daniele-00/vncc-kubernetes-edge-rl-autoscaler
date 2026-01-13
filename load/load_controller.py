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

# Funzione eseguita da ogni (Thread)
def worker_task(worker_id):
    while RUNNING:
        if CURRENT_MODE == "stop":
            time.sleep(1)
            continue
            
        # Esegue la richiesta
        generate_request()
        
        # Attende il tempo calcolato
        time.sleep(CURRENT_SLEEP)

# --- CERVELLO CENTRALE ---
if __name__ == "__main__":
    print(f" MULTI-THREAD Load Controller (15 Thread concorrenti) verso: {URL}")
    print(f"In attesa di comandi in '{CMD_FILE}'...")

    # 1. Avvia 15 Thread paralleli
    threads = []
    for i in range(15):
        t = threading.Thread(target=worker_task, args=(i,))
        t.daemon = True # Termina con il main thread
        t.start()
        threads.append(t)
        print(f" -> Thread {i+1} avviato.")

    start_time = time.time()

    # 2. Logica principale di controllo
    while True:
        # Leggi comando
        if os.path.exists(CMD_FILE):
            with open(CMD_FILE, "r") as f:
                CURRENT_MODE = f.read().strip().lower()
        else:
            CURRENT_MODE = "calma"

        if CURRENT_MODE == "stop":
            # Zero richieste.
            CURRENT_SLEEP = 1.0 

        elif CURRENT_MODE == "calma":
            # OBIETTIVO: Latenza bassa e stabile.
            # CALCOLO: 1 thread / 3.8s = ~0.26 req/s.

            CURRENT_SLEEP = 3.8 

        elif CURRENT_MODE == "spike":
            # OBIETTIVO: Saturazione totale.
            # CALCOLO: 15 thread / 0.05s = 300 req/s.
            CURRENT_SLEEP = 0.05 

        elif CURRENT_MODE == "onda":
            # OBIETTIVO: Variare da "gestibile" a "critico".
            factor = (math.sin(time.time() * 0.2) + 1) / 2
            # Sleep varia da 0.1s (Spike) a 3.8s (Calma)
            CURRENT_SLEEP = 0.1 + (3.7 * (1 - factor))

        # Il main thread aggiorna la logica ogni 0.1s
        time.sleep(0.1)