# Gmail Lead Extractor

An automated Python tool designed to authenticate with the Gmail API, search and fetch email threads, parse raw MIME and HTML bodies, extract leads, and sync results with Google Sheets.

---

## Project Roadmap & Status

- [x] **Module 1: Authentication & Configuration**
  - OAuth2 workflow setup using `google-auth-oauthlib`.
  - Token caching (`token.json`) and centralized config management via `python-dotenv`.
- [x] **Module 2: Email Fetching & Parsing**
  - Gmail API query search (`list_message_ids`).
  - MIME body parser handling `text/plain` and HTML fallback parsing with tag stripping.
- [x] **Module 3: Lead Classification & Extraction** 
  - Structured AI classification using Google GenAI SDK (`google-genai`)
  -Pydantic schema validation (`LeadData`) for extracting lead intent, name, email, budget, priority, and summary
- [x] **Module 4: Google Sheets Export & Automated Sync**
  - Automated lead export to Google Sheets via `gspread` with automatic spreadsheet creation.
  -Gmail email labeling (`gmail_labeler`) to tag processed emails and defensive deduplication(`sheets_exporter.py`).

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/SaraKhan-24/GmailLeadExtractor.git
cd GmailLeadExtractor
```

### 2. Setup Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

### 4. Add Google Cloud Credentials

1. Obtain credentials.json from the Google Cloud Console (OAuth 2.0 Client IDs).
2. Place credentials.json in the root directory of the project.

---

## Verification & Usage

### Test Authentication (Module 1):
```bash
python test_auth.py
```
### Test Email Fetching & Parsing (Module 2):
```bash
python test_fetch.py
```
### Test AI Lead Classification (Module 3):
```bash
python test_classify.py
```
### Test Full Pipeline & Google Sheets Export (Module 4):
```bash
python test_export.py
```
---
## Project Structure
```text
GmailLeadExtractor/
├── src/
│   ├── ai_classifier.py  # Structured AI lead classification via Google GenAI SDK
│   ├── auth.py           # Google OAuth2 service builder
│   ├── config.py         # Centralized env config loader
│   ├── gmail_labeler.py  # Gmail email labeling & status tracking
│   ├── gmail_reader.py   # Gmail API fetcher & MIME/HTML parser
│   └── sheets_exporter.py# Google Sheets creation & batch lead exporter
├── .env.example          # Environment variables template
├── requirements.txt      # Project dependencies
├── test_auth.py          # Authentication test script
├── test_classify.py      # AI lead classification test script
├── test_export.py        # End-to-end pipeline & Google Sheets export test script
└── test_fetch.py         # Email fetching test 
script
```
