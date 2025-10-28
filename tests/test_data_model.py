from utils.data_model import Service, MachineType, Region, Flow, Instance

def test_service_creation():
    s = Service("s1", 2.0, 4.0, 10.0, ["r1"], "internal", 99.9)
    assert s.id == "s1"
    assert s.cpu == 2.0
    assert s.zone == "internal"

def test_instance_structure():
    region = {"r1": Region("r1")}
    machine = {"m1": MachineType("m1", 4.0, 8.0, 100.0, 200.0)}
    services = {"s1": Service("s1", 1.0, 2.0, 5.0, ["r1"], "public", 99.9)}
    instance = Instance(services, machine, region, [], {}, {}, {})
    assert isinstance(instance.services["s1"], Service)