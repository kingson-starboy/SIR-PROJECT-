"""Functional Tests for Dual Scenario Comparison and Policy Sandbox."""

import pytest

from analysis import analyze_simulation
from sir_model import SIRParameters, solve_sir


class TestScenarioComparison:
    """Validate comparative dynamics, intervention damping, and scenario isolation."""

    def test_scenario_isolation_and_parameter_independence(self):
        """Modifying Scenario B parameters must not contaminate or alter Scenario A results."""
        params_a = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=0.35,
            recovery_rate=0.10,
            duration_days=100.0,
            num_points=200,
        )
        params_b = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=0.20,
            recovery_rate=0.10,
            duration_days=100.0,
            num_points=200,
        )

        res_a = solve_sir(params_a)
        res_b = solve_sir(params_b)

        sum_a = analyze_simulation(res_a)
        sum_b = analyze_simulation(res_b)

        # Baseline A must have higher R0, earlier peak, and higher peak burden
        assert sum_a.R0 == pytest.approx(3.5, rel=1e-4)
        assert sum_b.R0 == pytest.approx(2.0, rel=1e-4)
        assert sum_a.peak.peak_infections > sum_b.peak.peak_infections
        assert sum_a.peak.peak_day < sum_b.peak.peak_day

    def test_comparative_impact_metrics_calculation(self):
        """Verify delta metrics: peak burden reduction, peak delay, and R0 reduction."""
        params_unmitigated = SIRParameters(
            total_population=100000.0,
            initial_infected=50.0,
            initial_recovered=0.0,
            transmission_rate=0.40,
            recovery_rate=0.10,
            duration_days=120.0,
            num_points=500,
        )
        params_intervention = SIRParameters(
            total_population=100000.0,
            initial_infected=50.0,
            initial_recovered=0.0,
            transmission_rate=0.25,
            recovery_rate=0.10,
            duration_days=120.0,
            num_points=500,
        )

        res_a = solve_sir(params_unmitigated)
        res_b = solve_sir(params_intervention)

        sum_a = analyze_simulation(res_a)
        sum_b = analyze_simulation(res_b)

        # Relative peak reduction
        peak_reduction_pct = (
            (sum_a.peak.peak_infections - sum_b.peak.peak_infections) / sum_a.peak.peak_infections
        ) * 100
        assert peak_reduction_pct > 25.0

        # Peak delay in days
        peak_delay_days = sum_b.peak.peak_day - sum_a.peak.peak_day
        assert peak_delay_days > 5.0

        # R0 delta
        r0_reduction = sum_a.R0 - sum_b.R0
        assert r0_reduction == pytest.approx(1.5, rel=1e-4)
