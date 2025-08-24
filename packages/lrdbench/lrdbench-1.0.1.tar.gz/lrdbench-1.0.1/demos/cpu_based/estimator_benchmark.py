"""
Estimator Benchmark

Runs a small benchmark across key estimators and a set of H values for
Fractional Brownian Motion (fBm) and Fractional Gaussian Noise (fGn).

Outputs:
- CSV with per-run absolute errors
- Bar chart with mean absolute error per estimator

This script is CI-friendly: plotting can be disabled and/or saved only.
"""

from __future__ import annotations

import os
import sys
import argparse
from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

# Ensure project root on path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.data_models.fbm.fbm_model import FractionalBrownianMotion
from models.data_models.fgn.fgn_model import FractionalGaussianNoise

# Estimators (choose a compact but representative set)
from analysis.temporal.dfa.dfa_estimator import DFAEstimator
from analysis.temporal.rs.rs_estimator import RSEstimator
from analysis.spectral.periodogram.periodogram_estimator import PeriodogramEstimator
from analysis.spectral.gph.gph_estimator import GPHEstimator
from analysis.wavelet.log_variance.wavelet_log_variance_estimator import (
    WaveletLogVarianceEstimator,
)
from analysis.multifractal.mfdfa.mfdfa_estimator import MFDFAEstimator


@dataclass
class BenchmarkConfig:
    n_samples: int = 2000
    trials_per_H: int = 3
    h_values: Tuple[float, ...] = (0.55, 0.65, 0.75, 0.85)
    seed: int = 42
    show_plots: bool = False
    save_plots: bool = True
    output_dir: str = os.path.join("results", "benchmarks")


def ensure_dirs(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def generate_series(model_name: str, H: float, n: int, seed: int) -> np.ndarray:
    if model_name == "fBm":
        model = FractionalBrownianMotion(H=H, sigma=1.0)
    elif model_name == "fGn":
        model = FractionalGaussianNoise(H=H, sigma=1.0)
    else:
        raise ValueError(f"Unsupported model: {model_name}")
    return model.generate(n, seed=seed)


def estimate_H(estimator, data: np.ndarray) -> float:
    output = estimator.estimate(data)
    if isinstance(output, dict):
        if "hurst_parameter" in output:
            return float(output["hurst_parameter"])
        if "fractal_dimension" in output:
            return float(2 - output["fractal_dimension"])
        raise ValueError("Estimator output missing 'hurst_parameter'/'fractal_dimension'")
    return float(output)


def run_benchmark(cfg: BenchmarkConfig) -> Dict[str, float]:
    np.random.seed(cfg.seed)
    ensure_dirs(cfg.output_dir)

    # Estimator instances
    estimators = {
        "DFA": DFAEstimator(),
        "R/S": RSEstimator(),
        "Periodogram": PeriodogramEstimator(),
        "GPH": GPHEstimator(),
        "Wavelet Log Variance": WaveletLogVarianceEstimator(),
        "MFDFA": MFDFAEstimator(),
    }

    models = ("fBm", "fGn")

    # Records: list of (model, H_true, estimator, H_est, abs_error)
    records: List[Tuple[str, float, str, float, float]] = []

    for model_name in models:
        for H in cfg.h_values:
            for t in range(cfg.trials_per_H):
                seed = cfg.seed + t
                data = generate_series(model_name, H, cfg.n_samples, seed)
                for est_name, est in estimators.items():
                    try:
                        H_hat = estimate_H(est, data)
                        err = abs(H_hat - H)
                        records.append((model_name, H, est_name, H_hat, err))
                    except Exception as e:
                        # Record NaN for failures
                        records.append((model_name, H, est_name, np.nan, np.nan))

    # Save CSV
    import csv

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(cfg.output_dir, f"benchmark_results_{ts}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["model", "H_true", "estimator", "H_est", "abs_error"])
        for r in records:
            writer.writerow(r)
    print(f"Saved benchmark CSV to {csv_path}")

    # Aggregate MAE per estimator
    estimator_to_errors: Dict[str, List[float]] = {}
    for _, _, est_name, _, err in records:
        if not np.isnan(err):
            estimator_to_errors.setdefault(est_name, []).append(err)

    mae_per_est: Dict[str, float] = {
        est: float(np.mean(errs)) for est, errs in estimator_to_errors.items()
    }

    # Plot MAE
    if mae_per_est:
        ests = list(mae_per_est.keys())
        maes = [mae_per_est[e] for e in ests]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(ests, maes, color="#6baed6", alpha=0.9)
        ax.set_ylabel("Mean Absolute Error")
        ax.set_title("Estimator MAE across H and models")
        ax.set_ylim(0, max(maes) * 1.2)
        for i, v in enumerate(maes):
            ax.text(i, v + 0.01, f"{v:.3f}", ha="center", va="bottom", fontsize=9)
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()

        png_path = os.path.join(cfg.output_dir, f"benchmark_mae_{ts}.png")
        fig.savefig(png_path, dpi=300, bbox_inches="tight")
        print(f"Saved benchmark MAE plot to {png_path}")
        if cfg.show_plots:
            plt.show()
        else:
            plt.close(fig)

    return mae_per_est


def parse_args() -> BenchmarkConfig:
    p = argparse.ArgumentParser(description="Run estimator benchmark")
    p.add_argument("--n-samples", type=int, default=2000)
    p.add_argument("--trials-per-H", type=int, default=3)
    p.add_argument(
        "--H", type=float, nargs="*", default=[0.55, 0.65, 0.75, 0.85],
        help="List of H values"
    )
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--no-plot", action="store_true")
    p.add_argument("--save-plots", action="store_true")
    p.add_argument("--outdir", type=str, default=os.path.join("results", "benchmarks"))
    args = p.parse_args()
    return BenchmarkConfig(
        n_samples=args.n_samples,
        trials_per_H=args.trials_per_H,
        h_values=tuple(args.H),
        seed=args.seed,
        show_plots=not args.no_plot,
        save_plots=args.save_plots or True,
        output_dir=args.outdir,
    )


def main() -> None:
    cfg = parse_args()
    run_benchmark(cfg)


if __name__ == "__main__":
    main()


