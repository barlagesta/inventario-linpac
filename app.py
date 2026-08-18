import pandas as pd
import streamlit as st

# Configuración de la página en móvil
st.set_page_config(page_title="Consulta de Inventario", layout="centered")

st.title("📦 Consulta de Inventario")

# Cargar el archivo CSV
@st.cache_data
def load_data():
    return pd.read_csv("inventario_calles-v3.csv")

df = load_data()

# Tipo de consulta
opcion = st.radio("Selecciona tipo de búsqueda:", ["Buscar por Código", "Buscar por Posición", "Ver Calle Completa"])

# --- OPCIÓN 1: BUSCAR POR CÓDIGO ---
if opcion == "Buscar por Código":
    codigo = st.text_input("Introduce el código de producto (ej. 415716):")
    if codigo:
        matches = []
        for idx, row in df.iterrows():
            calle = str(row["Calle"])
            pos = row["Posición"]
            for col in ["Columna A", "Columna B", "Columna C", "Columna D"]:
                val = str(row[col]) if pd.notna(row[col]) else ""
                if codigo.strip() in val:
                    pallets = 2 if "x2" in val.lower() else 1
                    matches.append({"Calle": calle, "Posición": pos, "Columna": col, "Valor": val, "Palets": pallets})
        
        if matches:
            res_df = pd.DataFrame(matches)
            total_palets = res_df["Palets"].sum()
            st.success(f"¡Encontrado! Total de palets: **{total_palets}**")
            st.dataframe(res_df[["Calle", "Posición", "Columna", "Valor", "Palets"]], use_container_width=True)
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
else:
    calle_ver = st.selectbox("Selecciona la calle:", df["Calle"].unique())
    calle_df = df[df["Calle"] == calle_ver].sort_values("Posición").fillna("-")
    st.dataframe(calle_df, use_container_width=True)
