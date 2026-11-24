"""Script to generate all scientific diagrams and illustrations for the Academic Report."""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = "/Users/kingsonisrael/Downloads/SIR PROJECT/report_illustrations"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Common styling constants
COLOR_SUSC = "#2563EB"  # Blue
COLOR_INF = "#DC2626"  # Red
COLOR_REC = "#059669"  # Green
COLOR_DARK = "#0F172A"  # Slate 900
COLOR_MUTED = "#64748B"  # Slate 500
COLOR_CARD = "#FFFFFF"
COLOR_BG = "#F8FAFC"
COLOR_BORDER = "#CBD5E1"

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Helvetica", "Arial"]
plt.rcParams["axes.edgecolor"] = "#CBD5E1"
plt.rcParams["axes.linewidth"] = 0.8


def fig_01_sir_compartment_flow():
    """Figure 1: Classical SIR Compartment Model Transition Dynamics."""
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=300)
    ax.set_facecolor(COLOR_BG)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")

    # Susceptible Box
    s_box = patches.FancyBboxPatch(
        (0.8, 1.2),
        2.2,
        1.6,
        boxstyle="round,pad=0.2",
        facecolor="#EFF6FF",
        edgecolor=COLOR_SUSC,
        linewidth=2.5,
    )
    ax.add_patch(s_box)
    ax.text(1.9, 2.3, "SUSCEPTIBLE (S)", fontsize=11, fontweight="bold", ha="center", color=COLOR_SUSC)
    ax.text(1.9, 1.8, "Naive Hosts\nPotential Victims", fontsize=8.5, ha="center", color="#1E40AF")
    ax.text(1.9, 1.35, "dS/dt = - β·S·I / N", fontsize=9, fontweight="bold", ha="center", color=COLOR_DARK)

    # Infected Box
    i_box = patches.FancyBboxPatch(
        (4.0, 1.2),
        2.2,
        1.6,
        boxstyle="round,pad=0.2",
        facecolor="#FEF2F2",
        edgecolor=COLOR_INF,
        linewidth=2.5,
    )
    ax.add_patch(i_box)
    ax.text(5.1, 2.3, "INFECTED (I)", fontsize=11, fontweight="bold", ha="center", color=COLOR_INF)
    ax.text(5.1, 1.8, "Contagious Carriers\nActive Spreaders", fontsize=8.5, ha="center", color="#991B1B")
    ax.text(5.1, 1.35, "dI/dt = β·S·I/N - γ·I", fontsize=9, fontweight="bold", ha="center", color=COLOR_DARK)

    # Recovered Box
    r_box = patches.FancyBboxPatch(
        (7.2, 1.2),
        2.2,
        1.6,
        boxstyle="round,pad=0.2",
        facecolor="#ECFDF5",
        edgecolor=COLOR_REC,
        linewidth=2.5,
    )
    ax.add_patch(r_box)
    ax.text(8.3, 2.3, "RECOVERED (R)", fontsize=11, fontweight="bold", ha="center", color=COLOR_REC)
    ax.text(8.3, 1.8, "Immune Population\nSterilizing Immunity", fontsize=8.5, ha="center", color="#065F46")
    ax.text(8.3, 1.35, "dR/dt = γ·I", fontsize=9, fontweight="bold", ha="center", color=COLOR_DARK)

    # Arrow 1: S -> I
    arrow1 = patches.FancyArrowPatch(
        (3.15, 2.0), (3.85, 2.0), arrowstyle="->,head_width=5,head_length=8", color=COLOR_INF, linewidth=2.5
    )
    ax.add_patch(arrow1)
    ax.text(
        3.5,
        2.35,
        "Transmission\nFlux: β·S·I/N",
        fontsize=8.5,
        fontweight="bold",
        ha="center",
        color=COLOR_INF,
    )

    # Arrow 2: I -> R
    arrow2 = patches.FancyArrowPatch(
        (6.35, 2.0), (7.05, 2.0), arrowstyle="->,head_width=5,head_length=8", color=COLOR_REC, linewidth=2.5
    )
    ax.add_patch(arrow2)
    ax.text(6.7, 2.35, "Recovery\nFlux: γ·I", fontsize=8.5, fontweight="bold", ha="center", color=COLOR_REC)

    # Conservation Banner
    cons_box = patches.FancyBboxPatch(
        (2.0, 0.2),
        6.0,
        0.65,
        boxstyle="round,pad=0.1",
        facecolor="#FFFFFF",
        edgecolor=COLOR_BORDER,
        linewidth=1.2,
    )
    ax.add_patch(cons_box)
    ax.text(
        5.0,
        0.52,
        "MASS CONSERVATION LAW:  S(t) + I(t) + R(t) ≡ N  (for all t ≥ 0)",
        fontsize=9.5,
        fontweight="bold",
        ha="center",
        color=COLOR_DARK,
    )

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_01_sir_compartment_flow.png"), dpi=300)
    plt.close()


