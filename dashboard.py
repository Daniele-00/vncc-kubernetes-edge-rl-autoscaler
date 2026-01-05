# dashboard_ultra.py
import os
import time
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Kubernetes RL Autoscaler – Dashboard",
    page_icon="🤖",
    layout="wide"
)

RESULTS = "results"
LOG = os.path.join(RESULTS, "rl_log.csv")
os.makedirs(RESULTS, exist_ok=True)

st.title("🤖 Kubernetes RL Autoscaler – Dashboard")
st.caption("Dashboard live con soglie, colori dinamici e grafici combinati.")

# Sidebar: controlli
st.sidebar.header("Parametri visualizzazione")
low_thr  = st.sidebar.number_input("Soglia latenza bassa (s)", value=0.08, step=0.01, format="%.2f")
mid_thr  = st.sidebar.number_input("Soglia latenza media (s)", value=0.20, step=0.01, format="%.2f")
refresh  = st.sidebar.slider("Refresh (secondi)", 1, 10, 2)
window   = st.sidebar.slider("Media mobile (episodi)", 1, 20, 5)
st.sidebar.markdown("---")

# Traffic control
st.sidebar.header("Controllo Traffico")
modo_scelto = st.sidebar.radio(
    "Scegli Scenario:",
    ("Calma", "Spike", "Onda", "Stop")
)

# Pulsante per applicare lo scenario
if st.sidebar.button("Applica Scenario"):
    with open("current_scenario.txt", "w") as f:
        f.write(modo_scelto)
    st.sidebar.success(f"Attivato: {modo_scelto}")
    
st.sidebar.write("Assicurati che `autoscaler/rl_autoscaler.py` stia girando e scriva `results/rl_log.csv`.")

placeholder = st.empty()

def latency_color(lat):
    if lat < low_thr:
        return "#22c55e"  # verde
    elif lat < mid_thr:
        return "#f59e0b"  # arancione
    return "#ef4444"      # rosso

while True:
    try:
        df = pd.read_csv(LOG)
        df.columns = [c.strip().lower() for c in df.columns]
        if "episode" not in df.columns:
            df["episode"] = range(len(df))
    except Exception:
        with placeholder.container():
            st.warning("In attesa di dati… (manca results/rl_log.csv?)")
        time.sleep(refresh)
        continue

    # rolling per linee più pulite
    df["latency_roll"]  = df["latency"].rolling(window=window, min_periods=1).mean()
    df["replicas_roll"] = df["replicas"].rolling(window=window, min_periods=1).mean()
    df["reward_roll"]   = df["reward"].rolling(window=window, min_periods=1).mean()

    avg_lat  = df["latency"].mean()
    avg_rep  = df["replicas"].mean()
    avg_rew  = df["reward"].mean()
    last_lat = df["latency"].iloc[-1]
    last_rep = df["replicas"].iloc[-1]
    last_rew = df["reward"].iloc[-1]

    with placeholder.container():
        # KPI
        c1, c2, c3 = st.columns(3)
        c1.metric("Latenza media", f"{avg_lat:.3f}s", f"{last_lat:.3f}s")
        c2.metric("Repliche medie", f"{avg_rep:.2f}", f"{last_rep}")
        c3.metric("Reward medio", f"{avg_rew:.2f}", f"{last_rew:.2f}")

        st.markdown("---")

        colA, colB = st.columns([2, 1])

        # Grafico combinato (latency + replicas)
        with colA:
            fig = go.Figure()

            # barre per repliche (asse secondario)
            fig.add_trace(go.Bar(
                x=df["episode"], y=df["replicas"],
                name="Repliche", opacity=0.35, yaxis="y2"
            ))

            # linea latenza
            fig.add_trace(go.Scatter(
                x=df["episode"], y=df["latency_roll"],
                mode="lines+markers", name="Latenza (rolling)"
            ))

            # soglie orizzontali
            for thr, name, color in [
                (low_thr, "Soglia bassa", "#22c55e"),
                (mid_thr, "Soglia media", "#f59e0b"),
            ]:
                fig.add_hline(y=thr, line_dash="dot", line_color=color, annotation_text=name)

            fig.update_layout(
                title="Latenza & Repliche",
                xaxis_title="Episodio",
                yaxis=dict(title="Latenza [s]"),
                yaxis2=dict(title="Repliche [#]", overlaying="y", side="right"),
                template="plotly_white",
                legend=dict(orientation="h", y=1.1, x=0)
            )

            # punto finale colorato in base alla latenza
            fig.add_trace(go.Scatter(
                x=[df["episode"].iloc[-1]],
                y=[df["latency_roll"].iloc[-1]],
                mode="markers",
                marker=dict(size=14, color=latency_color(last_lat)),
                name="Stato attuale"
            ))

            # Key univoca per forzare il refresh del grafico
            st.plotly_chart(fig, use_container_width=True, theme="streamlit", key=f"latency_replicas_chart_{time.time()}")

        # Reward
        with colB:
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatter(
                x=df["episode"], y=df["reward_roll"],
                mode="lines+markers", name="Reward (rolling)"
            ))
            fig_r.update_layout(
                title="Reward",
                xaxis_title="Episodio",
                yaxis_title="Reward",
                template="plotly_white",
            )
            # key univoca anche qui
            st.plotly_chart(fig_r, use_container_width=True, theme="streamlit", key=f"reward_chart_{time.time()}")

        # Tabella ultime decisioni
        st.subheader("Ultime decisioni")
        st.dataframe(
            df.tail(10)[["episode", "latency", "replicas", "reward"]],
            use_container_width=True
        )

    time.sleep(refresh)
