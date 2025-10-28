from algorithms.simulated_annealing import simulated_annealing
from utils.generate_instances import generate_instance
from utils.evaluate import evaluate

def test_simulated_annealing_runs():
    instance = generate_instance(nb_services=4, nb_regions=3, nb_machines=2)
    placement = simulated_annealing(instance)
    total, details = evaluate(instance, placement)

    assert placement is not None
    assert total != float("inf")
    assert "machine_cost" in details