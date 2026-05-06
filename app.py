import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import hashlib
import io
from tinydb import TinyDB, Query

# --- CONFIGURACIÓN DE IDENTIDAD ---
st.set_page_config(page_title="DataSocio Intelligence OS", page_icon="⚡", layout="wide")

# --- DISEÑO UI PRO ---
st.markdown("""
    <style>
    :root { --primary: #38bdf8; --bg: #0f172a; }
    .res-card { background: #1e293b; padding: 15px; border-radius: 12px; border-left: 5px solid var(--primary); margin-bottom: 10px; }
    .stButton button { border-radius: 8px !important; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS Y SEGURIDAD ---
db = TinyDB('usuarios_db.json')
User = Query()

def hash_p(p): 
    return hashlib.sha256(str.encode(p)).hexdigest()

# 🔥 SOLUCIÓN DEFINITIVA: Auto-creación del Admin si la base está vacía
if len(db.all()) == 0:
    db.insert({
        'username': 'Cabecha305',
        'password': hash_p('Catonas305!'),
        'credits': 999999,
        'plan': 'Admin'
    })

# --- ESTADO DE SESIÓN ---
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False
if 'last_run' not in st.session_state: 
    st.session_state.last_run = []

# --- INTERFAZ DE LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>⚡ DataSocio Pro</h1>", unsafe_allow_html=True)
    with st.container():
        _, col, _ = st.columns([1,1.2,1])
        with col:
            u = st.text_input("Operador Autorizado").strip()
            p = st.text_input("Código de Acceso", type="password").strip()
            if st.button("ACCEDER AL SISTEMA"):
                res = db.search(User.username == u)
                if res and res[0]['password'] == hash_p(p):
                    st.session_state.logged_in = True
                    st.session_state.user_now = u
                    st.rerun()
                else: 
                    st.error("Acceso denegado. Verifique credenciales.")
    st.stop()

# --- PANEL PRINCIPAL (Solo si está logueado) ---
user_data = db.search(User.username == st.session_state.user_now)[0]
is_admin = (st.session_state.user_now == "Cabecha305")

with st.sidebar:
    st.title("DataSocio OS")
    menu = st.radio("Módulos", ["🔍 Inteligencia", "💎 Suscripción"])
    st.write("---")
    st.metric("Créditos", "Infinitos" if is_admin else user_data['credits'])
    if st.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

# --- MÓDULO INTELIGENCIA ---
if menu == "🔍 Inteligencia":
    st.subheader("Extracción de Datos de Precisión")
    urls_input = st.text_area("Ingrese URLs (una por línea):", height=150, placeholder="https://ejemplo.com")
    
    if st.button("🚀 INICIAR ESCANEO"):
        urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
        if not urls:
            st.warning("Por favor, ingrese URLs válidas que comiencen con http o https.")
        else:
            results = []
            progress_bar = st.progress(0)
            
            for i, url in enumerate(urls):
                try:
                    # Descuento de créditos (solo para no-admins)
                    if not is_admin:
                        db.update({'credits': user_data['credits'] - 1}, User.username == st.session_state.user_now)
                    
                    response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text_content = soup.get_text()
                    html_content = response.text
                    
                    # Extracción optimizada
                    emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text_content)))
                    whatsapp = list(set(re.findall(r'wa\.me/(\d+)', html_content) + re.findall(r'whatsapp\.com/send\?phone=(\d+)', html_content)))
                    instagram = list(set(re.findall(r'instagram\.com/([^/?"\s>]+)', html_content)))
                    
                    results.append({
                        "URL": url,
                        "Emails": emails,
                        "WhatsApp": whatsapp,
                        "Instagram": instagram
                    })
                except Exception as e:
                    results.append({"URL": url, "Error": "Inalcanzable u ocurrió un error"})
                
                progress_bar.progress((i + 1) / len(urls))
            
            st.session_state.last_run = results
            st.success(f"Escaneo finalizado: {len(urls)} URLs procesadas.")

    # Visualización y Exportación de Resultados
    if st.session_state.last_run:
        df = pd.DataFrame(st.session_state.last_run)
        st.dataframe(df)
        
        col1, col2 = st.columns(2)
        
        # Botón CSV
        csv_data = df.to_csv(index=False).encode('utf-8-sig')
        col1.download_button("📥 Descargar Reporte (CSV)", csv_data, "reporte_datasocio.csv", "text/csv")
        
        # Botón Excel (Manejo de errores si xlsxwriter falla)
        try:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            col2.download_button("📥 Descargar Reporte (Excel)", excel_buffer.getvalue(), "reporte_datasocio.xlsx")
        except:
            col2.info("Exportación a Excel no disponible en este entorno. Utilice CSV.")

elif menu == "💎 Suscripción":
    st.title("Planes y Créditos")
    st.info("Módulo de integración con Naranja X / Mobbex en desarrollo.")
