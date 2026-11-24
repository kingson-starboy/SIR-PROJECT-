# EpiSim Pro: Academic Project Report Suite
## Disease Spread Prediction and Simulation System Using SIR Differential Equations

---

### Executive Overview

This directory contains the complete visual academic project report suite for **EpiSim Pro** (Disease Spread Prediction and Simulation System Using SIR Differential Equations). The documentation has been created to provide an exhaustive, college-level technical reference and viva voce defense resource suitable for mini-project evaluations, academic defense juries, and software engineering audits.

---

### Deliverable Files

| File Name | Format | Size | Description |
| :--- | :--- | :--- | :--- |
| **`Disease_Spread_Prediction_Complete_Visual_Project_Report.pdf`** | PDF (A4) | ~2.6 MB | 20-Page complete academic project report with two-pass dynamic headers/footers (`Page X of Y`), formal cover page, TOC, mathematical proofs, embedded illustrations, bug audit logs, and 30 viva questions. |
| **`Disease_Spread_Prediction_Visual_Report.docx`** | Microsoft Word (.docx) | ~2.5 MB | Fully editable companion document mirroring all 20 chapters, comparative tables, viva Q&As, and embedded 300 DPI figures for customized institutional submissions. |
| **`report_illustrations/`** | Directory (PNG) | 16 Files | High-resolution standalone scientific figures and real application screenshots at 300 DPI. |
| **`generate_complete_visual_report.py`** | Python Script | ~34 KB | Automated script to compile the complete academic PDF using ReportLab with custom flowables and two-pass canvas. |
| **`generate_docx_report.py`** | Python Script | ~21 KB | Automated script to compile the Word document using `python-docx`. |
| **`generate_illustrations.py`** | Python Script | ~20 KB | Automated scientific illustration generator using Matplotlib, NumPy, and SciPy. |

---

### Structure of the 20-Chapter Academic Report

1. **Chapter 1: Executive Summary & Project Abstract**  
   Clinical motivation, high-level objectives, mathematical guarantees, and architectural overview.
2. **Chapter 2: Introduction, Clinical Motivation & Background**  
   Epidemiological challenges, non-pharmaceutical interventions (NPIs), and clinical resource management.
3. **Chapter 3: Mathematical Foundations of the SIR Compartmental Model**  
   Kermack-McKendrick non-linear ordinary differential equations, contact rate physics, mass conservation theorem, and basic reproduction number ($R_0$) threshold analysis.
4. **Chapter 4: System Architecture & Modular Decoupling**  
   Clean Architecture principles, presentation/computation/export decoupling, and data flow pipelines.
5. **Chapter 5: Numerical Solver Implementation (SciPy RK45 vs Euler)**  
   Dormand-Prince adaptive Runge-Kutta order 4(5) solver analysis, local truncation error $O(h^5)$, and numerical stability comparison.
6. **Chapter 6: User Interface Architecture & Design Systems**  
   Enterprise Slate & Modern Blue design tokens, WCAG 2.1 AA accessibility compliance, and CSS layout grids.
7. **Chapter 7: Feature Walkthrough: Interactive Simulation Dashboard**  
   Interactive parameter controls ($\beta, \gamma, N, I_0, t$), KPI status badges, multi-tab layout, and timeline scrubbers.
8. **Chapter 8: Feature Walkthrough: Dual-Scenario Comparison Engine**  
   Baseline vs. Intervention comparative analysis, 4 Delta KPI impact cards, and the "flatten the curve" visualization.
9. **Chapter 9: Feature Walkthrough: Data Export, Audit Logging & PDF Reports**  
   RFC-4180 compliant CSV export, complete JSON run parameter manifests, vector PNG chart downloads, and automated PDF clinical summaries.
10. **Chapter 10: Mathematical Validation & Conservation Law Verification**  
    Automated numerical invariant checks: population invariance $|S+I+R-N|/N < 10^{-6}$, monotonicity bounds, and critical peak nullcline $S^* = N/R_0$.
11. **Chapter 11: Phase Space Orbit, Equilibrium Points & Sensitivity Analysis**  
    Autonomous vector fields in $(S, I)$ phase space, analytical trajectory equation $I(S)$, and 2D parameter sensitivity heatmaps.
12. **Chapter 12: Extended Epidemiological Models (SIRV, SEIR & Spatial Grid)**  
    Architectural blueprint for active immunization (SIRV), latent incubation periods (SEIR), and multi-patch commuter metapopulations.
13. **Chapter 13: Software Quality Assurance & 11-Tier Testing Framework**  
    11-tier testing pyramid comprising 146 automated Pytest tests passing at 100% in 1.41s, with 0 Ruff linter errors.
