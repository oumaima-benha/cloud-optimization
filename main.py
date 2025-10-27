from data_model import Service, MachineType, Region, Flow, Instance, Placement
from evaluate import evaluate
import math

def main():
    # === 1) Création manuelle d'une petite instance ===
    services = {
        "s1": Service(id="s1", cpu=1.0, mem=1.0, storage=10.0,
                      allowed_regions=["r1", "r2"], zone="internal", sla=99.9),
        "s2": Service(id="s2", cpu=2.0, mem=1.0, storage=20.0,
                      allowed_regions=["r2"], zone="public", sla=99.99),
    }

    machines = {
        "m_small": MachineType(id="m_small", cpu=4.0, mem=4.0, storage=100.0, bandwidth=100.0),
        "m_medium": MachineType(id="m_medium", cpu=8.0, mem=16.0, storage=200.0, bandwidth=200.0),
    }

    regions = {
        "r1": Region(id="r1"),
        "r2": Region(id="r2"),
    }

    flows = [
        Flow(src="s1", dst="s2", bw=5.0, latency_max=80.0, encryption_required=True)
    ]

    latency = {("r1", "r2"): 50.0, ("r2", "r1"): 50.0, ("r1", "r1"): 5.0, ("r2", "r2"): 5.0}
    transfer_cost = {("r1", "r2"): 0.05, ("r2", "r1"): 0.05, ("r1", "r1"): 0.0, ("r2", "r2"): 0.0}
    security_rules = {("internal", "public"): True, ("public", "internal"): True}

    instance = Instance(
        services=services,
        machines=machines,
        regions=regions,
        flows=flows,
        latency=latency,
        transfer_cost=transfer_cost,
        security_rules=security_rules,
    )

    # === 2) Création d'une solution (placement) ===
    placement = Placement()
    placement.placement = {
        "s1": ("m_small", "r1"),
        "s2": ("m_medium", "r2"),
    }
    placement.redundancy = {"s1": 1, "s2": 2}
    placement.encryption = {("s1", "s2"): True}  # flux chiffré

    # === 3) Évaluation ===
    total_cost, details = evaluate(instance, placement)

    print("\n===== Résultat de l'évaluation =====")
    if total_cost == math.inf:
        print("⚠️ Solution infaisable (une contrainte dure est violée).")
    else:
        print(f"✅ Coût total = {total_cost:.4f}\n")
        for k, v in details.items():
            print(f"{k:25s}: {v}")

if __name__ == "__main__":
    main()
