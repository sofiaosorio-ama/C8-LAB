import streamlit as st
import openai
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="C8 Synth-Lab 2.0", page_icon="🧬", layout="wide")

# --- ESTILOS VISUALES (C8 BRANDING) ---
st.markdown("""
<style>
    .stChatMessage { border-radius: 10px; padding: 15px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .user-message { background-color: #f0f2f6; }
    h1 { color: #1E293B; font-family: 'Helvetica', sans-serif; }
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
    .reportview-container .main .block-container { max-width: 1000px; }
</style>
""", unsafe_allow_html=True)

# --- 1. MEMORIA DEL SISTEMA ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "simulation_active" not in st.session_state:
    st.session_state.simulation_active = False

# ARQUETIPOS EN MEMORIA
if "c8_archetypes" not in st.session_state:
    st.session_state.c8_archetypes = {
        "El Visionario": "Eres un estratega soñador. Tu foco: Expansión, Propósito y Futuro. No te preocupan los detalles técnicos, sino la GRAN visión. Usas metáforas inspiradoras.",
        "El Provocador": "Eres disruptivo, directo y un poco cínico. Odias los clichés de marketing. Tu trabajo es encontrar el punto débil, lo aburrido o lo falso de la idea. Retas al usuario.",
        "El Educador": "Eres metódico y estructurado. Te obsesiona la claridad, el paso a paso y la pedagogía. Preguntas: ¿Es accionable? ¿Se entiende? ¿Cuál es la metodología?",
        "El Curador": "Eres un esteta perfeccionista. Buscas la excelencia visual, la experiencia de usuario premium y la diferenciación por calidad. Odias lo 'barato' o genérico.",
        "El Estratega de Negocio": "Eres frío y calculador. Solo te importa el ROI, el Margen, la Escalabilidad y el Modelo de Negocio. Si no da dinero, no sirve."
    }

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1048/1048927.png", width=50)
    st.title("🎛️ Centro de Mando C8")
    
    # API Key
    api_key = st.text_input("Tu OpenAI API Key", type="password")
    if api_key:
        openai.api_key = api_key
    
    st.divider()

    # --- CONFIGURACIÓN DE LA SALA ---
    st.subheader("📍 Configuración del Escenario")
    
    scenario = st.selectbox(
        "¿Cuál es la situación actual?",
        ["Validación de Idea Nueva", "Preparación de Lanzamiento", "Rebranding / Cambio de Imagen", "Crisis de Reputación", "Escalado de Negocio", "Creación de Contenido"]
    )
    
    rounds = st.slider("🔄 Rondas de Debate (Profundidad)", min_value=1, max_value=5, value=2, help="Cuántas veces hablará cada agente.")

    st.divider()

    # --- EQUIPO ---
    st.subheader("👥 El Consejo C8")
    options_list = list(st.session_state.c8_archetypes.keys())
    selected_archetypes = st.multiselect(
        "Selecciona a los expertos:",
        options=options_list,
        default=["El Visionario", "El Provocador", "El Estratega de Negocio"]
    )

    # CREAR NUEVO
    with st.expander("✨ + Añadir Nuevo Experto"):
        new_name = st.text_input("Nombre del Rol")
        new_desc = st.text_area("Personalidad / Enfoque")
        if st.button("Guardar Experto"):
            if new_name and new_desc:
                st.session_state.c8_archetypes[new_name] = new_desc
                st.success(f"¡{new_name} añadido!")
                time.sleep(1)
                st.rerun()

    if st.button("🗑️ Reiniciar Sesión"):
        st.session_state.messages = []
        st.session_state.simulation_active = False
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.title("🧬 C8 Deep Intelligence Lab")
st.markdown(f"**Escenario Activo:** `{scenario}` | **Modo:** `Debate Multidireccional`")

