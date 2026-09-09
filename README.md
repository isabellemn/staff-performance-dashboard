# Rider Gate Staff Performance Dashboard - Streamlit + Apps Script (V4)

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


## V4 interface fixes

- Full-screen split login page and the word "Live" removed.
- Rider Gate sidebar restyled to match the earlier dashboard, with radio circles hidden and staff shown with account icons.
- Dealer trend cards use a solid Rider Gate red line plus shaded area instead of the plain dotted presentation.
- Hover details always include date, sales and bike listings; missing numeric values are normalised to 0 instead of displaying NaN.
- Synced time uses Malaysia time (Asia/Kuala_Lumpur).
- Refresh data and Log out buttons have more room so their labels do not truncate.
