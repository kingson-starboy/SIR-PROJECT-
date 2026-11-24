"""Property-Based Robustness and Invariant Fuzzing Tests for SIR Dynamical Engine."""

import numpy as np
import pytest

from sir_model import SIRParameters, solve_sir


class TestDynamicalInvariantsAndFuzzing:
    """Property-based fuzzing suite evaluating mathematical conservation laws and monotonicity."""

    @pytest.mark.parametrize("seed", list(range(42, 92)))
    def test_randomized_parameter_fuzzing_invariants(self, seed: int):
        """Evaluate 50 randomized epidemiological parameter regimes against strict physical laws.

        Invariants evaluated:
        1. Mass Conservation: S(t) + I(t) + R(t) = N within numerical tolerance.
        2. Non-negativity: S(t) >= 0, I(t) >= 0, R(t) >= 0 for all t in [0, T].
        3. Monotonic Susceptibility: dS/dt <= 0 implies S(t2) <= S(t1) + numerical epsilon.
        4. Monotonic Recovery: dR/dt >= 0 implies R(t2) >= R(t1) - numerical epsilon.
        5. Infection Boundedness: 0 <= I(t) <= N for all t in [0, T].
        """
        rng = np.random.default_rng(seed)

        # Draw randomized population scale: from small cohort (200) to metropolitan (2,000,000)
        total_pop = float(rng.uniform(200.0, 2_000_000.0))

        # Initial infections between 1 and 5% of population
        i0 = float(max(1.0, rng.uniform(1.0, total_pop * 0.05)))

        # Initial recovered between 0 and 2% of population
        r0 = float(rng.uniform(0.0, total_pop * 0.02))

        # Transmission rate beta in [0.05, 1.2]
        beta = float(rng.uniform(0.05, 1.2))

        # Recovery rate gamma in [0.02, 0.6]
        gamma = float(rng.uniform(0.02, 0.6))

        # Simulation horizon between 30 and 365 days
        duration = float(rng.uniform(30.0, 365.0))

        # Integration resolution between 200 and 600 points
        num_points = int(rng.integers(200, 600))

        params = SIRParameters(
            total_population=total_pop,
            initial_infected=i0,
            initial_recovered=r0,
            transmission_rate=beta,
            recovery_rate=gamma,
            duration_days=duration,
            num_points=num_points,
        )

        result = solve_sir(params)

        # 1. Successful convergence
        assert result.success is True, f"Solver failed for seed {seed} with status: {result.message}"

        # 2. Strict Mass Conservation
        total_sum = result.S + result.I + result.R
        relative_mass_error = np.max(np.abs(total_sum - total_pop)) / total_pop
        assert relative_mass_error < 1e-4, (
            f"Conservation breached: relative error {relative_mass_error:.2e} on seed {seed}"
        )

        # 3. Compartmental Non-negativity
        assert np.all(result.S >= -1e-6), f"Negative susceptible detected on seed {seed}"
        assert np.all(result.I >= -1e-6), f"Negative infected detected on seed {seed}"
        assert np.all(result.R >= -1e-6), f"Negative recovered detected on seed {seed}"

        # 4. Monotonic Susceptibility (S cannot increase)
        # S(t+1) <= S(t) + tolerance (accounting for RK45 step jitter)
        s_diff = np.diff(result.S)
        assert np.all(s_diff <= 1e-5 * total_pop), (
            f"Susceptible population unexpectedly increased on seed {seed}"
        )

        # 5. Monotonic Recovery (R cannot decrease)
        # R(t+1) >= R(t) - tolerance
        r_diff = np.diff(result.R)
        assert np.all(r_diff >= -1e-5 * total_pop), (
            f"Recovered population unexpectedly decreased on seed {seed}"
        )

        # 6. Peak Infection Boundedness
        assert np.all(result.I <= total_pop + 1e-5), (
            f"Infected compartment exceeded total population on seed {seed}"
        )
