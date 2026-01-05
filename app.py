import streamlit as st
from openai import OpenAI

# ⛪ Configuración de la página
st.set_page_config(page_title="El Monje - Asistente Virtual", page_icon="⛪", layout="centered")

# --- OPTIMIZACIÓN: Caché de Conexión ---
@st.cache_resource
def get_openai_client():
    # Asegúrate de tener la clave en secrets o cámbiala por tu clave directa para pruebas
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())

try:
    client = get_openai_client()
except Exception as e:
    st.error("Error de conexión con la abadía digital.")
    st.stop()

# --- DISEÑO PREMIUM (Estilo Monasterio / Negro y Ámbar) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Poppins:wght@300;400&display=swap');
    
    .block-container { padding-top: 1.5rem !important; max-width: 500px; }
    header {visibility: hidden !important;}
    
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.9)), 
                    url('https://images.unsplash.com/photo-1544911835-296896207868?q=80&w=800&auto=format&fit=crop'); 
        background-size: cover;
    }

    /* Cabecera */
    .header-monje { 
        text-align: center; border-bottom: 1px solid #FFBF00; 
        margin-bottom: 20px; padding-bottom: 10px;
    }
    .header-monje h1 { font-family: 'Cinzel', serif; color: #FFBF00; font-size: 1.6rem; margin: 0; }
    .header-monje p { font-family: 'Poppins', sans-serif; color: #FFBF00; font-size: 0.7rem; letter-spacing: 2px; opacity: 0.8; }

    /* Burbujas de Chat */
    .bubble-assistant { 
        background: rgba(40, 40, 40, 0.8); border-left: 4px solid #FFBF00; 
        padding: 15px; border-radius: 5px 15px 15px 15px; 
        color: #F2EADA; font-family: 'Poppins', sans-serif; margin-bottom: 15px;
    }
    .bubble-user { 
        background: rgba(255, 191, 0, 0.1); border-right: 4px solid #FFBF00; 
        padding: 12px; border-radius: 15px 5px 15px 15px; 
        color: #FFBF00; text-align: right; font-family: 'Poppins', sans-serif; 
        align-self: flex-end; margin-bottom: 15px;
    }
    .label-monje { color: #FFBF00; font-weight: 700; font-size: 0.7rem; display: block; margin-bottom: 5px; }

    .footer-brand { text-align: center; opacity: 0.4; font-size: 10px; color: white; margin-top: 20px; font-family: 'Poppins'; letter-spacing: 3px; }
    </style>

    <div class="header-monje">
        <h1>⛪ EL ASISTENTE DEL MONJE ⛪</h1>
        <p>SECRETOS Y TRADICIÓN CULINARIA</p>
    </div>
    """, unsafe_allow_html=True)

# --- LÓGICA DE MENSAJES ---
if "monje_messages" not in st.session_state:
    st.session_state.monje_messages = [
        {"role": "system", "content": "Eres el Monje, el sabio guardián de este restaurante. Tu tono es humilde, pausado y experto. Recomiendas platos caseros, vinos de la casa y postres tradicionales. Si preguntan por precios, sé elegante. No uses listas largas, habla como un consejero."},
        {"role": "assistant", "content": "Bienvenidos a nuestra mesa. Soy el Monje, y estoy aquí para guiarles por los sabores de nuestra cocina. ¿En qué puedo servirles hoy?"}
    ]

# Mostrar historial
for m in st.session_state.monje_messages:
    if m["role"] == "assistant":
        st.markdown(f'<div class="bubble-assistant"><span class="label-monje">⛪ EL MONJE</span>{m["content"]}</div>', unsafe_allow_html=True)
    elif m["role"] == "user":
        st.markdown(f'<div class="bubble-user">{m["content"]}</div>', unsafe_allow_html=True)

# --- ENTRADA Y STREAMING ---
if prompt := st.chat_input("Hable con el Monje..."):
    st.session_state.monje_messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="bubble-user">{prompt}</div>', unsafe_allow_html=True)
    
    with st.chat_message("assistant", avatar=None):
        st.markdown('<div class="bubble-assistant"><span class="label-monje">⛪ EL MONJE</span>', unsafe_allow_html=True)
        response_placeholder = st.empty()
        full_response = ""
        
        # Llamada con Streaming para máxima velocidad visual
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.monje_messages],
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.session_state.monje_messages.append({"role": "assistant", "content": full_response})
    st.rerun()

st.markdown('<div class="footer-brand">LOCALMIND AI</div>', unsafe_allow_html=True)
