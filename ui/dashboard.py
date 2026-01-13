import os, base64
import time
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURAZIONE PAGINA
# ═══════════════════════════════════════════════════════════════════════════
# Page config 
logo_path = None
candidate = os.path.join("logo", "logo.png")
if os.path.exists(candidate):
    logo_path = candidate
else:
    try:
        if os.path.isdir("logo"):
            for fname in os.listdir("logo"):
                if fname.lower().endswith((".png", ".jpg", ".jpeg", ".svg", ".ico")):
                    logo_path = os.path.join("logo", fname)
                    break
    except Exception:
        logo_path = None

st.set_page_config(
    page_title="Kubernetes RL Autoscaler Dashboard",
    page_icon=logo_path or "⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Export logo path for use elsewhere in the app
LOGO_PATH = logo_path

# ═══════════════════════════════════════════════════════════════════════════
# CSS PERSONALIZZATO - DESIGN PULITO E PROFESSIONALE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .material-icons,
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-symbols-sharp {
    font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
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
    
    /* Titolo */
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
    
    /* Metric Cards */
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
    
    /* Buttons */
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
RL_LOG = os.path.join(RESULTS, "rl_eval_log2.csv")
BASE_LOG = os.path.join(RESULTS, "baseline_log.csv")
CMD_FILE = "current_scenario.txt"
CONFIG_FILE = "autoscaler_config.json"

# ═══════════════════════════════════════════════════════════════════════════
# HEADER PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════
def img_to_data_uri(path: str) -> str:
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{ext};base64,{b64}"

st.markdown("""
<style>
.header-wrap{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:14px;
  margin-top: 6px;
  margin-bottom: 2px;
}
.header-logo{
  height:80px;
  width:80px;
  border-radius:16px;
  box-shadow: 0 8px 18px rgba(0,0,0,.35);
}
.header-title{
  margin:0;
  color:#f9fafb;
  font-size:3rem;
  font-weight:800;
  letter-spacing:-0.02em;
}
.header-subtitle{
  text-align:center;
  color:#9ca3af;
  font-size:1rem;
  margin-top: 6px;
  font-weight:500;
}
</style>
""", unsafe_allow_html=True)

if os.path.exists(LOGO_PATH):
    logo_uri = img_to_data_uri(LOGO_PATH)
    st.markdown(
        f"""
        <div class="header-wrap">
            <img class="header-logo" src="{logo_uri}" />
            <h1 class="header-title">Kubernetes RL Autoscaler</h1>
        </div>
        <div class="header-subtitle">Real-Time Control Center</div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown("<h1 class='header-title'>Kubernetes RL Autoscaler</h1>", unsafe_allow_html=True)
    st.markdown("<div class='header-subtitle'>Real-Time Control Center</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR: SELEZIONE MODALITÀ
# ═══════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("### Sorgente Dati")
data_source = st.sidebar.radio(
    "Visualizzazione:",
    ("RL AUTOSCALER", " Baseline AUTOSCALER ", " Confronto Diretto"),
    help="Seleziona quale sistema vuoi monitorare"
)

st.sidebar.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR: CONFIGURAZIONE
# ═══════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("### Configurazione Autoscaler")
st.sidebar.markdown("#### Soglie SLA")

# Carica configurazione esistente
default_low = 0.25
default_mid = 0.35

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f:
            saved_conf = json.load(f)
            default_low = saved_conf.get("low", 0.25)
            default_mid = saved_conf.get("high", 0.35)
    except:
        pass

# Input utente
low_thr = st.sidebar.number_input(
    "Target Ottimale (s)", 
    value=default_low, 
    step=0.01, 
    format="%.3f",
    help="Se la latenza è inferiore a questo valore, l'autoscaler cercherà di scalare DOWN."
)

mid_thr = st.sidebar.number_input(
    "Soglia Critica (s)", 
    value=default_mid, 
    step=0.01, 
    format="%.3f",
    help="Se la latenza supera questo valore, l'autoscaler cercherà di scalare UP."
)

# Salva configurazione
current_conf = {"low": low_thr, "high": mid_thr}
with open(CONFIG_FILE, "w") as f:
    json.dump(current_conf, f)

st.sidebar.success(f"Configurato: {low_thr}s / {mid_thr}s")


st.sidebar.markdown("---")
st.sidebar.markdown("#### Impostazioni Dashboard")

refresh_sec = st.sidebar.slider("Refresh Rate (s)", 1, 10, 2, help="Intervallo di aggiornamento automatico della dashboard")
window = st.sidebar.slider("Smoothing Window", 1, 10, 1, help="Finestra di smoothing per le metriche visualizzate")
max_points = st.sidebar.slider("Max Episodes", 20, 250, 150, help="Numero massimo di episodi da visualizzare nei grafici")

st.sidebar.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR: GENERATORE TRAFFICO
# ═══════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("### Generatore Traffico")

modo_scelto = st.sidebar.radio(
    "Load Scenario:",
    ("Calma", "Picco", "Onda", "Stop"),
    help="Seleziona il pattern di traffico da simulare"
)

if st.sidebar.button("Applica Scenario", width='stretch'):
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
    "Picco": "🔴",
    "Onda": "🟡",
    "Stop": "⚫",
    "Sconosciuto": "⚪"
}

st.sidebar.markdown(f"""
<div class='status-card'>
    <p class='status-title'>Stato Corrente</p>
    <p class='status-value'>{mode_emoji.get(current_mode, '⚪')} {current_mode}</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR: CONTROLLO PAUSA
# ═══════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("### ⏸️ Controllo Refresh Dashboard")
pausa = st.sidebar.checkbox("Pausa Dashboard", value=False, help="Metti in pausa per analizzare i grafici senza refresh")

if pausa:
    st.sidebar.info("Dashboard in pausa")
    
# ═══════════════════════════════════════════════════════════════════════════
# FUNZIONE CARICAMENTO DATI
# ═══════════════════════════════════════════════════════════════════════════
def load_data(filepath):
    if not os.path.exists(filepath):
        return pd.DataFrame()
    try:
        df = pd.read_csv(filepath)
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# ═══════════════════════════════════════════════════════════════════════════
# CARICAMENTO DATI IN BASE ALLA MODALITÀ
# ═══════════════════════════════════════════════════════════════════════════

# Inizializza variabili per evitare NameError
df = pd.DataFrame()
df_rl = pd.DataFrame()
df_baseline = pd.DataFrame()

if data_source == " Confronto Diretto":
    # ═══════════════════════════════════════════════════════════════════════════
    # MODALITÀ CONFRONTO AVANZATO 
    # ═══════════════════════════════════════════════════════════════════════════
    
    # 1. Caricamento Dati
    df_rl = load_data(RL_LOG)
    df_baseline = load_data(BASE_LOG)
    
    if df_rl.empty and df_baseline.empty:
        st.warning("⚠️ Nessun dato disponibile. Avvia i test per generare i CSV.")
        st.stop()
        
    st.markdown("### Analisi Statistiche")

    # 2. CALCOLO KPI MATEMATICI
    # Gestione casi vuoti
    mean_lat_rl = df_rl['latency'].mean() if not df_rl.empty else 0
    mean_lat_bl = df_baseline['latency'].mean() if not df_baseline.empty else 0
    
    mean_rep_rl = df_rl['replicas'].mean() if not df_rl.empty else 0
    mean_rep_bl = df_baseline['replicas'].mean() if not df_baseline.empty else 0
    
    # Calcolo Violazioni SLA (Quante volte latency > mid_thr)
    sla_viol_rl = len(df_rl[df_rl['latency'] > mid_thr]) if not df_rl.empty else 0
    sla_viol_bl = len(df_baseline[df_baseline['latency'] > mid_thr]) if not df_baseline.empty else 0

    # Calcolo Delta Percentuali (Risparmio/Miglioramento)
    # Se Baseline è 0, evito divisione per zero
    delta_lat_pct = ((mean_lat_rl - mean_lat_bl) / mean_lat_bl * 100) if mean_lat_bl > 0 else 0
    delta_rep_pct = ((mean_rep_rl - mean_rep_bl) / mean_rep_bl * 100) if mean_rep_bl > 0 else 0
    
    # 3. VISUALIZZAZIONE KPI (COLONNE)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric(
            "Latenza Media", 
            f"{mean_lat_rl:.3f} s", 
            f"{delta_lat_pct:.1f}% vs Base", 
            delta_color="inverse" # Verde se scende (Latenza minore è meglio)
        )
    
    with kpi2:
        st.metric(
            "Costo Medio (Repliche)", 
            f"{mean_rep_rl:.2f}", 
            f"{delta_rep_pct:.1f}% vs Base", 
            delta_color="inverse" # Verde se scende (Meno repliche è meglio)
        )
        
    with kpi3:
        diff_viol = sla_viol_rl - sla_viol_bl
        st.metric(
            "Violazioni SLA (Totali)", 
            f"{sla_viol_rl}", 
            f"{diff_viol} vs Base",
            delta_color="inverse" # Verde se ne ha meno
        )

    with kpi4:
        # Calcolo SLA (Percentuale episodi sotto soglia SLA)
        TARGET_SLA = low_thr  # Usa la soglia configurata nella sidebar

        # Calcolo SLA Met
        sla_met_rl = (df_rl['latency'] <= TARGET_SLA).mean() 
        sla_met_bl = (df_baseline['latency'] <= TARGET_SLA).mean()

        # Calcolo Efficienza: % Successo diviso Costo Medio
        eff_rl = sla_met_rl / mean_rep_rl if mean_rep_rl > 0 else 0
        eff_bl = sla_met_bl / mean_rep_bl if mean_rep_bl > 0 else 0

        # Delta percentuale
        delta_eff = ((eff_rl - eff_bl) / eff_bl * 100) if eff_bl > 0 else 0

        st.metric(
            label="SLA Yield / Replica", 
            value=f"{eff_rl:.3f}", 
            delta=f"{delta_eff:.1f}%",
            delta_color="normal",
            help=f"Indica la % di rispetto SLA ottenuta per ogni singola replica media attiva. (Target < {TARGET_SLA}s)"
        )

    st.markdown("---")
        # 4bis. KPI AGGREGATI IN FORMA GRAFICA (BAR CHART)
    st.subheader("Confronto KPI Aggregati")

    # Converto in percentuale la quota di episodi sotto la soglia SLA
    sla_met_rl_pct = sla_met_rl * 100.0 if mean_lat_rl > 0 else 0.0
    sla_met_bl_pct = sla_met_bl * 100.0 if mean_lat_bl > 0 else 0.0

    col_kpi1, col_kpi2 = st.columns(2)

    # --- Grafico 1: Latenza media e Repliche medie ---
    with col_kpi1:
        fig_kpi1 = go.Figure()

        x_labels_1 = ["Latenza media (s)", "Repliche medie"]
        baseline_vals_1 = [mean_lat_bl, mean_rep_bl]
        rl_vals_1 = [mean_lat_rl, mean_rep_rl]

        fig_kpi1.add_trace(go.Bar(
            x=x_labels_1,
            y=baseline_vals_1,
            name="Baseline",
            marker=dict(color="#ef4444")
        ))
        fig_kpi1.add_trace(go.Bar(
            x=x_labels_1,
            y=rl_vals_1,
            name="RL Agent",
            marker=dict(color="#6366f1")
        ))

        fig_kpi1.update_layout(
            title="Prestazioni e costo medio",
            barmode="group",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e5e7eb"),
            yaxis_title="Valore"
        )

        st.plotly_chart(fig_kpi1, width='stretch')

    # --- Grafico 2: SLA Met e SLA Yield/Replica ---
    with col_kpi2:
        fig_kpi2 = go.Figure()

        x_labels_2 = [f"% episodi ≤ {low_thr:.3f}s", "SLA Yield / Replica"]
        baseline_vals_2 = [sla_met_bl_pct, eff_bl]
        rl_vals_2 = [sla_met_rl_pct, eff_rl]

        fig_kpi2.add_trace(go.Bar(
            x=x_labels_2,
            y=baseline_vals_2,
            name="Baseline",
            marker=dict(color="#ef4444")
        ))
        fig_kpi2.add_trace(go.Bar(
            x=x_labels_2,
            y=rl_vals_2,
            name="RL Agent",
            marker=dict(color="#6366f1")
        ))

        fig_kpi2.update_layout(
            title="Affidabilità SLA e Efficienza",
            barmode="group",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e5e7eb"),
            yaxis_title="Valore (%, score)"
        )

        st.plotly_chart(fig_kpi2, width='stretch')
    st.markdown("---")

    # 4. GRAFICI STATISTICI (BOX PLOT)
    st.subheader(" Analisi Distribuzione e Stabilità")
    st.caption("Box Plot delle metriche chiave per valutare la stabilità e l'affidabilità di ciascun autoscaler.")

    tab_dist, tab_ts = st.tabs([" Distribuzione", " Serie Temporale "])

    with tab_dist:
        col_box1, col_box2 = st.columns(2)
        
        with col_box1:
            # Box Plot Latenza
            fig_box_lat = go.Figure()
            if not df_baseline.empty:
                fig_box_lat.add_trace(go.Box(y=df_baseline["latency"], name="Baseline", marker_color="#ef4444", boxpoints='outliers'))
            if not df_rl.empty:
                fig_box_lat.add_trace(go.Box(y=df_rl["latency"], name="RL Agent", marker_color="#6366f1", boxpoints='outliers'))
            
            fig_box_lat.add_hline(y=mid_thr, line_dash="dot", line_color="orange", annotation_text="SLA Limit")
            fig_box_lat.update_layout(title="Distribuzione Latenza", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e5e7eb"))
            st.plotly_chart(fig_box_lat, width='stretch')

        with col_box2:
            # Box Plot Repliche
            fig_box_rep = go.Figure()
            if not df_baseline.empty:
                fig_box_rep.add_trace(go.Box(y=df_baseline["replicas"], name="Baseline", marker_color="#ef4444"))
            if not df_rl.empty:
                fig_box_rep.add_trace(go.Box(y=df_rl["replicas"], name="RL Agent", marker_color="#6366f1"))
            
            fig_box_rep.update_layout(title="Utilizzo Risorse", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e5e7eb"))
            st.plotly_chart(fig_box_rep, width='stretch')

    with tab_ts:
        # 5. SERIE TEMPORALE MIGLIORATA (TIME-BASED)
        st.markdown("### Serie Temporale Dettagliata")
        
        use_smooth = st.checkbox("Applica Smoothing", value=True)
        w_smooth = window if use_smooth else 1

        fig_ts = go.Figure()

        # --- A. PREPARAZIONE DATI BASELINE ---
        if not df_baseline.empty:
            # 1. Converti stringa in datetime
            df_baseline["timestamp"] = pd.to_datetime(df_baseline["timestamp"])
            # 2. Calcola i secondi trascorsi dall'inizio (T0)
            start_time_base = df_baseline["timestamp"].iloc[0]
            df_baseline["elapsed_time"] = (df_baseline["timestamp"] - start_time_base).dt.total_seconds()
            
            # 3. Smoothing
            y_base = df_baseline["latency"].rolling(window=w_smooth, min_periods=1).mean()
            
            # 4. Plot usando il TEMPO (elapsed_time) invece dell'episodio
            fig_ts.add_trace(go.Scatter(
                x=df_baseline["elapsed_time"], 
                y=y_base,
                name="Baseline Autoscaler", 
                line=dict(color="#fb923c", width=2), 
                opacity=0.8
            ))

        # --- B. PREPARAZIONE DATI RL AGENT ---
        if not df_rl.empty:
            # 1. Converti stringa in datetime
            df_rl["timestamp"] = pd.to_datetime(df_rl["timestamp"])
            # 2. Calcola i secondi trascorsi dall'inizio (T0)
            start_time_rl = df_rl["timestamp"].iloc[0]
            df_rl["elapsed_time"] = (df_rl["timestamp"] - start_time_rl).dt.total_seconds()
            
            # 3. Smoothing
            y_rl = df_rl["latency"].rolling(window=w_smooth, min_periods=1).mean()
            
            # 4. Plot usando il TEMPO
            fig_ts.add_trace(go.Scatter(
                x=df_rl["elapsed_time"], 
                y=y_rl,
                name="RL Agent", 
                line=dict(color="#6366f1", width=3), 
                opacity=1.0
            ))

        # --- C. AREE DI SFONDO PER LE FASI DI CARICO ---
        # Definizione fasi con colori e durate
        phases = [
            # 1. Verde Acqua: Inizio tranquillo
            ("Calma Iniziale", 120, "rgba(0, 255, 200, 0.1)"),
            
            # 2. Giallo Acceso: Inizia il carico 
            ("Prima Onda", 300, "rgba(255, 255, 0, 0.1)"),
            
            # 3. Arancione: Primo pericolo
            ("Primo Spike", 300, "rgba(255, 140, 0, 0.15)"),
            
            # 4. Azzurro Ciano: Pausa 
            ("Recupero", 60, "rgba(0, 255, 255, 0.1)"),
            
            # 5. Rosso Fuoco: Picco
            ("Secondo Spike", 300, "rgba(255, 50, 50, 0.2)"), 
            
            # 6. Viola: Onda secondaria
            ("Seconda Onda", 120, "rgba(255, 0, 255, 0.1)"),
            
            # 7. Rosa: Ultimo picco
            ("Terzo Spike", 120, "rgba(255, 20, 147, 0.15)"),
            
            # 8. Blu: Calma finale
            ("Calma Finale", 160, "rgba(65, 105, 225, 0.1)"),
            
            # 9. Grigio: Stop traffico
            ("Stop Traffico", 10, "rgba(128, 128, 128, 0.1)"),
        ]
        
        current_time = 0
        for name, duration, color in phases:
            fig_ts.add_vrect(
                x0=current_time, x1=current_time + duration,
                fillcolor=color, layer="below", line_width=0,
                annotation_text=name, annotation_position="top left"
            )
            current_time += duration

        # --- D. SOGLIE ORIZZONTALI (SLA) ---
        fig_ts.add_hline(y=mid_thr, line_width=2, line_dash="longdash", line_color="#ff0000", 
                         annotation_text="SLA Limit", annotation_position="top right")
        
        fig_ts.add_hline(
            y=low_thr,
            line_width=1,           
            line_dash="dot",        
            line_color="#ffffff",   
            opacity=0.5,           
            annotation_text=f"Target",
            annotation_position="bottom right"
        )

        # --- E. LAYOUT FINALE ---
        fig_ts.update_layout(
            title="Serie Temporale Latenza (Basata sul Tempo)",
            xaxis_title="Tempo Trascorso (Secondi)", 
            yaxis_title="Latenza (s)",
            plot_bgcolor="rgba(17, 24, 39, 0.5)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e5e7eb"),
            hovermode="x unified",
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        )
        st.plotly_chart(fig_ts, width='stretch')

    # Stop per evitare che il codice sotto venga eseguito
    if not pausa:
        time.sleep(refresh_sec)
        st.rerun()
    st.stop()

else:
    # --- MODALITÀ SINGOLA (RL o Baseline) ---
    target_file = RL_LOG if "RL" in data_source else BASE_LOG
    color_main = "#6366f1" if "RL" in data_source else "#ef4444"
    system_name = "RL Agent" if "RL" in data_source else "Baseline"
    reward_name = "Reward Progress (RL)" if "RL" in data_source else "Reward Progress (Baseline)"
    
    df = load_data(target_file)
    
    if df.empty:
        st.info(f"⏳ In attesa di dati per {system_name}...")
        if not pausa:
            time.sleep(2)
            st.rerun()
        st.stop()
    
    # Applica window per smoothing
    df = df.tail(max_points).reset_index(drop=True)

    # Calcolo metriche
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

    # KPI CARDS
    c1, c2, c3 = st.columns(3)

    with c1:
        delta_str = f"{lat_delta:.3f} s" if lat_delta is not None else None
        st.metric(f"{system_name} - Latenza", f"{last_lat:.3f} s", delta=delta_str, delta_color="inverse")

    with c2:
        st.metric(f"{system_name} - Repliche", f"{int(last_rep)}")

    with c3:
        delta_str = f"{rew_delta:.2f}" if rew_delta is not None else None
        st.metric(f"{system_name} - Reward", f"{last_rew:.2f}", delta=delta_str)

    st.markdown("---")

    # GRAFICI PRINCIPALI 
    colA, colB = st.columns([2, 1])

    with colA:
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df["episode"], 
            y=df["replicas"],
            name="Repliche",
            opacity=0.35,
            yaxis="y2",
            marker=dict(color=color_main, line=dict(color=color_main, width=1)),
            hovertemplate='<b>Ep. %{x}</b><br>Repliche: %{y}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=df["episode"], 
            y=df["latency_roll"],
            mode="lines+markers",
            name="Latenza",
            line=dict(width=3, color="#f59e0b"),
            marker=dict(size=6, color="#fbbf24"),
            hovertemplate='<b>Ep. %{x}</b><br>Latenza: %{y:.3f}s<extra></extra>'
        ))
        
        fig.add_hline(y=low_thr, line_dash="dash", line_color="#10b981", line_width=2,
                    annotation_text=f"Target ({low_thr}s)", annotation_position="right")
        fig.add_hline(y=mid_thr, line_dash="dash", line_color="#ef4444", line_width=2,
                    annotation_text=f"Critico ({mid_thr}s)", annotation_position="right")
        
        fig.update_layout(
            title=dict(text=f"Performance {system_name}", font=dict(size=18, color="#e5e7eb", family="Inter"), x=0),
            
            xaxis=dict(title="Episodio", title_font=dict(size=12, color="#9ca3af"), tickfont=dict(color="#d1d5db", size=10),
                    rangemode="tozero", gridcolor="rgba(75, 85, 99, 0.2)", showgrid=True, zeroline=False),
            yaxis=dict(title="Latenza (s)", title_font=dict(size=12, color="#9ca3af"), tickfont=dict(color="#d1d5db", size=10),
                    rangemode="tozero", gridcolor="rgba(75, 85, 99, 0.2)", showgrid=True, zeroline=False),
            yaxis2=dict(title="Repliche", title_font=dict(size=12, color="#9ca3af"), tickfont=dict(color="#d1d5db", size=10),
                    overlaying="y", side="right", range=[0, 5], gridcolor="rgba(75, 85, 99, 0.1)", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=11, color="#d1d5db"),
                    bgcolor="rgba(17, 24, 39, 0.8)", bordercolor="rgba(75, 85, 99, 0.3)", borderwidth=1),
            plot_bgcolor="rgba(10, 14, 39, 0.5)",
            paper_bgcolor="rgba(10, 14, 39, 0)",
            height=420,
            margin=dict(l=50, r=50, t=60, b=40),
            hovermode='x unified'
        )
        st.plotly_chart(fig, width='stretch', key=f"main_{time.time()}")

    with colB:
        fig_r = go.Figure()
        
        fig_r.add_trace(go.Scatter(
            x=df["episode"], y=df["reward_roll"], mode="lines", name="Reward",
            line=dict(width=0), fillcolor="rgba(139, 92, 246, 0.15)", fill='tozeroy', showlegend=False
        ))
        
        fig_r.add_trace(go.Scatter(
            x=df["episode"], y=df["reward_roll"], mode="lines+markers", name="Reward",
            line=dict(color="#8b5cf6", width=3), marker=dict(size=6, color="#a78bfa"),
            hovertemplate='<b>Ep. %{x}</b><br>Reward: %{y:.2f}<extra></extra>'
        ))
        
        fig_r.update_layout(
            title=dict(text= f"{reward_name}", font=dict(size=16, color="#e5e7eb", family="Inter"), x=0),
            xaxis=dict(title="Episodio", title_font=dict(size=11, color="#9ca3af"), tickfont=dict(color="#d1d5db", size=10),
                    rangemode="tozero", gridcolor="rgba(75, 85, 99, 0.2)", showgrid=True, zeroline=False),
            yaxis=dict(title="Score", title_font=dict(size=11, color="#9ca3af"), tickfont=dict(color="#d1d5db", size=10),
                    gridcolor="rgba(75, 85, 99, 0.2)", showgrid=True, zeroline=False),
            plot_bgcolor="rgba(10, 14, 39, 0.5)",
            paper_bgcolor="rgba(10, 14, 39, 0)",
            height=420,
            margin=dict(l=50, r=30, t=60, b=40),
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_r, width='stretch', key=f"reward_{time.time()}")

    # FOOTER CON STATISTICHE 
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    avg_lat = df["latency"].mean()
    avg_rep = df["replicas"].mean()
    total_episodes = len(df)
    cumulative_reward = df["reward"].sum()

    with col1:
        st.markdown(f"<div class='stat-card'><p class='stat-label'>Latenza Media</p><p class='stat-value'>{avg_lat:.3f}s</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stat-card'><p class='stat-label'>Repliche Medie</p><p class='stat-value'>{avg_rep:.1f}</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='stat-card'><p class='stat-label'>Episodi Totali</p><p class='stat-value'>{total_episodes}</p></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='stat-card'><p class='stat-label'>Reward Cumulativo</p><p class='stat-value'>{cumulative_reward:.1f}</p></div>", unsafe_allow_html=True)

# AUTO-REFRESH GENERALE 
if not pausa:
    time.sleep(refresh_sec)
    st.rerun()
