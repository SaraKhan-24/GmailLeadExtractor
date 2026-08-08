# 📬 Gmail Lead Extractor

An automated Python tool designed to authenticate with the Gmail API, search and fetch email threads, parse raw MIME and HTML bodies, extract leads, and sync results with Google Sheets.

---

## 🚀 Project Roadmap & Status

- [x] **Module 1: Authentication & Configuration**
  - OAuth2 workflow setup using `google-auth-oauthlib`.
  - Token caching (`token.json`) and centralized config management via `python-dotenv`.
- [x] **Module 2: Email Fetching & Parsing**
  - Gmail API query search (`list_message_ids`).
  - MIME body parser handling `text/plain` and HTML fallback parsing with tag stripping.
- [ ] **Module 3: Lead Classification & Extraction** *(In Progress)*
  - Extract structured lead data (sender, phone numbers, query intent, call-to-actions).
- [ ] **Module 4: Google Sheets Export & Automated Sync** *(Upcoming)*
  - Automated lead export to Google Sheets via `gspread`.

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/SaraKhan-24/GmailLeadExtractor.git
cd GmailLeadExtractor

### 2. Setup Virtual Environment

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

### 3. Configure Environment Variables

cp .env.example .env

### 4. Add Google Cloud Credentials

1. Obtain credentials.json from the Google Cloud Console (OAuth 2.0 Client IDs).
2. Place credentials.json in the root directory of the project.

##🧪Verification & Usage

###Test Authentication (Module 1):

python test_auth.py

###Test Email Fetching & Parsing (Module 2):

python test_fetch.py

##📁 Project Structure

GmailLeadExtractor/
├── src/
│   ├── auth.py         # Google OAuth2 service builder
│   ├── config.py       # Centralized env config loader
│   └── gmail_reader.py # Gmail API fetcher & MIME/HTML parser
├── .env.example        # Environment variables template
├── requirements.txt    # Project dependencies
├── test_auth.py        # Authentication test script
└── test_fetch.py       # Email fetching test script


---

### Step 4: Run Git Commands to Push to GitHub

Run these commands in your terminal to perform a clean push:

```bash
# 1. Initialize git (if not already initialized)
git init

# 2. Link your remote GitHub repository
git remote add origin https://github.com/SaraKhan-24/GmailLeadExtractor.git

# 3. Check status - IMPORTANT: Make sure credentials.json, token.json, and .venv are NOT listed!
git status

# 4. Stage files
git add .

# 5. Commit changes
git commit -m "feat: complete Module 1 (Auth) and Module 2 (Gmail Fetching & Parsing)"

# 6. Set main branch and push to GitHub
git branch -M main
git push -u origin main
