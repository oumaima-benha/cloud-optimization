from algorithms.greedy import greedy_place
from utils.generate_instances import generate_instance
from utils.evaluate import evaluate

def test_greedy_valid_solution():
    instance = generate_instance(nb_services=4, nb_regions=2, nb_machines=2)
    placement = greedy_place(instance)
    total, details = evaluate(instance, placement)
    assert total != float("inf")
    assert "machine_cost" in details