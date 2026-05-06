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

# CSS para darle vida y monetizar
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    /* Banners y Publicidad */
    .ad-banner {
        background: linear-gradient(90deg, #1e293b, #334155);
        padding: 10px; border-radius: 10px; border: 1px dashed #38bdf8;
        text-align: center; margin-bottom: 20px; font-size: 0.8rem; color: #94a3b8;
    }
    
    /* Panel de Control */
    .op-card {
        background: #1e293b; padding: 2rem; border-radius: 15px;
        border: 1px solid #1e4ed8; box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    
    /* Botones Premium */
    .stButton>button {
        background: linear-gradient(90deg, #38bdf8, #1d4ed8);
        color: white; border: none; font-weight: bold; border-radius: 8px; width: 100%;
    }
    .pay-button {
        display: inline-block; padding: 10px 20px; background: #10b981;
        color: white; text-decoration: none; border-radius: 8px; font-weight: bold;
        text-align: center; width: 100%; margin-top: 10px;
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

# --- LÓGICA DE ACCESO (PANTALLA DE INICIO) ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#38bdf8;'>DataSocio Intelligence OS</h1>", unsafe_allow_html=True)
    
    _, col_auth, _ = st.columns([1, 1.3, 1])
    with col_auth:
        mode = st.radio("Socio, elige tu entrada:", ["Ingresar", "Registrarse"], horizontal=True)
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        
        if mode == "Ingresar" and st.button("ACCEDER AL COMANDO"):
            res = db.search(User.username == u)
            if res and res[0]['password'] == hash_p(p):
                st.session_state.logged_in = True
                st.session_state.user_now = u
                st.rerun()
            else: st.error("Acceso denegado.")
        
        if mode == "Registrarse" and st.button("UNIRSE A LA RED"):
            if not db.search(User.username == u):
                db.insert({'username': u, 'password': hash_p(p), 'credits': 10})
                st.success("¡Bienvenido! Ya podés ingresar.")
            else: st.error("Usuario ya registrado.")
    st.stop()

# --- INTERFAZ OPERATIVA (USUARIO LOGUEADO) ---
user_rec = db.search(User.username == st.session_state.user_now)[0]

# --- SIDEBAR MONETIZADA ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_now}")
    st.metric("CRÉDITOS DISPONIBLES", user_rec['credits'])
    
    st.markdown("---")
    st.markdown("### 💎 PLAN PREMIUM")
    st.write("¿Te quedaste sin créditos? Potenciá tu alcance.")
    # ENLACE DE PAGO (Aquí podrías poner tu link de Mercado Pago o PayPal)
    st.markdown('<a href="https://tu-enlace-de-pago.com" target="_blank" class="pay-button">💳 COMPRAR 100 CRÉDITOS</a>', unsafe_allow_html=True)
    
    st.write("")
    if st.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.markdown("---")
    st.write("💡 *Sugerencia: El análisis de sentimiento ahorra 2 horas de trabajo manual.*")

# --- CUERPO PRINCIPAL ---

# Espacio para Publicidad (Top)
st.markdown('<div class="ad-banner">🚀 ESPACIO PUBLICITARIO DISPONIBLE - Contacta con DataSocio para anunciar aquí 🚀</div>', unsafe_allow_html=True)

st.title("⚡ Centro de Extracción de Datos")

with st.container():
    st.markdown('<div class="op-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        urls_input = st.text_area("📋 Inyectar URLs (una por línea):", height=150, placeholder="https://ejemplo.com.ar")
    
    with col2:
        st.write("### ⚙️ Parámetros")
        deep_scan = st.checkbox("Escaneo Profundo", value=True)
        get_sentiment = st.checkbox("Analizar Reputación", value=True)
        st.write("---")
        if st.button("⚡ EJECUTAR OPERACIÓN"):
            urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
            if not urls:
                st.warning("⚠️ Sin objetivos válidos.")
            elif len(urls) > user_rec['credits']:
                st.error("❌ Créditos insuficientes.")
            else:
                results = []
                bar = st.progress(0)
                
                for i, url in enumerate(urls):
                    try:
                        db.update({'credits': user_rec['credits'] - 1}, User.username == st.session_state.user_now)
                        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                        soup = BeautifulSoup(r.text, 'html.parser')
                        text = soup.get_text()
                        
                        emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
                        tels = list(set(re.findall(r'\+?\d{10,13}', text)))
                        
                        results.append({
                            "OBJETIVO": url,
                            "CONTACTOS": f"📧 {len(emails)} | 📞 {len(tels)}",
                            "EMAILS": ", ".join(emails),
                            "REPUTACIÓN": "⭐ Positiva" if "excelente" in text.lower() else "⚖️ Neutral"
                        })
                        bar.progress((i+1)/len(urls))
                    except:
                        results.append({"OBJETIVO": url, "CONTACTOS": "Error", "EMAILS": "-", "REPUTACIÓN": "-"})

                if results:
                    st.session_state.last_results = results
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- RESULTADOS CON ESTILO ---
if 'last_results' in st.session_state:
    st.write("### 📊 Reporte de Inteligencia")
    df = pd.DataFrame(st.session_state.last_results)
    st.table(df) # Usamos tabla para que se vea más sólido
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='DataSocio_Leads')
    
    st.download_button(
        label="📥 EXPORTAR BASE DE DATOS PROFESIONAL",
        data=output.getvalue(),
        file_name=f"Reporte_Elite_{st.session_state.user_now}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.write("---")
st.caption(f"DataSocio Engine v9.0 | Windows 11 i5 | Paso del Rey, Argentina")
