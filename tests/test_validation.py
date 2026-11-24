"""Unit Tests for Input Validation Functions."""

from validation import validate_sir_inputs


class TestValidation:
    """Test suite for boundary checking and constraint enforcement."""

    def test_valid_inputs_pass(self):
        """Standard realistic configuration should validate cleanly."""
        res = validate_sir_inputs(
            total_population=10000,
            initial_infected=10,
            initial_recovered=0,
            transmission_rate=0.30,
            recovery_rate=0.10,
            duration_days=160,
            num_points=1000,
        )
        assert res.is_valid is True
        assert len(res.errors) == 0

    def test_negative_population_rejected(self):
        """Negative or zero population must be rejected with descriptive message."""
        res = validate_sir_inputs(-500, 10, 0, 0.3, 0.1, 100)
        assert res.is_valid is False
        assert any("strictly greater than 0" in e for e in res.errors)

        res_zero = validate_sir_inputs(0, 0, 0, 0.3, 0.1, 100)
        assert res_zero.is_valid is False

    def test_negative_compartments_rejected(self):
        """Negative infected or recovered must be rejected."""
        res1 = validate_sir_inputs(10000, -10, 0, 0.3, 0.1, 100)
        assert res1.is_valid is False
        assert any("Initial infected population cannot be negative" in e for e in res1.errors)

        res2 = validate_sir_inputs(10000, 10, -5, 0.3, 0.1, 100)
        assert res2.is_valid is False
        assert any("Initial recovered population cannot be negative" in e for e in res2.errors)

    def test_compartments_exceeding_total_population(self):
        """Initial counts cannot exceed total population individually or jointly."""
        # Individual infected exceeds N
        res1 = validate_sir_inputs(1000, 1500, 0, 0.3, 0.1, 100)
        assert res1.is_valid is False
        assert any("cannot exceed total population" in e for e in res1.errors)

        # Individual recovered exceeds N
        res2 = validate_sir_inputs(1000, 10, 1200, 0.3, 0.1, 100)
        assert res2.is_valid is False
        assert any("cannot exceed total population" in e for e in res2.errors)

        # Combined infected + recovered exceeds N
        res3 = validate_sir_inputs(1000, 600, 500, 0.3, 0.1, 100)
        assert res3.is_valid is False
        assert any("Initial susceptible would be negative" in e for e in res3.errors)

    def test_negative_rates_rejected(self):
        """Negative beta or gamma must be rejected."""
        res1 = validate_sir_inputs(10000, 10, 0, -0.2, 0.1, 100)
        assert res1.is_valid is False
        assert any("Transmission rate (beta) cannot be negative" in e for e in res1.errors)

        res2 = validate_sir_inputs(10000, 10, 0, 0.3, -0.05, 100)
        assert res2.is_valid is False
        assert any("Recovery rate (gamma) cannot be negative" in e for e in res2.errors)

    def test_invalid_duration_and_resolution(self):
        """Duration and resolution bounds validation."""
        # Duration <= 0
        res1 = validate_sir_inputs(10000, 10, 0, 0.3, 0.1, 0)
        assert res1.is_valid is False
        assert any("strictly greater than 0 days" in e for e in res1.errors)

        # Duration > 3650
        res2 = validate_sir_inputs(10000, 10, 0, 0.3, 0.1, 5000)
        assert res2.is_valid is False
        assert any("exceeds maximum allowed limit" in e for e in res2.errors)

        # Num points too low
        res3 = validate_sir_inputs(10000, 10, 0, 0.3, 0.1, 100, num_points=5)
        assert res3.is_valid is False
        assert any("at least 10 points" in e for e in res3.errors)

    def test_zero_infection_warning(self):
        """Zero initial infections is valid mathematically but generates advisory warning."""
        res = validate_sir_inputs(10000, 0, 0, 0.3, 0.1, 100)
        assert res.is_valid is True
        assert any("Initial infected population is 0" in w for w in res.warnings)

    def test_zero_recovery_warning(self):
        """Zero recovery rate gamma is valid but triggers R0 warning."""
        res = validate_sir_inputs(10000, 10, 0, 0.3, 0.0, 100)
        assert res.is_valid is True
        assert any("Recovery rate gamma is 0" in w for w in res.warnings)
