import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
import hashlib
from io import BytesIO
from tinydb import TinyDB, Query

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DataSocio OS | Elite Intelligence", page_icon="⚡", layout="wide")

# CSS para darle vida, humanidad y elegancia
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    /* Header & Prólogo */
    .hero-section {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 3rem; border-radius: 20px; border: 1px solid #38bdf8;
        text-align: center; margin-bottom: 2rem;
    }
    
    /* Tarjetas de Beneficios */
    .feature-card {
        background: rgba(30, 41, 59, 0.7);
        padding: 1.5rem; border-radius: 15px;
        border: 1px solid #334155; text-align: center; height: 100%;
    }

    /* Tarjetas de Resultados (Vista Humana) */
    .result-card {
        background: #1e293b; padding: 1.5rem; border-radius: 12px;
        border-left: 6px solid #38bdf8; margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #38bdf8, #1d4ed8);
        color: white; border: none; font-weight: bold; border-radius: 8px;
    }
    .pay-link {
        display: block; padding: 12px; background: #10b981;
        color: white; text-decoration: none; border-radius: 8px;
        text-align: center; font-weight: bold; margin-top: 15px;
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

# --- PANTALLA DE INICIO (PRÓLOGO + LOGIN) ---
if not st.session_state.logged_in:
    # 1. EL PRÓLOGO (LA VITRINA)
    st.markdown("""
        <div class="hero-section">
            <h1 style='color: #38bdf8; font-size: 3.5rem;'>DataSocio Intelligence OS</h1>
            <p style='font-size: 1.4rem; color: #94a3b8;'>La herramienta definitiva para potenciar tu red de contactos y analizar mercados en segundos.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown('<div class="feature-card"><h2>🔍</h2><h3>Extracción Pro</h3><p>Rastrea emails y teléfonos reales sin vueltas.</p></div>', unsafe_allow_html=True)
    with col_f2:
        st.markdown('<div class="feature-card"><h2>🧠</h2><h3>Análisis de IA</h3><p>Detecta el sentimiento y reputación de cada sitio.</p></div>', unsafe_allow_html=True)
    with col_f3:
        st.markdown('<div class="feature-card"><h2>📊</h2><h3>Reportes Listos</h3><p>Exporta todo a Excel profesional en un clic.</p></div>', unsafe_allow_html=True)

    st.write("---")

    # 2. EL ACCESO (DISCRETO Y ELEGANTE)
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<h3 style='text-align:center;'>🔐 Panel de Acceso</h3>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])
        
        with tab1:
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.button("🚀 ENTRAR AL SISTEMA"):
                res = db.search(User.username == u)
                if res and res[0]['password'] == hash_p(p):
                    st.session_state.logged_in = True
                    st.session_state.user_now = u
                    st.rerun()
                else: st.error("Error en credenciales.")
        
        with tab2:
            u_reg = st.text_input("Nuevo Usuario")
            p_reg = st.text_input("Nueva Contraseña", type="password")
            if st.button("🎁 CREAR MI CUENTA"):
                if not db.search(User.username == u_reg):
                    db.insert({'username': u_reg, 'password': hash_p(p_reg), 'credits': 10})
                    st.success("¡Listo! Ya podés ingresar.")
                else: st.error("Ese usuario ya existe.")
    st.stop()

# --- INTERFAZ OPERATIVA (USUARIO LOGUEADO) ---
user_rec = db.search(User.username == st.session_state.user_now)[0]

with st.sidebar:
    st.title(f"👤 {st.session_state.user_now}")
    st.metric("TUS CRÉDITOS", user_rec['credits'])
    st.write("---")
    st.markdown("### 🚀 Subir de Nivel")
    st.write("Obtené escaneos ilimitados y soporte prioritario.")
    st.markdown('<a href="#" class="pay-link">💳 SUSCRIBIRSE PRO</a>', unsafe_allow_html=True)
    st.write("")
    if st.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

# --- CUERPO PRINCIPAL ---
st.markdown("<h1 style='color: #38bdf8;'>🚀 Consola de Operaciones</h1>", unsafe_allow_html=True)

# Banner de publicidad/cooperación
st.info("📢 **¿Querés cooperar con el proyecto?** Tu marca puede aparecer aquí ante cientos de socios. Contactanos.")

with st.expander("🛠️ CONFIGURAR ESCANEO", expanded=True):
    urls_input = st.text_area("📋 Inyectar URLs (una por línea):", height=100)
    if st.button("⚡ INICIAR INTELIGENCIA"):
        urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
        if not urls:
            st.warning("Ingrese objetivos válidos.")
        elif len(urls) > user_rec['credits']:
            st.error("No tenés créditos suficientes.")
        else:
            results = []
            progress_bar = st.progress(0)
            for i, url in enumerate(urls):
                try:
                    db.update({'credits': user_rec['credits'] - 1}, User.username == st.session_state.user_now)
                    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    text = soup.get_text()
                    emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
                    tels = list(set(re.findall(r'\+?\d{10,13}', text)))
                    
                    results.append({
                        "url": url,
                        "emails": emails,
                        "tels": tels,
                        "sentimiento": "Positivo ⭐" if "excelente" in text.lower() else "Neutral ⚖️"
                    })
                    progress_bar.progress((i+1)/len(urls))
                except:
                    results.append({"url": url, "emails": [], "tels": [], "sentimiento": "Error ❌"})
            st.session_state.last_run = results

# --- VISTA HUMANA DE RESULTADOS ---
if 'last_run' in st.session_state:
    st.write("### 💎 Hallazgos de Inteligencia")
    
    for res in st.session_state.last_run:
        with st.container():
            st.markdown(f"""
                <div class="result-card">
                    <h4>🔗 {res['url']}</h4>
                    <p><b>📧 Emails:</b> {', '.join(res['emails']) if res['emails'] else 'No encontrados'}</p>
                    <p><b>📞 Teléfonos:</b> {', '.join(res['tels']) if res['tels'] else 'No encontrados'}</p>
                    <p><b>🛡️ Reputación:</b> {res['sentimiento']}</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Botón de Descarga
    df_export = pd.DataFrame(st.session_state.last_run)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 DESCARGAR BASE DE DATOS (Excel)",
        data=output.getvalue(),
        file_name="DataSocio_Intelligence.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.write("---")
st.caption("DataSocio Engine v9.1 | Powered by i5 Win11 | Argentina")
