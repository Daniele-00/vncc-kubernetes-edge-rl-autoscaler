import numpy as np
import os

# CONFIGURAZIONE
FILE_PATH = "results/qtable.npy"
ACTIONS = ["DOWN (-1)", "HOLD (0)", "UP (+1)"]
LATENCY_NAMES = ["LOW (0)", "TARGET (1)", "HIGH (2)"]
MAX_PODS = 5  # Deve corrispondere al tuo rl_autoscaler.py

def inspect():
    if not os.path.exists(FILE_PATH):
        print(f"❌ ERRORE: Il file {FILE_PATH} non esiste. Fai prima il training!")
        return

    try:
        Q = np.load(FILE_PATH)
    except Exception as e:
        print(f"❌ Errore nel caricamento: {e}")
        return

    print(f"\n📂 ANALISI Q-TABLE: {FILE_PATH}")
    print(f"   Dimensioni: {Q.shape}")
    print(f"   Valore Max: {np.max(Q):.4f}")
    print(f"   Valore Min: {np.min(Q):.4f}")
    print(f"   Celle piene (non zero): {np.count_nonzero(Q)} su {Q.size}")
    
    if np.all(Q == 0):
        print("\n⚠️  ATTENZIONE: LA Q-TABLE È COMPLETAMENTE VUOTA (TUTTI ZERI)!")
        return

    print("\n------")
    header = f"{'STATO (Lat / Reps)':<25} | {'DOWN':<12} | {'HOLD':<12} | {'UP':<12}"
    print(header)
    print("-" * len(header))

    
    for lat_idx, lat_name in enumerate(LATENCY_NAMES):
        for rep in range(1, MAX_PODS + 1):
            state_idx = lat_idx * MAX_PODS + (rep - 1)
            
            if state_idx >= len(Q):
                break

            row = Q[state_idx]
            
            # Evidenzia l'azione migliore
            best_action_idx = np.argmax(row)
            best_marker = ["", "", ""]
            
            if not np.all(row == 0):
                best_marker[best_action_idx] = "*"

            vals = (
                f"{row[0]:.2f}{best_marker[0]}",
                f"{row[1]:.2f}{best_marker[1]}",
                f"{row[2]:.2f}{best_marker[2]}"
            )
            
            print(f"{lat_name} / {rep} pod{' ':<7} | {vals[0]:<12} | {vals[1]:<12} | {vals[2]:<12}")
            
        print("-" * len(header)) # Separatore tra gruppi di latenza

if __name__ == "__main__":
    inspect()