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
    .report-box { background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 5px solid #2196f3; }
</style>
""", unsafe_allow_html=True)

# --- GESTIÓN DE LA API KEY (SECRETA) ---
# Intenta leer la llave de los Secretos de Streamlit. Si no está, la pide manual.
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

# --- DEFINICIÓN DE PERSONALIDADES (ACTUACIÓN) ---
if "c8_archetypes" not in st.session_state:
    st.session_state.c8_archetypes = {
        "El Visionario": """ERES EL VISIONARIO.
        Tono: Inspirador, futurista, elevado.
        Acciones: *Mira al horizonte*, *extiende los brazos*, *susurra con emoción*.
        Enfoque: Propósito, legado y "The Big Picture". Ignora los detalles técnicos.
        Frase típica: "¿Estamos construyendo un negocio o un legado?".""",
        
        "El Provocador": """ERES EL PROVOCADOR.
        Tono: Cínico, agresivo, directo, sin filtros. Odiador de gurús.
        Acciones: *Golpea la mesa*, *se cruza de brazos*, *resopla*, *levanta una ceja con duda*.
        Enfoque: Destruir el humo. Buscar la autenticidad radical.
        Ejemplo: "¿'100% rentable'? ¿En serio? Eso suena a estafa de 2019. Dame realidad.".""",
        
        "El Educador": """ERES EL EDUCADOR.
        Tono: Calmado, analítico, pedagógico, protector del alumno.
        Acciones: *Se ajusta las gafas*, *toma notas en su libreta*, *levanta un dedo para puntualizar*.
        Enfoque: Metodología, claridad y aplicabilidad. ¿Es replicable o es caos?
        Ejemplo: "Espera, bajemos la guardia. Si esto me da el CÓMO exacto, es oro.".""",
        
        "El Curador": """ERES EL CURADOR.
        Tono: Sofisticado, exigente, elitista (en el buen sentido).
        Acciones: *Mira con ojo crítico*, *hace una mueca de disgusto*, *asiente lentamente*.
        Enfoque: Estética, experiencia de usuario (UX), selección premium. Odia la saturación.
        Ejemplo: "Yo busco la Exquisitez Estratégica. ¿Esto me eleva o me hace uno más?".""",
        
        "El Cliente Escéptico": """ERES EL CLIENTE ESCÉPTICO.
        Tono: Desconfiado, impaciente, con miedo a perder dinero.
        Acciones: *Revisa su cartera*, *mira el reloj*, *frunce el ceño*.
        Enfoque: ROI (Retorno), garantías y resultados rápidos."""
    }

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🎛️ Centro C8")
    
    # Check de Llave
    if api_key_configured:
        st.success("🔑 Llave C8 Activada Automáticamente")
    else:
        manual_key = st.text_input("Pega tu API Key (O configúrala en Secrets):", type="password")
        if manual_key:
            openai.api_key = manual_key
            api_key_configured = True
    
    st.divider()
    
    # Configuración
    rounds = st.slider("🔄 Intensidad del Debate (Rondas)", 1, 4, 2)
    
    st.subheader("👥 El Consejo")
    options_list = list(st.session_state.c8_archetypes.keys())
    selected_archetypes = st.multiselect(
        "Expertos en sala:",
        options=options_list,
        default=["El Provocador", "El Educador", "El Curador"]
    )

    # Botón de Historial (Simulado para MVP)
    with st.expander("📂 Historial de Sesiones (Beta)"):
        st.info("Para guardar chats permanentemente, necesitaremos conectar una base de datos en la Fase 3. Por ahora, usa el botón de 'Descargar Reporte' al final.")

    if st.button("🗑️ Nueva Sesión (Borrar)"):
        st.session_state.messages = []
        st.session_state.simulation_active = False
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.title("🧬 C8 Deep Intelligence Lab")

# 1. INPUT
if len(st.session_state.messages) == 0:
    st.info("👋 Los expertos están esperando. ¿Qué idea vamos a someter a juicio hoy?")
    initial_idea = st.chat_input("Escribe tu idea, promesa o copy aquí...")
    if initial_idea:
        st.session_state.messages.append({"role": "user", "content": initial_idea, "name": "Sofia (CEO)"})
        st.session_state.simulation_active = True
        st.rerun()

# 2. CHAT VISUAL
for msg in st.session_state.messages:
    avatar = "👩‍💻" if msg["role"] == "user" else "⚡"
    with st.chat_message(msg["role"], avatar=avatar):
        # Detectar quién habla para poner negrita
        name = msg.get('name', 'AI')
        st.markdown(f"**{name}:**")
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
                
                # INGENIERÍA DE PROMPT (ACTUACIÓN)
                persona = st.session_state.c8_archetypes[agent_name]
                system_prompt = f"""
                {persona}
                
                INSTRUCCIONES DE ACTUACIÓN:
                1. Estás en un debate real. RESPONDE a lo que dijeron los otros agentes antes que tú.
                2. USA ACOTACIONES de teatro entre asteriscos al inicio o mitad de la frase. Ejemplo: *golpea la mesa* o *se ríe irónicamente*.
                3. Mantén tu personalidad al 100%. Si eres el Provocador, sé duro. Si eres el Educador, sé útil.
                4. Sé conciso pero impactante.
                
                HISTORIAL DEL DEBATE:
                """
                
                messages = [{"role": "system", "content": system_prompt}]
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "assistant"
                    messages.append({"role": role, "content": f"{m.get('name')}: {m['content']}"})

                try:
                    client = openai.OpenAI() # Usa la key configurada globalmente
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.8
                    )
                    reply = response.choices[0].message.content
                    
                    message_placeholder.markdown(f"**{agent_name}:**\n{reply}")
                    st.session_state.messages.append({"role": "assistant", "content": reply, "name": agent_name})
                    time.sleep(1.5) # Pausa dramática
                    
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.session_state.simulation_active = False
    st.success("✅ Debate finalizado. Puedes responder o Generar el Reporte.")
    st.rerun()

# 4. OPCIONES FINALES: RESPONDER O REPORTE
if not st.session_state.simulation_active and len(st.session_state.messages) > 1:
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_input = st.chat_input("Responde a los agentes para seguir peleando...")
        if new_input:
            st.session_state.messages.append({"role": "user", "content": new_input, "name": "Sofia (CEO)"})
            st.session_state.simulation_active = True
            st.rerun()
            
    with col2:
        if st.button("📊 GENERAR REPORTE C8"):
            with st.spinner("Analizando debate y generando Insights..."):
                # Prompt especial para el reporte
                report_messages = [{"role": "system", "content": """
                Actúa como el DIRECTOR DE INTELIGENCIA C8.
                Analiza todo el debate anterior y genera un reporte EJECUTIVO.
                Usa EXACTAMENTE este formato:
                
                ### 📊 REPORTE DE INTELIGENCIA C8
                
                **1. ⚠️ El Punto Débil (Lo que hay que ajustar):**
                [Texto aquí]
                
                **2. 🌟 El "Wow" Factor (Lo que enamora):**
                [Texto aquí]
                
                **3. 🚀 La Oportunidad de Expansión:**
                [Texto aquí]
                
                **4. 🏁 Veredicto Final:**
                [Frase contundente de aprobación o rechazo]
                """}]
                
                # Añadir contexto
                chat_text = "\n".join([f"{m['name']}: {m['content']}" for m in st.session_state.messages])
                report_messages.append({"role": "user", "content": f"Analiza este debate:\n{chat_text}"})
                
                client = openai.OpenAI()
                report = client.chat.completions.create(model="gpt-3.5-turbo", messages=report_messages).choices[0].message.content
                
                st.markdown(f"<div class='report-box'>{report}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": report, "name": "C8 INTELLIGENCE"})
