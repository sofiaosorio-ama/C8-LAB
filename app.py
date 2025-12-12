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
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- SISTEMA DE LOGIN Y REGISTRO ---
def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=80)
        st.markdown("<h2 style='text-align: center;'>Acceso Inteligencia C8</h2>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Iniciar Sesión", "📝 Registrarse"])
        
        # --- TAB 1: LOGIN ---
        with tab1:
            username = st.text_input("Usuario", key="login_user")
            password = st.text_input("Contraseña", type="password", key="login_pass")
            
            if st.button("Entrar", key="btn_login"):
                sheet = connect_to_gsheets()
                if sheet:
                    try:
                        ws_users = sheet.worksheet("Usuarios")
                        users_data = ws_users.get_all_records()
                        
                        # Buscar usuario
                        user_found = False
                        for user in users_data:
                            if str(user["Usuario"]) == username and str(user["Password"]) == password:
                                st.session_state.authenticated = True
                                st.session_state.current_user = username
                                st.success(f"¡Bienvenida de nuevo, {user['Nombre']}!")
                                time.sleep(1)
                                st.rerun()
                                user_found = True
                                break
                        
                        if not user_found:
                            st.error("Usuario o contraseña incorrectos.")
                    except:
                        st.error("Error conectando a base de usuarios.")
                else:
                    st.error("Error de conexión con Google Sheets.")

        # --- TAB 2: REGISTRO ---
        with tab2:
            new_user = st.text_input("Elige un Usuario", key="reg_user")
            new_pass = st.text_input("Elige una Contraseña", type="password", key="reg_pass")
            new_name = st.text_input("Tu Nombre Real", key="reg_name")
            
            if st.button("Crear Cuenta", key="btn_reg"):
                sheet = connect_to_gsheets()
                if sheet and new_user and new_pass:
                    try:
                        ws_users = sheet.worksheet("Usuarios")
                        # Verificar si ya existe
                        existing_users = ws_users.col_values(1)
                        if new_user in existing_users:
                            st.warning("⚠️ Ese usuario ya existe. Elige otro.")
                        else:
                            ws_users.append_row([new_user, new_pass, new_name, str(datetime.now())])
                            st.success("✅ ¡Cuenta creada con éxito! Ahora inicia sesión.")
                    except Exception as e:
                        st.error(f"Error al registrar: {e}")
                else:
                    st.warning("Por favor completa todos los campos.")

