import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
import os

# Leggi i dati
df = pd.read_csv("results/baseline_log.csv")
df.columns = [c.strip().lower() for c in df.columns]

# Crea una cartella per i grafici finali
os.makedirs("tesina_img", exist_ok=True)

# --- GRAFICO 1: PERFORMANCE COMPARATA ---
# Un grafico con due assi Y: Latenza (sx) e Repliche (dx)
fig = go.Figure()

# Area Latenza
fig.add_trace(go.Scatter(
    x=df["episode"], y=df["latency"],
    name="Latenza Misurata (s)",
    mode='lines',
    line=dict(color='rgb(31, 119, 180)', width=2)
))

# Area Repliche (Barre)
fig.add_trace(go.Bar(
    x=df["episode"], y=df["replicas"],
    name="Numero Repliche",
    yaxis='y2',
    marker=dict(color='rgba(255, 127, 14, 0.5)'),
    width=1
))

fig.update_layout(
    title="Analisi Prestazionale: Latenza vs Scaling",
    xaxis=dict(title="Episodio (Tempo)"),
    yaxis=dict(title="Latenza [s]", side='left', showgrid=True),
    yaxis2=dict(title="N. Repliche", side='right', overlaying='y', range=[0, 5], showgrid=False),
    template="simple_white", # Stile molto pulito per documenti
    legend=dict(x=0.01, y=0.99, bordercolor="Black", borderwidth=1)
)

fig.write_html("tesina_img/grafico_performance.html")
print("✅ Creato tesina_img/grafico_performance.html")


# --- GRAFICO 2: FUNZIONE DI REWARD (APPRENDIMENTO) ---
# Mostra come l'agente migliora (o oscilla) nel tempo
fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=df["episode"], y=df["reward"],
    mode='markers', name='Reward Puntuale',
    marker=dict(color='lightgray', size=5)
))

# Aggiungiamo una media mobile per far vedere il trend
df['reward_ma'] = df['reward'].rolling(window=10).mean()

fig2.add_trace(go.Scatter(
    x=df["episode"], y=df['reward_ma'],
    mode='lines', name='Trend (Media Mobile)',
    line=dict(color='purple', width=3)
))

fig2.update_layout(
    title="Convergenza dell'Apprendimento (Reward)",
    xaxis=dict(title="Episodio"),
    yaxis=dict(title="Reward Cumulativo"),
    template="simple_white"
)

fig2.write_html("tesina_img/grafico_reward.html")
print("✅ Creato tesina_img/grafico_reward.html")

print("\n💡 CONSIGLIO: Apri i file HTML, regola lo zoom come preferisci")
print("   e clicca sull'icona della 📷 (Camera) in alto a destra nel grafico")
print("   per scaricare il PNG in alta definizione per la tesina.")