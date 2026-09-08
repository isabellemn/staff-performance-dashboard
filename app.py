import io
import re
from datetime import datetime

import altair as alt
import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Staff Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

STAFF_SHEETS = [
    {
        "id": "person-1",
        "name": "Person 1",
        "sheet_id": "1oXwvTc5iXf54_vA4N-jXLi3agPOX4fxv5b-qAJy2JXw",
    },
    {
        "id": "person-2",
        "name": "Person 2",
        "sheet_id": "1bNAL5x_J86Mv_Klbs2iqzVIyrNZWaibWlSPJHG4hSPg",
    },
]

HEADER_VARIANTS = {
    "Date of Visit": {"date of visit", "date visit", "visit date", "date"},
    "Dealer Name": {"dealer name", "dealer"},
    "Bike Listing": {"bike listing", "bike listings", "listing", "listings"},
    "No. of Sales": {"no. of sales", "no of sales", "number of sales", "sales"},
}

st_autorefresh(interval=60_000, key="dashboard_refresh")

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.8rem; padding-bottom: 3rem;}
    [data-testid="stSidebar"] {background: linear-gradient(180deg,#7f1d1d,#b91c1c);}
    [data-testid="stSidebar"] * {color: white;}
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e7eaf0;
        padding: 16px;
        border-radius: 14px;
        box-shadow: 0 8px 28px rgba(16,24,40,.05);
    }
    .dealer-card {
        background: white;
        border: 1px solid #e7eaf0;
        border-radius: 14px;
        padding: 14px 16px 4px 16px;
        margin-bottom: 10px;
    }
    .dealer-title {font-size: 1.05rem; font-weight: 800;}
    .dealer-totals {color:#667085;font-size:.84rem;margin-top:4px}
    </style>
    """,
    unsafe_allow_html=True,
)


def normalise_header(value):
    s = str(value or "").strip().lower()
    s = re.sub(r"[._-]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def detect_header_row(raw: pd.DataFrame):
    for i in range(min(len(raw), 15)):
        values = [normalise_header(v) for v in raw.iloc[i].tolist()]
        mapping = {}
        for canonical, variants in HEADER_VARIANTS.items():
            idx = next((j for j, cell in enumerate(values) if cell in variants), None)
            if idx is None:
                break
            mapping[canonical] = idx
        if len(mapping) == len(HEADER_VARIANTS):
            return i, mapping
    return None, None


@st.cache_data(ttl=55, show_spinner=False)
def load_staff_sheet(staff_id, staff_name, sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    r = requests.get(url, timeout=20, headers={"User-Agent": "RiderGate-Staff-Dashboard/1.0"})
    r.raise_for_status()

    if "<html" in r.text[:500].lower():
        raise ValueError("Sheet is not publicly readable. Set sharing to 'Anyone with the link - Viewer'.")

    raw = pd.read_csv(io.StringIO(r.text), header=None, dtype=str, keep_default_na=False)
    header_row, mapping = detect_header_row(raw)
    if mapping is None:
        raise ValueError(
            "Could not find Date of Visit, Dealer Name, Bike Listing and No. of Sales headers."
        )

    data = pd.DataFrame({
        "Date of Visit": raw.iloc[header_row + 1 :, mapping["Date of Visit"]].astype(str).str.strip(),
        "Dealer Name": raw.iloc[header_row + 1 :, mapping["Dealer Name"]].astype(str).str.strip(),
        "Bike Listing": raw.iloc[header_row + 1 :, mapping["Bike Listing"]].astype(str).str.strip(),
        "No. of Sales": raw.iloc[header_row + 1 :, mapping["No. of Sales"]].astype(str).str.strip(),
    })

    data = data[
        (data["Dealer Name"] != "")
        | (data["Date of Visit"] != "")
        | (data["Bike Listing"] != "")
        | (data["No. of Sales"] != "")
    ].copy()
    data = data[data["Dealer Name"] != ""].copy()

    data["Bike Listing"] = pd.to_numeric(
        data["Bike Listing"].str.replace(",", "", regex=False).str.extract(r"(-?\d+(?:\.\d+)?)")[0],
        errors="coerce",
    ).fillna(0)
    data["No. of Sales"] = pd.to_numeric(
        data["No. of Sales"].str.replace(",", "", regex=False).str.extract(r"(-?\d+(?:\.\d+)?)")[0],
        errors="coerce",
    ).fillna(0)

    # dayfirst=True matches common Malaysian date entry style such as 31/08/2026.
    data["Date Parsed"] = pd.to_datetime(data["Date of Visit"], errors="coerce", dayfirst=True)
    data["Staff ID"] = staff_id
    data["Staff Name"] = staff_name
    return data.reset_index(drop=True)


frames = []
errors = []
for staff in STAFF_SHEETS:
    try:
        frames.append(load_staff_sheet(staff["id"], staff["name"], staff["sheet_id"]))
    except Exception as exc:
        errors.append((staff["name"], str(exc)))

df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(
    columns=["Date of Visit", "Dealer Name", "Bike Listing", "No. of Sales", "Date Parsed", "Staff ID", "Staff Name"]
)

with st.sidebar:
    st.markdown("## Staff Performance")
    st.caption("Dealer Visit Dashboard")
    choices = ["Overview"] + [s["name"] for s in STAFF_SHEETS]
    selected = st.radio("View", choices, label_visibility="collapsed")

if selected == "Overview":
    view_df = df.copy()
    title = "Performance Overview"
    subtitle = "Combined performance across all staff"
else:
    selected_staff = next(s for s in STAFF_SHEETS if s["name"] == selected)
    view_df = df[df["Staff ID"] == selected_staff["id"]].copy()
    title = selected
    subtitle = "Individual dealer visit and sales performance"

st.title(title)
st.caption(subtitle)

for staff_name, error in errors:
    if selected == "Overview" or staff_name == selected:
        st.warning(f"{staff_name}: {error}")

filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 2])

valid_dates = view_df["Date Parsed"].dropna()
min_date = valid_dates.min().date() if not valid_dates.empty else None
max_date = valid_dates.max().date() if not valid_dates.empty else None

with filter_col1:
    date_from = st.date_input("From date", value=min_date)
with filter_col2:
    date_to = st.date_input("To date", value=max_date)
with filter_col3:
    dealer_search = st.text_input("Dealer search", placeholder="Search dealer name")

filtered = view_df.copy()
if date_from:
    filtered = filtered[filtered["Date Parsed"].isna() | (filtered["Date Parsed"].dt.date >= date_from)]
if date_to:
    filtered = filtered[filtered["Date Parsed"].isna() | (filtered["Date Parsed"].dt.date <= date_to)]
if dealer_search.strip():
    filtered = filtered[
        filtered["Dealer Name"].str.contains(dealer_search.strip(), case=False, na=False)
    ]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Visits", f"{len(filtered):,}")
m2.metric("Total Sales", f"{filtered['No. of Sales'].sum():,.0f}")
m3.metric("Bike Listings", f"{filtered['Bike Listing'].sum():,.0f}")
m4.metric("Active Dealers", f"{filtered['Dealer Name'].str.lower().nunique():,}")

st.subheader("Dealer Performance Summary")
if filtered.empty:
    st.info("No records match the current filters.")
else:
    summary = (
        filtered.groupby("Dealer Name", as_index=False)
        .agg(
            **{
                "No. of Visits": ("Dealer Name", "size"),
                "No. of Sales": ("No. of Sales", "sum"),
                "Bike Listing": ("Bike Listing", "sum"),
            }
        )
        .sort_values(["No. of Sales", "Bike Listing", "Dealer Name"], ascending=[False, False, True])
    )
    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "No. of Visits": st.column_config.NumberColumn(format="%d"),
            "No. of Sales": st.column_config.NumberColumn(format="%.0f"),
            "Bike Listing": st.column_config.NumberColumn(format="%.0f"),
        },
    )

st.subheader("Dealer Trends")

if filtered.empty:
    st.info("No dealer trend data to display.")
else:
    for dealer in sorted(filtered["Dealer Name"].dropna().unique(), key=str.lower):
        dealer_df = filtered[filtered["Dealer Name"] == dealer].copy()
        dealer_df = dealer_df.sort_values("Date Parsed")

        total_sales = dealer_df["No. of Sales"].sum()
        total_listings = dealer_df["Bike Listing"].sum()

        st.markdown(
            f"""
            <div class="dealer-card">
                <div class="dealer-title">{dealer}</div>
                <div class="dealer-totals">
                    Total Sales: <b>{total_sales:,.0f}</b>
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    Total Bike Listings: <b>{total_listings:,.0f}</b>
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    Visits: <b>{len(dealer_df):,}</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        plot_df = dealer_df.dropna(subset=["Date Parsed"]).copy()
        if plot_df.empty:
            st.caption("No valid dates are available for this dealer's trend graph.")
            continue

        long_df = plot_df.melt(
            id_vars=["Date Parsed", "Date of Visit"],
            value_vars=["No. of Sales", "Bike Listing"],
            var_name="Metric",
            value_name="Value",
        )

        chart = (
            alt.Chart(long_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("Date Parsed:T", title="Date"),
                y=alt.Y("Value:Q", title="Number"),
                color=alt.Color("Metric:N", title=None),
                tooltip=[
                    alt.Tooltip("Date of Visit:N", title="Date"),
                    alt.Tooltip("Metric:N", title="Metric"),
                    alt.Tooltip("Value:Q", title="Value", format=",.0f"),
                ],
            )
            .properties(height=260)
            .interactive()
        )

        st.altair_chart(chart, use_container_width=True)

st.caption("Dashboard refreshes automatically every 60 seconds.")
