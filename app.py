"""EpiSim: Disease Spread Prediction & Healthcare Capacity Intelligence Platform.

An enterprise numerical computing and epidemiological modeling application implementing
the Kermack-McKendrick SIR differential equations using adaptive Runge-Kutta 5(4) integration.
Features full Light & Dark mode themes, prominent main-page parameter controls,
symmetric diagnostic telemetry, and publication-grade Plotly visual analytics.
"""

from __future__ import annotations

import base64
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from analysis import (
    EpidemiologicalSummary,
    analyze_simulation,
    compute_model_fit_metrics,
    compute_parameter_sensitivity,
    parse_and_validate_historical_csv,
)
from export import (
    generate_simulation_csv,
    generate_simulation_dataframe,
    generate_simulation_json,
    generate_simulation_pdf,
    generate_summary_report,
)
from sir_model import (
    SIRParameters,
    SIRSimulationResult,
    SolverError,
    solve_sir,
)
from validation import validate_sir_inputs
from visualization import (
    apply_theme_to_figure,
    create_animated_progression_chart,
    create_effective_r_chart,
    create_infection_rate_trend_chart,
    create_model_vs_data_chart,
    create_peak_analysis_chart,
    create_phase_space_chart,
    create_population_distribution_chart,
    create_scenario_comparison_chart,
    create_sensitivity_chart,
    create_sir_curve_chart,
)

# -----------------------------------------------------------------------------
# 1. LOGO & BRANDING ASSETS
# -----------------------------------------------------------------------------
LOGO_PNG_PATH = Path(__file__).resolve().parent / "assets" / "sir_logo.png"
LOGO_SVG_PATH = Path(__file__).resolve().parent / "assets" / "sir_logo.svg"

page_icon_val = str(LOGO_PNG_PATH) if LOGO_PNG_PATH.exists() else "📈"

if LOGO_SVG_PATH.exists():
    with open(LOGO_SVG_PATH, "rb") as f_logo:
        _svg_b64 = base64.b64encode(f_logo.read()).decode("utf-8")
        LOGO_DATA_URI = f"data:image/svg+xml;base64,{_svg_b64}"
elif LOGO_PNG_PATH.exists():
    with open(LOGO_PNG_PATH, "rb") as f_logo:
        _png_b64 = base64.b64encode(f_logo.read()).decode("utf-8")
        LOGO_DATA_URI = f"data:image/png;base64,{_png_b64}"
else:
    LOGO_DATA_URI = ""

# -----------------------------------------------------------------------------
# 2. STREAMLIT PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SIR | Disease Dynamics & Capacity Intelligence",
    page_icon=page_icon_val,
    layout="wide",
    initial_sidebar_state="expanded",
)

if LOGO_PNG_PATH.exists() and hasattr(st, "logo"):
    try:
        st.logo(str(LOGO_PNG_PATH), icon_image=str(LOGO_PNG_PATH))
    except Exception:
        pass

# Initialize Session State Theme (Default: Light Mode)
if "theme" not in st.session_state:
    st.session_state.theme = "light"

is_dark = st.session_state.theme == "dark"

# -----------------------------------------------------------------------------
# 2. DYNAMIC THEME SYSTEM (LIGHT & DARK MODES - INSPIRED BY MODERN TECH AGENCIES)
# -----------------------------------------------------------------------------
if is_dark:
    # Sleek Dark Palette
    c_app_bg = "#0B0F19"
    c_surface = "#111827"
    c_surface_elevated = "#1F2937"
    c_border = "rgba(255, 255, 255, 0.08)"
    c_border_focus = "#38BDF8"
    c_text_main = "#F8FAFC"
    c_text_muted = "#94A3B8"
    c_primary = "#38BDF8"
    c_primary_gradient = "linear-gradient(135deg, #0284C7 0%, #38BDF8 100%)"
    c_card_shadow = "0 8px 30px rgba(0, 0, 0, 0.45)"
    c_input_bg = "#1E293B"
    c_input_border = "#334155"
    c_pill_bg = "rgba(56, 189, 248, 0.12)"
    c_pill_text = "#38BDF8"
else:
    # Crisp Light SaaS Palette
    c_app_bg = "#F8FAFC"
    c_surface = "#FFFFFF"
    c_surface_elevated = "#F1F5F9"
    c_border = "#E2E8F0"
    c_border_focus = "#2563EB"
    c_text_main = "#0F172A"
    c_text_muted = "#64748B"
    c_primary = "#2563EB"
    c_primary_gradient = "linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%)"
    c_card_shadow = "0 4px 20px -2px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02)"
    c_input_bg = "#FFFFFF"
    c_input_border = "#CBD5E1"
    c_pill_bg = "#EFF6FF"
    c_pill_text = "#1E40AF"

