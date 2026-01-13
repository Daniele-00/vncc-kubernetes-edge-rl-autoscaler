import time
import os
import random
import sys

CMD_FILE = "current_scenario.txt"

# --- CONFIGURAZIONE TESI ---
NUM_SUPER_CYCLES = 6  # Numero di super-cicli (epoche)

# Definizione dei blocchi di training (Scenario, Min_Sec, Max_Sec)
TRAIN_BLOCKS = [
    ("calma",  90, 120),   # Periodo di calma per stabilizzare
    ("onda",   120, 180),  # Carico sinusoidale (impara a gestire variazioni)
    ("spike",  90,  120),  # Picchi improvvisi di carico (impara a reagire rapidamente)
]

def write_scenario(mode: str):
    mode = mode.lower()
    with open(CMD_FILE, "w") as f:
        f.write(mode)
    # Usa sys.stdout per essere sicuro che stampi subito
    print(f"\n\n➡️  CAMBIO SCENARIO: {mode.upper()}")

def run_training():
    random.seed(42) # Seme per riproducibilità

    print("\n🎓 AVVIO TRAINING CURRICULUM RL")
    print(f"   Epoche (Super-Cicli): {NUM_SUPER_CYCLES}")
    print(f"   Strategia: Warmup -> {NUM_SUPER_CYCLES} Cicli Misti -> Stop")
    print("---------------------------------------------------\n")

    try:
        # FASE 0: WARM-UP (Riscaldamento)
        # Periodo di calma per permettere al sistema di stabilizzarsi
        print("🔥 FASE 0: WARM-UP (Calma Iniziale - 60s)")
        write_scenario("calma")
        for i in range(30, 0, -1):
            sys.stdout.write(f"\r   Riscaldamento... {i}s ")
            sys.stdout.flush()
            time.sleep(1)
        
        # CICLO PRINCIPALE (EPOCHE)
        start_global = time.time()
        
        for cycle in range(NUM_SUPER_CYCLES):
            print(f"\n\n🔄 SUPER-CICLO (EPOCA) {cycle + 1}/{NUM_SUPER_CYCLES}")
            print("=========================================")

            # Mischia i blocchi per variare l'ordine di apprendimento
            blocks = TRAIN_BLOCKS.copy()
            random.shuffle(blocks)

            for mode, d_min, d_max in blocks:
                duration = random.randint(d_min, d_max)
                write_scenario(mode)

                start_block = time.time()
                while True:
                    elapsed = int(time.time() - start_block)
                    remaining = duration - elapsed
                    
                    if remaining <= 0:
                        break
                    
                    # Barra di progresso visiva
                    bar_len = 20
                    progress = int((elapsed / duration) * bar_len)
                    bar = "█" * progress + "-" * (bar_len - progress)
                    
                    sys.stdout.write(f"\r   [{mode.upper():<5}] |{bar}| {remaining:3d}s rimasti")
                    sys.stdout.flush()
                    time.sleep(1)

        total_time = int(time.time() - start_global)
        print(f"\n\n✅ TRAINING COMPLETATO in {total_time//60} min {total_time%60} sec.")
        print("   Q-Table consolidata.")

    except KeyboardInterrupt:
        print("\n\n⛔ Training interrotto manualmente.")
    finally:
        write_scenario("stop")
        print("🛑 Scenario settato a STOP.")

if __name__ == "__main__":
    # Check di sicurezza per la fisica del sistema
    print("⚠️  CHECKLIST PRIMA DI PARTIRE:")
    print("   1. [Load Controller] Avviato e pronto a ricevere comandi")
    print("   2. [RL Autoscaler]   Avviato in modalità TRAINING")
    
    x = input("\nPremi INVIO se è tutto pronto... ")
    run_training()