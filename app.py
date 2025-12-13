import streamlit as st
import json
from openai import OpenAI

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Taberna El Monje",
    page_icon="🍷",
    layout="centered"
)

# --- 1. TU CLAVE DE OPENAI ---
# ⚠️ IMPORTANTE: PEGA AQUÍ TU CLAVE
# --- 1. TU CLAVE DE OPENAI (Usando Secretos) ---
# En lugar de pegar la clave aquí, le decimos que la busque en la caja fuerte de la nube
API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)

# --- 2. ESTILOS CSS (ESTILO BODEGA PREMIUM) ---
st.markdown("""
    <style>
    /* 1. FONDO DE PANTALLA */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?q=80&w=1920&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* 2. LIMPIEZA DE INTERFAZ */
    [data-testid="stHeader"] {background-color: rgba(0,0,0,0);}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* 3. TÍTULOS */
    .titulo-principal {
        font-family: 'Garamond', serif;
        color: #FFFFFF;
        text-align: center;
        font-size: 4rem;
        font-weight: bold;
        text-shadow: 0px 0px 10px rgba(0,0,0,0.8); /* Sombra brillante */
        margin-top: 10px;
    }
    .subtitulo {
        text-align: center;
        color: #E0C097; /* Color Dorado suave */
        font-style: italic;
        font-size: 1.4rem;
        text-shadow: 1px 1px 2px #000000;
        margin-bottom: 30px;
    }

    /* 4. CAJA DEL CHAT (CRISTAL AHUMADO) */
    .stChatMessage {
        background-color: rgba(20, 20, 20, 0.85); /* Negro casi opaco */
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #7F2A3C; /* Borde sutil vino */
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }

    /* 5. TEXTOS DENTRO DEL CHAT */
    .stChatMessage p, .stChatMessage li {
        color: #F5F5F5 !important; /* Blanco hueso para leer bien */
        font-size: 1.05rem;
        line-height: 1.6;
    }
    .stChatMessage strong {
        color: #FFD700 !important; /* Dorados para resaltar platos */
    }
    
    /* Iconos del chat */
    .stChatMessage .stAvatar {
        border: 2px solid #E0C097;
    }

    /* 6. BARRA LATERAL (VINO OSCURO) */
    section[data-testid="stSidebar"] {
        background-color: #2D0F15; /* Color vino muy oscuro */
        border-right: 1px solid #5C1925;
    }
    /* Textos de la barra lateral en blanco/dorado */
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: #E0C097 !important; /* Dorado */
    }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] li, section[data-testid="stSidebar"] div, section[data-testid="stSidebar"] span {
        color: #F0F0F0 !important; /* Blanco suave */
    }
    /* Cajas de info en sidebar (success, info, warning) */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CARGAR DATOS ---
@st.cache_data
def cargar_menu():
    try:
        with open('menu_maestro.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError: return []

menu_data = cargar_menu()
menu_texto = json.dumps(menu_data, ensure_ascii=False)

# --- 4. BARRA LATERAL MEJORADA ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; margin-bottom: 10px;'>🍷 El Monje</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.9rem; color: #aaa !important;'>Vegueta, Las Palmas</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # SECCIÓN HORARIO VISUAL
    st.markdown("### 🕒 Horario Apertura")
    # Usamos columnas para que quede alineado perfecto
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("**L - V**")
        st.markdown("**Sáb**")
        st.markdown("**Dom**")
    with c2:
        st.markdown("09:00 - 23:00")
        st.markdown("10:00 - 00:00")
        st.markdown("10:00 - 23:00")

    st.markdown("---")
    
    # RESERVAS
    st.markdown("### 📞 Reservas")
    st.info("**928 31 01 85**")
    
    # NUEVO MENSAJE DE ALERGIAS
    st.markdown("---")
    st.warning("⚠️ **¿Alergias?**\nNo te la juegues. Pregúntame a mí por los ingredientes exactos (Gluten, Lactosa, etc).")

# --- 5. LÓGICA DEL CHAT ---
system_prompt = f"""
Eres 'Monjito', el sumiller virtual de 'El Monje'.
MENÚ: {menu_texto}
REGLAS:
1. Tu misión es vender y dar seguridad.
2. Si preguntan por alergias, revisa el campo 'alergenos' y responde con precisión total.
3. Usa negritas para resaltar platos y precios.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "¡Bienvenido a **El Monje**! 🍷\n\nSoy tu asistente personal. Puedes preguntarme por sugerencias, maridajes o consultar cualquier **alergia** con total confianza."}
    ]

# --- 6. INTERFAZ ---
st.markdown('<div class="titulo-principal">Taberna El Monje</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Tradición y Sabor en Vegueta</div>', unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar="🍷" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

if prompt := st.chat_input("Ej: ¿Las croquetas tienen lactosa?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🍷"):
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})