# Rider Gate Staff Performance Dashboard — Streamlit + Apps Script

This version uses Google Apps Script as the private data bridge between the Streamlit dashboard and the staff Google Sheets.

## Architecture

Private Google Sheets -> Google Apps Script Web App -> Streamlit Dashboard

The Sheets can remain **Restricted**. The Apps Script Web App executes as the Google account that owns/has access to the sheets. Streamlit sends a secret API token to Apps Script, so a person who discovers the Web App URL cannot retrieve dashboard data without the token.

## Files

- `app.py` — Streamlit dashboard
- `apps-script/Code.gs` — paste this into Google Apps Script
- `.streamlit/secrets.example.toml` — example Streamlit Secrets
- `requirements.txt` — Python packages
- `assets/rider_gate_logo.png` — dashboard logo

## GitHub

Do not commit `.streamlit/secrets.toml`.

## Streamlit Secrets

Use:

```toml
[app]
password = "YOUR-DASHBOARD-PASSWORD"

[data_api]
url = "https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec"
token = "THE-SAME-API-TOKEN-AS-IN-APPS-SCRIPT"
```