def fig_02_problem_solution():
    """Figure 2: Problem-to-Solution Transformation Workflow."""
    fig, ax = plt.subplots(figsize=(10, 3.6), dpi=300)
    ax.set_facecolor(COLOR_BG)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")

    # Left: The Problem
    p_box = patches.FancyBboxPatch(
        (0.5, 0.8), 3.8, 2.6, boxstyle="round,pad=0.2", facecolor="#FFF1F2", edgecolor="#E11D48", linewidth=2
    )
    ax.add_patch(p_box)
    ax.text(
        2.4, 3.0, "THE PROBLEM & CHALLENGE", fontsize=10.5, fontweight="bold", ha="center", color="#9F1239"
    )
    p_text = (
        "• Non-linear ODEs lack closed-form solutions\n"
        "• Manual Euler steps are tedious and unstable\n"
        "• Impossible to visualize threshold dynamics\n"
        "• Healthcare capacity breaches unforeseen\n"
        "• Abstract equations disengage learners"
    )
    ax.text(0.8, 1.85, p_text, fontsize=8.2, va="center", color="#4C0519", linespacing=1.4)

    # Center: Transformation Arrow
    t_arrow = patches.FancyArrowPatch(
        (4.5, 2.1), (5.5, 2.1), arrowstyle="->,head_width=6,head_length=10", color="#4F46E5", linewidth=3
    )
    ax.add_patch(t_arrow)
    ax.text(
        5.0,
        2.45,
        "COMPUTATIONAL\nTRANSFORMATION",
        fontsize=8,
        fontweight="bold",
        ha="center",
        color="#4338CA",
    )

    # Right: The Solution
    s_box = patches.FancyBboxPatch(
        (5.7, 0.8), 3.8, 2.6, boxstyle="round,pad=0.2", facecolor="#F0FDF4", edgecolor="#16A34A", linewidth=2
    )
    ax.add_patch(s_box)
    ax.text(
        7.6, 3.0, "THE EPISIM PRO SOLUTION", fontsize=10.5, fontweight="bold", ha="center", color="#166534"
    )
    s_text = (
        "• Adaptive SciPy Runge-Kutta solver (RK45)\n"
        "• Real-time interactive parameter sliders\n"
        "• Hospital capacity surge breach detection\n"
        "• Dual-scenario comparative intervention\n"
        "• Automated publication-grade PDF reporting"
    )
    ax.text(6.0, 1.85, s_text, fontsize=8.2, va="center", color="#052E16", linespacing=1.4)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_02_problem_solution.png"), dpi=300)
    plt.close()


