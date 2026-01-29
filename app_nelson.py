import streamlit as st
import requests
import unicodedata

# Configuración de apariencia profesional
st.set_page_config(page_title="Nelson Seguridad Pro", page_icon="🛡️", layout="wide")

TICKET = "081040C1-4072-483E-9054-12D7D69DA9EE"
URL_API = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"

# Listado maestro de filtros sugeridos por tus documentos
FILTROS_SEGURIDAD = [
    "televigilancia", "camaras", "cámara", "lectoras de patente", "lpr", "ptz",
    "monitoreo", "software seguridad", "cctv", "central de mando", "vigilancia municipal", "termica", "gore"
]

def limpiar(t):
    return "".join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn').lower() if t else ""

def detectar_caracteristicas(texto):
    """Detecta tecnicismos presentes en la descripción."""
    caracteristicas = []
    if "ptz" in texto: caracteristicas.append("📹 Domos PTZ")
    if "inalambrica" in texto: caracteristicas.append("🌐 Inalambrica")
    if "lpr" in texto or "patente" in texto: caracteristicas.append("🚗 Lectura Patentes (LPR)")
    if "poste" in texto: caracteristicas.append("🏗️ Instalación de Postes")
    if "sala" in texto or "espejo" in texto: caracteristicas.append("🖥️ Sala de Monitoreo")
    if "fibra" in texto: caracteristicas.append("🌐 Conectividad Fibra")
    return caracteristicas

st.title("🛡️ Análisis RTD ")
st.markdown("### Enfoque: Seguridad Electronica")

# Barra lateral para personalizar la búsqueda
with st.sidebar:
    st.header("Configuración")
    dias_vencimiento = st.slider("Días restantes de cierre (aprox)", 1, 30, 15)
    solo_municipios = st.checkbox("Priorizar Municipalidades", value=True)

if st.button('🔍 Escanear Mercado Público'):
    try:
        with st.spinner('Analizando licitaciones activas de seguridad...'):
            res = requests.get(URL_API, params={"estado": "activas", "ticket": TICKET})
            licitaciones = res.json().get("Listado", [])
            
            filtros_limpios = [limpiar(f) for f in FILTROS_SEGURIDAD]
            encontradas = 0

            for l in licitaciones:
                nombre_orig = l.get("Nombre", "")
                desc_orig = l.get("Descripcion", "")
                org_orig = l.get("NombreOrganismo", "")
                
                texto_total = limpiar(nombre_orig + " " + desc_orig)
                org_limpio = limpiar(org_orig)
                
                # Filtro: Debe coincidir con seguridad y (si se activa) ser municipal/gobierno
                match_seguridad = any(f in texto_total for f in filtros_limpios)
                es_gobierno = any(g in org_limpio for g in ["municipal", "gore", "intendencia", "subsecretaria", "carabineros"])
                
                if match_seguridad:
                    if solo_municipios and not es_gobierno:
                        continue
                        
                    encontradas += 1
                    caracts = detectar_caracteristicas(texto_total)
                    
                    # Interfaz de tarjeta profesional
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.subheader(f"📦 {nombre_orig}")
                            st.write(f"🏢 **Organismo:** {org_orig}")
                            st.write(f"📝 **Descripción:** {desc_orig[:250]}...")
                        
                        with col2:
                            st.info(f"🆔 ID: {l.get('CodigoExterno')}")
                            st.warning(f"⌛ Cierre: {l.get('FechaCierre')}")
                            st.link_button("🌐 Abrir Ficha y Anexos", f"https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idLicitacion={l.get('CodigoExterno')}")
                        
                        # Mostrar características técnicas detectadas
                        if caracts:
                            st.markdown(" **Requerimientos Técnicos Detectados:**")
                            st.write(" | ".join(caracts))
                        
                        st.divider()

            if encontradas == 0:
                st.info("No se hallaron procesos de seguridad municipal activos hoy.")
            else:
                st.success(f"Análisis completo: {encontradas} licitaciones de seguridad detectadas.")

    except Exception as e:

        st.error(f"Error en la conexión con la API: {e}")
