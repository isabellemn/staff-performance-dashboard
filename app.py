import base64
import hmac
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import altair as alt
import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Rider Gate Staff Performance Dashboard",
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


MAP_BG_PATH = ROOT / "assets" / "dashboard_map_bg.png"


def logo_data_uri() -> str:
    if not LOGO_PATH.exists():
        return ""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def map_bg_data_uri() -> str:
    if not MAP_BG_PATH.exists():
        return ""
    encoded = base64.b64encode(MAP_BG_PATH.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def hide_streamlit_chrome(keep_sidebar_toggle=False):
    if keep_sidebar_toggle:
        header_css = """
        /* Keep the Streamlit header available because sidebar state is
           managed by Streamlit itself, but hide the unrelated controls. */
        header[data-testid="stHeader"] {
            display:block !important;
            background:transparent !important;
            height:3.25rem !important;
            min-height:3.25rem !important;
            pointer-events:none !important;
        }

        [data-testid="stToolbar"],
        [data-testid="stHeaderActionElements"],
        [data-testid="stStatusWidget"],
        [data-testid="stHeaderActionElements"] {
            display:none !important;
        }
        """
    else:
        header_css = """
        header[data-testid="stHeader"] {display:none !important;}
        """

    st.markdown(
        f"""
        <style>
        #MainMenu {{display:none !important;}}
        footer {{display:none !important;}}
        [data-testid="stDecoration"] {{display:none !important;}}
        {header_css}

        /* Remove Streamlit's image/chart/table toolbar. Altair point hover
           remains enabled. */
        [data-testid="stElementToolbar"] {{display:none !important;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_login_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family:'Poppins',sans-serif;
        }}

        .stApp {{
            background:#FFFFFF;
        }}

        section[data-testid="stSidebar"] {{
            display:none !important;
        }}

        /* LOGIN LAYOUT - V8
           No fixed positioning and no 50vw offset hacks.
           The page is built from two real Streamlit columns. */
        .block-container,
        [data-testid="stMainBlockContainer"] {{
            width:100vw !important;
            max-width:100vw !important;
            min-height:100vh !important;
            margin:0 !important;
            padding:0 !important;
        }}

        main[data-testid="stMain"] {{
            width:100% !important;
            min-height:100vh !important;
            margin:0 !important;
            padding:0 !important;
            background:#FFFFFF !important;
        }}

        /* The first horizontal block on the login page is the 50/50 layout. */
        [data-testid="stHorizontalBlock"] {{
            gap:0 !important;
            min-height:100vh !important;
            align-items:center !important;
        }}

        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
            padding:0 !important;
            margin:0 !important;
            min-width:0 !important;
        }}

        /* Left panel */
        .login-hero {{
            width:100%;
            min-height:100vh;
            box-sizing:border-box;
            overflow:hidden;
            background:
                radial-gradient(circle at 12% 16%, rgba(255,255,255,.12) 0 90px, transparent 91px),
                radial-gradient(circle at 82% 84%, rgba(255,255,255,.07) 0 180px, transparent 181px),
                linear-gradient(145deg,{BRAND_RED} 0%, {BRAND_RED_DARK} 100%);
            color:#FFFFFF;
            padding:clamp(54px,7vw,110px);
            display:flex;
            align-items:center;
        }}

        .login-hero-inner {{
            width:100%;
            max-width:580px;
            margin:0 auto;
        }}

        .login-logo {{
            display:block;
            width:128px;
            height:auto;
            border-radius:16px;
            margin:0 0 42px 0;
            box-shadow:0 12px 32px rgba(65,10,8,.20);
        }}

        .login-eyebrow {{
            font-size:11px;
            font-weight:700;
            text-transform:uppercase;
            letter-spacing:.18em;
            opacity:.72;
            margin-bottom:14px;
        }}

        .login-hero h1 {{
            margin:0 0 20px;
            font-size:clamp(34px,3.2vw,54px);
            line-height:1.08;
            letter-spacing:-1.8px;
            font-weight:800;
        }}

        .login-hero p {{
            margin:0;
            max-width:520px;
            font-size:13px;
            line-height:1.85;
            color:rgba(255,255,255,.82);
        }}

        /* Right column:
           constrain its complete vertical block to 460px and centre it.
           Support both current and older Streamlit test-id names. */
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) > div,
        [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2) > div {{
            width:100% !important;
            max-width:460px !important;
            margin-left:auto !important;
            margin-right:auto !important;
        }}

        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2),
        [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2) {{
            box-sizing:border-box !important;
            padding:48px clamp(42px,5vw,82px) !important;
        }}

        .login-form-title {{
            width:100%;
            margin:0 0 5px;
            font-size:28px;
            font-weight:800;
            letter-spacing:-.6px;
            color:{INK};
        }}

        .login-form-subtitle {{
            width:100%;
            margin:0 0 28px;
            color:{MUTED};
            font-size:12px;
            line-height:1.6;
        }}

        div[data-testid="stForm"] {{
            width:100% !important;
            max-width:460px !important;
            margin:0 !important;
            padding:0 !important;
            border:0 !important;
        }}

        div[data-testid="stForm"] label p {{
            font-size:11px !important;
            font-weight:650 !important;
            color:{MUTED} !important;
        }}

        div[data-testid="stTextInput"] input {{
            min-height:48px;
            border:1px solid #D7DCE4;
            border-radius:10px;
            background:#FFFFFF;
            color:{INK};
            box-shadow:none;
        }}

        div[data-testid="stTextInput"] input:focus {{
            border-color:{BRAND_RED};
            box-shadow:0 0 0 2px rgba(181,47,37,.08);
        }}

        div[data-testid="stFormSubmitButton"] button {{
            min-height:48px;
            width:100%;
            border:0 !important;
            border-radius:10px;
            background:{BRAND_RED} !important;
            color:#FFFFFF !important;
            font-weight:700;
            box-shadow:0 8px 18px rgba(181,47,37,.16);
        }}

        div[data-testid="stFormSubmitButton"] button:hover {{
            background:{BRAND_RED_DARK} !important;
            color:#FFFFFF !important;
        }}

        .login-hint {{
            width:100%;
            margin:16px 0 0;
            font-size:10px;
            color:#9AA1AD;
        }}

        @media (max-width:800px) {{
            [data-testid="stHorizontalBlock"] {{
                display:block !important;
                min-height:0 !important;
            }}

            .login-hero {{
                min-height:42vh;
                padding:38px 28px;
            }}

            .login-logo {{
                width:92px;
                margin-bottom:24px;
            }}

            .login-hero h1 {{
                font-size:31px;
            }}

            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2),
            [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2) {{
                min-height:58vh !important;
                padding:46px 28px !important;
                display:flex !important;
                align-items:center !important;
            }}

            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) > div,
            [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2) > div {{
                max-width:520px !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_dashboard_css():
    map_bg = map_bg_data_uri()

    if map_bg:
        background_css = f"""
        main[data-testid="stMain"]::before {{
            content:"";
            position:fixed;
            inset:0 0 0 auto;
            left:0;
            right:0;
            top:0;
            bottom:0;
            background-image:
                linear-gradient(rgba(246,248,251,.90), rgba(246,248,251,.90)),
                url('{map_bg}');
            background-repeat:no-repeat, repeat;
            background-position:center center, center top;
            background-size:cover, 1400px auto;
            opacity:1;
            pointer-events:none;
            z-index:0;
        }}

        main[data-testid="stMain"] > div {{
            position:relative;
            z-index:1;
        }}
        """
    else:
        background_css = ""

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family:'Poppins',sans-serif;
        }}

        .stApp {{
            background:{LIGHT_BG};
        }}

        main[data-testid="stMain"] {{
            position:relative !important;
            background:transparent !important;
        }}

        {background_css}

        /* Critical: the dashboard now uses the entire available width.
           When the sidebar is collapsed, the content expands with it. */
        .block-container {{
            width:100% !important;
            max-width:none !important;
            padding:1.45rem clamp(1rem,2.2vw,2.4rem) 3rem !important;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background:linear-gradient(180deg,{BRAND_RED} 0%, {BRAND_RED_DARK} 100%);
            border-right:0 !important;
        }}

        section[data-testid="stSidebar"] > div:first-child {{
            padding-top:1rem;
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {{
            background:#FFFFFF !important;
            color:{BRAND_RED} !important;
            border:0 !important;
            border-radius:999px !important;
            width:42px !important;
            height:42px !important;
            box-shadow:0 6px 18px rgba(55,15,12,.14);
        }}

        /* Keep the actual Streamlit toggle visible at all times. */
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {{
            visibility:visible !important;
            opacity:1 !important;
            display:block !important;
            pointer-events:auto !important;
            z-index:1000001 !important;
        }}

        /* COLLAPSED SIDEBAR
           Streamlit translates the entire sidebar off-screen when collapsed.
           Instead, keep only a 58px transparent fixed rail with the original
           toggle button. Because it is fixed, it takes no width from the main
           dashboard. Clicking the arrow restores the complete sidebar. */
        section[data-testid="stSidebar"][aria-expanded="false"] {{
            position:fixed !important;
            top:0 !important;
            left:0 !important;
            bottom:0 !important;
            width:58px !important;
            min-width:58px !important;
            max-width:58px !important;
            height:100vh !important;
            transform:none !important;
            transition:none !important;
            background:transparent !important;
            box-shadow:none !important;
            border:0 !important;
            z-index:1000000 !important;
            pointer-events:none !important;
        }}

        section[data-testid="stSidebar"][aria-expanded="false"]
        [data-testid="stSidebarContent"] {{
            width:58px !important;
            height:70px !important;
            overflow:visible !important;
            padding:0 !important;
            margin:0 !important;
            scrollbar-gutter:auto !important;
            pointer-events:none !important;
        }}

        section[data-testid="stSidebar"][aria-expanded="false"]
        [data-testid="stSidebarHeader"] {{
            width:58px !important;
            height:66px !important;
            min-height:66px !important;
            margin:0 !important;
            padding:0 !important;
            display:flex !important;
            align-items:center !important;
            justify-content:center !important;
            overflow:visible !important;
        }}

        section[data-testid="stSidebar"][aria-expanded="false"]
        [data-testid="stLogoSpacer"],
        section[data-testid="stSidebar"][aria-expanded="false"]
        [data-testid="stSidebarLogo"],
        section[data-testid="stSidebar"][aria-expanded="false"]
        [data-testid="stSidebarUserContent"],
        section[data-testid="stSidebar"][aria-expanded="false"]
        [data-testid="stSidebarResizeHandle"] {{
            display:none !important;
        }}

        section[data-testid="stSidebar"][aria-expanded="false"]
        [data-testid="stSidebarCollapseButton"] {{
            display:block !important;
            visibility:visible !important;
            opacity:1 !important;
            position:fixed !important;
            top:14px !important;
            left:14px !important;
            width:44px !important;
            height:44px !important;
            margin:0 !important;
            pointer-events:auto !important;
            z-index:1000002 !important;
        }}

        section[data-testid="stSidebar"][aria-expanded="false"]
        [data-testid="stSidebarCollapseButton"] button {{
            width:44px !important;
            height:44px !important;
            min-width:44px !important;
            min-height:44px !important;
            padding:0 !important;
            border-radius:999px !important;
            border:1px solid #E4E7EC !important;
            background:#FFFFFF !important;
            color:{BRAND_RED} !important;
            box-shadow:0 6px 18px rgba(32,41,56,.14) !important;
            pointer-events:auto !important;
        }}

        section[data-testid="stSidebar"][aria-expanded="false"]
        [data-testid="stSidebarCollapseButton"] svg {{
            transform:rotate(180deg) !important;
        }}

        section[data-testid="stSidebar"][aria-expanded="false"] ~
        main[data-testid="stMain"] .block-container {{
            padding-left:4.6rem !important;
        }}

        .sidebar-logo-wrap {{
            padding:1rem .8rem 1.9rem;
            text-align:center;
        }}

        .sidebar-logo-wrap img {{
            width:min(205px,88%);
            max-width:205px;
            height:auto;
            border-radius:22px;
            box-shadow:0 10px 25px rgba(67,13,10,.16);
        }}

        .sidebar-label {{
            margin:0 .85rem .65rem;
            color:rgba(255,255,255,.66);
            font-size:10px;
            font-weight:700;
            letter-spacing:.15em;
            text-transform:uppercase;
        }}

        /* Real buttons instead of radio buttons. */
        section[data-testid="stSidebar"] div[data-testid="stButton"] {{
            margin:.18rem .62rem !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stButton"] button {{
            width:100% !important;
            min-height:50px !important;
            justify-content:flex-start !important;
            border-radius:12px !important;
            padding:.68rem .85rem !important;
            border:0 !important;
            box-shadow:none !important;
            font-size:14px !important;
            font-weight:650 !important;
            transition:.15s ease;
        }}

        section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"] {{
            background:transparent !important;
            color:#FFFFFF !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"]:hover {{
            background:rgba(255,255,255,.09) !important;
            color:#FFFFFF !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {{
            background:rgba(255,255,255,.21) !important;
            color:#FFFFFF !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stButton"] button svg {{
            color:#FFFFFF !important;
            fill:#FFFFFF !important;
        }}

        h1,h2,h3,p,span,label,button,input {{
            font-family:'Poppins',sans-serif;
        }}

        h1,h2,h3 {{
            color:{INK};
        }}

        .top-subtitle {{
            color:{MUTED};
            font-size:12px;
            margin-top:-4px;
        }}

        .sync-text {{
            color:#8991A0;
            font-size:11px;
            text-align:right;
            padding-top:10px;
            white-space:nowrap;
        }}

        main div[data-testid="stButton"] button {{
            background:#FFFFFF;
            color:{INK};
            border:1px solid #E1E5EB;
            border-radius:12px;
            min-height:42px;
            font-weight:650;
            box-shadow:0 2px 8px rgba(32,41,56,.03);
            white-space:nowrap;
            font-size:12px;
        }}

        main div[data-testid="stButton"] button:hover {{
            border-color:#CDD2DA;
            color:{BRAND_RED};
            background:#FFFFFF;
        }}

        .kpi-card {{
            background:rgba(255,255,255,.90);
            backdrop-filter: blur(1.5px);
            border:1px solid #E7EAF0;
            border-radius:16px;
            padding:18px 20px;
            box-shadow:0 8px 24px rgba(32,41,56,.04);
            min-height:112px;
        }}

        .kpi-label {{
            font-size:11px;
            font-weight:650;
            color:{MUTED};
            text-transform:uppercase;
            letter-spacing:.05em;
        }}

        .kpi-value {{
            font-size:28px;
            font-weight:800;
            color:{INK};
            margin-top:8px;
            letter-spacing:-.8px;
        }}

        .kpi-note {{
            font-size:10px;
            color:#9AA1AD;
            margin-top:3px;
        }}

        .section-title {{
            font-size:17px;
            font-weight:750;
            color:{INK};
            margin:1.2rem 0 .65rem;
        }}

        .dealer-header {{
            display:flex;
            justify-content:space-between;
            align-items:flex-start;
            gap:15px;
            margin-bottom:2px;
        }}

        .dealer-name {{
            font-size:14px;
            font-weight:700;
            color:#5F6878;
            padding-top:3px;
        }}

        .dealer-totals {{
            display:flex;
            gap:16px;
            text-align:right;
        }}

        .dealer-total-label {{
            font-size:8px;
            text-transform:uppercase;
            letter-spacing:.05em;
            color:#A0A7B2;
        }}

        .dealer-total-value {{
            font-size:17px;
            font-weight:800;
            color:{ACCENT_RED};
            line-height:1.2;
        }}

        /* Dealer chart tabs */
        div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
            gap:5px !important;
            background:#F4F5F7 !important;
            border-radius:10px !important;
            padding:4px !important;
            width:max-content !important;
            margin:.4rem 0 .55rem !important;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"] {{
            min-height:32px !important;
            height:32px !important;
            padding:0 14px !important;
            border-radius:8px !important;
            color:#707988 !important;
            font-size:11px !important;
            font-weight:650 !important;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {{
            background:{BRAND_RED} !important;
            color:#FFFFFF !important;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
        div[data-testid="stTabs"] [data-baseweb="tab-border"] {{
            display:none !important;
        }}

        div[data-testid="stTabs"] [role="tabpanel"] {{
            padding-top:0 !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border:1px solid #E8EBF0 !important;
            border-radius:16px !important;
            background:
                linear-gradient(rgba(255,255,255,.96),rgba(255,255,255,.96)),
                repeating-linear-gradient(135deg,#F1F3F6 0,#F1F3F6 1px,transparent 1px,transparent 13px) !important;
            box-shadow:0 8px 25px rgba(32,41,56,.04);
        }}

        div[data-testid="stDataFrame"] {{
            border-radius:14px;
            overflow:hidden;
            border:1px solid #E7EAF0;
            background:rgba(255,255,255,.96);
            backdrop-filter: blur(1.5px);
        }}

        div[data-testid="stDateInput"] input,
        div[data-testid="stTextInput"] input {{
            background:rgba(255,255,255,.96);
            border-radius:10px;
            border:1px solid #DDE1E7;
            min-height:40px;
        }}

        @media(max-width:900px) {{
            .dealer-totals {{
                gap:8px;
            }}
        }}
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
    logo_html = (
        f'<img class="login-logo" src="{logo}" alt="Rider Gate logo">'
        if logo
        else ""
    )

    # Use two genuine 50/50 Streamlit columns. The left panel has a full
    # viewport-height hero, which makes the row 100vh. vertical_alignment
    # then centres the right-hand login content within that same height.
    left_col, right_col = st.columns(
        [1, 1],
        gap=None,
        vertical_alignment="center",
    )

    with left_col:
        st.markdown(
            f"""
            <div class="login-hero">
                <div class="login-hero-inner">
                    {logo_html}
                    <div class="login-eyebrow">Rider Gate</div>
                    <h1>Staff Performance<br>Dashboard</h1>
                    <p>
                        Access dealer visits, bike listings and staff sales
                        performance in one secure dashboard.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(
            '<div class="login-form-title">Dashboard Login</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="login-form-subtitle">'
            'Enter your password to access the staff performance dashboard.'
            '</div>',
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter password",
            )
            submitted = st.form_submit_button(
                "Login",
                use_container_width=True,
            )

        if submitted:
            expected = get_app_password()
            if not expected:
                st.error(
                    "The dashboard password has not been configured "
                    "in Streamlit Secrets."
                )
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
    data = data.rename(
        columns={
            "date": "Date of Visit",
            "dealer": "Dealer Name",
            "bikeListing": "Bike Listing",
            "sales": "No. of Sales",
            "staffId": "Staff ID",
            "staffName": "Staff Name",
        }
    )

    for col in ["Date of Visit", "Dealer Name", "Staff ID", "Staff Name"]:
        if col not in data:
            data[col] = ""
        data[col] = data[col].fillna("").astype(str).str.strip()

    for col in ["Bike Listing", "No. of Sales"]:
        if col not in data:
            data[col] = 0
        data[col] = clean_numeric_series(data[col])

    data["Date Parsed"] = pd.to_datetime(
        data["Date of Visit"],
        errors="coerce",
        dayfirst=True,
    )

    return data[columns], staff_members, errors



def clean_numeric_series(series):
    """Convert spreadsheet values to numbers and guarantee no NaN values.

    Handles ordinary numbers, blanks, N/A-style text and comma-formatted
    values. Missing/non-numeric values are treated as 0 for dashboard totals
    and trend points.
    """
    if series is None:
        return pd.Series(dtype="float64")

    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(",", "", regex=False)
        .replace({
            "": "0",
            "nan": "0",
            "NaN": "0",
            "None": "0",
            "N/A": "0",
            "n/a": "0",
            "NA": "0",
            "-": "0",
        })
    )
    return pd.to_numeric(cleaned, errors="coerce").fillna(0.0)


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


def dealer_chart(plot_df, metric):
    """Render either Sales or Bike Listing using safe internal field names.

    Hovering either graph always shows the complete values for the date.
    """
    if plot_df.empty:
        return None

    plot_df = plot_df.copy()
    plot_df["Sales"] = clean_numeric_series(plot_df["Sales"])
    plot_df["BikeListings"] = clean_numeric_series(plot_df["BikeListings"])

    visible_field = "Sales" if metric == "Sales" else "BikeListings"

    tooltip = [
        alt.Tooltip(field="Date", type="temporal", title="Date", format="%d %b %Y"),
        alt.Tooltip(field="Sales", type="quantitative", title="Sales", format=",.0f"),
        alt.Tooltip(
            field="BikeListings",
            type="quantitative",
            title="Bike listings",
            format=",.0f",
        ),
    ]

    base = alt.Chart(plot_df).encode(
        x=alt.X(
            field="Date",
            type="temporal",
            title=None,
            axis=alt.Axis(
                format="%-d %b",
                labelAngle=0,
                labelOverlap=True,
                tickCount=6,
            ),
        )
    )

    area = base.mark_area(
        color=ACCENT_RED,
        opacity=0.14,
        interpolate="linear",
    ).encode(
        y=alt.Y(
            field=visible_field,
            type="quantitative",
            title=None,
            scale=alt.Scale(zero=True),
        )
    )

    line = base.mark_line(
        color=ACCENT_RED,
        strokeWidth=2.8,
        point=alt.OverlayMarkDef(
            filled=True,
            color=ACCENT_RED,
            size=52,
            stroke="white",
            strokeWidth=1.4,
        ),
    ).encode(
        y=alt.Y(
            field=visible_field,
            type="quantitative",
            title=None,
            scale=alt.Scale(zero=True),
        ),
        tooltip=tooltip,
    )

    return (
        alt.layer(area, line)
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


def render_dealer_card(dealer, dealer_df):
    dealer_df = dealer_df.copy()
    dealer_df["No. of Sales"] = clean_numeric_series(dealer_df["No. of Sales"])
    dealer_df["Bike Listing"] = clean_numeric_series(dealer_df["Bike Listing"])

    total_sales = dealer_df["No. of Sales"].sum()
    total_listings = dealer_df["Bike Listing"].sum()

    dated = dealer_df.dropna(subset=["Date Parsed"]).copy()
    if not dated.empty:
        grouped = (
            dated.groupby("Date Parsed", as_index=False)[
                ["No. of Sales", "Bike Listing"]
            ]
            .sum()
            .sort_values("Date Parsed")
        )

        # Altair/Vega-Lite uses dots in field names to represent nested paths.
        # Rename plotting fields so "No. of Sales" cannot be misread.
        plot_df = grouped.rename(
            columns={
                "Date Parsed": "Date",
                "No. of Sales": "Sales",
                "Bike Listing": "BikeListings",
            }
        )
        plot_df["Sales"] = clean_numeric_series(plot_df["Sales"])
        plot_df["BikeListings"] = clean_numeric_series(plot_df["BikeListings"])
    else:
        plot_df = pd.DataFrame(columns=["Date", "Sales", "BikeListings"])

    with st.container(border=True):
        st.markdown(
            f"""
            <div class="dealer-header">
                <div class="dealer-name">{dealer}</div>
                <div class="dealer-totals">
                    <div>
                        <div class="dealer-total-label">Total Sales</div>
                        <div class="dealer-total-value">{total_sales:,.0f}</div>
                    </div>
                    <div>
                        <div class="dealer-total-label">Bike Listings</div>
                        <div class="dealer-total-value">{total_listings:,.0f}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if plot_df.empty:
            st.caption("No valid visit dates are available for this dealer.")
            return

        sales_tab, listing_tab = st.tabs(["Sales", "Bike Listing"])

        with sales_tab:
            sales_chart = dealer_chart(plot_df, "Sales")
            if sales_chart is not None:
                st.altair_chart(sales_chart, use_container_width=True)

        with listing_tab:
            listing_chart = dealer_chart(plot_df, "Bike Listing")
            if listing_chart is not None:
                st.altair_chart(listing_chart, use_container_width=True)


def set_navigation(view_id: str):
    st.session_state["dashboard_view"] = view_id


def render_sidebar(staff_members):
    logo = logo_data_uri()

    with st.sidebar:
        if logo:
            st.markdown(
                f'<div class="sidebar-logo-wrap"><img src="{logo}" alt="Rider Gate logo"></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="sidebar-label">DASHBOARD</div>',
            unsafe_allow_html=True,
        )

        if "dashboard_view" not in st.session_state:
            st.session_state["dashboard_view"] = "overview"

        current = st.session_state["dashboard_view"]

        if st.button(
            "Overview",
            key="nav_overview",
            type="primary" if current == "overview" else "secondary",
            icon=":material/home:",
            use_container_width=True,
        ):
            set_navigation("overview")
            st.rerun()

        for person in staff_members:
            view_id = person["id"]
            if st.button(
                person["name"],
                key=f"nav_{view_id}",
                type="primary" if current == view_id else "secondary",
                icon=":material/account_box:",
                use_container_width=True,
            ):
                set_navigation(view_id)
                st.rerun()

    return st.session_state["dashboard_view"]


def dashboard():
    hide_streamlit_chrome(keep_sidebar_toggle=True)
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

    selected_view = render_sidebar(staff_members)

    # Guard against a staff member being removed from Apps Script while
    # still being selected in the user's browser session.
    valid_views = {"overview"} | {p["id"] for p in staff_members}
    if selected_view not in valid_views:
        selected_view = "overview"
        st.session_state["dashboard_view"] = "overview"

    person = next(
        (p for p in staff_members if p["id"] == selected_view),
        None,
    )

    title = (
        "Performance Overview"
        if selected_view == "overview"
        else person["name"]
    )

    subtitle = (
        "Combined staff and dealer performance"
        if selected_view == "overview"
        else "Individual dealer visit and sales performance"
    )

    t1, t2, t3, t4 = st.columns(
        [6.2, 1.6, 1.55, 1.25],
        vertical_alignment="center",
    )

    with t1:
        st.markdown(
            f"<h1 style='font-size:30px;margin:0'>{title}</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="top-subtitle">{subtitle}</div>',
            unsafe_allow_html=True,
        )

    with t2:
        sync_time = (
            datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))
            .strftime("%I:%M %p")
            .lstrip("0")
            .lower()
        )
        st.markdown(
            f'<div class="sync-text">Synced {sync_time}</div>',
            unsafe_allow_html=True,
        )

    with t3:
        if st.button(
            "Refresh data",
            use_container_width=True,
            key="refresh_data",
            icon=":material/refresh:",
        ):
            st.cache_data.clear()
            st.rerun()

    with t4:
        if st.button(
            "Log out",
            use_container_width=True,
            key="logout",
            icon=":material/logout:",
        ):
            st.session_state["authenticated"] = False
            st.session_state.pop("dashboard_view", None)
            st.rerun()

    relevant_errors = (
        errors
        if selected_view == "overview"
        else [
            e for e in errors
            if e.get("staffId") == selected_view
        ]
    )

    for err in relevant_errors:
        if isinstance(err, dict):
            staff_name = err.get("staffName", "Staff")
            message = err.get("error", "Unknown data error.")
        else:
            # Compatibility with older payload shapes.
            try:
                _, staff_name, message = err
            except Exception:
                staff_name, message = "Staff", str(err)
        st.warning(f"{staff_name}: {message}")

    view_df = data.copy()
    if selected_view != "overview":
        view_df = view_df[
            view_df["Staff ID"] == selected_view
        ].copy()

    # Filters
    st.markdown(
        '<div class="section-title">Filters</div>',
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns([1, 1, 2])

    valid_dates = view_df["Date Parsed"].dropna()
    min_date = (
        valid_dates.min().date()
        if not valid_dates.empty
        else None
    )
    max_date = (
        valid_dates.max().date()
        if not valid_dates.empty
        else None
    )

    with f1:
        date_from = st.date_input(
            "From date",
            value=min_date,
            key=f"from_{selected_view}",
        )

    with f2:
        date_to = st.date_input(
            "To date",
            value=max_date,
            key=f"to_{selected_view}",
        )

    with f3:
        dealer_search = st.text_input(
            "Dealer search",
            placeholder="Search dealer name",
            key=f"search_{selected_view}",
        )

    filtered = view_df.copy()

    if date_from is not None:
        filtered = filtered[
            filtered["Date Parsed"].isna()
            | (filtered["Date Parsed"].dt.date >= date_from)
        ]

    if date_to is not None:
        filtered = filtered[
            filtered["Date Parsed"].isna()
            | (filtered["Date Parsed"].dt.date <= date_to)
        ]

    if dealer_search.strip() and not filtered.empty:
        filtered = filtered[
            filtered["Dealer Name"].str.contains(
                dealer_search.strip(),
                case=False,
                na=False,
            )
        ]

    st.markdown(
        '<div class="section-title">Performance Summary</div>',
        unsafe_allow_html=True,
    )
    render_kpis(filtered)

    st.markdown(
        '<div class="section-title">Dealer Performance Summary</div>',
        unsafe_allow_html=True,
    )

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
            .sort_values(
                ["No. of Sales", "Bike Listing", "Dealer Name"],
                ascending=[False, False, True],
            )
            .reset_index(drop=True)
        )

        # Explicit 1-based row numbering.
        summary.insert(0, "No.", range(1, len(summary) + 1))

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True,
            column_config={
                "No.": st.column_config.NumberColumn(
                    "No.",
                    format="%d",
                    width="small",
                ),
                "Dealer Name": st.column_config.TextColumn(
                    "Dealer Name"
                ),
                "No. of Visits": st.column_config.NumberColumn(
                    "No. of Visits",
                    format="%d",
                ),
                "No. of Sales": st.column_config.NumberColumn(
                    "No. of Sales",
                    format="%.0f",
                ),
                "Bike Listing": st.column_config.NumberColumn(
                    "Bike Listing",
                    format="%.0f",
                ),
            },
        )

    st.markdown(
        '<div class="section-title">Dealer Trends</div>',
        unsafe_allow_html=True,
    )

    if filtered.empty:
        st.info("No dealer trend data to display.")
    else:
        dealers = sorted(
            filtered["Dealer Name"].dropna().unique(),
            key=str.lower,
        )

        for i in range(0, len(dealers), 2):
            cols = st.columns(2)
            for j, dealer in enumerate(dealers[i:i + 2]):
                with cols[j]:
                    render_dealer_card(
                        dealer,
                        filtered[
                            filtered["Dealer Name"] == dealer
                        ].copy(),
                    )


if not is_authenticated():
    login_screen()
else:
    dashboard()
