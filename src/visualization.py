"""Visualization Module for Sinhala-English AI Assistant Evaluation.

Provides reusable plotting functions using Matplotlib to generate clean, professional,
standalone PNG figures for pass rates, score distributions, dimension metrics, failure frequencies,
and latency performance.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd

# Color palette: professional modern blue/teal hues
COLOR_PRIMARY = "#1f77b4"
COLOR_SECONDARY = "#2ca02c"
COLOR_ACCENT = "#ff7f0e"
COLOR_MUTED = "#7f7f7f"
PALETTE_LANGUAGES = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd"]
PALETTE_DIFFICULTIES = ["#2ca02c", "#ff7f0e", "#d62728"]


def _format_label(name: str) -> str:
    """Format column/category identifier for display."""
    clean = str(name).replace("_", " ").title()
    if clean.lower() == "code mixed":
        return "Code-mixed"
    return clean


def plot_pass_rate_by_language(
    df: pd.DataFrame, output_path: Union[str, Path]
) -> Path:
    """Chart 1: Bar chart of Pass Rate (%) by Language Type."""
    if df.empty:
        raise ValueError("DataFrame for pass_rate_by_language is empty.")
    for col in ["language_type", "pass_rate"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in DataFrame.")

    # Reorder languages if present
    desired_order = ["english", "sinhala", "singlish", "code_mixed"]
    df_sorted = df.copy()
    df_sorted["lang_lower"] = df_sorted["language_type"].str.lower()
    df_sorted["sort_key"] = df_sorted["lang_lower"].apply(
        lambda x: desired_order.index(x) if x in desired_order else 99
    )
    df_sorted = df_sorted.sort_values("sort_key")

    labels = [_format_label(l) for l in df_sorted["language_type"]]
    values = [float(v) for v in df_sorted["pass_rate"]]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=PALETTE_LANGUAGES[: len(labels)], width=0.55)

    ax.set_ylim(0, 105)
    ax.set_ylabel("Pass Rate (%)", fontsize=11, fontweight="bold")
    ax.set_title("Pass Rate by Language Type", fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(
            f"{val:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_p, dpi=300)
    plt.close(fig)
    return out_p


def plot_average_score_by_language(
    df: pd.DataFrame, output_path: Union[str, Path]
) -> Path:
    """Chart 2: Bar chart of Average Score (out of 14) by Language Type."""
    if df.empty:
        raise ValueError("DataFrame for average_score_by_language is empty.")
    for col in ["language_type", "avg_score"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in DataFrame.")

    desired_order = ["english", "sinhala", "singlish", "code_mixed"]
    df_sorted = df.copy()
    df_sorted["lang_lower"] = df_sorted["language_type"].str.lower()
    df_sorted["sort_key"] = df_sorted["lang_lower"].apply(
        lambda x: desired_order.index(x) if x in desired_order else 99
    )
    df_sorted = df_sorted.sort_values("sort_key")

    labels = [_format_label(l) for l in df_sorted["language_type"]]
    values = [float(v) for v in df_sorted["avg_score"]]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=PALETTE_LANGUAGES[: len(labels)], width=0.55)

    ax.set_ylim(0, 15)
    ax.set_ylabel("Average Score (out of 14)", fontsize=11, fontweight="bold")
    ax.set_title(
        "Average Evaluation Score by Language Type", fontsize=13, fontweight="bold", pad=12
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(
            f"{val:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_p, dpi=300)
    plt.close(fig)
    return out_p


def plot_pass_rate_by_difficulty(
    df: pd.DataFrame, output_path: Union[str, Path]
) -> Path:
    """Chart 3: Bar chart of Pass Rate (%) by Difficulty (Easy, Medium, Hard)."""
    if df.empty:
        raise ValueError("DataFrame for pass_rate_by_difficulty is empty.")
    for col in ["difficulty", "pass_rate"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in DataFrame.")

    desired_order = ["easy", "medium", "hard"]
    df_sorted = df.copy()
    df_sorted["diff_lower"] = df_sorted["difficulty"].str.lower()
    df_sorted["sort_key"] = df_sorted["diff_lower"].apply(
        lambda x: desired_order.index(x) if x in desired_order else 99
    )
    df_sorted = df_sorted.sort_values("sort_key")

    labels = [_format_label(d) for d in df_sorted["difficulty"]]
    values = [float(v) for v in df_sorted["pass_rate"]]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, values, color=PALETTE_DIFFICULTIES[: len(labels)], width=0.5)

    ax.set_ylim(0, 105)
    ax.set_ylabel("Pass Rate (%)", fontsize=11, fontweight="bold")
    ax.set_title("Pass Rate by Test Difficulty", fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(
            f"{val:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_p, dpi=300)
    plt.close(fig)
    return out_p


def plot_average_dimension_scores(
    df: pd.DataFrame, output_path: Union[str, Path]
) -> Path:
    """Chart 4: Horizontal bar chart of Average Scores across 7 Dimensions (0 to 2)."""
    if df.empty:
        raise ValueError("DataFrame for average_dimension_scores is empty.")
    for col in ["dimension", "mean_score"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in DataFrame.")

    # Sort so top dimension is at the top of horizontal chart
    df_sorted = df.sort_values("mean_score", ascending=True)

    labels = [_format_label(d) for d in df_sorted["dimension"]]
    values = [float(v) for v in df_sorted["mean_score"]]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(labels, values, color=COLOR_PRIMARY, height=0.55)

    ax.set_xlim(0, 2.2)
    ax.set_xlabel("Average Score (0 to 2)", fontsize=11, fontweight="bold")
    ax.set_title(
        "Average Score by Evaluation Dimension", fontsize=13, fontweight="bold", pad=12
    )
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    for bar, val in zip(bars, values):
        width = bar.get_width()
        ax.annotate(
            f"{val:.2f}",
            xy=(width, bar.get_y() + bar.get_height() / 2),
            xytext=(5, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=9.5,
            fontweight="bold",
        )

    plt.tight_layout()
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_p, dpi=300)
    plt.close(fig)
    return out_p


def plot_failure_type_frequency(
    df: pd.DataFrame, output_path: Union[str, Path]
) -> Path:
    """Chart 5: Horizontal bar chart of Failure Type Frequencies."""
    if df.empty:
        raise ValueError("DataFrame for failure_type_frequency is empty.")
    for col in ["failure_type", "count"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in DataFrame.")

    # Filter to count >= 0 or non-empty
    df_filtered = df[df["count"].astype(float) >= 0].copy()
    df_sorted = df_filtered.sort_values("count", ascending=True)

    labels = [_format_label(ft) for ft in df_sorted["failure_type"]]
    values = [int(float(c)) for c in df_sorted["count"]]

    max_val = max(values) if values else 10
    x_limit = max(max_val + 2, 5)

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(labels, values, color="#d62728", height=0.55)

    ax.set_xlim(0, x_limit)
    ax.set_xlabel("Frequency (Count)", fontsize=11, fontweight="bold")
    ax.set_title(
        "Frequency of Recorded Failure Types", fontsize=13, fontweight="bold", pad=12
    )
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    for bar, val in zip(bars, values):
        width = bar.get_width()
        ax.annotate(
            f"{val}",
            xy=(width, bar.get_y() + bar.get_height() / 2),
            xytext=(5, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=9.5,
            fontweight="bold",
        )

    plt.tight_layout()
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_p, dpi=300)
    plt.close(fig)
    return out_p


def plot_pass_rate_by_category(
    df: pd.DataFrame, output_path: Union[str, Path]
) -> Path:
    """Chart 6: Horizontal bar chart of Pass Rate (%) by Category."""
    if df.empty:
        raise ValueError("DataFrame for pass_rate_by_category is empty.")
    for col in ["category", "pass_rate"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in DataFrame.")

    df_sorted = df.sort_values("pass_rate", ascending=True)

    labels = [str(c) for c in df_sorted["category"]]
    values = [float(v) for v in df_sorted["pass_rate"]]

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(labels, values, color="#17becf", height=0.6)

    ax.set_xlim(0, 110)
    ax.set_xlabel("Pass Rate (%)", fontsize=11, fontweight="bold")
    ax.set_title("Pass Rate by Evaluation Category", fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    for bar, val in zip(bars, values):
        width = bar.get_width()
        ax.annotate(
            f"{val:.1f}%",
            xy=(width, bar.get_y() + bar.get_height() / 2),
            xytext=(5, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_p, dpi=300)
    plt.close(fig)
    return out_p


def plot_dimension_scores_by_language(
    df: pd.DataFrame, output_path: Union[str, Path]
) -> Path:
    """Chart 7: Grouped bar chart of 7 Evaluation Dimensions across Language Types."""
    if df.empty:
        raise ValueError("DataFrame for dimension_scores_by_language is empty.")
    if "language_type" not in df.columns:
        raise ValueError("Missing required column 'language_type' in DataFrame.")

    dim_cols = [c for c in df.columns if c != "language_type"]
    if not dim_cols:
        raise ValueError("No dimension columns found in DataFrame.")

    # Reorder languages
    desired_order = ["english", "sinhala", "singlish", "code_mixed"]
    df_sorted = df.copy()
    df_sorted["lang_lower"] = df_sorted["language_type"].str.lower()
    df_sorted["sort_key"] = df_sorted["lang_lower"].apply(
        lambda x: desired_order.index(x) if x in desired_order else 99
    )
    df_sorted = df_sorted.sort_values("sort_key")

    languages = [_format_label(l) for l in df_sorted["language_type"]]
    n_langs = len(languages)
    n_dims = len(dim_cols)

    import numpy as np

    x = np.arange(n_dims)
    width = 0.8 / max(n_langs, 1)

    fig, ax = plt.subplots(figsize=(11, 6))

    for i, (_, row) in enumerate(df_sorted.iterrows()):
        lang_lbl = _format_label(row["language_type"])
        vals = [float(row[d]) for d in dim_cols]
        offset = x + (i - n_langs / 2 + 0.5) * width
        ax.bar(
            offset,
            vals,
            width,
            label=lang_lbl,
            color=PALETTE_LANGUAGES[i % len(PALETTE_LANGUAGES)],
        )

    dim_labels = [_format_label(d) for d in dim_cols]
    ax.set_xticks(x)
    ax.set_xticklabels(dim_labels, rotation=25, ha="right", fontsize=9.5)
    ax.set_ylim(0, 2.3)
    ax.set_ylabel("Average Dimension Score (0 to 2)", fontsize=11, fontweight="bold")
    ax.set_title(
        "Evaluation Dimension Scores by Language Type",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(title="Language Modality", loc="upper right")

    plt.tight_layout()
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_p, dpi=300)
    plt.close(fig)
    return out_p


def plot_latency_by_language(
    df: pd.DataFrame, output_path: Union[str, Path]
) -> Path:
    """Chart 8: Bar chart of Average API Latency (seconds) by Language Type."""
    if df.empty:
        raise ValueError("DataFrame for latency_by_language is empty.")
    for col in ["language_type", "latency_seconds"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in DataFrame.")

    # Group by language_type
    grouped = (
        df.groupby("language_type")["latency_seconds"]
        .mean()
        .reset_index()
        .rename(columns={"latency_seconds": "avg_latency"})
    )

    desired_order = ["english", "sinhala", "singlish", "code_mixed"]
    grouped["lang_lower"] = grouped["language_type"].str.lower()
    grouped["sort_key"] = grouped["lang_lower"].apply(
        lambda x: desired_order.index(x) if x in desired_order else 99
    )
    grouped = grouped.sort_values("sort_key")

    labels = [_format_label(l) for l in grouped["language_type"]]
    values = [float(v) for v in grouped["avg_latency"]]

    max_val = max(values) if values else 5.0

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color="#9467bd", width=0.55)

    ax.set_ylim(0, max_val * 1.25)
    ax.set_ylabel("Average Latency (seconds)", fontsize=11, fontweight="bold")
    ax.set_title(
        "Average Gemini Response Latency by Language Type",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(
            f"{val:.2f}s",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_p, dpi=300)
    plt.close(fig)
    return out_p
