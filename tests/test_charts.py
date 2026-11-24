"""Automated Unit Tests for Plotly Visualization Builders."""

import pandas as pd
import plotly.graph_objects as go

from analysis import analyze_simulation, compute_model_fit_metrics
from sir_model import SIRParameters, solve_sir
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


class TestChartBuilders:
    """Verify that every Plotly chart builder constructs valid figures with populated data channels."""

    @classmethod
    def setup_class(cls):
        cls.params = SIRParameters(
            total_population=10000.0,
            initial_infected=20.0,
            initial_recovered=0.0,
            transmission_rate=0.30,
            recovery_rate=0.10,
            duration_days=100.0,
            num_points=100,
        )
        cls.res = solve_sir(cls.params)
        cls.summary = analyze_simulation(cls.res)

    def test_sir_curve_chart(self):
        fig = create_sir_curve_chart(self.res)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 3  # S, I, R traces
        assert fig.layout.xaxis.title.text is not None

    def test_peak_analysis_chart(self):
        fig = create_peak_analysis_chart(self.res, self.summary, show_capacity=True)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 2  # Active I and Hospital Capacity line

    def test_population_distribution_chart(self):
        fig = create_population_distribution_chart(self.summary, self.res.parameters.total_population)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Pie)

    def test_animated_progression_chart(self):
        fig = create_animated_progression_chart(self.res)
        assert isinstance(fig, go.Figure)
        assert len(fig.frames) > 0
        assert len(fig.layout.sliders) > 0
        assert len(fig.layout.updatemenus) > 0

    def test_infection_rate_trend_chart(self):
        fig = create_infection_rate_trend_chart(self.res)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1

    def test_effective_r_chart(self):
        fig = create_effective_r_chart(self.res, self.summary)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1

    def test_phase_space_chart(self):
        fig = create_phase_space_chart(self.res, self.summary)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 2  # Trajectory and Peak Crest Marker

    def test_sensitivity_chart(self):
        from analysis import compute_parameter_sensitivity

        items = compute_parameter_sensitivity(self.params, variations=[-0.10, +0.10])
        fig = create_sensitivity_chart(items)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1

    def test_scenario_comparison_chart(self):
        params_b = SIRParameters(
            total_population=10000.0,
            initial_infected=20.0,
            initial_recovered=0.0,
            transmission_rate=0.20,
            recovery_rate=0.10,
            duration_days=100.0,
            num_points=100,
        )
        res_b = solve_sir(params_b)
        fig = create_scenario_comparison_chart(self.res, res_b, "Baseline", "Flattened")
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 4  # A Infected, B Infected, A Recovered, B Recovered

    def test_model_vs_data_chart(self):
        hist_df = pd.DataFrame({"day": [10.0, 20.0, 30.0, 40.0], "cases": [15.0, 120.0, 800.0, 2500.0]})
        fit_metrics = compute_model_fit_metrics(self.res, hist_df)
        fig = create_model_vs_data_chart(self.res, hist_df, fit_metrics)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 2  # Model Curve and Empirical Scatter Points
