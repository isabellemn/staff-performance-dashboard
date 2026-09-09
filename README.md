# Rider Gate Staff Performance Dashboard V10 — Streamlit + Apps Script

V10 fixes the map background visibility.

## Why V9 looked blank

The supplied map image is already very light. V9 added another 90% white wash
over it, so the road lines were almost invisible.

## V10

- Removes the white wash completely.
- Applies the map directly to the main dashboard area.
- Forces Streamlit's main content wrappers to remain transparent.
- Repeats the map vertically so it continues as you scroll.
- Scales the map to the dashboard width.
- Leaves the Rider Gate sidebar and login page unchanged.
- Keeps cards and tables mostly white so the data remains easy to read.

## Update GitHub with CMD

```cmd
git add .
git commit -m "Make dashboard map background visible V10"
git push
```

No Apps Script or Streamlit Secrets changes are required.
