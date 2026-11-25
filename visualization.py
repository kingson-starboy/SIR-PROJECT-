"""Interactive Plotly Visualizations for the SIR Epidemic Simulation System.

Generates publication-quality, interactive epidemiological charts with clean
scientific styling, explicit hover tooltips, and distinct color schemes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from analysis import EpidemiologicalSummary, SensitivityItem
from sir_model import SIRSimulationResult

# Scientific Design System Color Palette (WCAG 2.2 AA Conforming)
COLOR_SUSCEPTIBLE = "#3478D4"  # Scientific Cerulean Blue
COLOR_INFECTED = "#E45454"  # Coral Red
COLOR_RECOVERED = "#20A477"  # Jade Emerald Green
COLOR_PRIMARY_ACCENT = "#315EF7"  # Deep Royal Indigo
COLOR_WARNING = "#D99A35"  # Amber Warning
COLOR_MUTED_GRAY = "#687386"  # Slate Secondary Text
COLOR_GRID = "#E5E8EF"  # Soft Grid Line
COLOR_SURFACE = "#FFFFFF"  # Pure White Card Surface
COLOR_BACKGROUND = "#F7F8FA"  # Canvas Neutral Tint
COLOR_ACCENT_PURPLE = "#7C3AED"  # Analytical Violet


# Compartment-specific comparison chart (S, I, or R) for two scenarios
def create_compartment_comparison_chart(
    r_a: SIRSimulationResult, r_b: SIRSimulationResult, compartment: str
) -> go.Figure:
    """Return a Plotly figure comparing a single compartment between two scenarios.

    * ``compartment`` must be one of ``"S"``, ``"I"`` or ``"R"``.
    The function uses the same colour palette as the full SIR curve chart.
    """
    comp_map = {
        "S": (r_a.S, r_b.S, COLOR_SUSCEPTIBLE, "Susceptible"),
        "I": (r_a.I, r_b.I, COLOR_INFECTED, "Infected"),
        "R": (r_a.R, r_b.R, COLOR_RECOVERED, "Recovered"),
    }
    if compartment not in comp_map:
        raise ValueError("compartment must be one of 'S', 'I', 'R'")
    a_vals, b_vals, color, label = comp_map[compartment]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=r_a.t,
            y=a_vals,
            name="Scenario A (Baseline)",
            mode="lines",
            line=dict(color=color, width=2.8),
            hovertemplate=f"<b>Scenario A {label}:</b> %{{y:,.0f}}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=r_b.t,
            y=b_vals,
            name="Scenario B (Intervention)",
            mode="lines",
            line=dict(color=color, width=2.8, dash="dash"),
            hovertemplate=f"<b>Scenario B {label}:</b> %{{y:,.0f}}<extra></extra>",
        )
    )
    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(
            text=f"<b>{label} Compartment</b>",
            font=dict(size=14, color="#0F172A"),
            x=0.01,
            y=1.0,
            yref="paper",
            yanchor="bottom",
            pad=dict(b=18),
        ),
        xaxis_title="Time (Days)",
        yaxis_title=f"{label} Count",
        showlegend=True,
    )
    return fig


def get_chart_layout(is_dark: bool = False) -> dict:
    """Return layout dictionary customized for Light or Dark theme."""
    if is_dark:
        bg = "#111827"
        plot_bg = "#0F172A"
        text_color = "#F8FAFC"
        grid_color = "#1E293B"
        zero_color = "#334155"
        legend_bg = "rgba(17, 24, 39, 0.95)"
        legend_border = "#334155"
        legend_text = "#E2E8F0"
        sub_text = "#94A3B8"
    else:
        bg = "#FFFFFF"
        plot_bg = "#FFFFFF"
        text_color = "#0F172A"
        grid_color = "#E5E8EF"
        zero_color = "#CBD5E1"
        legend_bg = "rgba(255, 255, 255, 0.95)"
        legend_border = "#E2E8F0"
        legend_text = "#334155"
        sub_text = "#64748B"

    return dict(
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
            size=12,
            color=text_color,
        ),
        paper_bgcolor=bg,
        plot_bgcolor=plot_bg,
        hovermode="x unified",
        margin=dict(l=60, r=30, t=110, b=95),
        modebar=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,
            bgcolor=legend_bg,
            bordercolor=legend_border,
            borderwidth=1,
            font=dict(size=11, color=legend_text),
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            gridwidth=1,
            zeroline=True,
            zerolinecolor=zero_color,
            linecolor=zero_color,
            tickfont=dict(size=11, color=sub_text),
            title_font=dict(size=12, color=text_color),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            gridwidth=1,
            zeroline=True,
            zerolinecolor=zero_color,
            linecolor=zero_color,
            tickfont=dict(size=11, color=sub_text),
            title_font=dict(size=12, color=text_color),
        ),
    )


CHART_LAYOUT_DEFAULTS = get_chart_layout(is_dark=False)


def apply_theme_to_figure(fig: go.Figure, is_dark: bool = False) -> go.Figure:
    """Dynamically applies Light or Dark theme styling to a Plotly Figure."""
    fig.update_layout(
        modebar=dict(
            bgcolor="rgba(0,0,0,0)",
            color="#94A3B8" if is_dark else "#475569",
            activecolor="#38BDF8" if is_dark else "#2563EB",
        )
    )
    if is_dark:
        layout = get_chart_layout(is_dark=True)
        fig.update_layout(
            paper_bgcolor=layout["paper_bgcolor"],
            plot_bgcolor=layout["plot_bgcolor"],
            font=layout["font"],
            legend=layout["legend"],
            xaxis=dict(
                gridcolor=layout["xaxis"]["gridcolor"],
                zerolinecolor=layout["xaxis"]["zerolinecolor"],
                linecolor=layout["xaxis"]["linecolor"],
                tickfont=layout["xaxis"]["tickfont"],
                title_font=layout["xaxis"]["title_font"],
            ),
            yaxis=dict(
                gridcolor=layout["yaxis"]["gridcolor"],
                zerolinecolor=layout["yaxis"]["zerolinecolor"],
                linecolor=layout["yaxis"]["linecolor"],
                tickfont=layout["yaxis"]["tickfont"],
                title_font=layout["yaxis"]["title_font"],
            ),
        )
        if fig.layout.title.text:
            fig.update_layout(title_font_color="#F8FAFC")
    return fig


def create_sir_curve_chart(result: SIRSimulationResult) -> go.Figure:
    """Chart 1: Interactive SIR Population Curves over Time."""
    fig = go.Figure()

    # Susceptible trace
    fig.add_trace(
        go.Scatter(
            x=result.t,
            y=result.S,
            name="Susceptible S(t)",
            mode="lines",
            line=dict(color=COLOR_SUSCEPTIBLE, width=2.8),
            hovertemplate="<b>Susceptible:</b> %{y:,.0f} individuals<extra></extra>",
        )
    )

    # Infected trace with subtle soft glow fill
    fig.add_trace(
        go.Scatter(
            x=result.t,
            y=result.I,
            name="Infected I(t)",
            mode="lines",
            line=dict(color=COLOR_INFECTED, width=3.2),
            fill="tozeroy",
            fillcolor="rgba(220, 38, 38, 0.07)",
            hovertemplate="<b>Infected:</b> %{y:,.0f} active cases<extra></extra>",
        )
    )

    # Recovered trace
    fig.add_trace(
        go.Scatter(
            x=result.t,
            y=result.R,
            name="Recovered R(t)",
            mode="lines",
            line=dict(color=COLOR_RECOVERED, width=2.8),
            hovertemplate="<b>Recovered:</b> %{y:,.0f} individuals<extra></extra>",
        )
    )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(
            text="<b>SIR Compartmental Population Trajectory</b>",
            font=dict(size=15, color="#0F172A"),
            x=0.01,
            y=1.0,
            yref="paper",
            yanchor="bottom",
            pad=dict(b=18),
        ),
        xaxis_title="Simulation Time (Days)",
        yaxis_title="Population Count (Individuals)",
    )
    return fig


def create_peak_analysis_chart(
    result: SIRSimulationResult,
    summary: EpidemiologicalSummary,
    show_capacity: bool = True,
) -> go.Figure:
    """Chart 2: Detailed Infection Peak, Active Cases, and Hospital Capacity Limits."""
    fig = go.Figure()

    # Infected curve with gradient fill
    fig.add_trace(
        go.Scatter(
            x=result.t,
            y=result.I,
            name="Active Infections I(t)",
            mode="lines",
            line=dict(color=COLOR_INFECTED, width=3.0),
            fill="tozeroy",
            fillcolor="rgba(220, 38, 38, 0.12)",
            hovertemplate="<b>Active Cases:</b> %{y:,.0f} individuals<extra></extra>",
        )
    )

    peak = summary.peak
    # Highlight peak coordinate with halo marker
    fig.add_trace(
        go.Scatter(
            x=[peak.peak_day],
            y=[peak.peak_infections],
            mode="markers+text",
            name="Infection Peak",
            marker=dict(
                size=12,
                color="#DC2626",
                symbol="diamond",
                line=dict(width=2.5, color="#FFFFFF"),
            ),
            text=[f"  Peak: {peak.peak_infections:,.0f} cases (Day {peak.peak_day:.1f})"],
            textposition="top right",
            textfont=dict(size=11, color="#991B1B", family="sans-serif"),
            hoverinfo="skip",
        )
    )

    # Vertical reference line at peak day
    fig.add_vline(
        x=peak.peak_day,
        line_width=1.5,
        line_dash="dash",
        line_color="#DC2626",
        opacity=0.8,
    )

    # Healthcare capacity threshold overlay
    if show_capacity and summary.capacity is not None:
        cap_val = summary.capacity.capacity_limit
        fig.add_hline(
            y=cap_val,
            line_width=2.0,
            line_dash="dashdot",
            line_color="#475569",
            annotation_text=f"Hospital Capacity ({cap_val:,.0f} beds / {summary.capacity.capacity_percentage:.0f}%)",
            annotation_position="top left",
            annotation_font=dict(size=10, color="#334155"),
        )

        # Highlight breach duration if capacity is overwhelmed
        if summary.capacity.is_breached and summary.capacity.breach_day_start is not None:
            fig.add_vrect(
                x0=summary.capacity.breach_day_start,
                x1=summary.capacity.breach_day_end,
                fillcolor="rgba(239, 68, 68, 0.08)",
                line_width=0,
                annotation_text="Capacity Overwhelmed",
                annotation_position="top left",
                annotation_font=dict(size=10, color="#991B1B"),
            )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(
            text=f"<b>Infection Peak Dynamics</b> — Maximum: {peak.peak_infections:,.0f} ({peak.peak_percentage:.1f}%) on Day {peak.peak_day:.1f}",
            font=dict(size=15, color="#0F172A"),
            x=0.01,
            y=1.0,
            yref="paper",
            yanchor="bottom",
            pad=dict(b=18),
        ),
        xaxis_title="Simulation Time (Days)",
        yaxis_title="Active Infected Individuals",
        showlegend=False,
    )
    return fig


def create_population_distribution_chart(
    summary: EpidemiologicalSummary, total_population: float
) -> go.Figure:
    """Chart 3: Final Population Distribution Donut Chart."""
    labels = ["Remaining Susceptible", "Active Infected", "Recovered & Immune"]
    values = [
        summary.final_stats.final_susceptible,
        summary.final_stats.final_infected,
        summary.final_stats.final_recovered,
    ]
    colors = [COLOR_SUSCEPTIBLE, COLOR_INFECTED, COLOR_RECOVERED]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.62,
                marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2.5)),
                textinfo="percent+label",
                textposition="outside",
                hovertemplate="<b>%{label}</b><br>Count: %{value:,.0f} individuals<br>Proportion: %{percent}<extra></extra>",
                direction="clockwise",
                sort=False,
            )
        ]
    )

    fig.update_layout(
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
            size=12,
            color="#1E293B",
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=30, r=30, t=105, b=30),
        title=dict(
            text="<b>Final Outbreak Population Distribution</b>",
            font=dict(size=15, color="#0F172A"),
            x=0.01,
            y=1.0,
            yref="paper",
            yanchor="bottom",
            pad=dict(b=18),
        ),
        annotations=[
            dict(
                text=f"<span style='font-size:11px;color:#64748B;'>TOTAL POPULATION</span><br><b>{total_population:,.0f}</b>",
                x=0.5,
                y=0.5,
                font=dict(size=14, color="#0F172A"),
                showarrow=False,
            )
        ],
        showlegend=False,
    )
    return fig


def create_animated_progression_chart(result: SIRSimulationResult) -> go.Figure:
    """Chart 3B: Animated Disease Progression Timeline with Interactive Scrubber.

    Renders dynamic population state transitions (S, I, R) across discrete time steps
    with play, pause, and scrubber controls derived strictly from numerical ODE integration.
    """
    t = result.t
    S = result.S
    I = result.I
    R = result.R
    N = result.N

    n_steps = min(40, len(t))
    indices = np.linspace(0, len(t) - 1, n_steps, dtype=int)

    frames = []
    for idx in indices:
        cur_day = t[idx]
        cur_s = S[idx]
        cur_i = I[idx]
        cur_r = R[idx]
        s_pct = (cur_s / N) * 100
        i_pct = (cur_i / N) * 100
        r_pct = (cur_r / N) * 100

        frames.append(
            go.Frame(
                data=[
                    go.Bar(
                        x=["Susceptible S(t)", "Active Infected I(t)", "Recovered R(t)"],
                        y=[cur_s, cur_i, cur_r],
                        marker_color=[COLOR_SUSCEPTIBLE, COLOR_INFECTED, COLOR_RECOVERED],
                        text=[
                            f"{cur_s:,.0f} ({s_pct:.1f}%)",
                            f"{cur_i:,.0f} ({i_pct:.1f}%)",
                            f"{cur_r:,.0f} ({r_pct:.1f}%)",
                        ],
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate="<b>%{x}</b><br>Count: %{y:,.0f}<br>Proportion: %{text}<extra></extra>",
                    )
                ],
                name=f"Day {cur_day:.1f}",
            )
        )

    # Initial frame (t=0)
    init_s, init_i, init_r = S[0], I[0], R[0]
    fig = go.Figure(
        data=[
            go.Bar(
                x=["Susceptible S(t)", "Active Infected I(t)", "Recovered R(t)"],
                y=[init_s, init_i, init_r],
                marker_color=[COLOR_SUSCEPTIBLE, COLOR_INFECTED, COLOR_RECOVERED],
                text=[
                    f"{init_s:,.0f} ({(init_s / N) * 100:.1f}%)",
                    f"{init_i:,.0f} ({(init_i / N) * 100:.1f}%)",
                    f"{init_r:,.0f} ({(init_r / N) * 100:.1f}%)",
                ],
                textposition="outside",
                cliponaxis=False,
            )
        ],
        frames=frames,
    )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(
            text="Dynamic Disease Progression (Interactive Timeline Scrubber)",
            font=dict(size=15, color="#0F172A"),
            x=0.01,
            y=1.0,
            yref="paper",
            yanchor="bottom",
            pad=dict(b=18),
        ),
        xaxis_title="Epidemiological Compartment",
        yaxis_title="Population Headcount",
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                y=1.14,
                x=0.01,
                xanchor="left",
                yanchor="top",
                direction="left",
                buttons=[
                    dict(
                        label="▶ Play Timeline",
                        method="animate",
                        args=[
                            None,
                            dict(
                                frame=dict(duration=160, redraw=True),
                                fromcurrent=True,
                                mode="immediate",
                            ),
                        ],
                    ),
                    dict(
                        label="⏸ Pause",
                        method="animate",
                        args=[
                            [None],
                            dict(
                                frame=dict(duration=0, redraw=False),
                                mode="immediate",
                            ),
                        ],
                    ),
                ],
            )
        ],
        sliders=[
            dict(
                active=0,
                steps=[
                    dict(
                        method="animate",
                        args=[
                            [f"Day {t[i]:.1f}"],
                            dict(mode="immediate", frame=dict(duration=0, redraw=True)),
                        ],
                        label=f"D{t[i]:.0f}",
                    )
                    for i in indices
                ],
                currentvalue=dict(
                    prefix="Simulation Progression: ",
                    visible=True,
                    xanchor="center",
                    font=dict(size=12, color="#1E3A8A"),
                ),
                pad=dict(t=35, b=10),
                len=0.95,
                x=0.025,
            )
        ],
    )
    fig.update_yaxes(range=[0, N * 1.15])
    return fig


def create_infection_rate_trend_chart(result: SIRSimulationResult) -> go.Figure:
    """Chart 4: Rate of Change of Infected Population (dI/dt) over Time."""
    beta = result.parameters.transmission_rate
    gamma = result.parameters.recovery_rate
    N = result.N
    didt = (beta * result.S * result.I / N) - (gamma * result.I)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=result.t,
            y=didt,
            name="Net Rate of Change (dI/dt)",
            mode="lines",
            line=dict(color=COLOR_ACCENT_PURPLE, width=2.8),
            hovertemplate="<b>dI/dt:</b> %{y:+,.1f} cases/day<extra></extra>",
        )
    )

    # Zero equilibrium line
    fig.add_hline(
        y=0.0,
        line_width=1.5,
        line_dash="dash",
        line_color="#475569",
        annotation_text="Equilibrium (dI/dt = 0)",
        annotation_position="bottom right",
        annotation_font=dict(size=11, color="#475569"),
    )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(
            text="<b>Infection Growth Rate Trend (dI/dt)</b>",
            font=dict(size=15, color="#0F172A"),
            x=0.01,
            y=1.0,
            yref="paper",
            yanchor="bottom",
            pad=dict(b=18),
        ),
        xaxis_title="Simulation Time (Days)",
        yaxis_title="Net Case Change per Day (dI/dt)",
        showlegend=False,
    )
    return fig


def create_effective_r_chart(result: SIRSimulationResult, summary: EpidemiologicalSummary) -> go.Figure:
    """Chart 5: Effective Reproduction Number Re(t) with Epidemic Threshold."""
    fig = go.Figure()

    if np.all(np.isnan(summary.Re_trajectory)):
        fig.add_annotation(
            text="Effective Reproduction Number Re(t) is undefined when recovery rate gamma = 0",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=13, color="#DC2626"),
        )
    else:
        max_re = float(np.nanmax(summary.Re_trajectory)) if len(summary.Re_trajectory) > 0 else 2.0
        upper_bound = max(max_re * 1.05, 1.5)

        fig.add_hrect(
            y0=1.0,
            y1=upper_bound,
            fillcolor="rgba(239, 68, 68, 0.05)",
            line_width=0,
            annotation_text="Epidemic Growth Zone (Re > 1.0)",
            annotation_position="top left",
            annotation_font=dict(size=10, color="#B91C1C"),
        )
        fig.add_hrect(
            y0=0.0,
            y1=1.0,
            fillcolor="rgba(16, 185, 129, 0.05)",
            line_width=0,
            annotation_text="Containment Zone (Re < 1.0)",
            annotation_position="bottom left",
            annotation_font=dict(size=10, color="#047857"),
        )

        fig.add_trace(
            go.Scatter(
                x=result.t,
                y=summary.Re_trajectory,
                name="Effective Reproduction Number Re(t)",
                mode="lines",
                line=dict(color="#D97706", width=2.8),
                hovertemplate="<b>Re(t):</b> %{y:.3f}<extra></extra>",
            )
        )

        fig.add_hline(
            y=1.0,
            line_width=2.0,
            line_dash="dot",
            line_color="#DC2626",
            annotation_text="Epidemic Threshold (Re = 1.0)",
            annotation_position="top right",
            annotation_font=dict(size=11, color="#DC2626"),
        )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(
            text="<b>Effective Reproduction Number Re(t) Over Time</b>",
            font=dict(size=15, color="#0F172A"),
            x=0.01,
            y=1.0,
            yref="paper",
            yanchor="bottom",
            pad=dict(b=18),
        ),
        xaxis_title="Simulation Time (Days)",
        yaxis_title="Effective Reproduction Number Re(t)",
        showlegend=False,
    )
    return fig


def create_phase_space_chart(
    result: SIRSimulationResult,
    summary: EpidemiologicalSummary,
) -> go.Figure:
    """Chart 6: Phase Space Portrait (S vs. I) Trajectory and Nullcline Analysis.

    Demonstrates the dynamical systems orbit in the S-I state space. The infection
    crest occurs exactly where the trajectory crosses the critical threshold S* = N / R0.
    """
    fig = go.Figure()

    # Phase trajectory orbit S(t) vs I(t)
    fig.add_trace(
        go.Scatter(
            x=result.S,
            y=result.I,
            mode="lines",
            name="Orbit (S, I)",
            line=dict(color="#2563EB", width=3.0),
            hovertemplate="<b>Susceptible:</b> %{x:,.0f}<br><b>Infected:</b> %{y:,.0f}<extra></extra>",
        )
    )

    # Initial condition coordinate
    fig.add_trace(
        go.Scatter(
            x=[result.S[0]],
            y=[result.I[0]],
            mode="markers+text",
            name="Initial State (t=0)",
            marker=dict(size=10, color="#059669", symbol="circle"),
            text=["  Start (t=0)"],
            textposition="top right",
            textfont=dict(size=11, color="#059669"),
            hoverinfo="skip",
        )
    )

    # Peak coordinate in phase space
    max_idx = int(np.argmax(result.I))
    fig.add_trace(
        go.Scatter(
            x=[result.S[max_idx]],
            y=[result.I[max_idx]],
            mode="markers+text",
            name="Crest / Max I",
            marker=dict(size=12, color="#DC2626", symbol="diamond"),
            text=[f"  Peak I: {result.I[max_idx]:,.0f}"],
            textposition="top right",
            textfont=dict(size=11, color="#DC2626"),
            hoverinfo="skip",
        )
    )

    # Nullcline vertical line S* = N / R0
    if summary.critical_susceptible_threshold is not None:
        crit_s = summary.critical_susceptible_threshold
        fig.add_vline(
            x=crit_s,
            line_width=1.8,
            line_dash="dash",
            line_color="#DC2626",
            annotation_text=f"Nullcline S* = N/R₀ ({crit_s:,.0f})",
            annotation_position="top left",
            annotation_font=dict(size=10, color="#DC2626"),
        )

    phase_layout = dict(CHART_LAYOUT_DEFAULTS)
    phase_layout["hovermode"] = "closest"

    fig.update_layout(
        **phase_layout,
        title=dict(
            text="<b>Phase Space Portrait: S(t) vs. I(t) Dynamical Orbit</b>",
            font=dict(size=15, color="#0F172A"),
            x=0.01,
            y=1.0,
            yref="paper",
            yanchor="bottom",
            pad=dict(b=18),
        ),
        xaxis_title="Susceptible Population S(t)",
        yaxis_title="Infected Population I(t)",
        showlegend=False,
    )
    return fig


def create_sensitivity_chart(sensitivity_items: list[SensitivityItem]) -> go.Figure:
    """Chart 7: Parameter Sensitivity Analysis for Peak Burden."""
    fig = go.Figure()

    beta_items = [item for item in sensitivity_items if "β" in item.parameter]
    gamma_items = [item for item in sensitivity_items if "γ" in item.parameter]

    if beta_items:
        fig.add_trace(
            go.Bar(
                x=[f"{item.variation_pct:+.0f}%" for item in beta_items],
                y=[item.peak_cases_change_pct for item in beta_items],
                name="Transmission Rate (β)",
                marker_color="#DC2626",
                hovertemplate="<b>β shift:</b> %{x}<br><b>Peak Change:</b> %{y:+.1f}%<extra></extra>",
            )
        )

    if gamma_items:
        fig.add_trace(
            go.Bar(
                x=[f"{item.variation_pct:+.0f}%" for item in gamma_items],
                y=[item.peak_cases_change_pct for item in gamma_items],
                name="Recovery Rate (γ)",
                marker_color="#059669",
                hovertemplate="<b>γ shift:</b> %{x}<br><b>Peak Change:</b> %{y:+.1f}%<extra></extra>",
            )
        )

    fig.add_hline(y=0.0, line_width=1.0, line_color="#475569")

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        barmode="group",
        title=dict(
            text="<b>Parameter Elasticity: Impact of Rate Shifts on Infection Peak</b>",
            font=dict(size=15, color="#0F172A"),
            x=0.01,
            y=1.0,
            yref="paper",
            yanchor="bottom",
            pad=dict(b=18),
        ),
        xaxis_title="Parameter Shift from Baseline",
        yaxis_title="Percentage Change in Peak Cases (%)",
    )
    return fig


def create_scenario_comparison_chart(
    res_a: SIRSimulationResult,
    res_b: SIRSimulationResult,
    label_a: str = "Scenario A (Baseline)",
    label_b: str = "Scenario B (Intervention)",
) -> go.Figure:
    """Scenario Comparison: Overlay active infected curves and cumulative recovery."""
    fig = go.Figure()

    # Scenario A Infected
    fig.add_trace(
        go.Scatter(
            x=res_a.t,
            y=res_a.I,
            name=f"{label_a}: Active Cases",
            mode="lines",
            line=dict(color="#DC2626", width=2.8),
            hovertemplate=f"<b>{label_a} Cases:</b> %{{y:,.0f}}<extra></extra>",
        )
    )

    # Scenario B Infected
    fig.add_trace(
        go.Scatter(
            x=res_b.t,
            y=res_b.I,
            name=f"{label_b}: Active Cases",
            mode="lines",
            line=dict(color="#2563EB", width=2.8, dash="dash"),
            hovertemplate=f"<b>{label_b} Cases:</b> %{{y:,.0f}}<extra></extra>",
        )
    )

    # Scenario A Recovered
    fig.add_trace(
        go.Scatter(
            x=res_a.t,
            y=res_a.R,
            name=f"{label_a}: Recovered",
            mode="lines",
            line=dict(color="#059669", width=2.0, dash="dot"),
            opacity=0.7,
            hovertemplate=f"<b>{label_a} Recovered:</b> %{{y:,.0f}}<extra></extra>",
        )
    )

    # Scenario B Recovered
    fig.add_trace(
        go.Scatter(
            x=res_b.t,
            y=res_b.R,
            name=f"{label_b}: Recovered",
            mode="lines",
            line=dict(color="#0D9488", width=2.0, dash="longdashdot"),
            opacity=0.7,
            hovertemplate=f"<b>{label_b} Recovered:</b> %{{y:,.0f}}<extra></extra>",
        )
    )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        height=520,
        title=dict(
            text="<b>Comparative Epidemic Trajectory (Dual Scenarios)</b>",
            font=dict(size=15, color="#0F172A"),
            x=0.015,
            y=1.0,
            yref="paper",
            yanchor="bottom",
            pad=dict(b=18),
        ),
        xaxis_title="Simulation Time (Days)",
        yaxis_title="Population Count (Individuals)",
    )
    return fig


def create_model_vs_data_chart(
    result: SIRSimulationResult,
    hist_df: pd.DataFrame,
    fit_metrics: dict[str, float] | None = None,
) -> go.Figure:
    """Chart 8: Model vs. Empirical Historical Data Comparison."""
    fig = go.Figure()

    # 1. Continuous Model Simulated Curve
    fig.add_trace(
        go.Scatter(
            x=result.t,
            y=result.I,
            name="SIR Model Active Cases I(t)",
            mode="lines",
            line=dict(color=COLOR_INFECTED, width=2.5),
            hovertemplate="<b>Simulated I(t):</b> %{y:,.0f} cases<extra></extra>",
        )
    )

    # 2. Discrete Empirical Data Points
    fig.add_trace(
        go.Scatter(
            x=hist_df["day"],
            y=hist_df["cases"],
            name="Reported Empirical Cases",
            mode="markers",
            marker=dict(
                size=7,
                color=COLOR_PRIMARY_ACCENT,
                symbol="circle",
                line=dict(color="#FFFFFF", width=1.5),
            ),
            hovertemplate="<b>Observed:</b> %{y:,.0f} cases at Day %{x:.1f}<extra></extra>",
        )
    )

    title_text = "<b>Epidemiological Calibration: Simulated ODE vs. Empirical Observations</b>"
    if fit_metrics:
        rmse = fit_metrics.get("rmse", 0.0)
        mae = fit_metrics.get("mae", 0.0)
        r2 = fit_metrics.get("r_squared", 0.0)
        title_text += (
            f"<br><span style='font-size:12px; color:#687386; font-weight:normal;'>"
            f"Goodness of Fit: RMSE = {rmse:,.1f} • MAE = {mae:,.1f} • R² = {r2:.3f}"
            f"</span>"
        )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(
            text=title_text,
            font=dict(size=14, color="#172033"),
            x=0.01,
            y=1.0,
            yref="paper",
            yanchor="bottom",
            pad=dict(b=18),
        ),
        xaxis_title="Time Horizon (Days)",
        yaxis_title="Active Infection Count",
    )
    return fig
