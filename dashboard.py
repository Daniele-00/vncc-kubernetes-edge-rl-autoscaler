import os
import time
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURAZIONE PAGINA
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Kubernetes RL Autoscaler – Control Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════
# CSS PERSONALIZZATO - DESIGN PULITO E PROFESSIONALE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .material-icons,
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-symbols-sharp {
    font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
    } 
    

    [data-testid="collapsedControl"] svg {
        display: block !important;
    }
    
    /* Background pulito con gradiente sottile */
    .main {
        background: linear-gradient(to bottom, #0a0e27 0%, #1a1f3a 100%);
        padding: 2rem 1rem;
    }
    
    /* Sidebar con tono scuro professionale */
    [data-testid="stSidebar"] {
        background: #0f1419;
        border-right: 1px solid rgba(75, 85, 99, 0.3);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #e5e7eb !important;
        font-weight: 600 !important;
    }
    
    /* Titolo elegante senza effetti esagerati */
    h1 {
        color: #f9fafb !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.02em;
    }
    
    /* Sottotitolo */
    .subtitle {
        text-align: center;
        color: #9ca3af;
        font-size: 1rem;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Metric Cards - design pulito con bordi sottili */
    [data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.7);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(75, 85, 99, 0.4);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
    }
    
    [data-testid="stMetric"] label {
        color: #9ca3af !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f9fafb !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* Buttons - design solido professionale */
    .stButton button {
        background: #4f46e5 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.3px;
    }
    
    .stButton button:hover {
        background: #4338ca !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
    }
    
    /* Radio Buttons */
    [data-testid="stRadio"] {
        background: rgba(17, 24, 39, 0.5);
        padding: 0.75rem;
        border-radius: 8px;
        border: 1px solid rgba(75, 85, 99, 0.3);
    }
    
    [data-testid="stRadio"] label {
        color: #d1d5db !important;
        font-weight: 500 !important;
    }
    
    /* Number Input */
    input[type="number"] {
        background: rgba(17, 24, 39, 0.8) !important;
        color: #f9fafb !important;
        border: 1px solid rgba(75, 85, 99, 0.4) !important;
        border-radius: 8px !important;
        padding: 0.6rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    input[type="number"]:focus {
        border-color: #6366f1 !important;
        outline: none !important;
    }
    
    /* Success/Warning Messages */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border-left: 3px solid #10b981 !important;
        border-radius: 6px !important;
        color: #d1fae5 !important;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        border-left: 3px solid #f59e0b !important;
        border-radius: 6px !important;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.1) !important;
        border-left: 3px solid #3b82f6 !important;
        border-radius: 6px !important;
    }
    
    /* Divider sottile */
    hr {
        border: none;
        height: 1px;
        background: rgba(75, 85, 99, 0.3);
        margin: 1.5rem 0;
    }
    
    /* Plotly Charts */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Status Card nel sidebar */
    .status-card {
        background: rgba(17, 24, 39, 0.8);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid rgba(75, 85, 99, 0.4);
        margin-top: 1rem;
    }
    
    .status-card p {
        margin: 0;
    }
    
    .status-title {
        color: #9ca3af;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-value {
        color: #f9fafb;
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }
    
    /* Footer stats cards */
    .stat-card {
        background: rgba(17, 24, 39, 0.6);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(75, 85, 99, 0.3);
        text-align: center;
    }
    
    .stat-label {
        color: #9ca3af;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0;
    }
    
    .stat-value {
        color: #f9fafb;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0.5rem 0 0 0;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# PERCORSI FILE
# ═══════════════════════════════════════════════════════════════════════════
RESULTS = "results"
LOG = os.path.join(RESULTS, "rl_log.csv")
CMD_FILE = "current_scenario.txt"
CONFIG_FILE = "autoscaler_config.json"

# ═══════════════════════════════════════════════════════════════════════════
# HEADER PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("<h1>⚡ Kubernetes RL Autoscaler</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Real-Time Control Center</p>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR: CONFIGURAZIONE
# ═══════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("### ⚙️ Configurazione")
st.sidebar.markdown("---")
st.sidebar.markdown("#### Soglie SLA")

# Carica configurazione esistente
default_low = 0.08
default_mid = 0.20

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f:
            saved_conf = json.load(f)
            default_low = saved_conf.get("low", 0.08)
            default_mid = saved_conf.get("high", 0.20)
    except:
        pass

# Input utente
low_thr = st.sidebar.number_input(
    "Target Ottimale (s)", 
    value=default_low, 
    step=0.01, 
    format="%.3f",
    help="Modifica questo valore per rendere l'AI più o meno esigente."
)

mid_thr = st.sidebar.number_input(
    "Soglia Critica (s)", 
    value=default_mid, 
    step=0.01, 
    format="%.3f",
    help="Se la latenza supera questo valore, l'AI cercherà di scalare UP."
)

# Salva configurazione
current_conf = {"low": low_thr, "high": mid_thr}
with open(CONFIG_FILE, "w") as f:
    json.dump(current_conf, f)

st.sidebar.success(f"Configurato: {low_thr}s / {mid_thr}s")

st.sidebar.markdown("---")
st.sidebar.markdown("#### Dashboard Settings")

refresh_sec = st.sidebar.slider("Refresh Rate (s)", 1, 10, 2, help="Intervallo di aggiornamento automatico della dashboard")
window = st.sidebar.slider("Smoothing Window", 1, 10, 1, help="Finestra di smoothing per le metriche visualizzate")
max_points = st.sidebar.slider("Max Episodes", 20, 200, 50, help="Numero massimo di episodi da visualizzare nei grafici")

st.sidebar.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR: GENERATORE TRAFFICO
# ═══════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("### 🎮 Traffic Generator")

modo_scelto = st.sidebar.radio(
    "Load Scenario:",
    ("Calma", "Spike", "Onda", "Stop"),
    help="Seleziona il pattern di traffico da simulare"
)

if st.sidebar.button("Apply Scenario", use_container_width=True):
    with open(CMD_FILE, "w") as f:
        f.write(modo_scelto)
    st.sidebar.success(f"Attivato: {modo_scelto}")

# Stato corrente
current_mode = "Sconosciuto"
if os.path.exists(CMD_FILE):
    with open(CMD_FILE, "r") as f:
        current_mode = f.read().strip()

mode_emoji = {
    "Calma": "🟢",
    "Spike": "🔴",
    "Onda": "🟡",
    "Stop": "⚫",
    "Sconosciuto": "⚪"
}

st.sidebar.markdown(f"""
<div class='status-card'>
    <p class='status-title'>Current Status</p>
    <p class='status-value'>{mode_emoji.get(current_mode, '⚪')} {current_mode}</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# CARICAMENTO DATI
# ═══════════════════════════════════════════════════════════════════════════
if not os.path.exists(LOG):
    st.warning("⚠️ In attesa di dati... Assicurati che 'autoscaler/rl_autoscaler.py' sia avviato.")
    time.sleep(2)
    st.rerun()

try:
    df = pd.read_csv(LOG)
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.tail(max_points).reset_index(drop=True)
except Exception as e:
    st.error(f"❌ Errore lettura CSV: {e}")
    st.stop()

if df.empty:
    st.info("⏳ Attendo primo episodio...")
    time.sleep(2)
    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# ELABORAZIONE DATI
# ═══════════════════════════════════════════════════════════════════════════
df["latency_roll"] = df["latency"].rolling(window=window, min_periods=1).mean()
df["reward_roll"] = df["reward"].rolling(window=window, min_periods=1).mean()

last_lat = df["latency"].iloc[-1]
last_rep = df["replicas"].iloc[-1]
last_rew = df["reward"].iloc[-1]

lat_delta = None
rew_delta = None
if len(df) > 1:
    lat_delta = last_lat - df["latency"].iloc[-2]
    rew_delta = last_rew - df["reward"].iloc[-2]

# ═══════════════════════════════════════════════════════════════════════════
# KPI CARDS
# ═══════════════════════════════════════════════════════════════════════════
c1, c2, c3 = st.columns(3)

with c1:
    delta_str = f"{lat_delta:.3f} s" if lat_delta is not None else None
    st.metric("Latenza Attuale", f"{last_lat:.3f} s", delta=delta_str, delta_color="inverse")

with c2:
    st.metric("Repliche Attive", f"{int(last_rep)}")

with c3:
    delta_str = f"{rew_delta:.2f}" if rew_delta is not None else None
    st.metric("Reward Score", f"{last_rew:.2f}", delta=delta_str)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# GRAFICI PRINCIPALI
# ═══════════════════════════════════════════════════════════════════════════
colA, colB = st.columns([2, 1])

with colA:
    fig = go.Figure()
    
    # Barre repliche
    fig.add_trace(go.Bar(
        x=df["episode"], 
        y=df["replicas"],
        name="Repliche",
        opacity=0.35,
        yaxis="y2",
        marker=dict(
            color='#6366f1',
            line=dict(color='#4f46e5', width=1)
        ),
        hovertemplate='<b>Ep. %{x}</b><br>Repliche: %{y}<extra></extra>'
    ))
    
    # Linea latenza
    fig.add_trace(go.Scatter(
        x=df["episode"], 
        y=df["latency_roll"],
        mode="lines+markers",
        name="Latenza",
        line=dict(width=3, color="#f59e0b"),
        marker=dict(size=6, color="#fbbf24"),
        hovertemplate='<b>Ep. %{x}</b><br>Latenza: %{y:.3f}s<extra></extra>'
    ))
    
    # Soglie
    fig.add_hline(
        y=low_thr, 
        line_dash="dash", 
        line_color="#10b981", 
        line_width=2,
        annotation_text=f"Target ({low_thr}s)",
        annotation_position="right"
    )
    
    fig.add_hline(
        y=mid_thr, 
        line_dash="dash", 
        line_color="#ef4444", 
        line_width=2,
        annotation_text=f"Critico ({mid_thr}s)",
        annotation_position="right"
    )
    
    fig.update_layout(
        title=dict(
            text="Performance vs Risorse",
            font=dict(size=18, color="#e5e7eb", family="Inter"),
            x=0
        ),
        xaxis=dict(
            title="Episodio",
            title_font=dict(size=12, color="#9ca3af"),
            tickfont=dict(color="#d1d5db", size=10),
            rangemode="tozero",
            gridcolor="rgba(75, 85, 99, 0.2)",
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            title="Latenza (s)",
            title_font=dict(size=12, color="#9ca3af"),
            tickfont=dict(color="#d1d5db", size=10),
            rangemode="tozero",
            gridcolor="rgba(75, 85, 99, 0.2)",
            showgrid=True,
            zeroline=False
        ),
        yaxis2=dict(
            title="Repliche",
            title_font=dict(size=12, color="#9ca3af"),
            tickfont=dict(color="#d1d5db", size=10),
            overlaying="y",
            side="right",
            range=[0, 5],
            gridcolor="rgba(75, 85, 99, 0.1)",
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11, color="#d1d5db"),
            bgcolor="rgba(17, 24, 39, 0.8)",
            bordercolor="rgba(75, 85, 99, 0.3)",
            borderwidth=1
        ),
        plot_bgcolor="rgba(10, 14, 39, 0.5)",
        paper_bgcolor="rgba(10, 14, 39, 0)",
        height=420,
        margin=dict(l=50, r=50, t=60, b=40),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, width='stretch', key=f"main_{time.time()}")

with colB:
    fig_r = go.Figure()
    
    # Area sotto la curva
    fig_r.add_trace(go.Scatter(
        x=df["episode"], 
        y=df["reward_roll"],
        mode="lines",
        name="Reward",
        line=dict(width=0),
        fillcolor="rgba(139, 92, 246, 0.15)",
        fill='tozeroy',
        showlegend=False
    ))
    
    # Linea reward
    fig_r.add_trace(go.Scatter(
        x=df["episode"], 
        y=df["reward_roll"],
        mode="lines+markers",
        name="Reward",
        line=dict(color="#8b5cf6", width=3),
        marker=dict(size=6, color="#a78bfa"),
        hovertemplate='<b>Ep. %{x}</b><br>Reward: %{y:.2f}<extra></extra>'
    ))
    
    fig_r.update_layout(
        title=dict(
            text="Learning Progress",
            font=dict(size=16, color="#e5e7eb", family="Inter"),
            x=0
        ),
        xaxis=dict(
            title="Episodio",
            title_font=dict(size=11, color="#9ca3af"),
            tickfont=dict(color="#d1d5db", size=10),
            rangemode="tozero",
            gridcolor="rgba(75, 85, 99, 0.2)",
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            title="Score",
            title_font=dict(size=11, color="#9ca3af"),
            tickfont=dict(color="#d1d5db", size=10),
            gridcolor="rgba(75, 85, 99, 0.2)",
            showgrid=True,
            zeroline=False
        ),
        plot_bgcolor="rgba(10, 14, 39, 0.5)",
        paper_bgcolor="rgba(10, 14, 39, 0)",
        height=420,
        margin=dict(l=50, r=30, t=60, b=40),
        hovermode='x unified',
        showlegend=False
    )
    
    st.plotly_chart(fig_r, width='stretch', key=f"reward_{time.time()}")

# ═══════════════════════════════════════════════════════════════════════════
# FOOTER CON STATISTICHE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

avg_lat = df["latency"].mean()
avg_rep = df["replicas"].mean()
total_episodes = len(df)
cumulative_reward = df["reward"].sum()

with col1:
    st.markdown(f"""
    <div class='stat-card'>
        <p class='stat-label'>Latenza Media</p>
        <p class='stat-value'>{avg_lat:.3f}s</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='stat-card'>
        <p class='stat-label'>Repliche Medie</p>
        <p class='stat-value'>{avg_rep:.1f}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='stat-card'>
        <p class='stat-label'>Episodi Totali</p>
        <p class='stat-value'>{total_episodes}</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='stat-card'>
        <p class='stat-label'>Reward Cumulativo</p>
        <p class='stat-value'>{cumulative_reward:.1f}</p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# AUTO-REFRESH
# ═══════════════════════════════════════════════════════════════════════════
time.sleep(refresh_sec)
st.rerun()