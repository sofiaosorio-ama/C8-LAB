import streamlit as st
import openai
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="C8 Synth-Lab", page_icon="🧬", layout="wide")

# --- ESTILOS VISUALES (C8 BRANDING) ---
st.markdown("""
<style>
    .stChatMessage { border-radius: 10px; padding: 10px; margin-bottom: 5px;}
    .user-message { background-color: #f0f2f6; }
    .agent-message { background-color: #e8f4f8; border-left: 4px solid #007bff; }
    h1 { color: #2C3E50; }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADO (MEMORIA DEL PROYECTO) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "simulation_active" not in st.session_state:
    st.session_state.simulation_active = False

# --- BARRA LATERAL: CONFIGURACIÓN DEL UNIVERSO ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1904/1904425.png", width=50)
    st.title("🎛️ Panel de Control C8")
    
    # 1. API KEY
    api_key = st.text_input("Tu OpenAI API Key", type="password")
    if api_key:
        openai.api_key = api_key
    
    st.divider()

    # 2. SELECCIÓN DE ARQUETIPOS
    st.subheader("👥 El Consejo de Sabios")
    
    archetypes_options = {
        "El Visionario": "Eres un estratega soñador. Buscas el propósito, la expansión y el impacto a largo plazo. Te emocionan las ideas grandes.",
        "El Provocador": "Eres disruptivo y directo. Odias los clichés. Cuestionas todo lo que suena a 'vendehumos'. Buscas la innovación radical.",
        "El Educador": "Eres metódico y pedagógico. Te importa la estructura, el paso a paso y que el cliente entienda el proceso. Buscas claridad.",
        "El Curador": "Eres un esteta perfeccionista. Buscas la excelencia, la calidad visual y la experiencia premium. Odias lo mediocre.",
        "El Cliente Escéptico": "Eres un cliente que ha comprado cursos malos. No confías fácil. Buscas ROI (Retorno de Inversión) rápido y seguridad."
    }
    
    selected_archetypes = st.multiselect(
        "Elige de 3 a 5 Arquetipos para la Sala:",
        options=list(archetypes_options.keys()),
        default=["El Visionario", "El Provocador", "El Educador"]
    )

    # 3. CREAR ARQUETIPO PERSONALIZADO
    with st.expander("✨ Crear Arquetipo Personalizado"):
        new_name = st.text_input("Nombre del Rol (ej: Inversionista)")
        new_desc = st.text_area("Personalidad / Prompt")
        if st.button("Añadir a la Sala"):
            if new_name and new_desc:
                archetypes_options[new_name] = new_desc
                selected_archetypes.append(new_name)
                st.success(f"{new_name} añadido.")

# --- INTERFAZ PRINCIPAL: EL UNIVERSO ---
st.title("🧬 C8 Intelligence Universe")
st.caption("Arquitectura de Negocios Asistida por IA - Modo Validación Infinita")

# INICIO DEL DEBATE (INPUT INICIAL)
if len(st.session_state.messages) == 0:
    with st.container():
        st.info("👋 Bienvenida, Sofía. Vamos a crear un nuevo Universo de Validación.")
        initial_idea = st.chat_input("Escribe aquí tu Idea de Negocio...")
        
        if initial_idea:
            st.session_state.messages.append({"role": "user", "content": initial_idea, "name": "Sofia (Arquitecta)"})
            st.session_state.simulation_active = True
            st.rerun()

# MOSTRAR HISTORIAL DEL CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(f"**{msg.get('name', 'AI')}:** {msg['content']}")

# MOTOR DE SIMULACIÓN
if st.session_state.simulation_active:
    if not api_key:
        st.warning("⚠️ Por favor ingresa tu API Key en la barra lateral para iniciar.")
        st.stop()

    st.divider()
    st.write("👀 **Observando el debate...**")
    
    for agent_name in selected_archetypes:
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            
            # Construir contexto
            agent_persona = archetypes_options[agent_name]
            conversation_history = [
                {"role": "system", "content": f"Eres '{agent_name}'. Tu personalidad es: {agent_persona}. Opina brevemente."}
            ]
            
            for m in st.session_state.messages[-10:]:
                role = "user" if m["role"] == "user" else "assistant"
                conversation_history.append({"role": role, "content": f"{m.get('name')}: {m['content']}"})

            try:
                client = openai.OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=conversation_history,
                    temperature=0.7
                )
                response_text = response.choices[0].message.content
                
                # --- VERSIÓN CORREGIDA Y ESTABLE ---
                message_placeholder.markdown(f"**{agent_name}:** {response_text}")
                st.session_state.messages.append({"role": "assistant", "content": response_text, "name": agent_name})
                time.sleep(1) 
                
            except Exception as e:
                st.error(f"Error: {e}")
                break

    st.session_state.simulation_active = False
    st.rerun()

# INPUT PARA CONTINUAR
if not st.session_state.simulation_active and len(st.session_state.messages) > 0:
    new_input = st.chat_input("Añade información para continuar...")
    if new_input:
        st.session_state.messages.append({"role": "user", "content": new_input, "name": "Sofia (Arquitecta)"})
        st.session_state.simulation_active = True
        st.rerun()
