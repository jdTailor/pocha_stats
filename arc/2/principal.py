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

# Lista de jugadores (se sincroniza con la página de configuración)
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
        
        # Generar campos dinámicamente según el número seleccionado
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
            
            datos_partida.append({
                'Fecha': fecha, 
                'Jugador': nom, 
                'Posición': pos, 
                'Pedidas': ped, 
                'Hechas': hac
            })
            if i < num_jug - 1:
                st.divider()

        # BOTÓN DE GUARDAR CON VALIDACIÓN DE DUPLICADOS
        if st.button("Guardar Partida", use_container_width=True):
            # Obtener lista de nombres seleccionados
            nombres_en_partida = [d['Jugador'] for d in datos_partida]
            
            # Verificar si hay duplicados
            if len(nombres_en_partida) != len(set(nombres_en_partida)):
                # Encontrar cuáles son los nombres repetidos para el mensaje de error
                repetidos = set([n for n in nombres_en_partida if nombres_en_partida.count(n) > 1])
                st.error(f"❌ No se puede guardar: El jugador **{', '.join(repetidos)}** aparece varias veces.")
            else:
                # Si no hay duplicados, añadir al DataFrame histórico
                nueva_p = pd.DataFrame(datos_partida)
                st.session_state.historico = pd.concat([st.session_state.historico, nueva_p], ignore_index=True)
                st.success("✅ Partida registrada correctamente.")
                st.rerun()

# --- COLUMNA DERECHA: TABLA ACUMULATIVA ---
with col_der:
    st.header("📊 Histórico Acumulativo")
    
    if not st.session_state.historico.empty:
        df = st.session_state.historico.copy()
        
        # Crear la cadena de texto para mostrar en la celda de la tabla
        df['Info'] = "P:" + df['Posición'].astype(str) + " (" + df['Pedidas'].astype(str) + "/" + df['Hechas'].astype(str) + ")"
        
        # Crear tabla pivote: Fechas en filas, Jugadores en columnas
        tabla_pivote = df.pivot_table(
            index='Fecha', 
            columns='Jugador', 
            values='Info', 
            aggfunc='first'
        ).fillna("-")
        
        st.write("Leyenda: **P:Posición (Bazas Pedidas / Bazas Hechas)**")
        st.dataframe(tabla_pivote, use_container_width=True)
        
        # Sección de totales para ver el rendimiento general
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
        
        # Formatear la posición media a 2 decimales
        st.table(resumen.style.format({"Pos. Media": "{:.2f}"}))
    else:
        st.info("La tabla está vacía. Registra los resultados de la primera partida a la izquierda.")