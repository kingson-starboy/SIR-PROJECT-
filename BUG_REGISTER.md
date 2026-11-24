# Bug Register: EpiSim Pro QA & Fix Validation

**System:** Disease Spread Prediction and Simulation System Using SIR Differential Equations  
**Evaluation Period:** November 2026  
**Status:** All Confirmed Defects Fully Resolved & Verified via Automated Regression Suite

---

### Bug Summary Matrix

| Bug ID | Module | Severity | Summary | Root Cause | Fix Applied | Regression Test | Status |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **BUG-01** | `visualization.py` | **CRITICAL** | `TypeError: Layout() got multiple values for keyword argument 'yaxis'` in animated chart | Passing `**CHART_LAYOUT_DEFAULTS` inside `go.Layout(yaxis=...)` conflicted with existing default dictionary key. | Shifted to `fig = go.Figure(...)` followed by `fig.update_layout()` and `fig.update_yaxes()`. | `test_bug_reg_01_no_duplicate_yaxis_in_animated_chart` | ✅ Resolved |
| **BUG-02** | `app.py` | **HIGH** | `TypeError: create_scenario_comparison_chart() takes from 2 to 4 positional arguments but 6 were given` | Call site passed 6 arguments `(r_a, s_a, r_b, s_b, label_a, label_b)` instead of 4 `(r_a, r_b, label_a, label_b)`. | Corrected call signature to pass `(r_a, r_b, "Scenario A", "Scenario B")`. | `test_bug_reg_02_scenario_comparison_chart_parameter_signature` | ✅ Resolved |
| **BUG-03** | `export.py` | **HIGH** | `AttributeError: 'HealthcareCapacityMetrics' object has no attribute 'capacity_threshold'` | Inconsistent attribute access in PDF generation (`capacity_threshold` vs `capacity_limit`). | Updated reference to `summary.capacity.capacity_limit`. | `test_bug_reg_03_healthcare_capacity_attribute_name` | ✅ Resolved |
| **BUG-04** | `analysis.py` | **MEDIUM** | Potential `ZeroDivisionError` when recovery rate $\gamma = 0$ | Direct calculation of $R_0 = \beta / \gamma$ without zero-division guard. | Guarded division: if $\gamma \le 0$, $R_0 = \text{None}$ with explicit status `"Undefined / Infinite"`. | `test_bug_reg_04_zero_recovery_rate_division_by_zero` | ✅ Resolved |
| **BUG-05** | `sir_model.py` | **MEDIUM** | Spurious numerical drift when initial infection $I(0) = 0$ | ODE solver attempting adaptive steps from non-zero tolerances on static equilibrium. | Analytical short-circuit returning static constant arrays $S(t) = S_0, I(t) = 0, R(t) = R_0$. | `test_bug_reg_05_zero_initial_infection_equilibrium` | ✅ Resolved |
| **BUG-06** | `app.py` (UI) | **MEDIUM** | Staggered vertical baseline on KPI metric cards | Unconstrained flex column wrapping and variable title wrap line-counts. | Enforced flex column stretch, standardized `min-height: 126px`, and wrapped badges in fixed containers. | Browser automation geometry check ($y = 256.52\text{ px}$). | ✅ Resolved |
| **BUG-07** | `app.py` (UI) | **LOW** | Cramped number input stepper controls in sidebar | Two `st.number_input` controls packed into narrow columns ($\sim 130\text{ px}$ width). | Migrated to clean, full-width primary steppers and secondary range sliders. | Visual browser verification across viewports. | ✅ Resolved |
| **BUG-08** | `app.py` (UI) | **LOW** | Uneven vertical baseline on Data & Reports download buttons | Differing paragraph line-heights in export description cards. | Configured `.info-card { height: 140px; }` and `.info-card p { min-height: 52px; }`. | Browser automation geometry check ($y = 399.76\text{ px}$). | ✅ Resolved |

---

### Detailed Defect Reports

#### BUG-01: Duplicate Keyword Argument in Animated Progression Chart
- **Severity:** CRITICAL
- **File:** `visualization.py`, Line 341
- **Symptoms:** Streamlit page crash with `TypeError: plotly.graph_objs._layout.Layout() got multiple values for keyword argument 'yaxis'`.
- **Root Cause:** In Python, passing a dictionary unpack `**CHART_LAYOUT_DEFAULTS` (which already defines `yaxis`) inside `go.Layout(..., yaxis=...)` raises a syntax-level runtime error.
- **Verification:** Verified in `tests/test_regression.py::TestRegressionSuite::test_bug_reg_01_no_duplicate_yaxis_in_animated_chart` and live browser inspection.

#### BUG-02: Positional Argument Signature Mismatch in Scenario Comparison Chart
- **Severity:** HIGH
- **File:** `app.py`, Line 987
- **Symptoms:** Tab 6 / Scenario Comparison view failed to render with `TypeError`.
- **Root Cause:** The caller in `app.py` passed both simulation results and summary dataclasses `(r_a, s_a, r_b, s_b, ...)` whereas `create_scenario_comparison_chart` only expects `(res_a, res_b, label_a, label_b)`.
- **Verification:** Verified in `tests/test_regression.py::TestRegressionSuite::test_bug_reg_02_scenario_comparison_chart_parameter_signature`.

#### BUG-03: Attribute Name Discrepancy in Healthcare Surge Dataclass
- **Severity:** HIGH
- **File:** `export.py` & `analysis.py`
- **Symptoms:** PDF generation crashed with `AttributeError`.
- **Root Cause:** In `analysis.py`, the dataclass field was declared as `capacity_limit`, but early PDF generation routines called `summary.capacity.capacity_threshold`.
- **Verification:** Verified in `tests/test_regression.py::TestRegressionSuite::test_bug_reg_03_healthcare_capacity_attribute_name`.
