import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import hashlib
import io
from tinydb import TinyDB, Query
from fpdf import FPDF

# --- CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(
    page_title="DataSocio Pro | Intelligence OS", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS de alta fidelidad (Recuperados y mantenidos)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    :root {
        --primary: #38bdf8;
        --bg: #0f172a;
        --card: #1e293b;
        --danger: #ef4444;
        --admin: #10b981;
        --text-muted: #94a3b8;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: var(--bg);
    }
    
    /* Login High-End */
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 2.5rem;
        background: var(--card);
        border-radius: 15px;
        border: 1px solid #334155;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* Prólogo de Bienvenida */
    .prologo-section {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #334155;
        margin-bottom: 2rem;
        box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
    }

    /* Botones Personalizados */
    .stButton button {
        border-radius: 8px !important;
        transition: all 0.2s ease;
    }
    .logout-btn button {
        background-color: var(--danger) !important;
        color: white !important;
        border: none !important;
    }
    .clear-btn button {
        background-color: #475569 !important;
        color: white !important;
        border: none !important;
    }
    
    /* Tarjetas de Resultados */
    .res-card {
        background: var(--card);
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid var(--primary);
        margin-bottom: 15px;
        transition: transform 0.2s ease;
    }
    .res-card:hover {
        transform: translateX(5px);
    }
    
    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-left: 12px;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NÚCLEO DE DATOS Y SEGURIDAD ---
db = TinyDB('usuarios_db.json')
User = Query()
def hash_p(password): return hashlib.sha256(str.encode(password)).hexdigest()

# Manejo de Estados de Sesión
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'last_run' not in st.session_state: st.session_state.last_run = []
if 'input_reset_key' not in st.session_state: st.session_state.input_reset_key = 0

# --- LÓGICA DE ACCESO ---
if not st.session_state.logged_in:
    st.markdown("""
        <div class="login-header">
            <h1 style="color: #38bdf8; margin:0;">DataSocio Intelligence</h1>
            <p style="color:#94a3b8; margin-top:10px;">Consola de Extracción de Datos de Precisión</p>
        </div>
    """, unsafe_allow_html=True)
    
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        with st.container():
            u = st.text_input("Identificador de Operador").strip()
            p = st.text_input("Código de Acceso", type="password").strip()
            if st.button("🚀 INICIAR SESIÓN", use_container_width=True):
                res = db.search(User.username == u)
                if res and res[0]['password'] == hash_p(p):
                    st.session_state.logged_in = True
                    st.session_state.user_now = u
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. Acceso denegado.")
    st.stop()

