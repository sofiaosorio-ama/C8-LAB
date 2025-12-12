import streamlit as st
import openai
import time

# --- CONFIGURACIÓN DE PÁGINA PROFESIONAL ---
st.set_page_config(page_title="C8 Intelligence System", page_icon="🧬", layout="wide")

# --- DISEÑO C8 PRO (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .stChatMessage {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 15px;
    }
    div[data-testid="stChatMessage"]:nth-child(odd) { border-left: 5px solid #2196F3; }
    div[data-testid="stChatMessage"]:nth-child(even) { border-left: 5px solid #000000; background-color: #f8f9fa; }
    
    .report-box {
        background-color: #F0F4F8; padding: 25px; border-radius: 10px; border: 1px solid #D9E2EC; margin-top: 20px;
    }
    .stButton button {
        background-color: #1E293B; color: white; border-radius: 8px; font-weight: 600; width: 100%;
    }
    .stButton button:hover { background-color: #334155; color: white; }
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

# --- MEMORIA DEL SISTEMA ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "simulation_active" not in st.session_state:
    st.session_state.simulation_active = False

# --- INICIALIZACIÓN DE ARQUETIPOS (BASE + PERSONALIZADOS) ---
if "c8_archetypes" not in st.session_state:
    st.session_state.c8_archetypes = {
        "El Provocador": """ERES EL PROVOCADOR.
        Personalidad: Cínico, disruptivo, odia el marketing vacío.
        Acciones: (Golpea la mesa), (Se ríe sarcásticamente), (Niega con la cabeza).
        Misión: Encontrar el fallo. Tono agresivo pero inteligente.""",
        
        "El Educador": """ERES EL EDUCADOR.
        Personalidad: Calmado, estructurado, protector del alumno.
        Acciones: (Se ajusta las gafas), (Toma notas), (Levanta la mano pidiendo calma).
        Misión: Asegurar que sea enseñable y replicable. Busca el 'CÓMO'.""",
        
        "El Curador": """ERES EL CURADOR.
        Personalidad: Sofisticado, exigente, elitista.
        Acciones: (Mira con ojo crítico), (Hace una mueca), (Analiza el diseño).
        Misión: Filtrar la saturación. Buscar la 'Exquisitez Estratégica'.""",
        
        "El Visionario": """ERES EL VISIONARIO.
        Personalidad: Inspirador, futurista, magnético.
        Acciones: (Mira al horizonte), (Extiende los brazos), (Sonríe con certeza).
        Misión: Conectar la idea con el propósito mayor y el legado."""
    }

# --- SIDEBAR: CENTRO DE MANDO ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=60)
    st.markdown("### C8 INTELLIGENCE™")
    
    if not api_key_configured:
        st.warning("⚠️ Sistema Desconectado")
        manual_key = st.text_input("Ingresa API Key:", type="password")
        if manual_key:
            openai.api_key = manual_key
            api_key_configured = True
    
    st.divider()
    
    # 1. SELECTOR DE ESCENARIO
    st.subheader("📍 Escenario")
    scenario = st.selectbox(
        "Contexto de la Simulación:",
        ["Validación de Idea Nueva", "Lanzamiento Oficial", "Pitch de Venta", "Gestión de Crisis", "Rebranding"]
    )
    
    st.divider()

    # 2. FÁBRICA DE ARQUETIPOS (¡AQUÍ ESTÁ LA MAGIA!)
    with st.expander("✨ FÁBRICA DE AGENTES C8", expanded=True):
        st.caption("Crea un nuevo experto para tu consejo.")
        new_name = st.text_input("Nombre del Rol (Ej: Inversor)")
        new_desc = st.text_area("Personalidad y Actitud (Ej: Agresivo, solo le importa el dinero)")
        
        if st.button("💾 Crear Agente"):
            if new_name and new_desc:
                # Guardamos en la memoria viva
                st.session_state.c8_archetypes[new_name] = f"ERES {new_name.upper()}.\nPersonalidad: {new_desc}\nInstrucción: Actúa acorde a este rol exagerando tus rasgos."
                st.success(f"¡{new_name} se ha unido al equipo!")
                time.sleep(1)
                st.rerun()

    # 3. SELECTOR DE EQUIPO (Ahora incluye los nuevos)
    st.subheader("👥 Consejo Activo")
    options_list = list(st.session_state.c8_archetypes.keys()) # Lista dinámica
    
    selected_archetypes = st.multiselect(
        "Selecciona quién entra a la sala:",
        options=options_list,
        default=["El Provocador", "El Educador"]
    )
    
    st.divider()
    if st.button("🗑️ Nueva Sesión"):
        st.session_state.messages = []
        st.session_state.simulation_active = False
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.title(f"🧬 Laboratorio C8: {scenario}")

# 1. INPUT INICIAL
if len(st.session_state.messages) == 0:
    st.info(f"👋 Bienvenida, Arquitecta. Configura tu equipo a la izquierda y lanza el tema.")
    initial_idea = st.chat_input("Escribe tu idea, promesa o copy aquí...")
    if initial_idea:
        st.session_state.messages.append({"role": "user", "content": initial_idea, "name": "Sofia (CEO)"})
        st.session_state.simulation_active = True
        st.rerun()

# 2. VISUALIZACIÓN DEL CHAT
for msg in st.session_state.messages:
    avatar = "👩‍💻" if msg["role"] == "user" else "⚡"
    if msg.get("name") == "C8 INTELLIGENCE": avatar = "📊"
    
    with st.chat_message(msg["role"], avatar=avatar):
        name = msg.get('name', 'AI')
        st.markdown(f"**{name}**")
        if name == "C8 INTELLIGENCE":
             st.markdown(f"<div class='report-box'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
             st.markdown(msg["content"])

# 3. MOTOR DE SIMULACIÓN HUMANA (V5.0)
if st.session_state.simulation_active:
    if not api_key_configured:
        st.warning("⚠️ Falta API Key.")
        st.stop()

    st.markdown("---")
    
    # RONDAS FIJAS: 3
    rounds_fixed = 3
    
    for r in range(rounds_fixed):
        st.markdown(f"#### 🔄 Ronda {r + 1} / {rounds_fixed}")
        
        for agent_name in selected_archetypes:
            with st.chat_message("assistant", avatar="🎭"):
                message_placeholder = st.empty()
                
                # CEREBRO DINÁMICO: Funciona con los PREDEFINIDOS y los NUEVOS
                persona = st.session_state.c8_archetypes[agent_name]
                
                system_prompt = f"""
                Estás interpretando a: {agent_name}
                
                TU PERFIL:
                {persona}
                
                CONTEXTO:
                - Escenario: {scenario}
                - Ronda: {r + 1} de {rounds_fixed}
                
                INSTRUCCIONES DE ACTUACIÓN REALISTA:
                1. INTERACTÚA: Menciona a los otros agentes por nombre. Discute con ellos.
                2. TEATRO: Usa acotaciones entre paréntesis. Ej: (Se levanta), (Golpea la mesa).
                3. PROFUNDIDAD: Haz preguntas difíciles a Sofía. No seas complaciente.
                4. TONO: Usa el tono descrito en tu perfil. Si eres el Provocador, sé agresivo.
                
                HISTORIAL:
                """
                
                messages = [{"role": "system", "content": system_prompt}]
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "assistant"
                    messages.append({"role": role, "content": f"{m.get('name')}: {m['content']}"})

                try:
                    client = openai.OpenAI() 
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.85, 
                        max_tokens=550
                    )
                    reply = response.choices[0].message.content
                    
                    message_placeholder.markdown(f"**{agent_name}**\n\n{reply}")
                    st.session_state.messages.append({"role": "assistant", "content": reply, "name": agent_name})
                    time.sleep(1) 
                    
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.session_state.simulation_active = False
    st.success("✅ Debate finalizado.")
    st.rerun()

# 4. ACCIONES FINALES
if not st.session_state.simulation_active and len(st.session_state.messages) > 1:
    col1, col2 = st.columns([3, 1])
    with col1:
        new_input = st.chat_input("Responde al Consejo...")
        if new_input:
            st.session_state.messages.append({"role": "user", "content": new_input, "name": "Sofia (CEO)"})
            st.session_state.simulation_active = True
            st.rerun()
    with col2:
        if st.button("📊 Reporte C8"):
            with st.spinner("Generando Insights..."):
                report_messages = [{"role": "system", "content": """
                Actúa como el DIRECTOR DE INTELIGENCIA C8.
                Genera un reporte EJECUTIVO FINAL.
                Formato Markdown:
                ### 📊 REPORTE DE INTELIGENCIA C8
                **1. ⚠️ Puntos de Fricción:**
                **2. 🌟 Factor C8 (Strength):**
                **3. 🚀 Oportunidades:**
                **4. 🏁 Veredicto:**
                """}]
                chat_text = "\n".join([f"{m.get('name')}: {m['content']}" for m in st.session_state.messages])
                report_messages.append({"role": "user", "content": f"Analiza:\n{chat_text}"})
                client = openai.OpenAI()
                report = client.chat.completions.create(model="gpt-3.5-turbo", messages=report_messages).choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": report, "name": "C8 INTELLIGENCE"})
                st.rerun()
