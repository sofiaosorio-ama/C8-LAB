import streamlit as st
import openai
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="C8 Synth-Lab", page_icon="🧬", layout="wide")

# --- ESTILOS VISUALES (C8 BRANDING) ---
st.markdown("""
<style>
    .stChatMessage { border-radius: 10px; padding: 10px; margin-bottom: 10px;}
    .user-message { background-color: #f0f2f6; }
    h1 { color: #2C3E50; }
    .stButton button { width: 100%; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 1. MEMORIA DEL SISTEMA (Estado Persistente) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "simulation_active" not in st.session_state:
    st.session_state.simulation_active = False

# AQUÍ ESTÁ LA MAGIA: Guardamos los arquetipos en la memoria para no perderlos
if "c8_archetypes" not in st.session_state:
    st.session_state.c8_archetypes = {
        "El Visionario": "Eres un estratega soñador. Buscas el propósito, la expansión y el impacto a largo plazo. Te emocionan las ideas grandes.",
        "El Provocador": "Eres disruptivo y directo. Odias los clichés. Cuestionas todo lo que suena a 'vendehumos'. Buscas la innovación radical.",
        "El Educador": "Eres metódico y pedagógico. Te importa la estructura, el paso a paso y que el cliente entienda el proceso. Buscas claridad.",
        "El Curador": "Eres un esteta perfeccionista. Buscas la excelencia, la calidad visual y la experiencia premium. Odias lo mediocre.",
        "El Cliente Escéptico": "Eres un cliente que ha comprado cursos malos. No confías fácil. Buscas ROI (Retorno de Inversión) rápido y seguridad."
    }

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🎛️ Panel C8")
    
    # API Key
    api_key = st.text_input("Tu OpenAI API Key", type="password")
    if api_key:
        openai.api_key = api_key
    
    st.divider()

    # --- CREADOR DE ARQUETIPOS (Ahora con memoria) ---
    with st.expander("✨ Crear Nuevo Agente", expanded=False):
        new_name = st.text_input("Nombre del Rol (ej: Inversor)")
        new_desc = st.text_area("Personalidad / Prompt")
        
        if st.button("Guardar Agente"):
            if new_name and new_desc:
                # Guardamos en la memoria persistente
                st.session_state.c8_archetypes[new_name] = new_desc
                st.success(f"¡{new_name} creado!")
                time.sleep(1)
                st.rerun() # Recargamos para que aparezca en la lista de abajo

    st.divider()

    # --- SELECTOR DE AGENTES ---
    # Ahora lee de la memoria, así que incluye los nuevos que creaste
    st.subheader("👥 El Consejo de Sabios")
    
    # Lista actualizada con tus creaciones
    options_list = list(st.session_state.c8_archetypes.keys())
    
    selected_archetypes = st.multiselect(
        "¿Quién entra a la sala?",
        options=options_list,
        default=["El Visionario", "El Provocador"] if "El Visionario" in options_list else []
    )

    if st.button("🧹 Limpiar Chat"):
        st.session_state.messages = []
        st.session_state.simulation_active = False
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.title("🧬 C8 Intelligence Universe")

# 1. INPUT DEL USUARIO
if len(st.session_state.messages) == 0:
    st.info("👋 Bienvenida al Laboratorio C8. Configura tu equipo a la izquierda y lanza un tema.")
    initial_idea = st.chat_input("Escribe tu idea, copy o estrategia aquí...")
    if initial_idea:
        st.session_state.messages.append({"role": "user", "content": initial_idea, "name": "Sofia"})
        st.session_state.simulation_active = True
        st.rerun()

# 2. MOSTRAR HISTORIAL (Visualización mejorada)
for msg in st.session_state.messages:
    # Elegimos avatar según quién hable
    avatar = "👩‍💻" if msg["role"] == "user" else "🤖"
    
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(f"**{msg.get('name', 'AI')}:**")
        st.write(msg["content"])

# 3. MOTOR DE SIMULACIÓN
if st.session_state.simulation_active:
    if not api_key:
        st.warning("⚠️ Pega tu API Key a la izquierda para iniciar.")
        st.stop()

    st.write("---")
    st.caption("⚡ Analizando con Metodología C8...")
    
    # Bucle de agentes seleccionados
    for agent_name in selected_archetypes:
        with st.chat_message("assistant", avatar="🧠"):
            message_placeholder = st.empty()
            
            # Recuperamos la personalidad desde la memoria
            agent_persona = st.session_state.c8_archetypes[agent_name]
            
            # Construimos la memoria del agente
            messages = [{"role": "system", "content": f"Eres {agent_name}. Personalidad: {agent_persona}. Sé breve, directo y constructivo."}]
            
            # Añadimos contexto reciente
            for m in st.session_state.messages[-8:]:
                role = "user" if m["role"] == "user" else "assistant"
                messages.append({"role": role, "content": f"{m.get('name')}: {m['content']}"})

            try:
                client = openai.OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                reply = response.choices[0].message.content
                
                # Renderizado
                message_placeholder.markdown(f"**{agent_name}:** {reply}")
                st.session_state.messages.append({"role": "assistant", "content": reply, "name": agent_name})
                time.sleep(0.5) # Ritmo de lectura
                
            except Exception as e:
                st.error(f"Error de conexión: {e}")
    
    st.session_state.simulation_active = False
    st.rerun()

# 4. CONTINUAR DEBATE
if not st.session_state.simulation_active and len(st.session_state.messages) > 0:
    new_input = st.chat_input("Responde a los agentes para continuar...")
    if new_input:
        st.session_state.messages.append({"role": "user", "content": new_input, "name": "Sofia"})
        st.session_state.simulation_active = True
        st.rerun()
