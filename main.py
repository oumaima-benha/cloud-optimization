import pandas as pd
from utils.generate_instances import generate_instance
from utils.run_experiment import run_experiment
from utils.visualization import *
from algorithms.greedy import greedy_place
from algorithms.simulated_annealing import simulated_annealing
from algorithms.genetic import run_genetic
from utils.random_solution_generator import random_baseline


def main():
    # ======================== 1️⃣ Generate an instance ========================
    instance = generate_instance(nb_services=50, nb_regions=12, nb_machines=20)

    results = []  # to store all results for final DataFrame

    # ======================== 2️⃣ Random Baseline ========================
    print("\n================================================ 0 - Random Baseline ================================================")
    rand_result = run_experiment(instance, random_baseline, "Random Baseline")
    results.append(rand_result)
    print("Total cost of the random baseline:", rand_result["total_cost"])
    print("\n--- Details ---")
    print(rand_result["cost_details"])

    # ======================== 3️⃣ Greedy Algorithm ========================
    print("\n================================================ 1 - Greedy Algorithm ================================================")
    greedy_result = run_experiment(instance, greedy_place, "Greedy")
    results.append(greedy_result)
    print("Total cost of the Greedy algorithm:", greedy_result["total_cost"])
    print("\n--- Details ---")
    print(greedy_result["cost_details"])

    # ======================== 4️⃣ Simulated Annealing ========================
    print("\n================================================ 2 - Simulated Annealing ================================================")
    sa_result = run_experiment(instance, simulated_annealing, "Simulated Annealing")
    results.append(sa_result)
    print("Total cost of the Simulated Annealing algorithm:", sa_result["total_cost"])
    print("\n--- Details ---")
    print(sa_result["cost_details"])

    # ======================== 5️⃣ Genetic Algorithm ========================
    print("\n================================================ 3 - Genetic Algorithm ================================================")
    ga_result = run_experiment(instance, run_genetic, "Genetic Algorithm")
    results.append(ga_result)
    print("Total cost of the Genetic Algorithm:", ga_result["total_cost"])
    print("\n--- Details ---")
    print(ga_result["cost_details"])
    
    # ======================== 6️⃣ Summary Table ========================
    print("\n\n================================================ 🔍 Overall Comparison Summary ================================================")
    df = pd.DataFrame(results)
    print(df[["algorithm", "total_cost", "execution_time (s)"]])

    # ======================== 7️⃣ Visualization ========================
    plot_cost_comparison(df.rename(columns={
        "algorithm": "algorithm",
        "total_cost": "total_cost"}))
    
    plot_execution_time_comparison(df.rename(columns={
        "algorithm": "algorithm",
        "execution_time (s)": "execution_time"}))


if __name__ == "__main__":
    main()