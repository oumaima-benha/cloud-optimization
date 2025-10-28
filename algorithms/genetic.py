import random
import math
from typing import Tuple, List
from utils.data_model import Instance, Placement
from utils.evaluate import evaluate

def random_individual(instance: Instance) -> Placement:
    """Crée un individu aléatoire (Placement) cohérent pour l'instance"""
    
    p = Placement()
    machines = list(instance.machines.keys())
    regions = list(instance.regions.keys())
    for s_id, svc in instance.services.items():
        # choisir une région autorisée si possible, sinon n'importe laquelle
        if svc.allowed_regions:
            r = random.choice(svc.allowed_regions)
        else:
            r = random.choice(regions)
        m = random.choice(machines)
        p.placement[s_id] = (m, r)
        p.redundancy[s_id] = random.choice([1, 1, 2])  # bias vers 1
    # initialiser chiffrement selon les exigences des flux
    for f in instance.flows:
        p.encryption[(f.src, f.dst)] = f.encryption_required
    return p

def tournament_selection(pop: List[Tuple[float, Placement]], k: int = 3) -> Placement:
    """
    Sélection par tournoi
    pop est une liste de tuples (cost, placement) triée ou non
    On tire k individus aléatoires et on renvoie le meilleur (coût minimal)
    """
    chosen = random.sample(pop, min(k, len(pop)))
    chosen.sort(key=lambda x: x[0])
    return chosen[0][1].copy()

def crossover(parent1: Placement, parent2: Placement) -> Placement:
    """
    Crossover simple : pour chaque service, prendre l'affectation d'un des parents
    (choix aléatoire). Retourne un enfant.
    """
    child = Placement()
    svc_ids = set(parent1.placement.keys()) | set(parent2.placement.keys())
    for s in svc_ids:
        if s in parent1.placement and s in parent2.placement:
            # choix binaire entre parents
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
    # encryption : on combine (si parents d'accord -> garder, sinon aléatoire)
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
    Mutation : pour chaque service, avec prob mutation_rate, déplacer sur (machine, region)
    ou changer redondance ; pour certains flux, toggler chiffrement
    Mutation se fait sur place (modifie l'individu)
    """
    machines = list(instance.machines.keys())
    regions = list(instance.regions.keys())
    # muter placements
    for s_id in list(ind.placement.keys()):
        if random.random() < mutation_rate:
            svc = instance.services[s_id]
            if svc.allowed_regions:
                r = random.choice(svc.allowed_regions)
            else:
                r = random.choice(regions)
            m = random.choice(machines)
            ind.placement[s_id] = (m, r)
        # muter redondance
        if random.random() < mutation_rate:
            ind.redundancy[s_id] = random.choice([1, 2, 3])
    # muter chiffrement sur quelques flux
    for f in instance.flows:
        if random.random() < mutation_rate:
            key = (f.src, f.dst)
            ind.encryption[key] = not ind.encryption.get(key, f.encryption_required)

def run_genetic(instance: Instance) -> Placement:
    """
    Exécute l'algorithme génétique et retourne le meilleur individu trouvé
    """
    #Les paramètres de l'AG
    pop_size = 20
    generations = 50
    elite_count = 2
    mutation_rate = 0.1
    tournament_k = 3

    # 1) Initialisation
    population: List[Tuple[float, Placement]] = []
    for _ in range(pop_size):
        ind = random_individual(instance)
        cost, _ = evaluate(instance, ind)
        # si infaisable? assigner coût très grand plutôt que math.inf pour garder l'individu
        if cost == math.inf:
            cost = 1e12
        population.append((cost, ind))

    # garder le meilleur global
    population.sort(key=lambda x: x[0])
    best_cost, best_placement = population[0][0], population[0][1].copy()

    # 2) Boucle des générations
    for g in range(generations):
        # tri et élitisme
        population.sort(key=lambda x: x[0])
        new_pop: List[Tuple[float, Placement]] = []
        # conserver les élites (copies)
        for i in range(min(elite_count, len(population))):
            cpy = population[i][1].copy()
            new_pop.append((population[i][0], cpy))

        # remplissage par reproduction, produire des enfants jusquu'à pop_size
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

        # mise à jour du meilleur global
        population.sort(key=lambda x: x[0])
        if population[0][0] < best_cost:
            best_cost = population[0][0]
            best_placement = population[0][1].copy()

    return best_placement