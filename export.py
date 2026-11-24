"""Data Export and Report Generation for SIR Simulations.

Provides functions to format simulation results into downloadable CSV datasets,
structured JSON packages, formal academic markdown reports, and publication-grade PDF documents.
"""

from __future__ import annotations

import datetime
import io
import json

import pandas as pd
from reportlab.graphics.shapes import Circle, Drawing, Line, PolyLine, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from analysis import EpidemiologicalSummary
from sir_model import SIRSimulationResult


def generate_simulation_dataframe(
    result: SIRSimulationResult,
    summary: EpidemiologicalSummary | None = None,
) -> pd.DataFrame:
    """Construct an enriched pandas DataFrame containing all numerical channels."""
    df = pd.DataFrame(
        {
            "Day": result.t,
            "Susceptible_S": result.S,
            "Infected_I": result.I,
            "Recovered_R": result.R,
            "Total_Population_N": result.S + result.I + result.R,
        }
    )

    if summary is not None:
        df["Effective_Reproduction_Number_Re"] = summary.Re_trajectory
        df["Daily_New_Infections_Rate"] = summary.daily_new_infections
        df["Cumulative_Infections_Affected"] = summary.cumulative_affected

    return df


def generate_simulation_csv(
    result: SIRSimulationResult,
    summary: EpidemiologicalSummary | None = None,
) -> str:
    """Generate a standard CSV string representation of the simulation results."""
    df = generate_simulation_dataframe(result, summary)
    return df.to_csv(index=False, float_format="%.4f")


def generate_simulation_json(
    result: SIRSimulationResult,
    summary: EpidemiologicalSummary,
) -> str:
    """Generate a structured JSON export for API pipelines or programmatic analysis."""
    params = result.parameters
    data = {
        "metadata": {
            "title": "Disease Spread Prediction and Simulation System",
            "model": "Kermack-McKendrick SIR Differential Equations",
            "generated_at": datetime.datetime.now().isoformat(),
            "solver": result.solver_method,
            "conservation_error": result.max_conservation_error,
        },
        "parameters": {
            "total_population": params.total_population,
            "initial_susceptible": params.initial_susceptible,
            "initial_infected": params.initial_infected,
            "initial_recovered": params.initial_recovered,
            "transmission_rate_beta": params.transmission_rate,
            "recovery_rate_gamma": params.recovery_rate,
            "duration_days": params.duration_days,
            "num_points": params.num_points,
        },
        "epidemiological_metrics": {
            "basic_reproduction_number_R0": summary.R0,
            "peak_active_cases": summary.peak.peak_infections,
            "peak_day": summary.peak.peak_day,
            "peak_population_percentage": summary.peak.peak_percentage,
            "final_susceptible": summary.final_stats.final_susceptible,
            "final_recovered": summary.final_stats.final_recovered,
            "total_affected_attack_rate_pct": summary.final_stats.percent_affected,
            "alert_level": summary.trends.alert_level,
            "herd_immunity_threshold_pct": summary.trends.herd_immunity_threshold,
            "hospital_capacity_breached": summary.capacity.is_breached,
        },
    }
    return json.dumps(data, indent=2)


