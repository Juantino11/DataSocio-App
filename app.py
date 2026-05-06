import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import hashlib
import io
from tinydb import TinyDB, Query
from fpdf import FPDF

# --- CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="DataSocio Pro | Intelligence", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    :root { --primary: #38bdf8; --bg: #0f172a; --card: #1e293b; --danger: #ef4444; --admin: #10b981; }
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--bg); }
    
    .login-header {
        text-align: center; margin-bottom: 2rem; padding: 2rem;
        background: var(--card); border-radius: 15px; border: 1px solid #334155;
    }
    .prologo-section {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        padding: 1.5rem; border-radius: 15px; border: 1px solid #334155;
        margin-bottom: 2rem;
    }
    .stButton button { border-radius: 8px !important; font-weight: bold; }
    .logout-btn button { background-color: var(--danger) !important; color: white !important; }
    .clear-btn button { background-color: #475569 !important; color: white !important; margin-top: 5px; }
    
    .res-card {
        background: var(--card); padding: 20px; border-radius: 12px;
        border-left: 6px solid var(--primary); margin-bottom: 15px;
    }
    .status-badge {
        display: inline-block; padding: 2px 8px; border-radius: 4px;
        font-size: 0.7rem; font-weight: bold; margin-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS LOCAL ---
db = TinyDB('usuarios_db.json')
User = Query()
def hash_p(password): return hashlib.sha256(str.encode(password)).hexdigest()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'last_run' not in st.session_state: st.session_state.last_run = []

# --- PANTALLA DE LOGIN ---
if not st.session_state.logged_in:
    st.markdown('<div class="login-header"><h1 style="color: #38bdf8;">DataSocio OS</h1><p style="color:#94a3b8;">Acceso Restringido</p></div>', unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1, 1])
    with col_login:
        u = st.text_input("Operador").strip()
        p = st.text_input("Contraseña", type="password").strip()
        if st.button("🚀 INICIAR SESIÓN", use_container_width=True):
            res = db.search(User.username == u)
            if res and res[0]['password'] == hash_p(p):
                st.session_state.logged_in = True
                st.session_state.user_now = u
                st.rerun()
            else: st.error("Acceso denegado. Verifique credenciales.")
    st.stop()

# --- VALIDACIÓN DE USUARIO ---
user_data = db.search(User.username == st.session_state.user_now)[0]
is_admin = (st.session_state.user_now == "Cabecha305")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("⬅️ FINALIZAR SESIÓN", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    if is_admin:
        st.markdown(f"### 👑 `ADMIN: {st.session_state.user_now}`")
        st.success("✨ Modo Dios Activo")
    else:
        st.markdown(f"### 👤 `Operador: {st.session_state.user_now}`")
        st.metric("CRÉDITOS", user_data['credits'])

# --- PANEL CENTRAL ---
st.title("🛠️ Consola de Inteligencia")

st.markdown("""
    <div class="prologo-section">
        <h4 style='color: #38bdf8; margin-top:0;'>Bienvenido al Motor de Extracción</h4>
        <p style='color: #cbd5e1; font-size: 0.9rem;'>Siga los pasos para procesar datos de forma masiva y exportarlos limpios.</p>
    </div>
""", unsafe_allow_html=True)

col_p1, col_p2, col_p3 = st.columns(3)
with col_p1: st.info("1️⃣ **Inyección**: Cargue URLs.")
with col_p2: st.info("2️⃣ **Rastreo**: Extraiga datos.")
with col_p3: st.info("3️⃣ **Dataset**: Exporte en múltiples formatos.")
st.write("---")

col_in, col_opt = st.columns([2, 1])
with col_in:
    urls_input = st.text_area("📋 Inyectar URLs (una por línea):", height=150, placeholder="https://ejemplo.com")

with col_opt:
    st.markdown("🎯 **Objetivos de Análisis**")
    c_mail = st.checkbox("Extraer Emails", value=True)
    c_tel = st.checkbox("Extraer Teléfonos", value=True)
    c_ssl = st.checkbox("Verificar SSL", value=True)

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

st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
if st.button("🧹 LIMPIAR CONSULTA", use_container_width=True):
    st.session_state.last_run = []
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- GENERADOR DE PDF ---
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

# --- RENDERIZADO Y EXPORTACIÓN ---
if st.session_state.last_run:
    st.write("---")
    st.subheader("💎 Inteligencia Obtenida")
    
    # LÓGICA DE DESGLOSE (TIDY DATA) PARA EXCEL/CSV
    export_list = []
    for r in st.session_state.last_run:
        if "Error" in r: continue
        url = r['URL']
        sec = r['Seguridad']
        
        ems = r.get('Emails', '').split(', ') if r.get('Emails') != 'Ninguno' else []
        tls = r.get('Teléfonos', '').split(', ') if r.get('Teléfonos') != 'Ninguno' else []
        
        if not ems and not tls:
            export_list.append({'URL': url, 'Seguridad': sec, 'Tipo': 'Sin Datos', 'Contacto': 'Ninguno'})
        
        for e in ems:
            export_list.append({'URL': url, 'Seguridad': sec, 'Tipo': 'Email', 'Contacto': e})
        for t in tls:
            export_list.append({'URL': url, 'Seguridad': sec, 'Tipo': 'Teléfono', 'Contacto': t})
            
    df_export = pd.DataFrame(export_list)

    # BOTONES DE DESCARGA EN 3 COLUMNAS
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    with col_dl1:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Contactos')
        st.download_button("📥 EXCEL (.xlsx)", buffer, "contactos_datasocio.xlsx", "application/vnd.ms-excel", use_container_width=True)

    with col_dl2:
        csv = df_export.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 CSV (.csv)", csv, "contactos_datasocio.csv", "text/csv", use_container_width=True)

    with col_dl3:
        pdf_bytes = generar_pdf(st.session_state.last_run)
        st.download_button("📥 PDF (.pdf)", pdf_bytes, "reporte_datasocio.pdf", "application/pdf", use_container_width=True)

    st.write("---")
    # VISTA PREVIA EN TARJETAS
    for r in st.session_state.last_run:
        if "Error" in r:
            st.error(f"❌ {r['URL']} - Error de conexión.")
        else:
            badge_color = "#10b981" if r['Seguridad'] == "Segura" else "#ef4444"
            st.markdown(f"""
                <div class="res-card">
                    <b style="color:#38bdf8; font-size:1.1rem;">🔗 {r['URL']}</b>
                    <span class="status-badge" style="background:{badge_color}; color:white;">{r['Seguridad']}</span>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top:10px;">
                        <div><p style="margin:0; font-size:0.8rem; color:#94a3b8;">📧 Emails:</p><span style="color:white;">{r.get('Emails', 'N/A')}</span></div>
                        <div><p style="margin:0; font-size:0.8rem; color:#94a3b8;">📞 Teléfonos:</p><span style="color:white;">{r.get('Teléfonos', 'N/A')}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.write("---")
st.caption("DataSocio Engine v16.0 | Tidy Data & PDF Export")
