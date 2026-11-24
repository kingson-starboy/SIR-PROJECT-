# Disease Spread Prediction and Simulation System Using SIR Differential Equations

An applied numerical computing and mathematical epidemiology simulation platform engineered for rigorous modeling of non-linear contagion dynamics using **Ordinary Differential Equations (ODEs)** and adaptive **Runge-Kutta 5(4)** numerical integration.

---

## 1. Project Overview

The **Disease Spread Prediction and Simulation System** models how infectious pathogens propagate through a host population over time. By translating biological transmission mechanisms into a system of coupled, non-linear ordinary differential equations (the Kermack-McKendrick SIR model), the system computes continuous population trajectories, identifies infection peaks, evaluates intervention scenarios, and computes key epidemiological indicators including the Basic Reproduction Number ($R_0$) and the time-dependent Effective Reproduction Number ($R_e(t)$).

The entire application runs locally, requires no external cloud APIs or database subscriptions, and provides interactive, publication-quality Plotly visualizations within a clean Streamlit interface.

---

## 2. Problem Statement

Predicting the trajectory of an infectious disease outbreak is critical for public health planning, hospital capacity allocation, and the design of non-pharmaceutical interventions (such as social distancing and quarantine). 

However, epidemic spread is inherently non-linear: each infected individual can interact with multiple susceptible hosts, creating exponential initial growth that saturates only as the pool of susceptible individuals is depleted. Closed-form algebraic solutions do not exist for the non-linear SIR system. This project demonstrates how numerical integration methods (specifically, adaptive Runge-Kutta 5(4)) solve these differential equations deterministically, stably, and accurately.

---

## 3. Project Objectives

- **Mathematical Rigor:** Implement the Kermack-McKendrick continuous differential equations using numerical integration (`scipy.integrate.solve_ivp` with RK45) rather than arbitrary curve fitting.
- **Population Conservation:** Enforce and verify the conservation of total population ($S(t) + I(t) + R(t) = N$) to within machine floating-point tolerance ($< 10^{-11}$).
- **Epidemiological Analysis:** Automatically calculate $R_0$, $R_e(t)$, peak infection burden, peak infection day, herd immunity thresholds, and final attack rates.
- **Intervention Modeling:** Enable side-by-side scenario comparison (e.g., baseline vs. social distancing or antiviral treatments).
- **Academic Demonstration:** Offer a dedicated educational module explaining the derivation, threshold theorems, and physical intuition of the differential equations for classroom presentation.
- **Open Data & Reproducibility:** Support one-click CSV export of raw numerical trajectory channels and formal academic Markdown summary reports.

---

## 4. Mathematical Background & SIR Differential Equations

The population of total size $N$ is partitioned into three mutually exclusive compartments:

- **$S(t)$ — Susceptible:** Individuals currently healthy but vulnerable to contracting the infection upon contact with an infectious host.
- **$I(t)$ — Infected:** Individuals actively harboring the pathogen who can transmit it to susceptible individuals.
- **$R(t)$ — Recovered:** Individuals who have cleared the infection, are no longer infectious, and possess protective immunity.

### The Differential Equation System

$$\frac{dS}{dt} = -\beta \frac{S(t) \cdot I(t)}{N}$$

$$\frac{dI}{dt} = \beta \frac{S(t) \cdot I(t)}{N} - \gamma I(t)$$

$$\frac{dR}{dt} = \gamma I(t)$$

### Population Conservation Law

Summing the three derivatives yields:

$$\frac{dN}{dt} = \frac{dS}{dt} + \frac{dI}{dt} + \frac{dR}{dt} = -\beta \frac{SI}{N} + \left(\beta \frac{SI}{N} - \gamma I\right) + \gamma I = 0$$

Since $\frac{dN}{dt} = 0$, the total population remains strictly invariant:

$$S(t) + I(t) + R(t) = N \quad \forall t \ge 0$$

### Initial Conditions

$$S(0) = N - I(0) - R(0)$$

$$I(0) \ge 0, \quad R(0) \ge 0$$

---

## 5. Model Parameters & Epidemiological Metrics

