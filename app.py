import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time

# 1. Configuración de la página
st.set_page_config(page_title="DataSocio Monetizer | Pro Edition", page_icon="💰", layout="wide")

# Estilo de Interfaz Premium (Negro y Dorado/Verde)
st.markdown("""
    <style>
    .stApp { background-color: #0a0a0a; color: #d4af37; } /* Dorado sobre negro */
    .stTextArea textarea { background-color: #1a1a1a; color: #00ff41; border: 1px solid #d4af37; }
    .stButton>button {
        background: linear-gradient(90deg, #d4af37, #f9e29b);
        color: black; font-weight: bold; border-radius: 5px; border: none;
    }
    .payment-card {
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #d4af37;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Lógica de Créditos (Simulada para el prototipo)
if 'user_credits' not in st.session_state:
    st.session_state.user_credits = 5  # Créditos iniciales de regalo

# 3. Barra Lateral: TIENDA DE CRÉDITOS
with st.sidebar:
    st.title("💰 CENTRO DE PAGOS")
    st.metric(label="Tus Créditos Actuales", value=st.session_state.user_credits)
    
    st.write("---")
    st.subheader("Obtener más Poder")
    
    # Opción 1: Pack Básico
    st.markdown('<div class="payment-card"><b>Pack Starter</b><br>50 Consultas<br><b>$9.99 USD</b></div>', unsafe_allow_html=True)
    if st.button("Comprar 50 Créditos"):
        # Aquí pondrías el link real de Stripe: st.write("Redirigiendo a Stripe...")
        st.success("Redirigiendo a pasarela segura...")
        time.sleep(1)
        st.session_state.user_credits += 50 # Simulación de compra exitosa
    
    # Opción 2: Pack Pro
    st.markdown('<div class="payment-card"><b>Pack Business</b><br>500 Consultas<br><b>$39.99 USD</b></div>', unsafe_allow_html=True)
    if st.button("Comprar 500 Créditos"):
        st.success("Redirigiendo a PayPal...")
        time.sleep(1)
        st.session_state.user_credits += 500

    st.write("---")
    st.caption("Pagos procesados por Stripe®")

# 4. Cuerpo Principal
st.title("💎 DATASOCIO MONETIZER")
st.write("Extrae activos de alto valor. Cada consulta consume 1 crédito.")

if st.session_state.user_credits <= 0:
    st.error("❌ Te has quedado sin créditos. Por favor, adquiere un pack en la barra lateral.")
else:
    urls_input = st.text_area("📋 Lista de objetivos (URLs):", height=100)

    if st.button("🔥 EJECUTAR EXTRACCIÓN MAESTRA"):
        lista_urls = [url.strip() for url in urls_input.split('\n') if url.strip().startswith('http')]
        
        if not lista_urls:
            st.warning("Introduce objetivos válidos.")
        elif len(lista_urls) > st.session_state.user_credits:
            st.error(f"No tienes suficientes créditos para {len(lista_urls)} URLs. Tienes {st.session_state.user_credits}.")
        else:
            all_data = []
            progreso = st.progress(0)
            
            for idx, url in enumerate(lista_urls):
                try:
                    # Descontar crédito por cada URL procesada
                    st.session_state.user_credits -= 1
                    
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0'}
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        texto = soup.get_text()
                        links = [a['href'] for a in soup.find_all('a', href=True)]
                        
                        # Extracción rápida
                        whatsapp = list(set(re.findall(r'\+?\d{10,13}', texto) + [l for l in links if "wa.me" in l]))
                        emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', texto)))
                        prices = list(set(re.findall(r'[\$\€]\s?\d+(?:[\.,]\d+)?', texto)))

                        all_data.append({
                            "URL": url,
                            "WhatsApp/Tel": ", ".join(whatsapp[:3]),
                            "Emails": ", ".join(emails[:3]),
                            "Precios": ", ".join(prices[:3])
                        })
                    
                    progreso.progress(int((idx + 1) / len(lista_urls) * 100))
                    
                except Exception as e:
                    st.error(f"Error en {url}")

            if all_data:
                st.success(f"Extracción finalizada. Créditos restantes: {st.session_state.user_credits}")
                st.dataframe(pd.DataFrame(all_data), use_container_width=True)
                
                csv = pd.DataFrame(all_data).to_csv(index=False).encode('utf-8')
                st.download_button("📥 DESCARGAR ACTIVOS", csv, "extraccion_paga.csv", "text/csv")

# 5. Footer Técnico
st.write("---")
st.caption("Infraestructura: i5 / Win 11 | Secure Payment Protocol Enabled")