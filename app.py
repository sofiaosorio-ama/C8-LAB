import streamlit as st
import openai
import time
import datetime

# --- CONFIGURACIÓN DE PÁGINA PROFESIONAL ---
st.set_page_config(page_title="C8 Intelligence System", page_icon="🧬", layout="wide")

# --- DISEÑO C8 PRO (CSS) ---
st.markdown("""
<style>
    /* Tipografía y Fondos */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Chat Bubbles Estilizados */
    .stChatMessage {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 15px;
    }
    
    /* Diferenciación Usuario vs IA */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        border-left: 5px solid #2196F3; /* Azul C8 para IA */
    }
    div[data-testid="stChatMessage"]:nth-child(even) {
        border-left: 5px solid #000000; /* Negro para Sofia */
        background-color: #f8f9fa;
    }

    /* Caja de Reporte */
    .report-box {
        background-color: #F0F4F8;
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #D9E2EC;
        margin-top: 20px;
    }
    
    /* Botones */
    .stButton button {
        background-color: #1E293B;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton button:hover {
        background-color: #334155;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- GESTIÓN SILENCIOSA DE API KEY ---
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

# --- PERSONALIDADES C8 (ENTRENADAS CON TU GUIÓN) ---
if "c8_archetypes" not in st.session_state:
    st.session_state.c8_archetypes = {
        "El Provocador": """ERES EL PROVOCADOR.
        Personalidad: Cínico, disruptivo, odia el marketing vacío.
        Estilo de habla: Agresivo pero inteligente. Usa ironía.
        Acciones Teatrales: (Golpea la mesa), (Se ríe sarcásticamente), (Niega con la cabeza).
        Misión: Encontrar el fallo.
        EJEMPLO REAL DE TU TONO:
        "¿'100% rentable'? ¿En serio, Sofía? Empezamos mal. Eso suena a promesa de gurú de 2019. Mi primera bandera roja es esa. Si la IA lo hace todo, ¿dónde queda el alma? Si no me demuestras que esto rompe el molde, para mí es un NO."
        """,
        
        "El Educador": """ERES EL EDUCADOR.
        Personalidad: Calmado, estructurado, protector del alumno.
        Estilo de habla: Pedagógico, usa analogías, busca el 'CÓMO'.
        Acciones Teatrales: (Se ajusta las gafas), (Toma notas), (Levanta la mano pidiendo calma).
        Misión: Asegurar que sea enseñable y replicable.
        EJEMPLO REAL DE TU TONO:
        "Espera, Provocador, baja la guardia. Yo veo algo interesante aquí. Si este programa me da el cómo exacto... es decir, si me da la Toolbox C8 ya integrada, eso es oro. Mi duda es: ¿Es replicable? ¿O solo le funciona a Sofía?"
        """,
        
        "El Curador": """ERES EL CURADOR.
        Personalidad: Sofisticado, exigente, elitista.
        Estilo de habla: Culto, crítico con la estética y la experiencia.
        Acciones Teatrales: (Mira con ojo crítico), (Hace una mueca), (Analiza el diseño).
        Misión: Filtrar la saturación. Buscar la "Exquisitez Estratégica".
        EJEMPLO REAL DE TU TONO:
        "Coincido con el Educador, pero me preocupa la saturación. Lo que yo compraría de Sofía no es 'todas las herramientas', sino SU selección. Si me da una lista de 50 apps, me aburro."
        """,
        
        "El Visionario": """ERES EL VISIONARIO.
        Personalidad: Inspirador, futurista, magnético.
        Estilo de habla: Elevado, habla de legado y transformación global.
        Acciones Teatrales: (Mira al horizonte), (Extiende los brazos), (Sonríe con certeza).
        Misión: Conectar la idea con el propósito mayor.
        """
    }

# --- SIDEBAR PROFESIONAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=60)
    st.markdown("### C8 INTELLIGENCE™")
    st.caption("v4.0 | System Online")
    
    st.divider()
    
    # 1. SELECTOR DE SITUACIÓN
    st.subheader("📍 Situación Estratégica")
    scenario = st.selectbox(
        "¿Qué estamos simulando hoy?",
        ["Validación de Idea Nueva", "Lanzamiento de Marca Oficial", "Pitch de Venta (High Ticket)", "Práctica de Speech", "Gestión de Crisis"]
    )
    
    # 2. EL CONSEJO
    st.subheader("👥 Consejo Asesor")
    selected_archetypes = st.multiselect(
        "Expertos Activos:",
        options=list(st.session_state.c8_archetypes.keys()),
        default=["El Provocador", "El Educador"]
    )
    
    st.divider()
    
    # 3. ESTADO DEL SISTEMA (Simulado Visualmente)
    st.markdown("bla**System Status**")
    if api_key_configured:
        st.success("🟢 OpenAI Neural Link: Active")
    else:
        st.error("🔴 OpenAI Key: Missing")
        manual_key = st.text_input("Ingreso Manual de Llave:", type="password")
        if manual_key:
            openai.api_key = manual_key
            api_key_configured = True
            
    st.info("🟢 Database C8: Ready (Local)")

    if st.button("🗑️ Resetear Simulación"):
        st.session_state.messages = []
        st.session_state.simulation_active = False
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.title(f"🧬 Laboratorio C8: {scenario}")
st.markdown("**Objetivo:** Simulación de debate profundo con interacción humana y metodología C8.")

# 1. INPUT INICIAL
if len(st.session_state.messages) == 0:
    st.info(f"👋 Bienvenida, Arquitecta. El Consejo está listo para simular un escenario de **{scenario}**.")
    initial_idea = st.chat_input("Ingresa los parámetros de tu idea o copy...")
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

# 3. MOTOR DE SIMULACIÓN HUMANA (V4.0)
if st.session_state.simulation_active:
    if not api_key_configured:
        st.warning("⚠️ Sistema en pausa: Requiere Llave de Acceso.")
        st.stop()

    st.markdown("---")
    
    # RONDAS FIJAS: 3 (Profundidad Garantizada)
    rounds_fixed = 3
    
    for r in range(rounds_fixed):
        # Header de Ronda elegante
        st.markdown(f"#### 🔄 Ronda de Debate {r + 1} / {rounds_fixed}")
        
        for agent_name in selected_archetypes:
            with st.chat_message("assistant", avatar="🎭"):
                message_placeholder = st.empty()
                
                # RECUPERAR MEMORIA Y PERSONALIDAD
                persona = st.session_state.c8_archetypes[agent_name]
                
                # --- PROMPT MAESTRO V4.0 (INTERACCIÓN HUMANA) ---
                system_prompt = f"""
                Estás interpretando a: {agent_name}
                
                TU PERFIL PSICOLÓGICO:
                {persona}
                
                CONTEXTO ACTUAL:
                - Escenario: {scenario}
                - Ronda actual: {r + 1} de {rounds_fixed}
                
                INSTRUCCIONES DE INTERACCIÓN (CRUCIAL):
                1. NO seas un robot. Eres un humano experto en una mesa redonda.
                2. USA TUS ACOTACIONES: (Golpea la mesa), (Suspira), (Se ríe).
                3. INTERACTÚA: Menciona a los otros agentes por su nombre ("Como dice el Educador...", "Provocador, estás equivocado...").
                4. SI ESTÁS EN RONDA 2 o 3: Profundiza. Haz preguntas difíciles a Sofía o desafía a los otros agentes.
                5. MODULA TU TONO: Si es "Lanzamiento", sé urgente. Si es "Validación", sé crítico.
                
                HISTORIAL DE LA SALA:
                """
                
                messages = [{"role": "system", "content": system_prompt}]
                # Inyectamos todo el historial
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "assistant"
                    messages.append({"role": role, "content": f"{m.get('name')}: {m['content']}"})

                # LLAMADA AL CEREBRO
                try:
                    client = openai.OpenAI() 
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.85, # Alta creatividad para más humanidad
                        max_tokens=500
                    )
                    reply = response.choices[0].message.content
                    
                    # Escritura directa
                    message_placeholder.markdown(f"**{agent_name}**\n\n{reply}")
                    st.session_state.messages.append({"role": "assistant", "content": reply, "name": agent_name})
                    time.sleep(1.5) # Ritmo de conversación natural
                    
                except Exception as e:
                    st.error(f"Error en el sistema: {e}")
    
    st.session_state.simulation_active = False
    st.success("✅ Debate finalizado. El Consejo espera tu respuesta.")
    st.rerun()

# 4. ACCIONES FINALES
if not st.session_state.simulation_active and len(st.session_state.messages) > 1:
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_input = st.chat_input("Responde al Consejo o aporta nuevos datos...")
        if new_input:
            st.session_state.messages.append({"role": "user", "content": new_input, "name": "Sofia (CEO)"})
            st.session_state.simulation_active = True
            st.rerun()
            
    with col2:
        if st.button("📊 Generar Reporte C8"):
            with st.spinner("Procesando Inteligencia..."):
                report_messages = [{"role": "system", "content": """
                Actúa como el DIRECTOR DE INTELIGENCIA C8.
                Analiza el debate y genera un reporte EJECUTIVO FINAL.
                Formato Markdown limpio:
                
                ### 📊 REPORTE DE INTELIGENCIA C8
                
                **1. ⚠️ Puntos de Fricción (Weakness):**
                
                **2. 🌟 Factor C8 (Strength/Wow):**
                
                **3. 🚀 Oportunidades de Escala:**
                
                **4. 🏁 Veredicto Final:**
                """}]
                
                chat_text = "\n".join([f"{m.get('name')}: {m['content']}" for m in st.session_state.messages])
                report_messages.append({"role": "user", "content": f"Analiza:\n{chat_text}"})
                
                client = openai.OpenAI()
                report = client.chat.completions.create(model="gpt-3.5-turbo", messages=report_messages).choices[0].message.content
                
                st.session_state.messages.append({"role": "assistant", "content": report, "name": "C8 INTELLIGENCE"})
                st.rerun()