| Parameter / Metric | Symbol | Mathematical Definition | Physical Meaning |
| :--- | :---: | :--- | :--- |
| **Transmission Rate** | $\beta$ | Contact rate $\times$ transmission probability | Effective contact rate per individual per day. |
| **Recovery Rate** | $\gamma$ | $1 / \text{infectious duration}$ | Fraction of infected individuals recovering each day. |
| **Basic Reproduction Number** | $R_0$ | $R_0 = \frac{\beta}{\gamma}$ | Average number of secondary cases produced by one infectious case in a fully susceptible population. |
| **Effective Reproduction Number** | $R_e(t)$ | $R_e(t) = R_0 \cdot \frac{S(t)}{N}$ | Real-time reproduction number as susceptible individuals are depleted. |
| **Infection Crest Condition** | — | $\frac{dI}{dt} = 0 \iff R_e(t) = 1.0$ | Peak infection occurs when the susceptible fraction drops to $1 / R_0$. |
| **Herd Immunity Threshold** | $HIT$ | $1 - \frac{1}{R_0}$ | Fraction of immune population required to prevent sustained epidemic growth. |
| **Total Attack Rate** | — | $\frac{N - S_{\text{final}}}{N} \times 100\%$ | Cumulative proportion of the population that contracted the disease. |

---

## 6. Technology Stack

- **Core Language:** Python 3.9+ / 3.11
- **Web UI & Dashboard:** Streamlit (>= 1.30.0)
- **Mathematical Computation & ODE Solver:** SciPy (`scipy.integrate.solve_ivp`, RK45)
- **Numerical Arrays:** NumPy (>= 1.23.0)
- **Tabular Data Structures:** Pandas (>= 2.0.0)
- **Interactive Visualizations:** Plotly Graph Objects (>= 5.18.0)
- **Automated Unit Testing:** Pytest (>= 7.4.0)
- **Code Quality & Formatting:** Ruff (>= 0.3.0)

---

## 7. Application Architecture

```
SIR-PROJECT/
│
├── app.py                  # Main Streamlit web application and navigation
├── sir_model.py            # ODE formulation and SciPy numerical solver engine
├── analysis.py             # Epidemiological metrics, R0, Re(t), peak detection
├── visualization.py        # Interactive Plotly figures (SIR curves, donut, Re)
├── validation.py           # Robust input validation and boundary constraint checking
├── export.py               # CSV export and academic Markdown summary report generator
│
├── requirements.txt        # Pinned, tested Python package dependencies
├── pyproject.toml          # Tool configuration for Ruff linter and Pytest
├── README.md               # Detailed academic project documentation
├── .gitignore              # Git exclusions for Python artifacts and venv
│
└── tests/                  # Automated verification test suite (30 passing tests)
    ├── test_sir_model.py   # Solver convergence, conservation law, boundary tests
    ├── test_validation.py  # Input parameter checks and constraint enforcement
    ├── test_analysis.py    # R0, Re(t), peak detection, trend classifications
    └── test_export.py      # CSV and Markdown serialization validation
```

---

## 8. Application Modules & Features

1. **Main Overview Dashboard:** Comprehensive executive summary, compartmental explanation, and model equations.
2. **Simulation Engine:**
   - Sliders and numeric inputs for $N$, $I(0)$, $R(0)$, $\beta$, $\gamma$, duration, and output resolution.
   - Built-in educational presets:
     - *Moderate Transmission (Default)*: $\beta = 0.30, \gamma = 0.10 \implies R_0 = 3.00$
     - *Low Transmission (Controlled)*: $\beta = 0.15, \gamma = 0.10 \implies R_0 = 1.50$
     - *High Transmission (Uncontrolled)*: $\beta = 0.50, \gamma = 0.10 \implies R_0 = 5.00$
     - *Fast Recovery*: $\beta = 0.30, \gamma = 0.20 \implies R_0 = 1.50$
     - *Slow Recovery*: $\beta = 0.30, \gamma = 0.05 \implies R_0 = 6.00$
   - Real-time numerical solver execution with conservation diagnostics.
3. **Interactive Trajectory Charts:**
   - **Chart 1:** Full SIR Population Curves ($S$, $I$, $R$ vs. time).
   - **Chart 2:** Peak Infection Dynamics with coordinate markers and clearance threshold lines.
   - **Chart 3:** Final Outbreak Population Distribution (Donut chart).
   - **Chart 4:** Growth Rate Trend ($dI/dt$) showing epidemic expansion and contraction phases.
   - **Chart 5:** Time-varying Effective Reproduction Number $R_e(t)$ with critical threshold line ($R_e = 1.0$).
