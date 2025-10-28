import random
import math
from typing import Tuple
from utils.data_model import Instance, Placement
from utils.evaluate import evaluate
from algorithms.greedy import greedy_place  # on peut démarrer depuis greedy si disponible

def random_neighbor(placement: Placement, instance: Instance) -> Placement:
    """
    Génère un voisin en effectuant une petite modification aléatoire :
    - déplacer un service vers une autre (machine,region) 
    - ou changer la redondance d'un service (1..3) 
    - ou changer le chiffrement d'un flux
    On renvoie une copie modifiée de placement
    """
    neigh = placement.copy()
    services = list(instance.services.keys())
    machines = list(instance.machines.keys())
    regions = list(instance.regions.keys())

    move_type = random.choice(["move_service", "change_redundancy", "toggle_encryption"])
    if move_type == "move_service" and services:
        s = random.choice(services)
        # choisir machine et région valides (préférence aux allowed_regions)
        svc = instance.services[s]
        # si service a allowed_regions, on choisit dedans sinon dans toutes
        possible_regions = svc.allowed_regions if svc.allowed_regions else regions
        new_r = random.choice(possible_regions)
        new_m = random.choice(machines)
        neigh.placement[s] = (new_m, new_r)
    elif move_type == "change_redundancy" and services:
        s = random.choice(services)
        new_red = random.choice([1, 2, 3])
        neigh.redundancy[s] = new_red
    elif move_type == "toggle_encryption" and instance.flows:
        f = random.choice(instance.flows)
        key = (f.src, f.dst)
        current = neigh.encryption.get(key, f.encryption_required)
        neigh.encryption[key] = not current
    else:
        # fallback : déplacer un service si rien d'autre possible
        if services:
            s = random.choice(services)
            svc = instance.services[s]
            possible_regions = svc.allowed_regions if svc.allowed_regions else regions
            new_r = random.choice(possible_regions)
            new_m = random.choice(machines)
            neigh.placement[s] = (new_m, new_r)

    return neigh

def simulated_annealing(instance: Instance) -> Placement:
    """
    Paramètres :
      - T0 : température initiale
      - Tmin : température finale
      - alpha : facteur de refroidissement (0 < alpha < 1)
      - iter_per_T : nombre d'itérations par palier de température
      - max_evals : nombre maximal d'évaluations (sécurité)
    """
    
    T0 = 1000.0
    Tmin = 1.0
    alpha = 0.85
    iter_per_T = 50
    max_evals = 5000                        
        
    current = greedy_place(instance)

    current_cost, _ = evaluate(instance, current)
    best = current.copy()
    best_cost = current_cost

    T = T0
    evals = 1  # on a déjà évalué l'initiale

    while T > Tmin and evals < max_evals:
        for _ in range(iter_per_T):
            if evals >= max_evals:
                break
            # générer voisin et évaluer
            neighbor = random_neighbor(current, instance)
            neighbor_cost, _ = evaluate(instance, neighbor)
            evals += 1

            if neighbor_cost is None:
                continue

            delta = neighbor_cost - current_cost

            if neighbor_cost < current_cost:
                # amélioration -> accepter
                current = neighbor
                current_cost = neighbor_cost
                if neighbor_cost < best_cost:
                    best = neighbor.copy()
                    best_cost = neighbor_cost
            else:
                # accepter avec probabilité exp(-delta / T)
                try:
                    prob = math.exp(-delta / T) if T > 0 else 0.0
                except OverflowError:
                    prob = 0.0
                if random.random() < prob:
                    current = neighbor
                    current_cost = neighbor_cost
        # refroidissement
        T = T * alpha

    return best