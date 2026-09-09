# Rider Gate Staff Performance Dashboard V9 — Streamlit + Apps Script

V9 adds the map background behind the main dashboard content.

## What's added

- The uploaded map image is now included in `assets/dashboard_map_bg.png`.
- The main dashboard area uses the map as a background layer behind the content.
- The Rider Gate sidebar is unaffected.
- The login page is unaffected.
- KPI cards, tables and dealer trend cards remain readable with a soft white overlay and slight translucency.

## Notes

- The background is applied only to the dashboard main content area.
- No Apps Script changes are required.
- No Streamlit Secrets changes are required.

## Update GitHub using CMD

Replace the current project files with V9 while keeping your `.git` folder:

```cmd
git add .
git commit -m "Add dashboard map background V9"
git push
```

Streamlit should redeploy automatically.
