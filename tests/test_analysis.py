"""Unit and Numerical Tests for Epidemiological Analysis Calculations."""

import numpy as np
import pytest

from analysis import (
    analyze_simulation,
    calculate_effective_r,
    calculate_r0,
    compute_parameter_sensitivity,
    evaluate_healthcare_capacity,
)
from sir_model import SIRParameters, solve_sir


class TestR0Calculations:
    """Test suite for basic and effective reproduction numbers."""

    def test_r0_standard_case(self):
        """R0 = beta / gamma for typical values."""
        r0, status, interp = calculate_r0(beta=0.3, gamma=0.1)
        assert r0 == pytest.approx(3.0, rel=1e-5)
        assert status == "3.00"
        assert "outbreak will occur" in interp or "wave will emerge" in interp

    def test_r0_subcritical(self):
        """When R0 < 1.0, epidemic declines."""
        r0, status, interp = calculate_r0(beta=0.15, gamma=0.3)
        assert r0 == pytest.approx(0.5, rel=1e-5)
        assert status == "0.50"
        assert "Subcritical" in interp or "monotonically decline" in interp

    def test_r0_zero_recovery_division_by_zero_prevention(self):
        """When gamma = 0, R0 is undefined/infinite without crashing."""
        r0, status, interp = calculate_r0(beta=0.3, gamma=0.0)
        assert r0 is None
        assert "Undefined / Infinite" in status
        assert "mathematically infinite" in interp

    def test_effective_r_trajectory(self):
        """Re(t) = R0 * S(t) / N."""
        beta = 0.4
        gamma = 0.2  # R0 = 2.0
        N = 1000.0
        S = np.array([1000.0, 750.0, 500.0, 250.0, 0.0])

        re = calculate_effective_r(beta, gamma, S, N)
        expected = np.array([2.0, 1.5, 1.0, 0.5, 0.0])
        assert np.allclose(re, expected)


