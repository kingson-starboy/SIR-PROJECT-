"""Regression Test Suite for Confirmed and Resolved Software Defects."""

import numpy as np
import plotly.graph_objects as go

from analysis import analyze_simulation
from export import generate_simulation_pdf
from sir_model import SIRParameters, solve_sir
from visualization import (
    create_animated_progression_chart,
    create_scenario_comparison_chart,
)


class TestRegressionSuite:
    """Regression tests asserting that previously identified bugs remain permanently fixed."""

    def test_bug_reg_01_no_duplicate_yaxis_in_animated_chart(self):
        """REG-01: create_animated_progression_chart must not raise TypeError for duplicate yaxis."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=20.0,
            initial_recovered=0.0,
            transmission_rate=0.30,
            recovery_rate=0.10,
            duration_days=60.0,
            num_points=100,
        )
        res = solve_sir(params)
        # Previously threw: TypeError: Layout() got multiple values for keyword argument 'yaxis'
        fig = create_animated_progression_chart(res)
        assert isinstance(fig, go.Figure)
        assert fig.layout.yaxis.range[1] > 10000.0

    def test_bug_reg_02_scenario_comparison_chart_parameter_signature(self):
        """REG-02: create_scenario_comparison_chart signature must accept (res_a, res_b, label_a, label_b)."""
        params_a = SIRParameters(10000.0, 20.0, 0.0, 0.35, 0.10, 60.0, 100)
        params_b = SIRParameters(10000.0, 20.0, 0.0, 0.20, 0.10, 60.0, 100)
        res_a = solve_sir(params_a)
        res_b = solve_sir(params_b)

        # Previously threw: TypeError: takes from 2 to 4 positional arguments but 6 were given
        fig = create_scenario_comparison_chart(res_a, res_b, "Baseline", "Intervention")
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 4

    def test_bug_reg_03_healthcare_capacity_attribute_name(self):
        """REG-03: HealthcareCapacityMetrics must expose capacity_limit without AttributeError."""
        params = SIRParameters(10000.0, 20.0, 0.0, 0.30, 0.10, 60.0, 100)
        res = solve_sir(params)
        summ = analyze_simulation(res)
        # Previously threw: AttributeError: 'HealthcareCapacityMetrics' object has no attribute 'capacity_threshold'
        assert hasattr(summ.capacity, "capacity_limit")
        assert summ.capacity.capacity_limit > 0

    def test_bug_reg_04_zero_recovery_rate_division_by_zero(self):
        """REG-04: gamma = 0 must produce R0 = None and avoid ZeroDivisionError."""
        params = SIRParameters(10000.0, 20.0, 0.0, 0.30, 0.0, 60.0, 100)
        res = solve_sir(params)
        summ = analyze_simulation(res)
        assert summ.R0 is None
        assert summ.R0_status == "Undefined / Infinite"

    def test_bug_reg_05_zero_initial_infection_equilibrium(self):
        """REG-05: I(0) = 0 must remain in exact static equilibrium with zero spurious infections."""
        params = SIRParameters(10000.0, 0.0, 0.0, 0.30, 0.10, 60.0, 100)
        res = solve_sir(params)
        assert np.all(res.I == 0.0)
        assert np.all(res.S == 10000.0)
        assert np.all(res.R == 0.0)
        assert res.max_conservation_error == 0.0

    def test_bug_reg_06_pdf_report_compilation_with_extreme_rates(self):
        """REG-06: PDF generator must compile successfully even with zero recovery rate."""
        params = SIRParameters(10000.0, 20.0, 0.0, 0.30, 0.0, 60.0, 100)
        res = solve_sir(params)
        summ = analyze_simulation(res)
        pdf_bytes = generate_simulation_pdf(res, summ)
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b"%PDF-")
