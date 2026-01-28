import streamlit as st
import requests
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO DARK PRO
st.set_page_config(page_title="Vigilancia Pública 24/7", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1c24; padding: 10px; border-radius: 10px; }
    .card {
        background-color: #1e2130;
        border: 1px solid #3e445e;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    .trato-directo {
        border: 2px solid #ff4b4b !important;
        background-color: #2b1b1b !important;
    }
    .badge-pago {
        background-color: #28a745;
        color: white;
        padding: 4px 8px;
        border-radius: 5px;
        font-size: 12px;
        float: right;
    }
    .badge-urgencia {
        color: #ff4b4b;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. VARIABLES Y FILTROS
TICKET = "081040C1-4072-483E-9054-12D7D69DA9EE"
URL_API = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"
FILTROS = ["televigilancia", "camaras", "lpr", "ptz", "software", "municipal", "cctv"]

def limpiar(t):
    return "".join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn').lower() if t else ""

# 3. INTERFAZ SUPERIOR
st.title("🛡️ Vigilancia Pública 24/7")
col_sw1, col_sw2 = st.columns([1, 1])
with col_sw1:
    priorizar_mun = st.toggle("Priorizar Municipalidades y GORE", value=True)
with col_sw2:
    solo_urgencia = st.toggle("Solo Trato Directo / Emergencia", value=False)

# 4. LÓGICA DE BÚSQUEDA
if st.button('🔍 ACTUALIZAR PANEL DE CONTROL'):
    try:
        res = requests.get(URL_API, params={"estado": "activas", "ticket": TICKET})
        licitaciones = res.json().get("Listado", [])
        filtros_limpios = [limpiar(f) for f in FILTROS]
        
        # Grid de 2 columnas para las tarjetas
        cols = st.columns(2)
        idx = 0

        for l in licitaciones:
            nombre = l.get("Nombre", "")
            desc = l.get("Descripcion", "")
            org = l.get("NombreOrganismo", "")
            tipo_oc = str(l.get("CodigoEstado", "")) # Usado para detectar urgencia
            
            texto_total = limpiar(nombre + " " + desc)
            match_seguridad = any(f in texto_total for f in filtros_limpios)
            es_urgente = any(x in texto_total for x in ["emergencia", "imprevisto", "urgencia", "directo"])

            if match_seguridad:
                if solo_urgencia and not es_urgente: continue
                
                # Definir clase de estilo
                clase_tarjeta = "card trato-directo" if es_urgente else "card"
                
                with cols[idx % 2]:
                    html_card = f"""
                    <div class="{clase_tarjeta}">
                        <span class="badge-pago">PAGO: 30 DÍAS</span>
                        <div style="color: #fffd8d; font-size: 14px;">ID: {l.get('CodigoExterno')}</div>
                        <h3 style="margin: 10px 0;">{nombre[:60]}...</h3>
                        {f'<div class="badge-urgencia">🔥 ¡URGENCIA DETECTADA! POSTULA YA</div>' if es_urgente else ''}
                        <p style="font-size: 14px; color: #b0b0b0;">🏢 {org}</p>
                        <div style="display: flex; gap: 10px; margin-top: 10px;">
                            <span>📹 CCTV</span> | <span>🌐 FIBRA</span> | <span>🚗 LPR</span>
                        </div>
                        <br>
                        <a href="https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idLicitacion={l.get('CodigoExterno')}" 
                           target="_blank" style="text-decoration: none;">
                            <button style="background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; width: 100%;">
                                Abrir Ficha y Anexos
                            </button>
                        </a>
                    </div>
                    """
                    st.markdown(html_card, unsafe_allow_html=True)
                    idx += 1

    except Exception as e:
        st.error(f"Error de conexión: {e}")

st.sidebar.markdown("---")
st.sidebar.write(" Última Actualización: " + st.session_state.get('last_run', 'Recién iniciado'))