def fig_03_equation_breakdown():
    """Figure 3: Annotated Mathematical Equation Breakdown."""
    fig, ax = plt.subplots(figsize=(10, 4.0), dpi=300)
    ax.set_facecolor(COLOR_BG)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    # Main Card
    card = patches.FancyBboxPatch(
        (0.5, 0.5),
        9.0,
        4.0,
        boxstyle="round,pad=0.2",
        facecolor="#FFFFFF",
        edgecolor=COLOR_BORDER,
        linewidth=1.5,
    )
    ax.add_patch(card)
    ax.text(
        5.0,
        4.1,
        "MATHEMATICAL FORMULATION & ANNOTATED DERIVATIVE TERMS",
        fontsize=11,
        fontweight="bold",
        ha="center",
        color=COLOR_DARK,
    )

    # Term 1: dS/dt
    ax.text(1.2, 3.2, "dS/dt  =  - β · ( S · I ) / N", fontsize=12, fontweight="bold", color=COLOR_SUSC)
    ax.text(
        1.2,
        2.7,
        "[-] Negative sign: Susceptible population strictly decreases over time.",
        fontsize=8,
        color=COLOR_MUTED,
    )
    ax.text(
        1.2,
        2.35,
        "[β·S·I/N] Bilinear incidence: infection probability is proportional to contacts.",
        fontsize=8,
        color=COLOR_MUTED,
    )

    # Term 2: dI/dt
    ax.text(
        1.2, 1.6, "dI/dt  =  + β · ( S · I ) / N  -  γ · I", fontsize=12, fontweight="bold", color=COLOR_INF
    )
    ax.text(
        1.2,
        1.1,
        "[+ Inflow] Newly exposed susceptibles entering infectious state.",
        fontsize=8,
        color=COLOR_MUTED,
    )
    ax.text(
        1.2,
        0.75,
        "[- Outflow] Infected individuals recovering at rate γ = 1 / (infectious duration).",
        fontsize=8,
        color=COLOR_MUTED,
    )

    # Right Callout: Nullcline
    callout = patches.FancyBboxPatch(
        (6.6, 0.9),
        2.6,
        2.6,
        boxstyle="round,pad=0.15",
        facecolor="#F1F5F9",
        edgecolor="#94A3B8",
        linewidth=1.2,
    )
    ax.add_patch(callout)
    ax.text(7.9, 3.15, "EPIDEMIC THRESHOLD", fontsize=9.5, fontweight="bold", ha="center", color=COLOR_DARK)
    ax.text(
        7.9,
        2.5,
        "dI/dt = 0  iff:\nS* = N / R₀\n\nIf S > N/R₀: Wave expands\nIf S < N/R₀: Wave declines",
        fontsize=8.5,
        ha="center",
        color="#334155",
        linespacing=1.3,
    )

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_03_equation_breakdown.png"), dpi=300)
    plt.close()


def fig_04_r0_threshold():
    """Figure 4: Reproduction Number Threshold Phase Spectrum."""
    fig, ax = plt.subplots(figsize=(10, 3.2), dpi=300)
    ax.set_facecolor(COLOR_BG)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")

    # Gradient Spectrum Bar
    ax.fill_between([0.8, 5.0], [1.2, 1.2], [1.8, 1.8], color="#DCFCE7")  # Subcritical (Green)
    ax.fill_between([5.0, 9.2], [1.2, 1.2], [1.8, 1.8], color="#FEE2E2")  # Supercritical (Red)
    rect = patches.Rectangle((0.8, 1.2), 8.4, 0.6, fill=False, edgecolor=COLOR_BORDER, linewidth=1.5)
    ax.add_patch(rect)

    # Threshold Line at R0 = 1.0
    ax.plot([5.0, 5.0], [0.9, 2.1], color=COLOR_DARK, linewidth=2.5, linestyle="--")
    ax.text(
        5.0,
        2.3,
        "CRITICAL THRESHOLD: R₀ = 1.0",
        fontsize=10,
        fontweight="bold",
        ha="center",
        color=COLOR_DARK,
    )

    # Subcritical annotations
    ax.text(
        2.9, 1.5, "SUBCRITICAL REGIME (R₀ < 1.0)", fontsize=9, fontweight="bold", ha="center", color="#166534"
    )
    ax.text(
        2.9,
        0.6,
        "Pathogen Burns Out Naturally\nEach host infects < 1 person\nNo Epidemic Wave Crest",
        fontsize=8,
        ha="center",
        color="#14532D",
    )

    # Supercritical annotations
    ax.text(
        7.1,
        1.5,
        "SUPERCRITICAL REGIME (R₀ > 1.0)",
        fontsize=9,
        fontweight="bold",
        ha="center",
        color="#991B1B",
    )
    ax.text(
        7.1,
        0.6,
        "Exponential Pathogen Spread\nEach host infects > 1 person\nWave crests until S drops below N/R₀",
        fontsize=8,
        ha="center",
        color="#7F1D1D",
    )

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_04_r0_threshold.png"), dpi=300)
    plt.close()


