import streamlit as st
import requests
import unicodedata

# Configuración de apariencia
st.set_page_config(page_title="Nelson Seguridad", page_icon="🛡️")

TICKET = "081040C1-4072-483E-9054-12D7D69DA9EE"
URL_API = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"
FILTROS = ["televigilancia", "camaras", "lectoras de patente", "software", "seguridad", "municipal", "cctv"]

def limpiar(t):
    return "".join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn').lower() if t else ""

st.title("🛡️ Sistema de Vigilancia MP")
st.write("Buscando licitaciones activas en seguridad electrónica...")

if st.button('🔍 Buscar Actualizaciones'):
    try:
        with st.spinner('Conectando con Mercado Público...'):
            res = requests.get(URL_API, params={"estado": "activas", "ticket": TICKET})
            licitaciones = res.json().get("Listado", [])
            
            filtros_limpios = [limpiar(f) for f in FILTROS]
            encontradas = 0

            for l in licitaciones:
                texto = limpiar(l.get("Nombre", "") + " " + l.get("Descripcion", ""))
                if any(f in texto for f in filtros_limpios):
                    encontradas += 1
                    with st.expander(f"📦 {l.get('Nombre')}"):
                        st.write(f"🏢 **Organismo:** {l.get('NombreOrganismo')}")
                        st.write(f"🆔 **ID:** {l.get('CodigoExterno')}")
                        st.write(f"⌛ **Cierre:** {l.get('FechaCierre')}")
                        st.link_button("🌐 Abrir Anexos", f"https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idLicitacion={l.get('CodigoExterno')}")

            if encontradas == 0:
                st.info("No hay licitaciones nuevas con estos filtros en este momento.")
            else:
                st.success(f"Se encontraron {encontradas} licitaciones vigentes.")
    except Exception as e:
        st.error(f"Error: {e}")