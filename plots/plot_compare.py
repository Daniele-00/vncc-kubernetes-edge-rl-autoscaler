import pandas as pd
import plotly.graph_objects as go
import os

# --- CONFIGURAZIONE ---
SLA_LIMIT = 0.35   # Soglia High (Violazione)
TARGET_SLA = 0.25  # Soglia Low (Target Ottimale)

# Fasi del test (Durata in secondi)
PHASES = [
    ("Calma Iniziale", 120, "rgba(0, 128, 0, 0.05)"),   # Verde
    ("Prima Onda", 300, "rgba(255, 255, 0, 0.05)"),      # Giallo
    ("Primo Spike", 300, "rgba(255, 165, 0, 0.1)"),      # Arancio
    ("Recupero", 60, "rgba(0, 128, 0, 0.05)"),           # Verde
    ("Secondo Spike", 300, "rgba(255, 0, 0, 0.1)"),      # Rosso
    ("Seconda Onda", 120, "rgba(255, 255, 0, 0.05)"),  # Giallo
    ("Terzo Spike", 120, "rgba(255, 20, 147, 0.15)"),     # Rosa
    ("Calma Finale", 120, "rgba(0, 128, 0, 0.05)"),      # Verde
    ("Stop Traffico", 30, "rgba(128, 128, 128, 0.1)"),   # Grigio
]

# 1. CARICAMENTO E PREPARAZIONE
try:
    df_rl = pd.read_csv("results/rl_eval_log.csv")
    df_base = pd.read_csv("results/baseline_log.csv")
except FileNotFoundError:
    print("❌ ERRORE: Non trovo i file in 'results/'. Controlla i nomi.")
    exit()

# Pulizia nomi colonne
df_rl.columns = [c.strip().lower() for c in df_rl.columns]
df_base.columns = [c.strip().lower() for c in df_base.columns]

# Aggiunta colonna 'elapsed' (tempo trascorso in secondi dall'inizio)
df_rl['timestamp'] = pd.to_datetime(df_rl['timestamp'])
df_base['timestamp'] = pd.to_datetime(df_base['timestamp'])

start_rl = df_rl['timestamp'].iloc[0]
start_base = df_base['timestamp'].iloc[0]

df_rl['elapsed'] = (df_rl['timestamp'] - start_rl).dt.total_seconds()
df_base['elapsed'] = (df_base['timestamp'] - start_base).dt.total_seconds()

# --- HELPER PER BANDE COLORATE ---
def add_phases_background(fig):
    t = 0
    for name, duration, color in PHASES:
        fig.add_vrect(
            x0=t, x1=t+duration,
            fillcolor=color, layer="below", line_width=0,
            annotation_text=name, annotation_position="top left",
            annotation_font_size=10, annotation_font_color="#555"
        )
        t += duration

# ==========================================
# GRAFICO 1: CONFRONTO LATENZA
# ==========================================
fig1 = go.Figure()

# Baseline (Arancione)
fig1.add_trace(go.Scatter(
    x=df_base["elapsed"], y=df_base["latency"],
    mode='lines', name='Baseline Autoscaler',
    line=dict(color='#f97316', width=2), 
    opacity=0.7
))

# RL Agent (Blu)
fig1.add_trace(go.Scatter(
    x=df_rl["elapsed"], y=df_rl["latency"],
    mode='lines', name='RL Autoscaler',
    line=dict(color='#2563eb', width=2.5) 
))

# Soglie
fig1.add_hline(y=SLA_LIMIT, line_dash="dash", line_color="#dc2626", 
               annotation_text=f"SLA Limit ({SLA_LIMIT}s)", annotation_position="bottom right")
fig1.add_hline(y=TARGET_SLA, line_dash="dot", line_color="#16a34a", 
               annotation_text="Target", annotation_position="bottom right")

add_phases_background(fig1)

fig1.update_layout(
    title="<b>Confronto Performance: Latenza di Risposta</b><br><sup>RL Agent vs Rule-Based Autoscaler sotto carico variabile</sup>",
    xaxis_title="Tempo Trascorso (Secondi)",
    yaxis_title="Latenza (s)",
    template="plotly_white", 
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)

# ==========================================
# GRAFICO 2: CONFRONTO UTILIZZO RISORSE
# ==========================================
fig2 = go.Figure()

# Baseline (Arancione)
fig2.add_trace(go.Scatter(
    x=df_base["elapsed"], y=df_base["replicas"],
    mode='lines', name='Baseline Autoscaler',
    line=dict(color='#f97316', width=2, shape='hv'), 
    fill='tozeroy', fillcolor='rgba(249, 115, 22, 0.1)' 
))

# RL Agent (Blu)
fig2.add_trace(go.Scatter(
    x=df_rl["elapsed"], y=df_rl["replicas"],
    mode='lines', name='RL Autoscaler',
    line=dict(color='#2563eb', width=2.5, shape='hv') 
))

add_phases_background(fig2)

fig2.update_layout(
    title="<b>Efficienza Risorse: Scaling dei Pod</b><br><sup>Reattività dello scaling orizzontale</sup>",
    xaxis_title="Tempo Trascorso (Secondi)",
    yaxis_title="Numero di Repliche",
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified",
    yaxis=dict(tickmode='linear', tick0=1, dtick=1) 
)

fig3 = go.Figure()

# Controlliamo se la colonna reward esiste 
if 'reward' in df_base.columns:
    fig3.add_trace(go.Scatter(
        x=df_base["elapsed"], y=df_base["reward"],
        mode='lines', name='Baseline Reward',
        line=dict(color='#f97316', width=2),
        opacity=0.6  # Un po' più trasparente per vedere bene l'RL
    ))
else:
    print("⚠️ Attenzione: Colonna 'reward' non trovata nel CSV Baseline.")

if 'reward' in df_rl.columns:
    fig3.add_trace(go.Scatter(
        x=df_rl["elapsed"], y=df_rl["reward"],
        mode='lines', name='RL Reward',
        line=dict(color='#2563eb', width=2.5)
    ))

add_phases_background(fig3)

fig3.update_layout(
    title="<b>Analisi Reward: Qualità della Policy</b><br><sup>Confronto del punteggio (Più alto è meglio)</sup>",
    xaxis_title="Tempo Trascorso (Secondi)",
    yaxis_title="Reward Istantaneo",
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)

# --- SALVATAGGIO ---
os.makedirs("img_compare", exist_ok=True)
fig1.write_html("img_compare/tesi_confronto_latenza.html")
fig2.write_html("img_compare/tesi_confronto_repliche.html")
fig3.write_html("img_compare/tesi_confronto_reward.html")

print("✅ Grafici generati in 'img_compare/'.")
print("   - tesi_confronto_latenza.html")
print("   - tesi_confronto_repliche.html")
print("   - tesi_confronto_reward.html")