"""Epidemiological Metrics, Outbreak Analysis, and Dynamical Systems Analysis for SIR Model.

Computes reproduction numbers (R0, Re(t)), peak infection dynamics, final state statistics,
healthcare capacity thresholds, phase-space nullclines, and parameter sensitivity.
"""

from __future__ import annotations

import io
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from sir_model import SIRParameters, SIRSimulationResult


@dataclass
class PeakInfectionMetrics:
    """Metrics related to the maximum infection burden."""

    peak_infections: float
    peak_day: float
    peak_percentage: float
    has_distinct_peak: bool


@dataclass
class FinalOutbreakStatistics:
    """Final cumulative statistics at the end of the simulation."""

    final_susceptible: float
    final_infected: float
    final_recovered: float
    total_affected: float
    percent_affected: float
    percent_recovered: float


@dataclass
class HealthcareCapacityMetrics:
    """Assessment against hospital / ICU bed capacity limits."""

    capacity_limit: float
    capacity_percentage: float
    is_breached: bool
    breach_day_start: float | None
    breach_day_end: float | None
    breach_duration_days: float
    peak_excess_cases: float


@dataclass
class EpidemicTrendAnalysis:
    """Qualitative and quantitative trajectory trend markers."""

    initial_trend: str  # "Increasing", "Decreasing", "Static"
    reaches_significant_peak: bool
    clearance_day: float | None  # Day when active infections drop below threshold
    threshold_value: float
    herd_immunity_threshold: float | None  # 1 - 1/R0 if R0 > 1
    alert_level: str  # "Low (Green)", "Moderate (Yellow)", "Elevated (Orange)", "Severe (Red)"
    alert_description: str


@dataclass
class SensitivityItem:
    """Sensitivity of a key metric under parameter variation."""

    parameter: str
    variation_pct: float
    varied_value: float
    new_r0: float | None
    new_peak_cases: float
    new_peak_day: float
    peak_cases_change_pct: float


@dataclass
class EpidemiologicalSummary:
    """Comprehensive analysis report of the SIR simulation."""

    R0: float | None
    R0_status: str
    R0_interpretation: str
    Re_trajectory: np.ndarray
    peak: PeakInfectionMetrics
    final_stats: FinalOutbreakStatistics
    trends: EpidemicTrendAnalysis
    capacity: HealthcareCapacityMetrics
    daily_new_infections: np.ndarray
    cumulative_affected: np.ndarray
    critical_susceptible_threshold: float | None  # S* = N / R0


def calculate_r0(beta: float, gamma: float) -> tuple[float | None, str, str]:
    """Calculate the basic reproduction number R0 = beta / gamma."""
    if gamma <= 0:
        return (
            None,
            "Undefined / Infinite",
            (
                "Since the recovery rate gamma is 0 (infected individuals do not recover), "
                "the basic reproduction number R0 is mathematically infinite/undefined."
            ),
        )

    r0_val = beta / gamma

    if r0_val > 1.0:
        interp = (
            f"R0 = {r0_val:.2f} > 1.0: Each infected host transmits to on average more than "
            "one susceptible individual. An epidemic wave will emerge."
        )
    elif math.isclose(r0_val, 1.0, rel_tol=1e-3):
        interp = (
            f"R0 = {r0_val:.2f} ≈ 1.0: The outbreak is at the critical endemic equilibrium. "
            "Infections remain approximately constant."
        )
    else:
        interp = (
            f"R0 = {r0_val:.2f} < 1.0: Subcritical transmission. Each infected individual "
            "fails to replace themselves, leading to monotonic extinction without a major wave."
        )

    return (r0_val, f"{r0_val:.2f}", interp)


def calculate_effective_r(
    beta: float,
    gamma: float,
    S: np.ndarray,
    N: float,
) -> np.ndarray:
    """Compute the time-varying effective reproduction number: Re(t) = (beta / gamma) * (S(t) / N)."""
    if gamma <= 0 or N <= 0:
        return np.full_like(S, np.nan, dtype=float)

    r0 = beta / gamma
    return r0 * (S / N)


