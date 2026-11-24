"""Unit and Integration Tests for Application Startup, Dependencies, and Module Integrity."""

import importlib
import sys
from pathlib import Path

import pytest


class TestApplicationStartup:
    """Validate system bootstrapping, dependency availability, and import safety."""

    REQUIRED_MODULES = [
        "numpy",
        "scipy",
        "pandas",
        "plotly",
        "streamlit",
        "reportlab",
        "sir_model",
        "analysis",
        "visualization",
        "validation",
        "export",
    ]

    @pytest.mark.parametrize("module_name", REQUIRED_MODULES)
    def test_module_imports_without_exception(self, module_name: str):
        """Ensure all core architectural dependencies and application modules import cleanly."""
        mod = importlib.import_module(module_name)
        assert mod is not None

    def test_application_entrypoint_exists(self):
        """Verify presence of app.py entry point file."""
        app_path = Path(__file__).resolve().parent.parent / "app.py"
        assert app_path.exists()
        assert app_path.is_file()
        assert app_path.stat().st_size > 1000

    def test_python_runtime_compatibility(self):
        """Ensure runtime Python version meets project requirements (>= 3.9)."""
        assert sys.version_info.major == 3
        assert sys.version_info.minor >= 9

    def test_dependency_version_bounds(self):
        """Verify installed packages satisfy numerical and plotting compatibility constraints."""
        import numpy as np
        import pandas as pd
        import plotly
        import reportlab
        import scipy

        assert int(np.__version__.split(".")[0]) >= 1
        assert int(scipy.__version__.split(".")[0]) >= 1
        assert int(pd.__version__.split(".")[0]) >= 2
        assert int(plotly.__version__.split(".")[0]) >= 5
        assert int(reportlab.__version__.split(".")[0]) >= 3