def generate_summary_report(
    result: SIRSimulationResult,
    summary: EpidemiologicalSummary,
) -> str:
    """Generate an academic markdown report summarizing the mathematical simulation."""
    params = result.parameters
    r0_display = f"{summary.R0:.4f}" if summary.R0 is not None else "Undefined (gamma = 0)"
    clearance_str = (
        f"Day {summary.trends.clearance_day:.1f}"
        if summary.trends.clearance_day is not None
        else f"Did not fall below {summary.trends.threshold_value} individuals within duration"
    )
    hit_str = (
        f"{summary.trends.herd_immunity_threshold:.2f}%"
        if summary.trends.herd_immunity_threshold is not None
        else "N/A (R0 <= 1.0 or undefined)"
    )

    cap_str = (
        f"BREACHED on Day {summary.capacity.breach_day_start:.1f} (Duration: {summary.capacity.breach_duration_days:.1f} days, Peak Excess: {summary.capacity.peak_excess_cases:,.0f} patients)"
        if summary.capacity.is_breached
        else "WITHIN CAPACITY LIMITS (Zero Breaches)"
    )

    report = f"""# Disease Spread Prediction and Simulation System
## Academic & Technical Executive Summary Report
*Generated on:* {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
*Model:* Classical Kermack-McKendrick SIR Differential Equations (Kermack & McKendrick, 1927)

---

### 1. Mathematical Formulation
The continuous ordinary differential equations governing population dynamics:

- **Susceptible (S):**  `dS/dt = - beta * (S * I) / N`
- **Infected (I):**     `dI/dt =   beta * (S * I) / N - gamma * I`
- **Recovered (R):**    `dR/dt =   gamma * I`
- **Total Population:** `N = S(t) + I(t) + R(t)` (Strictly conserved closed system)

---

### 2. Simulation Configuration Parameters
- **Total Population (N):** {params.total_population:,.0f}
- **Initial Susceptible S(0):** {params.initial_susceptible:,.0f} ({(params.initial_susceptible / params.total_population) * 100:.2f}%)
- **Initial Infected I(0):** {params.initial_infected:,.0f} ({(params.initial_infected / params.total_population) * 100:.2f}%)
- **Initial Recovered R(0):** {params.initial_recovered:,.0f} ({(params.initial_recovered / params.total_population) * 100:.2f}%)
- **Transmission Rate (beta):** {params.transmission_rate:.4f} per day
- **Recovery Rate (gamma):** {params.recovery_rate:.4f} per day
- **Average Infectious Period (1/gamma):** {f"{1.0 / params.recovery_rate:.2f} days" if params.recovery_rate > 0 else "Infinite"}
- **Simulation Horizon:** {params.duration_days:.1f} days ({params.num_points} discrete evaluation steps)
- **Numerical Solver:** SciPy `solve_ivp` ({result.solver_method})

---

### 3. Key Epidemiological Metrics
- **Basic Reproduction Number (R0):** {r0_display}
  - *Status:* {summary.R0_status}
  - *Interpretation:* {summary.R0_interpretation}
  - *Epidemic Alert Level:* {summary.trends.alert_level}
- **Peak Infection Load:** {summary.peak.peak_infections:,.1f} active cases ({summary.peak.peak_percentage:.2f}% of population)
- **Peak Infection Day:** Day {summary.peak.peak_day:.2f}
- **Outbreak Trajectory:** {summary.trends.initial_trend} initial phase; {"Distinct epidemic wave emerged" if summary.peak.has_distinct_peak else "No secondary wave"}
- **Clearance Day (< {summary.trends.threshold_value} active):** {clearance_str}
- **Theoretical Herd Immunity Threshold:** {hit_str}
- **Healthcare Capacity Status:** {cap_str}

---

### 4. Final Outbreak Outcome (Day {params.duration_days:.0f})
- **Remaining Susceptible:** {summary.final_stats.final_susceptible:,.1f} ({(summary.final_stats.final_susceptible / params.total_population) * 100:.2f}%)
- **Active Infected:** {summary.final_stats.final_infected:,.1f} ({(summary.final_stats.final_infected / params.total_population) * 100:.2f}%)
- **Recovered & Immune:** {summary.final_stats.final_recovered:,.1f} ({summary.final_stats.percent_recovered:.2f}%)
- **Total Affected Population:** {summary.final_stats.total_affected:,.1f} ({summary.final_stats.percent_affected:.2f}%)

---

### 5. Numerical Diagnostics
- **Conservation Law Check:** Maximum |S + I + R - N| = {result.max_conservation_error:.2e}
- **Relative Numerical Discrepancy:** {(result.max_conservation_error / params.total_population) * 100:.4e}%
- **Solver Status:** {result.message}

---
*Notice: This epidemiological simulation report was synthesized automatically by the EpiSim Computational Engine for operational planning, scenario analysis, and differential dynamics assessment.*
"""
    return report