def evaluate_healthcare_capacity(
    t: np.ndarray,
    I: np.ndarray,
    capacity_limit: float,
    total_population: float,
) -> HealthcareCapacityMetrics:
    """Analyze whether active cases exceed healthcare / ICU capacity."""
    capacity_pct = (capacity_limit / total_population * 100.0) if total_population > 0 else 0.0
    breached_indices = np.where(I > capacity_limit)[0]

    if len(breached_indices) == 0:
        return HealthcareCapacityMetrics(
            capacity_limit=capacity_limit,
            capacity_percentage=capacity_pct,
            is_breached=False,
            breach_day_start=None,
            breach_day_end=None,
            breach_duration_days=0.0,
            peak_excess_cases=0.0,
        )

    start_day = float(t[breached_indices[0]])
    end_day = float(t[breached_indices[-1]])
    duration = max(0.0, end_day - start_day)
    max_cases = float(np.max(I))
    excess = max(0.0, max_cases - capacity_limit)

    return HealthcareCapacityMetrics(
        capacity_limit=capacity_limit,
        capacity_percentage=capacity_pct,
        is_breached=True,
        breach_day_start=start_day,
        breach_day_end=end_day,
        breach_duration_days=duration,
        peak_excess_cases=excess,
    )


def determine_alert_level(
    r0: float | None,
    peak_pct: float,
    capacity_breached: bool,
) -> tuple[str, str]:
    """Classify the epidemic severity into standard epidemiological alert tiers."""
    if r0 is None or r0 > 3.0 or (capacity_breached and peak_pct > 25.0):
        return (
            "Severe (Red)",
            "High transmission dynamics. Urgent hospital capacity planning and strict suppression required.",
        )
    elif r0 > 1.8 or capacity_breached:
        return (
            "Elevated (Orange)",
            "Substantial epidemic wave. Public health mitigation and targeted containment recommended.",
        )
    elif r0 > 1.0:
        return (
            "Moderate (Yellow)",
            "Controlled transmission above replacement threshold. Active surveillance required.",
        )
    else:
        return (
            "Low (Green)",
            "Subcritical transmission (R0 < 1.0). Outbreak is self-limiting and declining.",
        )


def analyze_simulation(
    result: SIRSimulationResult,
    clearance_threshold: float = 1.0,
    healthcare_capacity_limit: float | None = None,
) -> EpidemiologicalSummary:
    """Perform exhaustive epidemiological and dynamical systems analysis on an SIR trajectory."""
    params = result.parameters
    N = result.N
    t = result.t
    S = result.S
    I = result.I
    R = result.R

    # Basic & Effective Reproduction
    r0_val, r0_status, r0_interp = calculate_r0(params.transmission_rate, params.recovery_rate)
    re_traj = calculate_effective_r(params.transmission_rate, params.recovery_rate, S, N)

    # Peak Infection Analysis
    max_idx = int(np.argmax(I))
    peak_infections = float(I[max_idx])
    peak_day = float(t[max_idx])
    peak_percentage = (peak_infections / N) * 100.0 if N > 0 else 0.0

    has_distinct_peak = (
        max_idx > 0
        and peak_infections > (params.initial_infected + 1e-4)
        and (r0_val is None or r0_val > 1.0)
    )

    peak_metrics = PeakInfectionMetrics(
        peak_infections=peak_infections,
        peak_day=peak_day,
        peak_percentage=peak_percentage,
        has_distinct_peak=has_distinct_peak,
    )

    # Final Outbreak Statistics
    final_S = float(S[-1])
    final_I = float(I[-1])
    final_R = float(R[-1])
    total_affected = max(0.0, float(N - final_S))
    percent_affected = (total_affected / N) * 100.0 if N > 0 else 0.0
    percent_recovered = (final_R / N) * 100.0 if N > 0 else 0.0

    final_stats = FinalOutbreakStatistics(
        final_susceptible=final_S,
        final_infected=final_I,
        final_recovered=final_R,
        total_affected=total_affected,
        percent_affected=percent_affected,
        percent_recovered=percent_recovered,
    )

    # Healthcare capacity analysis (default: 15% of total population if not specified)
    effective_capacity = healthcare_capacity_limit if healthcare_capacity_limit is not None else (0.15 * N)
    capacity_metrics = evaluate_healthcare_capacity(t, I, effective_capacity, N)

    # Initial Trend & Clearance Day
    if params.initial_infected <= 0:
        initial_trend = "Static"
    else:
        init_didt = (
            params.transmission_rate * (params.initial_susceptible * params.initial_infected) / N
            - params.recovery_rate * params.initial_infected
        )
        if init_didt > 1e-5:
            initial_trend = "Increasing"
        elif init_didt < -1e-5:
            initial_trend = "Decreasing"
        else:
            initial_trend = "Static"

    clearance_day: float | None = None
    if has_distinct_peak:
        post_peak_indices = np.where((t >= peak_day) & (I < clearance_threshold))[0]
        if len(post_peak_indices) > 0:
            clearance_day = float(t[post_peak_indices[0]])
    else:
        indices = np.where(I < clearance_threshold)[0]
        if len(indices) > 0:
            clearance_day = float(t[indices[0]])

    hit: float | None = None
    critical_s_threshold: float | None = None
    if r0_val is not None and r0_val > 1.0:
        hit = (1.0 - (1.0 / r0_val)) * 100.0
        critical_s_threshold = N / r0_val

    alert_tier, alert_info = determine_alert_level(
        r0=r0_val,
        peak_pct=peak_percentage,
        capacity_breached=capacity_metrics.is_breached,
    )

    trends = EpidemicTrendAnalysis(
        initial_trend=initial_trend,
        reaches_significant_peak=has_distinct_peak,
        clearance_day=clearance_day,
        threshold_value=clearance_threshold,
        herd_immunity_threshold=hit,
        alert_level=alert_tier,
        alert_description=alert_info,
    )

    daily_new_infections = params.transmission_rate * (S * I) / N
    cumulative_affected = np.maximum(0.0, N - S)

    return EpidemiologicalSummary(
        R0=r0_val,
        R0_status=r0_status,
        R0_interpretation=r0_interp,
        Re_trajectory=re_traj,
        peak=peak_metrics,
        final_stats=final_stats,
        trends=trends,
        capacity=capacity_metrics,
        daily_new_infections=daily_new_infections,
        cumulative_affected=cumulative_affected,
        critical_susceptible_threshold=critical_s_threshold,
    )


