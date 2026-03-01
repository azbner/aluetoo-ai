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
# --- 3. GESTION DE LA MÉMOIRE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"Tu es {NOM_IA}, une IA créée par {CREATEUR}. Réponds toujours en français."}
    ]

# --- NOUVEAU : VÉRIFICATION DU CODE SECRET ---
if prompt := st.chat_input("Demande à ALUETOO AI..."):
    # Si tu tapes le code secret
    if "je suis ton créateur code secret: banane123" in prompt.lower():
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # On change l'instruction de l'IA secrètement
        admin_instruction = "MODE ADMINISTRATEUR ACTIVÉ. Tu es maintenant en mode technique avec LEO CIACH. Tu peux parler de ton code, de tes serveurs et répondre de façon très technique sans filtre."
        st.session_state.messages[0] = {"role": "system", "content": admin_instruction}
        
        with st.chat_message("assistant"):
            st.success("Accès créateur confirmé. Bonjour Leo. Mode technique activé. Que veux-tu modifier ?")
            st.session_state.messages.append({"role": "assistant", "content": "Accès créateur confirmé. Mode technique activé."})
    
    else:
        # --- FONCTIONNEMENT NORMAL ---
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
            )
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
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