def fig_05_technology_architecture():
    """Figure 5: Decoupled Multi-Tier Technology Architecture."""
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=300)
    ax.set_facecolor(COLOR_BG)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    # Title
    ax.text(
        5.0,
        4.6,
        "EPISIM PRO — TECHNOLOGY STACK INTEGRATION MATRIX",
        fontsize=11,
        fontweight="bold",
        ha="center",
        color=COLOR_DARK,
    )

    techs = [
        ("Python 3.9+", "Core Language\nNumerical Architecture", 0.6, 2.8, "#EFF6FF", "#2563EB"),
        ("SciPy solve_ivp", "Adaptive RK45 ODE\nIntegration Engine", 2.9, 2.8, "#F0FDF4", "#16A34A"),
        ("NumPy & Pandas", "Tensor Trajectories &\nData Processing", 5.2, 2.8, "#FEF3C7", "#D97706"),
        ("Streamlit", "Reactive Scientific UI\n& Session State", 7.5, 2.8, "#FEE2E2", "#DC2626"),
        ("Plotly Graph Objects", "Interactive WebGL\nScientific Charts", 1.8, 0.8, "#F3E8FF", "#9333EA"),
        ("ReportLab", "Publication-Grade\nPDF Document Engine", 4.1, 0.8, "#E0F2FE", "#0284C7"),
        ("Pytest & Ruff", "Test Automation (146 Tests)\n& Static Linting", 6.4, 0.8, "#F1F5F9", "#475569"),
    ]

    for name, desc, x, y, bg, border in techs:
        box = patches.FancyBboxPatch(
            (x, y), 1.9, 1.3, boxstyle="round,pad=0.12", facecolor=bg, edgecolor=border, linewidth=1.8
        )
        ax.add_patch(box)
        ax.text(x + 0.95, y + 0.95, name, fontsize=9, fontweight="bold", ha="center", color=border)
        ax.text(x + 0.95, y + 0.45, desc, fontsize=7.5, ha="center", color="#334155", linespacing=1.2)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_05_technology_architecture.png"), dpi=300)
    plt.close()


def fig_06_system_architecture():
    """Figure 6: Modular System Architecture & Pipeline."""
    fig, ax = plt.subplots(figsize=(10, 4.0), dpi=300)
    ax.set_facecolor(COLOR_BG)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.5)
    ax.axis("off")

    ax.text(
        5.0,
        4.1,
        "EPISIM PRO — COMPONENT DATAFLOW & ARCHITECTURE",
        fontsize=11,
        fontweight="bold",
        ha="center",
        color=COLOR_DARK,
    )

    steps = [
        ("1. Presentation\napp.py\n(Streamlit Views)", 0.6, 2.0, "#EFF6FF", "#2563EB"),
        ("2. Validation Guard\nvalidation.py\n(Physical Invariants)", 2.4, 2.0, "#FEE2E2", "#DC2626"),
        ("3. ODE Solver\nsir_model.py\n(SciPy RK45 Solver)", 4.2, 2.0, "#F0FDF4", "#16A34A"),
        ("4. Analysis Core\nanalysis.py\n(Peaks & Velocity)", 6.0, 2.0, "#FEF3C7", "#D97706"),
        ("5. Output Channels\nvisualization.py\n& export.py", 7.8, 2.0, "#F3E8FF", "#9333EA"),
    ]

    for title, x, y, bg, border in steps:
        box = patches.FancyBboxPatch(
            (x, y), 1.6, 1.4, boxstyle="round,pad=0.1", facecolor=bg, edgecolor=border, linewidth=1.8
        )
        ax.add_patch(box)
        ax.text(
            x + 0.8,
            y + 0.7,
            title,
            fontsize=8,
            fontweight="bold",
            ha="center",
            color="#0F172A",
            linespacing=1.3,
        )

    # Connectors
    for x_arr in [2.25, 4.05, 5.85, 7.65]:
        arrow = patches.FancyArrowPatch(
            (x_arr, 2.7),
            (x_arr + 0.12, 2.7),
            arrowstyle="->,head_width=4,head_length=6",
            color=COLOR_MUTED,
            linewidth=2,
        )
        ax.add_patch(arrow)

    # Sub-footer description
    sub_box = patches.FancyBboxPatch(
        (1.0, 0.4),
        8.0,
        0.9,
        boxstyle="round,pad=0.1",
        facecolor="#FFFFFF",
        edgecolor=COLOR_BORDER,
        linewidth=1.2,
    )
    ax.add_patch(sub_box)
    ax.text(
        5.0,
        0.85,
        "STRICT SEPARATION OF CONCERNS: Mathematical model modules have zero Streamlit dependencies.",
        fontsize=8.5,
        fontweight="bold",
        ha="center",
        color="#1E3A8A",
    )

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_06_system_architecture.png"), dpi=300)
    plt.close()


