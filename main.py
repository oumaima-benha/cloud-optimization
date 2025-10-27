from generate_instances import generate_instance
from algorithms.greedy import greedy_place
from data_model import Placement
from evaluate import evaluate
import random
import math

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


def main():
    # Générer une instance de test
    instance = generate_instance(nb_services=6, nb_regions=3, nb_machines=4)

    # Greedy
    greedy_place_res = greedy_place(instance)
    afficher_placement(greedy_place_res)
    greedy_cost, greedy_details = evaluate(instance, greedy_place_res)
    print("\n--- Greedy ---")
    if greedy_cost == math.inf:
        print("Greedy solution infaisable")
    else:
        print(f"Coût greedy = {greedy_cost:.4f}")
    # Détail GGreedy
    print("\n--- Détails Greedy ---")
    for k, v in greedy_details.items():
        print(f"{k:25s}: {v}")


if __name__ == "__main__":
    main()
