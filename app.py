import streamlit as st
from groq import Groq
import base64

# --- CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# --- INTERFACE ---
st.title("ALUETOO AI - Vision Mode")

uploaded_file = st.file_uploader("Scanner une image", type=["jpg", "png"])

if prompt := st.chat_input("Ta question..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # LE SECRET DE LA COMPATIBILITÉ :
        if uploaded_file:
            model = "llama-3.2-11b-vision-preview" # Seul modèle compatible photo
            base64_image = encode_image(uploaded_file)
            
            # Structure de message spécifique pour la vision
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        },
                    ],
                }
            ]
        else:
            model = "llama-3.3-70b-versatile" # Modèle ultra-rapide pour le texte
            messages = [{"role": "user", "content": prompt}]

        # Appel API
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
        
        response = st.write_stream(completion)
