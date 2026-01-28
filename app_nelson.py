import streamlit as st
import requests
import unicodedata

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="Vigilancia Pública 24/7", layout="wide")

# Estilo CSS para las tarjetas
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .card {
        background-color: #1e2130;
        border: 1px solid #3e445e;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 25px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .trato-directo {
        border: 2px solid #ff4b4b !important;
        background-color: #2b1b1b !important;
    }
    .id-text { color: #fffd8d; font-weight: bold; font-size: 14px; }
    .org-text { color: #b0b0b0; font-size: 14px; margin-bottom: 10px; }
    .badge-pago {
        background-color: #28a745;
        color: white;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 12px;
        float: right;
    }
    .btn-link {
        display: block;
        width: 100%;
        padding: 12px;
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

TICKET = "081040C1-4072-483E-9054-12D7D69DA9EE"
URL_API = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"
FILTROS = ["televigilancia", "camaras", "lpr", "ptz", "software", "municipal", "cctv"]

def limpiar(t):
    return "".join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn').lower() if t else ""

# 2. INTERFAZ
st.title("🛡️ Vigilancia Pública 24/7")
col1, col2 = st.columns(2)
with col1: priorizar_mun = st.toggle("Priorizar Municipalidades y GORE", value=True)
with col2: solo_urgencia = st.toggle("Solo Trato Directo / Emergencia", value=False)

if st.button('🔍 ACTUALIZAR PANEL DE CONTROL'):
    try:
        with st.spinner('Analizando datos...'):
            res = requests.get(URL_API, params={"estado": "activas", "ticket": TICKET})
            licitaciones = res.json().get("Listado", [])
            filtros_limpios = [limpiar(f) for f in FILTROS]
            
            # Grid de 2 columnas
            grid_cols = st.columns(2)
            encontradas = 0

            for i, l in enumerate(licitaciones):
                nombre = l.get("Nombre", "").upper()
                desc = l.get("Descripcion", "")
                org = l.get("NombreOrganismo", "")
                id_ext = l.get("CodigoExterno")
                
                texto_total = limpiar(nombre + " " + desc)
                match = any(f in texto_total for f in filtros_limpios)
                es_urgente = any(x in texto_total for x in ["emergencia", "urgencia", "directo"])

                if match:
                    if solo_urgencia and not es_urgente: continue
                    encontradas += 1
                    
                    # Definimos el estilo de la tarjeta
                    css_clase = "card trato-directo" if es_urgente else "card"
                    
                    with grid_cols[encontradas % 2]:
                        # Construimos la tarjeta HTML
                        st.markdown(f"""
                        <div class="{css_clase}">
                            <span class="badge-pago">PAGO: 30 DÍAS</span>
                            <div class="id-text">ID: {id_ext}</div>
                            <h3 style="margin: 10px 0;">{nombre[:65]}...</h3>
                            <div class="org-text">🏢 {org}</div>
                            <div style="margin: 10px 0;">📹 CCTV | 🌐 FIBRA | 🚗 LPR</div>
                            {f'<div style="color:#ff4b4b; font-weight:bold;">🔥 URGENCIA DETECTADA</div>' if es_urgente else ''}
                            <a href="https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idLicitacion={id_ext}" 
                               target="_blank" class="btn-link">Abrir Ficha y Anexos</a>
                        </div>
                        """, unsafe_allow_html=True)

            if encontradas == 0:
                st.info("No se hallaron procesos de seguridad activos.")
                
    except Exception as e:
        st.error(f"Error: {e}")