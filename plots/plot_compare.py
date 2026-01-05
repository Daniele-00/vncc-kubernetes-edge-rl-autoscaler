import pandas as pd
import plotly.graph_objects as go
import os

# 1. Carica i due file separati
# Assicurati di aver rinominato i file come ti ho detto!
try:
    df_rl = pd.read_csv("results/dati_rl.csv")
    df_base = pd.read_csv("results/dati_baseline.csv")
except FileNotFoundError:
    print("ERRORE: Non trovo i file 'results/dati_rl.csv' o 'results/dati_baseline.csv'.")
    print("Ricordati di eseguire i test e rinominare manualmente i file di log!")
    exit()

# Pulizia nomi colonne
df_rl.columns = [c.strip().lower() for c in df_rl.columns]
df_base.columns = [c.strip().lower() for c in df_base.columns]

# --- GRAFICO 1: CONFRONTO LATENZA ---
fig1 = go.Figure()

# Linea RL
fig1.add_trace(go.Scatter(
    x=df_rl["episode"], y=df_rl["latency"],
    mode='lines', name='RL Autoscaler',
    line=dict(color='blue', width=2)
))

# Linea Baseline
fig1.add_trace(go.Scatter(
    x=df_base["episode"], y=df_base["latency"],
    mode='lines', name='Baseline (Soglia Fissa)',
    line=dict(color='red', width=2, dash='dash') # Tratteggiata per distinguerla
))

# Soglie (disegniamo le soglie critiche usate per far vedere chi le rispetta meglio)
fig1.add_hline(y=0.08, line_dash="dot", annotation_text="Target SLA", line_color="green")

fig1.update_layout(
    title="Confronto Latenza: AI vs Baseline",
    xaxis_title="Episodio",
    yaxis_title="Latenza (s)",
    template="plotly_white",
    xaxis=dict(rangemode="tozero"),
    yaxis=dict(rangemode="tozero")
)

# --- GRAFICO 2: CONFRONTO REPLICHE ---
fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=df_rl["episode"], y=df_rl["replicas"],
    mode='lines+markers', name='RL Replicas',
    line=dict(color='blue', width=2)
))

fig2.add_trace(go.Scatter(
    x=df_base["episode"], y=df_base["replicas"],
    mode='lines+markers', name='Baseline Replicas',
    line=dict(color='red', width=2, dash='dash')
))

fig2.update_layout(
    title="Confronto Utilizzo Risorse (Repliche)",
    xaxis_title="Episodio",
    yaxis_title="N. Repliche",
    template="plotly_white",
    xaxis=dict(rangemode="tozero"),
    yaxis=dict(rangemode="tozero", range=[0, 5])
)

# Salva i grafici
os.makedirs("results", exist_ok=True)
fig1.write_html("results/confronto_latenza.html")
fig2.write_html("results/confronto_repliche.html")

print("✅ Grafici generati in 'results/':")
print("   - confronto_latenza.html")
print("   - confronto_repliche.html")