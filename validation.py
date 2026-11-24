"""Input Validation for SIR Simulation Parameters.

Validates user-provided epidemiological parameters before numerical integration
to prevent mathematical instabilities, physical impossibilities, and solver crashes.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Encapsulates validation outcome, errors, and advisory warnings."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Register a fatal validation error."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Register an advisory notice that does not block execution."""
        self.warnings.append(message)


def validate_sir_inputs(
    total_population: float,
    initial_infected: float,
    initial_recovered: float,
    transmission_rate: float,
    recovery_rate: float,
    duration_days: float,
    num_points: int = 1000,
) -> ValidationResult:
    """Validate all user inputs for the SIR model against biological and mathematical constraints.

    Parameters
    ----------
    total_population : float
        Total size of the community (N).
    initial_infected : float
        Active infections at t=0 (I_0).
    initial_recovered : float
        Individuals already immune or recovered at t=0 (R_0).
    transmission_rate : float
        Effective contact/transmission rate beta.
    recovery_rate : float
        Daily recovery rate gamma.
    duration_days : float
        Total simulation timespan in days.
    num_points : int, default 1000
        Number of discrete time grid points.

    Returns
    -------
    ValidationResult
        Status flag along with specific error or warning strings.
    """
    result = ValidationResult(is_valid=True)

    # 1. Total Population Validation
    if total_population is None:
        result.add_error("Total population must be specified.")
    elif total_population <= 0:
        result.add_error(f"Total population must be strictly greater than 0 (received: {total_population}).")
    elif total_population < 10:
        result.add_warning(
            f"Total population ({total_population:,.0f}) is very small for a continuous "
            "compartmental ODE model. Differential equations assume large, well-mixed populations."
        )

    # 2. Initial Compartments
    if initial_infected is None:
        result.add_error("Initial infected count must be specified.")
    elif initial_infected < 0:
        result.add_error(f"Initial infected population cannot be negative (received: {initial_infected}).")

    if initial_recovered is None:
        result.add_error("Initial recovered count must be specified.")
    elif initial_recovered < 0:
        result.add_error(f"Initial recovered population cannot be negative (received: {initial_recovered}).")

    # Relational boundary checks (only if N and compartments are non-negative)
    if (
        total_population is not None
        and total_population > 0
        and initial_infected is not None
        and initial_infected >= 0
        and initial_recovered is not None
        and initial_recovered >= 0
    ):
        if initial_infected > total_population:
            result.add_error(
                f"Initial infected ({initial_infected:,.0f}) cannot exceed total population "
                f"({total_population:,.0f})."
            )

        if initial_recovered > total_population:
            result.add_error(
                f"Initial recovered ({initial_recovered:,.0f}) cannot exceed total population "
                f"({total_population:,.0f})."
            )

        combined_init = initial_infected + initial_recovered
        if combined_init > total_population:
            result.add_error(
                f"Initial infected ({initial_infected:,.0f}) + initial recovered "
                f"({initial_recovered:,.0f}) = {combined_init:,.0f}, which exceeds total population "
                f"({total_population:,.0f}). Initial susceptible would be negative."
            )
        elif initial_infected == 0:
            result.add_warning(
                "Initial infected population is 0. With no seed infections, the epidemic cannot spread."
            )

    # 3. Rate Parameters (Beta and Gamma)
    if transmission_rate is None:
        result.add_error("Transmission rate (beta) must be specified.")
    elif transmission_rate < 0:
        result.add_error(f"Transmission rate (beta) cannot be negative (received: {transmission_rate}).")
    elif transmission_rate > 5.0:
        result.add_warning(
            f"Transmission rate beta={transmission_rate:.2f} is exceptionally high. "
            "Typical respiratory diseases have beta between 0.1 and 1.5."
        )

    if recovery_rate is None:
        result.add_error("Recovery rate (gamma) must be specified.")
    elif recovery_rate < 0:
        result.add_error(f"Recovery rate (gamma) cannot be negative (received: {recovery_rate}).")
    elif recovery_rate == 0:
        result.add_warning(
            "Recovery rate gamma is 0. Infected individuals will never recover, meaning "
            "R0 is formally infinite/undefined."
        )
    elif recovery_rate > 2.0:
        result.add_warning(
            f"Recovery rate gamma={recovery_rate:.2f} corresponds to an average infectious "
            f"period of only {1.0 / recovery_rate:.2f} days."
        )

    # 4. Simulation Duration & Resolution
    if duration_days is None:
        result.add_error("Simulation duration must be specified.")
    elif duration_days <= 0:
        result.add_error(
            f"Simulation duration must be strictly greater than 0 days (received: {duration_days})."
        )
    elif duration_days > 3650:
        result.add_error(
            f"Simulation duration ({duration_days} days) exceeds maximum allowed limit of 3,650 days (10 years)."
        )

    if num_points is None:
        result.add_error("Evaluation resolution (num_points) must be specified.")
    elif num_points < 10:
        result.add_error(
            f"Evaluation resolution must have at least 10 points for reliable numerical curves (received: {num_points})."
        )
    elif num_points > 10000:
        result.add_error(
            f"Evaluation resolution ({num_points}) exceeds maximum allowed limit of 10,000 points."
        )

    return result