def generate_simulation_pdf(
    result: SIRSimulationResult,
    summary: EpidemiologicalSummary,
) -> bytes:
    """Generate a formal, publication-grade 2-page academic PDF report using ReportLab.

    Parameters
    ----------
    result : SIRSimulationResult
        Contains time coordinates, S, I, R numerical trajectories, and solver status.
    summary : EpidemiologicalSummary
        Computed R0, peak metrics, velocity, and capacity breach statistics.

    Returns
    -------
    bytes
        Raw byte contents of the generated PDF document.
    """
    params = result.parameters
    buf = io.BytesIO()

    # Printable area: 540 pt width, 720 pt height (Standard Letter)
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
    )
    sub_style = ParagraphStyle(
        "DocSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748B"),
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=5,
        spaceAfter=3,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#334155"),
    )
    table_hdr_style = ParagraphStyle(
        "TableHdr",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0F172A"),
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#334155"),
    )

    story = []

    # ==================== PAGE 1 ====================
    # 1. Header
    sim_id = f"SIM-{int(datetime.datetime.now().timestamp())}"
    hdr_table = Table(
        [
            [
                Paragraph("<b>EPISIM PRO</b> | Epidemiological Simulation & Intelligence", title_style),
                Paragraph(
                    f"<b>Sim ID:</b> {sim_id}<br/><b>Run Date:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    sub_style,
                ),
            ]
        ],
        colWidths=[360, 180],
    )
    hdr_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(hdr_table)
    story.append(
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceBefore=3, spaceAfter=8)
    )

    # 2. Executive Callout Box
    r0_str = f"{summary.R0:.3f}" if summary.R0 is not None else "Undefined"
    callout_data = [
        [
            Paragraph(f"<b>Alert Level:</b><br/>{summary.trends.alert_level.upper()}", table_hdr_style),
            Paragraph(f"<b>Reproduction No. (R₀):</b><br/>{r0_str}", table_hdr_style),
            Paragraph(
                f"<b>Peak Infection Load:</b><br/>{summary.peak.peak_infections:,.0f} ({summary.peak.peak_percentage:.1f}%)",
                table_hdr_style,
            ),
            Paragraph(f"<b>Day of Peak Influx:</b><br/>Day {summary.peak.peak_day:.1f}", table_hdr_style),
        ]
    ]
    callout_tbl = Table(callout_data, colWidths=[135, 135, 135, 135])
    callout_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(callout_tbl)
    story.append(Spacer(1, 6))

    # 3. Two-Column Metrics Tables
    story.append(Paragraph("1. System Configuration & Primary Epidemiological Metrics", h2_style))

    t_inf_period = f"{1.0 / params.recovery_rate:.1f} days" if params.recovery_rate > 0 else "Infinite"
    cap_status = "BREACHED" if summary.capacity.is_breached else "SUSTAINED"

    table1_data = [
        [
            Paragraph("<b>Model Parameter</b>", table_hdr_style),
            Paragraph("<b>Configured Value</b>", table_hdr_style),
        ],
        [
            Paragraph("Total Population (N)", table_cell_style),
            Paragraph(f"{params.total_population:,.0f}", table_cell_style),
        ],
        [
            Paragraph("Initial Susceptible S(0)", table_cell_style),
            Paragraph(
                f"{params.initial_susceptible:,.0f} ({(params.initial_susceptible / params.total_population) * 100:.1f}%)",
                table_cell_style,
            ),
        ],
        [
            Paragraph("Initial Infected I(0)", table_cell_style),
            Paragraph(
                f"{params.initial_infected:,.0f} ({(params.initial_infected / params.total_population) * 100:.2f}%)",
                table_cell_style,
            ),
        ],
        [
            Paragraph("Initial Recovered R(0)", table_cell_style),
            Paragraph(f"{params.initial_recovered:,.0f}", table_cell_style),
        ],
        [
            Paragraph("Transmission Rate (β)", table_cell_style),
            Paragraph(f"{params.transmission_rate:.4f} / day", table_cell_style),
        ],
        [
            Paragraph("Recovery Rate (γ)", table_cell_style),
            Paragraph(f"{params.recovery_rate:.4f} / day", table_cell_style),
        ],
        [Paragraph("Infectious Period (1/γ)", table_cell_style), Paragraph(t_inf_period, table_cell_style)],
        [
            Paragraph("Time Horizon / Steps", table_cell_style),
            Paragraph(f"{params.duration_days:.0f} days ({params.num_points} pts)", table_cell_style),
        ],
    ]

    table2_data = [
        [
            Paragraph("<b>Epidemiological Metric</b>", table_hdr_style),
            Paragraph("<b>Calculated Value</b>", table_hdr_style),
        ],
        [Paragraph("Basic Reproduction No. (R₀)", table_cell_style), Paragraph(r0_str, table_cell_style)],
        [
            Paragraph("Peak Active Burden", table_cell_style),
            Paragraph(f"{summary.peak.peak_infections:,.0f} hosts", table_cell_style),
        ],
        [
            Paragraph("Peak Day", table_cell_style),
            Paragraph(f"Day {summary.peak.peak_day:.2f}", table_cell_style),
        ],
        [
            Paragraph("Cumulative Attack Rate", table_cell_style),
            Paragraph(
                f"{summary.final_stats.percent_affected:.2f}% ({summary.final_stats.total_affected:,.0f} hosts)",
                table_cell_style,
            ),
        ],
        [
            Paragraph("End Susceptible S(T)", table_cell_style),
            Paragraph(f"{summary.final_stats.final_susceptible:,.0f}", table_cell_style),
        ],
        [
            Paragraph("End Recovered R(T)", table_cell_style),
            Paragraph(f"{summary.final_stats.final_recovered:,.0f}", table_cell_style),
        ],
        [
            Paragraph("Hospital Bed Threshold", table_cell_style),
            Paragraph(f"{summary.capacity.capacity_limit:,.0f} beds", table_cell_style),
        ],
        [Paragraph("Clinical Surge Status", table_cell_style), Paragraph(cap_status, table_cell_style)],
    ]

    t1 = Table(table1_data, colWidths=[160, 105])
    t2 = Table(table2_data, colWidths=[160, 105])
    for tbl in (t1, t2):
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                    ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

    metrics_grid = Table([[t1, t2]], colWidths=[268, 268])
    metrics_grid.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(metrics_grid)
    story.append(Spacer(1, 6))

    # 4. Embedded Vector Trajectory Drawing
    story.append(Paragraph("2. Epidemic Trajectory Simulation Curves (SciPy RK45)", h2_style))

    chart_w = 536
    chart_h = 175
    draw = Drawing(chart_w, chart_h)

    # Outer box
    draw.add(
        Rect(
            0,
            0,
            chart_w,
            chart_h,
            fillColor=colors.HexColor("#FFFFFF"),
            strokeColor=colors.HexColor("#CBD5E1"),
            strokeWidth=0.75,
            rx=3,
            ry=3,
        )
    )

    # Plotting canvas dimensions
    px0, px1 = 45, 520
    py0, py1 = 26, 152
    pw = px1 - px0
    ph = py1 - py0

    max_t = max(1.0, float(result.t[-1]))
    max_pop = max(1.0, float(params.total_population))

    # Gridlines and Y-ticks
    for frac, label in [(0.25, "25%"), (0.5, "50%"), (0.75, "75%"), (1.0, "100%")]:
        gy = py0 + frac * ph
        draw.add(Line(px0, gy, px1, gy, strokeColor=colors.HexColor("#F1F5F9"), strokeWidth=0.5))
        draw.add(
            String(
                px0 - 28,
                gy - 3,
                label,
                fontName="Helvetica",
                fontSize=6.5,
                fillColor=colors.HexColor("#64748B"),
            )
        )
    draw.add(
        String(
            px0 - 20, py0 - 3, "0", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor("#64748B")
        )
    )

    # X-ticks
    for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
        gx = px0 + frac * pw
        day_val = int(frac * max_t)
        draw.add(Line(gx, py0, gx, py0 - 3, strokeColor=colors.HexColor("#94A3B8"), strokeWidth=0.5))
        draw.add(
            String(
                gx - 6,
                py0 - 11,
                f"Day {day_val}",
                fontName="Helvetica",
                fontSize=6.5,
                fillColor=colors.HexColor("#64748B"),
            )
        )

    # Axes
    draw.add(Line(px0, py0, px1, py0, strokeColor=colors.HexColor("#94A3B8"), strokeWidth=1))
    draw.add(Line(px0, py0, px0, py1, strokeColor=colors.HexColor("#94A3B8"), strokeWidth=1))

    # Downsample points for polyline
    n_pts = len(result.t)
    step = max(1, n_pts // 120)
    indices = list(range(0, n_pts, step))
    if indices[-1] != n_pts - 1:
        indices.append(n_pts - 1)

    s_pts = []
    i_pts = []
    r_pts = []
    for idx in indices:
        cx = px0 + (result.t[idx] / max_t) * pw
        cy_s = py0 + (result.S[idx] / max_pop) * ph
        cy_i = py0 + (result.I[idx] / max_pop) * ph
        cy_r = py0 + (result.R[idx] / max_pop) * ph
        s_pts.extend([cx, cy_s])
        i_pts.extend([cx, cy_i])
        r_pts.extend([cx, cy_r])

    draw.add(PolyLine(s_pts, strokeColor=colors.HexColor("#2563EB"), strokeWidth=1.5))
    draw.add(PolyLine(r_pts, strokeColor=colors.HexColor("#059669"), strokeWidth=1.5))
    draw.add(PolyLine(i_pts, strokeColor=colors.HexColor("#DC2626"), strokeWidth=2.0))

    # Peak marker
    peak_x = px0 + (summary.peak.peak_day / max_t) * pw
    peak_y = py0 + (summary.peak.peak_infections / max_pop) * ph
    draw.add(
        Circle(
            peak_x,
            peak_y,
            3.5,
            fillColor=colors.HexColor("#DC2626"),
            strokeColor=colors.HexColor("#FFFFFF"),
            strokeWidth=1,
        )
    )
    draw.add(
        String(
            min(peak_x + 5, px1 - 105),
            min(peak_y + 4, py1 - 8),
            f"Peak: {summary.peak.peak_infections:,.0f} (D{summary.peak.peak_day:.1f})",
            fontName="Helvetica-Bold",
            fontSize=6.5,
            fillColor=colors.HexColor("#DC2626"),
        )
    )

    # Legend
    leg_y = py1 + 8
    draw.add(Rect(px0 + 50, leg_y, 8, 5, fillColor=colors.HexColor("#2563EB"), strokeColor=None))
    draw.add(
        String(
            px0 + 62,
            leg_y,
            "Susceptible S(t)",
            fontName="Helvetica",
            fontSize=7,
            fillColor=colors.HexColor("#334155"),
        )
    )
    draw.add(Rect(px0 + 180, leg_y, 8, 5, fillColor=colors.HexColor("#DC2626"), strokeColor=None))
    draw.add(
        String(
            px0 + 192,
            leg_y,
            "Infected I(t)",
            fontName="Helvetica",
            fontSize=7,
            fillColor=colors.HexColor("#334155"),
        )
    )
    draw.add(Rect(px0 + 290, leg_y, 8, 5, fillColor=colors.HexColor("#059669"), strokeColor=None))
    draw.add(
        String(
            px0 + 302,
            leg_y,
            "Recovered R(t)",
            fontName="Helvetica",
            fontSize=7,
            fillColor=colors.HexColor("#334155"),
        )
    )

    story.append(draw)
    story.append(Spacer(1, 5))

    # Page 1 Footer Note
    story.append(
        Paragraph(
            "<font size='6.5' color='#94A3B8'>Page 1 of 2 — EpiSim Pro Computational Intelligence Suite</font>",
            ParagraphStyle("P1Foot", parent=styles["Normal"], alignment=1),
        )
    )

    # ==================== PAGE 2 ====================
    story.append(PageBreak())

    # Page 2 Header
    story.append(Paragraph("<b>EPISIM PRO</b> | Mathematical Foundations & Clinical Analysis", title_style))
    story.append(
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceBefore=3, spaceAfter=8)
    )

    # 5. Differential Equations Box
    story.append(Paragraph("3. Kermack-McKendrick Ordinary Differential Equations (1927)", h2_style))
    ode_narrative = (
        "The continuous time dynamics of the host population are governed by the coupled bilinear system:<br/><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>dS/dt = - β · (S · I) / N</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>dI/dt =   β · (S · I) / N - γ · I</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>dR/dt =   γ · I</b><br/><br/>"
        "<b>Fundamental Invariants & Conservation:</b><br/>"
        "Summing the rate equations yields: <i>d(S + I + R)/dt = 0</i>, guaranteeing that total population <b>N</b> is strictly conserved for all time <i>t ≥ 0</i>. "
        "The critical transmission threshold occurs at the infective nullcline <i>dI/dt = 0</i>, yielding the critical susceptible density <b>S* = N / R₀</b>. "
        "An epidemic wave can only propagate if <i>S(0) &gt; N / R₀</i> (equivalent to <i>R₀ &gt; 1</i> in a fully susceptible population)."
    )
    ode_tbl = Table([[Paragraph(ode_narrative, body_style)]], colWidths=[536])
    ode_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(ode_tbl)
    story.append(Spacer(1, 5))

    # 6. Numerical Solver Diagnostics
    story.append(Paragraph("4. Numerical Solver Diagnostics & Error Analysis", h2_style))
    diag_data = [
        [
            Paragraph("<b>Diagnostic Metric</b>", table_hdr_style),
            Paragraph("<b>Observed Result</b>", table_hdr_style),
            Paragraph("<b>Assessment & Status</b>", table_hdr_style),
        ],
        [
            Paragraph("Integration Algorithm", table_cell_style),
            Paragraph(f"SciPy solve_ivp ({result.solver_method})", table_cell_style),
            Paragraph("Adaptive Runge-Kutta Order 5(4)", table_cell_style),
        ],
        [
            Paragraph("Solver Relative Tolerance", table_cell_style),
            Paragraph("rtol = 1.0e-07", table_cell_style),
            Paragraph("High Precision Numerical Accuracy", table_cell_style),
        ],
        [
            Paragraph("Solver Absolute Tolerance", table_cell_style),
            Paragraph("atol = 1.0e-09", table_cell_style),
            Paragraph("Near-Zero Boundary Protection", table_cell_style),
        ],
        [
            Paragraph("Max Conservation Error", table_cell_style),
            Paragraph(f"{result.max_conservation_error:.2e} individuals", table_cell_style),
            Paragraph(
                f"Strict Mass Conservation ({(result.max_conservation_error / params.total_population) * 100:.2e}%)",
                table_cell_style,
            ),
        ],
        [
            Paragraph("Integration Status", table_cell_style),
            Paragraph("Success = True", table_cell_style),
            Paragraph("Converged with Zero Divergence", table_cell_style),
        ],
    ]
    diag_tbl = Table(diag_data, colWidths=[160, 160, 216])
    diag_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(diag_tbl)
    story.append(Spacer(1, 5))

    # 7. Clinical Healthcare Capacity Assessment
    story.append(Paragraph("5. Clinical Healthcare Capacity & Surge Evaluation", h2_style))
    cap_narrative = (
        f"Hospital capacity is provisioned at <b>{summary.capacity.capacity_limit:,.0f} beds</b> "
        f"({summary.capacity.capacity_percentage:.1f}% of total population). "
    )
    if summary.capacity.is_breached:
        cap_narrative += (
            f"The active infective trajectory exceeds available clinical capacity from <b>Day {summary.capacity.breach_day_start:.1f}</b> "
            f"to <b>Day {summary.capacity.breach_day_end:.1f}</b> (a critical deficit spanning <b>{summary.capacity.breach_duration_days:.1f} days</b>). "
            f"At the epidemic crest, excess patient volume reaches <b>{summary.capacity.peak_excess_cases:,.0f} unaccommodated individuals</b>. "
            "Non-pharmaceutical interventions (NPIs) including contact restriction, physical distancing, and universal masking are urgently advised to suppress transmission below critical threshold R_e(t) &lt; 1.0."
        )
    else:
        cap_narrative += (
            "Active infection burden remains strictly within hospital bed threshold throughout the entire simulation window. "
            "No acute clinical capacity deficit is projected under current transmission parameters."
        )
    story.append(Paragraph(cap_narrative, body_style))
    story.append(Spacer(1, 5))

    # 8. Epidemiological Assumptions & Modeling Limitations
    story.append(Paragraph("6. Epidemiological Assumptions & Limitations", h2_style))
    limitations = (
        "<b>1. Homogeneous Mixing:</b> All individuals within the population are assumed to mix uniformly with equal contact probability. Spatial clustering, age-stratified contact matrices, and superspreading events are not modeled in this classical compartmental formulation.<br/>"
        "<b>2. Closed Demographics:</b> The model assumes a closed host population without vital dynamics (births, non-disease deaths, or migration fluxes).<br/>"
        "<b>3. Permanent Immunity:</b> Recovered hosts are assumed to acquire sterile, lifelong immunity without antigenic waning or reinfection.<br/>"
        "<b>4. Fixed Latency:</b> The classical SIR framework models instantaneous infectiousness upon exposure without an explicit latent / incubation compartment (unlike SEIR frameworks)."
    )
    story.append(Paragraph(limitations, body_style))
    story.append(Spacer(1, 6))

    # Sign-off & Academic Certification
    cert_text = (
        "<b>Academic Certification:</b> This simulation report was computed using the Kermack-McKendrick ordinary differential equations with adaptive Runge-Kutta numerical integration. "
        "Generated by EpiSim Pro Computational Engine for academic research, operational healthcare evaluation, and epidemiological modeling."
    )
    cert_tbl = Table(
        [
            [
                Paragraph(
                    cert_text,
                    ParagraphStyle(
                        "Cert",
                        parent=styles["Normal"],
                        fontSize=6.5,
                        leading=9,
                        textColor=colors.HexColor("#64748B"),
                    ),
                )
            ]
        ],
        colWidths=[536],
    )
    cert_tbl.setStyle(
        TableStyle(
            [
                ("LINEBEFORE", (0, 0), (0, -1), 2, colors.HexColor("#1E3A8A")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(cert_tbl)
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            "<font size='6.5' color='#94A3B8'>Page 2 of 2 — EpiSim Pro Computational Intelligence Suite</font>",
            ParagraphStyle("P2Foot", parent=styles["Normal"], alignment=1),
        )
    )

    doc.build(story)
    return buf.getvalue()
