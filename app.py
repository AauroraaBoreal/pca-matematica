import streamlit as st
import pandas as pd
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CONFIG ---
st.set_page_config(
    page_title="GDP Validator",
    page_icon="🎰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS ---
st.markdown("""
<style>
    .main { background-color: #0f0f0f; }
    .stApp { background-color: #0f0f0f; color: #ffffff; }
    .metric-card {
        background: #1a1a2e;
        border: 1px solid #16213e;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .anomalia-card {
        background: #1a0000;
        border-left: 4px solid #ff4444;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .normal-card {
        background: #001a00;
        border-left: 4px solid #44ff44;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .reporte-box {
        background: #1a1a2e;
        border: 1px solid #444;
        border-radius: 8px;
        padding: 20px;
        font-family: monospace;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# --- AUTENTICACIÓN ---
def login():
    st.markdown("<h1 style='text-align:center; color:#fff;'>🎰 GDP Validator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#aaa;'>Sistema inteligente de validación de jugadas</p>", unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("### Iniciar sesión")
        email = st.text_input("Correo electrónico", placeholder="analista@gdp.com")
        password = st.text_input("Contraseña", type="password")

        if st.button("Ingresar", use_container_width=True, type="primary"):
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state['user'] = response.user
                st.session_state['session'] = response.session
                st.rerun()
            except Exception as e:
                st.error("Correo o contraseña incorrectos")

def logout():
    supabase.auth.sign_out()
    st.session_state.clear()
    st.rerun()

# --- PROCESAR CSV ---
def procesar_archivo(uploaded_file):
    import tempfile
    from modules.modulo1_carga import cargar_csv
    from modules.modulo2_clasificacion import clasificar_eventos
    from modules.modulo3_anomalias import detectar_anomalias
    from modules.modulo4_base_datos import crear_tablas, guardar_jugador, guardar_validacion, guardar_anomalias
    from modules.modulo5_reportes import generar_reporte_whatsapp, generar_reporte_qa

    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        with st.spinner("Cargando y preprocesando datos..."):
            df = cargar_csv(tmp_path)

        with st.spinner("Clasificando eventos..."):
            df = clasificar_eventos(df)

        with st.spinner("Detectando anomalías..."):
            df, _ = detectar_anomalias(df)

        with st.spinner("Guardando en base de datos..."):
            crear_tablas()
            guardar_jugador(df)

        anomalias = df[df['es_anomalia'] == True]
        resultado = 'sospechoso' if len(anomalias) > 0 else 'normal'
        reporte_whatsapp = generar_reporte_whatsapp(df)
        reporte_qa = generar_reporte_qa(anomalias) if len(anomalias) > 0 else None

        validacion_id = guardar_validacion(df, resultado, reporte_whatsapp)
        guardar_anomalias(anomalias, validacion_id)

        os.unlink(tmp_path)
        return df, anomalias, resultado, reporte_whatsapp, reporte_qa

    except Exception as e:
        os.unlink(tmp_path)
        raise e

# --- PÁGINA: VALIDAR ---
def pagina_validar():
    st.markdown("## 📂 Nueva validación")
    st.markdown("Sube el archivo CSV del jugador para procesarlo.")

    uploaded_file = st.file_uploader(
        "Selecciona el archivo CSV",
        type=['csv'],
        help="Archivo de jugadas exportado del sistema de GDP Studios"
    )

    if uploaded_file:
        st.info(f"Archivo cargado: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

        if st.button("🔍 Procesar archivo", type="primary", use_container_width=True):
            try:
                df, anomalias, resultado, reporte_whatsapp, reporte_qa = procesar_archivo(uploaded_file)

                # Métricas resumen
                st.divider()
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total registros", f"{len(df):,}")
                with col2:
                    st.metric("Jugador", str(df['PlayerId'].iloc[0]))
                with col3:
                    st.metric("Anomalías detectadas", len(anomalias))
                with col4:
                    st.metric("Resultado", "⚠️ Sospechoso" if resultado == 'sospechoso' else "✅ Normal")

                st.divider()

                if resultado == 'normal':
                    st.markdown("<div class='normal-card'>✅ <b>Validación normal</b> — No se detectaron anomalías en este archivo.</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='anomalia-card'>⚠️ <b>Se detectaron {len(anomalias)} registros sospechosos</b> que requieren revisión.</div>", unsafe_allow_html=True)

                # Reportes
                st.markdown("### 📋 Reporte WhatsApp")
                st.code(reporte_whatsapp, language=None)
                if st.button("📋 Copiar reporte WhatsApp"):
                    st.write("✅ Copiado al portapapeles")
                    st.session_state['clipboard'] = reporte_whatsapp

                if reporte_qa:
                    st.markdown("### 🔴 Reporte para QA")
                    st.code(reporte_qa, language=None)

                    # Tabla de anomalías
                    st.markdown("### 📊 Detalle de anomalías")
                    df_display = anomalias[[
                        'EventTime', 'GameId', 'TotalBet', 'TotalWin',
                        'TotalJPWin', 'ratio_ganancia', 'tipo_anomalia'
                    ]].copy()
                    df_display.index = df_display.index + 1
                    df_display.columns = ['Fecha/Hora', 'Juego', 'Apuesta', 'Ganancia', 'Jackpot', 'Ratio', 'Tipo']
                    df_display['Apuesta'] = df_display['Apuesta'].apply(lambda x: f"${x:,.2f}")
                    df_display['Ganancia'] = df_display['Ganancia'].apply(lambda x: f"${x:,.2f}")
                    st.dataframe(df_display, use_container_width=True)

            except Exception as e:
                st.error(f"Error al procesar el archivo: {str(e)}")

# --- PÁGINA: HISTORIAL ---
def pagina_historial():
    st.markdown("## 📜 Historial de validaciones")

    try:
        response = supabase.table('validaciones').select(
            'validacion_id, player_id, fecha_inicio, fecha_fin, total_registros, resultado, fecha_procesamiento'
        ).order('fecha_procesamiento', desc=True).limit(50).execute()

        if not response.data:
            st.info("No hay validaciones registradas aún.")
            return

        df_hist = pd.DataFrame(response.data)
        df_hist['fecha_procesamiento'] = pd.to_datetime(df_hist['fecha_procesamiento']).dt.strftime('%d/%m/%Y %H:%M')
        df_hist['fecha_inicio'] = pd.to_datetime(df_hist['fecha_inicio']).dt.strftime('%d/%m/%Y')
        df_hist['fecha_fin'] = pd.to_datetime(df_hist['fecha_fin']).dt.strftime('%d/%m/%Y')
        df_hist['resultado'] = df_hist['resultado'].apply(
            lambda x: '⚠️ Sospechoso' if x == 'sospechoso' else '✅ Normal'
        )
        df_hist.columns = ['ID', 'Jugador', 'Desde', 'Hasta', 'Registros', 'Resultado', 'Procesado']

        # Filtro por jugador
        jugadores = ['Todos'] + sorted(df_hist['Jugador'].unique().tolist())
        filtro = st.selectbox("Filtrar por jugador", jugadores)
        if filtro != 'Todos':
            df_hist = df_hist[df_hist['Jugador'] == filtro]

        st.dataframe(df_hist, use_container_width=True, hide_index=True)

        # Ver detalle de anomalías
        st.markdown("### 🔍 Ver anomalías de una validación")
        validacion_id = st.number_input("ID de validación", min_value=1, step=1)
        if st.button("Ver anomalías"):
            anom_response = supabase.table('anomalias').select('*').eq(
                'validacion_id', validacion_id
            ).execute()
            if not anom_response.data:
                st.info("Esta validación no tiene anomalías registradas.")
            else:
                df_anom = pd.DataFrame(anom_response.data)
                st.dataframe(df_anom[[
                    'event_time', 'game_id', 'total_bet',
                    'total_win', 'tipo_anomalia', 'score_anomalia'
                ]], use_container_width=True)

    except Exception as e:
        st.error(f"Error al cargar historial: {str(e)}")

# --- PÁGINA: JUGADORES ---
def pagina_jugadores():
    st.markdown("## 👤 Perfil de jugadores")

    try:
        response = supabase.table('jugadores').select('*').order(
            'ultima_actualizacion', desc=True
        ).execute()

        if not response.data:
            st.info("No hay jugadores registrados aún.")
            return

        df_jug = pd.DataFrame(response.data)
        df_jug['ultima_actualizacion'] = pd.to_datetime(
            df_jug['ultima_actualizacion']
        ).dt.strftime('%d/%m/%Y %H:%M')
        df_jug['apuesta_promedio'] = df_jug['apuesta_promedio'].apply(lambda x: f"${x:,.2f}")
        df_jug['apuesta_max'] = df_jug['apuesta_max'].apply(lambda x: f"${x:,.2f}")
        df_jug['ganancia_max'] = df_jug['ganancia_max'].apply(lambda x: f"${x:,.2f}")

        st.dataframe(df_jug[[
            'player_id', 'currency', 'apuesta_promedio', 'apuesta_max',
            'ganancia_max', 'ratio_promedio', 'total_sesiones', 'ultima_actualizacion'
        ]].rename(columns={
            'player_id': 'Jugador',
            'currency': 'Moneda',
            'apuesta_promedio': 'Apuesta Prom.',
            'apuesta_max': 'Apuesta Máx.',
            'ganancia_max': 'Ganancia Máx.',
            'ratio_promedio': 'Ratio Prom.',
            'total_sesiones': 'Sesiones',
            'ultima_actualizacion': 'Última validación'
        }), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error al cargar jugadores: {str(e)}")

# --- NAVEGACIÓN PRINCIPAL ---
def main():
    if 'user' not in st.session_state:
        login()
        return

    user = st.session_state['user']

    with st.sidebar:
        st.markdown("### 🎰 GDP Validator")
        st.markdown(f"👤 **{user.email}**")
        st.divider()

        pagina = st.radio(
            "Navegación",
            ["📂 Nueva validación", "📜 Historial", "👤 Jugadores"],
            label_visibility="collapsed"
        )

        st.divider()
        if st.button("Cerrar sesión", use_container_width=True):
            logout()

    if pagina == "📂 Nueva validación":
        pagina_validar()
    elif pagina == "📜 Historial":
        pagina_historial()
    elif pagina == "👤 Jugadores":
        pagina_jugadores()

if __name__ == "__main__":
    main()