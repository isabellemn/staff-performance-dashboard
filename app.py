import base64
import hmac
import re
from datetime import datetime
from pathlib import Path

import altair as alt
import requests
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Rider Gate Live Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).parent
LOGO_PATH = ROOT / "assets" / "rider_gate_logo.png"

BRAND_RED = "#B52F25"
BRAND_RED_DARK = "#98251E"
ACCENT_RED = "#D7352F"
INK = "#202938"
MUTED = "#7B8494"
LIGHT_BG = "#F6F8FB"
GRID = "#E8EBF0"
LISTING_COLOUR = "#6B7280"

HEADER_VARIANTS = {
    "Date of Visit": {"date of visit", "date visit", "visit date", "date"},
    "Dealer Name": {"dealer name", "dealer"},
    "Bike Listing": {"bike listing", "bike listings", "listing", "listings"},
    "No. of Sales": {"no. of sales", "no of sales", "number of sales", "sales"},
}


def logo_data_uri() -> str:
    if not LOGO_PATH.exists():
        return ""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def hide_streamlit_chrome():
    st.markdown(
        """
        <style>
        #MainMenu {visibility:hidden;}
        footer {visibility:hidden;}
        header[data-testid="stHeader"] {background:transparent;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_login_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] {{font-family:'Poppins', sans-serif;}}
        .stApp {{background:#FFFFFF;}}
        section[data-testid="stSidebar"] {{display:none !important;}}
        .block-container {{max-width:1180px; padding-top:5.5rem; padding-bottom:3rem;}}
        .login-panel {{
            min-height:510px;
            border-radius:3px;
            padding:44px 42px;
            background:linear-gradient(145deg, {BRAND_RED} 0%, {BRAND_RED_DARK} 100%);
            color:white;
            box-shadow:0 15px 45px rgba(152,37,30,.12);
            display:flex;
            flex-direction:column;
            justify-content:center;
        }}
        .login-panel img {{width:132px; border-radius:13px; margin-bottom:38px;}}
        .login-panel h1 {{font-size:31px;line-height:1.18;margin:0 0 18px;font-weight:800;letter-spacing:-1.1px;}}
        .login-panel p {{font-size:12px;line-height:1.8;opacity:.86;max-width:430px;margin:0;}}
        .login-form-title {{font-size:22px;font-weight:750;color:{INK};margin-top:90px;margin-bottom:20px;}}
        div[data-testid="stTextInput"] label p {{font-size:12px;font-weight:600;color:{MUTED};}}
        div[data-testid="stTextInput"] input {{border-radius:7px;border:1px solid #C9CED7;min-height:44px;}}
        div[data-testid="stFormSubmitButton"] button {{
            width:100%;background:{BRAND_RED};color:#fff;border:0;border-radius:7px;min-height:44px;font-weight:650;
        }}
        div[data-testid="stFormSubmitButton"] button:hover {{background:{BRAND_RED_DARK};color:#fff;border:0;}}
        .login-hint {{color:{MUTED};font-size:11px;margin-top:14px;}}
        @media(max-width:800px) {{
            .block-container {{padding-top:2rem;}}
            .login-panel {{min-height:auto;padding:32px 28px;}}
            .login-form-title {{margin-top:15px;}}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_dashboard_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] {{font-family:'Poppins', sans-serif;}}
        .stApp {{background:{LIGHT_BG};}}
        .block-container {{padding-top:1.45rem;padding-bottom:3rem;max-width:1550px;}}

        section[data-testid="stSidebar"] {{
            background:linear-gradient(180deg,{BRAND_RED} 0%, {BRAND_RED_DARK} 100%);
            border-right:0;
        }}
        section[data-testid="stSidebar"] > div {{padding-top:1.7rem;}}
        section[data-testid="stSidebar"] img {{
            display:block;margin:0 auto 1.3rem auto;max-width:215px;border-radius:22px;
        }}
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] label {{color:white !important;}}
        section[data-testid="stSidebar"] div[role="radiogroup"] {{gap:.42rem;}}
        section[data-testid="stSidebar"] div[role="radiogroup"] label {{
            padding:.76rem .9rem;border-radius:12px;transition:.15s ease;font-weight:650;
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{background:rgba(255,255,255,.10);}}
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{background:rgba(255,255,255,.19);}}
        section[data-testid="stSidebar"] div[role="radiogroup"] label p {{font-size:14px !important;}}
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {{
            background:#fff;color:{BRAND_RED};border-radius:999px;
        }}
        .sidebar-label {{font-size:10px;letter-spacing:.14em;color:rgba(255,255,255,.62);font-weight:700;margin:1rem .25rem .45rem;}}

        h1,h2,h3,p,span,label,button,input {{font-family:'Poppins', sans-serif;}}
        h1 {{color:{INK};letter-spacing:-.8px;}}
        h2,h3 {{color:{INK};}}
        .top-subtitle {{color:{MUTED};font-size:12px;margin-top:-5px;}}
        .sync-text {{color:#8991A0;font-size:11px;text-align:right;padding-top:10px;white-space:nowrap;}}

        div[data-testid="stButton"] button {{
            background:#fff;color:{INK};border:1px solid #E1E5EB;border-radius:12px;min-height:42px;
            font-weight:650;box-shadow:0 2px 8px rgba(32,41,56,.03);
        }}
        div[data-testid="stButton"] button:hover {{border-color:#CDD2DA;color:{BRAND_RED};background:#fff;}}

        .kpi-card {{
            background:#fff;border:1px solid #E7EAF0;border-radius:16px;padding:18px 20px;
            box-shadow:0 8px 24px rgba(32,41,56,.04);min-height:112px;
        }}
        .kpi-label {{font-size:11px;font-weight:650;color:{MUTED};text-transform:uppercase;letter-spacing:.05em;}}
        .kpi-value {{font-size:28px;font-weight:800;color:{INK};margin-top:8px;letter-spacing:-.8px;}}
        .kpi-note {{font-size:10px;color:#9AA1AD;margin-top:3px;}}

        .section-title {{font-size:17px;font-weight:750;color:{INK};margin:1.2rem 0 .65rem;}}
        .dealer-header {{display:flex;justify-content:space-between;align-items:flex-start;gap:15px;margin-bottom:0;}}
        .dealer-name {{font-size:13px;font-weight:650;color:#5F6878;}}
        .dealer-totals {{display:flex;gap:14px;text-align:right;}}
        .dealer-total-label {{font-size:8px;text-transform:uppercase;letter-spacing:.05em;color:#A0A7B2;}}
        .dealer-total-value {{font-size:15px;font-weight:800;color:{ACCENT_RED};line-height:1.2;}}
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border:1px solid #E8EBF0 !important;border-radius:16px !important;background:#fff !important;
            box-shadow:0 8px 25px rgba(32,41,56,.035);
        }}
        div[data-testid="stDataFrame"] {{border-radius:14px;overflow:hidden;border:1px solid #E7EAF0;}}
        div[data-testid="stDateInput"] input, div[data-testid="stTextInput"] input {{
            background:#fff;border-radius:10px;border:1px solid #DDE1E7;min-height:40px;
        }}
        .data-note {{font-size:11px;color:{MUTED};}}
        .privacy-note {{font-size:10px;color:rgba(255,255,255,.64);line-height:1.6;margin-top:1.3rem;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_app_password() -> str:
    try:
        return str(st.secrets["app"]["password"])
    except Exception:
        return ""


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated", False))


def login_screen():
    hide_streamlit_chrome()
    inject_login_css()
    logo = logo_data_uri()

    left, right = st.columns([1, 1], gap="large")
    with left:
        img_html = f'<img src="{logo}" alt="Rider Gate logo">' if logo else ""
        st.markdown(
            f"""
            <div class="login-panel">
                {img_html}
                <h1>Rider Gate Live<br>Performance Dashboard</h1>
                <p>Access the Rider Gate performance dashboard for current operational, staff and dealer-management reporting.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="login-form-title">Dashboard Login</div>', unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            expected = get_app_password()
            if not expected:
                st.error("The dashboard password has not been configured in Streamlit Secrets.")
            elif hmac.compare_digest(password, expected):
                st.session_state["authenticated"] = True
                st.session_state["login_error"] = False
                st.rerun()
            else:
                st.session_state["login_error"] = True

        if st.session_state.get("login_error"):
            st.error("Incorrect password.")
        st.markdown(
            '<div class="login-hint">Authorised Rider Gate users only.</div>',
            unsafe_allow_html=True,
        )


def normalise_header(value):
    s = str(value or "").strip().lower()
    s = re.sub(r"[._-]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def detect_header_row(matrix):
    for i, row in enumerate(matrix[:20]):
        values = [normalise_header(v) for v in row]
        mapping = {}
        for canonical, variants in HEADER_VARIANTS.items():
            idx = next((j for j, cell in enumerate(values) if cell in variants), None)
            if idx is None:
                break
            mapping[canonical] = idx
        if len(mapping) == len(HEADER_VARIANTS):
            return i, mapping
    return None, None


def data_api_configuration():
    try:
        cfg = st.secrets["data_api"]
        url = str(cfg["url"]).strip()
        token = str(cfg["token"]).strip()
        if not url or not token:
            return None
        return {"url": url, "token": token}
    except Exception:
        return None


@st.cache_data(ttl=55, show_spinner=False)
def load_all_data():
    cfg = data_api_configuration()
    if not cfg:
        raise RuntimeError("Apps Script data API is not configured in Streamlit Secrets.")

    try:
        response = requests.post(
            cfg["url"],
            json={"token": cfg["token"]},
            timeout=30,
            allow_redirects=True,
            headers={"User-Agent": "RiderGate-Streamlit-Dashboard/1.0"},
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not reach the Apps Script data API: {exc}") from exc

    if not response.ok:
        raise RuntimeError(f"Apps Script returned HTTP {response.status_code}.")

    try:
        payload = response.json()
    except ValueError as exc:
        preview = response.text[:180].replace("\n", " ")
        raise RuntimeError(f"Apps Script did not return JSON. Response started with: {preview}") from exc

    if not payload.get("ok"):
        raise RuntimeError(payload.get("error") or "Apps Script returned an unknown error.")

    staff_members = payload.get("staff", [])
    rows = payload.get("rows", [])
    errors = payload.get("errors", [])

    columns = [
        "Date of Visit",
        "Dealer Name",
        "Bike Listing",
        "No. of Sales",
        "Date Parsed",
        "Staff ID",
        "Staff Name",
    ]

    if not rows:
        return pd.DataFrame(columns=columns), staff_members, errors

    data = pd.DataFrame(rows)
    rename = {
        "date": "Date of Visit",
        "dealer": "Dealer Name",
        "bikeListing": "Bike Listing",
        "sales": "No. of Sales",
        "staffId": "Staff ID",
        "staffName": "Staff Name",
    }
    data = data.rename(columns=rename)

    for col in ["Date of Visit", "Dealer Name", "Staff ID", "Staff Name"]:
        if col not in data:
            data[col] = ""
        data[col] = data[col].fillna("").astype(str).str.strip()

    for col in ["Bike Listing", "No. of Sales"]:
        if col not in data:
            data[col] = 0
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    data["Date Parsed"] = pd.to_datetime(data["Date of Visit"], errors="coerce", dayfirst=True)
    return data[columns], staff_members, errors

def render_kpis(df):
    visits = len(df)
    sales = df["No. of Sales"].sum() if not df.empty else 0
    listings = df["Bike Listing"].sum() if not df.empty else 0
    dealers = df["Dealer Name"].str.lower().nunique() if not df.empty else 0
    values = [
        ("Total Visits", visits, "Recorded dealer visits"),
        ("Total Sales", sales, "Sales recorded"),
        ("Bike Listings", listings, "Listings recorded"),
        ("Active Dealers", dealers, "Unique dealers"),
    ]
    cols = st.columns(4)
    for col, (label, value, note) in zip(cols, values):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value:,.0f}</div>
                    <div class="kpi-note">{note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def dealer_chart(plot_df):
    if plot_df.empty:
        return None

    base = alt.Chart(plot_df).encode(
        x=alt.X(
            "Date Parsed:T",
            title=None,
            axis=alt.Axis(format="%-d %b", labelAngle=0, labelOverlap=True, tickCount=6),
        )
    )

    tooltip = [
        alt.Tooltip("Date Parsed:T", title="Date", format="%d %b %Y"),
        alt.Tooltip("No. of Sales:Q", title="Sales", format=",.0f"),
        alt.Tooltip("Bike Listing:Q", title="Bike listings", format=",.0f"),
    ]

    sales_area = base.mark_area(
        color=ACCENT_RED,
        opacity=0.10,
        interpolate="linear",
    ).encode(y=alt.Y("No. of Sales:Q", title=None))

    sales_line = base.mark_line(
        color=ACCENT_RED,
        strokeWidth=2.7,
        point=alt.OverlayMarkDef(filled=True, color=ACCENT_RED, size=42),
    ).encode(
        y=alt.Y("No. of Sales:Q", title=None),
        tooltip=tooltip,
    )

    listing_line = base.mark_line(
        color=LISTING_COLOUR,
        strokeWidth=1.8,
        strokeDash=[5, 4],
        point=alt.OverlayMarkDef(filled=True, color=LISTING_COLOUR, size=30),
    ).encode(
        y=alt.Y("Bike Listing:Q", title=None),
        tooltip=tooltip,
    )

    chart = (
        alt.layer(sales_area, sales_line, listing_line)
        .resolve_scale(y="shared")
        .properties(height=225)
        .configure_view(strokeOpacity=0)
        .configure_axis(
            labelFont="Poppins",
            titleFont="Poppins",
            labelColor="#9AA1AD",
            labelFontSize=9,
            gridColor=GRID,
            gridOpacity=1,
            domain=False,
            ticks=False,
        )
    )
    return chart


def render_dealer_card(dealer, dealer_df):
    total_sales = dealer_df["No. of Sales"].sum()
    total_listings = dealer_df["Bike Listing"].sum()

    dated = dealer_df.dropna(subset=["Date Parsed"]).copy()
    if not dated.empty:
        plot_df = (
            dated.groupby("Date Parsed", as_index=False)
            .agg({"No. of Sales": "sum", "Bike Listing": "sum"})
            .sort_values("Date Parsed")
        )
    else:
        plot_df = pd.DataFrame()

    with st.container(border=True):
        st.markdown(
            f"""
            <div class="dealer-header">
                <div>
                    <div class="dealer-name">{dealer}</div>
                    <div class="data-note">Sales <span style="color:{ACCENT_RED};font-weight:700">●</span> &nbsp; Bike listings <span style="color:{LISTING_COLOUR};font-weight:700">●</span></div>
                </div>
                <div class="dealer-totals">
                    <div><div class="dealer-total-label">Total Sales</div><div class="dealer-total-value">{total_sales:,.0f}</div></div>
                    <div><div class="dealer-total-label">Bike Listings</div><div class="dealer-total-value">{total_listings:,.0f}</div></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        chart = dealer_chart(plot_df)
        if chart is None:
            st.caption("No valid visit dates are available for this dealer.")
        else:
            st.altair_chart(chart, use_container_width=True)


def dashboard():
    hide_streamlit_chrome()
    inject_dashboard_css()
    st_autorefresh(interval=60_000, key="staff_dashboard_auto_refresh")

    try:
        data, staff_members, errors = load_all_data()
    except Exception as exc:
        st.error(str(exc))
        st.info("Check the Apps Script deployment URL and API token in Streamlit Secrets.")
        st.stop()

    if not staff_members:
        st.error("Apps Script returned no configured staff members.")
        st.stop()

    # Sidebar navigation
    with st.sidebar:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_container_width=True)
        st.markdown('<div class="sidebar-label">DASHBOARD</div>', unsafe_allow_html=True)
        choices = ["overview"] + [p["id"] for p in staff_members]
        labels = {"overview": "⌂   Overview"}
        labels.update({p["id"]: f"▣   {p['name']}" for p in staff_members})
        selected_view = st.radio(
            "Navigation",
            choices,
            format_func=lambda x: labels[x],
            label_visibility="collapsed",
            key="dashboard_nav",
        )
        st.markdown(
            '<div class="privacy-note">Private Google Sheets are read through a protected Google Apps Script API. Sheet IDs and the API token are not stored in the public GitHub code.</div>',
            unsafe_allow_html=True,
        )

    # Top bar
    person = next((p for p in staff_members if p["id"] == selected_view), None)
    title = "Performance Overview" if selected_view == "overview" else person["name"]
    subtitle = (
        "Combined staff and dealer performance"
        if selected_view == "overview"
        else "Individual dealer visit and sales performance"
    )

    t1, t2, t3, t4 = st.columns([6.4, 1.7, 1.35, 1.05], vertical_alignment="center")
    with t1:
        st.markdown(f"<h1 style='font-size:30px;margin:0'>{title}</h1>", unsafe_allow_html=True)
        st.markdown(f'<div class="top-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    with t2:
        sync_time = datetime.now().astimezone().strftime("%I:%M %p").lstrip("0").lower()
        st.markdown(f'<div class="sync-text">Synced {sync_time}</div>', unsafe_allow_html=True)
    with t3:
        if st.button("Refresh data", use_container_width=True, key="refresh_data"):
            st.cache_data.clear()
            st.rerun()
    with t4:
        if st.button("Log out", use_container_width=True, key="logout"):
            st.session_state["authenticated"] = False
            st.session_state.pop("dashboard_nav", None)
            st.rerun()

    relevant_errors = errors if selected_view == "overview" else [e for e in errors if e[0] == selected_view]
    for _, staff_name, error in relevant_errors:
        st.warning(f"{staff_name}: {error}")

    view_df = data.copy()
    if selected_view != "overview":
        view_df = view_df[view_df["Staff ID"] == selected_view].copy()

    # Filters
    st.markdown('<div class="section-title">Filters</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1, 1, 2])
    valid_dates = view_df["Date Parsed"].dropna()
    min_date = valid_dates.min().date() if not valid_dates.empty else None
    max_date = valid_dates.max().date() if not valid_dates.empty else None

    with f1:
        date_from = st.date_input("From date", value=min_date, key=f"from_{selected_view}")
    with f2:
        date_to = st.date_input("To date", value=max_date, key=f"to_{selected_view}")
    with f3:
        dealer_search = st.text_input(
            "Dealer search", placeholder="Search dealer name", key=f"search_{selected_view}"
        )

    filtered = view_df.copy()
    if date_from is not None and "Date Parsed" in filtered:
        filtered = filtered[
            filtered["Date Parsed"].isna() | (filtered["Date Parsed"].dt.date >= date_from)
        ]
    if date_to is not None and "Date Parsed" in filtered:
        filtered = filtered[
            filtered["Date Parsed"].isna() | (filtered["Date Parsed"].dt.date <= date_to)
        ]
    if dealer_search.strip() and not filtered.empty:
        filtered = filtered[
            filtered["Dealer Name"].str.contains(dealer_search.strip(), case=False, na=False)
        ]

    st.markdown('<div class="section-title">Performance Summary</div>', unsafe_allow_html=True)
    render_kpis(filtered)

    st.markdown('<div class="section-title">Dealer Performance Summary</div>', unsafe_allow_html=True)
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
                "Dealer Name": st.column_config.TextColumn("Dealer Name"),
                "No. of Visits": st.column_config.NumberColumn("No. of Visits", format="%d"),
                "No. of Sales": st.column_config.NumberColumn("No. of Sales", format="%.0f"),
                "Bike Listing": st.column_config.NumberColumn("Bike Listing", format="%.0f"),
            },
        )

    st.markdown('<div class="section-title">Dealer Trends</div>', unsafe_allow_html=True)
    if filtered.empty:
        st.info("No dealer trend data to display.")
    else:
        dealers = sorted(filtered["Dealer Name"].dropna().unique(), key=str.lower)
        for i in range(0, len(dealers), 2):
            cols = st.columns(2)
            for j, dealer in enumerate(dealers[i : i + 2]):
                with cols[j]:
                    render_dealer_card(dealer, filtered[filtered["Dealer Name"] == dealer].copy())


if not is_authenticated():
    login_screen()
else:
    dashboard()
