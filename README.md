# Staff Performance Dashboard — Streamlit Backup

This is the backup version of the staff performance dashboard.

## Features

- Overview across all staff
- Sidebar navigation for each staff member
- Total visits, sales, bike listings and active dealers
- Dealer performance summary
- One dealer trend graph per dealer
- Hover details for date, bike listings and sales
- Total sales and listings shown above each graph
- Date filter and dealer search
- Automatic refresh every 60 seconds

## Google Sheet requirements

Each spreadsheet should have:

- Date of Visit
- Dealer Name
- Bike Listing
- No. of Sales

The app scans the first 15 rows, so a blank row or blank column before the headers is fine.

The sheets should be shared as:
**Anyone with the link → Viewer**

## Run locally

```cmd
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

Upload this folder to a GitHub repository and select `app.py` as the main file.

No Streamlit secrets are required when the sheets are publicly viewable.

## Add or rename staff

Edit the `STAFF_SHEETS` list near the top of `app.py`.
