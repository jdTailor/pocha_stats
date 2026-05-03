import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Pocha Stats", layout="wide")

# Inicialización de datos
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=[
        'Fecha', 'Jugador', 'Posición', 'Pedidas', 'Hechas'
    ])

if 'jugadores' not in st.session_state:
    st.session_state.jugadores = ["Alex", "Bea"]

st.title("🃏 Panel de Control de Pocha")

# --- DIVISIÓN EN DOS COLUMNAS ---
col_izq, col_der = st.columns([1, 2], gap="large")

# --- ZONA IZQUIERDA: ENTRADA DE DATOS ---
with col_izq:
    st.header("📝 Nueva Partida")
    with st.form("registro_partida"):
        fecha = st.date_input("Fecha", datetime.now())
        num_jug = st.number_input("¿Cuántos juegan?", 2, 10, 4)
        
        datos_partida = []
        for i in range(num_jug):
            st.markdown(f"**Jugador {i+1}**")
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            with c1:
                nom = st.selectbox(f"Nombre", st.session_state.jugadores, key=f"n_{i}")
            with c2:
                pos = st.number_input(f"Pos.", 1, 10, key=f"p_{i}")
            with c3:
                ped = st.number_input(f"Ped.", 0, 100, key=f"a_{i}")
            with c4:
                hac = st.number_input(f"Hec.", 0, 100, key=f"h_{i}")
            
            datos_partida.append({'Fecha': fecha, 'Jugador': nom, 'Posición': pos, 'Pedidas': ped, 'Hechas': hac})
            
        btn_guardar = st.form_submit_button("Guardar Partida")
        
        if btn_guardar:
            nueva_p = pd.DataFrame(datos_partida)
            st.session_state.historico = pd.concat([st.session_state.historico, nueva_p], ignore_index=True)
            st.success("¡Partida registrada!")

# --- ZONA DERECHA: HISTÓRICO ACUMULATIVO ---
with col_der:
    st.header("📊 Histórico Acumulativo")
    
    if not st.session_state.historico.empty:
        # Transformar datos para la tabla pivote (Eje V: Fecha, Eje H: Jugador)
        # Creamos una columna combinada para mostrar Pos/Ped/Hec en una celda
        df = st.session_state.historico.copy()
        df['Info'] = "P:" + df['Posición'].astype(str) + " (" + df['Pedidas'].astype(str) + "/" + df['Hechas'].astype(str) + ")"
        
        tabla_pivote = df.pivot_table(
            index='Fecha', 
            columns='Jugador', 
            values='Info', 
            aggfunc='first'
        ).fillna("-")
        
        st.write("Formato: **P:Posición (Pedidas/Hechas)**")
        st.dataframe(tabla_pivote, use_container_width=True)
        
        # Sumatorio al final (Métricas agregadas)
        st.subheader("🏆 Totales Acumulados")
        resumen = df.groupby('Jugador').agg({
            'Posición': 'mean',
            'Pedidas': 'sum',
            'Hechas': 'sum'
        }).rename(columns={'Posición': 'Pos. Media', 'Pedidas': 'Total Pedidas', 'Hechas': 'Total Hechas'})
        
        st.table(resumen.style.format({"Pos. Media": "{:.2f}"}))
    else:
        st.info("Aún no hay partidas guardadas.")