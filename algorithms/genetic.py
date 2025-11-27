import random
import math
from typing import Tuple, List
from utils.data_model import Instance, Placement
from utils.evaluate import evaluate

def random_individual(instance: Instance) -> Placement:
    """Creates a random individual (Placement) consistent with the instance"""
    
    p = Placement()
    machines = list(instance.machines.keys())
    regions = list(instance.regions.keys())
    for s_id, svc in instance.services.items():
        # choose an allowed region if possible, otherwise any region
        if svc.allowed_regions:
            r = random.choice(svc.allowed_regions)
        else:
            r = random.choice(regions)
        m = random.choice(machines)
        p.placement[s_id] = (m, r)
        p.redundancy[s_id] = random.choice([1, 1, 2])  # bias toward 1
    # initialize encryption according to flow requirements
    for f in instance.flows:
        p.encryption[(f.src, f.dst)] = f.encryption_required
    return p

def tournament_selection(pop: List[Tuple[float, Placement]], k: int = 3) -> Placement:
    """
    Tournament selection
    pop is a list of tuples (cost, placement), sorted or not
    We draw k random individuals and return the best (minimal cost)
    """
    chosen = random.sample(pop, min(k, len(pop)))
    chosen.sort(key=lambda x: x[0])
    return chosen[0][1].copy()

def crossover(parent1: Placement, parent2: Placement) -> Placement:
    """
    Simple crossover: for each service, take the assignment of one parent
    (random choice). Returns a child.
    """
    child = Placement()
    svc_ids = set(parent1.placement.keys()) | set(parent2.placement.keys())
    for s in svc_ids:
        if s in parent1.placement and s in parent2.placement:
            # binary choice between parents
            if random.random() < 0.5:
                child.placement[s] = parent1.placement[s]
                child.redundancy[s] = parent1.redundancy.get(s, 1)
            else:
                child.placement[s] = parent2.placement[s]
                child.redundancy[s] = parent2.redundancy.get(s, 1)
        elif s in parent1.placement:
            child.placement[s] = parent1.placement[s]
            child.redundancy[s] = parent1.redundancy.get(s, 1)
        else:
            child.placement[s] = parent2.placement[s]
            child.redundancy[s] = parent2.redundancy.get(s, 1)
    # encryption: combine (if both parents agree -> keep, otherwise random pick)
    for key in set(list(parent1.encryption.keys()) + list(parent2.encryption.keys())):
        v1 = parent1.encryption.get(key, None)
        v2 = parent2.encryption.get(key, None)
        if v1 is None:
            child.encryption[key] = v2
        elif v2 is None:
            child.encryption[key] = v1
        else:
            child.encryption[key] = v1 if random.random() < 0.5 else v2
    return child

def mutate(ind: Placement, instance: Instance, mutation_rate: float = 0.1):
    """
    Mutation: for each service, with probability mutation_rate, move to another
    (machine, region) or change redundancy; for some flows, toggle encryption.
    Mutation happens in-place (modifies the individual)
    """
    machines = list(instance.machines.keys())
    regions = list(instance.regions.keys())
    # mutate placements
    for s_id in list(ind.placement.keys()):
        if random.random() < mutation_rate:
            svc = instance.services[s_id]
            if svc.allowed_regions:
                r = random.choice(svc.allowed_regions)
            else:
                r = random.choice(regions)
            m = random.choice(machines)
            ind.placement[s_id] = (m, r)
        # mutate redundancy
        if random.random() < mutation_rate:
            ind.redundancy[s_id] = random.choice([1, 2, 3])
    # mutate encryption on some flows
    for f in instance.flows:
        if random.random() < mutation_rate:
            key = (f.src, f.dst)
            ind.encryption[key] = not ind.encryption.get(key, f.encryption_required)

def run_genetic(instance, pop_size=20, generations=50, mutation_rate=0.1, elite_count=2, seed=None) -> Placement:
    """
    Runs the genetic algorithm and returns the best individual found
    """
    if seed is not None:
        random.seed(seed)
    tournament_k = 3

    # 1) Initialization
    population: List[Tuple[float, Placement]] = []
    for _ in range(pop_size):
        ind = random_individual(instance)
        cost, _ = evaluate(instance, ind)
        # if infeasible? assign a very large cost instead of math.inf to keep the individual
        if cost == math.inf:
            cost = 1e12
        population.append((cost, ind))

    # keep global best
    population.sort(key=lambda x: x[0])
    best_cost, best_placement = population[0][0], population[0][1].copy()

    # 2) Generations loop
    for g in range(generations):
        # sorting and elitism
        population.sort(key=lambda x: x[0])
        new_pop: List[Tuple[float, Placement]] = []
        # keep elites (copies)
        for i in range(min(elite_count, len(population))):
            cpy = population[i][1].copy()
            new_pop.append((population[i][0], cpy))

        # fill population by reproduction, produce children until pop_size
        while len(new_pop) < pop_size:
            parent1 = tournament_selection(population, k=tournament_k)
            parent2 = tournament_selection(population, k=tournament_k)
            child = crossover(parent1, parent2)
            mutate(child, instance, mutation_rate=mutation_rate)
            cost_child, _ = evaluate(instance, child)
            if cost_child == math.inf:
                cost_child = 1e12
            new_pop.append((cost_child, child))

        population = new_pop

        # update global best
        population.sort(key=lambda x: x[0])
        if population[0][0] < best_cost:
            best_cost = population[0][0]
            best_placement = population[0][1].copy()

    return best_placement