def compute_parameter_sensitivity(
    base_params: SIRParameters,
    variations: list[float] | None = None,
) -> list[SensitivityItem]:
    """Compute elasticity and sensitivity of epidemic peak to variations in transmission and recovery."""
    from sir_model import solve_sir

    if variations is None:
        variations = [-0.20, -0.10, +0.10, +0.20]

    base_res = solve_sir(base_params)
    base_summary = analyze_simulation(base_res)
    base_peak = base_summary.peak.peak_infections

    sensitivity_results: list[SensitivityItem] = []

    # Test transmission rate beta variations
    for var in variations:
        new_beta = max(0.01, base_params.transmission_rate * (1.0 + var))
        p = SIRParameters(
            total_population=base_params.total_population,
            initial_infected=base_params.initial_infected,
            initial_recovered=base_params.initial_recovered,
            transmission_rate=new_beta,
            recovery_rate=base_params.recovery_rate,
            duration_days=base_params.duration_days,
            num_points=base_params.num_points,
        )
        try:
            sol = solve_sir(p)
            summ = analyze_simulation(sol)
            pct_chg = ((summ.peak.peak_infections - base_peak) / base_peak * 100.0) if base_peak > 0 else 0.0
            sensitivity_results.append(
                SensitivityItem(
                    parameter="Transmission Rate (β)",
                    variation_pct=var * 100.0,
                    varied_value=new_beta,
                    new_r0=summ.R0,
                    new_peak_cases=summ.peak.peak_infections,
                    new_peak_day=summ.peak.peak_day,
                    peak_cases_change_pct=pct_chg,
                )
            )
        except Exception:
            continue

    # Test recovery rate gamma variations
    for var in variations:
        new_gamma = max(0.01, base_params.recovery_rate * (1.0 + var))
        p = SIRParameters(
            total_population=base_params.total_population,
            initial_infected=base_params.initial_infected,
            initial_recovered=base_params.initial_recovered,
            transmission_rate=base_params.transmission_rate,
            recovery_rate=new_gamma,
            duration_days=base_params.duration_days,
            num_points=base_params.num_points,
        )
        try:
            sol = solve_sir(p)
            summ = analyze_simulation(sol)
            pct_chg = ((summ.peak.peak_infections - base_peak) / base_peak * 100.0) if base_peak > 0 else 0.0
            sensitivity_results.append(
                SensitivityItem(
                    parameter="Recovery Rate (γ)",
                    variation_pct=var * 100.0,
                    varied_value=new_gamma,
                    new_r0=summ.R0,
                    new_peak_cases=summ.peak.peak_infections,
                    new_peak_day=summ.peak.peak_day,
                    peak_cases_change_pct=pct_chg,
                )
            )
        except Exception:
            continue

    return sensitivity_results