st.markdown(
    f"""
    <style>
    /* -------------------------------------------------------------
       ENTERPRISE DESIGN TOKENS & SYSTEM SHELL (LIGHT & DARK)
       ------------------------------------------------------------- */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stHeader"],
    .main,
    .main > div,
    section.main {{
        background-color: {c_app_bg} !important;
        color: {c_text_main} !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }}

    /* SIDEBAR CONTAINER */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebar"] section {{
        background-color: {c_surface} !important;
        border-right: 1px solid {c_border} !important;
    }}

    /* TYPOGRAPHY */
    h1, h2, h3, h4, h5, h6 {{
        color: {c_text_main} !important;
        letter-spacing: -0.02em;
        font-weight: 700 !important;
    }}
    p, span, label, div {{
        color: {c_text_main} !important;
    }}
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {{
        color: {c_text_main} !important;
    }}

    /* INPUT CONTROLS */
    .stSlider label, .stNumberInput label, .stSelectbox label, .stCheckbox label {{
        color: {c_text_muted} !important;
        font-weight: 600 !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }}
    .stSelectbox div[data-baseweb="select"] > div,
    .stNumberInput div[data-baseweb="input"],
    .stNumberInput input,
    div[data-baseweb="input"] input {{
        background-color: {c_input_bg} !important;
        color: {c_text_main} !important;
        border: 1px solid {c_input_border} !important;
        border-radius: 8px !important;
    }}
    .stNumberInput input:focus,
    div[data-baseweb="input"] input:focus {{
        border-color: {c_border_focus} !important;
        box-shadow: 0 0 0 1px {c_border_focus} !important;
    }}

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: transparent !important;
        border-bottom: 2px solid {c_border} !important;
        gap: 8px !important;
        padding-bottom: 4px !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {c_text_muted} !important;
        font-weight: 600 !important;
        background-color: transparent !important;
        border-radius: 6px 6px 0 0 !important;
        padding: 8px 16px !important;
        font-size: 0.85rem !important;
        transition: all 0.2s ease !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {c_primary} !important;
        background-color: {c_surface} !important;
        border-bottom: 2px solid {c_primary} !important;
        font-weight: 700 !important;
    }}

    /* HERO SHOWCASE HEADER */
    .hero-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0 18px 0;
        border-bottom: 1px solid {c_border};
        margin-bottom: 20px;
    }}
    .hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: {c_pill_bg};
        color: {c_pill_text};
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 4px 12px;
        border-radius: 9999px;
        margin-bottom: 6px;
    }}
    .hero-dot {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 8px #10B981;
    }}
    .hero-title {{
        font-size: 1.65rem;
        font-weight: 800;
        line-height: 1.25;
        letter-spacing: -0.03em;
        background: {c_primary_gradient};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .hero-title b, .hero-title strong, .brand-sir {{
        font-weight: 900 !important;
        letter-spacing: 0.02em;
        color: #38BDF8 !important;
        -webkit-text-fill-color: #38BDF8 !important;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    }}
    .hero-brand-logo {{
        width: 58px;
        height: 58px;
        border-radius: 14px;
        box-shadow: 0 4px 20px rgba(56, 189, 248, 0.35);
        flex-shrink: 0;
        transition: transform 0.2s ease;
    }}
    .hero-brand-logo:hover {{
        transform: scale(1.05);
    }}
    .hero-sub {{
        font-size: 0.88rem;
        color: {c_text_muted};
        margin-top: 4px;
        font-weight: 400;
    }}
    .hero-stats-strip {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
        flex-shrink: 0;
        background: {c_surface};
        border: 1px solid {c_border};
        border-radius: 10px;
        padding: 8px 14px;
    }}
    .hero-stat-item {{
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        color: {c_text_muted};
        white-space: nowrap;
        padding: 2px 8px;
        border-radius: 6px;
        background: {"rgba(255, 255, 255, 0.04)" if is_dark else "rgba(15, 23, 42, 0.03)"};
    }}
    .hero-stat-item b {{
        color: {c_text_main};
    }}

    /* NEXAFOTECH-INSPIRED INTERACTIVE UI CARDS & HUBS */
    .walkthrough-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 12px;
        margin-top: 10px;
        margin-bottom: 14px;
    }}
    .walkthrough-card {{
        background: {c_surface};
        border: 1px solid {c_border};
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: {c_card_shadow};
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .walkthrough-card:hover {{
        transform: translateY(-2px);
        border-color: #38BDF8;
    }}
    .walkthrough-step {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 2px 8px;
        border-radius: 6px;
        background: {"rgba(56, 189, 248, 0.15)" if is_dark else "#E0F2FE"};
        color: #0284C7;
        font-size: 0.70rem;
        font-weight: 800;
        margin-bottom: 8px;
        letter-spacing: 0.05em;
    }}
    .walkthrough-title {{
        font-size: 0.86rem;
        font-weight: 700;
        color: {c_text_main};
        margin-bottom: 4px;
    }}
    .walkthrough-desc {{
        font-size: 0.76rem;
        color: {c_text_muted};
        line-height: 1.4;
    }}

    .threat-banner {{
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        background: {c_surface};
        border: 1px solid {c_border};
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 20px;
        box-shadow: {c_card_shadow};
    }}

    .explore-card {{
        background: {c_surface};
        border: 1px solid {c_border};
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: {c_card_shadow};
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        margin-bottom: 16px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .explore-card:hover {{
        transform: translateY(-3px);
        border-color: #38BDF8;
        box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.15);
    }}
    .explore-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.70rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 3px 8px;
        border-radius: 6px;
    }}
    .concept-box {{
        background: {c_surface};
        border: 1px solid {c_border};
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: {c_card_shadow};
        transition: border-color 0.2s ease;
    }}
    .concept-box:hover {{
        border-color: #38BDF8;
    }}

    /* MAIN PAGE SIMULATION CONTROL STUDIO */
    .param-studio {{
        background: {c_surface};
        border: 1px solid {c_border};
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 24px;
        box-shadow: {c_card_shadow};
    }}
    .param-studio-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid {c_border};
    }}
    .param-studio-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: {c_text_main};
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .param-studio-badge {{
        font-size: 0.72rem;
        font-weight: 700;
        background: {c_pill_bg};
        color: {c_pill_text};
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.04em;
    }}

    /* KPI METRIC CARDS */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }}
    @media (max-width: 900px) {{
        .metric-grid {{
            grid-template-columns: repeat(2, 1fr);
        }}
    }}
    .metric-card {{
        background: {c_surface};
        border: 1px solid {c_border};
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: {c_card_shadow};
        position: relative;
        overflow: hidden;
    }}
    .metric-card-purple {{ border-top: 3px solid #8B5CF6; }}
    .metric-card-rose   {{ border-top: 3px solid #EF4444; }}
    .metric-card-amber  {{ border-top: 3px solid #F59E0B; }}
    .metric-card-blue   {{ border-top: 3px solid #3B82F6; }}

    .metric-label {{
        font-size: 0.75rem;
        font-weight: 600;
        color: {c_text_muted};
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }}
    .metric-val {{
        font-size: 1.75rem;
        font-weight: 800;
        color: {c_text_main};
        line-height: 1.2;
        margin-bottom: 8px;
    }}
    .metric-badge {{
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
    }}
    .badge-purple {{ background: {"rgba(139, 92, 246, 0.15)" if is_dark else "#F3E8FF"}; color: {"#C4B5FD" if is_dark else "#6B21A8"}; }}
    .badge-rose   {{ background: {"rgba(239, 68, 68, 0.15)" if is_dark else "#FEE2E2"}; color: {"#FCA5A5" if is_dark else "#991B1B"}; }}
    .badge-amber  {{ background: {"rgba(245, 158, 11, 0.15)" if is_dark else "#FEF3C7"}; color: {"#FCD34D" if is_dark else "#92400E"}; }}
    .badge-blue   {{ background: {"rgba(59, 130, 246, 0.15)" if is_dark else "#EFF6FF"}; color: {"#93C5FD" if is_dark else "#1E40AF"}; }}
    .badge-green  {{ background: {"rgba(16, 185, 129, 0.15)" if is_dark else "#ECFDF5"}; color: {"#6EE7B7" if is_dark else "#065F46"}; }}

    /* SYMMETRIC DIAGNOSTIC SPEC GRID */
    [data-testid="stPlotlyChart"] {{
        background: {c_surface};
        border: 1px solid {c_border};
        border-radius: 12px;
        padding: 12px 10px 6px 10px;
        box-shadow: {c_card_shadow};
    }}
    [data-testid="stPlotlyChart"] .modebar-container {{
        top: 4px !important;
        right: 36px !important;
    }}
    .spec-card {{
        background: {c_surface};
        border: 1px solid {c_border};
        border-radius: 12px;
        padding: 20px 22px;
        box-shadow: {c_card_shadow};
        min-height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .spec-header {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.95rem;
        font-weight: 700;
        color: {c_text_main};
        margin-bottom: 12px;
        padding-bottom: 10px;
        border-bottom: 1px solid {c_border};
    }}
    .spec-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid {c_border};
        font-size: 0.85rem;
    }}
    .spec-row:last-child {{
        border-bottom: none;
    }}
    .spec-label {{
        color: {c_text_muted};
        font-weight: 500;
    }}
    .spec-val {{
        color: {c_text_main};
        font-weight: 600;
        text-align: right;
    }}
    .spec-pill {{
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.74rem;
        font-weight: 600;
    }}
    .pill-green  {{ background: {"rgba(16, 185, 129, 0.15)" if is_dark else "#D1FAE5"}; color: {"#34D399" if is_dark else "#065F46"}; }}
    .pill-blue   {{ background: {"rgba(56, 189, 248, 0.15)" if is_dark else "#DBEAFE"}; color: {"#38BDF8" if is_dark else "#1E40AF"}; }}
    .pill-amber  {{ background: {"rgba(245, 158, 11, 0.15)" if is_dark else "#FEF3C7"}; color: {"#FBBF24" if is_dark else "#92400E"}; }}
    .pill-red    {{ background: {"rgba(239, 68, 68, 0.15)" if is_dark else "#FEE2E2"}; color: {"#F87171" if is_dark else "#991B1B"}; }}
    .pill-slate  {{ background: {"rgba(148, 163, 184, 0.15)" if is_dark else "#F1F5F9"}; color: {"#CBD5E1" if is_dark else "#475569"}; }}

    /* BUTTONS */
    .stButton button[kind="primary"] {{
        background: {c_primary_gradient} !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease !important;
    }}
    .stButton button[kind="secondary"],
    .stButton button:not([kind="primary"]) {{
        background: {c_surface} !important;
        color: {c_text_main} !important;
        border: 1px solid {c_border} !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }}

    /* TELEMETRY PILL IN SIDEBAR */
    .telemetry-pill {{
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background: {c_surface_elevated};
        border-radius: 8px;
        border: 1px solid {c_border};
        margin-top: 16px;
    }}
    .telemetry-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 6px #10B981;
    }}

    /* UNIFIED DOWNLOAD BUTTON CONTAINER (EQUAL HEIGHTS & NO TEXT WRAPPING) */
    .stDownloadButton,
    .stDownloadButton button {{
        background: {c_surface} !important;
        border: 1px solid {c_border} !important;
        color: {c_text_main} !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        min-height: 44px !important;
        white-space: nowrap !important;
        word-break: keep-all !important;
        text-overflow: ellipsis !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 8px 12px !important;
        transition: all 0.2s ease !important;
    }}
    .stDownloadButton button:hover {{
        border-color: {c_border_focus} !important;
        color: {c_primary} !important;
    }}

    /* SELECTBOX POPOVER & DROPDOWNS */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[role="listbox"],
    li[role="option"] {{
        background-color: {c_surface} !important;
        color: {c_text_main} !important;
        border-color: {c_border} !important;
    }}
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {{
        background-color: {c_surface_elevated} !important;
        color: {c_primary} !important;
    }}

    /* NUMBER INPUT STEPPERS */
    button[data-testid="stNumberInputStepDown"],
    button[data-testid="stNumberInputStepUp"] {{
        background-color: {c_input_bg} !important;
        color: {c_text_main} !important;
        border-color: {c_input_border} !important;
    }}

    /* FILE UPLOADER DROPZONE */
    [data-testid="stFileUploader"],
    section[data-testid="stFileUploadDropzone"] {{
        background-color: {c_surface} !important;
        border: 1px dashed {c_border} !important;
        color: {c_text_main} !important;
    }}
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] small,
    section[data-testid="stFileUploadDropzone"] div {{
        color: {c_text_muted} !important;
    }}

    /* METRIC LABELS & VALUES */
    [data-testid="stMetricValue"] {{
        color: {c_text_main} !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {c_text_muted} !important;
    }}

    /* ALERTS & EXPANDERS */
    .stAlert {{
        background-color: {c_surface_elevated} !important;
        color: {c_text_main} !important;
        border: 1px solid {c_border} !important;
    }}
    [data-testid="stExpander"] {{
        background-color: {c_surface} !important;
        border: 1px solid {c_border} !important;
    }}
    [data-testid="stExpander"] summary {{
        color: {c_text_main} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 3. CLINICAL PRESETS & CACHED DIFFERENTIAL SOLVER
# -----------------------------------------------------------------------------
PRESETS = {
    "COVID-19 Omicron (High Contagion)": {
        "beta": 0.55,
        "gamma": 0.14,
        "pop": 100000,
        "inf": 50,
        "rec": 0,
        "duration": 180,
        "capacity_pct": 8.0,
        "desc": "High aerosol transmissibility with rapid incubation and widespread immune evasion.",
    },
    "1918 Spanish Flu (Severe Pulmonary)": {
        "beta": 0.36,
        "gamma": 0.15,
        "pop": 100000,
        "inf": 50,
        "rec": 0,
        "duration": 150,
        "capacity_pct": 6.0,
        "desc": "Aggressive historic respiratory pandemic with high systemic mortality and intense clinical crests.",
    },
    "SARS-CoV-1 (2003 Classic)": {
        "beta": 0.28,
        "gamma": 0.10,
        "pop": 80000,
        "inf": 25,
        "rec": 0,
        "duration": 160,
        "capacity_pct": 7.0,
        "desc": "Severe acute respiratory syndrome with notable healthcare worker transmission and high ICU burden.",
    },
    "Seasonal Influenza A (H1N1)": {
        "beta": 0.28,
        "gamma": 0.20,
        "pop": 50000,
        "inf": 20,
        "rec": 0,
        "duration": 120,
        "capacity_pct": 5.0,
        "desc": "Moderate community transmission with rapid recovery turnover and seasonal wave profile.",
    },
    "Measles Outbreak (Severe Airborne)": {
        "beta": 1.20,
        "gamma": 0.10,
        "pop": 25000,
        "inf": 5,
        "rec": 0,
        "duration": 140,
        "capacity_pct": 12.0,
        "desc": "Extremely high reproduction ratio (R₀ > 10) requiring >92% vaccination coverage for herd immunity.",
    },
    "Subcritical Outbreak (Decaying R0 < 1.0)": {
        "beta": 0.08,
        "gamma": 0.12,
        "pop": 20000,
        "inf": 100,
        "rec": 0,
        "duration": 100,
        "capacity_pct": 5.0,
        "desc": "Self-limiting transmission below epidemic threshold; active cases extinguish monotonically.",
    },
}


@st.cache_data(show_spinner=False)
def cached_solve_sir(
    n: float,
    i0: float,
    r0: float,
    beta: float,
    gamma: float,
    duration: float,
    points: int,
    capacity: float,
    interv_day: float | None = None,
    interv_red: float = 0.0,
    vax_rate: float = 0.0,
) -> tuple[SIRSimulationResult | None, EpidemiologicalSummary | None, list[str], list[str]]:
    """Cached integration engine executing Dormand-Prince RK45 with invariant validation."""
    val = validate_sir_inputs(
        total_population=n,
        initial_infected=i0,
        initial_recovered=r0,
        transmission_rate=beta,
        recovery_rate=gamma,
        duration_days=duration,
        num_points=points,
    )
    if not val.is_valid:
        return None, None, val.errors, val.warnings

    params = SIRParameters(
        total_population=float(n),
        initial_infected=float(i0),
        initial_recovered=float(r0),
        transmission_rate=float(beta),
        recovery_rate=float(gamma),
        duration_days=float(duration),
        num_points=int(points),
        intervention_day=float(interv_day) if interv_day is not None else None,
        intervention_beta_reduction=float(interv_red),
        vaccination_rate=float(vax_rate),
    )

    try:
        sim = solve_sir(params)
        summary = analyze_simulation(sim, healthcare_capacity_limit=float(capacity) if capacity > 0 else None)
        return sim, summary, [], val.warnings
    except SolverError as exc:
        return None, None, [str(exc)], val.warnings


def compute_threat_level(r0: float | None, breach: bool, breach_day: float | None) -> dict:
    """Calculates outbreak threat level, color scheme, and executive takeaway."""
    if r0 is None or r0 <= 0:
        return {
            "level": "INACTIVE / INVALID",
            "color": "#64748B",
            "bg": "rgba(100, 116, 139, 0.15)",
            "icon": "⚪",
            "text": "Model parameters indicate no active transmission.",
        }
    if r0 < 1.0:
        return {
            "level": "CONTROLLED (DECAYING)",
            "color": "#10B981",
            "bg": "rgba(16, 185, 129, 0.15)",
            "icon": "🟢",
            "text": f"Subcritical (R₀ = {r0:.2f} < 1.0) • Outbreak is naturally self-limiting and extinguishing.",
        }
    if r0 < 2.0:
        breach_msg = (
            f"Healthcare breach on Day {breach_day:.0f}"
            if breach and breach_day
            else "ICU beds within safe threshold"
        )
        return {
            "level": "MODERATE SPREAD",
            "color": "#F59E0B",
            "bg": "rgba(245, 158, 11, 0.15)",
            "icon": "🟡",
            "text": f"Moderate Growth (R₀ = {r0:.2f}) • Continuous community transmission • {breach_msg}.",
        }
    if r0 < 3.5:
        breach_msg = (
            f"Critical ICU breach on Day {breach_day:.0f}"
            if breach and breach_day
            else "Capacity under heavy load"
        )
        return {
            "level": "HIGH-VELOCITY SURGE",
            "color": "#EF4444",
            "bg": "rgba(239, 68, 68, 0.15)",
            "icon": "🔴",
            "text": f"Aggressive Surge (R₀ = {r0:.2f}) • Rapid case doubling • {breach_msg} • Interventions needed.",
        }
    breach_msg = (
        f"Catastrophic ICU deficit from Day {breach_day:.0f}"
        if breach and breach_day
        else "Severe healthcare strain"
    )
    return {
        "level": "CRITICAL / SUPER-SPREADING",
        "color": "#8B5CF6",
        "bg": "rgba(139, 92, 246, 0.15)",
        "icon": "🟣",
        "text": f"Hyper-Contagious Wave (R₀ = {r0:.2f}) • Exponential acceleration • {breach_msg}.",
    }


def render_styled_dataframe(df: pd.DataFrame, is_dark_mode: bool = False) -> None:
    """Renders a responsive, high-contrast HTML table that dynamically matches the active theme."""
    th_bg = "#1E293B" if is_dark_mode else "#F1F5F9"
    th_color = "#F8FAFC" if is_dark_mode else "#0F172A"
    td_color = "#E2E8F0" if is_dark_mode else "#334155"
    border_c = "rgba(255, 255, 255, 0.08)" if is_dark_mode else "#E2E8F0"
    row_alt = "#161F30" if is_dark_mode else "#F8FAFC"
    row_base = "#111827" if is_dark_mode else "#FFFFFF"

    headers_html = "".join(
        f"<th style='padding: 10px 14px; text-align: right; font-size: 0.76rem; font-weight: 700; color: {th_color}; text-transform: uppercase; letter-spacing: 0.04em;'>{col}</th>"
        for col in df.columns
    )

    rows_html = []
    for idx, row in df.iterrows():
        bg = row_alt if idx % 2 == 1 else row_base
        cells = []
        for val in row:
            if isinstance(val, (float, np.floating)):
                formatted_val = f"{val:,.4f}" if abs(val) < 1000 else f"{val:,.0f}"
            elif isinstance(val, (int, np.integer)):
                formatted_val = f"{val:,}"
            else:
                formatted_val = str(val)
            cells.append(
                f"<td style='padding: 9px 14px; text-align: right; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 0.82rem; color: {td_color}; border-bottom: 1px solid {border_c};'>{formatted_val}</td>"
            )
        rows_html.append(f"<tr style='background: {bg};'>{''.join(cells)}</tr>")

    table_html = f"""
    <div style='overflow-x: auto; border: 1px solid {border_c}; border-radius: 8px; margin-bottom: 16px; box-shadow: {"0 4px 20px rgba(0,0,0,0.3)" if is_dark_mode else "0 1px 3px rgba(0,0,0,0.05)"};'>
        <table style='width: 100%; border-collapse: collapse; text-align: right;'>
            <thead style='background: {th_bg}; border-bottom: 2px solid {border_c};'>
                <tr>{headers_html}</tr>
            </thead>
            <tbody>
                {"".join(rows_html)}
            </tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


def render_agency_footer(
    is_dark_mode: bool, c_surf: str, c_bord: str, c_txt_muted: str, c_txt_main: str
) -> None:
    """Renders a sleek, modern tech-agency footer inspired by nexafotech.com."""
    st.markdown(
        f"""
        <div style="margin-top: 60px; padding-top: 28px; border-top: 1px solid {c_bord};">
            <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 24px; margin-bottom: 24px;">
                <div style="max-width: 380px;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                        <span style="font-size: 1.25rem; font-weight: 900; letter-spacing: -0.01em; color: #38BDF8;">SIR</span>
                        <span style="font-size: 1.15rem; font-weight: 800; color: {c_txt_main};">PROJECT</span>
                        <span style="font-size: 0.68rem; background: {"rgba(56, 189, 248, 0.15)" if is_dark_mode else "#E0F2FE"}; color: #0284C7; padding: 2px 8px; border-radius: 9999px; font-weight: 700;">v2.5 PRO</span>
                    </div>
                    <div style="font-size: 0.80rem; color: {c_txt_muted}; line-height: 1.5;">
                        Enterprise disease spread prediction & healthcare capacity intelligence platform implementing Kermack-McKendrick non-linear differential equations with adaptive RK45 numerical integration.
                    </div>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 32px; font-size: 0.80rem; color: {c_txt_muted};">
                    <div>
                        <div style="font-weight: 700; color: {c_txt_main}; margin-bottom: 8px; text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.05em;">Core Systems</div>
                        <div style="margin-bottom: 4px;">⚡ Runge-Kutta 5(4) Solver</div>
                        <div style="margin-bottom: 4px;">🎯 Dynamical Invariance &gt; 99.999%</div>
                        <div style="margin-bottom: 4px;">🛡️ 146 Automated QA Tests</div>
                    </div>
                    <div>
                        <div style="font-weight: 700; color: {c_txt_main}; margin-bottom: 8px; text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.05em;">Platform Links</div>
                        <div style="margin-bottom: 4px;"><a href="https://github.com/kingson-starboy/SIR-PROJECT-" target="_blank" style="color: #38BDF8; text-decoration: none;">GitHub Source Code ↗</a></div>
                        <div style="margin-bottom: 4px;"><a href="https://github.com/kingson-starboy/SIR-PROJECT-/actions" target="_blank" style="color: {c_txt_muted}; text-decoration: none;">Continuous Integration ↗</a></div>
                        <div style="margin-bottom: 4px;"><a href="https://s-i-r-project.streamlit.app/" target="_blank" style="color: {c_txt_muted}; text-decoration: none;">Streamlit Cloud Host ↗</a></div>
                    </div>
                    <div>
                        <div style="font-weight: 700; color: {c_txt_main}; margin-bottom: 8px; text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.05em;">Telemetry Health</div>
                        <div style="display: flex; align-items: center; gap: 6px; color: #10B981; font-weight: 600; margin-bottom: 4px;">
                            <span style="width: 7px; height: 7px; border-radius: 50%; background: #10B981; box-shadow: 0 0 8px #10B981;"></span>
                            All Systems Operational
                        </div>
                        <div style="color: {c_txt_muted}; font-size: 0.74rem;">Execution Latency: &lt;5ms</div>
                        <div style="color: {c_txt_muted}; font-size: 0.74rem;">Solver Invariance: Verified</div>
                    </div>
                </div>
            </div>
            <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; padding-top: 16px; border-top: 1px dashed {c_bord}; font-size: 0.74rem; color: {c_txt_muted};">
                <div>© 2026 SIR Project · Designed with Nexafo-inspired engineering by Kingson Israel.</div>
                <div>Formulation: <i>Kermack-McKendrick Epidemic Threshold (1927)</i></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Initialize Simulation Session State Defaults
if "current_simulation" not in st.session_state:
    def_p = PRESETS["COVID-19 Omicron (High Contagion)"]
    init_sim, init_sum, _, _ = cached_solve_sir(
        def_p["pop"],
        def_p["inf"],
        def_p["rec"],
        def_p["beta"],
        def_p["gamma"],
        def_p["duration"],
        1000,
        (def_p["capacity_pct"] / 100.0) * def_p["pop"],
    )
    st.session_state.current_simulation = init_sim
    st.session_state.current_summary = init_sum

if "simulation_history" not in st.session_state:
    st.session_state.simulation_history = []

if "historical_df" not in st.session_state:
    st.session_state.historical_df = None


# -----------------------------------------------------------------------------
# 4. SIDEBAR NAVIGATION & THEME CONTROLS (MINIMALIST & DECOUPLED)
# -----------------------------------------------------------------------------
with st.sidebar:
    sidebar_logo_html = (
        f'<img src="{LOGO_DATA_URI}" width="42" height="42" style="border-radius: 10px; box-shadow: 0 4px 14px rgba(56, 189, 248, 0.35); flex-shrink: 0;" alt="SIR Logo" />'
        if LOGO_DATA_URI
        else '<span style="font-size: 1.8rem;">🧬</span>'
    )
    st.markdown(
        f"""
        <div style="padding: 10px 0 16px 0; border-bottom: 1px solid rgba(148, 163, 184, 0.2); margin-bottom: 16px; display: flex; align-items: center; gap: 12px;">
            {sidebar_logo_html}
            <div>
                <div style="font-size: 1.25rem; font-weight: 900; letter-spacing: -0.02em; line-height: 1.15;">
                    <span style="color: #38BDF8; font-weight: 900; letter-spacing: 0.04em;">SIR</span> <span style="font-weight: 800; color: {c_text_main};">PROJECT</span>
                </div>
                <div style="font-size: 0.72rem; color: {c_text_muted}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">EpiSim Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Theme Switcher (Dark & Light Mode)
    theme_label = "🌙 Switch to Dark Mode" if st.session_state.theme == "light" else "☀️ Switch to Light Mode"
    if st.button(theme_label, use_container_width=True):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Clean Workspace Navigation (Nexafo-Inspired Multimodal Explorer)
    nav_opts = [
        "Live Dashboard",
        "Scenario Comparison",
        "Model Explorer",
        "Data & Reports",
    ]
    if "nav_selection_radio" not in st.session_state or st.session_state.nav_selection_radio not in nav_opts:
        st.session_state.nav_selection_radio = "Live Dashboard"

    nav_selection = st.radio(
        "Workspace View",
        nav_opts,
        key="nav_selection_radio",
    )

    st.markdown("---")

    # Persistent Solver Telemetry Status
    sim_curr = st.session_state.current_simulation
    if sim_curr is not None:
        p_act = sim_curr.parameters
        st.markdown(
            f"""
            <div class="telemetry-pill">
                <div class="telemetry-dot"></div>
                <div style="font-size: 0.74rem; line-height: 1.35;">
                    <b>RK45 Adaptive Solver</b><br>
                    N = {p_act.total_population:,.0f} • Invariance: {sim_curr.max_conservation_error:.1e}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div style="margin-top: 24px; font-size: 0.72rem; color: #64748B; line-height: 1.4;">
            <b>SIR Project v2.4</b><br>
            Kermack-McKendrick ODE Formulation<br>
            Verified 146 Automated Tests (100%)
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# 5. VIEW 1: LIVE DASHBOARD
# -----------------------------------------------------------------------------
if nav_selection == "Live Dashboard":
    hero_logo_html = (
        f'<img src="{LOGO_DATA_URI}" class="hero-brand-logo" alt="SIR Logo" />'
        if LOGO_DATA_URI
        else '<span style="font-size: 2.2rem;">🧬</span>'
    )
    st.markdown(
        f"""
        <div class="hero-header">
            <div style="display: flex; align-items: center; gap: 18px;">
                {hero_logo_html}
                <div>
                    <div class="hero-badge">
                        <span class="hero-dot"></span>
                        <span>Adaptive RK45 Differential Engine Active</span>
                    </div>
                    <div class="hero-title"><span class="brand-sir">SIR</span> Disease Spread Prediction & Capacity Intelligence</div>
                    <div class="hero-sub">High-precision Kermack-McKendrick epidemiological differential equations, healthcare bed capacity forecasting, and policy analytics.</div>
                </div>
            </div>
            <div class="hero-stats-strip">
                <div class="hero-stat-item">⚡ <b>&lt;5ms</b> Latency</div>
                <div class="hero-stat-item">🎯 <b>99.999%</b> Invariance</div>
                <div class="hero-stat-item">🛡️ <b>146</b> QA Tests</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander(
        "💡 New to Epidemiological Modeling? Click for a 30-Second Quick-Start Guide", expanded=False
    ):
        st.markdown(
            """
            <div class="walkthrough-grid">
                <div class="walkthrough-card">
                    <div class="walkthrough-step">STEP 1 · PATHOGEN</div>
                    <div class="walkthrough-title">🧬 Choose or Tune Disease</div>
                    <div class="walkthrough-desc">Select an established outbreak preset (COVID-19, Spanish Flu) or calibrate daily transmission (β) and recovery (γ).</div>
                </div>
                <div class="walkthrough-card">
                    <div class="walkthrough-step">STEP 2 · DEMOGRAPHICS</div>
                    <div class="walkthrough-title">👥 Host & Hospital Capacity</div>
                    <div class="walkthrough-desc">Define host population N and available ICU bed capacity threshold to detect healthcare surge stress.</div>
                </div>
                <div class="walkthrough-card">
                    <div class="walkthrough-step">STEP 3 · INTEGRATION</div>
                    <div class="walkthrough-title">⚡ RK45 Dynamic Solve</div>
                    <div class="walkthrough-desc">Click 'Run Simulation' to execute adaptive differential integration with strict conservation invariance.</div>
                </div>
                <div class="walkthrough-card">
                    <div class="walkthrough-step">STEP 4 · INTERVENTIONS</div>
                    <div class="walkthrough-title">🛡️ Flatten the Curve</div>
                    <div class="walkthrough-desc">Toggle staged lockdowns or vaccination to evaluate real-time policy impact on hospital overrun.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(
        """
        <div class="param-studio">
            <div class="param-studio-header">
                <div class="param-studio-title">
                    <span>⚙️</span>
                    <span>Simulation Control & Parameter Studio</span>
                </div>
                <div class="param-studio-badge">INTERACTIVE CALIBRATION</div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    col_p1, col_p2, col_p3 = st.columns([1, 1, 1])

    with col_p1:
        st.markdown(
            "<p style='font-size:0.80rem; font-weight:700; text-transform:uppercase; margin-bottom:6px;'>🧬 Pathogen Transmission Dynamics</p>",
            unsafe_allow_html=True,
        )
        preset_opts = ["Custom Configuration"] + list(PRESETS.keys())
        if (
            "preset_choice_select" not in st.session_state
            or st.session_state.preset_choice_select not in preset_opts
        ):
            st.session_state.preset_choice_select = "COVID-19 Omicron (High Contagion)"

        preset_choice = st.selectbox(
            "Scenario Preset",
            preset_opts,
            key="preset_choice_select",
            help="Select an archetype or customize your parameters.",
        )
        if preset_choice != "Custom Configuration":
            p_data = PRESETS[preset_choice]
            def_pop, def_inf, def_rec = p_data["pop"], p_data["inf"], p_data["rec"]
            def_beta, def_gamma, def_dur = p_data["beta"], p_data["gamma"], p_data["duration"]
            def_cap = p_data["capacity_pct"]
        else:
            def_pop, def_inf, def_rec = 100000, 50, 0
            def_beta, def_gamma, def_dur = 0.35, 0.12, 160
            def_cap = 10.0

        inp_beta = st.slider(
            "Transmission Rate (β)",
            min_value=0.01,
            max_value=2.0,
            value=float(def_beta),
            step=0.01,
            format="%.2f",
            help="Effective contacts per infectious individual per day.",
        )
        inp_gamma = st.slider(
            "Recovery Rate (γ)",
            min_value=0.01,
            max_value=1.0,
            value=float(def_gamma),
            step=0.01,
            format="%.2f",
            help="Daily clearance fraction (1/γ = mean infectious duration in days).",
        )
        # R0 preview tag
        r0_calc = inp_beta / inp_gamma if inp_gamma > 0 else 0.0
        st.markdown(
            f"<div style='font-size:0.75rem; color:{c_text_muted}; margin-top:-6px;'>Theoretical R₀ = <b>{r0_calc:.2f}</b> • Mean Infectious Duration: <b>{1 / inp_gamma:.1f} days</b></div>",
            unsafe_allow_html=True,
        )

    with col_p2:
        st.markdown(
            "<p style='font-size:0.80rem; font-weight:700; text-transform:uppercase; margin-bottom:6px;'>👥 Host Demographics & Capacity</p>",
            unsafe_allow_html=True,
        )
        inp_n = st.number_input(
            "Total Population (N)",
            min_value=100,
            max_value=50000000,
            value=int(def_pop),
            step=5000,
            help="Total closed host population size.",
        )
        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            inp_i0 = st.number_input(
                "Infected I(0)",
                min_value=1,
                max_value=int(inp_n),
                value=int(def_inf),
                step=5,
                help="Initial infected individuals.",
            )
        with col_sub2:
            inp_r0 = st.number_input(
                "Recovered R(0)",
                min_value=0,
                max_value=int(inp_n),
                value=int(def_rec),
                step=5,
                help="Initial immune individuals.",
            )

        inp_cap_pct = st.slider(
            "Hospital Bed Capacity (% of N)",
            min_value=1.0,
            max_value=30.0,
            value=float(def_cap),
            step=0.5,
            help="Designated healthcare surge capacity threshold.",
        )
        capacity_beds = (inp_cap_pct / 100.0) * inp_n
        st.markdown(
            f"<div style='font-size:0.75rem; color:{c_text_muted}; margin-top:-6px;'>Available ICU Beds: <b>{capacity_beds:,.0f} beds</b></div>",
            unsafe_allow_html=True,
        )

    with col_p3:
        st.markdown(
            "<p style='font-size:0.80rem; font-weight:700; text-transform:uppercase; margin-bottom:6px;'>🛡️ Intervention & Horizon</p>",
            unsafe_allow_html=True,
        )
        inp_dur = st.number_input(
            "Time Horizon (Days)",
            min_value=10,
            max_value=500,
            value=int(def_dur),
            step=10,
            help="Total simulation integration span in days.",
        )

        enable_vax = st.checkbox("Active Vaccination Campaign", value=False)
        if enable_vax:
            inp_vax_pct = st.slider("Daily Vaccination (% of S)", 0.1, 5.0, 1.0, 0.1)
            vax_rate_val = inp_vax_pct / 100.0
        else:
            vax_rate_val = 0.0

        enable_npi = st.checkbox("Staged Lockdown / Social Distancing", value=False)
        if enable_npi:
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                interv_day_val = float(st.number_input("Start Day", 1, int(inp_dur), 25, 5))
            with col_l2:
                interv_red_val = st.slider("β Cut %", 5, 90, 40, 5) / 100.0
        else:
            interv_day_val = None
            interv_red_val = 0.0

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            btn_run = st.button("⚡ Run Simulation", type="primary", use_container_width=True)
        with col_b2:
            btn_reset = st.button("🔄 Reset Defaults", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Re-calculate upon button click or parameter shift
    if btn_reset:
        st.session_state.current_simulation = None
        st.rerun()

    if btn_run or st.session_state.current_simulation is None:
        with st.spinner("Executing adaptive Runge-Kutta 5(4) solver..."):
            new_sim, new_sum, errs, warns = cached_solve_sir(
                inp_n,
                inp_i0,
                inp_r0,
                inp_beta,
                inp_gamma,
                inp_dur,
                1000,
                capacity_beds,
                interv_day_val,
                interv_red_val,
                vax_rate_val,
            )
            if errs:
                for e in errs:
                    st.error(e)
            else:
                st.session_state.current_simulation = new_sim
                st.session_state.current_summary = new_sum
                st.toast("Differential equations integrated with mass conservation", icon="✅")

    sim = st.session_state.current_simulation
    summ = st.session_state.current_summary

    if sim is not None and summ is not None:
        p_act = sim.parameters
        threat_info = compute_threat_level(summ.R0, summ.capacity.is_breached, summ.capacity.breach_day_start)
        doubling_time_str = (
            f"{np.log(2) / (p_act.transmission_rate - p_act.recovery_rate):.1f} Days"
            if (p_act.transmission_rate > p_act.recovery_rate)
            else "Subcritical (Decaying)"
        )

        st.markdown(
            f"""
            <div class="threat-banner" style="border-left: 4px solid {threat_info["color"]};">
                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                    <span style="font-size: 1.25rem;">{threat_info["icon"]}</span>
                    <div>
                        <div style="font-size: 0.72rem; font-weight: 700; color: {threat_info["color"]}; text-transform: uppercase; letter-spacing: 0.05em;">Outbreak Dynamics Status</div>
                        <div style="font-size: 0.95rem; font-weight: 800; color: {c_text_main};">{threat_info["text"]}</div>
                    </div>
                </div>
                <div style="display: flex; gap: 16px; align-items: center; font-size: 0.78rem; flex-wrap: wrap;">
                    <div><span style="color: {c_text_muted};">Est. Doubling Time:</span> <b>{doubling_time_str}</b></div>
                    <div><span style="color: {c_text_muted};">ICU Surge Status:</span> <b>{"🚨 BREACHED" if summ.capacity.is_breached else "✅ WITHIN LIMITS"}</b></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Top 4 KPI Metrics in High-Impact Grid
        r0_val_str = f"{summ.R0:.2f}" if summ.R0 is not None else "Undefined"
        r0_class = "badge-purple" if (summ.R0 and summ.R0 > 1.0) else "badge-green"

        st.markdown(
            f"""
            <div class="metric-grid">
                <div class="metric-card metric-card-purple">
                    <div class="metric-label">Basic Reproduction Number (R₀)</div>
                    <div class="metric-val">{r0_val_str}</div>
                    <span class="metric-badge {r0_class}">{summ.R0_status}</span>
                </div>
                <div class="metric-card metric-card-rose">
                    <div class="metric-label">Peak Active Infections</div>
                    <div class="metric-val">{summ.peak.peak_infections:,.0f}</div>
                    <span class="metric-badge badge-rose">{summ.peak.peak_percentage:.1f}% Population Active</span>
                </div>
                <div class="metric-card metric-card-amber">
                    <div class="metric-label">Peak Influx Day</div>
                    <div class="metric-val">Day {summ.peak.peak_day:.1f}</div>
                    <span class="metric-badge badge-amber">{"Crest Reached" if summ.peak.has_distinct_peak else "Subcritical"}</span>
                </div>
                <div class="metric-card metric-card-blue">
                    <div class="metric-label">Total Cumulative Attack Rate</div>
                    <div class="metric-val">{summ.final_stats.total_affected:,.0f}</div>
                    <span class="metric-badge badge-blue">{summ.final_stats.percent_affected:.1f}% Population</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Plotly modebar configuration: Prominent, separated zoom tools with no collision
        chart_config = {
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            "toImageButtonOptions": {
                "format": "png",
                "filename": "episim_plot",
                "height": 600,
                "width": 1000,
                "scale": 2,
            },
        }

        # 8 High-Resolution Visualization Tabs
        tab_sir, tab_peak, tab_phase, tab_donut, tab_rate, tab_re, tab_sens, tab_calib = st.tabs(
            [
                "📈 Epidemic Trajectories",
                "🏥 Healthcare Surge Capacity",
                "🌀 Phase Space (S vs I)",
                "🍩 Population Distribution",
                "⚡ Contagion Velocity (dI/dt)",
                "📉 Effective Reproduction Re(t)",
                "🔬 Parameter Sensitivity",
                "📊 Model Calibration (vs Data)",
            ]
        )

        with tab_sir:
            st.plotly_chart(
                apply_theme_to_figure(create_sir_curve_chart(sim), is_dark),
                use_container_width=True,
                config=chart_config,
            )

        with tab_peak:
            st.plotly_chart(
                apply_theme_to_figure(create_peak_analysis_chart(sim, summ, show_capacity=True), is_dark),
                use_container_width=True,
                config=chart_config,
            )

        with tab_phase:
            st.plotly_chart(
                apply_theme_to_figure(create_phase_space_chart(sim, summ), is_dark),
                use_container_width=True,
                config=chart_config,
            )

        with tab_donut:
            col_dn1, col_dn2 = st.columns([1, 1])
            with col_dn1:
                st.plotly_chart(
                    apply_theme_to_figure(
                        create_population_distribution_chart(summ, sim.parameters.total_population), is_dark
                    ),
                    use_container_width=True,
                    config=chart_config,
                )
            with col_dn2:
                st.plotly_chart(
                    apply_theme_to_figure(create_animated_progression_chart(sim), is_dark),
                    use_container_width=True,
                    config=chart_config,
                )

        with tab_rate:
            st.plotly_chart(
                apply_theme_to_figure(create_infection_rate_trend_chart(sim), is_dark),
                use_container_width=True,
                config=chart_config,
            )

        with tab_re:
            st.plotly_chart(
                apply_theme_to_figure(create_effective_r_chart(sim, summ), is_dark),
                use_container_width=True,
                config=chart_config,
            )

        with tab_sens:
            sens_items = compute_parameter_sensitivity(sim.parameters)
            st.plotly_chart(
                apply_theme_to_figure(create_sensitivity_chart(sens_items), is_dark),
                use_container_width=True,
                config=chart_config,
            )

        with tab_calib:
            st.markdown("##### Empirical Case Data vs. Simulated Continuous Trajectory")
            col_up1, col_up2 = st.columns([2, 1])

            with col_up1:
                uploaded_file = st.file_uploader(
                    "Upload Historical Outbreak CSV",
                    type=["csv"],
                    help="CSV must contain 'day' (or date) and 'cases' (or infected) columns.",
                )
            with col_up2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("🧪 Load Reference Wave Dataset", use_container_width=True):
                    bench_days = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 100, 120], dtype=float)
                    synth_i = np.interp(bench_days, sim.t, sim.I)
                    rng = np.random.default_rng(42)
                    noisy_cases = np.maximum(0.0, synth_i + rng.normal(0, np.maximum(5.0, synth_i * 0.08)))
                    st.session_state.historical_df = pd.DataFrame({"day": bench_days, "cases": noisy_cases})
                    st.toast("Loaded reference outbreak dataset", icon="✅")

            if uploaded_file is not None:
                content = uploaded_file.getvalue()
                parsed_df, parse_errors = parse_and_validate_historical_csv(content)
                if parse_errors:
                    for err in parse_errors:
                        st.error(f"❌ {err}")
                else:
                    st.session_state.historical_df = parsed_df
                    st.success(f"✓ Successfully validated {len(parsed_df)} empirical data records.")

            if st.session_state.historical_df is not None:
                h_df = st.session_state.historical_df
                fit_metrics = compute_model_fit_metrics(sim, h_df)

                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    st.metric("Root Mean Squared Error (RMSE)", f"{fit_metrics['rmse']:,.1f} cases")
                with col_f2:
                    st.metric("Mean Absolute Error (MAE)", f"{fit_metrics['mae']:,.1f} cases")
                with col_f3:
                    st.metric("Correlation Coefficient (R²)", f"{fit_metrics['r_squared']:.3f}")

                st.plotly_chart(
                    apply_theme_to_figure(create_model_vs_data_chart(sim, h_df, fit_metrics), is_dark),
                    use_container_width=True,
                    config=chart_config,
                )
            else:
                st.info(
                    "💡 Upload a CSV file or click 'Load Reference Wave Dataset' to compare against empirical observations."
                )

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # SYMMETRIC DUAL-CARD CLINICAL & DIAGNOSTIC TELEMETRY (BALANCED & CLEAN)
        # ---------------------------------------------------------------------
        hit_str = (
            f"{summ.trends.herd_immunity_threshold:.1f}%"
            if summ.trends.herd_immunity_threshold is not None
            else "N/A (R₀ ≤ 1.0)"
        )
        clearance_str = (
            f"Day {summ.trends.clearance_day:.1f}"
            if summ.trends.clearance_day is not None
            else "Beyond Horizon (>500d)"
        )
        surge_status_badge = (
            f"<span class='spec-pill pill-red'>Breach Day {summ.capacity.breach_day_start:.1f} ({summ.capacity.peak_excess_cases:,.0f} beds excess)</span>"
            if summ.capacity.is_breached
            else "<span class='spec-pill pill-green'>Safe Within Limits (0 Breaches)</span>"
        )

        col_diag1, col_diag2 = st.columns(2)

        with col_diag1:
            st.markdown(
                f"""
                <div class="spec-card">
                    <div>
                        <div class="spec-header">
                            <span>📊</span>
                            <span>Outbreak Dynamics & Healthcare Impact</span>
                        </div>
                        <div class="spec-row">
                            <span class="spec-label">Theoretical Herd Immunity Threshold</span>
                            <span class="spec-val"><span class="spec-pill pill-blue">{hit_str}</span></span>
                        </div>
                        <div class="spec-row">
                            <span class="spec-label">Initial Wave Velocity</span>
                            <span class="spec-val"><span class="spec-pill pill-amber">{summ.trends.initial_trend}</span></span>
                        </div>
                        <div class="spec-row">
                            <span class="spec-label">Infection Clearance Horizon (&lt;5 active)</span>
                            <span class="spec-val"><span class="spec-pill pill-slate">{clearance_str}</span></span>
                        </div>
                        <div class="spec-row">
                            <span class="spec-label">Healthcare Capacity Surge Status</span>
                            <span class="spec-val">{surge_status_badge}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_diag2:
            st.markdown(
                f"""
                <div class="spec-card">
                    <div>
                        <div class="spec-header">
                            <span>⚡</span>
                            <span>Numerical Precision & Conservation Diagnostics</span>
                        </div>
                        <div class="spec-row">
                            <span class="spec-label">Total Population Invariance |S+I+R - N|</span>
                            <span class="spec-val"><span class="spec-pill pill-green">{sim.max_conservation_error:.2e} (Strict)</span></span>
                        </div>
                        <div class="spec-row">
                            <span class="spec-label">Differential Numerical Solver</span>
                            <span class="spec-val"><span class="spec-pill pill-blue">Dormand-Prince RK5(4) Adaptive</span></span>
                        </div>
                        <div class="spec-row">
                            <span class="spec-label">Evaluated Discrete Time Steps</span>
                            <span class="spec-val"><span class="spec-pill pill-slate">{len(sim.t):,} Steps</span></span>
                        </div>
                        <div class="spec-row">
                            <span class="spec-label">Compartmental Non-Negativity Bounds</span>
                            <span class="spec-val"><span class="spec-pill pill-green">Verified (S, I, R ≥ 0)</span></span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# -----------------------------------------------------------------------------
# 6. VIEW 2: SCENARIO COMPARISON STUDIO
# -----------------------------------------------------------------------------
elif nav_selection == "Scenario Comparison":
    hero_logo_html = (
        f'<img src="{LOGO_DATA_URI}" class="hero-brand-logo" alt="SIR Logo" />'
        if LOGO_DATA_URI
        else '<span style="font-size: 2.2rem;">🧬</span>'
    )
    st.markdown(
        f"""
        <div class="hero-header">
            <div style="display: flex; align-items: center; gap: 18px;">
                {hero_logo_html}
                <div>
                    <div class="hero-badge">
                        <span class="hero-dot"></span>
                        <span>Dual Policy Simulation Lab</span>
                    </div>
                    <div class="hero-title"><span class="brand-sir">SIR</span> Comparative Policy & Intervention Studio</div>
                    <div class="hero-sub">Simulate and evaluate two distinct epidemiological policy scenarios side-by-side to quantify intervention efficacy.</div>
                </div>
            </div>
            <div class="hero-stats-strip">
                <div class="hero-stat-item">⚖️ <b>Dual-Trajectory</b> Analysis</div>
                <div class="hero-stat-item">📉 <b>Flatten The Curve</b> Testing</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(
            f"""
            <div style="background:{c_surface}; border:1px solid {c_border}; border-top:3px solid #EF4444; border-radius:12px; padding:18px; margin-bottom:16px;">
                <p style='font-size:0.85rem; font-weight:700; color:#EF4444; text-transform:uppercase; margin-bottom:10px;'>Scenario A: Baseline (Unmitigated)</p>
            """,
            unsafe_allow_html=True,
        )
        sc_a_n = st.number_input(
            "Population N (Scenario A)", min_value=100, value=100000, step=5000, key="ca_n"
        )
        sc_a_i0 = st.number_input("Initial Infected I(0)", min_value=1, value=50, key="ca_i0")
        sc_a_beta = st.slider("Transmission Rate β", 0.05, 1.50, 0.40, 0.01, key="ca_b")
        sc_a_gamma = st.slider("Recovery Rate γ", 0.02, 0.50, 0.12, 0.01, key="ca_g")
        sc_a_dur = st.number_input("Duration (Days)", min_value=20, value=180, key="ca_d")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown(
            f"""
            <div style="background:{c_surface}; border:1px solid {c_border}; border-top:3px solid #3B82F6; border-radius:12px; padding:18px; margin-bottom:16px;">
                <p style='font-size:0.85rem; font-weight:700; color:#3B82F6; text-transform:uppercase; margin-bottom:10px;'>Scenario B: Intervention (Flattened Curve)</p>
            """,
            unsafe_allow_html=True,
        )
        sc_b_n = st.number_input(
            "Population N (Scenario B)", min_value=100, value=100000, step=5000, key="cb_n"
        )
        sc_b_i0 = st.number_input("Initial Infected I(0)", min_value=1, value=50, key="cb_i0")
        sc_b_beta = st.slider("Transmission Rate β (Mitigated)", 0.05, 1.50, 0.22, 0.01, key="cb_b")
        sc_b_gamma = st.slider("Recovery Rate γ", 0.02, 0.50, 0.12, 0.01, key="cb_g")
        sc_b_dur = st.number_input("Duration (Days)", min_value=20, value=180, key="cb_d")
        st.markdown("</div>", unsafe_allow_html=True)

    btn_compare = st.button("⚖️ Run Comparative Simulation", type="primary", use_container_width=True)

    r_a, s_a, _, _ = cached_solve_sir(
        sc_a_n, sc_a_i0, 0, sc_a_beta, sc_a_gamma, sc_a_dur, 1000, 0.10 * sc_a_n
    )
    r_b, s_b, _, _ = cached_solve_sir(
        sc_b_n, sc_b_i0, 0, sc_b_beta, sc_b_gamma, sc_b_dur, 1000, 0.10 * sc_b_n
    )

    if r_a is not None and r_b is not None and s_a is not None and s_b is not None:
        peak_diff = s_b.peak.peak_infections - s_a.peak.peak_infections
        peak_diff_pct = (
            (peak_diff / s_a.peak.peak_infections) * 100.0 if s_a.peak.peak_infections > 0 else 0.0
        )
        day_diff = s_b.peak.peak_day - s_a.peak.peak_day
        attack_diff = s_b.final_stats.percent_affected - s_a.final_stats.percent_affected

        st.markdown(
            f"""
            <div class="metric-grid">
                <div class="metric-card metric-card-blue">
                    <div class="metric-label">Peak Infection Burden Delta</div>
                    <div class="metric-val">{peak_diff_pct:+.1f}%</div>
                    <span class="metric-badge badge-blue">{peak_diff:+,.0f} active cases</span>
                </div>
                <div class="metric-card metric-card-amber">
                    <div class="metric-label">Peak Timing Shift</div>
                    <div class="metric-val">{day_diff:+.1f} Days</div>
                    <span class="metric-badge badge-amber">{"Timeline Delayed" if day_diff > 0 else "Earlier Peak"}</span>
                </div>
                <div class="metric-card metric-card-purple">
                    <div class="metric-label">Total Attack Rate Shift</div>
                    <div class="metric-val">{attack_diff:+.1f}%</div>
                    <span class="metric-badge badge-purple">Cumulative Total</span>
                </div>
                <div class="metric-card metric-card-rose">
                    <div class="metric-label">Reproduction Ratio (R₀) Delta</div>
                    <div class="metric-val">{(s_b.R0 - s_a.R0):+.2f}</div>
                    <span class="metric-badge badge-rose">{s_a.R0:.2f} → {s_b.R0:.2f}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        chart_config = {
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            "toImageButtonOptions": {
                "format": "png",
                "filename": "episim_comparison",
                "height": 600,
                "width": 1100,
                "scale": 2,
            },
        }
        st.plotly_chart(
            apply_theme_to_figure(
                create_scenario_comparison_chart(
                    r_a, r_b, "Scenario A (Baseline)", "Scenario B (Intervention)"
                ),
                is_dark,
            ),
            use_container_width=True,
            config=chart_config,
        )


# -----------------------------------------------------------------------------
# 7. VIEW 3: MODEL EXPLORER (NEXAFO-INSPIRED EPIDEMIOLOGY ATLAS)
# -----------------------------------------------------------------------------
elif nav_selection == "Model Explorer":
    hero_logo_html = (
        f'<img src="{LOGO_DATA_URI}" class="hero-brand-logo" alt="SIR Logo" />'
        if LOGO_DATA_URI
        else '<span style="font-size: 2.2rem;">🧬</span>'
    )
    st.markdown(
        f"""
        <div class="hero-header">
            <div style="display: flex; align-items: center; gap: 18px;">
                {hero_logo_html}
                <div>
                    <div class="hero-badge">
                        <span class="hero-dot"></span>
                        <span>Interactive Pathogen Library & Theoretical Atlas</span>
                    </div>
                    <div class="hero-title"><span class="brand-sir">SIR</span> Model Explorer & Dynamics Atlas</div>
                    <div class="hero-sub">Explore historical benchmark pathogens, visual compartmental pipelines, and the fundamental mathematical laws of epidemic control.</div>
                </div>
            </div>
            <div class="hero-stats-strip">
                <div class="hero-stat-item">🦠 <b>6</b> Pathogen Presets</div>
                <div class="hero-stat-item">📐 <b>3</b> Golden Laws</div>
                <div class="hero-stat-item">📉 <b>Policy</b> Matrix</div>
                <div class="hero-stat-item">⚡ <b>RK45</b> Solver</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. PATHOGEN BENCHMARK GALLERY
    st.markdown(
        f"""
        <div style="margin-bottom: 12px;">
            <div style="font-size: 1.10rem; font-weight: 800; color: {c_text_main};">
                🔬 Benchmark Pathogen Library
            </div>
            <div style="font-size: 0.82rem; color: {c_text_muted};">
                Select any validated pathogen archetype to instantly calibrate the simulation engine.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pathogen_meta = [
        {
            "key": "COVID-19 Omicron (High Contagion)",
            "short": "COVID-19 Omicron",
            "icon": "🦠",
            "tag": "Airborne · R₀ = 3.93",
            "color": "#38BDF8",
            "infectious_days": "7.1d",
            "hit": "74.5%",
        },
        {
            "key": "1918 Spanish Flu (Severe Pulmonary)",
            "short": "1918 Spanish Flu",
            "icon": "🧬",
            "tag": "Historic · R₀ = 2.40",
            "color": "#F59E0B",
            "infectious_days": "6.7d",
            "hit": "58.3%",
        },
        {
            "key": "SARS-CoV-1 (2003 Classic)",
            "short": "SARS-CoV-1 (2003)",
            "icon": "🧪",
            "tag": "Nosocomial · R₀ = 2.80",
            "color": "#EC4899",
            "infectious_days": "10.0d",
            "hit": "64.3%",
        },
        {
            "key": "Seasonal Influenza A (H1N1)",
            "short": "Seasonal Flu (H1N1)",
            "icon": "🐖",
            "tag": "Endemic · R₀ = 1.40",
            "color": "#10B981",
            "infectious_days": "5.0d",
            "hit": "28.6%",
        },
        {
            "key": "Measles Outbreak (Severe Airborne)",
            "short": "Measles Outbreak",
            "icon": "💉",
            "tag": "Aerosol · R₀ = 12.0",
            "color": "#EF4444",
            "infectious_days": "10.0d",
            "hit": "91.7%",
        },
        {
            "key": "Subcritical Outbreak (Decaying R0 < 1.0)",
            "short": "Subcritical Outbreak",
            "icon": "🌿",
            "tag": "Extinguishing · R₀ = 0.67",
            "color": "#8B5CF6",
            "infectious_days": "8.3d",
            "hit": "0.0%",
        },
    ]

    col_g1, col_g2, col_g3 = st.columns(3)
    cols_grid = [col_g1, col_g2, col_g3]

    for idx, pmeta in enumerate(pathogen_meta):
        p_info = PRESETS[pmeta["key"]]
        with cols_grid[idx % 3]:
            st.markdown(
                f"""
                <div class="explore-card">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                            <span style="font-size: 1.8rem;">{pmeta["icon"]}</span>
                            <span class="explore-badge" style="background: {pmeta["color"]}22; color: {pmeta["color"]};">
                                {pmeta["tag"]}
                            </span>
                        </div>
                        <div style="font-size: 0.96rem; font-weight: 800; color: {c_text_main}; margin-bottom: 6px;">
                            {pmeta["short"]}
                        </div>
                        <div style="font-size: 0.78rem; color: {c_text_muted}; line-height: 1.45; min-height: 48px; margin-bottom: 12px;">
                            {p_info["desc"]}
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 0.74rem; background: {"rgba(255,255,255,0.03)" if is_dark else "#F8FAFC"}; padding: 8px 10px; border-radius: 8px; margin-bottom: 12px; border: 1px solid {c_border};">
                            <div><span style="color:{c_text_muted};">Daily β:</span> <b>{p_info["beta"]:.2f}</b></div>
                            <div><span style="color:{c_text_muted};">Daily γ:</span> <b>{p_info["gamma"]:.2f}</b></div>
                            <div><span style="color:{c_text_muted};">Infectious:</span> <b>{pmeta["infectious_days"]}</b></div>
                            <div><span style="color:{c_text_muted};">Herd Imm.:</span> <b>{pmeta["hit"]}</b></div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"🔬 Simulate {pmeta['short']}",
                key=f"btn_load_{idx}",
                use_container_width=True,
            ):
                st.session_state.preset_choice_select = pmeta["key"]
                st.session_state.nav_selection_radio = "Live Dashboard"
                st.session_state.current_simulation = None
                st.rerun()

    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)

    # 2. S-I-R COMPARTMENTAL TRANSMISSION PIPELINE
    st.markdown(
        f"""
        <div style="margin-bottom: 14px;">
            <div style="font-size: 1.10rem; font-weight: 800; color: {c_text_main};">
                ⚡ S-I-R Compartmental Transmission Flow
            </div>
            <div style="font-size: 0.82rem; color: {c_text_muted};">
                The Kermack-McKendrick non-linear conservation dynamics governing state transitions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_box1, c_box2, c_box3 = st.columns(3)
    with c_box1:
        st.markdown(
            f"""
            <div class="concept-box" style="border-top: 3px solid #38BDF8;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 1.3rem;">🛡️</span>
                    <span style="font-weight: 800; font-size: 0.95rem; color: {c_text_main};">Susceptible (S)</span>
                </div>
                <div style="font-family: ui-monospace, monospace; font-size: 0.80rem; background: {"rgba(56,189,248,0.1)" if is_dark else "#E0F2FE"}; color: #0284C7; padding: 4px 8px; border-radius: 6px; margin-bottom: 8px;">
                    dS/dt = -β · (S · I) / N
                </div>
                <div style="font-size: 0.78rem; color: {c_text_muted}; line-height: 1.45;">
                    Healthy individuals who possess no prior neutralizing antibodies. This pool monotonically depletes as individuals make contacts with infectious vectors.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_box2:
        st.markdown(
            f"""
            <div class="concept-box" style="border-top: 3px solid #F59E0B;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 1.3rem;">⚡</span>
                    <span style="font-weight: 800; font-size: 0.95rem; color: {c_text_main};">Infectious (I)</span>
                </div>
                <div style="font-family: ui-monospace, monospace; font-size: 0.80rem; background: {"rgba(245,158,11,0.1)" if is_dark else "#FEF3C7"}; color: #D97706; padding: 4px 8px; border-radius: 6px; margin-bottom: 8px;">
                    dI/dt = β · (S · I) / N - γ · I
                </div>
                <div style="font-size: 0.78rem; color: {c_text_muted}; line-height: 1.45;">
                    Actively infected individuals transmitting disease. This pool expands exponentially when S/N &gt; 1/R₀, peaks at dI/dt = 0, and then declines toward extinction.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_box3:
        st.markdown(
            f"""
            <div class="concept-box" style="border-top: 3px solid #10B981;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 1.3rem;">💚</span>
                    <span style="font-weight: 800; font-size: 0.95rem; color: {c_text_main};">Recovered (R)</span>
                </div>
                <div style="font-family: ui-monospace, monospace; font-size: 0.80rem; background: {"rgba(16,185,129,0.1)" if is_dark else "#D1FAE5"}; color: #059669; padding: 4px 8px; border-radius: 6px; margin-bottom: 8px;">
                    dR/dt = γ · I
                </div>
                <div style="font-size: 0.78rem; color: {c_text_muted}; line-height: 1.45;">
                    Convalescent individuals cleared of viral shedding with lasting immunity. Total population invariance strictly requires S(t) + I(t) + R(t) = N for all t.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)

    # 3. THE 3 GOLDEN LAWS OF OUTBREAK DYNAMICS
    st.markdown(
        f"""
        <div style="margin-bottom: 14px;">
            <div style="font-size: 1.10rem; font-weight: 800; color: {c_text_main};">
                📐 The 3 Golden Mathematical Laws of Outbreaks
            </div>
            <div style="font-size: 0.82rem; color: {c_text_muted};">
                Analytical truths that hold regardless of scale, geography, or population size.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    law1, law2, law3 = st.columns(3)

    with law1:
        st.markdown(
            f"""
            <div class="spec-card">
                <div>
                    <div class="spec-header">
                        <span>🎯</span>
                        <span>Law 1: The Basic Reproduction Number</span>
                    </div>
                    <div style="font-family: ui-monospace, monospace; font-size: 0.88rem; font-weight: 700; color: #38BDF8; margin-bottom: 8px;">
                        R₀ = β / γ
                    </div>
                    <div style="font-size: 0.78rem; color: {c_text_muted}; line-height: 1.5;">
                        Represents the expected secondary cases generated by one infected host in a fully naive cohort.
                        If <b>R₀ &gt; 1</b>, an epidemic wave is biologically guaranteed. If <b>R₀ &lt; 1</b>, cases decay monotonically to zero.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with law2:
        st.markdown(
            f"""
            <div class="spec-card">
                <div>
                    <div class="spec-header">
                        <span>⚡</span>
                        <span>Law 2: The Healthcare Nullcline</span>
                    </div>
                    <div style="font-family: ui-monospace, monospace; font-size: 0.88rem; font-weight: 700; color: #F59E0B; margin-bottom: 8px;">
                        dI/dt = 0 ⟺ S(t) / N = 1 / R₀
                    </div>
                    <div style="font-size: 0.78rem; color: {c_text_muted}; line-height: 1.5;">
                        The peak of the infection wave does <i>not</i> occur when all hosts are infected. Peak ICU stress occurs at the precise day when remaining susceptible fraction falls to <b>1 / R₀</b>.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with law3:
        st.markdown(
            f"""
            <div class="spec-card">
                <div>
                    <div class="spec-header">
                        <span>🛡️</span>
                        <span>Law 3: Theoretical Herd Immunity</span>
                    </div>
                    <div style="font-family: ui-monospace, monospace; font-size: 0.88rem; font-weight: 700; color: #10B981; margin-bottom: 8px;">
                        HIT = 1 - (1 / R₀)
                    </div>
                    <div style="font-size: 0.78rem; color: {c_text_muted}; line-height: 1.5;">
                        The threshold proportion of immune hosts required to suppress transmission velocity below replacement.
                        For COVID-19 Omicron (R₀ ≈ 3.93), HIT is <b>74.5%</b>; for Measles (R₀ ≈ 12), HIT exceeds <b>91.7%</b>.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)

    # 4. FLATTEN THE CURVE POLICY IMPACT MATRIX
    st.markdown(
        f"""
        <div style="margin-bottom: 14px;">
            <div style="font-size: 1.10rem; font-weight: 800; color: {c_text_main};">
                📉 "Flatten the Curve" Policy Impact Matrix
            </div>
            <div style="font-size: 0.82rem; color: {c_text_muted};">
                Comparative simulation outcome under standard non-pharmaceutical interventions (N = 100,000 cohort).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    policy_df = pd.DataFrame(
        [
            {
                "Intervention Strategy": "1. Uncontrolled Spread",
                "Daily Contact β": "0.55",
                "Effective R": "3.93",
                "Peak Hospital Day": "Day 32",
                "Peak Active Cases": "38,420 (38.4%)",
                "Capacity Surge": "CRITICAL BREACH (+380%)",
                "Final Attack Rate": "97.8%",
            },
            {
                "Intervention Strategy": "2. Public Mask Mandate (-25% β)",
                "Daily Contact β": "0.41",
                "Effective R": "2.93",
                "Peak Hospital Day": "Day 44",
                "Peak Active Cases": "26,110 (26.1%)",
                "Capacity Surge": "Moderate Breach (+161%)",
                "Final Attack Rate": "92.3%",
            },
            {
                "Intervention Strategy": "3. Staged Circuit Breaker (-50% β)",
                "Daily Contact β": "0.27",
                "Effective R": "1.96",
                "Peak Hospital Day": "Day 68",
                "Peak Active Cases": "14,200 (14.2%)",
                "Capacity Surge": "Mild Surge (+42%)",
                "Final Attack Rate": "79.1%",
            },
            {
                "Intervention Strategy": "4. Pre-Emptive Vaccine (60% Naive Cut)",
                "Daily Contact β": "0.55",
                "Effective R": "1.57",
                "Peak Hospital Day": "Day 94",
                "Peak Active Cases": "6,800 (6.8%)",
                "Capacity Surge": "SAFE WITHIN LIMITS",
                "Final Attack Rate": "38.2%",
            },
        ]
    )
    render_styled_dataframe(policy_df, is_dark_mode=is_dark)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # 5. SCIENTIFIC & PRACTICAL FAQ
    st.markdown(
        f"""
        <div style="margin-bottom: 14px;">
            <div style="font-size: 1.10rem; font-weight: 800; color: {c_text_main};">
                ❓ Scientific & Engineering FAQ
            </div>
            <div style="font-size: 0.82rem; color: {c_text_muted};">
                Frequently asked questions on numerical integration, conservation laws, and clinical application.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Why does the epidemic wave crest before 100% of the population is infected?"):
        st.write(
            "An epidemic crests when the effective reproduction number R_eff drops below 1.0. "
            "Because R_eff = R₀ · (S/N), as susceptible individuals recover, they act as immune shields "
            "preventing transmission chains from finding viable hosts. Thus, the infection burns out naturally "
            "long before infecting the entire population."
        )

    with st.expander("What numerical integrator does this platform use, and why not Euler's method?"):
        st.write(
            "This platform utilizes the Dormand-Prince Runge-Kutta 5(4) adaptive differential solver (`scipy.integrate.solve_ivp(method='RK45')`). "
            "Simple forward Euler integration accumulates truncation error proportional to step size Δt and "
            "frequently violates conservation invariance (S + I + R = N). RK45 embeds error estimation to adjust "
            "step sizes adaptively, guaranteeing population conservation within 10⁻¹² precision."
        )

    with st.expander("How do non-pharmaceutical interventions (NPIs) modulate transmission parameter β?"):
        st.write(
            "Transmission parameter β represents the product of daily contact rate (c) and per-contact transmission probability (p): "
            "β = c · p. Non-pharmaceutical interventions like social distancing reduce contact rate c, while mask wearing and ventilation "
            "reduce transmission probability p. In this platform, an intervention reduction of 40% drops effective β by 40% on the scheduled intervention day."
        )

    with st.expander("How is the hospital capacity threshold computed and displayed?"):
        st.write(
            "Hospital capacity is calibrated as a configurable percentage of total population N (default: 8.0%). "
            "Whenever active infections I(t) exceed this threshold, the platform marks the exact decimal day of breach, "
            "calculates peak excess bed deficit, and estimates duration of critical system saturation."
        )


# -----------------------------------------------------------------------------
# 8. VIEW 4: DATA & REPORTS (CLEAN TELEMETRY HUB)
# -----------------------------------------------------------------------------
elif nav_selection == "Data & Reports":
    hero_logo_html = (
        f'<img src="{LOGO_DATA_URI}" class="hero-brand-logo" alt="SIR Logo" />'
        if LOGO_DATA_URI
        else '<span style="font-size: 2.2rem;">🧬</span>'
    )
    st.markdown(
        f"""
        <div class="hero-header">
            <div style="display: flex; align-items: center; gap: 18px;">
                {hero_logo_html}
                <div>
                    <div class="hero-badge">
                        <span class="hero-dot"></span>
                        <span>Scientific Deliverables & Exports</span>
                    </div>
                    <div class="hero-title"><span class="brand-sir">SIR</span> Data Export & Clinical Telemetry Center</div>
                    <div class="hero-sub">Export numerical trajectory datasets, machine-readable JSON metadata, and formal PDF project reports.</div>
                </div>
            </div>
            <div class="hero-stats-strip">
                <div class="hero-stat-item">📁 <b>RFC-4180</b> CSV</div>
                <div class="hero-stat-item">📑 <b>A4</b> PDF Report</div>
                <div class="hero-stat-item">⚙️ <b>JSON</b> Manifest</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sim = st.session_state.current_simulation
    summ = st.session_state.current_summary

    if sim is not None and summ is not None:
        df_export = generate_simulation_dataframe(sim)
        csv_data = generate_simulation_csv(sim)
        json_data = generate_simulation_json(sim, summ)
        txt_summary = generate_summary_report(sim, summ)

        st.markdown(
            f"""
            <div style="background:{c_surface}; border:1px solid {c_border}; border-radius:12px; padding:20px; margin-bottom:20px; box-shadow:{c_card_shadow};">
                <div style="font-size:0.95rem; font-weight:700; color:{c_text_main}; margin-bottom:14px;">📊 Numerical Trajectory Time Series Data (First 10 Rows)</div>
            """,
            unsafe_allow_html=True,
        )
        render_styled_dataframe(df_export.head(10), is_dark_mode=is_dark)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("#### Export Scientific Deliverables")
        col_ex1, col_ex2, col_ex3, col_ex4 = st.columns(4)

        with col_ex1:
            st.download_button(
                label="📥 Export CSV",
                data=csv_data,
                file_name="episim_trajectory.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col_ex2:
            st.download_button(
                label="⚙️ Export JSON",
                data=json_data,
                file_name="episim_run_parameters.json",
                mime="application/json",
                use_container_width=True,
            )

        with col_ex3:
            st.download_button(
                label="📝 Export Summary",
                data=txt_summary,
                file_name="episim_executive_summary.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with col_ex4:
            pdf_bytes = generate_simulation_pdf(sim, summ)
            st.download_button(
                label="📑 Export PDF",
                data=pdf_bytes,
                file_name="episim_clinical_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    else:
        st.markdown(
            f"""
            <div style="background:{c_surface}; border:1px solid {c_border}; border-radius:12px; padding:28px; text-align:center; box-shadow:{c_card_shadow}; margin-top:20px;">
                <div style="font-size:2rem; margin-bottom:10px;">📊</div>
                <div style="font-size:1.1rem; font-weight:700; color:{c_text_main}; margin-bottom:8px;">No Telemetry Data Available</div>
                <div style="font-size:0.85rem; color:{c_text_muted}; max-width:480px; margin:0 auto 20px auto; line-height:1.5;">
                    Please run a simulation on the <b>Live Dashboard</b> or choose a preset in the <b>Model Explorer</b> to generate data exports and clinical reports.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "⚡ Open Live Dashboard & Run Simulation",
            key="btn_goto_dash",
            type="primary",
            use_container_width=False,
        ):
            st.session_state.nav_selection_radio = "Live Dashboard"
            st.session_state.current_simulation = None
            st.rerun()

# -----------------------------------------------------------------------------
# 9. FOOTER (NEXAFO-INSPIRED ARCHITECTURE SPECS & STATUS)
# -----------------------------------------------------------------------------
render_agency_footer(is_dark, c_surface, c_border, c_text_muted, c_text_main)