4. **Scenario Comparison:**
   - Compare two distinct scenarios side-by-side (e.g., baseline vs. social distancing).
   - Comparative dual-trace Plotly chart and structured impact difference table.
5. **Mathematical Foundations Section:**
   - Derivation of the differential equations, explanation of non-linear mass action, population invariance proof, and RK45 Runge-Kutta numerical solver details.
6. **Data Export & Reports:**
   - One-click CSV download (`disease_simulation_results.csv`).
   - One-click formal academic Markdown summary report (`simulation_summary_report.md`).
   - Paginated preview of the first 20 evaluation steps.

---

## 9. Installation & Setup Instructions

### Prerequisites
- Python 3.9, 3.10, 3.11, or 3.12 installed on macOS, Linux, or Windows.

### Step 1: Clone or Navigate to the Project Directory
```bash
cd "SIR PROJECT"
```

### Step 2: Create a Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt / PowerShell)
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 10. Execution Instructions

Launch the Streamlit web application:

```bash
streamlit run app.py
```

Open your browser at:
```
http://localhost:8501
```

---

## 11. Automated Testing Instructions

The project includes an automated Pytest test suite covering 30 test cases across numerical accuracy, conservation laws, boundary conditions, and export formats:

```bash
# Run the test suite with verbose output
pytest -v

# Run code style and linting verification
ruff check .
```

### Test Coverage Highlights:
- Population conservation verified across diverse parameter spaces ($\Delta < 10^{-11}$).
- Zero initial infections ($I_0 = 0$) and zero transmission ($\beta = 0$) static equilibrium tests.
- Zero recovery ($\gamma = 0$) division-by-zero protection.
- High-transmission and high-recovery boundary stability.
- Input validation rejection of negative counts, out-of-range bounds, and impossible initial conditions.
- CSV and Markdown serialization integrity.

---

## 12. Sample Simulation Walkthrough

**Configuration:**
- Total Population ($N$): `10,000`
- Initial Infected ($I_0$): `10`
- Initial Recovered ($R_0$): `0`
- Initial Susceptible ($S_0$): `9,990`
- Transmission Rate ($\beta$): `0.30`
- Recovery Rate ($\gamma$): `0.10`
- Duration: `160 days`

**Results Computed by Solver:**
- Basic Reproduction Number ($R_0$): `3.00`
- Peak Infection Burden: `3,008` active cases (`30.08%` of population)
- Peak Infection Day: `Day 38.6`
- Final Susceptible ($S_{\text{final}}$): `595` (`5.95%`)
- Total Affected Population: `9,405` (`94.05%`)
- Maximum Numerical Conservation Error: `5.45 × 10⁻¹²` individuals

---

## 13. Model Assumptions and Limitations

1. **Closed Population:** Assumes no demographic vital dynamics (births and natural mortality rates are zero).
2. **Homogeneous Mixing:** Assumes uniform, well-mixed contact probabilities between all individuals in the population.
3. **Instantaneous Immunity:** Assumes recovered individuals immediately develop durable immunity without reinfection.
4. **Time-Invariant Parameters:** Transmission rate $\beta$ and recovery rate $\gamma$ are held constant throughout a given simulation run.
5. **Deterministic Framework:** Uses continuous differential equations; stochastic fluctuations in very small cohorts ($N < 50$) are not modeled.

> **Clinical & Policy Notice:** This platform implements continuous deterministic compartmental modeling. While calibrated against classic epidemiological dynamics, operational deployments should complement continuous ODE projections with agent-based and geospatial contact network analysis.

---

## 14. Extensibility Architecture

The modular architecture was specifically engineered to allow immediate extensions:
- **SEIR Model:** Introduction of an Exposed compartment ($E$) with incubation rate $\sigma$.
- **Vaccination Dynamics:** Continuous and pulsed vaccination rate terms $\nu(t)$.
- **Time-Dependent Transmission:** Piecewise functions $\beta(t)$ representing staged government lockdowns and mobility restrictions.
- **Vital Dynamics:** Birth rate $\mu$ and disease-induced mortality rate $\alpha$.
- **Automated Reporting:** High-throughput JSON / CSV telemetry export for clinical dashboards.

---

## 15. Operational Summary

Engineered for **Ordinary Differential Equations & Computational Numerical Systems**, demonstrating the direct bridge between continuous non-linear differential systems and operational epidemic risk management.
