import itertools
import time
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from utils.evaluate import evaluate


# ==============================================================
# 1️⃣ Utility function: measure cost and execution time
# ==============================================================
def _run_algo_and_measure(algo_func, instance, seed=None, **algo_kwargs):
    """
    Run an algorithm with specific parameters and return a result dictionary
    """
    start = time.time()
    placement = algo_func(instance, **algo_kwargs)
    elapsed = time.time() - start

    total, details = evaluate(instance, placement)
    return {
        "cost": total,
        "details": details,
        "duration": elapsed,
        **algo_kwargs
    }


# ==============================================================
# 2️⃣ Simulated Annealing Sweep
# ==============================================================
def sweep_simulated_annealing(instance, param_grid: dict, n_runs: int = 3,
                              algo_func=None, save_csv: str = None):
    """
    Explore different combinations of simulated annealing parameters
    """
    keys = list(param_grid.keys())
    all_combos = list(itertools.product(*param_grid.values()))

    results = []

    for combo in all_combos:
        combo_kwargs = dict(zip(keys, combo))
        for seed in range(n_runs):
            res = _run_algo_and_measure(algo_func, instance, seed=seed, **combo_kwargs)
            res["seed"] = seed
            results.append(res)

    df = pd.DataFrame(results)

    # aggregated statistics
    df_grouped = df.groupby(keys).agg(
        mean_cost=("cost", "mean"),
        std_cost=("cost", "std"),
        mean_time=("duration", "mean")
    ).reset_index()

    if save_csv:
        df_grouped.to_csv(save_csv, index=False)
        print(f"✅ Results saved to {save_csv}")

    return df_grouped


# ==============================================================
# 3️⃣ Genetic Algorithm Sweep
# ==============================================================
def sweep_genetic(instance, param_grid: dict, n_runs: int = 3,
                  algo_func=None, save_csv: str = None):
    """
    Explore different parameter combinations for the genetic algorithm
    """
    keys = list(param_grid.keys())
    all_combos = list(itertools.product(*param_grid.values()))

    results = []

    for combo in all_combos:
        combo_kwargs = dict(zip(keys, combo))
        for seed in range(n_runs):
            res = _run_algo_and_measure(algo_func, instance, seed=seed, **combo_kwargs)
            res["seed"] = seed
            results.append(res)

    df = pd.DataFrame(results)
    df_grouped = df.groupby(keys).agg(
        mean_cost=("cost", "mean"),
        std_cost=("cost", "std"),
        mean_time=("duration", "mean")
    ).reset_index()

    if save_csv:
        df_grouped.to_csv(save_csv, index=False)
        print(f"✅ Results saved to {save_csv}")

    return df_grouped


# ==============================================================
# 4️⃣ Visualization: Robust heatmap with automatic aggregation
# ==============================================================
def plot_heatmap(df: pd.DataFrame, x_param: str, y_param: str, metric: str = "mean_cost", title: str = ""):
    """
    Display a heatmap even if there are duplicates (automatic aggregation)
    """
    df_agg = df.groupby([x_param, y_param])[metric].mean().reset_index()

    pivot = df_agg.pivot(index=y_param, columns=x_param, values=metric)
    plt.figure(figsize=(8, 6))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="viridis")
    plt.title(title or f"{metric} heatmap")
    plt.xlabel(x_param)
    plt.ylabel(y_param)
    plt.tight_layout()
    plt.show()


def plot_scatter(df: pd.DataFrame, x_param: str, y_param: str, hue_param: str, metric: str = "mean_cost", title: str = ""):
    """
    2D scatter plot: color = 3rd parameter, size = cost
    """
    plt.figure(figsize=(8, 6))
    sns.scatterplot(
        data=df,
        x=x_param,
        y=y_param,
        hue=hue_param,
        size=metric,
        sizes=(50, 400),
        palette="coolwarm"
    )
    plt.title(title or f"Influence of {x_param}, {y_param}, and {hue_param}")
    plt.tight_layout()
    plt.show()


# ==============================================================
# 5️⃣ Visualization: average cost evolution by parameter
# ==============================================================
def plot_line(df: pd.DataFrame, x_param: str, metric: str = "mean_cost", title: str = ""):
    """
    Display the average cost curve according to a parameter
    """
    plt.figure(figsize=(7, 5))
    sns.lineplot(data=df, x=x_param, y=metric, marker="o")
    plt.title(title or f"{metric} as a function of {x_param}")
    plt.xlabel(x_param)
    plt.ylabel(metric)
    plt.tight_layout()
    plt.show()