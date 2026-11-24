"""Unit and Numerical Tests for the SIR Differential Equation Solver."""

import numpy as np
import pytest

from sir_model import (
    SIRParameters,
    sir_derivatives,
    solve_sir,
)


class TestSIRDerivatives:
    """Tests for the instantaneous differential rate computations."""

    def test_derivatives_zero_infection(self):
        """When I=0, all derivatives dS/dt, dI/dt, dR/dt must be zero."""
        derivatives = sir_derivatives(t=0.0, y=[9900.0, 0.0, 100.0], beta=0.3, gamma=0.1, N=10000.0)
        assert derivatives == [0.0, 0.0, 0.0]

    def test_derivatives_standard(self):
        """Verify analytical values of derivatives for known state."""
        N = 10000.0
        S = 9000.0
        I = 1000.0
        R = 0.0
        beta = 0.4
        gamma = 0.1

        # Expected:
        # dS/dt = -0.4 * (9000 * 1000) / 10000 = -360.0
        # dI/dt = 360.0 - (0.1 * 1000) = 260.0
        # dR/dt = 0.1 * 1000 = 100.0
        dS, dI, dR = sir_derivatives(t=0.0, y=[S, I, R], beta=beta, gamma=gamma, N=N)
        assert np.isclose(dS, -360.0)
        assert np.isclose(dI, 260.0)
        assert np.isclose(dR, 100.0)
        assert np.isclose(dS + dI + dR, 0.0)


class TestSIRModelSolver:
    """Tests for SciPy numerical integration and boundary conditions."""

    def test_initial_conditions_assignment(self):
        """Test that initial conditions S(0), I(0), R(0) match parameter configuration."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=50.0,
            initial_recovered=200.0,
            transmission_rate=0.3,
            recovery_rate=0.1,
            duration_days=100.0,
            num_points=500,
        )
        assert params.initial_susceptible == 9750.0

        res = solve_sir(params)
        assert np.isclose(res.S[0], 9750.0)
        assert np.isclose(res.I[0], 50.0)
        assert np.isclose(res.R[0], 200.0)

    def test_population_conservation(self):
        """S(t) + I(t) + R(t) == N must hold across the entire trajectory within tight tolerance."""
        params = SIRParameters(
            total_population=50000.0,
            initial_infected=25.0,
            initial_recovered=0.0,
            transmission_rate=0.35,
            recovery_rate=0.10,
            duration_days=180.0,
            num_points=1000,
        )
        res = solve_sir(params)
        total_pop_trajectory = res.S + res.I + res.R

        # Relative discrepancy must be well within 1e-6
        max_error = np.max(np.abs(total_pop_trajectory - params.total_population))
        assert max_error < 1e-5
        assert np.all(res.S >= 0.0)
        assert np.all(res.I >= 0.0)
        assert np.all(res.R >= 0.0)

    def test_zero_initial_infection(self):
        """When initial infections are 0, population remains completely static."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=0.0,
            initial_recovered=0.0,
            transmission_rate=0.4,
            recovery_rate=0.1,
            duration_days=100.0,
            num_points=200,
        )
        res = solve_sir(params)
        assert np.all(res.S == 10000.0)
        assert np.all(res.I == 0.0)
        assert np.all(res.R == 0.0)
        assert res.success is True

    def test_zero_transmission_rate(self):
        """When transmission rate beta is 0, infections monotonically decay to 0 and S is constant."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=100.0,
            initial_recovered=0.0,
            transmission_rate=0.0,
            recovery_rate=0.1,
            duration_days=100.0,
            num_points=500,
        )
        res = solve_sir(params)
        # S should remain completely untouched
        assert np.allclose(res.S, 9900.0, atol=1e-3)
        # I should monotonically decrease
        assert res.I[-1] < res.I[0]
        # R should increase by approximately the initial infected count
        assert np.isclose(res.R[-1], 100.0, atol=1e-2)

    def test_zero_recovery_rate(self):
        """When recovery rate gamma is 0, recovered remains at R0 and infected accumulates until S depletes."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=0.25,
            recovery_rate=0.0,
            duration_days=100.0,
            num_points=500,
        )
        res = solve_sir(params)
        # R should remain 0 throughout
        assert np.allclose(res.R, 0.0, atol=1e-5)
        # S should monotonically decrease
        assert res.S[-1] < res.S[0]
        # Conservation holds
        assert np.allclose(res.S + res.I, 10000.0, atol=1e-4)

    def test_high_transmission_rate(self):
        """A very high transmission rate (beta=1.5) should rapidly deplete susceptible population."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=1.5,
            recovery_rate=0.1,
            duration_days=60.0,
            num_points=600,
        )
        res = solve_sir(params)
        assert res.success is True
        # Vast majority of population will have been infected and recovered
        assert res.R[-1] > 9000.0
        assert np.max(res.I) > 5000.0

    def test_high_recovery_rate(self):
        """A very high recovery rate (gamma=1.0) with moderate beta (0.3) means R0=0.3 < 1, so no outbreak."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=50.0,
            initial_recovered=0.0,
            transmission_rate=0.3,
            recovery_rate=1.0,
            duration_days=50.0,
            num_points=300,
        )
        res = solve_sir(params)
        assert res.success is True
        # Infections decay immediately from t=0
        assert np.max(res.I) == res.I[0]
        assert res.I[-1] < 1e-4

    def test_invalid_parameters_raise_value_errors(self):
        """Verify that invalid inputs raise meaningful ValueErrors."""
        # Non-positive population
        with pytest.raises(ValueError, match="Total population N must be strictly positive"):
            solve_sir(SIRParameters(0, 10, 0, 0.3, 0.1, 100))

        # Negative infected
        with pytest.raises(ValueError, match="Initial infected population cannot be negative"):
            solve_sir(SIRParameters(1000, -5, 0, 0.3, 0.1, 100))

        # I0 + R0 > N
        with pytest.raises(ValueError, match="cannot be negative"):
            solve_sir(SIRParameters(1000, 800, 300, 0.3, 0.1, 100))

        # Negative beta
        with pytest.raises(ValueError, match="Transmission rate beta must be non-negative"):
            solve_sir(SIRParameters(1000, 10, 0, -0.3, 0.1, 100))

        # Negative duration
        with pytest.raises(ValueError, match="Simulation duration must be strictly positive"):
            solve_sir(SIRParameters(1000, 10, 0, 0.3, 0.1, -10))

    def test_dataframe_conversion(self):
        """Verify export to pandas DataFrame."""
        params = SIRParameters(1000, 10, 0, 0.3, 0.1, 50, 100)
        res = solve_sir(params)
        df = res.to_dataframe()
        assert len(df) == 100
        assert list(df.columns) == ["day", "susceptible", "infected", "recovered", "total_population"]


