import streamlit as st
import requests
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO DARK
st.set_page_config(page_title="Nelson Seguridad RTD", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .card {
        background-color: #1e2130;
        border: 1px solid #3e445e;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        color: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .trato-directo {
        border: 2px solid #ff4b4b !important;
        background-color: #2b1b1b !important;
    }
    .id-tag { color: #fffd8d; font-weight: bold; font-size: 13px; }
    .badge-tec {
        background-color: #3e445e;
        color: #00d4ff;
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 11px;
        margin-right: 5px;
    }
    .btn-ficha {
        display: block;
        width: 100%;
        padding: 10px;
        background-color: #007bff;
        color: white !important;
        text-align: center;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. VARIABLES Y FILTROS (Tus filtros actualizados)
TICKET = "081040C1-4072-483E-9054-12D7D69DA9EE"
URL_API = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"
FILTROS_SEGURIDAD = [
    "televigilancia", "camaras", "cámara", "lectoras de patente", "lpr", "ptz",
    "monitoreo", "software seguridad", "cctv", "central de mando", 
    "vigilancia municipal", "termica", "gore"
]

def limpiar(t):
    return "".join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn').lower() if t else ""

def detectar_caracteristicas(texto):
    caracts = []
    if "ptz" in texto: caracts.append("📹 PTZ")
    if "inalambrica" in texto: caracts.append("🌐 Wireless")
    if "lpr" in texto or "patente" in texto: caracts.append("🚗 LPR")
    if "poste" in texto: caracts.append("🏗️ Postes")
    if "sala" in texto or "espejo" in texto: caracts.append("🖥️ Sala Monitoreo")
    if "fibra" in texto: caracts.append("🌐 Fibra")
    if "termica" in texto: caracts.append("🔥 Térmica")
    return caracts

# 3. INTERFAZ SUPERIOR
st.title("🛡️ Análisis RTD - Seguridad Electrónica")

with st.sidebar:
    st.header("Configuración")
    solo_municipios = st.checkbox("Priorizar Municipalidades / GORE", value=True)
    solo_urgencia = st.toggle("🔔 Solo Urgencias / Tratos Directos", value=False)

if st.button('🔍 Escanear Mercado Público'):
    try:
        with st.spinner('Analizando licitaciones de seguridad...'):
            res = requests.get(URL_API, params={"estado": "activas", "ticket": TICKET})
            licitaciones = res.json().get("Listado", [])
            filtros_limpios = [limpiar(f) for f in FILTROS_SEGURIDAD]
            
            grid = st.columns(2)
            encontradas = 0

            for l in licitaciones:
                nombre = l.get("Nombre", "")
                desc = l.get("Descripcion", "")
                org = l.get("NombreOrganismo", "")
                id_ext = l.get("CodigoExterno")
                
                texto_total = limpiar(nombre + " " + desc)
                org_limpio = limpiar(org)
                
                match_seguridad = any(f in texto_total for f in filtros_limpios)
                es_gobierno = any(g in org_limpio for g in ["municipal", "gore", "intendencia", "subsecretaria", "carabineros"])
                es_urgente = any(x in texto_total for x in ["emergencia", "urgencia", "directo"])

                if match_seguridad:
                    if solo_municipios and not es_gobierno: continue
                    if solo_urgencia and not es_urgente: continue
                    
                    encontradas += 1
                    caracts = detectar_caracteristicas(texto_total)
                    clase_css = "card trato-directo" if es_urgente else "card"
                    
                    # Dibujar tarjeta en la cuadrícula
                    with grid[encontradas % 2]:
                        badges_html = "".join([f'<span class="badge-tec">{c}</span>' for c in caracts])
                        urgencia_html = '<div style="color:#ff4b4b; font-weight:bold; margin:5px 0;">🔥 URGENCIA DETECTADA</div>' if es_urgente else ''
                        
                        st.markdown(f"""
                        <div class="{clase_css}">
                            <div class="id-tag">ID: {id_ext}</div>
                            <h3 style="margin: 10px 0; font-size: 18px;">{nombre[:70]}...</h3>
                            <div style="color: #b0b0b0; font-size: 14px; margin-bottom: 10px;">🏢 {org}</div>
                            <div style="margin-bottom: 15px;">{badges_html}</div>
                            {urgencia_html}
                            <div style="font-size: 12px; color: #888;">⌛ Cierre: {l.get('FechaCierre')}</div>
                            <a href="https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idLicitacion={id_ext}" 
                               target="_blank" class="btn-ficha">Abrir Ficha y Anexos</a>
                        </div>
                        """, unsafe_allow_html=True)

            if encontradas == 0:
                st.info("No hay procesos activos con estos filtros.")
            else:
                st.success(f"Se encontraron {encontradas} licitaciones.")

    except Exception as e:
        st.error(f"Error: {e}")
        import streamlit as st
import requests
import unicodedata

# 1. FORZAR DISEÑO DE TABLERO PROFESIONAL (CSS)
st.set_page_config(page_title="Nelson Seguridad RTD", page_icon="🛡️", layout="wide")

