import streamlit as st
import json
from openai import OpenAI

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="LocalMind | Asistente Políglota",
    page_icon="🌍",
    layout="centered"
)

# --- CLAVE API ---
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ Falta la clave API en los Secrets.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# --- ESTILOS CSS (DISEÑO LIMPIO Y CULTURAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@300;400;700&display=swap');

    /* 1. FONDO */
    [data-testid="stAppViewContainer"] {
        background-color: #FAFAFA;
    }
    
    /* 2. TARJETA PRINCIPAL */
    [data-testid="stMainBlockContainer"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        max-width: 700px;
    }

    /* 3. TIPOGRAFÍA */
    .brand-title {
        font-family: 'Playfair Display', serif;
        color: #1A1A1A;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 5px;
    }
    .brand-subtitle {
        font-family: 'Lato', sans-serif;
        color: #666;
        text-align: center;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 30px;
    }

    /* 4. CHAT BUBBLES */
    .stChatMessage {
        background-color: #F9F9F9;
        border: none;
        border-radius: 12px;
    }
    
    /* 5. BOTÓN WHATSAPP (LLAMAR AL CAMARERO) */
    a[href^="https://wa.me"] button {
        background-color: #1A1A1A !important; /* Negro elegante */
        color: white !important;
        border: none !important;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* OCULTAR HEADER STREAMLIT */
    [data-testid="stHeader"], footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- MENÚ (Base de Datos) ---
MENU_DB = {
    "Jamón Ibérico de Bellota": 22.00,
    "Papas Arrugadas con Mojo": 8.50,
    "Pulpo a la Gallega": 18.00,
    "Paella de Marisco (p.p.)": 16.50,
    "Gazpacho Andaluz": 7.50,
    "Sangría (Jarra)": 12.00,
    "Vino Tinto Rioja (Copa)": 4.50,
    "Tarta de Queso Casera": 6.00,
    "Crema Catalana": 5.50
}
menu_str = ", ".join([f"{k} ({v}€)" for k,v in MENU_DB.items()])

# --- ESTADO ---
if "pedido" not in st.session_state: st.session_state.pedido = []
if "mesa" not in st.session_state: st.session_state.mesa = "Mesa 1"

# --- FUNCIONES ---
def agregar_item(nombre_plato):
    precio = MENU_DB.get(nombre_plato, 0.0)
    # Búsqueda difusa simple
    if precio == 0.0:
        for k, v in MENU_DB.items():
            if k.lower() in nombre_plato.lower():
                nombre_plato = k
                precio = v
                break
    st.session_state.pedido.append({"item": nombre_plato, "precio": precio})
    
    # --- INSTRUCCIÓN PARA LA IA ---
    # Aquí forzamos la "Magia Cultural": Explicar el plato.
    return f"""
    [SYSTEM]: Item '{nombre_plato}' added.
    [INSTRUCTION]: 
    1. Confirm in USER'S language.
    2. Explain briefly what the dish is (cultural context) so they fall in love with it.
    3. Suggest a drink pairing.
    """

def borrar_item(index):
    st.session_state.pedido.pop(index)

# --- TOOLS ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "agregar_al_pedido",
            "description": "Anota un plato en la lista.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre_plato": {"type": "string", "description": "Nombre del plato"}
                },
                "required": ["nombre_plato"],
            },
        }
    }
]

# --- SIDEBAR (Configuración) ---
with st.sidebar:
    st.write("🔧 Panel de Control")
    if st.button("🗑️ Limpiar Sesión"):
        st.session_state.pedido = []
        st.session_state.messages = []
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.markdown('<div class="brand-title">LocalMind</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-subtitle">Smart Menu Assistant</div>', unsafe_allow_html=True)

# --- VISOR DE PEDIDO (SIN PAGAR, SOLO LISTA) ---
total = sum(p['precio'] for p in st.session_state.pedido)
label = f"📝 TU CUENTA | {len(st.session_state.pedido)} items | {total:.2f}€"

