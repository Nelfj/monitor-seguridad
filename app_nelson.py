import streamlit as st
import requests
import google.generativeai as genai

# ==========================================
# 1. CONFIGURACIÓN DE IA (MODELO ACTUALIZADO)
# ==========================================
API_KEY = "AIzaSyCAGJkIZRX88u3MrU4q0TTphwdobFvIi3A"
genai.configure(api_key=API_KEY)

# Cambiamos a la versión específica que pide la API actualmente
model = genai.GenerativeModel('gemini-1.5-flash')

def obtener_analisis_ia(titulo, descripcion):
    prompt = f"""
    Eres experto en seguridad electrónica para la empresa RTD. 
    Analiza esta licitación de Mercado Público:
    TÍTULO: {titulo}
    DESCRIPCIÓN: {descripcion}
    
    Responde en 2 frases cortas:
    1. ¿Qué tecnología clave de seguridad piden?
    2. ¿Es buena oportunidad para RTD?
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error de IA: Verifique su cuota o conexión."

# ==========================================
# 2. CONFIGURACIÓN DE LA APP
# ==========================================
st.set_page_config(page_title="Monitor RTD Inteligente", layout="wide")

st.title("🛡️ Monitor de Licitaciones RTD + IA")
st.markdown("### Hola equipo licitaciones publicas RTD")
st.divider()

# --- OBTENCIÓN DE DATOS ---
TICKET = "081040C1-4072-483E-9054-12D7D69DA9EE"
URL_API = f"https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?estado=activas&ticket={TICKET}"

try:
    res = requests.get(URL_API)
    datos = res.json().get("Listado", [])
    
    # Filtros optimizados
    FILTROS = ["camaras", "televigilancia", "lpr", "ptz", "seguridad", "cctv", "monitoreo", "vigilancia"]
    
    encontradas = 0
    
    for l in datos:
        # CORRECCIÓN DE CAMPOS: Buscamos en varios nombres posibles para evitar el "None"
        nombre = l.get('Nombre') or "Licitación sin título"
        # Probamos sacar la descripción de varios campos comunes en la API
        desc = l.get('Descripcion') or l.get('Detalle') or "Descripción no disponible en el resumen."
        # Probamos varios campos para el Organismo
        organismo = l.get('NombreOrganismo') or l.get('OrganismoNombre') or "Organismo no informado"
        
        if any(f in (nombre + desc).lower() for f in FILTROS):
            encontradas += 1
            id_lic = l.get('CodigoExterno')
            
            with st.expander(f"📦 {nombre}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"🏢 **Organismo:** {organismo}")
                    st.write(f"📝 **Resumen:** {desc}")
                
                with col2:
                    st.link_button("🌐 Ver en Mercado Público", 
                                   f"https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idLicitacion={id_lic}",
                                   use_container_width=True)
                
                st.divider()
                st.markdown("#### 🤖 Análisis Estratégico IA")
                
                # Memoria de sesión
                key_ia = f"analisis_{id_lic}"
                if key_ia not in st.session_state:
                    st.session_state[key_ia] = None

                if st.button("Analizar con Gemini 1.5", key=f"btn_{id_lic}"):
                    with st.spinner("IA analizando..."):
                        st.session_state[key_ia] = obtener_analisis_ia(nombre, desc)
                
                if st.session_state[key_ia]:
                    st.info(st.session_state[key_ia])

    if encontradas == 0:
        st.info("No hay licitaciones nuevas de seguridad en este momento.")

except Exception as e:
    st.error(f"Error técnico: {e}")