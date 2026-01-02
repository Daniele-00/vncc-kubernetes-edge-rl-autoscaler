# Kubernetes Edge Cloud with Reinforcement Learning Autoscaler

Progetto per l’insegnamento **Virtual Networks and Cloud Computing** (a.a. **2024/25**)  
Autore: **<metti-il-tuo-nome>**

Questo progetto implementa un mini **Edge Cloud** basato su **Kubernetes** in cui il numero di repliche di un microservizio viene gestito da un autoscaler intelligente basato su **Reinforcement Learning (Q-learning)**.

L’obiettivo è mostrare, in modo riproducibile, come sia possibile:

- containerizzare un’applicazione “edge”
- orchestrarla con Kubernetes
- generare un carico variabile
- misurare la latenza
- usare un agente RL per decidere dinamicamente il numero di repliche (scaling up/down) in funzione delle prestazioni

Il repository include:

- codice dell’applicazione
- manifest Kubernetes
- autoscaler RL e baseline
- script di generazione carico
- strumenti per visualizzare i risultati (**Plotly + Streamlit**)
- istruzioni complete per riprodurre l’esperimento

---

## 🔍 Overview dell’architettura

### Architettura logica (high level)

```text
                +----------------------------------------+
                |              Load Generator             |
                |  (Python requests: traffico variabile)  |
                +-------------------------+--------------+
                                          |  HTTP
                                          v
                               +------------------------+
                               |   Kubernetes (minikube)|
                               | - Deployment: edge-app |
           NodePort:30080  +-->| - Service: NodePort    |
                           |   | - Pod(s): Docker       |
                           |   +------------------------+
                           |              ^
                           |              | HTTP
                           |              |
                           |   +-----------------------+
                           |   |     Edge App (Flask)  |
                           |   |   CPU-bound workload  |
                           |   +-----------------------+
                           |
                           |  Log CSV (lat,replicas,reward)
                           v
                 +--------------------------+
                 |  RL Autoscaler (Q-Learn) |
                 | - misura latenza         |
                 | - decide scaling         |
                 +--------------------------+
                             |
                             |  kubectl scale
                             v
                         Kubernetes

                 +--------------------------+
                 | Dashboard (Streamlit)    |
                 | + Plotly (grafici live)  |
                 +--------------------------+
```

---

## 📁 Struttura del repository

```text
kube-rl-edge/
│
├── app/                     # Applicazione edge (Flask) + Dockerfile
│   ├── app.py
│   └── Dockerfile
│
├── k8s/                     # Manifest Kubernetes
│   └── deployment.yaml      # Deployment + Service NodePort
│
├── autoscaler/              # Autoscaler intelligenti
│   ├── rl_autoscaler.py     # Autoscaling RL (Q-learning)
│   └── baseline_autoscaler.py   # Autoscaling a soglia fissa (baseline)
│
├── load/                    # Generatore di traffico
│   └── load_generator.py
│
├── results/                 # Log CSV e grafici generati
│   ├── rl_log.csv           # Log autoscaler RL
│   └── baseline_log.csv     # Log baseline (se eseguita)
│
├── dashboard_pretty.py      # Dashboard Streamlit “semplice”
├── dashboard_ultra.py       # Dashboard Streamlit avanzata (Plotly, soglie, colori)
├── plot_results.py          # Analisi e grafici offline (Plotly)
├── requirements.txt         # Dipendenze Python (consigliato)
└── README.md
```

> Se `requirements.txt` non esiste ancora, puoi crearlo con le librerie usate: `flask`, `requests`, `numpy`, `pandas`, `plotly`, `streamlit`.

---

## 🧱 Prerequisiti

### Opzione A – Ambiente tipico (Windows + WSL2)

- Windows 10/11
- WSL2 con Ubuntu 22.04 (o simile)
- Supporto virtualizzazione attivo nel BIOS

Dentro Ubuntu (WSL2):

- Docker Engine
- minikube
- kubectl
- Python 3.10+ e `python3-venv`

### Opzione B – Linux nativo

- Distribuzione Linux (Ubuntu consigliato)
- Docker Engine
- minikube
- kubectl
- Python 3.10+ e `python3-venv`

---

## ⚙️ Setup passo–passo

### 1️⃣ Clonare il repository

```bash
git clone https://github.com/<tu-utente>/<nome-repo>.git
cd <nome-repo>
```

### 2️⃣ Creare e attivare un virtual environment Python

```bash
python3 -m venv venv
source venv/bin/activate
```

Installare le dipendenze:

```bash
pip install --upgrade pip
pip install flask requests numpy pandas plotly streamlit
# oppure, se presente:
# pip install -r requirements.txt
```

### 3️⃣ Avviare minikube

```bash
minikube start --driver=docker
kubectl get nodes
```

### 4️⃣ Build dell’immagine Docker dell’applicazione edge

```bash
cd app
docker build -t edge-app:latest .
cd ..
```

