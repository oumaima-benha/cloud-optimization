import random
import math
from typing import Tuple
from utils.data_model import Instance, Placement
from utils.evaluate import evaluate
from algorithms.greedy import greedy_place  # we can start from greedy if available

def random_neighbor(placement: Placement, instance: Instance) -> Placement:
    """
    Generates a neighbor by making a small random modification:
    - move a service to another (machine, region)
    - or change the redundancy of a service (1..3)
    - or change the encryption of a flow
    Returns a modified copy of placement
    """
    neigh = placement.copy()
    services = list(instance.services.keys())
    machines = list(instance.machines.keys())
    regions = list(instance.regions.keys())

    move_type = random.choice(["move_service", "change_redundancy", "toggle_encryption"])
    if move_type == "move_service" and services:
        s = random.choice(services)
        # choose valid machine and region (prefer allowed_regions)
        svc = instance.services[s]
        # if service has allowed_regions, choose from them, otherwise from all
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
        # fallback: move a service if nothing else is possible
        if services:
            s = random.choice(services)
            svc = instance.services[s]
            possible_regions = svc.allowed_regions if svc.allowed_regions else regions
            new_r = random.choice(possible_regions)
            new_m = random.choice(machines)
            neigh.placement[s] = (new_m, new_r)

    return neigh

def simulated_annealing(instance, T0=1000.0, Tmin=1.0, alpha=0.85, iter_per_T=50, max_evals=5000, seed=None) -> Placement:
    """
    Parameters:
      - T0 : initial temperature
      - Tmin : final temperature
      - alpha : cooling factor (0 < alpha < 1)
      - iter_per_T : number of iterations per temperature level
      - max_evals : maximum number of evaluations (safety)
    """
    
    if seed is not None:
        random.seed(seed)                       
        
    current = greedy_place(instance)

    current_cost, _ = evaluate(instance, current)
    best = current.copy()
    best_cost = current_cost

    T = T0
    evals = 1  # the initial placement has already been evaluated

    while T > Tmin and evals < max_evals:
        for _ in range(iter_per_T):
            if evals >= max_evals:
                break
            # generate neighbor and evaluate
            neighbor = random_neighbor(current, instance)
            neighbor_cost, _ = evaluate(instance, neighbor)
            evals += 1

            if neighbor_cost is None:
                continue

            delta = neighbor_cost - current_cost

            if neighbor_cost < current_cost:
                # improvement -> accept
                current = neighbor
                current_cost = neighbor_cost
                if neighbor_cost < best_cost:
                    best = neighbor.copy()
                    best_cost = neighbor_cost
            else:
                # accept with probability exp(-delta / T)
                try:
                    prob = math.exp(-delta / T) if T > 0 else 0.0
                except OverflowError:
                    prob = 0.0
                if random.random() < prob:
                    current = neighbor
                    current_cost = neighbor_cost
        # cooling
        T = T * alpha

    return best