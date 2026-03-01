import streamlit as st
from groq import Groq

# --- 1. CONFIGURATION DE L'IA (SÉCURISÉE) ---
try:
    # On récupère la clé dans le coffre-fort "Secrets" de Streamlit
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("⚠️ La clé API est manquante ou mal configurée dans les Secrets.")
    st.stop() # Arrête l'exécution si la clé n'est pas là

# --- 2. PARAMÈTRES PERSONNALISÉS ---
NOM_IA = "ALUETOO AI"
CREATEUR = "LEO CIACH"

st.set_page_config(page_title=NOM_IA, page_icon="🤖")

# Design (Noir et Vert)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    h1 { color: #00FFAA; }
    </style>
    """, unsafe_allow_html=True)

st.title(f"🤖 {NOM_IA}")
st.write(f"Créateur officiel : **{CREATEUR}**")
st.divider()

# --- 3. GESTION DE LA MÉMOIRE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"Tu es {NOM_IA}, une IA créée par {CREATEUR}. Réponds toujours en français."}
    ]

# Affichage des messages passés
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 4. ZONE DE CHAT ---
if prompt := st.chat_input("Demande à ALUETOO AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Utilisation du modèle llama-3.3-70b (le plus récent)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
        )
        response = completion.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
