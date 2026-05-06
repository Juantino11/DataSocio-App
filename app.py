import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import hashlib
from tinydb import TinyDB, Query

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DataSocio Pro | Intelligence", page_icon="⚡", layout="wide")

# CSS para mantener la estética Pro
st.markdown("""
    <style>
    :root { --primary: #38bdf8; --bg: #0f172a; --card: #1e293b; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--bg); color: white; }
    .res-card { background: var(--card); padding: 20px; border-radius: 12px; border-left: 6px solid var(--primary); margin-bottom: 15px; }
    .stButton button { border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- DB Y SESIÓN ---
db = TinyDB('usuarios_db.json')
User = Query()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'last_run' not in st.session_state: st.session_state.last_run = []

# --- LOGIN (PRÓLOGO) ---
if not st.session_state.logged_in:
    st.title("⚡ DataSocio Intelligence OS")
    _, col_login, _ = st.columns([1, 1, 1])
    with col_login:
        u = st.text_input("Operador").strip()
        p = st.text_input("Contraseña", type="password").strip()
        if st.button("🚀 ACCEDER", use_container_width=True):
            res = db.search(User.username == u)
            if res and res[0]['password'] == hashlib.sha256(p.encode()).hexdigest():
                st.session_state.logged_in = True
                st.session_state.user_now = u
                st.rerun()
    st.stop()

# --- INTERFAZ DE CONSULTA ---
user_data = db.search(User.username == st.session_state.user_now)[0]

with st.sidebar:
    if st.button("⬅️ SALIR", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown(f"### 👤 `{st.session_state.user_now}`")
    st.metric("CRÉDITOS", user_data['credits'])
    if st.button("🧹 LIMPIAR TODO", use_container_width=True):
        st.session_state.last_run = []
        st.rerun()

st.title("🛠️ Consola de Extracción Limpia")
urls_input = st.text_area("📋 Inyectar URLs:", height=150, placeholder="https://ejemplo.com")

if st.button("⚡ EJECUTAR ESCANEO DE PRECISIÓN", use_container_width=True):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
    if urls and user_data['credits'] >= len(urls):
        raw_results = []
        for url in urls:
            try:
                db.update({'credits': user_data['credits'] - 1}, User.username == st.session_state.user_now)
                r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                soup = BeautifulSoup(r.text, 'html.parser')
                text = soup.get_text()
                
                mails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
                tels = list(set(re.findall(r'\+?\d{10,13}', text)))
                
                # REGLA DE ORO: Si hay varios mails, creamos una fila por cada uno para que en Excel quede uno abajo del otro
                if not mails:
                    raw_results.append({"URL": url, "Email": "No detectado", "Teléfono": tels[0] if tels else "N/A"})
                else:
                    for m in mails:
                        raw_results.append({
                            "URL": url,
                            "Email": m,
                            "Teléfono": tels[0] if tels else "N/A" # Tomamos el principal
                        })
            except:
                raw_results.append({"URL": url, "Email": "ERROR", "Teléfono": "ERROR"})
        
        st.session_state.last_run = raw_results
        st.rerun()

# --- EXPORTACIÓN PROLIJA ---
if st.session_state.last_run:
    df = pd.DataFrame(st.session_state.last_run)
    
    st.subheader("💎 Resultados Optimizados para Excel")
    
    # Botón de descarga corregido: usamos Excel (.xlsx) en lugar de CSV para asegurar el orden
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DataSocio_Report')
    
    st.download_button(
        label="📥 DESCARGAR REPORTE PROFESIONAL (EXCEL)",
        data=output.getvalue(),
        file_name=f"reporte_{st.session_state.user_now}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Visualización en pantalla
    for url in df['URL'].unique():
        sub_df = df[df['URL'] == url]
        st.markdown(f"""
            <div class="res-card">
                <b style="color:#38bdf8;">🔗 {url}</b><br>
                <p style="margin:5px 0; font-size:0.9rem;">
                Mails encontrados: {len(sub_df)}<br>
                Listado: {", ".join(sub_df['Email'].tolist())}
                </p>
            </div>
        """, unsafe_allow_html=True)

st.caption("DataSocio Engine v12.0 | Formato Atómico de Datos")
