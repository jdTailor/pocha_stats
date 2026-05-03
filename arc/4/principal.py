import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Pocha Stats", layout="wide")

# --- PERSISTENCIA TEMPORAL (Session State) ---
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=[
        'ID_Partida', 'Fecha', 'Jugador', 'Posición', 'Pedidas', 'Hechas', 'Num_Jugadores'
    ])

if 'jugadores' not in st.session_state:
    st.session_state.jugadores = ["pedro", "jd", "pedri", "lauri", "carlis", "ali", "deni", "rober", "mire", "adri", "mari"]

st.title("🃏 Panel de Control de Pocha")

# --- DISEÑO EN DOS COLUMNAS ---
col_izq, col_der = st.columns([1, 2], gap="large")

# --- COLUMNA IZQUIERDA: GESTIÓN (REGISTRO Y ELIMINACIÓN) ---
with col_izq:
    st.header("📝 Gestión de Partidas")
    
    # SECCIÓN: NUEVA PARTIDA
    with st.container(border=True):
        st.subheader("Nueva Partida")
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
            
            datos_partida.append({
                'Fecha': fecha, 
                'Jugador': nom, 
                'Posición': pos, 
                'Pedidas': ped, 
                'Hechas': hac,
                'Num_Jugadores': num_jug
            })
            if i < num_jug - 1:
                st.divider()

        if st.button("Guardar Partida", use_container_width=True):
            nombres_en_partida = [d['Jugador'] for d in datos_partida]
            if len(nombres_en_partida) != len(set(nombres_en_partida)):
                repetidos = set([n for n in nombres_en_partida if nombres_en_partida.count(n) > 1])
                st.error(f"❌ Error: {', '.join(repetidos)} repetido.")
            else:
                # Generamos ID único con la hora para permitir múltiples partidas el mismo día
                id_actual = datetime.now().strftime("%H:%M:%S")
                for d in datos_partida:
                    d['ID_Partida'] = f"{d['Fecha']} [{id_actual}]"
                
                nueva_p = pd.DataFrame(datos_partida)
                st.session_state.historico = pd.concat([st.session_state.historico, nueva_p], ignore_index=True)
                st.success("✅ Partida registrada.")
                st.rerun()

    # SECCIÓN: ELIMINAR PARTIDA (SEGURA)
    if not st.session_state.historico.empty:
        st.write("") 
        with st.expander("🗑️ Zona de Peligro: Eliminar Partida"):
            partidas_disponibles = st.session_state.historico['ID_Partida'].unique()
            
            partida_a_borrar = st.selectbox(
                "Selecciona partida para eliminar", 
                options=partidas_disponibles,
                index=None,
                placeholder="Escoge una partida..."
            )
            
            if partida_a_borrar:
                st.warning(f"⚠️ Vas a borrar: {partida_a_borrar}")
                if st.button("Confirmar Eliminación Permanente", type="primary", use_container_width=True):
                    st.session_state.historico = st.session_state.historico[
                        st.session_state.historico['ID_Partida'] != partida_a_borrar
                    ]
                    st.rerun()

# --- COLUMNA DERECHA: VISUALIZACIÓN DE DATOS ---
with col_der:
    st.header("📊 Histórico y Ranking")
    
    # Inyección CSS para centrado forzado de tablas
    st.markdown("""
        <style>
            .stTable th { text-align: center !important; vertical-align: middle !important; }
            .stTable td { text-align: center !important; vertical-align: middle !important; }
            .stTable th:first-child, .stTable td:first-child { text-align: left !important; }
        </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state.historico.empty:
        df = st.session_state.historico.copy()
        
        # 1. TABLA HISTÓRICA
        df['Info'] = "P:" + df['Posición'].astype(str) + " (" + df['Pedidas'].astype(str) + "/" + df['Hechas'].astype(str) + ")"
        tabla_pivote = df.pivot_table(
            index='ID_Partida', columns='Jugador', values='Info', aggfunc='first'
        ).fillna("-")
        tabla_pivote.index.name = "Partida (Fecha [Hora])"
        
        st.write("Leyenda: **P:Posición (Bazas Pedidas / Bazas Hechas)**")
        st.table(tabla_pivote)
        
        # 2. TABLA DE RESUMEN CON PERCENTIL
        st.subheader("🏆 Resumen Total de Jugadores")
        
        # Fórmula de Rendimiento Percentil
        def calcular_rendimiento(row):
            if row['Num_Jugadores'] <= 1: return 100.0
            return ((row['Num_Jugadores'] - row['Posición']) / (row['Num_Jugadores'] - 1)) * 100

        df['Rendimiento'] = df.apply(calcular_rendimiento, axis=1)

        resumen = df.groupby('Jugador').agg({
            'Posición': 'mean',
            'Rendimiento': 'mean',
            'Pedidas': 'sum',
            'Hechas': 'sum'
        }).rename(columns={
            'Posición': 'Pos. Media', 
            'Rendimiento': 'Rendimiento (%)',
            'Pedidas': 'Total Pedidas', 
            'Hechas': 'Total Hechas'
        })
        
        # Ordenar columnas y formatear
        resumen = resumen[['Pos. Media', 'Rendimiento (%)', 'Total Pedidas', 'Total Hechas']]
        resumen_f = resumen.copy()
        resumen_f["Pos. Media"] = resumen_f["Pos. Media"].map("{:.2f}".format)
        resumen_f["Rendimiento (%)"] = resumen_f["Rendimiento (%)"].map("{:.1f}%".format)
        
        st.table(resumen_f)
    else:
        st.info("No hay datos registrados todavía. ¡A jugar!")