class TestEpidemiologicalSummary:
    """Test full analysis suite on simulation solutions."""

    def test_peak_infection_detection(self):
        """Verify peak infection matches maximum of I array."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=0.30,
            recovery_rate=0.10,
            duration_days=160.0,
            num_points=1000,
        )
        res = solve_sir(params)
        summary = analyze_simulation(res)

        assert summary.R0 == pytest.approx(3.0)
        assert summary.peak.peak_infections == pytest.approx(np.max(res.I))
        assert summary.peak.has_distinct_peak is True
        assert summary.peak.peak_day > 0.0
        assert summary.peak.peak_percentage == pytest.approx((np.max(res.I) / 10000.0) * 100.0)

    def test_final_outbreak_statistics(self):
        """Final statistics must match end of simulation trajectory."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=0.30,
            recovery_rate=0.10,
            duration_days=160.0,
            num_points=1000,
        )
        res = solve_sir(params)
        summary = analyze_simulation(res)

        assert summary.final_stats.final_susceptible == pytest.approx(res.S[-1])
        assert summary.final_stats.final_infected == pytest.approx(res.I[-1])
        assert summary.final_stats.final_recovered == pytest.approx(res.R[-1])
        assert summary.final_stats.total_affected == pytest.approx(10000.0 - res.S[-1])
        assert summary.final_stats.percent_affected == pytest.approx(
            ((10000.0 - res.S[-1]) / 10000.0) * 100.0
        )

    def test_subcritical_outbreak_no_distinct_peak(self):
        """When R0 < 1, initial infections decay immediately, so no distinct secondary peak."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=100.0,
            initial_recovered=0.0,
            transmission_rate=0.05,
            recovery_rate=0.10,
            duration_days=100.0,
            num_points=500,
        )
        res = solve_sir(params)
        summary = analyze_simulation(res)

        assert summary.R0 == pytest.approx(0.5)
        assert summary.peak.has_distinct_peak is False
        assert summary.trends.initial_trend == "Decreasing"
        assert summary.trends.herd_immunity_threshold is None

    def test_daily_new_infections_and_cumulative(self):
        """Daily new infections rate and cumulative trajectory consistency."""
        params = SIRParameters(
            total_population=1000.0,
            initial_infected=5.0,
            initial_recovered=0.0,
            transmission_rate=0.3,
            recovery_rate=0.1,
            duration_days=50.0,
            num_points=200,
        )
        res = solve_sir(params)
        summary = analyze_simulation(res)

        # Cumulative affected must be monotonically non-decreasing
        diffs = np.diff(summary.cumulative_affected)
        assert np.all(diffs >= -1e-6)
        # Daily new rate must be non-negative
        assert np.all(summary.daily_new_infections >= 0.0)

    def test_healthcare_capacity_evaluation(self):
        """Test detection of hospital capacity breaches."""
        t = np.linspace(0, 100, 100)
        I = np.zeros(100)
        I[30:70] = 500.0  # Spike of 500 cases between t=30 and t=69

        # Case 1: Limit is 200 -> Breached
        cap_breached = evaluate_healthcare_capacity(t, I, capacity_limit=200.0, total_population=1000.0)
        assert cap_breached.is_breached is True
        assert cap_breached.peak_excess_cases == 300.0
        assert cap_breached.breach_day_start is not None

        # Case 2: Limit is 1000 -> Not breached
        cap_safe = evaluate_healthcare_capacity(t, I, capacity_limit=1000.0, total_population=1000.0)
        assert cap_safe.is_breached is False
        assert cap_safe.peak_excess_cases == 0.0
        assert cap_safe.breach_day_start is None

    def test_critical_susceptible_nullcline(self):
        """Verify nullcline threshold S* = N / R0 when R0 > 1."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=0.30,
            recovery_rate=0.10,
            duration_days=100.0,
            num_points=500,
        )
        res = solve_sir(params)
        summary = analyze_simulation(res)
        # R0 = 3.00 -> S* = 10000 / 3.00 = 3333.33
        assert summary.critical_susceptible_threshold == pytest.approx(10000.0 / 3.0, rel=1e-3)

    def test_parameter_sensitivity(self):
        """Verify sensitivity computations under rate variations."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=0.30,
            recovery_rate=0.10,
            duration_days=100.0,
            num_points=300,
        )
        sens_items = compute_parameter_sensitivity(params, variations=[-0.10, +0.10])
        assert len(sens_items) == 4
        # Increasing beta should increase peak cases
        beta_pos = [item for item in sens_items if "β" in item.parameter and item.variation_pct > 0][0]
        assert beta_pos.peak_cases_change_pct > 0.0


class TestHistoricalDataAndFitting:
    """Test suite for empirical dataset validation and model goodness-of-fit metrics."""

    def test_valid_historical_csv_parsing(self):
        """Standard valid CSV with day and cases columns parses correctly."""
        from analysis import parse_and_validate_historical_csv

        csv_content = "day,cases\n0,10\n10,120\n20,800\n30,2500\n40,2900\n50,1400\n"
        df, errors = parse_and_validate_historical_csv(csv_content)
        assert len(errors) == 0
        assert df is not None
        assert len(df) == 6
        assert list(df.columns) == ["day", "cases"]
        assert df["cases"].iloc[-1] == 1400

    def test_empty_historical_csv_rejected(self):
        """Empty or blank CSV content must yield understandable validation error."""
        from analysis import parse_and_validate_historical_csv

        df, errors = parse_and_validate_historical_csv("")
        assert df is None
        assert any("empty" in e.lower() for e in errors)

    def test_missing_columns_rejected(self):
        """CSV missing either day or cases must be rejected."""
        from analysis import parse_and_validate_historical_csv

        csv_missing_day = "foo,bar\n1,2\n3,4\n"
        df, errors = parse_and_validate_historical_csv(csv_missing_day)
        assert df is None
        assert any("missing" in e.lower() for e in errors)

    def test_negative_cases_rejected(self):
        """CSV containing negative case values must be rejected."""
        from analysis import parse_and_validate_historical_csv

        csv_neg = "day,cases\n0,10\n10,-50\n20,100\n"
        df, errors = parse_and_validate_historical_csv(csv_neg)
        assert df is None
        assert any("negative" in e.lower() for e in errors)

    def test_unsorted_and_duplicate_days_rejected(self):
        """CSV with non-monotonic or duplicate time stamps must be rejected."""
        from analysis import parse_and_validate_historical_csv

        csv_unsorted = "day,cases\n0,10\n20,800\n10,120\n"
        df, errors = parse_and_validate_historical_csv(csv_unsorted)
        assert df is None
        assert any("ascending" in e.lower() or "order" in e.lower() for e in errors)

        csv_dup = "day,cases\n0,10\n10,120\n10,150\n20,800\n"
        df_dup, errors_dup = parse_and_validate_historical_csv(csv_dup)
        assert df_dup is None
        assert any("duplicate" in e.lower() for e in errors_dup)

    def test_goodness_of_fit_metrics_calculation(self):
        """Verify empirical RMSE, MAE, and R² calculations against simulated trajectory."""
        import pandas as pd

        from analysis import compute_model_fit_metrics

        params = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=0.30,
            recovery_rate=0.10,
            duration_days=100.0,
            num_points=500,
        )
        sim = solve_sir(params)

        # Create synthetic observation sampling the true model plus small noise
        hist_days = np.array([0, 15, 30, 45, 60, 75, 90], dtype=float)
        true_cases = np.interp(hist_days, sim.t, sim.I)
        observed_cases = true_cases + np.array([0.0, 5.0, -10.0, 12.0, -8.0, 4.0, 0.0])
        hist_df = pd.DataFrame({"day": hist_days, "cases": observed_cases})

        metrics = compute_model_fit_metrics(sim, hist_df)
        assert "rmse" in metrics
        assert "mae" in metrics
        assert "r_squared" in metrics
        assert metrics["rmse"] > 0.0
        assert metrics["mae"] > 0.0
        # Should have extremely high correlation with slightly perturbed observations
        assert metrics["r_squared"] > 0.95