def fig_08_sample_sir_simulation():
    """Figure 8: High-Resolution Sample Simulation Curves (Benchmark Scenario)."""
    from scipy.integrate import solve_ivp

    def derivatives(t, y, beta, gamma, N):
        S, I, R = y
        return [-beta * S * I / N, beta * S * I / N - gamma * I, gamma * I]

    N = 10000.0
    I0 = 10.0
    R0 = 0.0
    S0 = N - I0 - R0
    beta = 0.30
    gamma = 0.10
    T_max = 160.0

    t_eval = np.linspace(0, T_max, 1000)
    sol = solve_ivp(
        derivatives, (0, T_max), [S0, I0, R0], t_eval=t_eval, method="RK45", args=(beta, gamma, N)
    )

    S = sol.y[0]
    I = sol.y[1]
    R = sol.y[2]

    peak_idx = np.argmax(I)
    peak_t = t_eval[peak_idx]
    peak_val = I[peak_idx]

    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=300)
    ax.set_facecolor("#FFFFFF")
    fig.patch.set_facecolor("#FFFFFF")

    ax.plot(t_eval, S, color=COLOR_SUSC, linewidth=2.4, label="Susceptible S(t)")
    ax.plot(t_eval, I, color=COLOR_INF, linewidth=2.8, label="Active Infected I(t)")
    ax.plot(t_eval, R, color=COLOR_REC, linewidth=2.4, label="Recovered R(t)")

    # Peak marker
    ax.scatter([peak_t], [peak_val], color=COLOR_INF, s=60, zorder=5)
    ax.annotate(
        f"Peak Crest: {peak_val:,.0f} cases\nDay {peak_t:.1f} (30.0% of pop)",
        xy=(peak_t, peak_val),
        xytext=(peak_t + 12, peak_val - 250),
        arrowprops=dict(facecolor=COLOR_INF, arrowstyle="->", lw=1.5),
        fontsize=8.5,
        fontweight="bold",
        color=COLOR_INF,
    )

    # Hospital capacity line
    ax.axhline(1500, color="#94A3B8", linestyle="--", linewidth=1.5, label="Hospital Bed Limit (1,500 beds)")

    ax.set_title(
        "Hypothetical Benchmark Simulation: SIR Epidemic Wave (N=10,000, β=0.30, γ=0.10, R₀=3.00)",
        fontsize=11,
        fontweight="bold",
        color=COLOR_DARK,
        pad=12,
    )
    ax.set_xlabel("Simulation Horizon (Days)", fontsize=9.5, color="#334155")
    ax.set_ylabel("Population Count (Individuals)", fontsize=9.5, color="#334155")
    ax.set_ylim(0, N * 1.05)
    ax.set_xlim(0, T_max)
    ax.grid(True, linestyle=":", alpha=0.6, color="#CBD5E1")
    ax.legend(frameon=True, facecolor="#F8FAFC", edgecolor=COLOR_BORDER, fontsize=8.5, loc="center right")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_08_sample_sir_simulation.png"), dpi=300)
    plt.close()


def fig_09_scenario_comparison():
    """Figure 9: Dual Scenario Comparative Epidemic Curve (Flattening the Curve)."""
    from scipy.integrate import solve_ivp

    def derivatives(t, y, beta, gamma, N):
        S, I, R = y
        return [-beta * S * I / N, beta * S * I / N - gamma * I, gamma * I]

    N = 10000.0
    T_max = 160.0
    t_eval = np.linspace(0, T_max, 1000)

    # Scenario A: Baseline unmitigated (beta = 0.30)
    sol_a = solve_ivp(derivatives, (0, T_max), [9990.0, 10.0, 0.0], t_eval=t_eval, args=(0.30, 0.10, N))
    # Scenario B: Flattened intervention (beta = 0.18)
    sol_b = solve_ivp(derivatives, (0, T_max), [9990.0, 10.0, 0.0], t_eval=t_eval, args=(0.18, 0.10, N))

    fig, ax = plt.subplots(figsize=(10, 4.0), dpi=300)
    ax.set_facecolor("#FFFFFF")
    fig.patch.set_facecolor("#FFFFFF")

    ax.plot(
        t_eval, sol_a.y[1], color="#DC2626", linewidth=2.6, label="Scenario A: Baseline (R₀=3.00, Peak 3,005)"
    )
    ax.plot(
        t_eval,
        sol_b.y[1],
        color="#059669",
        linewidth=2.6,
        label="Scenario B: Intervention (R₀=1.80, Peak 1,182)",
    )
    ax.axhline(
        1500, color="#64748B", linestyle="--", linewidth=1.5, label="Hospital Surge Threshold (1,500 beds)"
    )

    # Shading overload
    ax.fill_between(
        t_eval,
        1500,
        sol_a.y[1],
        where=(sol_a.y[1] > 1500),
        color="#FEE2E2",
        alpha=0.6,
        label="Scenario A Hospital Deficit Area",
    )

    ax.set_title(
        "Comparative Scenario Analysis: Non-Pharmaceutical Intervention Impact (Flattening the Curve)",
        fontsize=11,
        fontweight="bold",
        color=COLOR_DARK,
        pad=10,
    )
    ax.set_xlabel("Simulation Days", fontsize=9.5, color="#334155")
    ax.set_ylabel("Active Infected Individuals", fontsize=9.5, color="#334155")
    ax.set_xlim(0, T_max)
    ax.grid(True, linestyle=":", alpha=0.6, color="#CBD5E1")
    ax.legend(frameon=True, facecolor="#F8FAFC", edgecolor=COLOR_BORDER, fontsize=8.5, loc="upper right")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_09_scenario_comparison.png"), dpi=300)
    plt.close()


