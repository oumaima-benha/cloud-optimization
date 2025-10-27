import json
import random
from data_model import Service, MachineType, Region, Flow, Instance

def generate_small_example(path="instances/small_example.json"):
    services = {
        "s1": Service(id="s1", cpu=1.0, mem=1.0, storage=10.0, allowed_regions=["r1","r2"], zone="internal"),
        "s2": Service(id="s2", cpu=0.5, mem=0.5, storage=5.0, allowed_regions=["r1"], zone="public"),
        "s3": Service(id="s3", cpu=2.0, mem=2.0, storage=20.0, allowed_regions=["r2"], zone="restricted"),
    }
    machines = {
        "m_small": MachineType(id="m_small", cpu=4.0, mem=8.0, storage=100.0, bandwidth=100.0),
        "m_medium": MachineType(id="m_medium", cpu=8.0, mem=16.0, storage=500.0, bandwidth=500.0)
    }
    regions = {
        "r1": Region(id="r1"),
        "r2": Region(id="r2")
    }
    flows = [
        Flow(src="s1", dst="s2", bw=5.0, latency_max=100.0, encryption_required=False),
        Flow(src="s2", dst="s3", bw=1.0, latency_max=50.0, encryption_required=True),
    ]
    latency = {("r1","r1"):5.0, ("r2","r2"):5.0, ("r1","r2"):50.0, ("r2","r1"):50.0}
    transfer_cost = {("r1","r2"):0.05, ("r2","r1"):0.05, ("r1","r1"):0.0, ("r2","r2"):0.0}
    security_rules = {("internal","public"):True, ("public","restricted"):False}
    inst = Instance(services=services, machines=machines, regions=regions,
                    flows=flows, latency=latency, transfer_cost=transfer_cost,
                    security_rules=security_rules)
    with open(path, "w") as f:
        # naive serialization: convert dataclasses to dicts
        json.dump({
            "services": {k: v.__dict__ for k,v in services.items()},
            "machines": {k: v.__dict__ for k,v in machines.items()},
            "regions": list(regions.keys()),
            "flows": [f.__dict__ for f in flows],
            "latency": {f"{a}|{b}":lat for (a,b),lat in latency.items()},
            "transfer_cost": {f"{a}|{b}":c for (a,b),c in transfer_cost.items()},
            "security_rules": {f"{a}|{b}":val for (a,b),val in security_rules.items()}
        }, f, indent=2)

if __name__ == "__main__":
    generate_small_example()
    print("small_example.json generated in instances/")
