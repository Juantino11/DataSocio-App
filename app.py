import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import hashlib
import io
from tinydb import TinyDB, Query

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DataSocio Intelligence OS", page_icon="⚡", layout="wide")

# Diseño UI Dark Premium
st.markdown("""
    <style>
    :root { --primary: #38bdf8; --bg: #0f172a; --card: #1e293b; }
    html, body, [class*="css"] { background-color: var(--bg); color: white; }
    .stButton button { border-radius: 8px !important; font-weight: bold; background: #38bdf8; color: black; transition: 0.3s; }
    .stButton button:hover { background: #0ea5e9; transform: scale(1.02); }
    .price-card { 
        background: var(--card); padding: 25px; border-radius: 15px; 
        border: 1px solid #334155; text-align: center; height: 100%;
    }
    .price-card h3 { color: #38bdf8; margin-bottom: 10px; }
    .price-tag { font-size: 2rem; font-weight: bold; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
db = TinyDB('usuarios_db.json')
User = Query()
def hash_p(p): return hashlib.sha256(str.encode(p)).hexdigest()

# Auto-Admin
if len(db.all()) == 0:
    db.insert({'username': 'Cabecha305', 'password': hash_p('Catonas305!'), 'credits': 999999, 'plan': 'Admin'})

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>⚡ DataSocio Pro</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1.2,1])
    with col:
        u = st.text_input("Operador").strip()
        p = st.text_input("Acceso", type="password").strip()
        if st.button("ACCEDER"):
            res = db.search(User.username == u)
            if res and res[0]['password'] == hash_p(p):
                st.session_state.logged_in, st.session_state.user_now = True, u
                st.rerun()
    st.stop()

# Datos del usuario logueado
current_user = db.search(User.username == st.session_state.user_now)[0]
is_admin = (st.session_state.user_now == "Cabecha305")

# --- SIDEBAR ---
with st.sidebar:
    st.title("DataSocio OS")
    menu = st.radio("Módulos", ["🔍 Inteligencia", "💎 Cargar Créditos"])
    st.write("---")
    st.metric("CRÉDITOS DISPONIBLES", "∞" if is_admin else current_user['credits'])
    if st.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

# --- MÓDULO: INTELIGENCIA ---
if menu == "🔍 Inteligencia":
    st.title("Extracción de Datos de Precisión")
    urls_input = st.text_area("URLs a escanear (una por línea):", height=200)
    
    if st.button("🚀 INICIAR ESCANEO"):
        urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
        if not is_admin and len(urls) > current_user['credits']:
            st.error("Créditos insuficientes para esta cantidad de URLs.")
        elif urls:
            results = []
            bar = st.progress(0)
            for i, url in enumerate(urls):
                try:
                    if not is_admin:
                        db.update({'credits': current_user['credits'] - 1}, User.username == st.session_state.user_now)
                    
                    r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                    soup = BeautifulSoup(r.text, 'html.parser')
                    t = soup.get_text()
                    results.append({
                        "URL": url,
                        "WhatsApp": list(set(re.findall(r'wa\.me/(\d+)', r.text))),
                        "Instagram": list(set(re.findall(r'instagram\.com/([^/?"\s>]+)', r.text))),
                        "Emails": list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', t)))
                    })
                except: results.append({"URL": url, "Error": "Inalcanzable"})
                bar.progress((i + 1) / len(urls))
            
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Descargar CSV", df.to_csv(index=False).encode('utf-8-sig'), "data.csv")

# --- MÓDULO: CARGAR CRÉDITOS (AUTOMÁTICO) ---
elif menu == "💎 Cargar Créditos":
    st.title("Carga Automática de Créditos")
    st.write("Seleccioná un pack. Los créditos se acreditarán al instante después del pago.")
    
    c1, c2, c3 = st.columns(3)
    
    packs = [
        {"id": "p1", "name": "Pack Bronce", "creds": 500, "price": 2500},
        {"id": "p2", "name": "Pack Plata", "creds": 2000, "price": 8000},
        {"id": "p3", "name": "Pack Oro", "creds": 10000, "price": 30000},
    ]
    
    for i, col in enumerate([c1, c2, c3]):
        with col:
            st.markdown(f"""
            <div class="price-card">
                <h3>{packs[i]['name']}</h3>
                <div class="price-tag">${packs[i]['price']}</div>
                <p><b>{packs[i]['creds']}</b> Créditos</p>
                <p><small>Acreditación Instantánea</small></p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Comprar {packs[i]['creds']} CR", key=packs[i]['id']):
                st.info("Generando link de pago seguro...")
                # Aquí irá la URL de Mobbex una vez creada la cuenta
                st.link_button("🚀 PAGAR AHORA", "https://mobbex.com/p/checkout/ejemplo")
