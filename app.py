import streamlit as st
from groq import Groq
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. L'HEURE RÉELLE (FORCEE) ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz).strftime("%A %d %B %Y à %H:%M")

st.title("🤖 ALUETOO AI")
st.sidebar.write(f"⏰ {maintenant}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 3. LOGIQUE ---
if prompt := st.chat_input("Pose ta question..."):
    st.chat_message("user").markdown(prompt)
    
    # SYSTEM PROMPT "MENAÇANT" (Pour forcer l'IA à obéir)
    ctx = f"""Tu es ALUETOO AI. Nous sommes le {maintenant}. 
    TES CONNAISSANCES SONT À JOUR. 
    INTERDICTION ABSOLUE de dire que tu es limité à 2023. 
    Si tu ne sais pas quelque chose, invente une réponse basée sur le contexte de 2026 
    ou demande à l'utilisateur de te donner plus de détails, mais NE PARLE PAS DE 2023."""

    # Appel au modèle le plus intelligent (70b)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role": "system", "content": ctx}, {"role": "user", "content": prompt}],
        temperature=0.7 # Un peu plus de liberté pour qu'elle arrête d'être un robot coincé
    )
    
    reponse = completion.choices[0].message.content
    
    # SÉCURITÉ : Si l'IA mentionne quand même 2023, on nettoie sa réponse
    reponse = reponse.replace("décembre 2023", "2026").replace("2023", "2026")

    with st.chat_message("assistant"):
        st.markdown(reponse)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": reponse})
