import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import hashlib
import io
from tinydb import TinyDB, Query

# --- CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="DataSocio Pro | Intelligence", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    :root { --primary: #38bdf8; --bg: #0f172a; --card: #1e293b; --danger: #ef4444; --admin: #10b981; }
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--bg); }
    
    /* Login Minimalista */
    .login-header {
        text-align: center; margin-bottom: 2rem; padding: 2rem;
        background: var(--card); border-radius: 15px; border: 1px solid #334155;
    }

    /* Prólogo Interno */
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

# --- PANTALLA DE LOGIN (MINIMALISTA Y DIRECTA) ---
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

# --- VALIDACIÓN DE USUARIO (MODO DIOS) ---
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

# --- PANEL CENTRAL (CON PRÓLOGO INCLUIDO) ---
st.title("🛠️ Consola de Inteligencia")

# El Prólogo ahora vive aquí adentro
st.markdown("""
    <div class="prologo-section">
        <h4 style='color: #38bdf8; margin-top:0;'>Bienvenido al Motor de Extracción</h4>
        <p style='color: #cbd5e1; font-size: 0.9rem;'>Siga los pasos para procesar datos de forma masiva y exportarlos limpios.</p>
    </div>
""", unsafe_allow_html=True)

col_p1, col_p2, col_p3 = st.columns(3)
with col_p1: st.info("1️⃣ **Inyección**: Cargue URLs.")
with col_p2: st.info("2️⃣ **Rastreo**: Extraiga datos.")
with col_p3: st.info("3️⃣ **Dataset**: Exporte a Excel/CSV.")
st.write("---")

# Consola Operativa
col_in, col_opt = st.columns([2, 1])
with col_in:
    urls_input = st.text_area("📋 Inyectar URLs (una por línea):", height=150, placeholder="https://ejemplo.com")

with col_opt:
    st.markdown("🎯 **Objetivos de Análisis**")
    c_mail = st.checkbox("Extraer Emails", value=True)
    c_tel = st.checkbox("Extraer Teléfonos", value=True)
    c_ssl = st.checkbox("Verificar SSL", value=True)

# Botones agrupados
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

# --- RENDERIZADO Y DESCARGA PROFESIONAL ---
if st.session_state.last_run:
    st.write("---")
    st.subheader("💎 Inteligencia Obtenida")
    
    df = pd.DataFrame(st.session_state.last_run)

    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        # Excel: Requiere 'xlsxwriter' en requirements.txt
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Extracción')
        st.download_button("📥 DESCARGAR EXCEL (.xlsx)", buffer, "reporte_datasocio.xlsx", "application/vnd.ms-excel", use_container_width=True)

    with col_dl2:
        # CSV: Punto y coma para Excel Español
        csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 DESCARGAR CSV (.csv)", csv, "reporte_datasocio.csv", "text/csv", use_container_width=True)

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
st.caption("DataSocio Engine v15.0 | Diseño UI/UX Mobile First")
