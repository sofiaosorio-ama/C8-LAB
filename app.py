import streamlit as st
import openai
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema de Inteligencia C8", page_icon="🧬", layout="wide")

# --- ESTILOS VISUALES ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .stChatMessage { background-color: #ffffff !important; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 15px; color: #000000 !important; }
    .stChatMessage p, .stChatMessage li, .stChatMessage h1 { color: #1E293B !important; }
    
    div[data-testid="stChatMessage"]:nth-child(odd) { border-left: 6px solid #2196F3; }
    div[data-testid="stChatMessage"]:nth-child(even) { border-left: 6px solid #000000; background-color: #f8f9fa !important; }
    
    .report-box { background-color: #e3f2fd; padding: 25px; border-radius: 10px; border: 1px solid #90caf9; margin-top: 20px; }
    .report-box p { color: #0d47a1 !important; }
    
    .stButton button { width: 100%; border-radius: 8px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
def connect_to_gsheets():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        # Convertimos los secretos a formato legible
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            sheet = client.open("C8_DB")
            return sheet
        else:
            return None
    except Exception as e:
        # Error silencioso para no ensuciar la pantalla si no está configurado
        return None

# --- GESTIÓN DE API KEY ---
try:
    if "OPENAI_API_KEY" in st.secrets:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        api_key_configured = True
    else:
        api_key_configured = False
except:
    api_key_configured = False

# --- MEMORIA ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "simulation_active" not in st.session_state:
    st.session_state.simulation_active = False
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- PANTALLA DE ACCESO (LOGIN) ---
def login_screen():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=80)
        st.markdown("<h1 style='text-align: center;'>Acceso Inteligencia C8</h1>", unsafe_allow_html=True)
        
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar al Laboratorio"):
            if username == "sofia" and password == "c8":
                st.session_state.authenticated = True
                st.session_state.current_user = "sofia"
                st.rerun()
            else:
                st.error("❌ Datos incorrectos")

# --- APLICACIÓN PRINCIPAL ---
def main_app():
    # Cargar Arquetipos Base
    active_archetypes = {
        "El Provocador": "ERES EL PROVOCADOR. Tono: Cínico, agresivo. (Golpea la mesa).",
        "El Educador": "ERES EL EDUCADOR. Tono: Calmado, pedagógico. (Se ajusta las gafas).",
        "El Curador": "ERES EL CURADOR. Tono: Exigente, esteta. (Mira con ojo crítico).",
        "El Visionario": "ERES EL VISIONARIO. Tono: Inspirador. (Mira al horizonte)."
    }
    
    # Intentar cargar agentes personalizados de Google Sheets
    sheet = connect_to_gsheets()
    if sheet:
        try:
            ws_agents = sheet.worksheet("Agentes")
            agents_data = ws_agents.get_all_records()
            for agent in agents_data:
                active_archetypes[agent["Nombre"]] = agent["Personalidad"]
        except:
            pass 

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.markdown(f"### 👤 Arquitecta C8")
        if st.button("Cerrar Sesión"):
            st.session_state.authenticated = False
            st.rerun()
        
        st.divider()
        
        # 1. HISTORIAL GOOGLE SHEETS
        st.subheader("📂 Archivo de Chats (Nube)")
        if st.button("🔄 Actualizar Lista"):
            st.rerun()
            
        if sheet:
            try:
                ws_chats = sheet.worksheet("Chats")
                titles = ws_chats.col_values(1)[1:] # Nombres de chats
                # Eliminamos duplicados y mostramos
                unique_titles = list(set(titles))
                selected_chat = st.selectbox("Seleccionar Chat Guardado:", ["-"] + unique_titles)
                
                if selected_chat != "-":
                    if st.button("📂 Cargar este Chat"):
                        all_rows = ws_chats.get_all_records()
                        chat_rows = [row for row in all_rows if row["Titulo"] == selected_chat]
                        
                        loaded_msgs = []
                        for row in chat_rows:
                            loaded_msgs.append({"role": row["Role"], "name": row["Name"], "content": row["Content"]})
                        
                        st.session_state.messages = loaded_msgs
                        st.success(f"Chat '{selected_chat}' recuperado.")
                        time.sleep(1)
                        st.rerun()
            except:
                st.caption("No se encontraron chats aún.")
        else:
            st.warning("⚠️ Base de datos no conectada en Secrets")
        
        st.divider()

        # 2. CREADOR DE AGENTES
        with st.expander("✨ Crear Nuevo Agente"):
            new_name = st.text_input("Nombre del Rol")
            new_desc = st.text_area("Personalidad y Actitud")
            if st.button("Guardar Agente en Nube"):
                if new_name and new_desc and sheet:
                    try:
                        ws_agents = sheet.worksheet("Agentes")
                        if not ws_agents.row_values(1):
                            ws_agents.append_row(["Nombre", "Personalidad", "Fecha"])
                        
                        full_desc = f"ERES {new_name.upper()}.\nPersonalidad: {new_desc}\nInstrucción: Actúa exageradamente acorde a este rol."
                        ws_agents.append_row([new_name, full_desc, str(datetime.now())])
                        st.success(f"¡{new_name} guardado para siempre!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")

        st.divider()
        scenario = st.selectbox("Escenario:", ["Validación de Idea", "Lanzamiento Oficial", "Gestión de Crisis", "Pitch de Venta", "Rebranding"])
        selected_archetypes = st.multiselect("Consejo Activo:", options=list(active_archetypes.keys()), default=["El Provocador", "El Educador"])

        if st.button("🗑️ Nueva Sesión (Limpiar)"):
            st.session_state.messages = []
            st.rerun()

    # --- PANTALLA PRINCIPAL ---
    st.title(f"🧬 Laboratorio C8: {scenario}")

    # Input Inicial
    if len(st.session_state.messages) == 0:
        st.info(f"Conectado al Sistema C8. Agentes disponibles: {len(active_archetypes)}")
        initial_idea = st.chat_input("Escribe tu idea, copy o estrategia aquí...")
        if initial_idea:
            st.session_state.messages.append({"role": "user", "content": initial_idea, "name": "Sofia"})
            st.session_state.simulation_active = True
            st.rerun()

    # Mostrar Chat
    for msg in st.session_state.messages:
        avatar = "👩‍💻" if msg["role"] == "user" else "⚡"
        if msg.get("name") == "C8 INTELLIGENCE": avatar = "📊"
        
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(f"**{msg.get('name')}**")
            if msg.get("name") == "C8 INTELLIGENCE":
                 st.markdown(f"<div class='report-box'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                 st.markdown(msg["content"])

    # MOTOR DE SIMULACIÓN
    if st.session_state.simulation_active:
        if not api_key_configured:
            st.warning("⚠️ Falta configurar la API Key de OpenAI.")
            st.stop()
        
        st.markdown("---")
        rounds = 3
        for r in range(rounds):
            st.markdown(f"#### 🔄 Ronda {r+1} de {rounds}")
            for agent_name in selected_archetypes:
                with st.chat_message("assistant", avatar="🎭"):
                    with st.spinner(f"{agent_name} analizando..."):
                        persona = active_archetypes[agent_name]
                        prompt = f"""
                        Estás interpretando a: {agent_name}
                        TU PERFIL: {persona}
                        CONTEXTO: Escenario {scenario}, Ronda {r+1}.
                        
                        INSTRUCCIONES CLAVE:
                        1. Interactúa con los otros por su nombre.
                        2. Usa acotaciones teatrales (ej: *se levanta*, *mira con duda*).
                        3. Sé humano, directo y con la personalidad marcada.
                        """
                        msgs = [{"role": "system", "content": prompt}]
                        for m in st.session_state.messages:
                            msgs.append({"role": "user" if m["role"]=="user" else "assistant", "content": f"{m.get('name')}: {m['content']}"})
                        
                        try:
                            client = openai.OpenAI()
                            res = client.chat.completions.create(model="gpt-3.5-turbo", messages=msgs, temperature=0.85, max_tokens=550)
                            reply = res.choices[0].message.content
                            
                            st.markdown(f"**{agent_name}**")
                            st.markdown(reply)
                            st.session_state.messages.append({"role": "assistant", "content": reply, "name": agent_name})
                        except Exception as e:
                            st.error(f"Error de IA: {str(e)}")
                time.sleep(0.5)
        st.session_state.simulation_active = False
        st.rerun()

    # ZONA DE GUARDADO (ABAJO)
    if not st.session_state.simulation_active and len(st.session_state.messages) > 1:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.chat_input("Responder al consejo...") # Dummy visual
        with col2:
            save_name = st.text_input("Nombre del Chat:", placeholder="Ej: Idea Lanzamiento")
            if st.button("💾 Guardar en Nube"):
                if save_name and sheet:
                    try:
                        ws_chats = sheet.worksheet("Chats")
                        # Crear encabezados si está vacía
                        if not ws_chats.row_values(1):
                            ws_chats.append_row(["Titulo", "Fecha", "Role", "Name", "Content"])
                        
                        rows_to_add = []
                        now = str(datetime.now())
                        for m in st.session_state.messages:
                            rows_to_add.append([save_name, now, m["role"], m["name"], m["content"]])
                        
                        for row in rows_to_add:
                            ws_chats.append_row(row)
                            
                        st.success("¡Guardado en Google Sheets!")
                    except Exception as e:
                        st.error(f"Error guardando: {e}")
                elif not sheet:
                    st.error("Error: Base de datos no conectada.")

# --- INICIO ---
if st.session_state.authenticated:
    main_app()
else:
    login_screen()
