import streamlit as st
import psycopg2
import requests
import os
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()

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
        border-radius: 10px;
        text-align: center;
        margin-bottom: 24px;
    }
    .participant-card {
        background: #f0f4ff;
        border: 1px solid #c0d0ff;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #28a745;
        border-radius: 8px;
        padding: 16px;
        color: #155724;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 12px;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# --- DB Connection ---
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "erasmus_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "")
    )

# --- Fetch participants without contract ---
def get_pending_participants():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, first_name, last_name, email, study_programme, 
                   group_year, english_level, created_at
            FROM erasmus_participants
            WHERE status = 'New' OR contract_number IS NULL OR contract_number = ''
            ORDER BY created_at DESC
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        st.error(f"Duomenų bazės klaida: {e}")
        return []

# --- Send to n8n webhook ---
def send_to_n8n(data):
    webhook_url = os.getenv("N8N_WEBHOOK_URL", "")
    if not webhook_url:
        st.error("N8N_WEBHOOK_URL nenustatytas!")
        return False
    try:
        response = requests.post(webhook_url, json=data, timeout=30)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Webhook klaida: {e}")
        return False

# --- COUNTRIES with grant rates ---
COUNTRIES = {
    "Danija": {"rate": 106, "travel": 309},
    "Vokietija": {"rate": 99, "travel": 309},
    "Ispanija": {"rate": 88, "travel": 309},
    "Prancūzija": {"rate": 99, "travel": 309},
    "Italija": {"rate": 93, "travel": 309},
    "Suomija": {"rate": 99, "travel": 309},
    "Švedija": {"rate": 99, "travel": 309},
    "Nyderlandai": {"rate": 99, "travel": 309},
    "Austrija": {"rate": 99, "travel": 309},
    "Kita": {"rate": 99, "travel": 309},
}

# =====================
# MAIN APP
# =====================

st.markdown("""
<div class="main-header">
    <h2 style="margin:0;">🇪🇺 Erasmus+ Specialisto Portalas</h2>
    <p style="margin:4px 0 0; opacity:0.85;">Klaipėdos Ernesto Galvanausko PMC</p>
</div>
""", unsafe_allow_html=True)

# --- Fetch participants ---
participants = get_pending_participants()

