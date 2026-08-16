"""Time-series plots for every series in data/clean/ -- so a reader can see
the data before deciding whether to download it.

Usage
-----
    python scripts/make_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEAN_DIR = ROOT / "data" / "clean"
FIG_DIR = ROOT / "figures"


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    csv_paths = sorted(CLEAN_DIR.glob("*.csv"))

    for csv_path in csv_paths:
        df = pd.read_csv(csv_path, parse_dates=["date"])
        fig, ax = plt.subplots(figsize=(9, 3))
        ax.plot(df["date"], df["value"], color="#4C72B0", linewidth=1.0)
        ax.set_title(csv_path.stem)
        fig.tight_layout()
        fig.savefig(FIG_DIR / f"{csv_path.stem}.png", dpi=150)
        plt.close(fig)
        print(f"wrote figures/{csv_path.stem}.png")

    # A combined overview grid is worth more than N separate plots for a
    # reader deciding whether to look closer.
    n = len(csv_paths)
    cols = 3
    rows = -(-n // cols)
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 2.5 * rows))
    axes = axes.flatten()
    for ax, csv_path in zip(axes, csv_paths):
        df = pd.read_csv(csv_path, parse_dates=["date"])
        ax.plot(df["date"], df["value"], color="#4C72B0", linewidth=0.8)
        ax.set_title(csv_path.stem, fontsize=9)
        ax.tick_params(labelsize=7)
    for ax in axes[len(csv_paths) :]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "_overview.png", dpi=150)
    plt.close(fig)
    print("wrote figures/_overview.png")


if __name__ == "__main__":
    main()
