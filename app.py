import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from datetime import datetime
import pytz

# --- 1. CONFIGURATION INITIALE ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Erreur : Clé API manquante dans les Secrets Streamlit.")
    st.stop()

NOM_IA = "ALUETOO AI"
CREATEUR = "LEO CIACH"

# Gestion de l'heure belge
def obtenir_contexte_temps():
    tz_belgique = pytz.timezone('Europe/Brussels')
    maintenant = datetime.now(tz_belgique)
    return maintenant.strftime("%A %d %B %Y, %H:%M")

# Moteur de recherche mondial
def chercher_web(query):
    try:
        with DDGS() as ddgs:
            # On cherche les 5 meilleurs résultats mondiaux
            results = ddgs.text(query, max_results=5)
            if results:
                return "\n".join([f"- {r['body']}" for r in results])
            return "Aucune information récente trouvée sur le web."
    except Exception as e:
        return f"Erreur lors de la recherche : {e}"

# --- 2. INTERFACE UTILISATEUR ---
st.set_page_config(page_title=NOM_IA, page_icon="🇧🇪", layout="centered")

temps_belge = obtenir_contexte_temps()

# Sidebar stylée
with st.sidebar:
    st.title("🔧 Dashboard")
    st.metric("Heure locale (BE)", temps_belge.split(',')[1])
    st.write(f"📅 {temps_belge.split(',')[0]}")
    st.divider()
    st.write(f"Propulsé par Llama 3.3 & Groq")

st.title(f"🤖 {NOM_IA}")
st.caption(f"Une création de {CREATEUR} | Connectée au Web en temps réel")

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. LOGIQUE DE CHAT ---
if prompt := st.chat_input("Pose-moi une question sur l'actu (ex: Dubaï)..."):
    
    # Affichage du message utilisateur
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # VERIFICATION DU CODE SECRET (Banane123)
    if "banane123" in prompt.lower():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            st.success(f"🔓 ACCÈS CRÉATEUR CONFIRMÉ. Bonjour {CREATEUR}. Mode technique activé.")
            st.session_state.messages.append({"role": "assistant", "content": "Mode Créateur activé."})
        st.stop()

    # Enregistrement du message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # REPONSE DE L'ASSISTANT
    with st.chat_message("assistant"):
        with st.status("🔍 Recherche en cours sur le web mondial...", expanded=False) as status:
            contexte_web = chercher_web(prompt)
            status.update(label="Informations récupérées !", state="complete")
        
        # LE "SYSTEM PROMPT" QUI FORCE L'ACTUALITÉ
        system_instruction = (
            f"Tu es {NOM_IA}, l'IA de {CREATEUR}. "
            f"IMPORTANT : Nous sommes le {temps_belge}. "
            "Tes connaissances ne sont PAS limitées à 2023 car je te fournis un accès web. "
            "Tu DOIS utiliser les informations suivantes pour répondre à l'utilisateur. "
            "Si les informations web parlent d'événements de 2025 ou 2026, c'est que c'est VRAI. "
            f"\n\n--- DONNÉES WEB EN TEMPS RÉEL ---\n{contexte_web}"
        )

        try:
            # Construction de l'appel API
            full_messages = [{"role": "system", "content": system_instruction}] + st.session_state.messages
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=full_messages,
                temperature=0.3, # Plus bas pour être
