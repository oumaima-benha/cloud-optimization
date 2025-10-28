from utils.data_model import Service, MachineType, Region, Flow, Instance, Placement
from utils.evaluate import evaluate

def build_minimal_instance():
    services = {"s1": Service("s1", 1, 1, 10, ["r1"], "internal", 99.9),
                "s2": Service("s2", 1, 1, 10, ["r1"], "internal", 99.9)}
    machines = {"m1": MachineType("m1", 4, 8, 100, 200)}
    regions = {"r1": Region("r1")}
    flows = [Flow("s1", "s2", 1.0, 50, True)]
    return Instance(services, machines, regions, flows, {}, {}, {})

def test_evaluate_simple_case():
    instance = build_minimal_instance()
    placement = Placement(
        placement={"s1": ("m1", "r1"), "s2": ("m1", "r1")},
        redundancy={"s1": 1, "s2": 1},
        encryption={("s1", "s2"): True}
    )
    total, details = evaluate(instance, placement)
    assert total >= 0
    assert "machine_cost" in details