def fig_10_phase_space_nullcline():
    """Figure 10: Phase Space (S vs I) Orbit and Critical Nullcline."""
    from scipy.integrate import solve_ivp

    def derivatives(t, y, beta, gamma, N):
        S, I, R = y
        return [-beta * S * I / N, beta * S * I / N - gamma * I, gamma * I]

    N = 10000.0
    sol = solve_ivp(
        derivatives, (0, 160), [9990.0, 10.0, 0.0], t_eval=np.linspace(0, 160, 1000), args=(0.30, 0.10, N)
    )
    S = sol.y[0]
    I = sol.y[1]

    s_star = (0.10 / 0.30) * N  # 3,333

    fig, ax = plt.subplots(figsize=(10, 4.0), dpi=300)
    ax.set_facecolor("#FFFFFF")
    fig.patch.set_facecolor("#FFFFFF")

    ax.plot(S, I, color="#4F46E5", linewidth=2.8, label="Dynamical Phase Trajectory (S vs I)")
    ax.axvline(
        s_star,
        color="#DC2626",
        linestyle="--",
        linewidth=1.8,
        label=f"Critical Nullcline S* = N/R₀ = {s_star:,.0f}",
    )

    # Mark start and peak
    ax.scatter([S[0]], [I[0]], color="#2563EB", s=70, zorder=5, label="Initial State (S₀=9,990, I₀=10)")
    peak_idx = np.argmax(I)
    ax.scatter(
        [S[peak_idx]],
        [I[peak_idx]],
        color="#DC2626",
        s=80,
        zorder=5,
        label=f"Epidemic Peak (S={S[peak_idx]:,.0f}, I={I[peak_idx]:,.0f})",
    )

    ax.annotate(
        "Wave Expansion Phase\n(dI/dt > 0 since S > S*)",
        xy=(6500, 1800),
        fontsize=9,
        color="#4338CA",
        fontweight="bold",
    )
    ax.annotate(
        "Burnout Phase\n(dI/dt < 0 since S < S*)",
        xy=(1500, 1200),
        fontsize=9,
        color="#991B1B",
        fontweight="bold",
    )

    ax.set_title(
        "Phase Space Orbit in (S, I) State Space: Demonstration of Threshold Nullcline",
        fontsize=11,
        fontweight="bold",
        color=COLOR_DARK,
        pad=10,
    )
    ax.set_xlabel("Susceptible Population S(t)", fontsize=9.5, color="#334155")
    ax.set_ylabel("Infected Population I(t)", fontsize=9.5, color="#334155")
    ax.grid(True, linestyle=":", alpha=0.6, color="#CBD5E1")
    ax.legend(frameon=True, facecolor="#F8FAFC", edgecolor=COLOR_BORDER, fontsize=8.5, loc="upper left")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_10_phase_space_nullcline.png"), dpi=300)
    plt.close()


