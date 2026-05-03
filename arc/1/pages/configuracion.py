import streamlit as st
import pandas as pd

st.set_page_config(page_title="Configuración de Jugadores", layout="wide")

st.title("👥 Gestión de Jugadores")

# Cargar o inicializar lista de jugadores
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = ["Alex", "Bea", "Carlos"] # Valores por defecto

with st.container():
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Añadir Jugador")
        nuevo_jugador = st.text_input("Nombre del nuevo jugador")
        if st.button("Registrar"):
            if nuevo_jugador and nuevo_jugador not in st.session_state.jugadores:
                st.session_state.jugadores.append(nuevo_jugador)
                st.success(f"{nuevo_jugador} añadido.")
            else:
                st.warning("Nombre vacío o ya existe.")

    with col2:
        st.subheader("Jugadores Actuales")
        st.table(pd.DataFrame(st.session_state.jugadores, columns=["Nombre"]))
        if st.button("Limpiar lista"):
            st.session_state.jugadores = []
            st.rerun()