import time
import requests
import statistics

MINIKUBE_IP = "192.168.49.2"  # sostituisci con quello vero
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
