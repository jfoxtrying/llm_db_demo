# app/analytics/mc.py
import matplotlib
matplotlib.use("Agg")          # head-less backend for FastAPI
import matplotlib.pyplot as plt

import numpy as np, base64, io

def run_mc(
    n_draws: int,
    ltv_min: float, ltv_max: float,
    int_min: float, int_max: float,
    exit_cap_anchor: float,
    cap_beta: float = 0.50,
    cap_noise: float = 0.005,
    cap_target: float = 0.055,          # “success” threshold
) -> dict:
    """
    * Draw n samples for LTV and interest-rate.
    * Generate exit-cap = anchor + β·Δrate + noise.
    * Return P(exit-cap < target) + histogram PNG (base-64).
    """

    # ── random draws ───────────────────────────────────────────────────
    ltv   = np.random.uniform(ltv_min,  ltv_max,  n_draws)   # ← kept in case you need it later
    rate  = np.random.uniform(int_min,  int_max,  n_draws)

    cap   = (exit_cap_anchor +
             cap_beta * (rate - 0.0625) +
             np.random.normal(0, cap_noise, n_draws))

    p_success = float((cap < cap_target).mean())

    # ── histogram plot to show the distribution ───────────────────────
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.hist(cap, bins=40, edgecolor="black", alpha=0.80)
    ax.axvline(cap_target, color="red", ls="--",
               label=f"target {cap_target:.3%}")
    ax.set_xlabel("Exit cap-rate")
    ax.set_ylabel("Frequency")
    ax.set_title("Exit-cap Monte-Carlo distribution")
    ax.legend()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    hist_png = base64.b64encode(buf.getvalue()).decode()

    return {
        "p_below_target": p_success,                       # e.g. 0.57
        "hist_png": f"data:image/png;base64,{hist_png}",
    }