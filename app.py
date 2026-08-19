import pandas as pd
import streamlit as st

# Configuración de la página en móvil
st.set_page_config(page_title="Consulta de Inventario", layout="centered")

st.markdown(
    """
    <link rel="manifest" href="https://raw.githubusercontent.com/barlagesta/inventario-linpac/main/manifest.json">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="Inventario">
    """,
    unsafe_allow_html=True
)

st.title("📦 Consulta de Inventario")

# Cargar los archivos CSV
@st.cache_data
def load_data():
    df_general = pd.read_csv("inventario_calles-v3.csv")
    try:
        df_c0 = pd.read_csv("calle0.csv")
    except Exception:
        df_c0 = pd.DataFrame()
    return df_general, df_c0

df, df_calle0 = load_data()

# Tipo de consulta
opcion = st.radio(
    "Selecciona tipo de búsqueda:", 
    ["Buscar por Código", "Buscar por Posición", "Ver Calle Completa", "Calle 0 (Especial)"]
)

# --- OPCIÓN 1: BUSCAR POR CÓDIGO ---
if opcion == "Buscar por Código":
    codigo = st.text_input("Introduce el código de producto (ej. 415716 o 403076):")
    if codigo:
        cod_clean = codigo.strip()
        
        # Búsqueda en Inventario General
        matches = []
        for idx, row in df.iterrows():
            calle = str(row["Calle"])
            pos = row["Posición"]
            for col in ["Columna A", "Columna B", "Columna C", "Columna D"]:
                val = str(row[col]) if pd.notna(row[col]) else ""
                if cod_clean in val:
                    pallets = 2 if "x2" in val.lower() else 1
                    matches.append({"Calle": calle, "Posición": pos, "Columna": col, "Valor": val, "Palets": pallets})
        
        # Búsqueda en Calle 0
        matches_c0 = []
        if not df_calle0.empty:
            c0_res = df_calle0[df_calle0["codigo"].astype(str).str.contains(cod_clean, na=False)]
            for idx, row in c0_res.iterrows():
                matches_c0.append({
                    "Calle": "Calle 0",
                    "Sección": row["seccion"],
                    "Posición": row["posicion"],
                    "Código": row["codigo"],
                    "Bultos": row["bultos"],
                    "Cliente/Zona": row["zona_observaciones"]
                })

        # Mostrar Resultados
        if matches or matches_c0:
            if matches:
                res_df = pd.DataFrame(matches)
                total_palets = res_df["Palets"].sum()
                st.success(f"¡Encontrado en Calles Generales! Total palets: **{total_palets}**")
                st.dataframe(res_df[["Calle", "Posición", "Columna", "Valor", "Palets"]], use_container_width=True)
            
            if matches_c0:
                res_c0_df = pd.DataFrame(matches_c0)
                total_bultos = res_c0_df["Bultos"].sum()
                st.info(f"📍 ¡Encontrado en Calle 0! Total bultos: **{total_bultos}**")
                st.dataframe(res_c0_df[["Sección", "Posición", "Código", "Bultos", "Cliente/Zona"]], use_container_width=True)
        else:
            st.warning("No se encontró ese código en el inventario.")

# --- OPCIÓN 2: BUSCAR POR POSICIÓN ---
elif opcion == "Buscar por Posición":
    col1, col2, col3 = st.columns(3)
    with col1:
        calle_sel = st.selectbox("Calle:", df["Calle"].unique())
    with col2:
        pos_sel = st.number_input("Posición:", min_value=1, max_value=50, value=1)
    with col3:
        col_sel = st.selectbox("Columna:", ["Columna A", "Columna B", "Columna C", "Columna D"])
    
    if st.button("Consultar Ubicación"):
        row = df[(df["Calle"] == calle_sel) & (df["Posición"] == pos_sel)]
        if not row.empty:
            val = row[col_sel].values[0]
            val_str = str(val) if pd.notna(val) else "Vacío"
            st.info(f"📍 **{calle_sel}**, Posición **{pos_sel}**, **{col_sel}**:")
            st.markdown(f"### Código: `{val_str}`")
        else:
            st.error("Ubicación no encontrada.")

# --- OPCIÓN 3: VER CALLE COMPLETA ---
elif opcion == "Ver Calle Completa":
    calle_ver = st.selectbox("Selecciona la calle:", df["Calle"].unique())
    calle_df = df[df["Calle"] == calle_ver].sort_values("Posición").fillna("-")
    st.dataframe(calle_df, use_container_width=True)

# --- OPCIÓN 4: CALLE 0 (ESPECIAL) ---
else:
    st.subheader("📍 Calle 0 (Detalle por Bultos y Clientes)")
    if df_calle0.empty:
        st.error("No se encontró el archivo calle0.csv en GitHub.")
    else:
        seccion_sel = st.radio("Sección de Calle 0:", ["Todas", "00.01", "00.02"], horizontal=True)
        
        if seccion_sel != "Todas":
            df_c0_view = df_calle0[df_calle0["seccion"] == seccion_sel]
        else:
            df_c0_view = df_calle0
            
        st.dataframe(
            df_c0_view[["seccion", "posicion", "codigo", "bultos", "zona_observaciones"]],
            use_container_width=True
        )
