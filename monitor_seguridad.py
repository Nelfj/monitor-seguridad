import streamlit as st
import requests
import google.generativeai as genai
import unicodedata

# 1. Configuración de IA
API_KEY = "AIzaSyCAGJkIZRX88u3MrU4q0TTphwdobFvIi3A"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

def obtener_analisis_ia(titulo, descripcion):
    prompt = f"Analiza esta licitación de seguridad: {titulo}. Descripción: {descripcion}. Responde en 2 frases cortas sobre su valor estratégico."
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "⚠️ Error al conectar con la IA."

# 2. Interfaz
st.title("🛡️ Monitor Inteligente RTD")

# --- SIMULACIÓN DEL BUCLE DE LICITACIONES ---
# Aquí asumimos que tienes tu lista de licitaciones de Mercado Público
for l in licitaciones_encontradas:
    id_lic = l.get('CodigoExterno')
    
    with st.expander(f"📦 {l.get('Nombre')}"):
        st.write(f"🏢 **Organismo:** {l.get('NombreOrganismo')}")
        st.write(f"📝 **Descripción:** {l.get('Descripcion')}")
        
        st.divider()
        st.subheader("🤖 Análisis Estratégico IA")

        # --- MEMORIA DE LA APP ---
        # Creamos un nombre único en la memoria para esta licitación
        key_memoria = f"analisis_{id_lic}"

        # Si no existe en la memoria, lo preparamos como vacío
        if key_memoria not in st.session_state:
            st.session_state[key_memoria] = None

        # Botón para pedir el análisis
        if st.button("Analizar con Gemini", key=f"btn_{id_lic}"):
            with st.spinner("Leyendo bases técnicas..."):
                resultado = obtener_analisis_ia(l.get('Nombre'), l.get('Descripcion'))
                # GUARDAMOS EL RESULTADO EN LA MEMORIA
                st.session_state[key_memoria] = resultado

        # MOSTRAR EL RESULTADO (Si ya existe en la memoria, se queda ahí)
        if st.session_state[key_memoria]:
            st.info(st.session_state[key_memoria])
        
        st.link_button("🌐 Ver en Mercado Público", f"https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idLicitacion={id_lic}")