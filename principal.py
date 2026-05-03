import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Pocha Stats", layout="centered")

# --- CONTROL DE ACCESO (OPCIÓN 1) ---
def check_password():
    """Devuelve True si el usuario introdujo la contraseña correcta."""
    def password_entered():
        """Comprueba si la contraseña coincide."""
        if st.session_state["password_input"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]  # Eliminar contraseña de session_state
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Pantalla inicial de login
        st.text_input(
            "Introduce la contraseña para entrar", 
            type="password", 
            on_change=password_entered, 
            key="password_input"
        )
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 Contraseña incorrecta")
        return False
    return True

if not check_password():
    st.stop()  # Detiene la ejecución si no hay contraseña correcta

# --- PERSISTENCIA TEMPORAL (Session State) ---
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=[
        'ID_Partida', 'Fecha', 'Jugador', 'Posición', 'Pedidas', 'Hechas', 'Num_Jugadores'
    ])

if 'jugadores' not in st.session_state:
    st.session_state.jugadores = ["pedro", "jd", "pedri", "lauri", "carlis", "ali", "deni", "rober", "mire", "adri", "mari"]

st.title("🃏 Pocha Stats")

# --- ESTILO CSS PERSONALIZADO ---
st.markdown("""
    <style>
        /* 1. Forzar que los botones +/- aparezcan siempre */
        div[data-testid="stNumberInput"] button {
            display: flex !important;
        }
        
        /* 2. Centrar el número dentro del input */
        div[data-testid="stNumberInput"] input {
            text-align: center !important;
            padding-right: 0px !important;
        }

        /* 3. Ajustes estéticos de las tablas de resultados */
        .stTable {
            table-layout: fixed !important;
            width: 100% !important;
            border-collapse: collapse !important;
        }
        .stTable th {
            font-weight: normal !important;
            color: #666666 !important;
            text-align: center !important;
        }
        .stTable td {
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
        .no-jugado { color: #CCCCCC; }
        .bg-1 { background-color: #FFF59D; color: #827717; }
        .bg-2 { background-color: #E0E0E0; color: #424242; }
        .bg-3 { background-color: #FFCCBC; color: #BF360C; }
        .pos-num { font-size: 1.1em; }
        .bazas-txt { font-size: 0.82em; opacity: 0.85; }
    </style>
""", unsafe_allow_html=True)

# --- SECCIÓN 1: GESTIÓN DE PARTIDAS ---
with st.expander("📝 Gestión de Partidas", expanded=False):
    
    st.subheader("Nueva Partida")
    c_top1, c_top2 = st.columns(2)
    with c_top1:
        fecha = st.date_input("Fecha", datetime.now())
    with c_top2:
        num_jug = st.number_input("Nº Jugadores", min_value=1, max_value=len(st.session_state.jugadores), value=4)
    
    st.divider()
    
    # Columnas con espacio ajustado para los nuevos nombres de cabecera
    h1, h2, h3, h4, h5 = st.columns([0.4, 1.8, 1.3, 1.3, 1.3])
    h1.caption("ID")
    h2.caption("Jugador")
    h3.caption("Posición")
    h4.caption("Pedidas")
    h5.caption("Hechas")

    datos_partida = []
    for i in range(num_jug):
        c1, c2, c3, c4, c5 = st.columns([0.4, 1.8, 1.3, 1.3, 1.3])
        with c1:
            st.markdown(f"<div style='padding-top:7px; color:gray;'>{i+1}</div>", unsafe_allow_html=True)
        with c2:
            nom = st.selectbox(f"N_{i}", st.session_state.jugadores, key=f"n_{i}", label_visibility="collapsed")
        with c3:
            pos = st.number_input(f"P_{i}", 1, 20, value=i+1, key=f"p_{i}", label_visibility="collapsed")
        with c4:
            ped = st.number_input(f"A_{i}", 0, 100, value=0, key=f"a_{i}", label_visibility="collapsed")
        with c5:
            hac = st.number_input(f"H_{i}", 0, 100, value=0, key=f"h_{i}", label_visibility="collapsed")
        
        datos_partida.append({
            'Fecha': fecha, 
            'Jugador': nom, 
            'Posición': pos, 
            'Pedidas': ped, 
            'Hechas': hac,
            'Num_Jugadores': num_jug
        })

    if st.button("Guardar Partida", use_container_width=True, type="primary"):
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

    # --- SUBSECCIÓN: ELIMINAR PARTIDAS ---
    if not st.session_state.historico.empty:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.divider()
        st.subheader("🗑️ Eliminar Partida")
        partidas_disponibles = st.session_state.historico['ID_Partida'].unique()
        partida_a_borrar = st.selectbox("Selecciona partida para eliminar", 
                                       options=partidas_disponibles, 
                                       index=None, 
                                       placeholder="Escoge una partida...")
        
        if partida_a_borrar:
            st.warning(f"⚠️ Vas a borrar: {partida_a_borrar}")
            if st.button("Confirmar Eliminación", type="primary", use_container_width=True):
                st.session_state.historico = st.session_state.historico[st.session_state.historico['ID_Partida'] != partida_a_borrar]
                st.rerun()

