"""Dedicated Unit and Stress Tests for ReportLab PDF Report Generation."""

from analysis import analyze_simulation
from export import generate_simulation_pdf
from sir_model import SIRParameters, solve_sir


class TestPDFGeneration:
    """Validate PDF document compilation, formatting, vector plotting, and edge-case resilience."""

    def test_standard_pdf_report_synthesis(self):
        params = SIRParameters(
            total_population=100000.0,
            initial_infected=50.0,
            initial_recovered=0.0,
            transmission_rate=0.30,
            recovery_rate=0.10,
            duration_days=100.0,
            num_points=200,
        )
        res = solve_sir(params)
        summ = analyze_simulation(res)
        pdf_bytes = generate_simulation_pdf(res, summ)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 5000
        assert pdf_bytes.startswith(b"%PDF-")

    def test_subcritical_outbreak_pdf_report(self):
        """PDF generator must cleanly format scenarios with R0 <= 1.0 where no distinct peak crests."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=50.0,
            initial_recovered=0.0,
            transmission_rate=0.08,
            recovery_rate=0.10,
            duration_days=60.0,
            num_points=150,
        )
        res = solve_sir(params)
        summ = analyze_simulation(res)
        pdf_bytes = generate_simulation_pdf(res, summ)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 5000
        assert pdf_bytes.startswith(b"%PDF-")

    def test_hospital_capacity_unbreached_pdf_report(self):
        """PDF generator must format cleanly when hospital capacity is not breached."""
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=5.0,
            initial_recovered=0.0,
            transmission_rate=0.15,
            recovery_rate=0.10,
            duration_days=80.0,
            num_points=150,
        )
        res = solve_sir(params)
        summ = analyze_simulation(res, healthcare_capacity_limit=5000.0)  # 5,000 beds, will not breach
        assert summ.capacity.is_breached is False

        pdf_bytes = generate_simulation_pdf(res, summ)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 5000