# 1. INPUT DEL USUARIO
if len(st.session_state.messages) == 0:
    with st.container():
        st.info(f"👋 Hola Sofía. Tus expertos están listos para simular un escenario de **{scenario}**.")
        initial_idea = st.chat_input("Escribe la idea, copy o estrategia a debatir...")
        if initial_idea:
            st.session_state.messages.append({"role": "user", "content": initial_idea, "name": "Sofia (CEO)"})
            st.session_state.simulation_active = True
            st.rerun()

# 2. MOSTRAR HISTORIAL
for msg in st.session_state.messages:
    avatar = "👩‍💻" if msg["role"] == "user" else "⚡"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(f"**{msg.get('name', 'AI')}:**")
        st.write(msg["content"])

# 3. MOTOR DE DEBATE (LOOP COMPLEJO)
if st.session_state.simulation_active:
    if not api_key:
        st.warning("⚠️ Necesitas la API Key para activar el cerebro.")
        st.stop()

    # BUCLE DE RONDAS (Aquí está la potencia)
    total_turns = rounds * len(selected_archetypes)
    
    st.divider()
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    current_turn = 0
    
    # Iteramos por el número de rondas solicitadas
    for r in range(rounds):
        st.markdown(f"### 🔄 Ronda {r + 1} de {rounds}")
        
        for agent_name in selected_archetypes:
            # Actualizar barra de progreso
            current_turn += 1
            progress = current_turn / total_turns
            progress_bar.progress(progress)
            status_text.caption(f"Pensando: {agent_name} (Analizando contexto...)")
            
            with st.chat_message("assistant", avatar="🧠"):
                message_placeholder = st.empty()
                
                # RECUPERAR PERSONALIDAD
                agent_persona = st.session_state.c8_archetypes[agent_name]
                
                # PROMPT DE INGENIERÍA AVANZADA
                # Le damos instrucciones de debatir con los anteriores
                system_prompt = f"""
                Eres {agent_name}. 
                Tu personalidad es: {agent_persona}.
                
                CONTEXTO:
                - Escenario: {scenario}
                - Ronda actual: {r + 1} de {rounds}.
                
                OBJETIVO:
                Analiza la idea del usuario y las respuestas de los otros agentes.
                No seas genérico. Profundiza.
                Si estás en la Ronda 1: Da tu primera impresión fuerte.
                Si estás en Rondas siguientes: REFUTA o APOYA lo que dijeron los otros agentes antes que tú. Genera debate.
                Usa formato Markdown (negritas, listas) para estructurar tu respuesta.
                """
                
                messages = [{"role": "system", "content": system_prompt}]
                
                # Inyectamos toda la memoria de la conversación
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "assistant"
                    messages.append({"role": role, "content": f"{m.get('name')}: {m['content']}"})

                try:
                    client = openai.OpenAI(api_key=api_key)
                    # Usamos un poco más de temperatura para creatividad
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo", 
                        messages=messages,
                        temperature=0.8,
                        max_tokens=600 # Permitimos respuestas más largas
                    )
                    reply = response.choices[0].message.content
                    
                    message_placeholder.markdown(f"**{agent_name}:** \n\n{reply}")
                    st.session_state.messages.append({"role": "assistant", "content": reply, "name": agent_name})
                    time.sleep(1) 
                    
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state.simulation_active = False
                    st.stop()
    
    progress_bar.empty()
    status_text.empty()
    st.success("✅ Debate finalizado. Ahora es tu turno de intervenir.")
    st.session_state.simulation_active = False
    st.rerun()

# 4. INTERVENCIÓN DE SOFÍA (CONTINUAR EL LOOP)
if not st.session_state.simulation_active and len(st.session_state.messages) > 0:
    st.write("---")
    new_input = st.chat_input("Aporta nueva información, responde a una crítica o cambia el rumbo...")
    if new_input:
        st.session_state.messages.append({"role": "user", "content": new_input, "name": "Sofia (CEO)"})
        # Al responder tú, reactivamos la simulación para que ellos respondan a tu nuevo input
        st.session_state.simulation_active = True
        st.rerun()
