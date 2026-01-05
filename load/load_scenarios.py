import time
import requests
import sys
import math

import os

MINIKUBE_IP = os.getenv("MINIKUBE_IP", "192.168.49.2") # Per test sostituire con IP minikube corretto
URL = f"http://{MINIKUBE_IP}:30080/"

def generate_request():
    try:
        requests.get(URL, timeout=0.5)
    except:
        pass

def scenario_ramp_up(duration_sec=60):
    """Scenario RAMPA: Aumento graduale del traffico"""
    print("Avvio scenario: RAMPA (da 1 a 20 req/s)")
    start_time = time.time()
    while time.time() - start_time < duration_sec:
        elapsed = time.time() - start_time
        # Aumenta intensità col tempo
        intensity = 1 + (elapsed / duration_sec) * 20 
        sleep_time = 1.0 / intensity
        generate_request()
        time.sleep(sleep_time)

def scenario_spike(duration_sec=60):
    """Scenario SPIKE: Traffico normale con picco improvviso"""
    print("Avvio scenario: SPIKE")
    start_time = time.time()
    while time.time() - start_time < duration_sec:
        elapsed = time.time() - start_time
        # Picco tra il secondo 20 e 40
        if 20 < elapsed < 40:
            time.sleep(0.01) # Salita (100 req/s)
        else:
            time.sleep(0.2)  # Calma (5 req/s)
        generate_request()

def scenario_wave(duration_sec=120):
    """Scenario ONDA: Onda sinusoidale"""
    print("Avvio scenario: ONDA")
    start_time = time.time()
    while time.time() - start_time < duration_sec:
        elapsed = time.time() - start_time
        # Funzione seno per oscillare il carico
        factor = (math.sin(elapsed * 0.2) + 1) / 2 # va da 0 a 1
        sleep_time = 0.05 + (1 - factor) * 0.3 
        generate_request()
        time.sleep(sleep_time)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usa: python load_scenarios.py [ramp|spike|wave]")
    elif sys.argv[1] == "ramp":
        scenario_ramp_up()
    elif sys.argv[1] == "spike":
        scenario_spike()
    elif sys.argv[1] == "wave":
        scenario_wave()