# --- DATOS DEL OPERADOR ---
user_data = db.search(User.username == st.session_state.user_now)[0]
is_admin = (st.session_state.user_now == "Cabecha305")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🛠️ Panel de Control")
    st.write("---")
    
    if is_admin:
        st.markdown(f"**Nivel de Acceso:** 👑 `ADMIN`")
        st.markdown(f"**Usuario:** `{st.session_state.user_now}`")
        st.success("Modo Dios: Créditos Infinitos")
    else:
        st.markdown(f"**Nivel de Acceso:** 👤 `OPERADOR`")
        st.markdown(f"**Usuario:** `{st.session_state.user_now}`")
        st.metric("Créditos Disponibles", user_data['credits'])
    
    st.write("---")
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("⬅️ FINALIZAR SESIÓN", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- INTERFAZ DE OPERACIONES ---
st.title("🛡️ Consola Operativa de Inteligencia")

# Prólogo Interno Recuperado
st.markdown("""
    <div class="prologo-section">
        <h4 style='color: #38bdf8; margin-top:0;'>Bienvenido al Motor de Extracción v17.1</h4>
        <p style='color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;'>
            Esta herramienta permite la extracción automatizada de puntos de contacto. 
            Asegúrese de que las URLs inyectadas sean válidas y tengan el protocolo HTTP/HTTPS.
        </p>
        <div style="display: flex; gap: 20px; margin-top: 15px;">
            <div style="background: rgba(56, 189, 248, 0.1); padding: 10px 15px; border-radius: 8px; border: 1px solid var(--primary);">
                <span style="color: var(--primary); font-weight: bold;">1. Inyección</span>
            </div>
            <div style="background: rgba(56, 189, 248, 0.1); padding: 10px 15px; border-radius: 8px; border: 1px solid var(--primary);">
                <span style="color: var(--primary); font-weight: bold;">2. Rastreo</span>
            </div>
            <div style="background: rgba(56, 189, 248, 0.1); padding: 10px 15px; border-radius: 8px; border: 1px solid var(--primary);">
                <span style="color: var(--primary); font-weight: bold;">3. Dataset</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Área de Trabajo
col_in, col_opt = st.columns([2, 1])

with col_in:
    # CLAVE DINÁMICA: Cuando st.session_state.input_reset_key cambia, este widget se vacía solo.
    urls_input = st.text_area(
        "📋 Inyectar URLs de Objetivo (una por línea):", 
        height=200, 
        placeholder="Ejemplo: https://empresa.com",
        key=f"input_area_{st.session_state.input_reset_key}"
    )

with col_opt:
    st.markdown("### 🎯 Objetivos")
    c_mail = st.checkbox("Extraer Emails", value=True)
    c_tel = st.checkbox("Extraer Teléfonos", value=True)
    c_ssl = st.checkbox("Verificar SSL", value=True)
    st.info("El sistema prioriza la velocidad sobre el renderizado de JS.")

# Acciones Principales
col_btn1, col_btn2 = st.columns([2, 1])

with col_btn1:
    if st.button("⚡ EJECUTAR ESCANEO DE PRECISIÓN", use_container_width=True):
        urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
        puede_operar = is_admin or (user_data['credits'] >= len(urls))
        
        if urls and puede_operar:
            results = []
            progress = st.progress(0)
            for i, url in enumerate(urls):
                try:
                    if not is_admin:
                        nuevos_creditos = user_data['credits'] - 1
                        db.update({'credits': nuevos_creditos}, User.username == st.session_state.user_now)
                        user_data['credits'] = nuevos_creditos
                    
                    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    text = soup.get_text()
                    
                    res_obj = {"URL": url, "Seguridad": "Segura" if url.startswith("https") else "No Segura"}
                    if c_mail: 
                        emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
                        res_obj["Emails"] = ", ".join(emails) if emails else "Ninguno"
                    if c_tel: 
                        tels = list(set(re.findall(r'\+?\d{10,13}', text)))
                        res_obj["Teléfonos"] = ", ".join(tels) if tels else "Ninguno"
                    results.append(res_obj)
                except:
                    results.append({"URL": url, "Error": "Inalcanzable"})
                progress.progress((i+1)/len(urls))
            
            st.session_state.last_run = results
            st.rerun()
        elif not urls:
            st.warning("No se detectaron URLs válidas.")
        else:
            st.error("Créditos insuficientes.")

with col_btn2:
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("🧹 LIMPIAR TODO", use_container_width=True):
        st.session_state.last_run = []
        st.session_state.input_reset_key += 1 # RESETEA EL CUADRO DE TEXTO
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- FUNCIONES DE EXPORTACIÓN ---
def generar_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "DataSocio OS - Reporte de Inteligencia", ln=True, align='C')
    pdf.ln(10)
    for r in datos:
        if "Error" in r: continue
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, f"URL: {r['URL']} ({r['Seguridad']})", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 6, f"Emails: {r.get('Emails', 'Ninguno')}")
        pdf.multi_cell(0, 6, f"Teléfonos: {r.get('Teléfonos', 'Ninguno')}")
        pdf.ln(5)
    return bytes(pdf.output(dest='S').encode('latin1', 'replace'))

# --- VISUALIZACIÓN DE RESULTADOS ---
if st.session_state.last_run:
    st.write("---")
    st.subheader("💎 Datos Extraídos")
    
    # Lógica de Desglose para Excel/CSV (Mantenida de v16.0)
    export_list = []
    for r in st.session_state.last_run:
        if "Error" in r: continue
        url, sec = r['URL'], r['Seguridad']
        ems = r.get('Emails', '').split(', ') if r.get('Emails') != 'Ninguno' else []
        tls = r.get('Teléfonos', '').split(', ') if r.get('Teléfonos') != 'Ninguno' else []
        
        if not ems and not tls:
            export_list.append({'URL': url, 'Seguridad': sec, 'Tipo': 'N/A', 'Contacto': 'Sin Datos'})
        for e in ems: export_list.append({'URL': url, 'Seguridad': sec, 'Tipo': 'Email', 'Contacto': e})
        for t in tls: export_list.append({'URL': url, 'Seguridad': sec, 'Tipo': 'Teléfono', 'Contacto': t})
            
    df_export = pd.DataFrame(export_list)

    col_dl1, col_dl2, col_dl3 = st.columns(3)
    with col_dl1:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Resultados')
        st.download_button("📥 EXCEL (.xlsx)", buffer, "data_socio.xlsx", use_container_width=True)
    with col_dl2:
        st.download_button("📥 CSV (.csv)", df_export.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig'), "data_socio.csv", use_container_width=True)
    with col_dl3:
        st.download_button("📥 PDF (.pdf)", generar_pdf(st.session_state.last_run), "reporte_socio.pdf", use_container_width=True)

    # Vista previa en tarjetas (Recuperada con diseño completo)
    for r in st.session_state.last_run:
        if "Error" in r:
            st.error(f"❌ {r['URL']} - No se pudo acceder al servidor.")
        else:
            badge_color = "#10b981" if r['Seguridad'] == "Segura" else "#ef4444"
            st.markdown(f"""
                <div class="res-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <b style="color:#38bdf8; font-size:1.1rem;">🔗 {r['URL']}</b>
                        <span class="status-badge" style="background:{badge_color}; color:white;">{r['Seguridad']}</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top:15px;">
                        <div>
                            <p style="margin:0; font-size:0.8rem; color:#94a3b8; text-transform:uppercase;">📧 Emails Detectados</p>
                            <span style="color:white; font-size:0.9rem;">{r.get('Emails', 'Ninguno')}</span>
                        </div>
                        <div>
                            <p style="margin:0; font-size:0.8rem; color:#94a3b8; text-transform:uppercase;">📞 Líneas Telefónicas</p>
                            <span style="color:white; font-size:0.9rem;">{r.get('Teléfonos', 'Ninguno')}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.write("---")
st.caption("DataSocio Engine v17.1 | Full-Stack Extraction System | Windows 11 i5 Optimized")