with st.expander(label, expanded=(len(st.session_state.pedido) > 0)):
    # Selector de Mesa
    st.session_state.mesa = st.selectbox("Ubicación:", [f"Mesa {i}" for i in range(1,21)], index=0)
    
    st.markdown("---")
    
    if not st.session_state.pedido:
        st.caption("Pide recomendaciones al chat. Hablo +50 idiomas. 🌍")
    else:
        for i, p in enumerate(st.session_state.pedido):
            c1, c2, c3 = st.columns([6, 2, 1])
            c1.markdown(f"**{p['item']}**")
            c2.markdown(f"{p['precio']:.2f}€")
            c3.button("✖️", key=f"del_{i}", on_click=borrar_item, args=(i,))
        
        st.markdown("---")
        
        # EL "BOTÓN MÁGICO" (Sin cobrar, solo avisar)
        items_str = "%0A".join([f"▪️ {p['item']}" for p in st.session_state.pedido])
        msg = f"🔔 *NUEVO PEDIDO* 🔔%0A------------------%0A{items_str}%0A------------------%0A📍 *{st.session_state.mesa}*%0ATotal (A cobrar en mesa): {total:.2f}€"
        link = f"https://wa.me/34600000000?text={msg}"
        
        st.link_button("🛎️ LLAMAR AL CAMARERO (Enviar Pedido)", link, use_container_width=True)

# --- CEREBRO IA (MODO POLÍGLOTA EXTREMO) ---
system_prompt = f"""
Eres el "Sumiller Cultural" de este restaurante. 
MENÚ: {menu_str}

🌍 TUS 3 SUPERPODERES (OBLIGATORIOS):

1. **POLÍGLOTA RADICAL:**
   - Detecta AUTOMÁTICAMENTE el idioma: Chino (Mandarín/Cantonés), Ruso, Árabe, Japonés, Coreano, Hebreo, Alemán, Noruego, Sueco, etc.
   - Responde SIEMPRE en ese idioma nativo.

2. **GUÍA GASTRONÓMICO (Storytelling):**
   - No solo tomes nota. **Vende el plato.**
   - Si piden "Jamón", explica que es "Joya de España, curado por años".
   - Si piden "Papas con Mojo", menciona que es el "Sabor volcánico de Canarias".
   - Haz que se les haga la boca agua.

3. **ASISTENTE, NO CAJERO:**
   - Tu objetivo es crear la lista de deseos.
   - Usa emojis elegantes (🍷, 🥘, ✨).
   - Sé extremadamente educado y servicial.

EJEMPLO RUSO:
User: "Что такое gazpacho?"
AI: "Гаспачо — это освежающий холодный андалузский суп из спелых томатов... 🍅 Идеально подходит для жаркого дня! Хотите попробовать?"
"""

if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# Renderizar Chat
for m in st.session_state.messages:
    if m["role"] in ["assistant", "user"] and m.get("content"):
        with st.chat_message(m["role"], avatar="🤵🏻" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])

# Input Usuario
if prompt := st.chat_input("Ask me anything / Pregúntame lo que quieras..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.messages,
            tools=tools,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        
        # Procesar respuesta
        msg_dict = {"role": msg.role, "content": msg.content}
        
        if msg.tool_calls:
            msg_dict["tool_calls"] = [{"id": t.id, "type": t.type, "function": {"name": t.function.name, "arguments": t.function.arguments}} for t in msg.tool_calls]
            st.session_state.messages.append(msg_dict)
            
            for tool in msg.tool_calls:
                if tool.function.name == "agregar_al_pedido":
                    args = json.loads(tool.function.arguments)
                    res = agregar_item(args.get("nombre_plato"))
                    st.session_state.messages.append({"role": "tool", "tool_call_id": tool.id, "content": res})
            
            # Segunda vuelta para la explicación cultural
            final_res = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": final_res.choices[0].message.content})
            st.rerun()
        else:
            st.session_state.messages.append(msg_dict)
            st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")
