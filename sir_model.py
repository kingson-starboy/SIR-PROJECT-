"""SIR Epidemic Model - Mathematical Formulation and Numerical Solver.

This module implements the classic Kermack-McKendrick Susceptible-Infected-Recovered
(SIR) compartmental differential equation system using SciPy's numerical ODE solver.

Ordinary Differential Equations:
    dS/dt = - beta * (S * I) / N
    dI/dt =   beta * (S * I) / N - gamma * I
    dR/dt =   gamma * I

Conservation Law:
    S(t) + I(t) + R(t) = N for all t >= 0
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp


class SolverError(Exception):
    """Raised when numerical integration fails or diverges."""

    pass


@dataclass(frozen=True)
class SIRParameters:
    """Input parameters for the SIR differential equation model."""

    total_population: float
    initial_infected: float
    initial_recovered: float
    transmission_rate: float  # beta
    recovery_rate: float  # gamma
    duration_days: float
    num_points: int = 1000
    intervention_day: float | None = None
    intervention_beta_reduction: float = 0.0  # fraction, e.g. 0.40 = 40% reduction
    vaccination_rate: float = 0.0  # daily fraction of susceptible population vaccinated (nu)

    @property
    def initial_susceptible(self) -> float:
        """S(0) = N - I(0) - R(0)."""
        return self.total_population - self.initial_infected - self.initial_recovered

    def to_dict(self) -> dict:
        """Convert parameters to dictionary."""
        data = asdict(self)
        data["initial_susceptible"] = self.initial_susceptible
        return data


@dataclass
class SIRSimulationResult:
    """Encapsulates the numerical simulation solution and diagnostics."""

    t: np.ndarray
    S: np.ndarray
    I: np.ndarray
    R: np.ndarray
    N: float
    parameters: SIRParameters
    success: bool
    message: str
    max_conservation_error: float
    solver_method: str = "RK45"

    def to_dataframe(self) -> pd.DataFrame:
        """Export simulation trajectory as a pandas DataFrame."""
        return pd.DataFrame(
            {
                "day": np.round(self.t, 4),
                "susceptible": self.S,
                "infected": self.I,
                "recovered": self.R,
                "total_population": self.S + self.I + self.R,
            }
        )


def sir_derivatives(
    t: float,
    y: list[float] | np.ndarray,
    beta: float,
    gamma: float,
    N: float,
    intervention_day: float | None = None,
    intervention_beta_reduction: float = 0.0,
    vaccination_rate: float = 0.0,
) -> list[float]:
    """Compute the time derivatives for the SIR compartmental system.

    Parameters
    ----------
    t : float
        Current time (days).
    y : list[float] | np.ndarray
        Current state vector [S, I, R].
    beta : float
        Baseline transmission rate (effective contact rate per day).
    gamma : float
        Recovery rate (fraction of infected individuals recovering per day).
    N : float
        Total population size.
    intervention_day : float | None, optional
        Day on which a policy intervention starts (lockdown, masks, distancing).
    intervention_beta_reduction : float, optional
        Fractional reduction in beta after intervention_day (0.0 to 1.0).
    vaccination_rate : float, optional
        Fraction of susceptible hosts vaccinated per day (nu), transferring directly from S to R.

    Returns
    -------
    list[float]
        Time derivatives [dS/dt, dI/dt, dR/dt].
    """
    S, I, R = y

    # Boundary protection: if population compartments are zero or negative,
    # prevent spurious negative flux
    S_eff = max(0.0, float(S))
    I_eff = max(0.0, float(I))

    if N <= 0:
        return [0.0, 0.0, 0.0]

    # Staged intervention: dampen beta if t >= intervention_day
    if intervention_day is not None and t >= intervention_day:
        effective_beta = max(0.0, beta * (1.0 - intervention_beta_reduction))
    else:
        effective_beta = beta

    # Standard bilinear incidence rate (beta(t) * S * I / N)
    transmission_flux = effective_beta * (S_eff * I_eff) / N
    recovery_flux = gamma * I_eff
    vaccination_flux = max(0.0, vaccination_rate * S_eff)

    dSdt = -transmission_flux - vaccination_flux
    dIdt = transmission_flux - recovery_flux
    dRdt = recovery_flux + vaccination_flux

    return [dSdt, dIdt, dRdt]


def solve_sir(
    params: SIRParameters,
    method: str = "RK45",
    rtol: float = 1e-7,
    atol: float = 1e-9,
) -> SIRSimulationResult:
    """Solve the SIR differential equations numerically using SciPy's solve_ivp.

    Parameters
    ----------
    params : SIRParameters
        Configuration containing population, rates, and duration.
    method : str, default 'RK45'
        Explicit Runge-Kutta method of order 5(4).
    rtol : float, default 1e-7
        Relative tolerance for the solver.
    atol : float, default 1e-9
        Absolute tolerance for the solver.

    Returns
    -------
    SIRSimulationResult
        Contains time points, population trajectories, and convergence diagnostics.

    Raises
    ------
    ValueError
        If initial conditions or parameters violate mathematical constraints.
    SolverError
        If numerical integration fails or violates conservation beyond tolerance.
    """
    # Strict validation of fundamental physical bounds
    if params.total_population <= 0:
        raise ValueError("Total population N must be strictly positive.")
    if params.initial_infected < 0:
        raise ValueError("Initial infected population cannot be negative.")
    if params.initial_recovered < 0:
        raise ValueError("Initial recovered population cannot be negative.")
    if params.initial_susceptible < 0:
        raise ValueError(
            f"Initial susceptible population S(0) = {params.initial_susceptible:.2f} "
            f"cannot be negative. I(0) + R(0) exceeds total population N."
        )
    if params.transmission_rate < 0:
        raise ValueError("Transmission rate beta must be non-negative.")
    if params.recovery_rate < 0:
        raise ValueError("Recovery rate gamma must be non-negative.")
    if params.duration_days <= 0:
        raise ValueError("Simulation duration must be strictly positive.")
    if params.num_points < 2:
        raise ValueError("Number of evaluation points must be at least 2.")

    y0 = [params.initial_susceptible, params.initial_infected, params.initial_recovered]
    t_span = (0.0, float(params.duration_days))
    t_eval = np.linspace(0.0, float(params.duration_days), params.num_points)

    # Edge case: No infections present initially
    # Analytical solution is constant: S(t) = S0, I(t) = 0, R(t) = R0
    if params.initial_infected == 0.0:
        S = np.full_like(t_eval, params.initial_susceptible, dtype=float)
        I = np.zeros_like(t_eval, dtype=float)
        R = np.full_like(t_eval, params.initial_recovered, dtype=float)
        return SIRSimulationResult(
            t=t_eval,
            S=S,
            I=I,
            R=R,
            N=params.total_population,
            parameters=params,
            success=True,
            message="Zero initial infections; system remained in static equilibrium.",
            max_conservation_error=0.0,
            solver_method=method,
        )

    # Solve the system of ODEs
    sol = solve_ivp(
        fun=lambda t, y: sir_derivatives(
            t,
            y,
            params.transmission_rate,
            params.recovery_rate,
            params.total_population,
            params.intervention_day,
            params.intervention_beta_reduction,
            params.vaccination_rate,
        ),
        t_span=t_span,
        y0=y0,
        t_eval=t_eval,
        method=method,
        rtol=rtol,
        atol=atol,
    )

    if not sol.success:
        raise SolverError(f"Numerical integration failed: {sol.message}")

    S_raw = sol.y[0]
    I_raw = sol.y[1]
    R_raw = sol.y[2]

    # Verify conservation of mass: S(t) + I(t) + R(t) == N
    total_trajectory = S_raw + I_raw + R_raw
    conservation_errors = np.abs(total_trajectory - params.total_population)
    max_conservation_error = float(np.max(conservation_errors))
    relative_conservation_error = max_conservation_error / params.total_population

    # Numerical tolerance check: relative conservation must not exceed 0.1%
    if relative_conservation_error > 1e-3:
        raise SolverError(
            f"Numerical conservation violated: max discrepancy is {max_conservation_error:.4e} "
            f"({relative_conservation_error * 100:.3f}% of total population)."
        )

    # Clean up minor floating-point solver residuals (< 1e-10) without distorting mathematics
    S_clean = np.maximum(0.0, S_raw)
    I_clean = np.maximum(0.0, I_raw)
    R_clean = np.maximum(0.0, R_raw)

    # Normalize gently to preserve exact population conservation S + I + R = N
    sum_clean = S_clean + I_clean + R_clean
    nonzero_mask = sum_clean > 0
    scale = np.ones_like(sum_clean)
    scale[nonzero_mask] = params.total_population / sum_clean[nonzero_mask]

    S_final = S_clean * scale
    I_final = I_clean * scale
    R_final = R_clean * scale

    return SIRSimulationResult(
        t=sol.t,
        S=S_final,
        I=I_final,
        R=R_final,
        N=params.total_population,
        parameters=params,
        success=True,
        message=sol.message or "Numerical integration completed successfully.",
        max_conservation_error=max_conservation_error,
        solver_method=method,
    )
