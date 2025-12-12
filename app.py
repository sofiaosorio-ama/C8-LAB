import streamlit as st
import openai
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="C8 Synth-Lab 3.0", page_icon="🧬", layout="wide")

# --- ESTILOS VISUALES (C8 BRANDING) ---
st.markdown("""
<style>
    .stChatMessage { border-radius: 12px; padding: 15px; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .user-message { background-color: #f0f2f6; }
    h1 { color: #1E293B; font-family: 'Helvetica', sans-serif; font-weight: 700; }
    .report-box { background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 5px solid #2196f3; font-family: sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- GESTIÓN DE LA API KEY (SECRETA) ---
# Intenta leer la llave de los Secretos de Streamlit.
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

# --- PERSONALIDADES C8 EXTREMAS (Tus Prompts Exactos) ---
if "c8_archetypes" not in st.session_state:
    st.session_state.c8_archetypes = {
        "El Provocador": """ERES EL PROVOCADOR.
        ACTITUD: Entras golpeando la mesa. Eres cínico, directo, odias el humo.
        FRASES: "¿En serio, Sofía?", "Bandera roja", "Cállate y toma mi dinero".
        MISIÓN: Destruir promesas vacías tipo "100% rentable". Exigir alma y diferenciación radical.
        EJEMPLO DE TONO: "¿'100% rentable'? Eso suena a gurú de 2019. Si no me demuestras que esto rompe el molde, es un NO." """,
        
        "El Educador": """ERES EL EDUCADOR.
        ACTITUD: Te ajustas las gafas, intervienes con calma pero firmeza.
        FRASES: "Baja la guardia", "Mi dolor de cabeza es...", "¿Es replicable?".
        MISIÓN: Buscar la metodología, el paso a paso, la Toolbox C8. Quieres saber si puedes enseñar esto a tus propios clientes (licencia).
        EJEMPLO DE TONO: "Si me da la Toolbox C8 ya integrada con los prompts, eso es oro. Pero, ¿es pedagógico o un caos?" """,
        
        "El Curador": """ERES EL CURADOR.
        ACTITUD: Miras con ojo crítico, buscas exquisitez.
        FRASES: "Me preocupa la saturación", "Exquisitez Estratégica", "¿Me eleva el estatus?".
        MISIÓN: Filtrar la basura. No quieres 50 apps, quieres LA selección de Sofía. Valoras la estética y la integración Branding + Negocio.
        EJEMPLO DE TONO: "Si me da una lista de 50 apps, me aburro. Yo compro la selección de Sofía." """,
        
        "El Visionario": """ERES EL VISIONARIO.
        ACTITUD: Miras el horizonte, hablas de legado y futuro.
        MISIÓN: Conectar la idea con el propósito global. ¿Esto cambia el mundo o es solo ruido?"""
    }

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=50)
    st.title("🎛️ Centro C8")
    
    # Check de Llave
    if api_key_configured:
        st.success("🔑 Llave C8 Activada (Modo Seguro)")
    else:
        st.warning("⚠️ No se detectó llave en Secrets.")
        manual_key = st.text_input("Pega tu API Key manual:", type="password")
        if manual_key:
            openai.api_key = manual_key
            api_key_configured = True
    
    st.divider()
    
    # Configuración
    rounds = st.slider("🔄 Intensidad (Rondas de Debate)", 1, 4, 2)
    
    st.subheader("👥 El Consejo")
    options_list = list(st.session_state.c8_archetypes.keys())
    selected_archetypes = st.multiselect(
        "Expertos en sala:",
        options=options_list,
        default=["El Provocador", "El Educador", "El Curador"]
    )
    
    st.info("💡 Nota: Para guardar el historial en una base de datos externa, configuraremos Google Sheets en la siguiente fase.")

    if st.button("🗑️ Reiniciar Universo"):
        st.session_state.messages = []
        st.session_state.simulation_active = False
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.title("🧬 C8 Deep Intelligence Lab")

# 1. INPUT
if len(st.session_state.messages) == 0:
    st.info("👋 Bienvenida, Arquitecta. El Consejo está reunido.")
    initial_idea = st.chat_input("Escribe tu idea para iniciar el juicio...")
    if initial_idea:
        st.session_state.messages.append({"role": "user", "content": initial_idea, "name": "Sofia (CEO)"})
        st.session_state.simulation_active = True
        st.rerun()

# 2. CHAT VISUAL
for msg in st.session_state.messages:
    avatar = "👩‍💻" if msg["role"] == "user" else "⚡"
    if msg.get("name") == "C8 INTELLIGENCE": avatar = "📊"
    
    with st.chat_message(msg["role"], avatar=avatar):
        # Detectar quién habla para poner negrita
        name = msg.get('name', 'AI')
        st.markdown(f"**{name}:**")
        if name == "C8 INTELLIGENCE":
             st.markdown(f"<div class='report-box'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
             st.markdown(msg["content"])

# 3. MOTOR DE ACTUACIÓN (LOOP)
if st.session_state.simulation_active:
    if not api_key_configured:
        st.error("⚠️ Falta la API Key.")
        st.stop()

    st.divider()
    
    # Bucle de Rondas
    for r in range(rounds):
        st.caption(f"🔥 DEBATE: RONDA {r + 1} DE {rounds}")
        
        for agent_name in selected_archetypes:
            with st.chat_message("assistant", avatar="🎭"):
                message_placeholder = st.empty()
                
                # INGENIERÍA DE PROMPT (ACTUACIÓN EXTREMA)
                persona = st.session_state.c8_archetypes[agent_name]
                system_prompt = f"""
                {persona}
                
                INSTRUCCIONES DE ACTUACIÓN:
                1. Estás en un debate real. LEE lo que dijeron los otros y responde, ataca o apoya.
                2. USA ACOTACIONES TEATRALES entre paréntesis al inicio. Ej: (Golpea la mesa), (Se ajusta las gafas).
                3. Mantén tu personalidad C8 al 100%. Sé radical.
                4. NO seas complaciente. Si la idea es mala, dilo.
                
                HISTORIAL DEL DEBATE:
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
                        temperature=0.8
                    )
                    reply = response.choices[0].message.content
                    
                    message_placeholder.markdown(f"**{agent_name}:**\n{reply}")
                    st.session_state.messages.append({"role": "assistant", "content": reply, "name": agent_name})
                    time.sleep(1) # Pausa dramática
                    
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.session_state.simulation_active = False
    st.success("✅ Debate finalizado.")
    st.rerun()

