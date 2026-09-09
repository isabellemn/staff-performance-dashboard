# Rider Gate Staff Performance Dashboard V5 - Streamlit + Apps Script

V5 addresses the latest interface corrections.

## Changes in V5

- Login screen rebuilt as a true full-height split screen.
- Dashboard content expands to the full available width when the sidebar is collapsed.
- Rider Gate logo is rendered as normal HTML, so it no longer has a fullscreen/expand control.
- Sidebar navigation uses real buttons instead of radio buttons.
- Overview uses a home icon and staff use account/user icons.
- Streamlit element toolbars are hidden, removing the graph-to-table/fullscreen controls.
- Dealer graph now displays Bike Listings only as the visible red shaded trend.
- Hover still shows Date, Sales and Bike Listings.
- Removed the Sales/Bike Listings colour legend because two visible trend lines are no longer used.
- Removed helper fields such as "Sales Tooltip" and "Listings Tooltip".
- Dealer Performance Summary has a visible row number starting at 1.
- Malaysia timezone remains Asia/Kuala_Lumpur.
- Apps Script API setup is unchanged.

## Update GitHub from CMD

Replace the old project files with the V5 files, keeping your existing `.git` folder.

Then run:

```cmd
git add .
git commit -m "Update staff dashboard interface V5"
git push
```

Streamlit should redeploy automatically.

## Apps Script

No Apps Script redeployment is required for these interface changes.
The included `apps-script/Code.gs` is the same API approach as before.

## Streamlit Secrets

Your existing secrets remain:

```toml
[app]
password = "YOUR_PASSWORD"

[data_api]
url = "YOUR_APPS_SCRIPT_EXEC_URL"
token = "YOUR_API_TOKEN"
```

Do not commit real secrets to GitHub.
