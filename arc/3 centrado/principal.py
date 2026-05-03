import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Pocha Stats", layout="wide")

# --- PERSISTENCIA TEMPORAL (Session State) ---
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=[
        'Fecha', 'Jugador', 'Posición', 'Pedidas', 'Hechas'
    ])

if 'jugadores' not in st.session_state:
    st.session_state.jugadores = ["pedro", "jd", "pedri", "lauri", "carlis", "ali", "deni", "rober", "mire", "adri", "mari"]

st.title("🃏 Panel de Control de Pocha")

# --- DISEÑO EN DOS COLUMNAS ---
col_izq, col_der = st.columns([1, 2], gap="large")

# --- COLUMNA IZQUIERDA: REGISTRO DE PARTIDA ---
with col_izq:
    st.header("📝 Nueva Partida")
    
    with st.container(border=True):
        fecha = st.date_input("Fecha", datetime.now())
        num_jug = st.number_input("¿Cuántos juegan?", min_value=1, max_value=len(st.session_state.jugadores), value=4)
        
        datos_partida = []
        for i in range(num_jug):
            st.markdown(f"**Jugador {i+1}**")
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            with c1:
                nom = st.selectbox(f"Nombre", st.session_state.jugadores, key=f"n_{i}")
            with c2:
                pos = st.number_input(f"Pos.", 1, 20, value=1, key=f"p_{i}")
            with c3:
                ped = st.number_input(f"Ped.", 0, 100, value=0, key=f"a_{i}")
            with c4:
                hac = st.number_input(f"Hec.", 0, 100, value=0, key=f"h_{i}")
            
            datos_partida.append({'Fecha': fecha, 'Jugador': nom, 'Posición': pos, 'Pedidas': ped, 'Hechas': hac})
            if i < num_jug - 1:
                st.divider()

        if st.button("Guardar Partida", use_container_width=True):
            nombres_en_partida = [d['Jugador'] for d in datos_partida]
            if len(nombres_en_partida) != len(set(nombres_en_partida)):
                repetidos = set([n for n in nombres_en_partida if nombres_en_partida.count(n) > 1])
                st.error(f"❌ Error: {', '.join(repetidos)} aparece varias veces.")
            else:
                nueva_p = pd.DataFrame(datos_partida)
                st.session_state.historico = pd.concat([st.session_state.historico, nueva_p], ignore_index=True)
                st.success("✅ Partida registrada.")
                st.rerun()

# --- COLUMNA DERECHA: HISTÓRICO ACUMULATIVO ---
with col_der:
    st.header("📊 Histórico Acumulativo")
    
    # Inyectamos CSS para forzar el centrado que Streamlit a veces bloquea
    st.markdown("""
        <style>
            /* Centrar cabeceras de columnas */
            .stTable th {
                text-align: center !important;
                vertical-align: middle !important;
            }
            /* Centrar todas las celdas de datos */
            .stTable td {
                text-align: center !important;
                vertical-align: middle !important;
            }
            /* Mantener la primera columna (índices) a la izquierda */
            .stTable th:first-child, 
            .stTable td:first-child {
                text-align: left !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state.historico.empty:
        df = st.session_state.historico.copy()
        
        # 1. Preparar datos para la tabla pivote
        df['Info'] = "P:" + df['Posición'].astype(str) + " (" + df['Pedidas'].astype(str) + "/" + df['Hechas'].astype(str) + ")"
        
        tabla_pivote = df.pivot_table(
            index='Fecha', 
            columns='Jugador', 
            values='Info', 
            aggfunc='first'
        ).fillna("-")
        
        st.write("Leyenda: **P:Posición (Bazas Pedidas / Bazas Hechas)**")
        
        # Mostramos la tabla (el CSS de arriba se encargará del estilo)
        st.table(tabla_pivote)
        
        # 2. Resumen Total
        st.subheader("🏆 Resumen Total de Jugadores")
        resumen = df.groupby('Jugador').agg({
            'Posición': 'mean',
            'Pedidas': 'sum',
            'Hechas': 'sum'
        }).rename(columns={
            'Posición': 'Pos. Media', 
            'Pedidas': 'Total Pedidas', 
            'Hechas': 'Total Hechas'
        })
        
        # Formateamos solo los decimales antes de mostrar
        resumen_formateado = resumen.copy()
        resumen_formateado["Pos. Media"] = resumen_formateado["Pos. Media"].map("{:.2f}".format)
        
        st.table(resumen_formateado)
    else:
        st.info("La tabla está vacía. Registra los resultados de la primera partida a la izquierda.")