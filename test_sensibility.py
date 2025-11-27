from utils.generate_instances import generate_instance
from algorithms.simulated_annealing import simulated_annealing
from algorithms.genetic import run_genetic
from utils.sensitivity_analysis import (
    sweep_simulated_annealing,
    sweep_genetic,
    plot_heatmap,
    plot_scatter,
    plot_line
)

# === Generate an instance ===
instance = generate_instance(nb_services=6, nb_regions=3, nb_machines=3)

# === 1️⃣ Simulated Annealing Sensitivity ===
sa_grid = {
    "T0": [500.0, 1000.0, 2000.0],
    "alpha": [0.8, 0.85, 0.9],
    "iter_per_T": [20],
    "max_evals": [2000]
}

df_sa = sweep_simulated_annealing(
    instance,
    sa_grid,
    n_runs=3,
    algo_func=simulated_annealing,
    save_csv="results/sa_sensitivity.csv"
)

print("\n=== Simulated Annealing Summary ===")
print(df_sa.head())

plot_heatmap(df_sa, x_param="T0", y_param="alpha", metric="mean_cost", title="Sensitivity - Simulated Annealing")
plot_line(df_sa, x_param="T0", metric="mean_cost", title="Influence of T0 on Average Cost (Simulated Annealing)")

# === 2️⃣ Genetic Algorithm Sensitivity ===
ga_grid = {
    "pop_size": [10, 20, 30],
    "mutation_rate": [0.05, 0.1, 0.2],
    "generations": [30]
}

df_ga = sweep_genetic(
    instance,
    ga_grid,
    n_runs=3,
    algo_func=run_genetic,
    save_csv="results/ga_sensitivity.csv"
)

print("\n=== Genetic Algorithm Summary ===")
print(df_ga.head())

plot_scatter(
    df_ga,
    x_param="pop_size",
    y_param="mutation_rate",
    hue_param="generations",
    metric="mean_cost",
    title="Sensitivity - Genetic Algorithm"
)
plot_line(
    df_ga,
    x_param="pop_size",
    metric="mean_cost",
    title="Influence of Population Size on Average Cost (GA)"
)