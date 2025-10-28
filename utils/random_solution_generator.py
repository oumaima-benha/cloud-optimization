import random
from utils.data_model import Placement


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