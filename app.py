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
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    :root { --primary: #38bdf8; --bg: #0f172a; --card: #1e293b; }
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stMetric { background: var(--card); padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    
    /* Botón de Salida Pro */
    .stButton button { transition: all 0.3s; }
    .logout-btn button { background-color: #ef4444 !important; color: white !important; border: none !important; }
    
    /* Tarjetas de Resultados */
    .res-card {
        background: var(--card); padding: 25px; border-radius: 15px;
        border-left: 8px solid var(--primary); margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .status-tag {
        padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
db = TinyDB('usuarios_db.json')
User = Query()
def hash_p(password): return hashlib.sha256(str.encode(password)).hexdigest()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_now = None

# --- ACCESO / LOGIN ---
if not st.session_state.logged_in:
    # (Mantener el prólogo visual que ya tenías aquí...)
    st.title("⚡ DataSocio Intelligence OS")
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        u = st.text_input("Usuario").strip()
        p = st.text_input("Contraseña", type="password").strip()
        if st.button("🚀 INICIAR OPERACIONES", use_container_width=True):
            res = db.search(User.username == u)
            if res and res[0]['password'] == hash_p(p):
                st.session_state.logged_in = True
                st.session_state.user_now = u
                st.rerun()
            else: st.error("Acceso Denegado")
    st.stop()

# --- SIDEBAR (Funciones de Usuario) ---
user_data = db.search(User.username == st.session_state.user_now)[0]

with st.sidebar:
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("⬅️ FINALIZAR SESIÓN", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"### ⚡ Operador: `{st.session_state.user_now}`")
    st.metric("CRÉDITOS DISPONIBLES", user_data['credits'])
    
    st.write("---")
    st.write("🔍 **Historial Rápido**")
    # Función objetiva: Ver últimas URLs procesadas
    st.caption("Próximamente: Log de auditoría")

# --- CONSOLA OPERATIVA PRO ---
st.markdown("## 🛠️ Panel de Extracción e Inteligencia")

col_in, col_opt = st.columns([2, 1])

with col_in:
    urls_input = st.text_area("📋 Inyectar URLs (una por línea):", height=150)

with col_opt:
    st.write("🎯 **Objetivos de Análisis**")
    check_mail = st.checkbox("Extraer Emails", value=True)
    check_tel = st.checkbox("Extraer Teléfonos", value=True)
    check_security = st.checkbox("Verificar SSL/Seguridad", value=True)

if st.button("⚡ EJECUTAR ESCANEO DE PRECISIÓN", use_container_width=True):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
    
    if urls and user_data['credits'] >= len(urls):
        results = []
        progress_text = st.empty()
        bar = st.progress(0)
        
        for i, url in enumerate(urls):
            progress_text.text(f"Escaneando objetivo {i+1}/{len(urls)}: {url}")
            try:
                # Actualizar créditos
                new_credits = user_data['credits'] - 1
                db.update({'credits': new_credits}, User.username == st.session_state.user_now)
                
                # Request con Timeout y Seguridad
                start_time = time.time()
                r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                scan_time = round(time.time() - start_time, 2)
                
                soup = BeautifulSoup(r.text, 'html.parser')
                text = soup.get_text()
                
                # Inteligencia Objetiva
                data = {"url": url, "time": f"{scan_time}s", "secure": url.startswith("https")}
                if check_mail:
                    data["emails"] = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
                if check_tel:
                    data["tels"] = list(set(re.findall(r'\+?\d{10,13}', text)))
                
                results.append(data)
            except Exception as e:
                results.append({"url": url, "error": "Inalcanzable"})
            
            bar.progress((i+1)/len(urls))
        
        st.session_state.last_run = results
        st.rerun()

# --- VISUALIZACIÓN DE DATOS OBJETIVA ---
if 'last_run' in st.session_state:
    st.write("### 💎 Inteligencia Obtenida")
    
    # Función Objetiva: Exportar a Excel/CSV
    df_export = pd.DataFrame(st.session_state.last_run)
    csv = df_export.to_csv(index=False).encode('utf-8')
    st.download_button("📥 DESCARGAR DATASET (CSV)", csv, "extraccion_datasocio.csv", "text/csv")
    
    for r in st.session_state.last_run:
        if "error" in r:
            st.error(f"❌ {r['url']} - Error de conexión")
        else:
            secure_icon = "🟢 Segura" if r['secure'] else "🔴 No Segura"
            st.markdown(f"""
                <div class="res-card">
                    <div style="display:flex; justify-content:space-between;">
                        <h4 style="margin:0; color:#38bdf8;">🔗 {r['url']}</h4>
                        <span class="status-tag" style="background:#064e3b; color:#10b981;">{secure_icon}</span>
                    </div>
                    <div style="margin-top:15px; display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                        <div>
                            <p style="color:#94a3b8; margin:0;">📧 Emails Detectados:</p>
                            <code style="color:white;">{", ".join(r['emails']) if r.get('emails') else "Nulo"}</code>
                        </div>
                        <div>
                            <p style="color:#94a3b8; margin:0;">📞 Contacto Directo:</p>
                            <code style="color:white;">{", ".join(r['tels']) if r.get('tels') else "Nulo"}</code>
                        </div>
                    </div>
                    <p style="margin-top:10px; font-size:0.7rem; color:#475569;">Latencia de escaneo: {r['time']}</p>
                </div>
            """, unsafe_allow_html=True)

st.write("---")
st.caption("DataSocio Engine v10.0 | Win11 i5 | Paso del Rey")