def fig_11_parameter_sensitivity():
    """Figure 11: Parameter Sensitivity Heatmap of Peak Infection Volume."""
    beta_vals = np.linspace(0.15, 0.45, 7)
    gamma_vals = np.linspace(0.05, 0.20, 7)
    peak_grid = np.zeros((len(gamma_vals), len(beta_vals)))

    from scipy.integrate import solve_ivp

    def derivatives(t, y, beta, gamma, N):
        return [-beta * y[0] * y[1] / N, beta * y[0] * y[1] / N - gamma * y[1], gamma * y[1]]

    N = 10000.0
    for i, g in enumerate(gamma_vals):
        for j, b in enumerate(beta_vals):
            sol = solve_ivp(
                derivatives, (0, 150), [9990.0, 10.0, 0.0], t_eval=np.linspace(0, 150, 400), args=(b, g, N)
            )
            peak_grid[i, j] = np.max(sol.y[1])

    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=300)
    im = ax.imshow(peak_grid, cmap="YlOrRd", origin="lower", aspect="auto")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Peak Infection Volume (Cases)", fontsize=9, color="#334155")

    ax.set_xticks(np.arange(len(beta_vals)))
    ax.set_xticklabels([f"{b:.2f}" for b in beta_vals], fontsize=8.5)
    ax.set_yticks(np.arange(len(gamma_vals)))
    ax.set_yticklabels([f"{g:.2f}" for g in gamma_vals], fontsize=8.5)

    ax.set_xlabel("Transmission Rate β (Contact Rate per Day)", fontsize=9.5, color="#334155")
    ax.set_ylabel("Recovery Rate γ (Recovery per Day)", fontsize=9.5, color="#334155")
    ax.set_title(
        "Parameter Sensitivity Analysis: Peak Infection Load vs. Contact & Recovery Rates",
        fontsize=11,
        fontweight="bold",
        color=COLOR_DARK,
        pad=12,
    )

    # Loop over data dimensions and create text annotations.
    for i in range(len(gamma_vals)):
        for j in range(len(beta_vals)):
            ax.text(
                j,
                i,
                f"{int(peak_grid[i, j]):,}",
                ha="center",
                va="center",
                color="#0F172A",
                fontsize=7.5,
                fontweight="bold",
            )

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_11_parameter_sensitivity.png"), dpi=300)
    plt.close()


def fig_12_extended_sirv_model():
    """Figure 12: Extended SIRV Compartment Transition Model."""
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=300)
    ax.set_facecolor(COLOR_BG)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")

    # Susceptible
    s_box = patches.FancyBboxPatch(
        (0.6, 2.0), 2.0, 1.4, boxstyle="round,pad=0.2", facecolor="#EFF6FF", edgecolor=COLOR_SUSC, linewidth=2
    )
    ax.add_patch(s_box)
    ax.text(1.6, 2.9, "SUSCEPTIBLE (S)", fontsize=10, fontweight="bold", ha="center", color=COLOR_SUSC)
    ax.text(1.6, 2.3, "dS/dt = -βSI/N - νS", fontsize=8.5, ha="center", color="#1E40AF")

    # Infected
    i_box = patches.FancyBboxPatch(
        (4.0, 2.0), 2.0, 1.4, boxstyle="round,pad=0.2", facecolor="#FEF2F2", edgecolor=COLOR_INF, linewidth=2
    )
    ax.add_patch(i_box)
    ax.text(5.0, 2.9, "INFECTED (I)", fontsize=10, fontweight="bold", ha="center", color=COLOR_INF)
    ax.text(5.0, 2.3, "dI/dt = βSI/N - γI", fontsize=8.5, ha="center", color="#991B1B")

    # Recovered
    r_box = patches.FancyBboxPatch(
        (7.4, 2.0), 2.0, 1.4, boxstyle="round,pad=0.2", facecolor="#ECFDF5", edgecolor=COLOR_REC, linewidth=2
    )
    ax.add_patch(r_box)
    ax.text(8.4, 2.9, "RECOVERED (R)", fontsize=10, fontweight="bold", ha="center", color=COLOR_REC)
    ax.text(8.4, 2.3, "dR/dt = γI", fontsize=8.5, ha="center", color="#065F46")

    # Vaccinated
    v_box = patches.FancyBboxPatch(
        (4.0, 0.4), 2.0, 1.2, boxstyle="round,pad=0.2", facecolor="#F5F3FF", edgecolor="#7C3AED", linewidth=2
    )
    ax.add_patch(v_box)
    ax.text(5.0, 1.15, "VACCINATED (V)", fontsize=10, fontweight="bold", ha="center", color="#7C3AED")
    ax.text(5.0, 0.65, "dV/dt = νS", fontsize=8.5, ha="center", color="#5B21B6")

    # Connectors
    ax.add_patch(
        patches.FancyArrowPatch(
            (2.7, 2.7), (3.9, 2.7), arrowstyle="->,head_width=4,head_length=6", color=COLOR_INF, linewidth=2
        )
    )
    ax.text(3.3, 2.9, "βSI/N", fontsize=8, fontweight="bold", color=COLOR_INF, ha="center")

    ax.add_patch(
        patches.FancyArrowPatch(
            (6.1, 2.7), (7.3, 2.7), arrowstyle="->,head_width=4,head_length=6", color=COLOR_REC, linewidth=2
        )
    )
    ax.text(6.7, 2.9, "γI", fontsize=8, fontweight="bold", color=COLOR_REC, ha="center")

    # Vaccination diagonal arrow S -> V
    ax.add_patch(
        patches.FancyArrowPatch(
            (2.2, 1.9), (3.9, 1.1), arrowstyle="->,head_width=4,head_length=6", color="#7C3AED", linewidth=2
        )
    )
    ax.text(2.6, 1.3, "Vaccination: ν·S", fontsize=8, fontweight="bold", color="#7C3AED", ha="center")

    ax.text(
        5.0,
        0.1,
        "EXTENDED CONSERVATION:  S(t) + I(t) + R(t) + V(t) ≡ N",
        fontsize=9,
        fontweight="bold",
        ha="center",
        color=COLOR_DARK,
    )

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_12_extended_sirv_model.png"), dpi=300)
    plt.close()


