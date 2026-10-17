"""Model parameters, taken from Vera et al. (2019) unless marked as our assumption."""
from dataclasses import dataclass, field

MMHG = 133.322  # Pa per mmHg
ML = 1e-6       # m^3 per ml


@dataclass
class Params:
    # Blood (paper)
    rho: float = 1050.0          # kg/m^3
    mu: float = 0.004            # Pa s

    # Physics switches
    gravity: bool = False        # paper runs the model with and without gravity
    g: float = 9.81
    friction: str = "womersley"  # "womersley" (paper) or "poiseuille" (simpler)
    womersley_alpha_min: float = 3.0   # paper: Womersley friction where alpha > 3
    n_harmonics: int = 30              # our choice

    # Arterial wall, Eq (3) (paper)
    distensibility_scale: float = 1.0   # multiply every segment's distensibility (e.g. 0.7 = stiffer, older arteries)
    P_ref_mmHg: float = 100.0
    a1: float = 0.76
    b1: float = 5.0
    PmaxC_mmHg: float = 10.0
    Pwidth_mmHg: float = 21.0

    # Heart: time-varying elastance with internal resistance, Eqs (10)-(11) (paper)
    heart_rate_bpm: float = 40.0
    T_max: float = 0.478         # s, "systolic duration", used as time to peak elastance
    E_max: float = 0.26          # mmHg/ml
    E_min: float = 0.01          # mmHg/ml
    V0_ml: float = 0.0
    kappa: float = 55e-6         # s/ml
    P_fill_mmHg: float = 16.0    # end-diastolic pressure; filling source pressure
    R_fill: float = 0.003        # mmHg s/ml, LV filling (internal) resistance
    # Shape of the normalized elastance curve: double-Hill fit to Senzaki et al.
    # (Stergiopulos et al. 1996), stretched so the peak falls at T_max (our choice).
    hill_a1: float = 0.303
    hill_a2: float = 0.508
    hill_n1: float = 1.32
    hill_n2: float = 21.9

    # Terminal 3-element Windkessels, Eqs (7)-(8)
    terminals: str = "s1"                # "s1": the paper's S1 Table; "estimated": paper's method, our guess
    R_total_parallel: float = 0.14       # mmHg s/ml (paper: "about 0.14"); used when estimated
    terminal_compliance_fraction: float = 0.20   # paper: ~20% of total compliance
    P_out_mmHg: float = 0.0              # outflow (venous) pressure, our assumption
    # Target share of cardiac output by region. Default: the paper's own model
    # without gravity (Table 2, first column). Used only because the per-branch
    # values in the paper's S1 Table are not in the PDF.
    flow_targets: dict = field(default_factory=lambda: {
        "heart": 4.2, "brain": 15.4, "muscle": 7.7,
        "kidney": 18.2, "splanchnic": 28.3, "other": 26.2})
    murray_exponent: float = 1.5   # within a region, flow ~ (distal area)^1.5, i.e. r^3

    # Numerics (ours)
    dx_target: float = 0.01      # m
    cfl: float = 0.8
    # Shock-capturing damping (Jameson-type, our choice). The paper's nonlinear wall law
    # makes the pulse front steepen along the aorta; this keeps the explicit scheme from
    # ringing there. 0 turns it off.
    shock_capturing: float = 1.0
    n_cycles: int = 8            # paper: 8 cardiac cycles
    history_samples: int = 256   # samples per cycle for the Womersley friction history
    output_samples: int = 1000   # samples saved for the last cycle
    P_init_mmHg: float = 100.0   # paper initial condition
    Q_init_ml_s: float = 1.0     # paper initial condition

    @property
    def T(self):
        return 60.0 / self.heart_rate_bpm
