import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
NOM_IA = "ALUETOO AI"
CREATEUR = "LEO CIACH"

def obtenir_heure_belge():
    tz = pytz.timezone('Europe/Brussels')
    return datetime.now(tz).strftime("%A %d %B %Y, %H:%M:%S")

def chercher_web(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
            return "\n".join([r['body'] for r in results])
    except:
        return "Pas d'infos web trouvées."

# --- 2. INTERFACE ---
st.set_page_config(page_title=NOM_IA, page_icon="🤖")
st.title(f"🤖 {NOM_IA}")
heure_actuelle = obtenir_heure_belge()
st.sidebar.write(f"⏰ Heure en Belgique : {heure_actuelle}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 3. LOGIQUE DU CHAT ---
if prompt := st.chat_input("Pose ta question..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        # On cherche sur le web AVANT de répondre
        infos_recentes = chercher_web(prompt)
        
        # ON FORCE L'IA À LIRE CES INFOS
        instruction_forcee = (
            f"Tu es {NOM_IA}, l'IA de {CREATEUR}. "
            f"Oublie ta limite de 2023. Nous sommes le {heure_actuelle}. "
            f"Voici les infos actuelles du web : {infos_recentes}. "
            "Réponds à l'utilisateur en utilisant ces données."
        )

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": instruction_forcee}] + st.session_state.messages,
            temperature=0.1 # Plus précis, moins de blabla sur 2023
        )
        
        reponse = completion.choices[0].message.content
        st.markdown(reponse)
        st.session_state.messages.append({"role": "assistant", "content": reponse})
