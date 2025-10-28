import json
import random
import os
from utils.data_model import Service, MachineType, Region, Flow, Instance, Placement
from utils.evaluate import evaluate

"""
    Cette fonction généree une instance (un probleme) aléatoire mais cohérente 
    """
def generate_instance(nb_services=5, nb_regions=3, nb_machines=3):
    
    path = "instances/example_instance{}{}{}.json".format(nb_services, nb_regions, nb_machines)

    random.seed()  # réinitialisation de la graine pour variabilité

    # === 1️ Régions ===
    regions = {f"r{i+1}": Region(id=f"r{i+1}") for i in range(nb_regions)}

    # === 2️ Types de machines (choisis parmi un catalogue connu) ===
    # On définit un catalogue réaliste
    machine_catalogue = {
        "m_micro":   {"cpu": 1.0,  "mem": 1.0,  "storage": 20.0,  "bandwidth": 50.0},
        "m_small":   {"cpu": 2.0,  "mem": 4.0,  "storage": 100.0, "bandwidth": 100.0},
        "m_medium":  {"cpu": 4.0,  "mem": 8.0,  "storage": 200.0, "bandwidth": 200.0},
        "m_large":   {"cpu": 8.0,  "mem": 16.0, "storage": 400.0, "bandwidth": 400.0},
        "m_xlarge":  {"cpu": 16.0, "mem": 32.0, "storage": 800.0, "bandwidth": 800.0},
    }

    # On sélectionne aléatoirement nb_machines types parmi le catalogue
    chosen_types = random.sample(list(machine_catalogue.keys()), k=min(nb_machines, len(machine_catalogue)))
    machines = {
        name: MachineType(id=name, **machine_catalogue[name])
        for name in chosen_types
    }

    # === 3️ Services ===
    zones = ["internal", "public", "restreint"]
    services = {}
    for i in range(nb_services):
        s_id = f"s{i+1}"
        cpu = round(random.uniform(0.5, 4.0), 2)
        mem = round(random.uniform(0.5, 8.0), 2)
        storage = round(random.uniform(5.0, 100.0), 2)
        allowed_regions = random.sample(list(regions.keys()), k=random.randint(1, nb_regions))
        zone = random.choice(zones)
        sla = random.choice([99.9, 99.95, 99.99, 99.999])
        services[s_id] = Service(
            id=s_id,
            cpu=cpu,
            mem=mem,
            storage=storage,
            allowed_regions=allowed_regions,
            zone=zone,
            sla=sla
        )

    # === 4️ Flux réseau ===
    flows = []
    nb_flows = random.randint(nb_services, nb_services * 2)
    for _ in range(nb_flows):
        src, dst = random.sample(list(services.keys()), 2)
        bw = round(random.uniform(1.0, 15.0), 2)  # Mbps
        latency_max = random.choice([30, 50, 80, 100])
        encryption_required = random.choice([True, False])
        flows.append(Flow(src=src, dst=dst, bw=bw, latency_max=latency_max, encryption_required=encryption_required))

    # === 5️ Latence & coûts réseau inter-régions ===
    latency = {}
    transfer_cost = {}
    for r1 in regions:
        for r2 in regions:
            if r1 == r2:
                latency[(r1, r2)] = 5.0
                transfer_cost[(r1, r2)] = 0.0
            else:
                latency[(r1, r2)] = round(random.uniform(20.0, 100.0), 2)
                transfer_cost[(r1, r2)] = round(random.uniform(0.01, 0.05), 3)

    # === 6️ Règles de sécurité ===
    security_rules = {
        ("internal", "public"): True,
        ("public", "internal"): True,
        ("internal", "restreint"): False,
        ("restreint", "public"): False,
        ("restreint", "internal"): True,
    }

    # === 7️ Création de l'instance ===
    instance = Instance(
        services=services,
        machines=machines,
        regions=regions,
        flows=flows,
        latency=latency,
        transfer_cost=transfer_cost,
        security_rules=security_rules
    )

    # === 8️ Sauvegarde JSON ===
    os.makedirs("instances", exist_ok=True)
    data = {
        "services": {sid: vars(s) for sid, s in services.items()},
        "machines": {mid: vars(m) for mid, m in machines.items()},
        "regions": list(regions.keys()),
        "flows": [vars(f) for f in flows],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Instance sauvegardée dans {path}")

    return instance


def test_basic_solution(instance):
    """
    Crée une solution de placement simple et évalue son coût.
    """
    placement = Placement()
    region_list = list(instance.regions.keys())
    machine_list = list(instance.machines.keys())

    for s_id in instance.services:
        r = random.choice(region_list)
        m = random.choice(machine_list)
        placement.placement[s_id] = (m, r)
        placement.redundancy[s_id] = random.choice([1, 2])
    for f in instance.flows:
        placement.encryption[(f.src, f.dst)] = f.encryption_required

    total, details = evaluate(instance, placement)
    print("\n=== Évaluation d'une solution basique ===")
    print(f"Coût total = {total}")
    for k, v in details.items():
        print(f"{k:25s}: {v}")