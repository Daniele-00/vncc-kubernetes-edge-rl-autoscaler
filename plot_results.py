import os
import pandas as pd
import plotly.graph_objects as go

os.makedirs("results", exist_ok=True)

# Carica il log del RL
df = pd.read_csv("results/rl_log.csv")

# Grafico 1: latenza nel tempo
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=df["episode"], y=df["latency"],
                          mode="lines+markers", name="Latency (s)"))
fig1.update_layout(title="Latenza nel tempo (RL Autoscaler)",
                   xaxis_title="Episodio", yaxis_title="Latenza (s)")

# Grafico 2: numero di repliche
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df["episode"], y=df["replicas"],
                          mode="lines+markers", name="Repliche"))
fig2.update_layout(title="Numero di repliche nel tempo",
                   xaxis_title="Episodio", yaxis_title="Repliche")

# Grafico 3: reward
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=df["episode"], y=df["reward"],
                          mode="lines+markers", name="Reward"))
fig3.update_layout(title="Reward nel tempo",
                   xaxis_title="Episodio", yaxis_title="Reward")

# 👉 invece di fig.show(), salviamo in HTML
fig1.write_html("results/rl_latency.html", include_plotlyjs="cdn")
fig2.write_html("results/rl_replicas.html", include_plotlyjs="cdn")
fig3.write_html("results/rl_reward.html", include_plotlyjs="cdn")

print("Grafici salvati in:")
print("  results/rl_latency.html")
print("  results/rl_replicas.html")
print("  results/rl_reward.html")
print("Aprili dal browser in Windows.")
