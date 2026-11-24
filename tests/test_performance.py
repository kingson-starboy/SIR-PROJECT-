"""Performance, Benchmark, and Scalability Tests for SIR Solver Engine."""

import time

import numpy as np

from sir_model import SIRParameters, solve_sir


class TestPerformanceAndScalability:
    """Industrial benchmark suite evaluating computation speed, memory, and scale."""

    def test_subsecond_execution_time(self):
        """Solver must complete high-resolution integration (1,000 steps) in under 200 ms."""
        params = SIRParameters(
            total_population=100000.0,
            initial_infected=50.0,
            initial_recovered=0.0,
            transmission_rate=0.35,
            recovery_rate=0.10,
            duration_days=200.0,
            num_points=1000,
        )

        start_time = time.perf_counter()
        result = solve_sir(params)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        assert result.success is True
        assert len(result.t) == 1000
        # Industrial performance constraint: solver runs in well under 300 ms on modern CPUs
        assert duration_ms < 300.0, f"Solver took too long: {duration_ms:.2f} ms"

    def test_large_population_scale(self):
        """Verify numerical stability on metropolitan scale (N = 10,000,000)."""
        params = SIRParameters(
            total_population=10_000_000.0,
            initial_infected=100.0,
            initial_recovered=0.0,
            transmission_rate=0.40,
            recovery_rate=0.10,
            duration_days=180.0,
            num_points=1000,
        )
        result = solve_sir(params)
        assert result.success is True
        # Conservation law must strictly hold even for 10 million individuals
        max_error = np.max(np.abs((result.S + result.I + result.R) - params.total_population))
        assert max_error < 1e-4

    def test_small_population_scale(self):
        """Verify numerical stability on small cohort scale (N = 100)."""
        params = SIRParameters(
            total_population=100.0,
            initial_infected=1.0,
            initial_recovered=0.0,
            transmission_rate=0.30,
            recovery_rate=0.10,
            duration_days=100.0,
            num_points=500,
        )
        result = solve_sir(params)
        assert result.success is True
        assert np.all(result.S >= 0.0)
        assert np.all(result.I >= 0.0)
        assert np.all(result.R >= 0.0)
        assert np.max(np.abs((result.S + result.I + result.R) - 100.0)) < 1e-6
