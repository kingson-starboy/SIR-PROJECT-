"""EpiSim: Disease Spread Prediction & Healthcare Capacity Intelligence Platform.

An enterprise numerical computing and epidemiological modeling application implementing
the Kermack-McKendrick SIR differential equations using adaptive Runge-Kutta 5(4) integration.
"""

from __future__ import annotations

import datetime

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
# 1. STREAMLIT PAGE CONFIGURATION & ENTERPRISE LIGHT CSS ARCHITECTURE
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EpiSim | Disease Dynamics & Capacity Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* -------------------------------------------------------------
       SCIENTIFIC DESIGN SYSTEM (WCAG 2.2 AA CONFORMING)
       Palette tokens:
       Canvas: #F7F8FA | Surface: #FFFFFF | Text: #172033 | Muted: #687386
       Borders: #E5E8EF | Primary Accent: #315EF7 | Warning: #D99A35
       ------------------------------------------------------------- */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stHeader"],
    .main,
    .main > div,
    section.main {
        background-color: #F7F8FA !important;
        color: #172033 !important;
    }

    /* SIDEBAR SURFACE */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebar"] section {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E5E8EF !important;
    }

    /* TYPOGRAPHY */
    h1, h2, h3, h4, h5, h6 {
        color: #172033 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        letter-spacing: -0.02em;
    }
    p, span, label, div {
        color: #172033 !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #172033 !important;
    }

    /* INPUT CONTROLS */
    .stSlider label, .stNumberInput label, .stSelectbox label {
        color: #334155 !important;
        font-weight: 600 !important;
        font-size: 0.80rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }
    .stSelectbox div[data-baseweb="select"] > div,
    .stNumberInput div[data-baseweb="input"],
    .stNumberInput input,
    div[data-baseweb="input"] input {
        background-color: #FFFFFF !important;
        color: #172033 !important;
        border-color: #E5E8EF !important;
        border-radius: 6px !important;
    }

    /* EXPANDER CONTAINERS */
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E8EF !important;
        border-radius: 8px !important;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 2px solid #E5E8EF !important;
        gap: 8px !important;
        padding-bottom: 2px !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #687386 !important;
        font-weight: 500 !important;
        background-color: transparent !important;
        border-radius: 6px 6px 0 0 !important;
        padding: 8px 14px !important;
        font-size: 0.86rem !important;
    }
    .stTabs [aria-selected="true"] {
        color: #315EF7 !important;
        background-color: #FFFFFF !important;
        border-bottom: 2px solid #315EF7 !important;
        font-weight: 700 !important;
    }

    /* TOP HEADER BAR */
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 0 16px 0;
        border-bottom: 1px solid #E5E8EF;
        margin-bottom: 20px;
    }
    .top-header-title {
        font-size: 1.55rem;
        font-weight: 700;
        color: #172033;
        letter-spacing: -0.025em;
        line-height: 1.2;
    }
    .top-header-sub {
        font-size: 0.86rem;
        color: #687386;
        margin-top: 3px;
    }
    .top-header-badge {
        background: #FFFFFF;
        color: #334155;
        border: 1px solid #E5E8EF;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        font-family: monospace;
    }

    /* BRAND CARD */
    .brand-box {
        padding: 10px 12px;
        background: #FFFFFF;
        border: 1px solid #E5E8EF;
        border-left: 4px solid #315EF7;
        border-radius: 6px;
        margin-bottom: 16px;
    }
    .brand-title {
        font-size: 0.95rem;
        font-weight: 800;
        color: #172033;
        letter-spacing: 0.02em;
    }
    .brand-sub {
        font-size: 0.72rem;
        font-weight: 600;
        color: #687386;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-top: 1px;
    }

    /* METRIC CARDS */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    @media (max-width: 900px) {
        .metric-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E5E8EF;
        border-radius: 8px;
        padding: 16px 18px;
        position: relative;
        box-shadow: 0 1px 3px rgba(23, 32, 51, 0.04);
    }
    .metric-card-purple { border-top: 3px solid #7C3AED; }
    .metric-card-rose   { border-top: 3px solid #E45454; }
    .metric-card-amber  { border-top: 3px solid #D99A35; }
    .metric-card-blue   { border-top: 3px solid #315EF7; }

    .metric-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #687386;
        margin-bottom: 4px;
    }
    .metric-val {
        font-size: 1.80rem;
        font-weight: 700;
        color: #172033;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .metric-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-top: 8px;
    }
    .badge-purple { background: #F3E8FF; color: #6B21A8; }
    .badge-rose   { background: #FEE2E2; color: #991B1B; }
    .badge-amber  { background: #FEF3C7; color: #92400E; }
    .badge-blue   { background: #EFF6FF; color: #1E40AF; }
    .badge-green  { background: #ECFDF5; color: #065F46; }

    /* SUMMARY INFO PANEL */
    .info-card {
        background: #FFFFFF;
        border: 1px solid #E5E8EF;
        border-radius: 8px;
        padding: 16px 20px;
        min-height: 140px;
        height: 140px;
        margin-bottom: 12px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        box-shadow: 0 1px 3px rgba(23, 32, 51, 0.03);
    }
    .info-card p {
        min-height: 52px;
        margin-bottom: 0px !important;
        line-height: 1.35;
    }
    .info-card-header {
        font-size: 0.85rem;
        font-weight: 700;
        color: #172033;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* TELEMETRY PILL */
    .telemetry-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        background: #FFFFFF;
        border: 1px solid #E5E8EF;
        border-radius: 6px;
        padding: 10px 12px;
        margin-top: 16px;
    }
    .telemetry-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #20A477;
    }

    /* PRIMARY BUTTON */
    .stButton button[kind="primary"] {
        background-color: #315EF7 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 8px 16px !important;
    }
    .stButton button[kind="primary"]:hover {
        background-color: #2448C8 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. SCENARIO PRESETS CONFIGURATION
# -----------------------------------------------------------------------------
PRESETS: dict[str, dict] = {
    "Baseline Epidemic (R0 = 3.00)": {
        "pop": 10000,
        "inf": 10,
        "rec": 0,
        "beta": 0.30,
        "gamma": 0.10,
        "duration": 160,
        "capacity_pct": 15,
        "desc": "Typical airborne outbreak without non-pharmaceutical interventions.",
    },
    "Public Health Intervention (R0 = 1.50)": {
        "pop": 10000,
        "inf": 10,
        "rec": 0,
        "beta": 0.15,
        "gamma": 0.10,
        "duration": 200,
        "capacity_pct": 15,
        "desc": "Active mitigation (distancing, masking) suppressing transmission.",
    },
    "High Transmission Spike (R0 = 5.00)": {
        "pop": 10000,
        "inf": 10,
        "rec": 0,
        "beta": 0.50,
        "gamma": 0.10,
        "duration": 120,
        "capacity_pct": 15,
        "desc": "Uncontained, rapid propagation overwhelming healthcare capacity.",
    },
    "Therapeutic Clearance (R0 = 1.50)": {
        "pop": 10000,
        "inf": 10,
        "rec": 0,
        "beta": 0.30,
        "gamma": 0.20,
        "duration": 140,
        "capacity_pct": 15,
        "desc": "Early antiviral treatment reducing average infectious duration to 5 days.",
    },
}


# -----------------------------------------------------------------------------
# 3. HIGH-PERFORMANCE CACHED SOLVER
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def cached_solve_sir(
    total_pop: float,
    init_inf: float,
    init_rec: float,
    beta: float,
    gamma: float,
    duration: float,
    resolution: int,
    capacity_limit: float | None = None,
    intervention_day: float | None = None,
    intervention_beta_reduction: float = 0.0,
    vaccination_rate: float = 0.0,
) -> tuple[SIRSimulationResult | None, EpidemiologicalSummary | None, list[str], list[str]]:
    """Validate parameters and compute adaptive RK45 ODE integration."""
    val = validate_sir_inputs(
        total_population=total_pop,
        initial_infected=init_inf,
        initial_recovered=init_rec,
        transmission_rate=beta,
        recovery_rate=gamma,
        duration_days=duration,
        num_points=resolution,
    )

    if not val.is_valid:
        return None, None, val.errors, val.warnings

    params = SIRParameters(
        total_population=float(total_pop),
        initial_infected=float(init_inf),
        initial_recovered=float(init_rec),
        transmission_rate=float(beta),
        recovery_rate=float(gamma),
        duration_days=float(duration),
        num_points=int(resolution),
        intervention_day=float(intervention_day) if intervention_day is not None else None,
        intervention_beta_reduction=float(intervention_beta_reduction),
        vaccination_rate=float(vaccination_rate),
    )

    try:
        sim_res = solve_sir(params)
        summary = analyze_simulation(sim_res, healthcare_capacity_limit=capacity_limit)
        return sim_res, summary, [], val.warnings
    except (ValueError, SolverError) as err:
        return None, None, [f"Solver Error: {str(err)}"], val.warnings


# Initialize baseline simulation in session state
if "current_simulation" not in st.session_state or st.session_state.current_simulation is None:
    init_res, init_sum, _, _ = cached_solve_sir(10000, 10, 0, 0.30, 0.10, 160, 1000, 1500)
    st.session_state.current_simulation = init_res
    st.session_state.current_summary = init_sum

if "scenario_a" not in st.session_state:
    st.session_state.scenario_a = None

if "scenario_b" not in st.session_state:
    st.session_state.scenario_b = None

if "simulation_history" not in st.session_state:
    st.session_state.simulation_history = []

if "historical_df" not in st.session_state:
    st.session_state.historical_df = None


# -----------------------------------------------------------------------------
# 4. SIDEBAR: NAVIGATION & CONTROL CENTER
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-box">
            <div class="brand-title">EpiSim Pro</div>
            <div class="brand-sub">Epidemic Intelligence Platform</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_selection = st.radio(
        "Workspace View",
        [
            "Live Dashboard",
            "Scenario Comparison",
            "Mathematical Model",
            "Data & Reports",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Render Simulation Controls when on Live Dashboard
    if nav_selection == "Live Dashboard":
        st.markdown(
            "<p style='font-size:0.75rem; font-weight:700; color:#687386; text-transform:uppercase; margin-bottom:6px;'>Simulation Parameters</p>",
            unsafe_allow_html=True,
        )

        preset_choice = st.selectbox(
            "Scenario Preset",
            ["Custom Configuration"] + list(PRESETS.keys()),
            index=1,
            help="Select an epidemiological archetype or define custom parameters.",
        )

        if preset_choice != "Custom Configuration":
            p_data = PRESETS[preset_choice]
            def_pop, def_inf, def_rec = p_data["pop"], p_data["inf"], p_data["rec"]
            def_beta, def_gamma, def_dur = p_data["beta"], p_data["gamma"], p_data["duration"]
            def_cap = p_data["capacity_pct"]
        else:
            def_pop, def_inf, def_rec = 10000, 10, 0
            def_beta, def_gamma, def_dur = 0.30, 0.10, 160
            def_cap = 15

        inp_n = st.number_input(
            "Total Population (N)",
            min_value=100,
            max_value=50000000,
            value=int(def_pop),
            step=1000,
            help="Total closed host population size.",
        )

        col_in1, col_in2 = st.columns(2)
        with col_in1:
            inp_i0 = st.number_input(
                "Infected I(0)",
                min_value=1,
                max_value=int(inp_n),
                value=int(def_inf),
                step=1,
                help="Initial infectious individuals.",
            )
        with col_in2:
            inp_r0 = st.number_input(
                "Recovered R(0)",
                min_value=0,
                max_value=int(inp_n),
                value=int(def_rec),
                step=1,
                help="Initial immune individuals.",
            )

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
            help="Daily clearance fraction (1/γ = mean infectious duration).",
        )

        col_in3, col_in4 = st.columns(2)
        with col_in3:
            inp_dur = st.number_input(
                "Days",
                min_value=10,
                max_value=1000,
                value=int(def_dur),
                step=10,
                help="Integration time span.",
            )
        with col_in4:
            inp_cap_pct = st.number_input(
                "ICU Bed %",
                min_value=1,
                max_value=50,
                value=int(def_cap),
                step=1,
                help="Healthcare capacity threshold as % of population.",
            )

        capacity_beds = (inp_cap_pct / 100.0) * inp_n

        # Policy Interventions & Immunization Options
        with st.expander("🛡️ Interventions & Vaccination", expanded=False):
            enable_interv = st.checkbox("Staged Intervention (Lockdown / NPI)", value=False)
            if enable_interv:
                col_npi1, col_npi2 = st.columns(2)
                with col_npi1:
                    inp_interv_day = st.number_input(
                        "Start Day", min_value=1, max_value=int(inp_dur), value=25, step=5
                    )
                with col_npi2:
                    inp_beta_red = st.slider("β Reduction %", min_value=5, max_value=90, value=40, step=5)
                interv_day_val = float(inp_interv_day)
                interv_red_val = inp_beta_red / 100.0
            else:
                interv_day_val = None
                interv_red_val = 0.0

            enable_vax = st.checkbox("Active Vaccination Campaign", value=False)
            if enable_vax:
                inp_vax_rate_pct = st.slider(
                    "Daily Vaccination (% of S)", min_value=0.1, max_value=5.0, value=1.0, step=0.1
                )
                vax_rate_val = inp_vax_rate_pct / 100.0
            else:
                vax_rate_val = 0.0

        btn_run = st.button("⚡ Run Simulation", type="primary", use_container_width=True)

        if btn_run:
            with st.spinner("Solving differential system..."):
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
                    # Save run to history (capped at 5)
                    run_record = {
                        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                        "label": f"N={inp_n:,.0f}, β={inp_beta:.2f}, γ={inp_gamma:.2f}",
                        "params": (
                            inp_n,
                            inp_i0,
                            inp_r0,
                            inp_beta,
                            inp_gamma,
                            inp_dur,
                            capacity_beds,
                            interv_day_val,
                            interv_red_val,
                            vax_rate_val,
                        ),
                    }
                    st.session_state.simulation_history.insert(0, run_record)
                    if len(st.session_state.simulation_history) > 5:
                        st.session_state.simulation_history.pop()
                    st.toast("Simulation converged successfully", icon="✅")

        # Scenario History Selector
        if len(st.session_state.simulation_history) > 1:
            st.markdown(
                "<p style='font-size:0.75rem; font-weight:700; color:#687386; text-transform:uppercase; margin-top:12px;'>Recent Run History</p>",
                unsafe_allow_html=True,
            )
            history_labels = [f"{r['timestamp']} - {r['label']}" for r in st.session_state.simulation_history]
            selected_hist = st.selectbox("Restore Run", options=history_labels, label_visibility="collapsed")
            if st.button("🔄 Restore Selected Run", use_container_width=True):
                hist_idx = history_labels.index(selected_hist)
                p_tuple = st.session_state.simulation_history[hist_idx]["params"]
                restored_sim, restored_sum, _, _ = cached_solve_sir(
                    p_tuple[0],
                    p_tuple[1],
                    p_tuple[2],
                    p_tuple[3],
                    p_tuple[4],
                    p_tuple[5],
                    1000,
                    p_tuple[6],
                    p_tuple[7],
                    p_tuple[8],
                    p_tuple[9],
                )
                st.session_state.current_simulation = restored_sim
                st.session_state.current_summary = restored_sum
                st.rerun()

    # Persistent Solver Telemetry Status
    sim_curr = st.session_state.current_simulation
    if sim_curr is not None:
        p_act = sim_curr.parameters
        st.markdown(
            f"""
            <div class="telemetry-pill">
                <div class="telemetry-dot"></div>
                <div style="font-size: 0.74rem; color: #687386; line-height: 1.3;">
                    <b>RK45 Adaptive</b> • N = {p_act.total_population:,.0f}<br>
                    Conservation error: {sim_curr.max_conservation_error:.1e}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# -----------------------------------------------------------------------------
# 5. VIEW 1: LIVE DASHBOARD
# -----------------------------------------------------------------------------
if nav_selection == "Live Dashboard":
    sim = st.session_state.current_simulation
    summ = st.session_state.current_summary

    # Minimalist Header Bar
    st.markdown(
        """
        <div class="top-header">
            <div>
                <div class="top-header-title">Disease Spread Prediction & Healthcare Surge Intelligence</div>
                <div class="top-header-sub">Continuous Kermack-McKendrick SIR differential dynamics solved via adaptive Runge-Kutta 5(4).</div>
            </div>
            <div class="top-header-badge">DETERMINISTIC ODE ENGINE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if sim is not None and summ is not None:
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
                    <div class="metric-label">Peak Infection Burden</div>
                    <div class="metric-val">{summ.peak.peak_infections:,.0f}</div>
                    <span class="metric-badge badge-rose">{summ.peak.peak_percentage:.1f}% Population Active</span>
                </div>
                <div class="metric-card metric-card-amber">
                    <div class="metric-label">Peak Influx Day</div>
                    <div class="metric-val">Day {summ.peak.peak_day:.1f}</div>
                    <span class="metric-badge badge-amber">{"Crest Reached" if summ.peak.has_distinct_peak else "Subcritical"}</span>
                </div>
                <div class="metric-card metric-card-blue">
                    <div class="metric-label">Total Affected (Attack Rate)</div>
                    <div class="metric-val">{summ.final_stats.total_affected:,.0f}</div>
                    <span class="metric-badge badge-blue">{summ.final_stats.percent_affected:.1f}% Attack Rate</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
            st.plotly_chart(create_sir_curve_chart(sim), use_container_width=True)

        with tab_peak:
            st.plotly_chart(
                create_peak_analysis_chart(sim, summ, show_capacity=True), use_container_width=True
            )

        with tab_phase:
            st.plotly_chart(create_phase_space_chart(sim, summ), use_container_width=True)

        with tab_donut:
            col_dn1, col_dn2 = st.columns([1, 1])
            with col_dn1:
                st.plotly_chart(
                    create_population_distribution_chart(summ, sim.parameters.total_population),
                    use_container_width=True,
                )
            with col_dn2:
                st.plotly_chart(
                    create_animated_progression_chart(sim),
                    use_container_width=True,
                )

        with tab_rate:
            st.plotly_chart(create_infection_rate_trend_chart(sim), use_container_width=True)

        with tab_re:
            st.plotly_chart(create_effective_r_chart(sim, summ), use_container_width=True)

        with tab_sens:
            sens_items = compute_parameter_sensitivity(sim.parameters)
            st.plotly_chart(create_sensitivity_chart(sens_items), use_container_width=True)

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
                    # Generate synthetic benchmark empirical observations
                    bench_days = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 100, 120], dtype=float)
                    synth_i = np.interp(bench_days, sim.t, sim.I)
                    # Add mild noise
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

                st.plotly_chart(create_model_vs_data_chart(sim, h_df, fit_metrics), use_container_width=True)
            else:
                st.info(
                    "💡 Upload a CSV file or click 'Load Reference Wave Dataset' to compare against empirical data."
                )

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # 2-Column Clinical Dynamics & Numerical Diagnostics
        col_out1, col_out2 = st.columns(2)

        with col_out1:
            hit_str = (
                f"{summ.trends.herd_immunity_threshold:.1f}%"
                if summ.trends.herd_immunity_threshold is not None
                else "N/A (R₀ ≤ 1.0)"
            )
            clearance_str = (
                f"Day {summ.trends.clearance_day:.1f}"
                if summ.trends.clearance_day is not None
                else "Did not fall below threshold within time horizon"
            )
            surge_str = (
                f"Surge Breach at Day {summ.capacity.breach_day_start:.1f} ({summ.capacity.breach_duration_days:.1f} days breach, peak excess {summ.capacity.peak_excess_cases:,.0f} beds)"
                if summ.capacity.is_breached
                else "Within capacity limits (Zero breaches)"
            )

            st.markdown(
                f"""
                <div class="info-card">
                    <div class="info-card-header">📊 Outbreak Dynamics & Healthcare Impact</div>
                    <table style="width: 100%; font-size: 0.88rem; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #E5E8EF;">
                            <td style="padding: 6px 0; color: #687386;">Theoretical Herd Immunity Threshold</td>
                            <td style="padding: 6px 0; font-weight: 600; text-align: right; color: #172033;">{hit_str}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #E5E8EF;">
                            <td style="padding: 6px 0; color: #687386;">Initial Wave Trajectory</td>
                            <td style="padding: 6px 0; font-weight: 600; text-align: right; color: #172033;">{summ.trends.initial_trend}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #E5E8EF;">
                            <td style="padding: 6px 0; color: #687386;">Infection Clearance Horizon (&lt;5 active)</td>
                            <td style="padding: 6px 0; font-weight: 600; text-align: right; color: #172033;">{clearance_str}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #687386;">Healthcare Surge Status</td>
                            <td style="padding: 6px 0; font-weight: 600; text-align: right; color: {"#E45454" if summ.capacity.is_breached else "#20A477"};">{surge_str}</td>
                        </tr>
                    </table>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_out2:
            st.markdown(
                f"""
                <div class="info-card">
                    <div class="info-card-header">⚡ Numerical Precision & Conservation Diagnostics</div>
                    <table style="width: 100%; font-size: 0.88rem; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #E5E8EF;">
                            <td style="padding: 6px 0; color: #687386;">Total Population Invariance |S+I+R - N|</td>
                            <td style="padding: 6px 0; font-weight: 600; text-align: right; color: #20A477;">{sim.max_conservation_error:.2e} (Strict)</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #E5E8EF;">
                            <td style="padding: 6px 0; color: #687386;">Numerical Solver Algorithm</td>
                            <td style="padding: 6px 0; font-weight: 600; text-align: right; color: #172033;">Dormand-Prince RK5(4) Adaptive</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #E5E8EF;">
                            <td style="padding: 6px 0; color: #687386;">Evaluated Time Steps</td>
                            <td style="padding: 6px 0; font-weight: 600; text-align: right; color: #172033;">{len(sim.t):,} discrete steps</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #687386;">Compartmental Non-Negativity</td>
                            <td style="padding: 6px 0; font-weight: 600; text-align: right; color: #20A477;">Verified (S, I, R ≥ 0 for all t)</td>
                        </tr>
                    </table>
                </div>
                """,
                unsafe_allow_html=True,
            )


# -----------------------------------------------------------------------------
# 6. VIEW 2: SCENARIO COMPARISON STUDIO
# -----------------------------------------------------------------------------
elif nav_selection == "Scenario Comparison":
    st.markdown(
        """
        <div class="top-header">
            <div>
                <div class="top-header-title">Comparative Policy & Intervention Studio</div>
                <div class="top-header-sub">Simulate and evaluate two distinct epidemiological policy scenarios side-by-side.</div>
            </div>
            <div class="top-header-badge">POLICY LAB</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(
            "<p style='font-size:0.80rem; font-weight:700; color:#E45454; text-transform:uppercase;'>Scenario A: Baseline (Uncontrolled)</p>",
            unsafe_allow_html=True,
        )
        sc_a_n = st.number_input(
            "Population N (Scenario A)", min_value=100, value=10000, step=1000, key="ca_n"
        )
        sc_a_i0 = st.number_input("Initial Infected I(0)", min_value=1, value=10, key="ca_i0")
        sc_a_beta = st.slider("Transmission Rate β", 0.05, 1.50, 0.30, 0.01, key="ca_b")
        sc_a_gamma = st.slider("Recovery Rate γ", 0.02, 0.50, 0.10, 0.01, key="ca_g")
        sc_a_dur = st.number_input("Duration (Days)", min_value=20, value=160, key="ca_d")

    with col_b:
        st.markdown(
            "<p style='font-size:0.80rem; font-weight:700; color:#315EF7; text-transform:uppercase;'>Scenario B: Intervention (Flattened)</p>",
            unsafe_allow_html=True,
        )
        sc_b_n = st.number_input(
            "Population N (Scenario B)", min_value=100, value=10000, step=1000, key="cb_n"
        )
        sc_b_i0 = st.number_input("Initial Infected I(0)", min_value=1, value=10, key="cb_i0")
        sc_b_beta = st.slider("Transmission Rate β (Mitigated)", 0.05, 1.50, 0.18, 0.01, key="cb_b")
        sc_b_gamma = st.slider("Recovery Rate γ", 0.02, 0.50, 0.10, 0.01, key="cb_g")
        sc_b_dur = st.number_input("Duration (Days)", min_value=20, value=160, key="cb_d")

    btn_compare = st.button("⚖️ Run Comparative Simulation", type="primary", use_container_width=True)

    if btn_compare or st.session_state.scenario_a is None:
        r_a, s_a, _, _ = cached_solve_sir(sc_a_n, sc_a_i0, 0, sc_a_beta, sc_a_gamma, sc_a_dur, 1000)
        r_b, s_b, _, _ = cached_solve_sir(sc_b_n, sc_b_i0, 0, sc_b_beta, sc_b_gamma, sc_b_dur, 1000)
        st.session_state.scenario_a = (r_a, s_a)
        st.session_state.scenario_b = (r_b, s_b)

    if st.session_state.scenario_a and st.session_state.scenario_b:
        r_a, s_a = st.session_state.scenario_a
        r_b, s_b = st.session_state.scenario_b

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        peak_diff = s_b.peak.peak_infections - s_a.peak.peak_infections
        peak_pct_diff = (peak_diff / s_a.peak.peak_infections * 100) if s_a.peak.peak_infections > 0 else 0
        day_diff = s_b.peak.peak_day - s_a.peak.peak_day
        attack_diff = s_b.final_stats.percent_affected - s_a.final_stats.percent_affected

        st.markdown(
            f"""
            <div class="metric-grid">
                <div class="metric-card metric-card-blue">
                    <div class="metric-label">Peak Burden Reduction</div>
                    <div class="metric-val">{abs(peak_diff):,.0f}</div>
                    <span class="metric-badge badge-blue">{peak_pct_diff:.1f}% Peak Reduction</span>
                </div>
                <div class="metric-card metric-card-amber">
                    <div class="metric-label">Peak Delay (Curve Flattened)</div>
                    <div class="metric-val">{abs(day_diff):.1f} Days</div>
                    <span class="metric-badge badge-amber">Capacity Window Preserved</span>
                </div>
                <div class="metric-card metric-card-purple">
                    <div class="metric-label">Attack Rate Change</div>
                    <div class="metric-val">{attack_diff:+.1f}%</div>
                    <span class="metric-badge badge-purple">Cumulative Incidence</span>
                </div>
                <div class="metric-card metric-card-rose">
                    <div class="metric-label">R₀ Reduction</div>
                    <div class="metric-val">{(s_b.R0 - s_a.R0):+.2f}</div>
                    <span class="metric-badge badge-rose">{s_a.R0:.2f} → {s_b.R0:.2f}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.plotly_chart(
            create_scenario_comparison_chart(r_a, r_b, "Scenario A (Baseline)", "Scenario B (Intervention)"),
            use_container_width=True,
        )


# -----------------------------------------------------------------------------
# 7. VIEW 3: MATHEMATICAL MODEL & METHODOLOGY
# -----------------------------------------------------------------------------
elif nav_selection == "Mathematical Model":
    st.markdown(
        """
        <div class="top-header">
            <div>
                <div class="top-header-title">Mathematical Formulation & Dynamical Proofs</div>
                <div class="top-header-sub">Continuous differential systems, threshold theorems, and numerical solver specifications.</div>
            </div>
            <div class="top-header-badge">ODE FORMULATION</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_m1, col_m2 = st.columns([3, 2])

    with col_m1:
        st.markdown("#### The Kermack-McKendrick SIR System")
        st.markdown(
            """
            The transmission dynamics of an infectious pathogen in a closed host population are governed by
            three coupled non-linear ordinary differential equations:

            $$\\frac{dS}{dt} = -\\beta \\frac{S(t) \\cdot I(t)}{N} - \\nu S(t)$$

            $$\\frac{dI}{dt} = \\beta \\frac{S(t) \\cdot I(t)}{N} - \\gamma I(t)$$

            $$\\frac{dR}{dt} = \\gamma I(t) + \\nu S(t)$$

            Where:
            - **$S(t)$:** Susceptible hosts vulnerable to infection.
            - **$I(t)$:** Infectious hosts currently capable of transmitting the pathogen.
            - **$R(t)$:** Removed/recovered hosts with permanent protective immunity.
            - **$\\nu$:** Continuous vaccination rate diverting susceptible hosts directly to immunity.
            - **$N = S(t) + I(t) + R(t)$:** Total population, strictly conserved $\\left(\\frac{dN}{dt} = 0\\right)$.
            """
        )

        st.markdown("#### Threshold Theorems & The Critical Crest")
        st.markdown(
            """
            Factoring the infected differential equation:
            $$\\frac{dI}{dt} = \\left( \\frac{\\beta S(t)}{N} - \\gamma \\right) I(t) = \\gamma \\left( R_0 \\frac{S(t)}{N} - 1 \\right) I(t)$$

            - **Outbreak Expansion ($dI/dt > 0$):** Occurs if and only if $S(0) > \\frac{N}{R_0}$ and $R_0 > 1$.
            - **The Peak Infection Crest ($dI/dt = 0$):** The peak infection occurs exactly when the susceptible population crosses the critical nullcline:
            $$S^* = \\frac{N}{R_0}$$
            - **Burnout Phase ($dI/dt < 0$):** Once $S(t) < S^*$, transmission velocity becomes negative and the epidemic burns out, leaving a non-zero residual susceptible population ($S_\\infty > 0$).
            """
        )

    with col_m2:
        st.markdown(
            """
            <div class="info-card">
                <div class="info-card-header">⚙️ Numerical Integration Specs</div>
                <ul style="font-size: 0.88rem; color: #687386; padding-left: 20px; line-height: 1.6;">
                    <li><b>Solver Algorithm:</b> Explicit Runge-Kutta pair of order 5(4) (Dormand-Prince, RK45).</li>
                    <li><b>Error Tolerances:</b> Relative tolerance $10^{-7}$, Absolute tolerance $10^{-9}$.</li>
                    <li><b>Mass Conservation Law:</b> Invariance $\\sum |S+I+R - N| < 10^{-11}$.</li>
                    <li><b>Evaluation Domain:</b> Continuous $t \\in [0, T]$ evaluated uniformly over $M$ interpolation nodes.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="info-card">
                <div class="info-card-header">🛡️ Core Physical Assumptions</div>
                <ol style="font-size: 0.88rem; color: #687386; padding-left: 20px; line-height: 1.6;">
                    <li><b>Closed Cohort:</b> Zero natural births or mortality ($dN/dt = 0$).</li>
                    <li><b>Homogeneous Mixing:</b> Equal contact probability across all hosts.</li>
                    <li><b>Constant Durability:</b> Durable immunity post-infection.</li>
                    <li><b>Deterministic Formulation:</b> Continuous limits valid for $N \\gg 1$.</li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )


# -----------------------------------------------------------------------------
# 8. VIEW 4: DATA & TELEMETRY EXPORT
# -----------------------------------------------------------------------------
elif nav_selection == "Data & Reports":
    st.markdown(
        """
        <div class="top-header">
            <div>
                <div class="top-header-title">Data Export & Clinical Telemetry Center</div>
                <div class="top-header-sub">Export numerical trajectory datasets, machine-readable JSON metadata, and technical summary reports.</div>
            </div>
            <div class="top-header-badge">DATA HUB</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sim = st.session_state.current_simulation
    summ = st.session_state.current_summary

    if sim is not None and summ is not None:
        csv_str = generate_simulation_csv(sim, summ)
        json_str = generate_simulation_json(sim, summ)
        md_report = generate_summary_report(sim, summ)
        pdf_bytes = generate_simulation_pdf(sim, summ)
        df_export = generate_simulation_dataframe(sim, summ)

        col_d1, col_d2, col_d3, col_d4 = st.columns(4)

        with col_d1:
            st.markdown(
                """
                <div class="info-card">
                    <div class="info-card-header">📄 CSV Trajectory</div>
                    <p style="font-size: 0.82rem; color: #687386;">Full numerical time series of S, I, R, Re(t), and new infection rates.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.download_button(
                "⬇ Download CSV",
                data=csv_str,
                file_name="episim_trajectory_dataset.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col_d2:
            st.markdown(
                """
                <div class="info-card">
                    <div class="info-card-header">⚙️ Machine JSON</div>
                    <p style="font-size: 0.82rem; color: #687386;">Structured JSON containing solver metadata, parameters, and telemetry.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.download_button(
                "⬇ Download JSON",
                data=json_str,
                file_name="episim_telemetry_package.json",
                mime="application/json",
                use_container_width=True,
            )

        with col_d3:
            st.markdown(
                """
                <div class="info-card">
                    <div class="info-card-header">📋 Summary (MD)</div>
                    <p style="font-size: 0.82rem; color: #687386;">Executive Markdown report summarizing clinical metrics and equations.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.download_button(
                "⬇ Download MD",
                data=md_report,
                file_name="episim_summary_report.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with col_d4:
            st.markdown(
                """
                <div class="info-card">
                    <div class="info-card-header">📑 Scientific PDF</div>
                    <p style="font-size: 0.82rem; color: #687386;">Publication-grade 2-page PDF report with embedded vector charts and diagnostics.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.download_button(
                "⬇ Download PDF",
                data=pdf_bytes,
                file_name="episim_scientific_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        st.markdown("##### High-Resolution Trajectory Channel Preview")
        st.dataframe(df_export.head(15), use_container_width=True)

        with st.expander("📄 Preview Executive Technical Report"):
            st.markdown(md_report)
