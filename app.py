import streamlit as st
import openai
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="C8 Intelligence System", page_icon="🧬", layout="wide")

# --- ESTILOS VISUALES LIMPIOS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .stChatMessage { background-color: #ffffff !important; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 10px; color: #0f172a !important; }
    .stChatMessage p, .stChatMessage li { color: #334155 !important; font-size: 16px; line-height: 1.6; }
    
    div[data-testid="stChatMessage"]:nth-child(odd) { border-left: 5px solid #2563eb; } /* IA */
    div[data-testid="stChatMessage"]:nth-child(even) { border-left: 5px solid #000000; background-color: #f8fafc !important; } /* Humano */
    
    .status-badge { background-color: #dcfce7; color: #166534; padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; border: 1px solid #bbf7d0; }
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
    except:
        return None

# --- FUNCIÓN DE AUTOGUARDADO (SILENCIOSA) ---
def autosave_chat(user, messages):
    sheet = connect_to_gsheets()
    if sheet and len(messages) > 1:
        try:
            ws_chats = sheet.worksheet("Chats")
            # Si es el primer mensaje, creamos título automático
            first_user_msg = next((m["content"] for m in messages if m["role"] == "user"), "Sin Título")
            chat_title = f"{first_user_msg[:30]}... ({datetime.now().strftime('%d/%m %H:%M')})"
            
            # Preparamos filas
            rows = []
            now = str(datetime.now())
            for m in messages:
                # Evitamos guardar duplicados simples chequeando lógica básica o simplemente guardamos el lote
                rows.append([chat_title, now, m["role"], m["name"], m["content"], user])
            
            # Guardamos todo el lote al final
            ws_chats.append_rows(rows)
            return True
        except:
            return False
    return False

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

# --- LOGIN ---
def login_screen():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=80)
        st.markdown("<h2 style='text-align: center;'>C8 Intelligence Hub</h2>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Ingresar", "Registrar Nuevo"])
        with tab1:
            u = st.text_input("Usuario", key="l_u")
            p = st.text_input("Contraseña", type="password", key="l_p")
            if st.button("Acceder"):
                sheet = connect_to_gsheets()
                if sheet:
                    try:
                        users = sheet.worksheet("Usuarios").get_all_records()
                        for user in users:
                            if str(user["Usuario"]) == u and str(user["Password"]) == p:
                                st.session_state.authenticated = True
                                st.session_state.current_user = u
                                st.rerun()
                        st.error("Acceso denegado")
                    except: st.error("Error DB")
        with tab2:
            nu = st.text_input("Nuevo Usuario")
            np = st.text_input("Nueva Contraseña", type="password")
            nn = st.text_input("Nombre")
            if st.button("Crear Cuenta"):
                sheet = connect_to_gsheets()
                if sheet:
                    try:
                        sheet.worksheet("Usuarios").append_row([nu, np, nn, str(datetime.now())])
                        st.success("Creado. Inicia sesión.")
                    except: st.error("Error creando.")

# --- APP PRINCIPAL ---
def main_app():
    user = st.session_state.current_user
    
    # Arquetipos Base (Prompting Agresivo)
    active_archetypes = {
        "El Provocador": "ERES EL PROVOCADOR. Tono: Sarcástico, duro. Misión: Buscar el fallo financiero o lógico. PREGUNTA: ¿Dónde está la plata? ¿Por qué alguien pagaría?",
        "El Educador": "ERES EL EDUCADOR. Tono: Analítico. Misión: Buscar la estructura. PREGUNTA: ¿Cuál es el paso 1, 2 y 3? ¿Es confuso?",
        "El Curador": "ERES EL CURADOR. Tono: Exigente. Misión: Buscar la calidad. PREGUNTA: ¿Es visualmente horrible? ¿Se siente barato?",
        "La Gen-Z": "ERES LA GEN-Z. Tono: Viral, rápido, slang. Misión: Buscar el 'cringe'. PREGUNTA: ¿Esto es aburrido? ¿Es instagrameable?"
    }
    
    # Cargar personalizados
    sheet = connect_to_gsheets()
    if sheet:
        try:
            for r in sheet.worksheet("Agentes").get_all_records():
                active_archetypes[r["Nombre"]] = r["Personalidad"]
        except: pass

    # SIDEBAR
    with st.sidebar:
        st.markdown(f"**👤 {user.upper()}**")
        if st.button("Salir"):
            st.session_state.authenticated = False
            st.rerun()
        st.divider()
        
        # Historial (Solo lectura rápida)
        st.caption("📂 Historial Nube")
        if sheet:
            try:
                titles = list(set(sheet.worksheet("Chats").col_values(1)[1:]))
                sel = st.selectbox("Cargar anterior:", ["-"] + titles)
                if sel != "-" and st.button("Ver"):
                    rows = [r for r in sheet.worksheet("Chats").get_all_records() if r["Titulo"] == sel]
                    st.session_state.messages = [{"role": r["Role"], "name": r["Name"], "content": r["Content"]} for r in rows]
                    st.rerun()
            except: pass
        
        st.divider()
        with st.expander("✨ Nuevo Agente"):
            an = st.text_input("Nombre")
            ad = st.text_input("Personalidad")
            if st.button("Guardar Agente") and sheet:
                sheet.worksheet("Agentes").append_row([an, ad, user, str(datetime.now())])
                st.success("Guardado")
        
        st.divider()
        scenario = st.selectbox("Situación:", ["Validación Idea", "Lanzamiento", "Crisis", "Pitch"])
        team = st.multiselect("Consejo:", list(active_archetypes.keys()), default=["El Provocador", "El Educador"])
        if st.button("🗑️ Nuevo Chat"):
            st.session_state.messages = []
            st.rerun()

    # CHAT AREA
    st.title(f"🧬 C8 Lab: {scenario}")

    if not st.session_state.messages:
        st.info("💡 Consejo: Sé específica. El equipo será duro contigo.")
        idea = st.chat_input("Lanza tu idea...")
        if idea:
            st.session_state.messages.append({"role": "user", "content": idea, "name": user})
            st.session_state.simulation_active = True
            st.rerun()

    for m in st.session_state.messages:
        av = "👩‍💻" if m["role"] == "user" else "⚡"
        with st.chat_message(m["role"], avatar=av):
            st.markdown(f"**{m['name']}**")
            st.markdown(m["content"])

    # LOGICA DE SIMULACIÓN AUTOMÁTICA
    if st.session_state.simulation_active:
        st.markdown("---")
        
        rounds = 3
        for r in range(rounds):
            st.caption(f"🔥 Ronda de Fuego {r+1}/{rounds}")
            for agent in team:
                with st.chat_message("assistant", avatar="🎭"):
                    with st.spinner(f"{agent} analizando..."):
                        
                        # PROMPT ANTI-REPETICIÓN Y PREGUNTAS CLAVE
                        prompt = f"""
                        ERES: {agent}
                        PERFIL: {active_archetypes[agent]}
                        CONTEXTO: {scenario}, Ronda {r+1} de 3.
                        
                        TU OBJETIVO AHORA MISMO:
                        1. NO repitas tu introducción. Ve al grano.
                        2. Si es Ronda 1: Da tu opinión brutal inicial.
                        3. Si es Ronda 2 o 3: ATACA lo que dijeron los otros o CUESTIONA a Sofía.
                        4. TERMINA TU MENSAJE CON UNA PREGUNTA DIRECTA (ej: "¿Cómo piensas escalar X?", "¿Dónde está la prueba de Y?").
                        5. Sé breve (máximo 3 párrafos).
                        """
                        
                        hist = [{"role": "system", "content": prompt}]
                        for m in st.session_state.messages:
                            hist.append({"role": "user" if m["role"]=="user" else "assistant", "content": f"{m['name']}: {m['content']}"})
                        
                        try:
                            # frequency_penalty=0.5 EVITA QUE REPITAN FRASES
                            res = openai.chat.completions.create(
                                model="gpt-3.5-turbo", 
                                messages=hist, 
                                temperature=0.9, 
                                frequency_penalty=0.5
                            )
                            reply = res.choices[0].message.content
                            
                            st.markdown(f"**{agent}**")
                            st.markdown(reply)
                            st.session_state.messages.append({"role": "assistant", "content": reply, "name": agent})
                        except Exception as e:
                            st.error(str(e))
                time.sleep(0.5)
        
        # AUTOGUARDADO AL FINALIZAR
        with st.spinner("☁️ Autoguardando en Google Sheets..."):
            autosave_chat(user, st.session_state.messages)
        st.toast("✅ Debate guardado en la nube automáticamente.", icon="☁️")
        
        st.session_state.simulation_active = False
        st.rerun()

    # INPUT PARA CONTINUAR
    if not st.session_state.simulation_active and st.session_state.messages:
        new_idea = st.chat_input("Responde a sus preguntas...")
        if new_idea:
            st.session_state.messages.append({"role": "user", "content": new_idea, "name": user})
            st.session_state.simulation_active = True
            st.rerun()

if st.session_state.authenticated:
    main_app()
else:
    login_screen()
