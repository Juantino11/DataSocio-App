import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import hashlib
import io
from tinydb import TinyDB, Query

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DataSocio Pro | Intelligence OS", page_icon="⚡", layout="wide")

# Estilos Pro (Modern Dark Mode)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    :root { --primary: #38bdf8; --bg: #0f172a; --card: #1e293b; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--bg); color: white; }
    .res-card { 
        background: var(--card); padding: 20px; border-radius: 15px; 
        border: 1px solid #334155; border-left: 6px solid var(--primary);
        margin-bottom: 15px;
    }
    .stButton button { border-radius: 10px !important; font-weight: bold; width: 100%; }
    .ad-banner {
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        padding: 15px; border-radius: 10px; border: 1px dashed #38bdf8;
        text-align: center; margin: 10px 0; font-size: 0.8rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
db = TinyDB('usuarios_db.json')
User = Query()
def hash_p(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- ESTADO DE SESIÓN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'last_run' not in st.session_state: st.session_state.last_run = []

# --- LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#38bdf8;'>⚡ DataSocio Pro</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1.2,1])
    with col:
        u = st.text_input("Operador Autorizado").strip()
        p = st.text_input("Código de Acceso", type="password").strip()
        if st.button("ACCEDER AL SISTEMA"):
            res = db.search(User.username == u)
            if res and res[0]['password'] == hash_p(p):
                st.session_state.logged_in, st.session_state.user_now = True, u
                st.rerun()
            else: st.error("Acceso denegado. Verifique credenciales.")
    st.stop()

# Datos del usuario actual
user_data = db.search(User.username == st.session_state.user_now)[0]
is_admin = (st.session_state.user_now == "Cabecha305")

# --- SIDEBAR ---
with st.sidebar:
    st.title("DataSocio OS")
    menu = st.radio("MÓDULOS", ["🔍 Inteligencia", "💎 Suscripción", "📊 Configuración"])
    st.write("---")
    st.metric("CRÉDITOS", "∞" if is_admin else user_data['credits'])
    st.markdown('<div class="ad-banner">🚀 <b>ESPACIO PUBLICITARIO</b><br>Monetizá tu tráfico aquí</div>', unsafe_allow_html=True)
    if st.button("SALIR"):
        st.session_state.logged_in = False
        st.rerun()

# --- MÓDULO: INTELIGENCIA ---
if menu == "🔍 Inteligencia":
    st.title("Consola de Extracción Profunda")
    
    col_in, col_opt = st.columns([2, 1])
    with col_in:
        urls_input = st.text_area("Inyectar URLs (una por línea):", height=180, placeholder="https://ejemplo.com")
    
    with col_opt:
        st.markdown("### 🎯 Filtros")
        c_mail = st.checkbox("Extraer Emails", value=True)
        c_wa = st.checkbox("Extraer WhatsApp (AR)", value=True)
        c_ig = st.checkbox("Extraer Instagram", value=True)

    if st.button("⚡ INICIAR ESCANEO DE PRECISIÓN"):
        urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
        if not urls:
            st.warning("Por favor, ingrese URLs válidas.")
        elif not is_admin and user_data['credits'] < len(urls):
            st.error("Créditos insuficientes para esta operación.")
        else:
            results = []
            progress_bar = st.progress(0)
            
            for i, url in enumerate(urls):
                try:
                    # Descuento de créditos
                    if not is_admin:
                        db.update({'credits': user_data['credits'] - 1}, User.username == st.session_state.user_now)
                    
                    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    text = soup.get_text()
                    html = r.text
                    
                    data = {"URL": url}
                    if c_mail:
                        data["Emails"] = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
                    if c_wa:
                        # Busca wa.me y formatos comunes de Argentina
                        data["WhatsApp"] = list(set(re.findall(r'wa\.me/(\d+)', html) + re.findall(r'\+?54\s?9?\s?(\d{10,12})', text)))
                    if c_ig:
                        data["Instagram"] = list(set(re.findall(r'instagram\.com/([^/?"\s>]+)', html)))
                    
                    results.append(data)
                except Exception as e:
                    results.append({"URL": url, "Error": str(e)})
                
                progress_bar.progress((i + 1) / len(urls))
            
            st.session_state.last_run = results
            st.success(f"Escaneo finalizado: {len(urls)} procesadas.")

    # Visualización y Exportación
    if st.session_state.last_run:
        df = pd.DataFrame(st.session_state.last_run)
        
        st.write("---")
        col_down1, col_down2 = st.columns(2)
        
        # Exportación corregida para evitar errores de motor
        csv = df.to_csv(index=False).encode('utf-8-sig')
        col_down1.download_button("📥 DESCARGAR DATASET (CSV)", data=csv, file_name="reporte_datasocio.csv", mime="text/csv")
        
        try:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Extracción')
            col_down2.download_button("📥 DESCARGAR EXCEL (XLSX)", data=output.getvalue(), file_name="reporte_datasocio.xlsx")
        except:
            col_down2.info("Excel no disponible. Use CSV (más rápido).")

        for r in st.session_state.last_run:
            with st.container():
                st.markdown(f"""
                <div class="res-card">
                    <b>🔗 {r['URL']}</b><br>
                    <small>📧 Emails: {', '.join(r.get('Emails', ['-']))}</small><br>
                    <small>💬 WhatsApp: {', '.join(r.get('WhatsApp', ['-']))}</small><br>
                    <small>📸 Instagram: {', '.join(r.get('Instagram', ['-']))}</small>
                </div>
                """, unsafe_allow_html=True)

# --- MÓDULO: SUSCRIPCIÓN ---
elif menu == "💎 Suscripción":
    st.title("Planes y Créditos")
    st.info("Sistema de automatización para Naranja X mediante Mobbex.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Pack Starter")
        st.write("500 Créditos / $2.500 ARS")
        st.button("Comprar Pack 1")
    with c2:
        st.subheader("Pack Business")
        st.write("2.000 Créditos / $8.000 ARS")
        st.button("Comprar Pack 2")
    with c3:
        st.subheader("Pack Pro")
        st.write("10.000 Créditos / $30.000 ARS")
        st.button("Comprar Pack 3")

st.write("---")
st.caption("DataSocio v18.4 | Engine: Deep Scan AR | Optimizado para i5 Windows 11")
