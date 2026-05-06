import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import hashlib
import io
from tinydb import TinyDB, Query
from fpdf import FPDF

# --- CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="DataSocio Intelligence OS", page_icon="⚡", layout="wide")

# Clave secreta para firmar transacciones y evitar fraudes (Cambiá esto por cualquier frase larga)
SECRET_PAY_KEY = "DATASOCIO_SECURITY_TOKEN_2026"

# Estilos CSS de Alta Fidelidad (Mantenidos y consolidados)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    :root { 
        --primary: #38bdf8; 
        --bg: #0f172a; 
        --card: #1e293b; 
        --danger: #ef4444; 
        --admin: #10b981; 
    }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--bg); }
    .prologo-section { background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%); padding: 1.5rem; border-radius: 15px; border: 1px solid #334155; margin-bottom: 2rem; }
    .res-card { background: var(--card); padding: 20px; border-radius: 12px; border-left: 6px solid var(--primary); margin-bottom: 15px; }
    .status-badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; margin-left: 12px; text-transform: uppercase; }
    .ad-slot { background: #0f172a; border: 1px dashed #334155; padding: 12px; border-radius: 10px; text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 15px; }
    .pack-card { background: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 12px; text-align: center; transition: all 0.2s; }
    .pack-card:hover { border-color: var(--primary); transform: translateY(-2px); }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS LOCAL ---
db = TinyDB('usuarios_db.json')
User = Query()
def hash_p(p): return hashlib.sha256(str.encode(p)).hexdigest()

# Generador y verificador de firmas de pago para evitar fraudes por URL
def generar_firma_pago(usuario, credits_qty):
    token_source = f"{usuario}-{credits_qty}-{SECRET_PAY_KEY}"
    return hashlib.sha256(token_source.encode()).hexdigest()

# --- DETECTOR AUTOMÁTICO DE PAGOS (WEBHOOK REDIRECT) ---
# Se ejecuta al inicio para acreditar al usuario si viene de pagar exitosamente
query_params = st.query_params
if "payment" in query_params and query_params["payment"] == "success":
    pay_user = query_params.get("user")
    pay_credits = query_params.get("credits")
    pay_sig = query_params.get("sig")
    
    # Validamos que la firma de la URL coincida con nuestra clave secreta
    if pay_user and pay_credits and pay_sig:
        firma_esperada = generar_firma_pago(pay_user, pay_credits)
        if pay_sig == firma_esperada:
            # Firma válida -> Acreditamos créditos de forma segura
            user_entry = db.search(User.username == pay_user)
            if user_entry:
                nuevos_creditos = user_entry[0]['credits'] + int(pay_credits)
                db.update({'credits': nuevos_creditos}, User.username == pay_user)
                st.success(f"¡Pago Aprobado! Se acreditaron {pay_credits} créditos a {pay_user}.")
                st.balloons()
            # Limpiamos los parámetros de la URL para evitar recargas fraudulentas
            st.query_params.clear()

# Estados de sesión estándar
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'last_run' not in st.session_state: st.session_state.last_run = []
if 'input_key' not in st.session_state: st.session_state.input_key = 0

# --- PANTALLA DE LOGIN ---
if not st.session_state.logged_in:
    st.markdown('<div style="text-align:center; margin-top:50px;"><h1 style="color: #38bdf8; font-size:3rem;">DataSocio OS</h1><p style="color:#94a3b8;">SaaS Engine v19.0</p></div>', unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        u = st.text_input("Operador").strip()
        p = st.text_input("Contraseña", type="password").strip()
        if st.button("🚀 INGRESAR AL SISTEMA", use_container_width=True):
            res = db.search(User.username == u)
            if res and res[0]['password'] == hash_p(p):
                st.session_state.logged_in, st.session_state.user_now = True, u
                st.rerun()
            else: st.error("Acceso denegado.")
    st.stop()

# Recuperar datos del usuario logueado
user_data = db.search(User.username == st.session_state.user_now)[0]
is_admin = (st.session_state.user_now == "Cabecha305")

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("⚡ DataSocio Pro")
    menu = st.radio("Navegación", ["🔍 Escáner Inteligente", "💳 Cargar Créditos", "📊 Reportes"])
    st.write("---")
    st.metric("CRÉDITOS DISPONIBLES", "INFINITOS 👑" if is_admin else user_data['credits'])
    
    # Sección Publicitaria Estructurada
    st.markdown("""
        <div class="ad-slot">
            <span style="color:#38bdf8; font-weight:bold;">📢 SocioAds</span><br>
            ¿Querés publicitar tu marca acá?<br>
            <a href="mailto:ads@datasocio.com" style="color:#38bdf8; text-decoration:none;">Contacto Directo</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    if st.button("⬅️ FINALIZAR SESIÓN", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- SECCIÓN: ESCÁNER INTELIGENTE (DEEP SCAN) ---
if menu == "🔍 Escáner Inteligente":
    st.title("🛠️ Consola Operativa de Inteligencia")
    
    st.markdown("""
        <div class="prologo-section">
            <h4 style='color: #38bdf8; margin-top:0;'>Bienvenido al Motor de Extracción Avanzado</h4>
            <p style='color: #cbd5e1; font-size: 0.95rem; margin:0;'>Pegue las URLs objetivo. El sistema escaneará emails, perfiles de Instagram y números de WhatsApp locales.</p>
        </div>
    """, unsafe_allow_html=True)

    col_in, col_opt = st.columns([2, 1])
    with col_in:
        urls_input = st.text_area("📋 Inyectar URLs (una por línea):", height=180, placeholder="https://ejemplo.com", key=f"urls_{st.session_state.input_key}")
    with col_opt:
        st.markdown("### 🎯 Parámetros de Extracción")
        c_mail = st.checkbox("Extraer Emails", value=True)
        c_wa = st.checkbox("Extraer WhatsApp", value=True)
        c_ig = st.checkbox("Extraer Instagram", value=True)

    # Botones
    col_run, col_clean = st.columns([2, 1])
    with col_run:
        if st.button("⚡ EJECUTAR ESCANEO DE PRECISIÓN", use_container_width=True):
            urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
            if urls and (is_admin or user_data['credits'] >= len(urls)):
                results = []
                progress = st.progress(0)
                for i, url in enumerate(urls):
                    try:
                        if not is_admin:
                            nuevos_creditos = user_data['credits'] - 1
                            db.update({'credits': nuevos_creditos}, User.username == st.session_state.user_now)
                            user_data['credits'] = nuevos_creditos
                        
                        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, timeout=8)
                        soup = BeautifulSoup(r.text, 'html.parser')
                        text = soup.get_text()
                        
                        res_obj = {"URL": url, "Seguridad": "Segura" if url.startswith("https") else "No Segura"}
                        
                        if c_mail: 
                            emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
                            res_obj["Emails"] = ", ".join(emails) if emails else "Ninguno"
                        if c_wa:
                            # Patrón para enlaces y números directos de WhatsApp
                            tels_wa = list(set(re.findall(r'wa\.me/(\d+)', r.text) + re.findall(r'phone=(\d+)', r.text)))
                            res_obj["WhatsApp"] = ", ".join(tels_wa) if tels_wa else "Ninguno"
                        if c_ig:
                            # Patrón para perfiles de Instagram detectados en el código de la página
                            ig_profiles = list(set(re.findall(r'instagram\.com/([^/?"\s>]+)', r.text)))
                            res_obj["Instagram"] = ", ".join(ig_profiles) if ig_profiles else "Ninguno"
                        
                        results.append(res_obj)
                    except:
                        results.append({"URL": url, "Error": "Inalcanzable"})
                    progress.progress((i+1)/len(urls))
                st.session_state.last_run = results
                st.rerun()
            elif not urls:
                st.warning("Ingrese al menos una URL válida.")
            else:
                st.error("Créditos insuficientes. Por favor, recargue su saldo.")

    with col_clean:
        if st.button("🧹 LIMPIAR ESCÁNER", use_container_width=True):
            st.session_state.last_run = []
            st.session_state.input_key += 1
            st.rerun()

    # --- RENDERIZADO Y EXPORTACIÓN ---
    if st.session_state.last_run:
        st.write("---")
        st.subheader("💎 Datos Extraídos")
        
        # Desglose Tidy Data para Excel/CSV (Mantenido)
        export_list = []
        for r in st.session_state.last_run:
            if "Error" in r: continue
            url, sec = r['URL'], r['Seguridad']
            ems = r.get('Emails', '').split(', ') if r.get('Emails') != 'Ninguno' else []
            was = r.get('WhatsApp', '').split(', ') if r.get('WhatsApp') != 'Ninguno' else []
            igs = r.get('Instagram', '').split(', ') if r.get('Instagram') != 'Ninguno' else []
            
            if not ems and not was and not igs:
                export_list.append({'URL': url, 'Seguridad': sec, 'Tipo': 'N/A', 'Contacto': 'Sin Datos'})
            for e in ems: export_list.append({'URL': url, 'Seguridad': sec, 'Tipo': 'Email', 'Contacto': e})
            for w in was: export_list.append({'URL': url, 'Seguridad': sec, 'Tipo': 'WhatsApp', 'Contacto': w})
            for ig in igs: export_list.append({'URL': url, 'Seguridad': sec, 'Tipo': 'Instagram', 'Contacto': ig})
                
        df_export = pd.DataFrame(export_list)

        col_ex, col_csv = st.columns(2)
        with col_ex:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df_export.to_excel(wr, index=False)
            st.download_button("📥 EXPORTAR EXCEL (.xlsx)", buf, "contactos.xlsx", use_container_width=True)
        with col_csv:
            st.download_button("📥 EXPORTAR CSV (.csv)", df_export.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig'), "contactos.csv", use_container_width=True)

        for r in st.session_state.last_run:
            if "Error" in r:
                st.error(f"❌ {r['URL']} - Inalcanzable")
            else:
                badge = "#10b981" if r['Seguridad'] == "Segura" else "#ef4444"
                st.markdown(f"""
                    <div class="res-card">
                        <b>🔗 {r['URL']}</b> <span class="status-badge" style="background:{badge}; color:white;">{r['Seguridad']}</span><br>
                        <div style="margin-top: 10px; display: flex; gap: 15px;">
                            <span>📧 Emails: <b>{r.get('Emails','-')}</b></span>
                            <span>💬 WA: <b>{r.get('WhatsApp','-')}</b></span>
                            <span>📸 IG: <b>{r.get('Instagram','-')}</b></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# --- SECCIÓN: CARGAR CRÉDITOS (AUTOMATIZADO) ---
elif menu == "💳 Cargar Créditos":
    st.title("💳 Recarga Automática de Créditos")
    st.info("Elegí tu pack. Los pagos se procesan en ARS de forma segura y se acreditan automáticamente en tu Naranja X.")
    
    col1, col2, col3 = st.columns(3)
    
    # Firma criptográfica para cada pack del usuario actual
    sig_p1 = generar_firma_pago(st.session_state.user_now, "500")
    sig_p2 = generar_firma_pago(st.session_state.user_now, "2000")
    sig_p3 = generar_firma_pago(st.session_state.user_now, "10000")
    
    # URL de retorno de tu app en Streamlit Cloud (Socio-redirección)
    app_url = "https://datasocio.streamlit.app"  # Reemplazar por la URL real de tu app cuando esté online
    
    with col1:
        st.markdown("""
            <div class="pack-card">
                <h3>Pack Starter</h3>
                <h2 style="color:#38bdf8;">$2.500 ARS</h2>
                <p><b>500 Créditos</b></p>
                <p style="font-size:0.8rem; color:#94a3b8;">Ideal para validaciones rápidas.</p>
            </div>
        """, unsafe_allow_html=True)
        # Link de Checkout Mobbex/Dlocal (con parámetros de auto-retorno seguros)
        mobbex_link_1 = f"https://mobbex.com/p/checkout/xxxx?return_url={app_url}?payment=success%26user={st.session_state.user_now}%26credits=500%26sig={sig_p1}"
        st.link_button("🛒 COMPRAR PACK", mobbex_link_1, use_container_width=True)
        
    with col2:
        st.markdown("""
            <div class="pack-card" style="border-color:#38bdf8;">
                <h3>Pack Business</h3>
                <h2 style="color:#10b981;">$8.000 ARS</h2>
                <p><b>2.000 Créditos</b></p>
                <p style="font-size:0.8rem; color:#94a3b8;">La opción más elegida por agencias.</p>
            </div>
        """, unsafe_allow_html=True)
        mobbex_link_2 = f"https://mobbex.com/p/checkout/xxxx?return_url={app_url}?payment=success%26user={st.session_state.user_now}%26credits=2000%26sig={sig_p2}"
        st.link_button("🔥 COMPRAR RECOMENDADO", mobbex_link_2, use_container_width=True)
        
    with col3:
        st.markdown("""
            <div class="pack-card">
                <h3>Pack Pro-Scale</h3>
                <h2 style="color:#ef4444;">$30.000 ARS</h2>
                <p><b>10.000 Créditos</b></p>
                <p style="font-size:0.8rem; color:#94a3b8;">Para minería de datos a gran escala.</p>
            </div>
        """, unsafe_allow_html=True)
        mobbex_link_3 = f"https://mobbex.com/p/checkout/xxxx?return_url={app_url}?payment=success%26user={st.session_state.user_now}%26credits=10000%26sig={sig_p3}"
        st.link_button("🚀 COMPRAR ILIMITADO", mobbex_link_3, use_container_width=True)

# --- SECCIÓN: REPORTES (MANTENIDA) ---
elif menu == "📊 Reportes":
    st.title("📊 Estadísticas de Operación")
    st.write("Historial y rendimiento del operador.")
    # (Aquí va la lógica de métricas que usemos más adelante)
