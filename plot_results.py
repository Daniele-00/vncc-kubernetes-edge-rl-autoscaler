import os
import pandas as pd
import plotly.graph_objects as go

os.makedirs("results", exist_ok=True)
df = pd.read_csv("results/rl_log.csv")

# Funzione per creare grafici
def create_plot(df, x_col, y_col, title, y_label, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col],
                             mode="lines+markers", 
                             name=y_label,
                             line=dict(color=color, width=2)))
    
    fig.update_layout(
        title=title,
        xaxis_title="Episodio",
        yaxis_title=y_label,
        template="plotly_white", # Sfondo bianco per la stampa
        xaxis=dict(rangemode="nonnegative"), # Assicura che l'asse x inizi da 0
        font=dict(family="Serif", size=14)   
    )
    return fig

# 1. Latenza
fig1 = create_plot(df, "episode", "latency", "Latenza nel Tempo", "Latenza (s)", "#1f77b4")
# Salvataggio statico per la tesina (PNG alta risoluzione)
fig1.write_image("results/grafico_latenza.png", scale=3) 

# 2. Repliche
fig2 = create_plot(df, "episode", "replicas", "Scaling delle Repliche", "N. Repliche", "#ff7f0e")
fig2.write_image("results/grafico_repliche.png", scale=3)

# 3. Reward 
# Aggiunta della media mobile per evidenziare il trend
df['reward_ma'] = df['reward'].rolling(window=5).mean()
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=df["episode"], y=df["reward"], mode="markers", name="Reward Puntuale", opacity=0.3))
fig3.add_trace(go.Scatter(x=df["episode"], y=df['reward_ma'], mode="lines", name="Media Mobile (Trend)", line=dict(color="green", width=3)))
fig3.update_layout(title="Convergenza dell'Apprendimento (Reward)", template="plotly_white", xaxis=dict(rangemode="nonnegative"))
fig3.write_image("results/grafico_reward_learning.png", scale=3)

print("Grafici PNG generati in 'results/'")