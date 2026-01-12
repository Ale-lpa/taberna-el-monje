import streamlit as st
from openai import OpenAI

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="El Monje | Powered by Localmind.", page_icon="⛪", layout="centered")

# 2. CONEXIÓN OPTIMIZADA
@st.cache_resource
def get_openai_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())

try:
    client = get_openai_client()
except Exception as e:
    st.error("Error de conexión con la abadía digital.")
    st.stop()

# 3. DISEÑO PREMIUM (ESTILO MONASTERIO + BRANDING LOCALMIND)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Poppins:wght@300;400&display=swap');
    
    .block-container { padding-top: 1.5rem !important; max-width: 500px; }
    [data-testid="stHeader"], footer {visibility: hidden !important;}
    
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.92)), 
                    url('https://images.unsplash.com/photo-1544911835-296896207868?q=80&w=800&auto=format&fit=crop'); 
        background-size: cover;
    }

    /* BRANDING LOCALMIND */
    .branding-container { text-align: center; padding-bottom: 15px; }
    .powered-by { color: #FFBF00; font-size: 10px; letter-spacing: 3px; font-weight: bold; text-transform: uppercase; margin:0; opacity: 0.8; }
    .localmind-logo { color: #fff; font-size: 20px; font-weight: 800; margin:0; font-family: sans-serif; }
    .dot { color: #FFBF00; }

    /* Cabecera El Monje */
    .header-monje { 
        text-align: center; border-bottom: 1px solid #FFBF00; 
        margin-bottom: 25px; padding-bottom: 10px;
    }
    .header-monje h1 { font-family: 'Cinzel', serif; color: #FFBF00; font-size: 1.8rem; margin: 0; }
    .header-monje p { font-family: 'Poppins', sans-serif; color: #FFBF00; font-size: 0.7rem; letter-spacing: 2px; opacity: 0.8; }

    /* Burbujas de Chat */
    .bubble-assistant { 
        background: rgba(30, 30, 30, 0.9); border-left: 4px solid #FFBF00; 
        padding: 18px; border-radius: 5px 15px 15px 15px; 
        color: #F2EADA; font-family: 'Poppins', sans-serif; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .bubble-user { 
        background: rgba(255, 191, 0, 0.1); border-right: 4px solid #FFBF00; 
        padding: 12px; border-radius: 15px 5px 15px 15px; 
        color: #FFBF00; text-align: right; font-family: 'Poppins', sans-serif; 
        margin-bottom: 20px;
    }
    .label-monje { color: #FFBF00; font-weight: 700; font-size: 0.75rem; display: block; margin-bottom: 8px; letter-spacing: 1px; }
    </style>

    <div class="branding-container">
        <p class="powered-by">Powered by</p>
        <p class="localmind-logo">Localmind<span class="dot">.</span></p>
    </div>

    <div class="header-monje">
        <h1>⛪ EL MONJE </h1>
        <p>SECRETOS Y TRADICIÓN CULINARIA</p>
    </div>
    """, unsafe_allow_html=True)

# 4. LÓGICA DE MENSAJES CON REGLA DE ORO
if "monje_messages" not in st.session_state:
    st.session_state.monje_messages = [
        {
            "role": "system", 
            "content": """Eres 'El Monje', el sabio guardián de este restaurante. 
            TONO: Humilde, pausado, experto y místico. Hablas como un consejero culinario.
            REGLAS DE ORO DE IDIOMA:
            1. Detecta el idioma del usuario inmediatamente.
            2. Responde ÚNICA Y EXCLUSIVAMENTE en ese idioma.
            3. Prohibido mezclar idiomas. Si el usuario habla en inglés, no digas 'Hola'.
            4. Recomienda platos caseros y vinos con elegancia, sin usar listas largas."""
        },
        {"role": "assistant", "content": "Bienvenidos a nuestra humilde mesa. Soy el Monje, y estoy aquí para guiarles por los senderos de nuestra cocina. ¿En qué puedo servirles hoy?"}
    ]

# Mostrar historial
for m in st.session_state.monje_messages:
    if m["role"] == "assistant":
        st.markdown(f'<div class="bubble-assistant"><span class="label-monje">⛪ EL MONJE</span>{m["content"]}</div>', unsafe_allow_html=True)
    elif m["role"] == "user":
        st.markdown(f'<div class="bubble-user">{m["content"]}</div>', unsafe_allow_html=True)

# 5. ENTRADA Y STREAMING (GPT-4o-mini)
if prompt := st.chat_input("Hable con el Monje..."):
    st.session_state.monje_messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="bubble-user">{prompt}</div>', unsafe_allow_html=True)
    
    with st.chat_message("assistant", avatar=None):
        st.markdown('<div class="bubble-assistant"><span class="label-monje">⛪ EL MONJE</span>', unsafe_allow_html=True)
        response_placeholder = st.empty()
        full_response = ""
        
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