# --- APLICACIÓN PRINCIPAL ---
def main_app():
    user = st.session_state.current_user
    
    # Cargar Arquetipos Base
    active_archetypes = {
        "El Provocador": "ERES EL PROVOCADOR. Tono: Cínico, agresivo. (Golpea la mesa).",
        "El Educador": "ERES EL EDUCADOR. Tono: Calmado, pedagógico. (Se ajusta las gafas).",
        "El Curador": "ERES EL CURADOR. Tono: Exigente, esteta. (Mira con ojo crítico).",
        "El Visionario": "ERES EL VISIONARIO. Tono: Inspirador. (Mira al horizonte)."
    }
    
    # Cargar Agentes de Google Sheets
    sheet = connect_to_gsheets()
    if sheet:
        try:
            ws_agents = sheet.worksheet("Agentes")
            agents_data = ws_agents.get_all_records()
            for agent in agents_data:
                # Filtrar si quieres que sean públicos o privados (ahora son públicos para todos)
                active_archetypes[agent["Nombre"]] = agent["Personalidad"]
        except:
            pass 

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"### 👤 {user.upper()}")
        if st.button("Cerrar Sesión"):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()
        
        st.divider()
        
        # 1. HISTORIAL (FILTRADO POR USUARIO - Próxima mejora, ahora ve todos)
        st.subheader("📂 Chats Guardados")
        if st.button("🔄 Actualizar"):
            st.rerun()
            
        if sheet:
            try:
                ws_chats = sheet.worksheet("Chats")
                # Solo cargamos los títulos para el selector
                titles = ws_chats.col_values(1)[1:] 
                unique_titles = list(set(titles))
                selected_chat = st.selectbox("Abrir Chat:", ["-"] + unique_titles)
                
                if selected_chat != "-":
                    if st.button("📂 Cargar"):
                        all_rows = ws_chats.get_all_records()
                        # Filtramos las filas que coincidan con el título
                        chat_rows = [row for row in all_rows if row["Titulo"] == selected_chat]
                        
                        loaded_msgs = []
                        for row in chat_rows:
                            loaded_msgs.append({"role": row["Role"], "name": row["Name"], "content": row["Content"]})
                        
                        st.session_state.messages = loaded_msgs
                        st.success("Chat cargado.")
                        time.sleep(1)
                        st.rerun()
            except:
                st.caption("Sin conexión a historial.")
        
        st.divider()

        # 2. CREADOR AGENTES
        with st.expander("✨ Crear Nuevo Agente"):
            new_name = st.text_input("Nombre Rol")
            new_desc = st.text_area("Personalidad")
            if st.button("Guardar"):
                if new_name and new_desc and sheet:
                    try:
                        ws_agents = sheet.worksheet("Agentes")
                        if not ws_agents.row_values(1):
                            ws_agents.append_row(["Nombre", "Personalidad", "Creador", "Fecha"])
                        
                        full_desc = f"ERES {new_name.upper()}.\nPersonalidad: {new_desc}\nInstrucción: Actúa acorde."
                        ws_agents.append_row([new_name, full_desc, user, str(datetime.now())])
                        st.success("Agente creado.")
                        time.sleep(1)
                        st.rerun()
                    except:
                        st.error("Error al guardar.")

        st.divider()
        scenario = st.selectbox("Escenario:", ["Validación Idea", "Lanzamiento", "Crisis", "Pitch"])
        selected_archetypes = st.multiselect("Consejo:", options=list(active_archetypes.keys()), default=["El Provocador", "El Educador"])

        if st.button("🗑️ Limpiar Pantalla"):
            st.session_state.messages = []
            st.rerun()

    # --- PANTALLA PRINCIPAL ---
    st.title(f"🧬 Laboratorio C8: {scenario}")

    if len(st.session_state.messages) == 0:
        st.info(f"Conectado como {user}. Agentes: {len(active_archetypes)}")
        initial_idea = st.chat_input("Escribe tu idea...")
        if initial_idea:
            st.session_state.messages.append({"role": "user", "content": initial_idea, "name": user})
            st.session_state.simulation_active = True
            st.rerun()

    for msg in st.session_state.messages:
        avatar = "👩‍💻" if msg["role"] == "user" else "⚡"
        if msg.get("name") == "C8 INTELLIGENCE": avatar = "📊"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(f"**{msg.get('name')}**")
            if msg.get("name") == "C8 INTELLIGENCE":
                 st.markdown(f"<div class='report-box'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                 st.markdown(msg["content"])

    # MOTOR SIMULACIÓN
    if st.session_state.simulation_active:
        if not api_key_configured:
            st.warning("⚠️ Falta API Key.")
            st.stop()
        
        st.markdown("---")
        rounds = 3
        for r in range(rounds):
            st.markdown(f"#### 🔄 Ronda {r+1} de {rounds}")
            for agent_name in selected_archetypes:
                with st.chat_message("assistant", avatar="🎭"):
                    with st.spinner(f"{agent_name}..."):
                        persona = active_archetypes[agent_name]
                        prompt = f"Estás interpretando a: {agent_name}\nPERFIL: {persona}\nCONTEXTO: {scenario}, Ronda {r+1}.\nINSTRUCCIÓN: Interactúa, usa teatro, sé breve."
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
                            st.error(str(e))
                time.sleep(0.5)
        st.session_state.simulation_active = False
        st.rerun()

    # GUARDAR
    if not st.session_state.simulation_active and len(st.session_state.messages) > 1:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.chat_input("Responder...")
        with col2:
            save_name = st.text_input("Nombre Chat:", placeholder="Ej: Idea 1")
            if st.button("💾 Guardar"):
                if save_name and sheet:
                    try:
                        ws_chats = sheet.worksheet("Chats")
                        if not ws_chats.row_values(1):
                            ws_chats.append_row(["Titulo", "Fecha", "Role", "Name", "Content", "Owner"])
                        
                        rows_to_add = []
                        now = str(datetime.now())
                        for m in st.session_state.messages:
                            # Añadimos columna de "Owner" (Dueño) para filtrar en el futuro
                            rows_to_add.append([save_name, now, m["role"], m["name"], m["content"], user])
                        
                        for row in rows_to_add:
                            ws_chats.append_row(row)
                        st.success("¡Archivado!")
                    except Exception as e:
                        st.error(f"Error: {e}")

# --- FLUJO ---
if st.session_state.authenticated:
    main_app()
else:
    login_page()
