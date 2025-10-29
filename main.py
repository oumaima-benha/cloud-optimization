import pandas as pd
from utils.generate_instances import generate_instance
from utils.run_experiment import run_experiment
from utils.visualization import *
from algorithms.greedy import greedy_place
from algorithms.simulated_annealing import simulated_annealing
from algorithms.genetic import run_genetic
from utils.random_solution_generator import random_baseline


def main():
    # ======================== 1️ Générer une instance ========================
    instance = generate_instance(nb_services=50, nb_regions=12, nb_machines=20)

    results = []  # pour stocker tous les résultats dans un DataFrame à la fin

    # ======================== 2️ Baseline aléatoire ========================
    print("\n================================================ 0 - Baseline Aléatoire ================================================")
    rand_result = run_experiment(instance, random_baseline, "Baseline Aléatoire")
    results.append(rand_result)
    print("le coût total de la baseline aléatoire est :", rand_result["coût_total : "])
    print("\n--- Détails ---")
    print(rand_result["détails des coûts : "])

    # ======================== 3️ Greedy ========================
    print("\n================================================ 1 - Algorithme Greedy ================================================")
    greedy_result = run_experiment(instance, greedy_place, "Greedy")
    results.append(greedy_result)
    print("le coût total de l'algorithme Greedy est :", greedy_result["coût_total : "])
    print("\n--- Détails ---")
    print(greedy_result["détails des coûts : "])


    # ======================== 4️ Simulated Annealing ========================
    print("\n================================================ 2 - Algorithme de Recuit Simulé ================================================")
    sa_result = run_experiment(instance, simulated_annealing, "Recuit Simulé")
    results.append(sa_result)
    print("le coût total de l'algorithme Recuit Simulé est :", sa_result["coût_total : "])
    print("\n--- Détails ---")
    print(sa_result["détails des coûts : "])

    # ======================== 5️ Algorithme Génétique ========================
    print("\n================================================ 3 - Algorithme Génétique ================================================")
    ga_result = run_experiment(instance, run_genetic, "Algorithme Génétique")
    results.append(ga_result)
    print("le coût total de l'algorithme Génétique est :", ga_result["coût_total : "])
    print("\n--- Détails ---")
    print(ga_result["détails des coûts : "])
    

    # ======================== 6️ Tableau de synthèse ========================
    print("\n\n================================================ 🔍 Résumé comparatif global ================================================")
    df = pd.DataFrame(results)
    print(df[["algorithme : ", "coût_total : ", "temps_exécution (s) : "]])

    # ======================== 7️ Visualisation ========================
    plot_comparison_cout(df.rename(columns={
        "algorithme : ": "algorithme",
        "coût_total : ": "coût_total"}))
    
    plot_comparison_temps(df.rename(columns={
        "algorithme : ": "algorithme",
        "temps_exécution (s) : ": "temps_exécution"}))



if __name__ == "__main__":
    main()