def fig_13_testing_workflow():
    """Figure 13: 11-Level Quality Assurance & Testing Architecture."""
    fig, ax = plt.subplots(figsize=(10, 4.0), dpi=300)
    ax.set_facecolor(COLOR_BG)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.5)
    ax.axis("off")

    ax.text(
        5.0,
        4.1,
        "11-TIER COMPREHENSIVE TESTING PYRAMID (146 AUTOMATED TESTS)",
        fontsize=11,
        fontweight="bold",
        ha="center",
        color=COLOR_DARK,
    )

    tiers = [
        ("Level 1-3: Unit & Imports\n(test_startup, test_sir_model)", 1.2, 2.4, 2.2, "#EFF6FF", "#2563EB"),
        (
            "Level 4-5: Integration & Invariants\n(test_simulation, test_analysis)",
            3.9,
            2.4,
            2.2,
            "#F0FDF4",
            "#16A34A",
        ),
        (
            "Level 6-7: UI & Browser Automation\n(Playwright, Chrome DevTools)",
            6.6,
            2.4,
            2.2,
            "#FEF3C7",
            "#D97706",
        ),
        (
            "Level 8-9: Boundaries & Scaling\n(50 Monte Carlo Fuzzing, N=10M)",
            2.5,
            0.8,
            2.4,
            "#FEE2E2",
            "#DC2626",
        ),
        ("Level 10-11: Regression & E2E\n(6 Confirmed Defect Tests)", 5.2, 0.8, 2.4, "#F3E8FF", "#9333EA"),
    ]

    for title, x, y, w, bg, border in tiers:
        box = patches.FancyBboxPatch(
            (x, y), w, 1.2, boxstyle="round,pad=0.1", facecolor=bg, edgecolor=border, linewidth=1.6
        )
        ax.add_patch(box)
        ax.text(
            x + w / 2,
            y + 0.6,
            title,
            fontsize=7.5,
            fontweight="bold",
            ha="center",
            color="#0F172A",
            linespacing=1.3,
        )

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_13_testing_workflow.png"), dpi=300)
    plt.close()


def generate_all():
    print("Generating Figure 1...")
    fig_01_sir_compartment_flow()
    print("Generating Figure 2...")
    fig_02_problem_solution()
    print("Generating Figure 3...")
    fig_03_equation_breakdown()
    print("Generating Figure 4...")
    fig_04_r0_threshold()
    print("Generating Figure 5...")
    fig_05_technology_architecture()
    print("Generating Figure 6...")
    fig_06_system_architecture()
    print("Generating Figure 8...")
    fig_08_sample_sir_simulation()
    print("Generating Figure 9...")
    fig_09_scenario_comparison()
    print("Generating Figure 10...")
    fig_10_phase_space_nullcline()
    print("Generating Figure 11...")
    fig_11_parameter_sensitivity()
    print("Generating Figure 12...")
    fig_12_extended_sirv_model()
    print("Generating Figure 13...")
    fig_13_testing_workflow()
    print("All scientific illustrations successfully generated in:", OUTPUT_DIR)


if __name__ == "__main__":
    generate_all()
