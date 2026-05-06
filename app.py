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
    :root { --primary: #38bdf8; --bg: #0f172a; --card: #1e293b; --danger: #ef4444; --admin: #10b981; }
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--bg); }
    
    /* Prólogo en Login */
    .hero-section {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        padding: 2.5rem; border-radius: 20px; border: 1px solid #334155;
        text-align: center; margin-bottom: 2rem;
    }

    /* Botones y Sidebar */
    .stButton button { border-radius: 8px !important; }
    .logout-btn button { background-color: var(--danger) !important; color: white !important; }
    .clear-btn button { background-color: #475569 !important; color: white !important; }
    
    /* Tarjetas de Resultados */
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

# --- BASE DE DATOS LOCAL ---
# Recuerda agregar 'usuarios_db.json' a tu .gitignore para privacidad
db = TinyDB('usuarios_db.json')
User = Query()
def hash_p(password): return hashlib.sha256(str.encode(password)).hexdigest()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'last_run' not in st.session_state: st.session_state.last_run = []

# --- PANTALLA DE LOGIN ---
if not st.session_state.logged_in:
    st.markdown("""
        <div class="hero-section">
            <h1 style='color: #38bdf8;'>DataSocio Intelligence OS</h1>
            <p style='color: #cbd5e1;'>Motor de extracción masiva y análisis de reputación comercial.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: st.info("🔍 **Inyección**: Cargue URLs masivas.")
    with col2: st.info("⚡ **Rastreo**: Extracción en tiempo real.")
    with col3: st.info("📊 **Dataset**: Exportación directa a CSV.")

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

# --- VALIDACIÓN DE SUPERPODERES ---
user_data = db.search(User.username == st.session_state.user_now)[0]
is_admin = (st.session_state.user_now == "Cabecha305")

# --- INTERFAZ OPERATIVA (SIDEBAR) ---
with st.sidebar:
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("⬅️ FINALIZAR SESIÓN", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    if is_admin:
        st.markdown(f"### 👑 `ADMIN: {st.session_state.user_now}`")
        st.success("✨ Modo Dios: Créditos Infinitos")
    else:
        st.markdown(f"### 👤 `Operador: {st.session_state.user_now}`")
        st.metric("CRÉDITOS", user_data['credits'])
    
    st.write("---")
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("🧹 LIMPIAR CONSULTA", use_container_width=True):
        st.session_state.last_run = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL CENTRAL ---
st.title("🛠️ Consola de Inteligencia")

col_in, col_opt = st.columns([2, 1])
with col_in:
    urls_input = st.text_area("📋 Lista de objetivos (URLs):", height=150, placeholder="Pega aquí las URLs una por línea...")

with col_opt:
    st.markdown("🎯 **Filtros de Extracción**")
    c_mail = st.checkbox("Extraer Emails", value=True)
    c_tel = st.checkbox("Extraer Teléfonos", value=True)
    c_ssl = st.checkbox("Verificar Seguridad SSL", value=True)

if st.button("⚡ EJECUTAR ESCANEO DE PRECISIÓN", use_container_width=True):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
    
    # Verificación de créditos (Los Admin saltan esta valla)
    puede_operar = is_admin or (user_data['credits'] >= len(urls))
    
    if urls and puede_operar:
        results = []
        progress = st.progress(0)
        for i, url in enumerate(urls):
            try:
                # Solo descuenta créditos si no eres Admin
                if not is_admin:
                    nuevos_creditos = user_data['credits'] - 1
                    db.update({'credits': nuevos_creditos}, User.username == st.session_state.user_now)
                    user_data['credits'] = nuevos_creditos # Actualizar variable local
                
                # Proceso de extracción
                r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                soup = BeautifulSoup(r.text, 'html.parser')
                text = soup.get_text()
                
                res_obj = {"url": url, "secure": url.startswith("https")}
                if c_mail: res_obj["emails"] = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
                if c_tel: res_obj["tels"] = list(set(re.findall(r'\+?\d{10,13}', text)))
                results.append(res_obj)
            except:
                results.append({"url": url, "error": "Inalcanzable"})
            
            progress.progress((i+1)/len(urls))
        
        st.session_state.last_run = results
        st.rerun()
    elif not puede_operar:
        st.error("❌ Créditos insuficientes para esta operación.")

# --- RENDERIZADO DE RESULTADOS ---
if st.session_state.last_run:
    st.write("---")
    st.subheader("💎 Inteligencia Obtenida")
    
    # Exportación
    df = pd.DataFrame(st.session_state.last_run)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 DESCARGAR DATASET (CSV)", csv, "reporte_datasocio.csv", "text/csv")

    for r in st.session_state.last_run:
        if "error" in r:
            st.error(f"❌ {r['url']} - No se pudo establecer conexión.")
        else:
            badge_color = "#10b981" if r['secure'] else "#ef4444"
            st.markdown(f"""
                <div class="res-card">
                    <b style="color:#38bdf8; font-size:1.1rem;">🔗 {r['url']}</b>
                    <span class="status-badge" style="background:{badge_color}; color:white;">{'SEGURA' if r['secure'] else 'NO SEGURA'}</span>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top:10px;">
                        <div>
                            <p style="margin:0; font-size:0.8rem; color:#94a3b8;">📧 Emails Detectados:</p>
                            <span style="color:white; font-family:monospace;">{", ".join(r['emails']) if r.get('emails') else 'Ninguno'}</span>
                        </div>
                        <div>
                            <p style="margin:0; font-size:0.8rem; color:#94a3b8;">📞 Contacto Telefónico:</p>
                            <span style="color:white; font-family:monospace;">{", ".join(r['tels']) if r.get('tels') else 'Ninguno'}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.write("---")
st.caption("DataSocio Engine v13.0 | Operación: Paso del Rey | Sistema: Win11 i5")
