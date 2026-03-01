import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Clé API manquante dans les Secrets.")
    st.stop()

NOM_IA = "ALUETOO AI"
CREATEUR = "LEO CIACH"

# Heure exacte en Belgique
def obtenir_contexte_temps():
    tz_belgique = pytz.timezone('Europe/Brussels')
    maintenant = datetime.now(tz_belgique)
    return maintenant.strftime("%A %d %B %Y, %H:%M")

# Recherche Web Mondiale (plus puissante)
def chercher_web_mondial(query):
    try:
        with DDGS() as ddgs:
            # On cherche sans limite de région pour Dubaï ou l'actu mondiale
            results = ddgs.text(query, max_results=5)
            return "\n".join([r['body'] for r in results])
    except:
        return "Pas de résultats récents trouvés."

# --- 2. INTERFACE ---
st.set_page_config(page_title=NOM_IA, page_icon="🇧🇪")
temps_belge = obtenir_contexte_temps()

st.sidebar.title("Paramètres")
st.sidebar.write(f"⏰ **Heure Belge :**\n{temps_belge}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. CHAT ---
if prompt := st.chat_input("Pose ta question sur Dubaï ou l'actu..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Code Secret
    if "banane123" in prompt.lower():
        st.success("🔓 Mode Créateur activé.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.status("🌐 Recherche sur le Web mondial...", expanded=False):
            infos = chercher_web_mondial(prompt)
        
        # Le secret est ici : on dit à l'IA la date du jour TRÈS CLAIREMENT
        contexte_systeme = (
            f"Tu es {NOM_IA}, créé par {CREATEUR}. "
            f"Nous sommes le {temps_belge}. "
            f"Voici les infos récentes trouvées sur le web : {infos}. "
            "Réponds en utilisant ces infos pour être à jour."
        )
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": contexte_systeme}] + st.session_state.messages,
        )
        
        response = completion.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
