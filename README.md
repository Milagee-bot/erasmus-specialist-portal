[README.md](https://github.com/user-attachments/files/26148350/README.md)
# Erasmus+ Specialisto Portalas

Streamlit aplikacija skirta Erasmus+ mobilumų koordinatoriams. Leidžia greitai ir patogiai užpildyti mobilumo duomenis dalyviauviems kurie jau pateikė paraišką.

## Kaip veikia

1. **Mokinys** užpildo paraišką per n8n Student Form — duomenys išsaugomi PostgreSQL
2. **Specialistas** atidaro šią aplikaciją — mato visus mokinius laukiančius mobilumo duomenų
3. **Specialistas** pasirenka mokinį, užpildo mobilumo informaciją ir siunčia
4. **n8n** automatiškai generuoja sutartį su Claude AI, sukuria PDF ir įkelia į Google Drive

## Instaliacija (lokaliai)

```bash
git clone https://github.com/YOUR_USERNAME/erasmus-specialist-portal
cd erasmus-specialist-portal
pip install -r requirements.txt
cp .env.example .env
# Užpildykite .env failą savo duomenimis
streamlit run app.py
```

## Streamlit Cloud deploy

1. Įkelkite projektą į GitHub
2. Eikite į [share.streamlit.io](https://share.streamlit.io)
3. Pasirinkite savo repozitoriją
4. Nustatykite Secrets (Settings → Secrets):

```toml
DB_HOST = "your_host"
DB_PORT = "5432"
DB_NAME = "erasmus_db"
DB_USER = "postgres"
DB_PASSWORD = "your_password"
N8N_WEBHOOK_URL = "https://milagee.app.n8n.cloud/webhook/specialist-form"
```

## n8n konfigūracija

Vietoje **Specialist Form** node naudokite **Webhook** node su:
- HTTP Method: POST
- Path: `specialist-form`

## Duomenų bazė

PostgreSQL lentelė `erasmus_participants` — sukurkite pagal n8n workflow dokumentaciją.

## Technologijos

- [Streamlit](https://streamlit.io) — web sąsaja
- [PostgreSQL](https://postgresql.org) — duomenų bazė
- [n8n](https://n8n.io) — automatizacija
- [Claude AI](https://anthropic.com) — sutarčių generavimas
