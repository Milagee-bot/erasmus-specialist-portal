import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests
import threading
from datetime import date, timedelta

# --- Page config ---
st.set_page_config(
    page_title="Erasmus+ Specialisto Portalas",
    page_icon="🇪🇺",
    layout="centered"
)

# --- Styling ---
st.markdown("""
<style>
    .main-header {
        background: #003399;
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 24px;
    }
    .dalyvis-card {
        background: #f0f4ff;
        border-left: 4px solid #003399;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    .statusas-nauja { color: #2e7d32; font-weight: bold; }
    .statusas-kita { color: #666; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h2>🇪🇺 Erasmus+ Specialisto Portalas</h2><p>Mobilumo duomenų įvedimas</p></div>', unsafe_allow_html=True)

# --- Config ---
SHEETS_ID = "1DPSsv1b71nVWRA_N0xqSaoclqTDwcMq0CtGknWJvBIM"
WEBHOOK_URL = "http://localhost:5678/webhook/9e941ae8-9a88-4e2c-975c-29263ef651a7"
WEBHOOK_URL_2 = "http://localhost:5678/webhook/257879b9-9a60-4a7d-871b-674361458808"
CREDENTIALS_FILE = "credentials.json"

# --- Google Sheets prisijungimas ---
@st.cache_resource
def get_sheets_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def load_dalyviai():
    try:
        client = get_sheets_client()
        sheet = client.open_by_key(SHEETS_ID).worksheet("Dalyviai")
        data = sheet.get_all_records()
        return data
    except Exception as e:
        st.error(f"Klaida jungiантis prie Google Sheets: {e}")
        return []

# --- Dalyvių sąrašas ---
dalyviai = load_dalyviai()

if not dalyviai:
    st.warning("⚠️ Dalyvių nerasta arba nepavyko prisijungti prie Google Sheets.")
    st.stop()

# Filtruoti tik tuos kurie dar neturi sutarties
pasirenkamieji = dalyviai

if not pasirenkamieji:
    st.info("ℹ️ Šiuo metu nėra dalyvių laukiančių mobilumo duomenų.")
    st.stop()

# --- Dalyvio pasirinkimas ---
st.subheader("1️⃣ Pasirinkite dalyvį")

dalyvis_opcijos = {
    f"{d['Vardas']} {d['Pavardė']} — {d.get('Mokymosi programa / specialybė', '')} ({d.get('Statusas', 'Nauja')})": d
    for d in pasirenkamieji
}

pasirinktas_label = st.selectbox(
    "Dalyvis:",
    options=list(dalyvis_opcijos.keys()),
    index=0
)

dalyvis = dalyvis_opcijos[pasirinktas_label]

# Rodyti dalyvio info
with st.expander("📋 Dalyvio informacija", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Vardas, pavardė:** {dalyvis['Vardas']} {dalyvis['Pavardė']}")
        st.write(f"**El. paštas:** {dalyvis.get('El. pašto adresas', '')}")
        st.write(f"**Programa:** {dalyvis.get('Mokymosi programa / specialybė', '')}")
    with col2:
        st.write(f"**Grupė:** {dalyvis.get('Grupė ir kursas', '')}")
        st.write(f"**Anglų lygis:** {dalyvis.get('Anglų kalbos lygis', '')}")
        st.write(f"**Statusas:** {dalyvis.get('Statusas', 'Nauja')}")

st.divider()

# --- Mobilumo duomenų forma ---
st.subheader("2️⃣ Įveskite mobilumo duomenis")

with st.form("mobilumo_forma"):
    col1, col2 = st.columns(2)

    with col1:
        salis = st.selectbox("Šalis", [
            "Austrija", "Belgija", "Bulgarija", "Čekija", "Danija",
            "Estija", "Suomija", "Prancūzija", "Vokietija", "Graikija",
            "Vengrija", "Airija", "Italija", "Latvija", "Lenkija",
            "Nyderlandai", "Norvegija", "Portugalija", "Rumunija",
            "Slovakija", "Slovėnija", "Ispanija", "Švedija", "Kita"
        ])
        miestas = st.text_input("Miestas *", placeholder="pvz. Barselona")
        organizacija = st.text_input("Priimančios organizacijos pavadinimas *", placeholder="pvz. ABC Training Center")
        org_adresas = st.text_input("Priimančios organizacijos adresas *", placeholder="pvz. Calle Mayor 1")

    with col2:
        pradzia = st.date_input("Mobilumo pradžios data *", value=date.today() + timedelta(days=30))
        pabaiga = st.date_input("Mobilumo pabaigos data *", value=date.today() + timedelta(days=58))
        keliones_dienos = st.number_input("Kelionės dienų skaičius", min_value=1, max_value=4, value=2)

    st.divider()

    col3, col4 = st.columns(2)
    with col3:
        individuali_parama = st.number_input("Individuali parama (EUR) *", min_value=0.0, value=0.0, step=10.0)
    with col4:
        keliones_parama = st.number_input("Kelionės parama (EUR) *", min_value=0.0, value=0.0, step=10.0)

    # Automatinis skaičiavimas
    if pradzia and pabaiga:
        mobilumo_dienos = (pabaiga - pradzia).days + 1
        bendra_trukme = mobilumo_dienos + keliones_dienos
        bendra_dotacija = individuali_parama + keliones_parama

        st.info(f"📊 Mobilumo dienų: **{mobilumo_dienos}** | Bendra trukmė: **{bendra_trukme}** dienų | Bendra dotacija: **{bendra_dotacija:.2f} EUR**")

    papildomos_pastabos = st.text_area("Papildomos pastabos (neprivaloma)", placeholder="Jei reikia — įrašykite papildomą informaciją")

    submitted = st.form_submit_button("📤 Pateikti informaciją", use_container_width=True, type="primary")

# --- Siųsti į Webhook ---
if submitted:
    if not miestas or not organizacija or not org_adresas:
        st.error("⚠️ Prašome užpildyti visus privalomus laukus!")
    elif individuali_parama == 0 or keliones_parama == 0:
        st.error("⚠️ Prašome įvesti paramos sumas!")
    elif pabaiga <= pradzia:
        st.error("⚠️ Pabaigos data turi būti vėlesnė už pradžios datą!")
    else:
        mobilumo_dienos = (pabaiga - pradzia).days + 1
        bendra_trukme = mobilumo_dienos + keliones_dienos
        bendra_dotacija = individuali_parama + keliones_parama

        payload = {
            # Dalyvio duomenys
            "vardas": dalyvis.get("Vardas", ""),
            "pavarde": dalyvis.get("Pavardė", ""),
            "el_pastas": dalyvis.get("El. pašto adresas", ""),
            "gimimo_data": dalyvis.get("Gimimo data", ""),
            "adresas": dalyvis.get("Adresas (gatvė, miestas, pašto kodas)", ""),
            "telefonas": dalyvis.get("Telefono numeris", ""),
            "banko_saskaita": dalyvis.get("Banko sąskaitos numeris (IBAN)", ""),
            "banko_pavadinimas": dalyvis.get("Banko pavadinimas", ""),
            "programa": dalyvis.get("Mokymosi programa / specialybė", ""),
            "grupe": dalyvis.get("Grupė ir kursas", ""),
            "anglu_lygis": dalyvis.get("Anglų kalbos lygis", ""),
            # Mobilumo duomenys
            "salis": salis,
            "miestas": miestas,
            "organizacija": organizacija,
            "org_adresas": org_adresas,
            "mobilumo_pradzia": str(pradzia),
            "mobilumo_pabaiga": str(pabaiga),
            "mobilumo_dienos": mobilumo_dienos,
            "keliones_dienos": keliones_dienos,
            "bendra_trukme": bendra_trukme,
            "individuali_parama": individuali_parama,
            "keliones_parama": keliones_parama,
            "bendra_dotacija": bendra_dotacija,
            "pastabos": papildomos_pastabos,
        }

        with st.spinner("Siunčiama informacija..."):
            try:
                response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
                thread = threading.Thread(target=lambda: requests.post(WEBHOOK_URL_2, json=payload, timeout=60))
                thread.daemon = True
                thread.start()
                if response.status_code == 200:
                    st.success(f"✅ Informacija sėkmingai pateikta! Sutartis bus sugeneruota automatiškai.")
                    st.balloons()
                    st.cache_data.clear()
                else:
                    st.error(f"⚠️ Klaida siunčiant duomenis: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Nepavyko prisijungti prie n8n. Patikrinkite ar n8n veikia.")
            except Exception as e:
                st.error(f"⚠️ Klaida: {e}")