14. **Chapter 14: Bug Identification, Root Cause Analysis & Resolution Log**  
    Comprehensive post-mortem and audit resolution matrix of 8 identified and patched software defects (BUG-01 to BUG-08).
15. **Chapter 15: Accessibility, Contrast & Responsive UI Compliance**  
    WCAG 2.1 AA color contrast compliance (>7.8:1), keyboard focus navigation, and dual-coded visual encodings.
16. **Chapter 16: Performance Optimization, Caching & Scalability**  
    Vectorized NumPy execution (<5ms RK45 execution time), Streamlit `@st.cache_data` parameter hashing, and WebGL rendering.
17. **Chapter 17: User Manual & Step-by-Step Operator Guide**  
    End-to-end user operational workflow: parameterization, threshold monitoring, policy testing, and data export.
18. **Chapter 18: Project Installation, Configuration & Deployment Guide**  
    Local virtual environment setup, dependency management, CLI verification, and cloud containerization instructions.
19. **Chapter 19: Comprehensive Viva Voce Preparation Guide (30 Questions & Answers)**  
    30 rigorous examiner questions and answers covering ODE theory, numerical algorithms, software architecture, and public health policy.
20. **Chapter 20: 5-Minute Project Defense Presentation Script & References**  
    A structured, 5-minute minute-by-minute oral defense script paired with primary academic citations.

---

### Inventory of Embedded Figures & Screenshots

All figures are stored in `report_illustrations/`:

| Figure ID | File Name | Description |
| :--- | :--- | :--- |
| **Fig 1.1** | `fig_01_sir_compartment_flow.png` | SIR Compartmental Flow Model & Mass Conservation Flux |
| **Fig 2.1** | `fig_02_problem_solution.png` | Computational Bridge from Clinical Challenge to Epidemic Control Architecture |
| **Fig 3.1** | `fig_03_equation_breakdown.png` | Mathematical Decomposition of Kermack-McKendrick Differential System |
| **Fig 3.2** | `fig_04_r0_threshold.png` | Basic Reproduction Number ($R_0$) Spectrum & Herd Immunity Threshold Transition |
| **Fig 4.1** | `fig_05_technology_architecture.png` | Decoupled Multi-Layer Technology Architecture |
| **Fig 4.2** | `fig_06_system_architecture.png` | Data Flow and Component Interaction Pipeline |
| **Fig 5.1** | `fig_08_sample_sir_simulation.png` | High-Precision RK45 Trajectory Benchmark ($N=10k, R_0=3.00, \text{Peak}=38.6\text{d}$) |
| **Fig 6.1** | `screenshot_01_dashboard.png` | Real Web Application Dashboard with 4 KPI Metric Badges & SIR Curves |
| **Fig 7.1** | `screenshot_02_tab4_distribution_scrubber.png` | Tab 4 Population Distribution Donut and Interactive Day Scrubber |
| **Fig 8.1** | `screenshot_03_scenario_comparison.png` | Dual-Scenario Comparison View with 4 Delta Impact Metrics |
| **Fig 8.2** | `fig_09_scenario_comparison.png` | Flattening the Curve: Benchmark Comparative Trajectories (Baseline vs Policy) |
| **Fig 9.1** | `screenshot_04_data_and_reports.png` | Tab 5 Data & Reports View with 4 Standardized Export Action Triggers |
| **Fig 10.1** | `fig_10_phase_space_nullcline.png` | Phase Space Orbit ($S$ vs $I$) with Critical Peak Nullcline $S^* = N/R_0$ |
| **Fig 11.1** | `fig_11_parameter_sensitivity.png` | 2D Parameter Sensitivity Heatmap of Peak Infection Burden Across $\beta$ and $\gamma$ |
| **Fig 12.1** | `fig_12_extended_sirv_model.png` | Extended Compartmental Flow Architecture: SIRV Model with Active Immunization |
| **Fig 13.1** | `fig_13_testing_workflow.png` | 11-Tier Testing Pyramid & Automated Quality Assurance Pipeline |

---

### How to Regenerate Reports

To recompile the figures and reports from source at any time:

```bash
# 1. Activate the Python virtual environment
source venv/bin/activate

# 2. Re-generate all high-resolution scientific figures (300 DPI)
python generate_illustrations.py

# 3. Re-compile the 20-page Academic Project Report PDF
python generate_complete_visual_report.py

# 4. Re-compile the editable Microsoft Word Report (.docx)
python generate_docx_report.py
```
