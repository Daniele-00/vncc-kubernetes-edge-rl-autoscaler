import time
import requests
import os
import math
import sys

# Setup IP
MINIKUBE_IP = os.getenv("MINIKUBE_IP", "192.168.49.2")
URL = f"http://{MINIKUBE_IP}:30080/"
CMD_FILE = "current_scenario.txt"

def generate_request():
    try:
        requests.get(URL, timeout=0.5)
    except:
        pass

print(f"🎮 Load Controller Attivo. Target: {URL}")
print(f"In attesa di comandi in '{CMD_FILE}' (Scrivi dalla Dashboard)...")

start_time = time.time()

while True:
    # 1. Legge il comando dalla Dashboard
    mode = "calma"
    if os.path.exists(CMD_FILE):
        with open(CMD_FILE, "r") as f:
            mode = f.read().strip().lower()
    
    # 2. Esegue la logica in base alla modalità
    elapsed = time.time() - start_time
    
    if mode == "stop":
        time.sleep(1) # Nessun traffico
        
    elif mode == "calma":
        # Poco traffico (5 req/s)
        generate_request()
        time.sleep(0.2)
        
    elif mode == "spike":
        # Traffico alto fisso (50 req/s)
        generate_request()
        time.sleep(0.005)
        
    elif mode == "onda":
        # Sinusoide
        factor = (math.sin(time.time() * 0.5) + 1) / 2 # Oscilla veloce
        # Sleep varia da 0.01 (veloce) a 0.5 (lento)
        sleep_time = 0.01 + (1 - factor) * 0.5
        generate_request()
        time.sleep(sleep_time)
        
    # 3. Stampa lo stato ogni 5 secondi
    if int(time.time()) % 5 == 0:
        print(f"Status: {mode.upper()}...", end="\r")