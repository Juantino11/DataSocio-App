import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import hashlib
import time
from tinydb import TinyDB, Query

# --- CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="DataSocio Pro | Intelligence", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    :root { --primary: #38bdf8; --bg: #0f172a; --card: #1e293b; --danger: #ef4444; }
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--bg); }
    
    /* Prólogo en Login */
    .hero-section {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        padding: 2.5rem; border-radius: 20px; border: 1px solid #334155;
        text-align: center; margin-bottom: 2rem;
    }

    /* Botón de Salida y Limpieza */
    .stButton button { border-radius: 8px !important; }
    .logout-btn button { background-color: var(--danger) !important; color: white !important; }
    .clear-btn button { background-color: #475569 !important; color: white !important; }
    
    /* Tarjetas de Resultados Corregidas */
    .res-card {
        background: var(--card); padding: 20px; border-radius: 12px;
        border-left: 6px solid var(--primary); margin-bottom: 15px;
        position: relative;
    }
    .status-badge {
        display: inline-block; padding: 2px 8px; border-radius: 4px;
        font-size: 0.7rem; font-weight: bold; margin-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
db = TinyDB('usuarios_db.json')
User = Query()
def hash_p(password): return hashlib.sha256(str.encode(password)).hexdigest()

# Inicialización de estados
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'last_run' not in st.session_state: st.session_state.last_run = []

# --- PANTALLA DE LOGIN CON PRÓLOGO ---
if not st.session_state.logged_in:
    st.markdown("""
        <div class="hero-section">
            <h1 style='color: #38bdf8;'>DataSocio Intelligence OS</h1>
            <p style='color: #cbd5e1;'>Motor de extracción masiva y análisis de reputación comercial.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: st.info("🔍 **Inyección**: Cargue URLs masivas.")
    with col2: st.info("⚡ **Rastreo**: Extracción de datos en tiempo real.")
    with col3: st.info("📊 **Dataset**: Exportación directa a CSV/Excel.")

    st.write("---")
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
            else: st.error("Acceso denegado")
    st.stop()

# --- INTERFAZ OPERATIVA ---
user_data = db.search(User.username == st.session_state.user_now)[0]

with st.sidebar:
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("⬅️ FINALIZAR SESIÓN", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"### 👤 `{st.session_state.user_now}`")
    st.metric("CRÉDITOS", user_data['credits'])
    st.write("---")
    
    # BOTÓN PARA LIMPIAR RESULTADOS
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("🧹 LIMPIAR CONSULTA", use_container_width=True):
        st.session_state.last_run = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.title("🛠️ Consola de Inteligencia")

col_in, col_opt = st.columns([2, 1])
with col_in:
    urls_input = st.text_area("📋 Lista de objetivos (URLs):", height=150, placeholder="https://ejemplo.com")

with col_opt:
    st.markdown("🎯 **Filtros Activos**")
    c_mail = st.checkbox("Emails", value=True)
    c_tel = st.checkbox("Teléfonos", value=True)
    c_ssl = st.checkbox("Seguridad SSL", value=True)

if st.button("⚡ EJECUTAR ESCANEO", use_container_width=True):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
    if urls and user_data['credits'] >= len(urls):
        results = []
        progress = st.progress(0)
        for i, url in enumerate(urls):
            try:
                # Cobro de crédito
                db.update({'credits': user_data['credits'] - (i+1)}, User.username == st.session_state.user_now)
                
                r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                soup = BeautifulSoup(r.text, 'html.parser')
                text = soup.get_text()
                
                res_obj = {"url": url, "secure": url.startswith("https")}
                if c_mail: res_obj["emails"] = ", ".join(list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))))
                if c_tel: res_obj["tels"] = ", ".join(list(set(re.findall(r'\+?\d{10,13}', text))))
                results.append(res_obj)
            except:
                results.append({"url": url, "error": "Inalcanzable"})
            progress.progress((i+1)/len(urls))
        st.session_state.last_run = results
        st.rerun()

# --- RESULTADOS Y EXPORTACIÓN ---
if st.session_state.last_run:
    st.write("---")
    st.subheader("💎 Inteligencia Obtenida")
    
    # Exportación Optimizada (Cadenas en lugar de Listas para Excel)
    df = pd.DataFrame(st.session_state.last_run)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 DESCARGAR CSV", csv, "reporte_datasocio.csv", "text/csv")

    for r in st.session_state.last_run:
        if "error" in r:
            st.error(f"❌ {r['url']} - Error de conexión")
        else:
            badge_color = "#10b981" if r['secure'] else "#ef4444"
            badge_text = "SEGURA" if r['secure'] else "NO SEGURA"
            
            st.markdown(f"""
                <div class="res-card">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <b style="color:#38bdf8; font-size:1.1rem;">🔗 {r['url']}</b>
                        <span class="status-badge" style="background:{badge_color}; color:white;">{badge_text}</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <p style="margin:0; font-size:0.9rem; color:#94a3b8;">📧 <b>Emails:</b><br><span style="color:white;">{r.get('emails', 'N/A')}</span></p>
                        <p style="margin:0; font-size:0.9rem; color:#94a3b8;">📞 <b>Teléfonos:</b><br><span style="color:white;">{r.get('tels', 'N/A')}</span></p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.write("---")
st.caption(f"DataSocio Engine v11.0 | Win11 i5 | Paso del Rey")
