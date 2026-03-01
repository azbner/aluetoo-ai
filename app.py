import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from datetime import datetime
import pytz # Pour l'heure précise en Belgique

# --- 1. CONFIGURATION ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Clé API manquante dans les Secrets.")
    st.stop()

NOM_IA = "ALUETOO AI"
CREATEUR = "LEO CIACH"

# Fonction pour obtenir l'heure belge
def obtenir_heure_belgique():
    tz_belgique = pytz.timezone('Europe/Brussels')
    return datetime.now(tz_belgique).strftime("%d/%m/%Y %H:%M:%S")

# Fonction de recherche configurée pour la Belgique
def chercher_web(query):
    with DDGS() as ddgs:
        # 'be-fr' indique qu'on veut des résultats pour la Belgique en français
        resultats = [r['body'] for r in ddgs.text(query, region='be-fr', max_results=3)]
        return "\n".join(resultats)

# --- 2. INTERFACE ---
st.set_page_config(page_title=NOM_IA, page_icon="🇧🇪")
st.title(f"🤖 {NOM_IA}")

# On affiche l'heure en haut du site
heure_actuelle = obtenir_heure_belgique()
st.sidebar.write(f"📍 Lieu : Belgique")
st.sidebar.write(f"⏰ Heure : {heure_actuelle}")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"Tu es {NOM_IA}, créé par {CREATEUR}. Tu es basé en Belgique. Il est actuellement {heure_actuelle}."}
    ]

# --- 3. LOGIQUE DE CHAT ---
if prompt := st.chat_input("Pose ta question..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Code Secret
    if "banane123" in prompt.lower():
        st.success("🔓 Mode Créateur activé.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.status("Recherche en Belgique...", expanded=False) as status:
            infos_web = chercher_web(prompt)
            status.update(label="Infos trouvées !", state="complete")
        
        # On donne le contexte temporel et géographique à l'IA
        contexte = f"CONTEXTE : Nous sommes en Belgique. Heure actuelle : {heure_actuelle}.\nINFOS WEB : {infos_web}"
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": contexte}] + st.session_state.messages,
        )
        
        response = completion.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
