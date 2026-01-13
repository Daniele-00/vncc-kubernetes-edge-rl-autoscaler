import time
import subprocess
import sys
import os

# --- CONFIGURAZIONE SCENARIO DI TEST ---
# Ogni tupla è: (scenario, durata_in_secondi)
TEST_SEQUENCE = [
    ("calma", 120),   # 2 min di calma
    ("onda",  300),   # 5 min di carico sinusoidale
    ("spike", 300),   # 5 min di carico sinusoidale
    ("calma", 60),    # 1 min di recupero
    ("spike", 300),   # 5 min di picco intenso
    ("onda", 120),    # 2 min di carico sinusoidale
    ("spike", 120),   # 2 min di picco intenso
    ("calma", 120),   # 2 min di recupero
    ("stop",  10)     # Fine
    
]

CMD_FILE = "current_scenario.txt"
RESULTS_DIR = "results"

def set_scenario(mode):
    """Scrive il comando per il Load Generator"""
    with open(CMD_FILE, "w") as f:
        f.write(mode)
    print(f" CAMBIO SCENARIO -> {mode.upper()}")

def reset_cluster():
    """Riporta il cluster a 1 replica per partire puliti"""
    print(" Reset cluster a 1 replica...")
    subprocess.run("kubectl scale deploy edge-app --replicas=1", shell=True, check=False)
    time.sleep(5) # Tempo tecnico per k8s

def run_test(autoscaler_type):
    # 1. Preparazione
    print(f"\n AVVIO BENCHMARK: {autoscaler_type.upper()}")
    reset_cluster()
    
    # Determina quale script avviare
    script_name = "rl_autoscaler.py" if autoscaler_type == "rl" else "baseline_autoscaler.py"
    script_path = os.path.join("autoscaler", script_name)
    
    # 2. Avvia l'autoscaler in background

    print(f" Avvio {script_name}...")
    
    # IMPORTANTE: Passiamo le variabili d'ambiente se necessario (es. MINIKUBE_IP)
    env = os.environ.copy()
    
    # Avvio processo
    process = subprocess.Popen([sys.executable, script_path], env=env)
    
    try:
        # 3. Esegue la sequenza temporale
        start_time = time.time()
        
        for mode, duration in TEST_SEQUENCE:
            set_scenario(mode)
            
            # Countdown visivo
            for remaining in range(duration, 0, -1):
                elapsed = int(time.time() - start_time)
                print(f"   ⏳ {mode.upper()}: mancano {remaining}s (Tot: {elapsed}s)", end="\r")
                time.sleep(1)
            print(" " * 50, end="\r") # Pulisce la riga
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrotto manualmente!")
        
    finally:
        # 4. Chiusura pulita
        print(f"\nTEST COMPLETATO PER {autoscaler_type.upper()}")
        set_scenario("stop") # Ferma il traffico
        process.terminate()  # Uccide l'autoscaler
        try:
            process.wait(timeout=5)
        except:
            process.kill()
        print("✅ Processo terminato.")

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ["rl", "baseline"]:
        print("USO: python run_benchmark.py [rl | baseline]")
        sys.exit(1)
        
    target = sys.argv[1]
    
    # Verifica che il Load Generator sia attivo (o avvisa l'utente)
    print("⚠️  ASSICURATI CHE 'python load/load_controller.py' SIA IN ESECUZIONE IN UN ALTRO TERMINALE!")
    print("Premi INVIO per partire...")
    input()
    
    run_test(target)