import subprocess
import time
import statistics
import requests

MIN_PODS = 1
MAX_PODS = 4
MINIKUBE_IP = "192.168.49.2"
URL = f"http://{MINIKUBE_IP}:30080/"

def set_replicas(n):
    n = max(MIN_PODS, min(MAX_PODS, n))
    subprocess.run(
        ["kubectl", "scale", "deploy/edge-app", f"--replicas={n}"],
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

if __name__ == "__main__":
    current = set_replicas(1)
    time.sleep(5)
    log_file = "results/baseline_log.csv"
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "episode", "latency", "replicas"])


    episode = 0
    while True:
        lat = measure_latency()
        print(f"lat={lat:.3f}s, replicas={current}")

        if lat > 0.2 and current < MAX_PODS:
            current = set_replicas(current + 1)
        elif lat < 0.08 and current > MIN_PODS:
            current = set_replicas(current - 1)

        with open(log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), episode, lat, current])

        episode +=1

        time.sleep(5)