if not participants:
    st.markdown("""
    <div class="warning-box">
        Šiuo metu nėra mokinių laukiančių mobilumo duomenų.
        Kai mokiniai užpildys paraišką, jie atsiras čia.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- Participant selection ---
st.subheader("1. Pasirinkite dalyvį")

participant_options = {
    f"{row[1]} {row[2]} — {row[4]} ({row[3]})": row
    for row in participants
}

selected_label = st.selectbox(
    "Mokiniai laukiantys mobilumo duomenų:",
    options=list(participant_options.keys()),
    help="Rodomi tik mokiniai kurie dar neturi sutarties"
)

selected = participant_options[selected_label]
participant_id = selected[0]
first_name = selected[1]
last_name = selected[2]
email = selected[3]
study_programme = selected[4]
group_year = selected[5]
english_level = selected[6]
applied_date = selected[7]

# Show participant card
st.markdown(f"""
<div class="participant-card">
    <strong>{first_name} {last_name}</strong><br/>
    Programa: {study_programme} | Grupė: {group_year}<br/>
    Anglų k. lygis: {english_level} | El. paštas: {email}<br/>
    <small>Paraiška pateikta: {applied_date.strftime('%Y-%m-%d') if applied_date else '—'}</small>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- Mobility details ---
st.subheader("2. Mobilumo duomenys")

col1, col2 = st.columns(2)

with col1:
    contract_number = st.text_input(
        "Sutarties numeris *",
        placeholder="pvz. PS-124/2025",
        help="Unikalus sutarties identifikatorius"
    )
    project_code = st.text_input(
        "Projekto kodas *",
        value="2024-1-LT01-KA121-VET-000200419",
        help="Erasmus+ projekto kodas"
    )
    country = st.selectbox(
        "Šalis *",
        options=list(COUNTRIES.keys())
    )
    city = st.text_input("Miestas *", placeholder="pvz. Slagelse")

with col2:
    host_organisation = st.text_input(
        "Priimančioji organizacija *",
        placeholder="pvz. ZBC Zealand Business College"
    )
    host_address = st.text_input(
        "Organizacijos adresas",
        placeholder="pvz. Ahorn Allé 3-5, 4100 Ringsted"
    )
    host_contact = st.text_input(
        "Kontaktinis asmuo",
        placeholder="pvz. International Coordinator"
    )
    host_email = st.text_input(
        "Kontakto el. paštas",
        placeholder="pvz. international@zbc.dk"
    )

col3, col4 = st.columns(2)

with col3:
    start_date = st.date_input(
        "Mobilumo pradžia *",
        min_value=date.today()
    )
    end_date = st.date_input(
        "Mobilumo pabaiga *",
        min_value=date.today()
    )

with col4:
    travel_days = st.number_input(
        "Kelionės dienų skaičius *",
        min_value=1,
        max_value=5,
        value=1
    )
    accompanying_person = st.text_input(
        "Lydintis asmuo (jei yra)",
        placeholder="pvz. Daiva Anužienė"
    )

notes = st.text_area(
    "Papildomos pastabos",
    placeholder="Įveskite bet kokią papildomą informaciją...",
    height=80
)

# --- Grant calculation preview ---
if start_date and end_date and start_date < end_date:
    mobility_days = (end_date - start_date).days + travel_days
    rate = COUNTRIES[country]["rate"]
    travel = COUNTRIES[country]["travel"]
    individual_total = mobility_days * rate
    total_grant = individual_total + travel

    st.divider()
    st.subheader("3. Dotacijos apskaičiavimas")

    col5, col6, col7 = st.columns(3)
    col5.metric("Individual Support", f"{individual_total} EUR", f"{mobility_days} d. × {rate} EUR")
    col6.metric("Travel Support", f"{travel} EUR", f"Lietuva → {country}")
    col7.metric("Bendra dotacija", f"{total_grant} EUR", "")

st.divider()

# --- Submit button ---
st.subheader("4. Generuoti sutartį")

required_fields = [contract_number, project_code, city, host_organisation]
all_filled = all(required_fields) and start_date < end_date

if not all_filled:
    st.markdown("""
    <div class="warning-box">
        Užpildykite visus privalomus laukus (*) prieš generuojant sutartį.
    </div>
    """, unsafe_allow_html=True)

submit = st.button(
    "Generuoti Erasmus+ sutartį",
    type="primary",
    disabled=not all_filled,
    use_container_width=True
)

if submit:
    mobility_days = (end_date - start_date).days + travel_days
    rate = COUNTRIES[country]["rate"]
    travel_support = COUNTRIES[country]["travel"]

    payload = {
        "participant_email": email,
        "participant_id": participant_id,
        "contract_number": contract_number,
        "project_code": project_code,
        "country": country,
        "city": city,
        "host_organisation": host_organisation,
        "host_address": host_address,
        "host_contact_person": host_contact,
        "host_contact_email": host_email,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "mobility_days": mobility_days,
        "travel_days": travel_days,
        "individual_support_rate": rate,
        "travel_support": travel_support,
        "accompanying_person": accompanying_person,
        "notes": notes,
        "submitted_at": datetime.now().isoformat()
    }

    with st.spinner("Siunčiama į sistemą..."):
        success = send_to_n8n(payload)

    if success:
        st.markdown(f"""
        <div class="success-box">
            <strong>Puiku! Sutartis generuojama.</strong><br/>
            Dalyvis: {first_name} {last_name}<br/>
            Sutarties nr.: {contract_number}<br/>
            Šalis: {country}, {city}<br/>
            Bendra dotacija: {mobility_days * rate + travel_support} EUR<br/><br/>
            PDF bus sukurtas ir įkeltas į Google Drive.
            Gausite pranešimą el. paštu kai viskas bus paruošta.
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
    else:
        st.error("Klaida siunčiant duomenis. Patikrinkite n8n webhook URL.")