Caricare l’immagine dentro minikube:

```bash
minikube image load edge-app:latest
```

### 5️⃣ Deploy su Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
kubectl get pods
kubectl get svc
```

Recuperare l’IP del nodo minikube:

```bash
minikube ip
# es. 192.168.49.2
```

Test (da Ubuntu/WSL):

```bash
curl http://<MINIKUBE_IP>:30080/
# output atteso: OK
```

### 6️⃣ Configurare gli script con l’IP di minikube

Nei file:

- `load/load_generator.py`
- `autoscaler/rl_autoscaler.py`
- `autoscaler/baseline_autoscaler.py` (se usata)

sostituire:

```python
MINIKUBE_IP = "<MINIKUBE_IP>"
```

con l’IP reale, ad esempio:

```python
MINIKUBE_IP = "192.168.49.2"
URL = f"http://{MINIKUBE_IP}:30080/"
```

---

## 🚀 Esecuzione della demo completa

Usa **4 terminali** (tutti con `source venv/bin/activate`).

### Terminale 1 – Monitor Kubernetes

Mostra in tempo reale il numero di repliche:

```bash
kubectl get deploy edge-app -w
```

### Terminale 2 – Generatore di carico

```bash
python load/load_generator.py
```

Output tipico:

```text
Calma: 0.06...
Carico: 0.20...
Calma: 0.07...
Carico: 0.19...
```

### Terminale 3 – Autoscaler RL (Q-learning)

```bash
python autoscaler/rl_autoscaler.py
```

Output esemplificativo:

```text
Episode 0: lat=0.210s, replicas=1, reward=0.00
deployment.apps/edge-app scaled
Episode 1: lat=0.120s, replicas=2, reward=3.00
Episode 2: lat=0.085s, replicas=2, reward=4.00
...
```

Genera il file:

- `results/rl_log.csv`

In parallelo, nel Terminale 1 compaiono nuove righe quando cambia il numero di repliche:

```text
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
edge-app    1/1     1            1           5m
edge-app    2/2     2            2           6m   # scaling up
...
```

### Terminale 4 – Dashboard interattiva

Dashboard avanzata:

```bash
streamlit run dashboard_ultra.py --server.address=localhost --server.port=8502
```

Nel browser:

- `http://localhost:8502`

La dashboard mostra:

- KPI: latenza media, repliche medie, reward medio
- grafico combinato latenza + repliche (con soglie)
- grafico reward nel tempo
- tabella delle ultime decisioni dell’agente

---

## 📊 Analisi offline dei risultati

Dopo una run dell’RL (e opzionalmente della baseline):

```bash
python plot_results.py
```

Lo script legge:

- `results/rl_log.csv`
- `results/baseline_log.csv` (se presente)

e genera grafici HTML, ad es.:

- `results/rl_latency.html`
- `results/rl_replicas.html`
- `results/rl_reward.html`

Apribili da browser (doppio click su Windows / Linux).

---

## 🧠 Reinforcement Learning in breve

L’autoscaler RL modella il problema come un **Markov Decision Process**:

- **Stato** \(s\):
  - livello di latenza (bassa / media / alta)
  - numero corrente di repliche
- **Azioni** \(a\):
  - \(a \in \{-1, 0, +1\}\) (diminuire, mantenere, aumentare repliche)
- **Reward**:
  - positivo se la latenza è sotto soglia con poche repliche
  - negativo se la latenza è alta o vengono usate troppe repliche

Aggiornamento Q-learning:

\[
Q(s,a) \leftarrow Q(s,a) + \alpha \left[ r + \gamma \max_{a'} Q(s',a') - Q(s,a) \right]
\]

Strategia di scelta azioni: **ε-greedy** (equilibrio tra esplorazione e sfruttamento).

---

## 🔬 Baseline autoscaler

La baseline implementa una politica più semplice:

- se la latenza > soglia alta → scala “up” (aumenta repliche)
- se la latenza < soglia bassa → scala “down” (riduce repliche)
- altrimenti mantiene

I log vengono salvati in `results/baseline_log.csv` e possono essere confrontati con l’RL tramite `plot_results.py`.

---

## ✅ Possibili estensioni

- Epsilon decay (ridurre esplorazione nel tempo)
- Penalità per troppi cambi di repliche (stabilità)
- Stati arricchiti (CPU, throughput, percentili di latenza)
- RL con approssimazione di funzione (DQN)
- Edge multi-nodo / multi-servizio

---

## 💡 Note per il docente

Il progetto è pensato per essere:

- **didattico**: mostra chiaramente Docker, Kubernetes, autoscaling, RL
- **riproducibile**: tutti i comandi necessari sono elencati
- **estensibile**: la struttura a directory separa chiaramente app, manifest K8s, RL, carico, analisi

In caso di problemi di compatibilità con WSL2, il progetto è facilmente eseguibile anche su una macchina Linux nativa con Docker e minikube già installati.
