from generate_instances import generate_instance
from algorithms.greedy import greedy_place
from algorithms.simulated_annealing import simulated_annealing
from data_model import Placement
from evaluate import evaluate
import random
import math

#Fonction d'affichage
def afficher_placement(placement):
    print("\n===== Placement des services =====")
    if not placement.placement:
        print("⚠️ Aucun service placé.")
        return

    # --- Affichage des placements par service ---
    print("\n🖥️  Services placés :")
    for s_id, (m_id, r_id) in placement.placement.items():
        red = placement.redundancy.get(s_id, 1)
        print(f"  - {s_id:<5s} → Machine: {m_id:<10s} | Région: {r_id:<5s} | Redondance: {red}")

    # --- Affichage du chiffrement des flux ---
    if placement.encryption:
        print("\n Chiffrement des flux :")
        for (src, dst), enc in placement.encryption.items():
            status = "✅" if enc else "❌"
            print(f"  - {src} → {dst} : {status}")
    else:
        print("\n Aucun flux configuré pour le chiffrement.")

    print("=====================================\n")


# Fonction pour générer une solution aléatoirement
def random_baseline(instance):
    p = Placement()
    region_list = list(instance.regions.keys())
    machine_list = list(instance.machines.keys())
    for s_id in instance.services.keys():
        p.placement[s_id] = (random.choice(machine_list), random.choice(region_list))
        p.redundancy[s_id] = random.choice([1,2])
    for f in instance.flows:
        p.encryption[(f.src, f.dst)] = f.encryption_required
    return p


def main():
    # ======================== Générer une instance de test ========================
    instance = generate_instance(nb_services=6, nb_regions=3, nb_machines=4)

    # Baseline aléatoire
    rand_place = random_baseline(instance)
    rand_cost, _ = evaluate(instance, rand_place)
    print("\n======================== Solution aléatoire ========================")
    afficher_placement(rand_place)
    print(f"Coût baseline = {rand_cost}")

    # ======================== Greedy ========================
    greedy_place_res = greedy_place(instance)
    greedy_cost, greedy_details = evaluate(instance, greedy_place_res)
    print("\n======================== Greedy ========================")
    afficher_placement(greedy_place_res)
    if greedy_cost == math.inf:
        print("Greedy solution infaisable")
    else:
        print(f"Coût greedy = {greedy_cost:.4f}")
    # Détail GGreedy
    print("\n--- Détails Greedy ---")
    for k, v in greedy_details.items():
        print(f"{k:25s}: {v}")
        
        
        
    # ======================== Simulated Annealing ========================
    best_sa = simulated_annealing(instance)
    best_cost, sa_details = evaluate(instance, best_sa)
    print("\n======================== Simulated Annealing ========================")
    afficher_placement(best_sa)
    print(f"Coût SA = {best_cost}")
    # Détail Recuit simulé
    print("\n--- Détails Recuit simulé ---")
    for k, v in sa_details.items():
        print(f"{k:25s}: {v}")


if __name__ == "__main__":
    main()
