# Rider Gate Staff Performance Dashboard V6 — Streamlit + Apps Script

V6 makes three interface changes requested after V5.

## Changes in V6

1. Login form
   - The full login block is now centred horizontally and vertically within the right half of the screen.
   - The Rider Gate panel remains on the left.

2. Collapsible sidebar
   - Dashboard content still expands to full width when the sidebar is closed.
   - Streamlit's native sidebar reopen arrow is deliberately retained and styled as a white circular button.
   - The rest of Streamlit's toolbar/chrome remains hidden.

3. Dealer trend tabs
   - Every dealer card now contains two tabs:
     - Sales
     - Bike Listing
   - Selecting Sales shows that dealer's sales trend.
   - Selecting Bike Listing shows that dealer's bike-listing trend.
   - The total sales and total bike listings remain in the top-right corner of the dealer card.
   - Hovering any graph point always shows the full details for that date:
     - Date
     - Sales
     - Bike listings

## Apps Script

No Apps Script change or redeployment is required for V6.

## Streamlit Secrets

Keep your existing secrets unchanged:

```toml
[app]
password = "YOUR_PASSWORD"

[data_api]
url = "YOUR_APPS_SCRIPT_EXEC_URL"
token = "YOUR_API_TOKEN"
```

## Update GitHub with CMD

Replace your old project files with the V6 files, while keeping the existing `.git` folder.

Then run:

```cmd
git add .
git commit -m "Update dashboard login sidebar and dealer trend tabs"
git push
```

Streamlit should redeploy automatically.
