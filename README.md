# Rider Gate Staff Performance Dashboard V8 — Streamlit + Apps Script

V8 replaces the login layout implementation.

## Login fix

The previous login versions tried to position Streamlit's entire `main`
element at `left: 50vw`. That was unreliable because Streamlit's internal
wrappers still applied their own layout calculations.

V8 removes that approach completely.

The login page is now created using two actual Streamlit columns:

- Left column: 50% Rider Gate red panel
- Right column: 50% login area
- The row is full viewport height
- Streamlit's `vertical_alignment="center"` centres the right-side content
- The right-side content is constrained to a 460px form block and horizontally
  centred inside the right column

There is no fixed right-side `main` positioning and no `left:50vw` hack.

## Other V7 fixes retained

- Sidebar can collapse and reopen
- Sales and Bike Listing dealer tabs
- Sales chart fix
- Full Date / Sales / Bike Listings hover details
- No NaN chart values
- Malaysia timezone
- Private sheets via Apps Script

## Update GitHub using CMD

Replace the existing project files with V8 while keeping your `.git` folder:

```cmd
git add .
git commit -m "Fix login layout V8"
git push
```

No Apps Script or Streamlit Secrets changes are required.
