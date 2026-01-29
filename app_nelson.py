import streamlit as st
import requests
import google.generativeai as genai
from datetime import datetime

# 1. CONFIGURACIÓN DE IA
API_KEY = "AIzaSyCAGJkIZRX88u3MrU4q0TTphwdobFvIi3A"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

def obtener_analisis_ia(titulo, descripcion):
    prompt = f"""
    Eres experto en seguridad electrónica (RTD). Analiza esta licitación:
    TÍTULO: {titulo}
    DESCRIPCIÓN: {descripcion}
    Responde en máximo 2 frases: ¿Qué tecnología clave piden y por qué es una buena oportunidad?
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "⚠️ Análisis temporalmente no disponible."

# 2. CONFIGURACIÓN DE LA APP (Sin Sidebar)
st.set_page_config(page_title="Monitor RTD Inteligente", layout="wide")

# Título Principal
st.title("🛡️ Monitor de Licitaciones RTD + IA")
st.markdown("### Hola equipo licitaciones publicas RTD")
st.divider()

# --- OBTENCIÓN DE DATOS ---
TICKET = "081040C1-4072-483E-9054-12D7D69DA9EE"
URL_API = f"https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?estado=activas&ticket={TICKET}"

try:
    res = requests.get(URL_API)
    datos = res.json().get("Listado", [])
    
    # Filtros optimizados para tu rubro
    FILTROS = ["camaras", "televigilancia", "lpr", "ptz", "seguridad", "cctv", "monitoreo", "vigilancia"]
    
    # Contador para el resumen
    encontradas = 0
    
    # Primero recorremos para contar y luego mostrar
    for l in datos:
        nombre = l.get('Nombre', '')
        desc = l.get('Descripcion', '')
        if any(f in (nombre + desc).lower() for f in FILTROS):
            encontradas += 1
            id_lic = l.get('CodigoExterno')
            
            # Formato de tarjeta limpia
            with st.expander(f"📦 {nombre}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"🏢 **Organismo:** {l.get('NombreOrganismo')}")
                    st.write(f"📝 **Descripción:** {desc}")
                
                with col2:
                    st.link_button("🌐 Ver en Mercado Público", 
                                   f"https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idLicitacion={id_lic}",
                                   use_container_width=True)
                
                st.divider()
                st.markdown("#### 🤖 Sugerencia Estratégica IA")
                
                # Memoria para que el análisis persista
                key_ia = f"analisis_{id_lic}"
                if key_ia not in st.session_state:
                    st.session_state[key_ia] = None

                if st.button("Analizar con Gemini", key=f"btn_{id_lic}"):
                    with st.spinner("Leyendo bases técnicas..."):
                        resultado = obtener_analisis_ia(nombre, desc)
                        st.session_state[key_ia] = resultado
                
                if st.session_state[key_ia]:
                    st.info(st.session_state[key_ia])

    if encontradas == 0:
        st.warning("No se encontraron licitaciones con los filtros de seguridad en este momento.")

except Exception as e:
    st.error(f"Error de conexión: {e}")