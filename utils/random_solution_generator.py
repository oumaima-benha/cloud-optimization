import random
from utils.data_model import Placement


# Function to generate a random solution
def random_baseline(instance):
    p = Placement()
    region_list = list(instance.regions.keys())
    machine_list = list(instance.machines.keys())
    
    for s_id in instance.services.keys():
        # Randomly assign machine and region
        p.placement[s_id] = (random.choice(machine_list), random.choice(region_list))
        # Randomly assign redundancy 1 or 2
        p.redundancy[s_id] = random.choice([1, 2])
    
    for f in instance.flows:
        # Set encryption according to flow requirement
        p.encryption[(f.src, f.dst)] = f.encryption_required
    
    return p