from algorithms.genetic import run_genetic
from utils.generate_instances import generate_instance
from utils.evaluate import evaluate

def test_genetic_algorithm_valid_result():
    instance = generate_instance(nb_services=4, nb_regions=3, nb_machines=2)
    placement = run_genetic(instance)
    total, details = evaluate(instance, placement)

    assert placement is not None
    assert total != float("inf")
    assert isinstance(details, dict)