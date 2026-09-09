import base64
import hmac
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import altair as alt
import requests
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Rider Gate DM Performance Dashboard",
    page_icon="👤",
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
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400,0,0&display=swap');
        html, body, [class*="css"] {{font-family:'Poppins', sans-serif;}}
        .stApp {{background:#FFFFFF;}}
        section[data-testid="stSidebar"] {{display:none !important;}}
        .block-container {{max-width:none !important; padding:0 !important;}}

        /* Full-screen split login, matching the Rider Gate dashboard reference. */
        div[data-testid="stHorizontalBlock"]:has(.login-panel) {{
            gap:0 !important;
            min-height:100vh;
            align-items:stretch !important;
        }}
        div[data-testid="stHorizontalBlock"]:has(.login-panel) > div[data-testid="stColumn"] {{
            min-height:100vh;
        }}
        div[data-testid="stHorizontalBlock"]:has(.login-panel) > div[data-testid="stColumn"]:first-child {{
            background:linear-gradient(145deg, {BRAND_RED} 0%, {BRAND_RED_DARK} 100%);
        }}
        div[data-testid="stHorizontalBlock"]:has(.login-panel) > div[data-testid="stColumn"]:nth-child(2) {{
            display:flex;
            align-items:center;
            justify-content:center;
            background:#fff;
        }}
        div[data-testid="stHorizontalBlock"]:has(.login-panel) > div[data-testid="stColumn"]:nth-child(2) > div {{
            width:min(520px, 76%);
        }}
        .login-panel {{
            min-height:100vh;
            padding:clamp(48px,7vw,100px);
            color:white;
            display:flex;
            flex-direction:column;
            justify-content:center;
        }}
        .login-panel img {{
            width:142px;
            border-radius:15px;
            margin-bottom:46px;
            box-shadow:0 9px 22px rgba(94,15,11,.18);
        }}
        .login-panel h1 {{
            font-size:clamp(30px,3vw,46px);
            line-height:1.12;
            margin:0 0 20px;
            font-weight:800;
            letter-spacing:-1.4px;
            max-width:560px;
        }}
        .login-panel p {{
            font-size:13px;
            line-height:1.85;
            opacity:.88;
            max-width:520px;
            margin:0;
        }}
        .login-form-title {{font-size:24px;font-weight:750;color:{INK};margin:0 0 24px;}}
        div[data-testid="stTextInput"] label p {{font-size:12px;font-weight:600;color:{MUTED};}}
        div[data-testid="stTextInput"] input {{
            border-radius:8px;border:1px solid #C9CED7;min-height:46px;background:#fff;
        }}
        div[data-testid="stFormSubmitButton"] button {{
            width:100%;background:{BRAND_RED};color:#fff;border:0;border-radius:8px;min-height:46px;font-weight:700;
        }}
        div[data-testid="stFormSubmitButton"] button:hover {{background:{BRAND_RED_DARK};color:#fff;border:0;}}
        .login-hint {{color:{MUTED};font-size:11px;margin-top:15px;}}
        @media(max-width:800px) {{
            div[data-testid="stHorizontalBlock"]:has(.login-panel) {{display:block !important;}}
            div[data-testid="stHorizontalBlock"]:has(.login-panel) > div[data-testid="stColumn"] {{min-height:auto; width:100% !important;}}
            .login-panel {{min-height:42vh;padding:36px 28px;}}
            .login-panel img {{width:105px;margin-bottom:25px;}}
            div[data-testid="stHorizontalBlock"]:has(.login-panel) > div[data-testid="stColumn"]:nth-child(2) {{min-height:58vh;padding:34px 0;}}
            div[data-testid="stHorizontalBlock"]:has(.login-panel) > div[data-testid="stColumn"]:nth-child(2) > div {{width:84%;}}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_dashboard_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400,0,0&display=swap');
        html, body, [class*="css"] {{font-family:'Poppins', sans-serif;}}
        .stApp {{background:{LIGHT_BG};}}
        .block-container {{padding-top:1.45rem;padding-bottom:3rem;max-width:1550px;}}

        /* Rider Gate sidebar - no Streamlit radio circles. */
        section[data-testid="stSidebar"] {{
            background:linear-gradient(180deg,{BRAND_RED} 0%, {BRAND_RED_DARK} 100%);
            border-right:0;
            min-width:270px !important;
            max-width:270px !important;
        }}
        section[data-testid="stSidebar"] > div {{padding-top:1.3rem;}}
        section[data-testid="stSidebar"] img {{
            display:block;margin:1.25rem auto 2.2rem auto;max-width:205px;border-radius:22px;
            box-shadow:0 8px 24px rgba(84,17,13,.14);
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {{
            background:#fff !important;color:{BRAND_RED} !important;border-radius:999px !important;
            width:42px;height:42px;border:0 !important;box-shadow:0 5px 15px rgba(55,15,12,.12);
        }}
        .sidebar-label {{
            font-size:10px;letter-spacing:.15em;color:rgba(255,255,255,.70);font-weight:700;
            margin:0 .8rem .55rem;text-transform:uppercase;
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] {{gap:.44rem;padding:0 .62rem;}}
        section[data-testid="stSidebar"] div[role="radiogroup"] label {{
            padding:.78rem .85rem !important;
            border-radius:12px !important;
            transition:.15s ease;
            font-weight:650 !important;
            background:transparent;
            min-height:48px;
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{background:rgba(255,255,255,.09);}}
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{background:rgba(255,255,255,.20);}}
        section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {{display:none !important;}}
        section[data-testid="stSidebar"] div[role="radiogroup"] label p,
        section[data-testid="stSidebar"] div[role="radiogroup"] label span,
        section[data-testid="stSidebar"] div[role="radiogroup"] label * {{
            color:#fff !important;
            font-family:'Poppins',sans-serif !important;
            font-size:14px !important;
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] label p::before {{
            font-family:'Material Symbols Rounded' !important;
            font-size:20px !important;
            font-weight:400 !important;
            vertical-align:-4px;
            margin-right:11px;
            content:'account_box';
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] label:first-child p::before {{content:'home';}}

        h1,h2,h3,p,span,label,button,input {{font-family:'Poppins', sans-serif;}}
        h1 {{color:{INK};letter-spacing:-.8px;}}
        h2,h3 {{color:{INK};}}
        .top-subtitle {{color:{MUTED};font-size:12px;margin-top:-5px;}}
        .sync-text {{color:#8991A0;font-size:11px;text-align:right;padding-top:10px;white-space:nowrap;}}

        div[data-testid="stButton"] button {{
            background:#fff;color:{INK};border:1px solid #E1E5EB;border-radius:12px;min-height:42px;
            font-weight:650;box-shadow:0 2px 8px rgba(32,41,56,.03);white-space:nowrap;font-size:12px;
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
        .dealer-name {{font-size:13px;font-weight:700;color:#5F6878;}}
        .dealer-totals {{display:flex;gap:14px;text-align:right;}}
        .dealer-total-label {{font-size:8px;text-transform:uppercase;letter-spacing:.05em;color:#A0A7B2;}}
        .dealer-total-value {{font-size:16px;font-weight:800;color:{ACCENT_RED};line-height:1.2;}}
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border:1px solid #E8EBF0 !important;border-radius:16px !important;
            background:
                linear-gradient(rgba(255,255,255,.96),rgba(255,255,255,.96)),
                repeating-linear-gradient(135deg,#F1F3F6 0,#F1F3F6 1px,transparent 1px,transparent 13px) !important;
            box-shadow:0 8px 25px rgba(32,41,56,.04);
        }}
        div[data-testid="stDataFrame"] {{border-radius:14px;overflow:hidden;border:1px solid #E7EAF0;}}
        div[data-testid="stDateInput"] input, div[data-testid="stTextInput"] input {{
            background:#fff;border-radius:10px;border:1px solid #DDE1E7;min-height:40px;
        }}
        .data-note {{font-size:10px;color:{MUTED};margin-top:2px;}}
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
                <h1>Rider Gate Staff<br>Performance Dashboard</h1>
                <p>Access dealer visits, bike listings and sales performance across Rider Gate staff and dealers in one secure dashboard.</p>
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

    plot_df = plot_df.copy()
    plot_df["No. of Sales"] = pd.to_numeric(plot_df["No. of Sales"], errors="coerce").fillna(0.0)
    plot_df["Bike Listing"] = pd.to_numeric(plot_df["Bike Listing"], errors="coerce").fillna(0.0)
    plot_df["Sales Tooltip"] = plot_df["No. of Sales"].map(lambda v: f"{v:,.0f}")
    plot_df["Listings Tooltip"] = plot_df["Bike Listing"].map(lambda v: f"{v:,.0f}")

    base = alt.Chart(plot_df).encode(
        x=alt.X(
            "Date Parsed:T",
            title=None,
            axis=alt.Axis(format="%-d %b", labelAngle=0, labelOverlap=True, tickCount=6),
        )
    )

    tooltip = [
        alt.Tooltip("Date Parsed:T", title="Date", format="%d %b %Y"),
        alt.Tooltip("Sales Tooltip:N", title="Sales"),
        alt.Tooltip("Listings Tooltip:N", title="Bike listings"),
    ]

    # Bike listings form the main shaded trend so the card keeps the strong red visual
    # shown in the Rider Gate reference even when sales numbers are much smaller.
    listing_area = base.mark_area(
        color=ACCENT_RED,
        opacity=0.13,
        interpolate="linear",
    ).encode(
        y=alt.Y("Bike Listing:Q", title=None),
        tooltip=tooltip,
    )

    listing_line = base.mark_line(
        color=ACCENT_RED,
        strokeWidth=2.6,
        point=alt.OverlayMarkDef(filled=True, color=ACCENT_RED, size=46),
    ).encode(
        y=alt.Y("Bike Listing:Q", title=None),
        tooltip=tooltip,
    )

    sales_line = base.mark_line(
        color=BRAND_RED_DARK,
        strokeWidth=2.4,
        point=alt.OverlayMarkDef(filled=True, color=BRAND_RED_DARK, size=44),
    ).encode(
        y=alt.Y("No. of Sales:Q", title=None),
        tooltip=tooltip,
    )

    chart = (
        alt.layer(listing_area, listing_line, sales_line)
        .resolve_scale(y="shared")
        .properties(height=220)
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
    dealer_df = dealer_df.copy()
    dealer_df["No. of Sales"] = pd.to_numeric(dealer_df["No. of Sales"], errors="coerce").fillna(0.0)
    dealer_df["Bike Listing"] = pd.to_numeric(dealer_df["Bike Listing"], errors="coerce").fillna(0.0)

    total_sales = dealer_df["No. of Sales"].sum()
    total_listings = dealer_df["Bike Listing"].sum()

    dated = dealer_df.dropna(subset=["Date Parsed"]).copy()
    if not dated.empty:
        plot_df = (
            dated.groupby("Date Parsed", as_index=False)[["No. of Sales", "Bike Listing"]]
            .sum()
            .sort_values("Date Parsed")
        )
        plot_df["No. of Sales"] = pd.to_numeric(plot_df["No. of Sales"], errors="coerce").fillna(0.0)
        plot_df["Bike Listing"] = pd.to_numeric(plot_df["Bike Listing"], errors="coerce").fillna(0.0)
    else:
        plot_df = pd.DataFrame(columns=["Date Parsed", "No. of Sales", "Bike Listing"])

    with st.container(border=True):
        st.markdown(
            f"""
            <div class="dealer-header">
                <div>
                    <div class="dealer-name">{dealer}</div>
                    <div class="data-note">
                        Sales <span style="color:{BRAND_RED_DARK};font-weight:800">●</span>
                        &nbsp;&nbsp; Bike listings <span style="color:{ACCENT_RED};font-weight:800">●</span>
                    </div>
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
        labels = {"overview": "Overview"}
        labels.update({p["id"]: p["name"] for p in staff_members})
        selected_view = st.radio(
            "Navigation",
            choices,
            format_func=lambda x: labels[x],
            label_visibility="collapsed",
            key="dashboard_nav",
        )

    # Top bar
    person = next((p for p in staff_members if p["id"] == selected_view), None)
    title = "Performance Overview" if selected_view == "overview" else person["name"]
    subtitle = (
        "Combined staff and dealer performance"
        if selected_view == "overview"
        else "Individual dealer visit and sales performance"
    )

    t1, t2, t3, t4 = st.columns([6.1, 1.65, 1.6, 1.3], vertical_alignment="center")
    with t1:
        st.markdown(f"<h1 style='font-size:30px;margin:0'>{title}</h1>", unsafe_allow_html=True)
        st.markdown(f'<div class="top-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    with t2:
        sync_time = datetime.now(ZoneInfo("Asia/Kuala_Lumpur")).strftime("%I:%M %p").lstrip("0").lower()
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
