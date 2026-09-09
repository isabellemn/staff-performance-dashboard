# Rider Gate Staff Performance Dashboard V7 - Streamlit + Apps Script

V7 fixes the four issues reported after V6.

## Fixed in V7

1. Login form centring
   - The Streamlit main area is explicitly constrained to the right 50% of the viewport.
   - The complete login block is centred inside that half, horizontally and vertically.

2. Sidebar can always be reopened
   - V6 targeted an obsolete collapsed-control selector.
   - V7 uses Streamlit's current `stSidebarCollapseButton`.
   - When the sidebar is collapsed, only a small transparent fixed rail and a white circular reopen arrow remain.
   - The rail is fixed/overlaid, so it does not take width away from the dashboard.
   - The dashboard still expands to the available full width.

3. Sales graph fixed
   - The source column name `No. of Sales` contains periods.
   - Altair/Vega-Lite can interpret periods in field names as nested data paths.
   - V7 uses safe internal plotting fields: `Sales` and `BikeListings`.
   - The Sales tab now plots Sales correctly.

4. No more Sales NaN on hover
   - Sales and bike-listing values are normalised before charting.
   - Blanks, N/A-style values and non-numeric values are converted to 0.
   - Hover details use safe plotting field names.
   - Both Sales and Bike Listing tabs show Date, Sales and Bike listings on hover.

## Apps Script

No Apps Script change or redeployment is required.

## Streamlit Secrets

Keep your existing secrets unchanged.

## Update GitHub with CMD

Replace the old project files with V7 while keeping the existing `.git` folder.

Then run:

```cmd
git add .
git commit -m "Fix login sidebar and dealer sales charts V7"
git push
```

Streamlit should redeploy automatically.
