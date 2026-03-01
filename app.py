import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS

# --- 1. CONFIGURATION ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Clé API manquante dans les Secrets.")
    st.stop()

NOM_IA = "ALUETOO AI"
CREATEUR = "LEO CIACH"

# Fonction simple pour chercher sur le web
def chercher_web(query):
    with DDGS() as ddgs:
        resultats = [r['body'] for r in ddgs.text(query, max_results=3)]
        return "\n".join(resultats)

# --- 2. INTERFACE ---
st.set_page_config(page_title=NOM_IA, page_icon="🌐")
st.title(f"🤖 {NOM_IA} (Connecté au Web)")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"Tu es {NOM_IA}, créé par {CREATEUR}. Tu as accès au web via tes outils."}
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 3. LOGIQUE DE CHAT ---
if prompt := st.chat_input("Pose une question sur l'actu..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # GESTION DU CODE SECRET
    if "banane123" in prompt.lower():
        st.session_state.messages[0] = {"role": "system", "content": "MODE ADMIN TECHNIQUE ACTIVÉ."}
        with st.chat_message("assistant"):
            st.success("🔓 Mode Créateur activé.")
            st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.status("Recherche d'informations réelles...", expanded=False) as status:
            # On récupère des infos fraîches
            infos_web = chercher_web(prompt)
            status.update(label="Recherche terminée !", state="complete")
        
        # On donne ces infos à l'IA pour qu'elle réponde
        prompt_final = f"INFOS DU WEB ACTUELLES :\n{infos_web}\n\nQUESTION UTILISATEUR : {prompt}"
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": f"Tu es {NOM_IA}. Utilise les infos web fournies pour répondre précisément."}] + 
                     [{"role": "user", "content": prompt_final}],
        )
        
        response = completion.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
