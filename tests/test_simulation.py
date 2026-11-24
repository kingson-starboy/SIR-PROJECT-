"""Functional and Integration Tests for the Simulation Pipeline."""

import numpy as np
import pytest

from analysis import analyze_simulation
from sir_model import SIRParameters, solve_sir
from validation import validate_sir_inputs


class TestSimulationPipeline:
    """End-to-end verification of parameter ingestion, solving, and metric evaluation."""

    def test_deterministic_reproducibility(self):
        """Simulations executed with identical parameters must produce bitwise identical trajectories."""
        params = SIRParameters(
            total_population=50000.0,
            initial_infected=25.0,
            initial_recovered=0.0,
            transmission_rate=0.35,
            recovery_rate=0.12,
            duration_days=90.0,
            num_points=500,
        )
        res1 = solve_sir(params)
        res2 = solve_sir(params)

        assert np.array_equal(res1.t, res2.t)
        assert np.allclose(res1.S, res2.S, atol=1e-12)
        assert np.allclose(res1.I, res2.I, atol=1e-12)
        assert np.allclose(res1.R, res2.R, atol=1e-12)

    @pytest.mark.parametrize(
        "preset_name, beta, gamma",
        [
            ("Low Transmission (R0=1.5)", 0.15, 0.10),
            ("Moderate Transmission (R0=2.5)", 0.25, 0.10),
            ("High Transmission (R0=4.0)", 0.40, 0.10),
            ("Rapid Clearance (Short Infection)", 0.30, 0.20),
            ("Prolonged Contagion (Slow Recovery)", 0.25, 0.05),
        ],
    )
    def test_standard_preset_configurations(self, preset_name: str, beta: float, gamma: float):
        """Standard educational and empirical presets must converge with strictly bounded conservation errors."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=beta,
            recovery_rate=gamma,
            duration_days=100.0,
            num_points=500,
        )
        res = solve_sir(params)
        summary = analyze_simulation(res)

        assert res.success is True
        assert res.max_conservation_error < 1e-4
        assert summary.R0 == pytest.approx(beta / gamma, rel=1e-5)
        assert summary.peak.peak_infections > 0
        assert summary.final_stats.total_affected <= 10000.0

    def test_end_to_end_validation_and_solve_pipeline(self):
        """Validate input dictionary passing through validation into solver and analysis."""
        raw_inputs = {
            "total_population": 25000.0,
            "initial_infected": 50.0,
            "initial_recovered": 10.0,
            "transmission_rate": 0.28,
            "recovery_rate": 0.14,
            "duration_days": 120.0,
            "num_points": 600,
        }
        val_result = validate_sir_inputs(
            total_population=raw_inputs["total_population"],
            initial_infected=raw_inputs["initial_infected"],
            initial_recovered=raw_inputs["initial_recovered"],
            transmission_rate=raw_inputs["transmission_rate"],
            recovery_rate=raw_inputs["recovery_rate"],
            duration_days=raw_inputs["duration_days"],
            num_points=raw_inputs["num_points"],
        )
        assert val_result.is_valid is True

        params = SIRParameters(**raw_inputs)
        res = solve_sir(params)
        summ = analyze_simulation(res)

        assert res.success is True
        assert summ.R0 == pytest.approx(2.0, rel=1e-5)
        assert summ.final_stats.final_susceptible < params.initial_susceptible
        assert summ.final_stats.final_recovered > params.initial_recovered