# 4. OPCIONES FINALES
if not st.session_state.simulation_active and len(st.session_state.messages) > 1:
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_input = st.chat_input("Responde a los agentes para seguir peleando...")
        if new_input:
            st.session_state.messages.append({"role": "user", "content": new_input, "name": "Sofia (CEO)"})
            st.session_state.simulation_active = True
            st.rerun()
            
    with col2:
        # BOTÓN GENERADOR DE REPORTE C8
        if st.button("📊 GENERAR REPORTE C8"):
            with st.spinner("El Director de Inteligencia está analizando..."):
                report_messages = [{"role": "system", "content": """
                Actúa como el DIRECTOR DE INTELIGENCIA C8.
                Analiza todo el debate anterior y genera un reporte EJECUTIVO.
                Usa EXACTAMENTE este formato con iconos y negritas:
                
                ### 📊 REPORTE DE INTELIGENCIA C8
                
                **1. ⚠️ El Punto Débil (Lo que hay que ajustar):**
                [Texto aquí]
                
                **2. 🌟 El "Wow" Factor (Lo que enamora):**
                [Texto aquí]
                
                **3. 🚀 La Oportunidad de Expansión:**
                [Texto aquí]
                
                **4. 🏁 Veredicto Final:**
                [Frase contundente]
                """}]
                
                chat_text = "\n".join([f"{m.get('name')}: {m['content']}" for m in st.session_state.messages])
                report_messages.append({"role": "user", "content": f"Analiza este debate:\n{chat_text}"})
                
                client = openai.OpenAI()
                report = client.chat.completions.create(model="gpt-3.5-turbo", messages=report_messages).choices[0].message.content
                
                st.session_state.messages.append({"role": "assistant", "content": report, "name": "C8 INTELLIGENCE"})
                st.rerun()
