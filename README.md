# Rider Gate Staff Performance Dashboard — Streamlit V2

This version is Streamlit-only. It does **not** use Cloudflare and it does **not** require Google Apps Script.

## V2 changes

- Password login page styled to match the Rider Gate reference
- Google Sheets remain **private / Restricted**
- Private sheet access through a Google service account
- Google Sheet IDs and credentials are stored in **Streamlit Secrets**, not in GitHub code
- Rider Gate red sidebar styling and logo
- Overview plus one sidebar page for each staff member
- `Refresh data` button
- `Log out` button
- Synced-time display
- Dealer trend cards arranged two per row
- Red filled sales trend with bike-listing comparison line
- Hover shows date, sales and bike listings
- Total sales and total bike listings shown on every dealer card
- Automatic refresh every 60 seconds

---

# 1. Google Sheet format

Each staff Google Sheet should contain these four headings:

- Date of Visit
- Dealer Name
- Bike Listing
- No. of Sales

The headings can start after blank rows or blank columns. The app scans the first 20 rows to find them.

Each completed row represents one dealer visit.

---

# 2. Keep the Google Sheets private

For each Google Sheet:

1. Open the sheet.
2. Click **Share**.
3. Under General access, keep it as **Restricted**.

Do not use `Anyone with the link` for V2.

The service account created below will be given Viewer access directly.

---

# 3. Create a Google service account

Go to Google Cloud Console.

1. Create a new project, for example `Rider Gate Dashboard`.
2. Open **APIs & Services -> Library**.
3. Enable **Google Sheets API**.
4. Enable **Google Drive API**.
5. Open **IAM & Admin -> Service Accounts**.
6. Click **Create service account**.
7. Name it something like `rider-gate-dashboard`.
8. Finish creating the service account.
9. Open the service account.
10. Go to **Keys -> Add key -> Create new key -> JSON**.
11. Download the JSON key file.

Keep the JSON file private. Do not upload it to GitHub.

---

# 4. Share each private sheet with the service account

Open the downloaded JSON file and find the value called:

`client_email`

It will look similar to:

`rider-gate-dashboard@your-project.iam.gserviceaccount.com`

For Person 1's Google Sheet:

1. Click **Share**.
2. Paste the service-account email.
3. Set permission to **Viewer**.
4. Click **Send**.

Repeat for Person 2 and every future staff sheet.

The sheet remains Restricted to the public, but the Streamlit service account can read it.

---

# 5. Configure Streamlit Secrets

The repository includes:

`.streamlit/secrets.example.toml`

Do not rename or upload an actual `secrets.toml` file containing credentials to GitHub.

When deploying to Streamlit Community Cloud, open your app's **Settings / Advanced settings -> Secrets** and paste the configuration from `secrets.example.toml`, replacing the placeholders with your real values.

You need to enter:

- Dashboard password
- Person 1 name and Sheet ID
- Person 2 name and Sheet ID
- Google service-account JSON values

To add more staff later, add:

```toml
person_3_name = "Name"
person_3_sheet_id = "GOOGLE_SHEET_ID"
```

then continue with `person_4`, `person_5`, etc.

---

# 6. Upload to GitHub using CMD

Create an empty GitHub repository, for example:

`staff-performance-dashboard`

Do not initialise it with a README if you are creating a new repository.

Extract this V2 ZIP. Open the extracted folder in Windows File Explorer. Click the address bar, type:

```cmd
cmd
```

and press Enter.

Then run:

```cmd
git init
```

```cmd
git branch -M main
```

```cmd
git add .
```

```cmd
git commit -m "Create secure Rider Gate staff dashboard"
```

Connect it to GitHub, replacing the URL with your repository URL:

```cmd
git remote add origin https://github.com/YOUR-USERNAME/staff-performance-dashboard.git
```

Then push:

```cmd
git push -u origin main
```

The `.gitignore` file prevents `.streamlit/secrets.toml` and common Google credential JSON files from being uploaded.

---

# 7. Deploy on Streamlit Community Cloud

1. Open Streamlit Community Cloud.
2. Click **Create app**.
3. Choose your GitHub repository.
4. Branch: `main`.
5. Main file path: `app.py`.
6. Open **Advanced settings / Secrets**.
7. Paste your completed Streamlit Secrets configuration.
8. Click **Deploy**.

The app URL can be public, while the dashboard itself is password-protected and the Google Sheets remain private.

---

# 8. Updating through CMD later

When you replace `app.py` or other dashboard files with a newer version, open CMD in the repository folder and run:

```cmd
git add .
```

```cmd
git commit -m "Update Rider Gate staff dashboard"
```

```cmd
git push
```

Streamlit Community Cloud will automatically redeploy the updated version.

---

# Security notes

- Do not make the Google Sheets public.
- Do not put Sheet IDs in `app.py`.
- Do not put the service-account JSON key in GitHub.
- Do not put the dashboard password in GitHub.
- Store all private values in Streamlit Secrets.
- Only share each Google Sheet with the Google service-account email as Viewer.