# --- VISUALIZACIÓN DE RESULTADOS ---
if not st.session_state.historico.empty:
    df = st.session_state.historico.copy()

    # Ranking
    st.header("🏆 Clasificación General")
    def calcular_rendimiento(row):
        if row['Num_Jugadores'] <= 1: return 100.0
        return ((row['Num_Jugadores'] - row['Posición']) / (row['Num_Jugadores'] - 1)) * 100

    df['Rendimiento'] = df.apply(calcular_rendimiento, axis=1)
    resumen = df.groupby('Jugador').agg({'Rendimiento': 'mean', 'Posición': 'mean', 'Pedidas': 'sum', 'Hechas': 'sum'}).rename(columns={'Rendimiento': 'Rendimiento (%)', 'Posición': 'Posición media', 'Pedidas': 'Total Pedidas', 'Hechas': 'Total Hechas'})
    resumen['Diferencial'] = resumen['Total Pedidas'] - resumen['Total Hechas']
    resumen['Abs_Diferencial'] = resumen['Diferencial'].abs()
    resumen = resumen.sort_values(by=['Rendimiento (%)', 'Abs_Diferencial'], ascending=[False, True])
    
    res_disp = resumen[['Rendimiento (%)', 'Posición media', 'Total Pedidas', 'Total Hechas', 'Diferencial']].copy()
    res_disp["Posición media"] = res_disp["Posición media"].map("{:.2f}".format)
    res_disp["Rendimiento (%)"] = res_disp["Rendimiento (%)"].map("{:.1f}%".format)
    res_disp = res_disp.reset_index()

    def aplicar_iconos(row):
        if row.name == 0: return f"🥇 {row['Jugador'].upper()}"
        if row.name == 1: return f"🥈 {row['Jugador']}"
        if row.name == 2: return f"🥉 {row['Jugador']}"
        return f"⚪ {row['Jugador']}"

    res_disp['Jugador'] = res_disp.apply(aplicar_iconos, axis=1)
    st.table(res_disp.set_index('Jugador'))

    st.divider()

    # Historial
    st.header("📊 Histórico de Partidas")
    def formatear_info(row):
        pos = int(row['Posición'])
        clase_bg = "bg-1" if pos == 1 else "bg-2" if pos == 2 else "bg-3" if pos == 3 else ""
        return f'<div class="cell-fill {clase_bg}"><span class="pos-num">{pos}</span> <span class="bazas-txt">({row["Pedidas"]}/{row["Hechas"]})</span></div>'

    df['Info'] = df.apply(formatear_info, axis=1)
    tabla_pivote = df.pivot_table(index='ID_Partida', columns='Jugador', values='Info', aggfunc='first').fillna('<div class="cell-fill"><span class="no-jugado">•</span></div>')
    tabla_pivote.index.name = "Partida"
    st.write(tabla_pivote.to_html(escape=False, classes='stTable'), unsafe_allow_html=True)
else:
    st.info("No hay datos todavía.")