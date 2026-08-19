import pandas as pd
import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="Gestión de Inventario - LINPAC",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados para mejorar la interfaz visual
st.markdown("""
<style>
    /* Estilo general y tipografía */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Encabezado principal */
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #334155;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    .main-header h1 {
        color: #38bdf8;
        font-weight: 800;
        margin: 0;
        font-size: 1.8rem;
    }
    .main-header p {
        color: #94a3b8;
        margin-top: 5px;
        font-size: 0.9rem;
    }

    /* Tarjetas de resultados */
    .result-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        border-left: 5px solid #0284c7;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .result-card-c0 {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        border-left: 5px solid #f59e0b;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #f1f5f9;
    }
    .card-subtitle {
        font-size: 0.85rem;
        color: #94a3b8;
    }
    .card-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #0369a1;
        color: #ffffff;
    }
    
    /* Personalización de Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        background-color: #1e293b;
        color: #94a3b8;
        border: 1px solid #334155;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: white !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# PWA y cabeceras táctiles
st.markdown(
    """
    <link rel="manifest" href="https://raw.githubusercontent.com/barlagesta/inventario-linpac/main/manifest.json">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="Inventario">
    """,
    unsafe_allow_html=True
)

# Banner Principal
st.markdown("""
<div class="main-header">
    <h1>📦 LINPAC INVENTARIO</h1>
    <p>Consulta rápida de ubicaciones, bultos y stock</p>
</div>
""", unsafe_allow_html=True)

# Cargar archivos CSV
@st.cache_data
def load_data():
    df_general = pd.read_csv("inventario_calles-v3.csv")
    try:
        df_c0 = pd.read_csv("calle0.csv")
    except Exception:
        df_c0 = pd.DataFrame()
    return df_general, df_c0

df, df_calle0 = load_data()

# Pestañas de Navegación Visual
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Buscar Código", "📍 Por Posición", "📋 Ver Calle", "🏢 Calle 0"])

# --- TAB 1: BUSCAR CÓDIGO ---
with tab1:
    codigo = st.text_input("🔎 Código de producto:", placeholder="Ej. 415716 o 403076")
    
    if codigo:
        cod_clean = codigo.strip()
        
        # Buscar en general
        matches = []
        for idx, row in df.iterrows():
            calle = str(row["Calle"])
            pos = row["Posición"]
            for col in ["Columna A", "Columna B", "Columna C", "Columna D"]:
                val = str(row[col]) if pd.notna(row[col]) else ""
                if cod_clean in val:
                    pallets = 2 if "x2" in val.lower() else 1
                    matches.append({"Calle": calle, "Posición": pos, "Columna": col, "Valor": val, "Palets": pallets})
        
        # Buscar en Calle 0
        matches_c0 = []
        if not df_calle0.empty:
            c0_res = df_calle0[df_calle0["codigo"].astype(str).str.contains(cod_clean, na=False)]
            for idx, row in c0_res.iterrows():
                matches_c0.append({
                    "Sección": row["seccion"],
                    "Posición": row["posicion"],
                    "Código": row["codigo"],
                    "Bultos": row["bultos"],
                    "Cliente": row["zona_observaciones"]
                })

        # Mostrar métricas rápidas
        if matches or matches_c0:
            c1, c2 = st.columns(2)
            tot_p = sum(m["Palets"] for m in matches) if matches else 0
            tot_b = sum(m["Bultos"] for m in matches_c0) if matches_c0 else 0
            
            c1.metric(label="Palets (Calles Grales.)", value=f"{tot_p} palets")
            c2.metric(label="Bultos (Calle 0)", value=f"{tot_b} bultos")
            
            # Tarjetas Calles Generales
            if matches:
                st.subheader("📍 Calles Generales")
                for m in matches:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="card-title">Calle {m['Calle']} — Posición {m['Posición']}</div>
                        <div class="card-subtitle">Ubicación: <b>{m['Columna']}</b></div>
                        <div style="margin-top:8px;">
                            <span class="card-badge">📦 {m['Palets']} Palet(s)</span>
                            <span style="margin-left: 10px; color: #cbd5e1;">Código: <code>{m['Valor']}</code></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Tarjetas Calle 0
            if matches_c0:
                st.subheader("🏢 Calle 0")
                for m in matches_c0:
                    st.markdown(f"""
                    <div class="result-card-c0">
                        <div class="card-title">Sección {m['Sección']} — {m['Posición']}</div>
                        <div class="card-subtitle">Cliente/Zona: <b>{m['Cliente']}</b></div>
                        <div style="margin-top:8px;">
                            <span class="card-badge" style="background-color: #d97706;">📦 {m['Bultos']} Bultos</span>
                            <span style="margin-left: 10px; color: #cbd5e1;">Código: <code>{m['Código']}</code></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No se encontró ninguna coincidencia para ese código.")

# --- TAB 2: BUSCAR POR POSICIÓN ---
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        calle_sel = st.selectbox("Selecciona Calle:", df["Calle"].unique())
        pos_sel = st.number_input("Posición:", min_value=1, max_value=50, value=1)
    with col2:
        col_sel = st.selectbox("Columna / Nivel:", ["Columna A", "Columna B", "Columna C", "Columna D"])
    
    if st.button("🔎 Consultar Ubicación", use_container_width=True):
        row = df[(df["Calle"] == calle_sel) & (df["Posición"] == pos_sel)]
        if not row.empty:
            val = row[col_sel].values[0]
            val_str = str(val) if pd.notna(val) else "Vacío / Sin Cargar"
            st.success(f"📍 **Calle {calle_sel}** | Posición **{pos_sel}** | **{col_sel}**")
            st.info(f"### Código / Contenido: `{val_str}`")
        else:
            st.error("Ubicación no encontrada.")

# --- TAB 3: VER CALLE COMPLETA ---
with tab3:
    calle_ver = st.selectbox("Selecciona la calle a visualizar:", df["Calle"].unique())
    calle_df = df[df["Calle"] == calle_ver].sort_values("Posición").fillna("-")
    st.dataframe(calle_df, use_container_width=True, hide_index=True)

# --- TAB 4: CALLE 0 (ESPECIAL) ---
with tab4:
    if df_calle0.empty:
        st.error("Archivo calle0.csv no encontrado.")
    else:
        seccion_sel = st.segmented_control("Filtrar Sección:", ["Todas", "00.01", "00.02"], default="Todas")
        
        if seccion_sel and seccion_sel != "Todas":
            df_c0_view = df_calle0[df_calle0["seccion"] == seccion_sel]
        else:
            df_c0_view = df_calle0
            
        st.dataframe(
            df_c0_view[["seccion", "posicion", "codigo", "bultos", "zona_observaciones"]],
            use_container_width=True,
            hide_index=True
        )
