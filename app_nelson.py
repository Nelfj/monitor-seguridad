import streamlit as st
import requests
import google.generativeai as genai

# 1. IA
API_KEY = "AIzaSyCAGJkIZRX88u3MrU4q0TTphwdobFvIi3A"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

def obtener_analisis_ia(titulo, descripcion):
    prompt = f"Como experto en seguridad RTD, analiza esta licitacion: {titulo}. Descripcion: {descripcion}. Responde en 2 frases cortas."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error de conexión con IA: {e}"

# 2. APP
st.set_page_config(page_title="Monitor RTD", layout="wide")
st.title("🛡️ Monitor Inteligente RTD")
st.markdown("### Hola equipo licitaciones publicas RTD")

TICKET = "081040C1-4072-483E-9054-12D7D69DA9EE"
URL = f"https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?estado=activas&ticket={TICKET}"

try:
    res = requests.get(URL)
    datos = res.json().get("Listado", [])
    FILTROS = ["camaras", "televigilancia", "lpr", "ptz", "seguridad", "cctv"]

    for l in datos:
        nombre = l.get('Nombre') or "Sin Nombre"
        desc = l.get('Descripcion') or "Sin descripción disponible"
        org = l.get('NombreOrganismo') or "Organismo no especificado"
        
        if any(f in (nombre + desc).lower() for f in FILTROS):
            id_lic = l.get('CodigoExterno')
            with st.expander(f"📦 {nombre}"):
                st.write(f"🏢 **Organismo:** {org}")
                st.write(f"📝 **Descripción:** {desc}")
                
                st.divider()
                st.markdown("#### 🤖 Sugerencia Estratégica IA")
                
                key_ia = f"analisis_{id_lic}"
                if key_ia not in st.session_state:
                    st.session_state[key_ia] = None

                if st.button("Analizar con Gemini", key=f"btn_{id_lic}"):
                    with st.spinner("Analizando..."):
                        st.session_state[key_ia] = obtener_analisis_ia(nombre, desc)
                
                if st.session_state[key_ia]:
                    st.info(st.session_state[key_ia])
                
                st.link_button("🌐 Ver en Mercado Público", f"https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idLicitacion={id_lic}")
except:
    st.error("Error al cargar datos.")