def parse_and_validate_historical_csv(
    file_content: bytes | str,
) -> tuple[pd.DataFrame | None, list[str]]:
    """Parse and rigorously validate an uploaded historical epidemic dataset.

    Validates:
    - Non-empty CSV format
    - Presence of time column (day, date, time)
    - Presence of case count column (cases, infected, active)
    - Non-negative case values
    - Zero missing (NaN) values
    - Strictly monotonic chronological ordering
    - No duplicate time stamps
    """
    errors: list[str] = []
    if not file_content:
        return None, ["The provided file is empty."]

    try:
        if isinstance(file_content, bytes):
            text = file_content.decode("utf-8", errors="replace")
        else:
            text = file_content
        df = pd.read_csv(io.StringIO(text))
    except Exception as e:
        return None, [f"Failed to parse CSV dataset: {str(e)}"]

    if df.empty:
        return None, ["The CSV file contains no data rows."]

    col_map = {col: str(col).strip().lower() for col in df.columns}
    df.rename(columns=col_map, inplace=True)

    day_col = None
    for candidate in ["day", "days", "time", "t", "date"]:
        if candidate in df.columns:
            day_col = candidate
            break

    cases_col = None
    for candidate in ["infected", "cases", "active_cases", "active", "i"]:
        if candidate in df.columns:
            cases_col = candidate
            break

    if not day_col:
        errors.append("Missing time column. Expected: 'day', 'time', 'date', or 't'.")
    if not cases_col:
        errors.append("Missing infection column. Expected: 'infected', 'cases', 'active_cases', or 'i'.")

    if errors:
        return None, errors

    cleaned_df = pd.DataFrame()

    # Parse day/date column
    try:
        cleaned_df["day"] = pd.to_numeric(df[day_col])
    except Exception:
        try:
            dates = pd.to_datetime(df[day_col])
            cleaned_df["day"] = (dates - dates.min()).dt.total_seconds() / 86400.0
        except Exception:
            errors.append(f"Column '{day_col}' could not be parsed as numerical days or standard dates.")

    # Parse cases column
    try:
        cleaned_df["cases"] = pd.to_numeric(df[cases_col])
    except Exception:
        errors.append(f"Column '{cases_col}' contains non-numeric values.")

    if errors:
        return None, errors

    if cleaned_df["day"].isna().any() or cleaned_df["cases"].isna().any():
        errors.append("Dataset contains missing (NaN) values.")

    if (cleaned_df["cases"] < 0).any():
        errors.append("Dataset contains negative case counts.")

    if (cleaned_df["day"] < 0).any():
        errors.append("Dataset contains negative time values.")

    if not cleaned_df["day"].is_monotonic_increasing:
        errors.append("Time points are not in strictly ascending chronological order.")

    if cleaned_df["day"].duplicated().any():
        errors.append("Dataset contains duplicate day entries.")

    if errors:
        return None, errors

    return cleaned_df[["day", "cases"]], []


def compute_model_fit_metrics(
    sim: SIRSimulationResult,
    hist_df: pd.DataFrame,
) -> dict[str, float]:
    """Compute empirical goodness-of-fit error metrics (RMSE, MAE, R²) against observed cases."""
    t_hist = hist_df["day"].to_numpy(dtype=float)
    y_hist = hist_df["cases"].to_numpy(dtype=float)

    # Interpolate simulated active infected I(t) onto historical day coordinates
    y_sim_interp = np.interp(t_hist, sim.t, sim.I)

    residuals = y_sim_interp - y_hist
    rmse = float(np.sqrt(np.mean(residuals**2)))
    mae = float(np.mean(np.abs(residuals)))

    ss_tot = float(np.sum((y_hist - np.mean(y_hist)) ** 2))
    ss_res = float(np.sum(residuals**2))
    r_squared = float(1.0 - (ss_res / ss_tot)) if ss_tot > 1e-9 else 0.0

    nonzero_mask = y_hist > 0
    mape = (
        float(np.mean(np.abs(residuals[nonzero_mask] / y_hist[nonzero_mask])) * 100.0)
        if np.any(nonzero_mask)
        else 0.0
    )

    return {
        "rmse": rmse,
        "mae": mae,
        "mape": mape,
        "r_squared": max(-1.0, min(1.0, r_squared)),
        "n_points": float(len(t_hist)),
    }
