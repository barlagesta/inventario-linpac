import pandas as pd
import streamlit as st
import re

# Configuración de página
st.set_page_config(
    page_title="Gestión de Inventario - LINPAC",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS de MODO CLARO (Alto contraste y fácil lectura)
st.markdown("""
<style>
    /* Estilo general con fondo claro */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    /* Encabezado principal */
    .main-header {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1.2rem;
        color: #ffffff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        color: #ffffff !important;
        font-weight: 800;
        margin: 0;
        font-size: 1.7rem;
    }
    .main-header p {
        color: #bfdbfe;
        margin-top: 4px;
        font-size: 0.9rem;
    }

    /* Caja Resumen Inicio / Fin */
    .summary-box {
        background-color: #eff6ff;
        border: 2px solid #3b82f6;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1);
    }
    .summary-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #1e40af;
        margin-bottom: 8px;
    }
    .summary-text {
        font-size: 1rem;
        color: #1e3a8a;
        line-height: 1.5;
    }

    /* Tarjetas de resultados */
    .result-card {
        background-color: #ffffff;
        border: 2px solid #cbd5e1;
        border-left: 6px solid #2563eb;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .result-card-c0 {
        background-color: #ffffff;
        border: 2px solid #cbd5e1;
        border-left: 6px solid #d97706;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .card-title {
        font-size: 1.15rem;
        font-weight: bold;
        color: #0f172a;
    }
    .card-subtitle {
        font-size: 0.95rem;
        color: #334155;
        margin-top: 3px;
    }
    .card-badge {
        display: inline-block;
        padding: 0.3rem 0.7rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 700;
        background-color: #dbeafe;
        color: #1e40af;
        border: 1px solid #bfdbfe;
    }
    .card-badge-c0 {
        display: inline-block;
        padding: 0.3rem 0.7rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 700;
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }
    
    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 14px;
        background-color: #e2e8f0;
        color: #334155;
        font-weight: 600;
        border: 1px solid #cbd5e1;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
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

# Helper para extraer el número entero de posición
def parse_pos_num(val):
    try:
        nums = re.findall(r'\d+', str(val))
        return int(nums[0]) if nums else 0
    except Exception:
        return 0

# Pestañas de Navegación
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
            pos = int(row["Posición"]) if pd.notna(row["Posición"]) else 0
            for col in ["Columna A", "Columna B", "Columna C", "Columna D"]:
                val = str(row[col]) if pd.notna(row[col]) else ""
                if cod_clean in val:
                    pallets = 2 if "x2" in val.lower() else 1
                    matches.append({
                        "Calle": calle, 
                        "Posición": pos, 
                        "Columna": col, 
                        "Valor": val, 
                        "Palets": pallets
                    })
        
        # Buscar en Calle 0
        matches_c0 = []
        if not df_calle0.empty:
            c0_res = df_calle0[df_calle0["codigo"].astype(str).str.contains(cod_clean, na=False)]
            for idx, row in c0_res.iterrows():
                pos_val = str(row["posicion"])
                pos_num = parse_pos_num(pos_val)
                matches_c0.append({
                    "Sección": str(row["seccion"]),
                    "Posición_Str": pos_val,
                    "Posición_Num": pos_num,
                    "Código": row["codigo"],
                    "Bultos": int(row["bultos"]) if pd.notna(row["bultos"]) else 0,
                    "Cliente": row["zona_observaciones"]
                })

        # Ordenar por posición (de menor a mayor)
        matches = sorted(matches, key=lambda x: x["Posición"])
        matches_c0 = sorted(matches_c0, key=lambda x: x["Posición_Num"])

        if matches or matches_c0:
            
            # --- CAJA DE RESUMEN INICIO Y FIN AL PRINCIPIO ---
            if matches:
                inicio = matches[0]
                fin = matches[-1]
                
                if len(matches) == 1:
                    resumen_html = f"""
                    <div class="summary-box">
                        <div class="summary-title">📍 Resumen de Ubicación para <code>{cod_clean}</code></div>
                        <div class="summary-text">
                            El código está ubicado en:<br>
                            👉 <b>Calle {inicio['Calle']}</b>, <b>Posición {inicio['Posición']}</b>, <b>{inicio['Columna']}</b>
                        </div>
                    </div>
                    """
                else:
                    resumen_html = f"""
                    <div class="summary-box">
                        <div class="summary-title">↔️ Rango de Distribución para <code>{cod_clean}</code></div>
                        <div class="summary-text">
                            🟢 <b>Inicio:</b> Calle <b>{inicio['Calle']}</b>, Posición <b>{inicio['Posición']}</b>, <b>{inicio['Columna']}</b><br>
                            🔴 <b>Fin:</b> Calle <b>{fin['Calle']}</b>, Posición <b>{fin['Posición']}</b>, <b>{fin['Columna']}</b>
                        </div>
                    </div>
                    """
                st.markdown(resumen_html, unsafe_allow_html=True)
            
            elif matches_c0:
                inicio_c0 = matches_c0[0]
                fin_c0 = matches_c0[-1]
                
                if len(matches_c0) == 1:
                    resumen_html = f"""
                    <div class="summary-box">
                        <div class="summary-title">🏢 Resumen de Ubicación en Calle 0 para <code>{cod_clean}</code></div>
                        <div class="summary-text">
                            El código está ubicado en:<br>
                            👉 <b>Sección {inicio_c0['Sección']}</b>, <b>Posición {inicio_c0['Posición_Str']}</b>
                        </div>
                    </div>
                    """
                else:
                    resumen_html = f"""
                    <div class="summary-box">
                        <div class="summary-title">↔️ Rango de Distribución en Calle 0 para <code>{cod_clean}</code></div>
                        <div class="summary-text">
                            🟢 <b>Inicio:</b> Sección <b>{inicio_c0['Sección']}</b>, Posición <b>{inicio_c0['Posición_Str']}</b><br>
                            🔴 <b>Fin:</b> Sección <b>{fin_c0['Sección']}</b>, Posición <b>{fin_c0['Posición_Str']}</b>
                        </div>
                    </div>
                    """
                st.markdown(resumen_html, unsafe_allow_html=True)

            # Métricas
            c1, c2 = st.columns(2)
            tot_p = sum(m["Palets"] for m in matches) if matches else 0
            tot_b = sum(m["Bultos"] for m in matches_c0) if matches_c0 else 0
            
            c1.metric(label="Palets (Calles Grales.)", value=f"{tot_p} palet(s)")
            c2.metric(label="Bultos (Calle 0)", value=f"{tot_b} bulto(s)")
            
            # Tarjetas Calles Generales
            if matches:
                st.subheader("📍 Detalle por Posición (Calles Generales)")
                for m in matches:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="card-title">Calle {m['Calle']} — Posición {m['Posición']}</div>
                        <div class="card-subtitle">Ubicación: <b>{m['Columna']}</b></div>
                        <div style="margin-top:8px;">
                            <span class="card-badge">📦 {m['Palets']} Palet(s)</span>
                            <span style="margin-left: 10px; font-weight: bold; color: #0f172a;">Código: {m['Valor']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Tarjetas Calle 0
            if matches_c0:
                st.subheader("🏢 Detalle por Posición (Calle 0)")
                for m in matches_c0:
                    st.markdown(f"""
                    <div class="result-card-c0">
                        <div class="card-title">Sección {m['Sección']} — Posición {m['Posición_Str']}</div>
                        <div class="card-subtitle">Cliente/Zona: <b>{m['Cliente']}</b></div>
                        <div style="margin-top:8px;">
                            <span class="card-badge-c0">📦 {m['Bultos']} Bulto(s)</span>
                            <span style="margin-left: 10px; font-weight: bold; color: #0f172a;">Código: {m['Código']}</span>
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
        seccion_sel = st.radio("Filtrar Sección:", ["Todas", "00.01", "00.02"], horizontal=True)
        
        if seccion_sel != "Todas":
            df_c0_view = df_calle0[df_calle0["seccion"] == seccion_sel]
        else:
            df_c0_view = df_calle0
            
        st.dataframe(
            df_c0_view[["seccion", "posicion", "codigo", "bultos", "zona_observaciones"]],
            use_container_width=True,
            hide_index=True
        )
