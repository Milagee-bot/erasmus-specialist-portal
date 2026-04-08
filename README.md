# Erasmus+ Specialisto Portalas

Streamlit aplikacija Erasmus+ mobilumų koordinatoriams — leidžia greitai užpildyti mobilumo duomenis ir automatiškai sugeneruoti sutartis.

## Kaip veikia

1. **Mokinys** užpildo anketą per n8n Student Form — duomenys išsaugomi Google Sheets ir PDF įkeliamas į Google Drive
2. **Specialistas** atidaro šią aplikaciją — mato visus dalyvius
3. **Specialistas** pasirenka dalyvį, užpildo mobilumo duomenis ir siunčia
4. **n8n** per du AI agentus automatiškai sugeneruoja:
   - Dotacijos sutartį (lietuvių kalba)
   - Learning Agreement (anglų kalba)
5. Abu dokumentai įkeliami į Google Drive, specialistas gauna Gmail pranešimą su nuorodomis

## Technologijos

- [Streamlit](https://streamlit.io) — specialisto portalas
- [n8n](https://n8n.io) — automatizavimo platforma (3 workflow)
- [OpenAI GPT-4](https://openai.com) — AI agentai sutarčių generavimui
- [Pinecone](https://pinecone.io) — vektorių DB (profesijos + sutarčių šablonai)
- [Google Drive / Sheets](https://google.com) — dokumentų saugykla
- [Gmail](https://gmail.com) — automatiniai pranešimai
- [Flask + wkhtmltopdf](https://flask.palletsprojects.com) — PDF konvertavimas
- [Claude AI](https://anthropic.com) — kodo rašymas ir konsultavimas 😄

## Lokalus paleidimas (4 CMD langai)

```bash
# CMD 1
npx n8n

# CMD 2
python C:\Users\milag\n8n_files\pdf_server.py

# CMD 3
node C:\Users\milag\n8n_files\contract_server.js

# CMD 4
cd erasmus-specialist-portal
python -m streamlit run app.py
```

## Instaliacija

```bash
git clone https://github.com/Milagee-bot/erasmus-specialist-portal
cd erasmus-specialist-portal
pip install -r requirements.txt
cp env.example .env
streamlit run app.py
```