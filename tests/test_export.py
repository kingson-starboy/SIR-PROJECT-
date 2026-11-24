"""Unit Tests for CSV, JSON, and Academic Report Export."""

import json

import pytest

from analysis import analyze_simulation
from export import (
    generate_simulation_csv,
    generate_simulation_dataframe,
    generate_simulation_json,
    generate_simulation_pdf,
    generate_summary_report,
)
from sir_model import SIRParameters, solve_sir


class TestExport:
    """Test suite for data serialization and summary reporting."""

    @classmethod
    def setup_class(cls):
        """Prepare baseline simulation and summary for export testing."""
        cls.params = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=0.30,
            recovery_rate=0.10,
            duration_days=100.0,
            num_points=50,
        )
        cls.res = solve_sir(cls.params)
        cls.summary = analyze_simulation(cls.res)

    def test_dataframe_generation(self):
        """Verify generated dataframe columns and row counts."""
        df = generate_simulation_dataframe(self.res, self.summary)
        assert len(df) == 50
        assert "Day" in df.columns
        assert "Susceptible_S" in df.columns
        assert "Infected_I" in df.columns
        assert "Recovered_R" in df.columns
        assert "Total_Population_N" in df.columns
        assert "Effective_Reproduction_Number_Re" in df.columns
        assert "Daily_New_Infections_Rate" in df.columns
        assert "Cumulative_Infections_Affected" in df.columns

    def test_csv_generation(self):
        """Verify CSV text format and header presence."""
        csv_str = generate_simulation_csv(self.res, self.summary)
        assert isinstance(csv_str, str)
        lines = csv_str.strip().split("\n")
        assert len(lines) == 51  # 1 header + 50 rows
        header = lines[0].split(",")
        assert "Day" in header
        assert "Susceptible_S" in header

    def test_json_generation(self):
        """Verify JSON export schema and data structure."""
        json_str = generate_simulation_json(self.res, self.summary)
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert "metadata" in parsed
        assert "parameters" in parsed
        assert "epidemiological_metrics" in parsed
        assert parsed["parameters"]["total_population"] == 10000.0
        assert parsed["epidemiological_metrics"]["basic_reproduction_number_R0"] == pytest.approx(3.0)

    def test_summary_report_generation(self):
        """Verify academic summary report content and formatting."""
        report = generate_summary_report(self.res, self.summary)
        assert isinstance(report, str)
        assert "Disease Spread Prediction and Simulation System" in report
        assert "Mathematical Formulation" in report
        assert "10,000" in report
        assert "**Basic Reproduction Number (R0):** 3.0000" in report
        assert "Peak Infection Load" in report
        assert "Conservation Law Check" in report

    def test_pdf_generation(self):
        """Verify publication-grade academic PDF report synthesis."""
        pdf_bytes = generate_simulation_pdf(self.res, self.summary)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 2000
        # Standard PDF magic header
        assert pdf_bytes.startswith(b"%PDF-")
