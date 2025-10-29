import itertools
import time
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from utils.evaluate import evaluate


# ==============================================================
# 1️ Fonction utilitaire : mesurer le coût et le temps d'exécution
# ==============================================================
def _run_algo_and_measure(algo_func, instance, seed=None, **algo_kwargs):
    """
    Exécute un algorithme avec certains paramètres et renvoie un dict de résultats
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
# 2️ Sweep Recuit Simulé (Simulated Annealing)
# ==============================================================
def sweep_simulated_annealing(instance, param_grid: dict, n_runs: int = 3,
                              algo_func=None, save_csv: str = None):
    """
    Explore différentes combinaisons de paramètres du recuit simulé
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

    # statistiques agrégées
    df_grouped = df.groupby(keys).agg(
        mean_cost=("cost", "mean"),
        std_cost=("cost", "std"),
        mean_time=("duration", "mean")
    ).reset_index()

    if save_csv:
        df_grouped.to_csv(save_csv, index=False)
        print(f"✅ Résultats sauvegardés dans {save_csv}")

    return df_grouped


# ==============================================================
# 3️ Sweep Algorithme Génétique
# ==============================================================
def sweep_genetic(instance, param_grid: dict, n_runs: int = 3,
                  algo_func=None, save_csv: str = None):
    """
    Explore différentes combinaisons de paramètres pour l'algorithme génétique
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
        print(f"✅ Résultats sauvegardés dans {save_csv}")

    return df_grouped


# ==============================================================
# 4️ Visualisation : Heatmap robuste avec agrégation automatique
# ==============================================================
def plot_heatmap(df: pd.DataFrame, x_param: str, y_param: str, metric: str = "mean_cost", title: str = ""):
    """
    Affiche une heatmap même s'il y a des doublons (agrégation automatique)
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
    Scatter plot 3D à 2D : couleur = 3e paramètre, taille = coût
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
    plt.title(title or f"Influence de {x_param}, {y_param} et {hue_param}")
    plt.tight_layout()
    plt.show()


# ==============================================================
# 6️ Visualisation : évolution du coût moyen selon un paramètre
# ==============================================================
def plot_line(df: pd.DataFrame, x_param: str, metric: str = "mean_cost", title: str = ""):
    """
    Affiche une courbe moyenne du coût selon un paramètre
    """
    plt.figure(figsize=(7, 5))
    sns.lineplot(data=df, x=x_param, y=metric, marker="o")
    plt.title(title or f"{metric} en fonction de {x_param}")
    plt.xlabel(x_param)
    plt.ylabel(metric)
    plt.tight_layout()
    plt.show()
