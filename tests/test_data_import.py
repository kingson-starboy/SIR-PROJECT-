"""Unit and Negative Tests for Historical Data Ingestion and Validation."""

import pandas as pd

from analysis import compute_model_fit_metrics, parse_and_validate_historical_csv
from sir_model import SIRParameters, solve_sir


class TestDataImportAndValidation:
    """Validate empirical CSV parsing, schema enforcement, and error calculation."""

    def test_valid_csv_stream_parsing(self):
        csv_content = "day,cases\n1,10\n2,25\n3,70\n4,180\n5,420\n"
        df, errors = parse_and_validate_historical_csv(csv_content)
        assert len(errors) == 0
        assert df is not None
        assert len(df) == 5
        assert list(df.columns) == ["day", "cases"]
        assert df["cases"].iloc[-1] == 420

    def test_missing_day_column_rejected(self):
        csv_content = "date_invalid,cases\n1,10\n2,25\n"
        df, errors = parse_and_validate_historical_csv(csv_content)
        assert df is None
        assert any("missing" in e.lower() for e in errors)

    def test_missing_cases_column_rejected(self):
        csv_content = "day,infections_invalid\n1,10\n2,25\n"
        df, errors = parse_and_validate_historical_csv(csv_content)
        assert df is None
        assert any("missing" in e.lower() for e in errors)

    def test_negative_cases_rejected(self):
        csv_content = "day,cases\n1,10\n2,-5\n3,30\n"
        df, errors = parse_and_validate_historical_csv(csv_content)
        assert df is None
        assert any("negative" in e.lower() for e in errors)

    def test_empty_csv_rejected(self):
        df, errors = parse_and_validate_historical_csv("")
        assert df is None
        assert any("empty" in e.lower() for e in errors)

    def test_duplicate_days_rejected(self):
        csv_content = "day,cases\n1,10\n2,20\n2,25\n3,40\n"
        df, errors = parse_and_validate_historical_csv(csv_content)
        assert df is None
        assert any("duplicate" in e.lower() or "monotonic" in e.lower() for e in errors)

    def test_unsorted_days_rejected(self):
        csv_content = "day,cases\n1,10\n3,40\n2,25\n"
        df, errors = parse_and_validate_historical_csv(csv_content)
        assert df is None
        assert any("monotonic" in e.lower() or "chronological" in e.lower() for e in errors)

    def test_error_metrics_computation(self):
        params = SIRParameters(
            total_population=10000.0,
            initial_infected=10.0,
            initial_recovered=0.0,
            transmission_rate=0.30,
            recovery_rate=0.10,
            duration_days=50.0,
            num_points=100,
        )
        res = solve_sir(params)
        eval_df = pd.DataFrame({"day": [10.0, 20.0, 30.0], "cases": [50.0, 300.0, 1500.0]})
        metrics = compute_model_fit_metrics(res, eval_df)

        assert "mae" in metrics
        assert "rmse" in metrics
        assert "mape" in metrics
        assert metrics["mae"] >= 0.0
        assert metrics["rmse"] >= metrics["mae"]
        assert metrics["mape"] >= 0.0