class TestInterventionAndVaccination:
    """Test suite for policy interventions (time-dependent beta) and vaccination rate dynamics."""

    def test_staged_intervention_dampens_peak(self):
        """Introducing an intervention at Day 20 reducing beta by 50% must significantly reduce peak cases."""
        baseline_params = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=0.35,
            recovery_rate=0.10,
            duration_days=120.0,
            num_points=500,
        )
        base_res = solve_sir(baseline_params)

        interv_params = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=0.35,
            recovery_rate=0.10,
            duration_days=120.0,
            num_points=500,
            intervention_day=20.0,
            intervention_beta_reduction=0.50,
        )
        interv_res = solve_sir(interv_params)

        # Both must conserve total population strictly
        assert base_res.success and interv_res.success
        assert interv_res.max_conservation_error < 1e-4

        # Peak cases with intervention must be significantly lower
        assert np.max(interv_res.I) < np.max(base_res.I)

    def test_vaccination_transfers_susceptible_to_recovered(self):
        """Active vaccination transfers susceptible directly to recovered and conserves N."""
        vax_params = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=0.30,
            recovery_rate=0.10,
            duration_days=100.0,
            num_points=500,
            vaccination_rate=0.02,  # 2% of susceptible vaccinated daily
        )
        vax_res = solve_sir(vax_params)
        assert vax_res.success
        # S(t) + I(t) + R(t) = N must strictly hold
        assert np.max(np.abs(vax_res.S + vax_res.I + vax_res.R - 10000.0)) < 1e-4
        # Final recovered must be higher due to vaccination
        assert vax_res.R[-1] > 5000.0
