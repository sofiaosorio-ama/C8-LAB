import streamlit as st
import openai
import time
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="C8 Intelligence System", page_icon="🧬", layout="wide")

# --- ESTILOS VISUALES (C8 BRANDING & VISIBILIDAD) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* BURBUJAS DE CHAT: TEXTO NEGRO SIEMPRE */
    .stChatMessage {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 15px;
        color: #000000 !important;
    }
    .stChatMessage p, .stChatMessage li, .stChatMessage h1 { color: #1E293B !important; }
    
    /* Diferenciación visual */
    div[data-testid="stChatMessage"]:nth-child(odd) { border-left: 6px solid #2196F3; }
    div[data-testid="stChatMessage"]:nth-child(even) { border-left: 6px solid #000000; background-color: #f8f9fa !important; }

    /* Caja de Reporte */
    .report-box {
        background-color: #e3f2fd; padding: 25px; border-radius: 10px; border: 1px solid #90caf9; margin-top: 20px;
    }
    .report-box p { color: #0d47a1 !important; }

    /* Login Box */
    .login-box {
        padding: 40px; border-radius: 20px; background-color: #f8f9fa; border: 1px solid #e0e0e0; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- GESTIÓN DE API KEY ---
try:
    if "OPENAI_API_KEY" in st.secrets:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        api_key_configured = True
    else:
        api_key_configured = False
except:
    api_key_configured = False

# --- BASE DE DATOS SIMULADA (RAM) ---
# Aquí guardamos los usuarios y sus datos temporalmente
if "db" not in st.session_state:
    st.session_state.db = {
        "sofia": {
            "password": "c8",
            "chats": {}, # Aquí se guardarán los chats
            "custom_agents": {} # Aquí sus agentes creados
        },
        "invitado": {
            "password": "123",
            "chats": {},
            "custom_agents": {}
        }
    }

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- ARQUETIPOS BASE ---
base_archetypes = {
    "El Provocador": "ERES EL PROVOCADOR. Tono: Cínico, agresivo. (Golpea la mesa). Misión: Destruir el humo.",
    "El Educador": "ERES EL EDUCADOR. Tono: Calmado, pedagógico. (Se ajusta las gafas). Misión: Enseñar el cómo.",
    "El Curador": "ERES EL CURADOR. Tono: Exigente, esteta. (Mira con ojo crítico). Misión: Filtrar calidad.",
    "El Visionario": "ERES EL VISIONARIO. Tono: Inspirador. (Mira al horizonte). Misión: Propósito y legado."
}

# --- PANTALLA DE LOGIN ---
def login_screen():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=80)
        st.markdown("<h1 style='text-align: center;'>C8 Intelligence Access</h1>", unsafe_allow_html=True)
        st.info("🔐 Acceso Privado. Usa usuario: `sofia` / pass: `c8`")
        
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar al Laboratorio"):
            if username in st.session_state.db and st.session_state.db[username]["password"] == password:
                st.session_state.authenticated = True
                st.session_state.current_user = username
                st.success("✅ Acceso Autorizado")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Credenciales inválidas")

# --- APP PRINCIPAL ---
def main_app():
    user = st.session_state.current_user
    user_data = st.session_state.db[user]
    
    # Combinar agentes base + agentes del usuario
    active_archetypes = base_archetypes.copy()
    active_archetypes.update(user_data["custom_agents"])

    # --- SIDEBAR: CENTRO DE MANDO PERSONAL ---
    with st.sidebar:
        st.markdown(f"### 👤 Hola, {user.capitalize()}")
        if st.button("Cerrar Sesión"):
            st.session_state.authenticated = False
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        # 1. HISTORIAL DE CHATS (NUEVO!)
        st.subheader("📂 Mis Chats Guardados")
        if not user_data["chats"]:
            st.caption("No hay chats guardados aún.")
        else:
            for chat_title in user_data["chats"]:
                if st.button(f"📄 {chat_title}"):
                    # Cargar chat
                    st.session_state.messages = user_data["chats"][chat_title]
                    st.session_state.simulation_active = False
                    st.success(f"Chat '{chat_title}' cargado.")
                    time.sleep(1)
                    st.rerun()

        st.divider()

        # 2. FÁBRICA DE AGENTES (PERSONAL)
        with st.expander("✨ Crear Nuevo Agente"):
            new_name = st.text_input("Nombre Agente")
            new_desc = st.text_area("Personalidad")
            if st.button("Guardar en mi cuenta"):
                if new_name and new_desc:
                    # Guardar en la DB del usuario
                    st.session_state.db[user]["custom_agents"][new_name] = f"ERES {new_name.upper()}.\nPersonalidad: {new_desc}\nInstrucción: Actúa acorde a este rol."
                    st.success(f"{new_name} guardado en tu perfil.")
                    time.sleep(1)
                    st.rerun()

        # 3. CONFIGURACIÓN
        st.divider()
        scenario = st.selectbox("Escenario:", ["Validación Idea", "Lanzamiento", "Crisis", "Pitch"])
        
        st.subheader("👥 Equipo Activo")
        selected_archetypes = st.multiselect("Expertos:", options=list(active_archetypes.keys()), default=["El Provocador", "El Educador"])

        if st.button("🗑️ Limpiar Pantalla (Nuevo Chat)"):
            st.session_state.messages = []
            st.session_state.simulation_active = False
            st.rerun()

    # --- PANTALLA DE CHAT ---
    st.title(f"🧬 Laboratorio C8: {scenario}")

    # Inicializar mensajes si está vacío
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "simulation_active" not in st.session_state:
        st.session_state.simulation_active = False

    # Input Inicial
    if len(st.session_state.messages) == 0:
        st.info(f"El equipo está listo. Tus agentes personalizados: {len(user_data['custom_agents'])}")
        initial_idea = st.chat_input("Escribe tu idea para iniciar...")
        if initial_idea:
            st.session_state.messages.append({"role": "user", "content": initial_idea, "name": f"{user.capitalize()}"})
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

    # MOTOR DE DEBATE
    if st.session_state.simulation_active:
        if not api_key_configured:
            st.warning("⚠️ Falta API Key en Secrets.")
            st.stop()
            
        st.markdown("---")
        rounds = 3
        for r in range(rounds):
            st.markdown(f"#### 🔄 Ronda {r+1} / {rounds}")
            for agent_name in selected_archetypes:
                with st.chat_message("assistant", avatar="🎭"):
                    with st.spinner(f"{agent_name} analizando..."):
                        persona = active_archetypes[agent_name]
                        prompt = f"Estás interpretando a: {agent_name}\nPERFIL: {persona}\nCONTEXTO: {scenario}, Ronda {r+1}.\nINSTRUCCIÓN: Interactúa, usa teatro (acotaciones), sé breve."
                        
                        msgs = [{"role": "system", "content": prompt}]
                        for m in st.session_state.messages:
                            msgs.append({"role": "user" if m["role"]=="user" else "assistant", "content": f"{m.get('name')}: {m['content']}"})
                        
                        try:
                            client = openai.OpenAI()
                            res = client.chat.completions.create(model="gpt-3.5-turbo", messages=msgs, temperature=0.85, max_tokens=500)
                            reply = res.choices[0].message.content
                            st.markdown(f"**{agent_name}**")
                            st.markdown(reply)
                            st.session_state.messages.append({"role": "assistant", "content": reply, "name": agent_name})
                        except Exception as e:
                            st.error(str(e))
                time.sleep(0.5)
        
        st.session_state.simulation_active = False
        st.rerun()

    # --- BARRA INFERIOR DE ACCIONES ---
    if not st.session_state.simulation_active and len(st.session_state.messages) > 1:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.chat_input("Responder..."):
                pass # El input de arriba captura esto, Streamlit es tricky con doble input, usamos el principal si se limpia
                
        with col2:
            # BOTÓN DE GUARDAR CHAT
            save_name = st.text_input("Nombre para guardar:", placeholder="Ej: Idea Zapatillas")
            if st.button("💾 Guardar Debate"):
                if save_name:
                    st.session_state.db[user]["chats"][save_name] = st.session_state.messages
                    st.success("¡Guardado en tu barra lateral!")
                    time.sleep(1)
                    st.rerun()

        with col3:
            if st.button("📊 Generar Reporte"):
                st.session_state.messages.append({"role": "assistant", "content": "Generando reporte...", "name": "System"})
                # (Aquí iría la lógica del reporte igual que antes)
                st.rerun()
                
    # INPUT PARA CONTINUAR (SI NO ESTÁ ACTIVO EL INPUT DEL COMIENZO)
    if not st.session_state.simulation_active and len(st.session_state.messages) > 0:
        new_msg = st.chat_input("Responde o añade información...")
        if new_msg:
             st.session_state.messages.append({"role": "user", "content": new_msg, "name": f"{user.capitalize()}"})
             st.session_state.simulation_active = True
             st.rerun()

# --- CONTROL DE FLUJO ---
if st.session_state.authenticated:
    main_app()
else:
    login_screen()
