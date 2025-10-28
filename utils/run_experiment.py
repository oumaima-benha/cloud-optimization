import time
from utils.evaluate import evaluate
from utils.print_solution import *

def run_experiment(instance, algo_func, algo_name: str):
    """
    Exécute un algorithme de placement sur une instance et renvoie ses résultats

    Parameters
    ----------
    instance : Instance
        L'instance de test générée.
    algo_func : function
        Fonction de l'algorithme (doit retourner un Placement)
    algo_name : str
        Nom lisible de l'algorithme (pour l'affichage)

    Returns
    -------
    dict : {
        "algorithme": str,
        "placement" : affichage,
        "coût_total": float
        "temps_exécution (s)": float,
        "détails": dict,
    }
    """
    
    start_time = time.time()
    output = algo_func(instance)
    duration = time.time() - start_time
    placement = output

    total, details = evaluate(instance, placement)


    formatted_details = "\n".join(f"{k:25s}: {v}" for k, v in details.items())

    return {
        "algorithme : ": algo_name,
        "Placement des services : ": afficher_placement(placement),
        "coût_total : ": total,
        "temps_exécution (s) : ": round(duration, 3),
        "détails des coûts : ": formatted_details,
    }

