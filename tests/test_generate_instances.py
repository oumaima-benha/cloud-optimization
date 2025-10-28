from utils.generate_instances import generate_instance

def test_generate_instance_structure():
    instance = generate_instance(nb_services=50, nb_regions=30, nb_machines=21)
    assert len(instance.services) == 50
    assert len(instance.regions) == 30
    assert instance.services["s1"].cpu > 0