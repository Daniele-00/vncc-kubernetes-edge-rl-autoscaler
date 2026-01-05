import time # Per misurare i tempi
import requests # Per inviare richieste HTTP
import statistics # Per calcolare statistiche
import os # Per variabili d'ambiente

# Deinfizione dell'URL del servizio
MINIKUBE_IP = os.getenv("MINIKUBE_IP", "192.168.49.2") # Per test sostituire con IP minikube corretto
URL = f"http://{MINIKUBE_IP}:30080/"

def send_burst(n, sleep_between=0.0):
    latencies = []
    for _ in range(n):
        start = time.time()
        try:
            r = requests.get(URL, timeout=2)
            r.raise_for_status()
            latencies.append(time.time() - start)
        except Exception:
            latencies.append(2.0)
        if sleep_between > 0:
            time.sleep(sleep_between)
    return latencies

if __name__ == "__main__":
    while True:
        calm = send_burst(50, sleep_between=0.1)
        print("🟢 Calma:", statistics.mean(calm))

        busy = send_burst(200, sleep_between=0.01)
        print("🔴 Carico:", statistics.mean(busy))
