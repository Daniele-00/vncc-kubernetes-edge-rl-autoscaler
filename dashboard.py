import streamlit as st
import pandas as pd
import time

st.set_page_config(
    page_title="Kubernetes RL Autoscaler Dashboard",
    page_icon="☸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("☸️ Kubernetes RL Autoscaler – Live Dashboard")
st.markdown(
    "Monitoraggio in tempo reale delle performance del sistema di autoscaling basato su **Reinforcement Learning (Q-Learning)**. "
    "I dati vengono letti dal file di log generato dallo script `rl_autoscaler.py`."
)

# ---- Stile grafico moderno ----
st.markdown("""
<style>
body {
    background-color: #f9f9f9;
}
h1, h2, h3 {
    color: #1E3A8A;
}
</style>
""", unsafe_allow_html=True)

# ---- Placeholder grafici e metriche ----
placeholder = st.empty()

# Loop di aggiornamento automatico
while True:
    try:
        df = pd.read_csv("results/rl_log.csv")
        if df.empty:
            st.warning("In attesa di dati dal file `results/rl_log.csv`...")
            time.sleep(2)
            continue
    except FileNotFoundError:
        st.error("⚠️ File `results/rl_log.csv` non trovato. Avvia prima `rl_autoscaler.py`.")
        time.sleep(3)
        continue

    avg_latency = df["latency"].mean()
    avg_replicas = df["replicas"].mean()
    avg_reward = df["reward"].mean()

    with placeholder.container():
        # --- Riepilogo metriche ---
        st.subheader("📊 Metriche principali")
        col1, col2, col3 = st.columns(3)
        col1.metric("Latenza media", f"{avg_latency:.3f} s")
        col2.metric("Repliche medie", f"{avg_replicas:.2f}")
        col3.metric("Reward medio", f"{avg_reward:.2f}")

        st.markdown("---")

        # --- Grafici ---
        st.subheader("📈 Andamento temporale")

        colA, colB = st.columns(2)

        with colA:
            st.line_chart(df[["latency"]], height=300, use_container_width=True)
            st.caption("Latenza media per episodio (s)")

        with colB:
            st.line_chart(df[["replicas"]], height=300, use_container_width=True)
            st.caption("Numero di repliche per episodio")

        st.line_chart(df[["reward"]], height=300, use_container_width=True)
        st.caption("Reward per episodio")

    time.sleep(2)
