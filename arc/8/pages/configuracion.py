import streamlit as st
import pandas as pd

st.set_page_config(page_title="Configuración de Jugadores", layout="wide")

st.title("👥 Gestión de Jugadores")

# Inicializar la lista de jugadores en la sesión si no existe
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = ["pedro", "jd", "pedri", "lauri", "carlis", "ali", "deni", "rober", "mire", "adri", "mari"]

col1, col2 = st.columns([1, 1.5], gap="large")

# --- COLUMNA 1: AÑADIR NUEVO ---
with col1:
    st.subheader("Añadir Jugador")
    with st.container(border=True):
        nuevo_jugador = st.text_input("Nombre del nuevo jugador", key="input_nuevo")
        if st.button("Registrar", use_container_width=True):
            nombre_limpio = nuevo_jugador.strip()
            if nombre_limpio:
                if nombre_limpio not in st.session_state.jugadores:
                    st.session_state.jugadores.append(nombre_limpio)
                    st.success(f"✅ {nombre_limpio} añadido.")
                    st.rerun()
                else:
                    st.error("Ese nombre ya existe.")
            else:
                st.error("El nombre no puede estar vacío.")

# --- COLUMNA 2: LISTA Y EDICIÓN ---
with col2:
    st.subheader("Jugadores Actuales")
    
    # Creamos un contenedor para que la lista se vea ordenada
    for i, nombre in enumerate(st.session_state.jugadores):
        with st.container(border=True):
            c_nombre, c_editar = st.columns([3, 1])
            
            with c_nombre:
                # Campo de texto para cada jugador
                nuevo_nombre = st.text_input(
                    f"Editar nombre de index {i}", 
                    value=nombre, 
                    key=f"edit_{i}",
                    label_visibility="collapsed"
                )
            
            with c_editar:
                if st.button("💾 Guardar", key=f"btn_{i}", use_container_width=True):
                    nombre_editado_limpio = nuevo_nombre.strip()
                    
                    if not nombre_editado_limpio:
                        st.error("No puede estar vacío.")
                    elif nombre_editado_limpio in st.session_state.jugadores and nombre_editado_limpio != nombre:
                        st.error("Ese nombre ya existe.")
                    else:
                        # Actualizamos el nombre en la lista
                        st.session_state.jugadores[i] = nombre_editado_limpio
                        st.success("Cambiado")
                        st.rerun()

# Nota informativa al final
st.info("💡 Para cambiar un nombre, edita el texto en la lista y pulsa el botón 'Guardar' de esa fila.")