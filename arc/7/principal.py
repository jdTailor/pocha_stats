import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Pocha Stats", layout="centered")

# --- PERSISTENCIA TEMPORAL (Session State) ---
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=[
        'ID_Partida', 'Fecha', 'Jugador', 'Posición', 'Pedidas', 'Hechas', 'Num_Jugadores'
    ])

if 'jugadores' not in st.session_state:
    st.session_state.jugadores = ["pedro", "jd", "pedri", "lauri", "carlis", "ali", "deni", "rober", "mire", "adri", "mari"]

st.title("🃏 Pocha Stats")

# --- SECCIÓN 1: GESTIÓN DE PARTIDAS (COLAPSADA) ---
with st.expander("📝 Gestión de Partidas (Añadir o Eliminar)", expanded=False):
    
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
            id_actual = datetime.now().strftime("%H:%M:%S")
            for d in datos_partida:
                d['ID_Partida'] = f"{d['Fecha']} [{id_actual}]"
            
            nueva_p = pd.DataFrame(datos_partida)
            st.session_state.historico = pd.concat([st.session_state.historico, nueva_p], ignore_index=True)
            st.success("✅ Partida registrada.")
            st.rerun()

    if not st.session_state.historico.empty:
        st.divider()
        st.subheader("🗑️ Eliminar Partida")
        partidas_disponibles = st.session_state.historico['ID_Partida'].unique()
        partida_a_borrar = st.selectbox("Selecciona partida para eliminar", options=partidas_disponibles, index=None, placeholder="Escoge una partida...")
        
        if partida_a_borrar:
            st.warning(f"⚠️ Vas a borrar: {partida_a_borrar}")
            if st.button("Confirmar Eliminación Permanente", type="primary", use_container_width=True):
                st.session_state.historico = st.session_state.historico[st.session_state.historico['ID_Partida'] != partida_a_borrar]
                st.rerun()

# --- ESTILO GLOBAL PARA TABLAS (OPCIÓN C: PODIO CLÁSICO) ---
st.markdown("""
    <style>
        .stTable {
            table-layout: fixed !important;
            width: 100% !important;
            border-collapse: collapse !important;
        }
        .stTable th, .stTable td {
            text-align: center !important;
            vertical-align: middle !important;
            padding: 3px !important;
        }
        .stTable th:first-child, .stTable td:first-child {
            width: 180px !important;
            text-align: left !important;
            padding-left: 10px !important;
        }
        .cell-fill {
            display: block;
            width: 100%;
            padding: 8px 0;
            text-align: center;
            border-radius: 6px;
        }
        .no-jugado { color: #CCCCCC; font-weight: bold; }
        .bg-1 { background-color: #FFF59D; color: #827717; font-weight: bold; }
        .bg-2 { background-color: #E0E0E0; color: #424242; font-weight: bold; }
        .bg-3 { background-color: #FFCCBC; color: #BF360C; font-weight: bold; }
        .pos-num { font-size: 1.1em; }
        .bazas-txt { font-size: 0.82em; opacity: 0.85; font-weight: normal; }
    </style>
""", unsafe_allow_html=True)

# --- VERIFICACIÓN DE DATOS ---
if not st.session_state.historico.empty:
    df = st.session_state.historico.copy()

    # --- SECCIÓN 2: CLASIFICACIÓN GENERAL (PODIO DESTACADO) ---
    st.header("🏆 Clasificación General")
    
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
    
    resumen['Diferencial'] = resumen['Total Pedidas'] - resumen['Total Hechas']
    resumen['Abs_Diferencial'] = resumen['Diferencial'].abs()

    # Ordenamos por Rendimiento y desempatamos por Diferencial absoluto (cercanía a 0)
    resumen = resumen.sort_values(
        by=['Rendimiento (%)', 'Abs_Diferencial'], 
        ascending=[False, True]
    )
    
    # Preparamos el DataFrame de visualización
    resumen_display = resumen[['Pos. Media', 'Rendimiento (%)', 'Total Pedidas', 'Total Hechas', 'Diferencial']].copy()
    resumen_display["Pos. Media"] = resumen_display["Pos. Media"].map("{:.2f}".format)
    resumen_display["Rendimiento (%)"] = resumen_display["Rendimiento (%)"].map("{:.1f}%".format)

    # Aplicamos medallas Emoji a los tres primeros
    resumen_display = resumen_display.reset_index()
    
    def aplicar_medallas(row):
        if row.name == 0: return f"🥇 {row['Jugador'].upper()}"
        if row.name == 1: return f"🥈 {row['Jugador']}"
        if row.name == 2: return f"🥉 {row['Jugador']}"
        return row['Jugador']

    resumen_display['Jugador'] = resumen_display.apply(aplicar_medallas, axis=1)
    resumen_display = resumen_display.set_index('Jugador')

    st.table(resumen_display)

    st.divider()

    # --- SECCIÓN 3: HISTÓRICO DE PARTIDAS ---
    st.header("📊 Histórico de Partidas")
    
    def formatear_info(row):
        pos = int(row['Posición'])
        clase_bg = ""
        if pos == 1: clase_bg = "bg-1"
        elif pos == 2: clase_bg = "bg-2"
        elif pos == 3: clase_bg = "bg-3"
        return f'<div class="cell-fill {clase_bg}"><span class="pos-num">{pos}</span> <span class="bazas-txt">({row["Pedidas"]}/{row["Hechas"]})</span></div>'

    df['Info'] = df.apply(formatear_info, axis=1)
    
    tabla_pivote = df.pivot_table(
        index='ID_Partida', columns='Jugador', values='Info', aggfunc='first'
    ).fillna('<div class="cell-fill"><span class="no-jugado">•</span></div>')
    
    tabla_pivote.index.name = "Partida (Fecha [Hora])"
    
    st.write("Leyenda: **Posición (Bazas Pedidas / Bazas Hechas)**")
    st.write(tabla_pivote.to_html(escape=False, classes='stTable'), unsafe_allow_html=True)

else:
    st.info("No hay datos registrados todavía. Abre 'Gestión de Partidas' para empezar.")