import time
from utils.evaluate import evaluate
from utils.print_solution import *

def run_experiment(instance, algo_func, algo_name: str):
    """
    Runs a placement algorithm on an instance and returns its results.

    Parameters
    ----------
    instance : Instance
        The generated test instance.
    algo_func : function
        The algorithm function (must return a Placement)
    algo_name : str
        Human-readable name of the algorithm (for display)

    Returns
    -------
    dict : {
        "algorithm": str,
        "placement": display output,
        "total_cost": float,
        "execution_time (s)": float,
        "details": dict,
    }
    """
    
    start_time = time.time()
    output = algo_func(instance)
    duration = time.time() - start_time
    placement = output

    total, details = evaluate(instance, placement)

    formatted_details = "\n".join(f"{k:25s}: {v}" for k, v in details.items())

    return {
        "algorithm": algo_name,
        "service_placement": display_placement(placement),
        "total_cost": total,
        "execution_time (s)": round(duration, 3),
        "cost_details": formatted_details,
    }
