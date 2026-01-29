import streamlit as st
import requests
import unicodedata
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Vigilancia Pública Pro", layout="wide", page_icon="🛡️")

# 2. ESTILOS AVANZADOS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .card {
        background-color: #1e2130;
        border: 1px solid #3e445e;
        padding: 20px;
        border-radius: 12px;
        height: 320px;
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .card:hover { transform: translateY(-5px); border-color: #4da3ff; }
    .id-text { color: #fffd8d; font-family: monospace; font-size: 12px; }
    .trato-directo { border-left: 5px solid #ff4b4b !important; }
    .btn-link {
        display: block;
        padding: 8px;
        background-color: #007bff;
        color: white !important;
        text-align: center;
        border-radius: 5px;
        text-decoration: none;
        margin-top: 10px;
    }
    .metric-box {
        background: #262730;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #464855;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LÓGICA DE DATOS
TICKET = "081040C1-4072-483E-9054-12D7D69DA9EE"
URL_API = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"
FILTROS = ["televigilancia", "camaras", "lpr", "ptz", "software", "municipal", "cctv", "seguridad", "dron"]

def limpiar(t):
    if not t: return ""
    return "".join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn').lower()

# 4. INTERFAZ LATERAL (SIDEBAR)
with st.sidebar:
    st.image("https://www.mercadopublico.cl/Home/images/logo-mp.png", width=200)
    st.title("Configuración")
    solo_urgencia = st.toggle("🚨 Solo Urgencias", value=False)
    st.divider()
    st.info("Filtros activos: " + ", ".join(FILTROS))

# 5. CUERPO PRINCIPAL
st.title("🛡️ Panel de Vigilancia Tecnológica")
st.subheader("Monitoreo en tiempo real de Mercado Público Chile")

if st.button('🚀 ESCANEAR LICITACIONES AHORA'):
    try:
        with st.spinner('Consultando API de Mercado Público...'):
            res = requests.get(URL_API, params={"estado": "activas", "ticket": TICKET}, timeout=10)
            licitaciones = res.json().get("Listado", [])
            
            filtros_limpios = [limpiar(f) for f in FILTROS]
            encontradas = []

            for l in licitaciones:
                txt = limpiar(l.get("Nombre", "") + " " + l.get("Descripcion", ""))
                es_urgente = any(x in txt for x in ["emergencia", "urgencia", "directo"])
                
                if any(f in txt for f in filtros_limpios):
                    if solo_urgencia and not es_urgente: continue
                    encontradas.append({
                        "ID": l.get("CodigoExterno"),
                        "Nombre": l.get("Nombre"),
                        "Organismo": l.get("NombreOrganismo"),
                        "Fecha Cierre": l.get("FechaCierre"),
                        "Es Urgente": es_urgente,
                        "URL": f"https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idLicitacion={l.get('CodigoExterno')}"
                    })

            # Métrica y Exportación
            if encontradas:
                m1, m2, m3 = st.columns(3)
                with m1: st.markdown(f'<div class="metric-box"><h3>{len(encontradas)}</h3>Procesos detectados</div>', unsafe_allow_html=True)
                with m2: 
                    urgentes = sum(1 for x in encontradas if x["Es Urgente"])
                    st.markdown(f'<div class="metric-box" style="color:#ff4b4b"><h3>{urgentes}</h3>Críticos / Urgentes</div>', unsafe_allow_html=True)
                with m3:
                    df = pd.DataFrame(encontradas)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descargar Reporte Excel/CSV", data=csv, file_name=f"vigilancia_{datetime.now().date()}.csv", mime="text/csv")
                
                st.divider()

                # Grid de tarjetas
                cols = st.columns(2)
                for i, lic in enumerate(encontradas):
                    clase = "card trato-directo" if lic["Es Urgente"] else "card"
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div class="{clase}">
                            <div class="id-text">CÓDIGO: {lic['ID']}</div>
                            <h4 style="margin:8px 0; color:#fff;">{lic['Nombre'][:75]}...</h4>
                            <p style="color:#b0b0b0; font-size:13px;">🏢 {lic['Organismo']}</p>
                            <p style="font-size:12px; color:#4da3ff;">📅 Cierre: {lic['Fecha Cierre'] or 'No informada'}</p>
                            {f'<b style="color:#ff4b4b">🔥 DETECTADA COMO PRIORIDAD ALTA</b>' if lic['Es Urgente'] else ''}
                            <a href="{lic['URL']}" target="_blank" class="btn-link">Analizar Documentación</a>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No se hallaron coincidencias en el ciclo actual.")

    except Exception as e:
        st.error(f"Error de conexión: {e}")