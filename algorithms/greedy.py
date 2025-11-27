from typing import Tuple
import math
from utils.data_model import Instance, Placement
from utils.evaluate import evaluate

def greedy_place(instance: Instance) -> Placement:
    """
    Computes a placement using a greedy heuristic
    Returns a Placement object

    Strategy:
      - sort services by decreasing CPU (place the largest ones first)
      - for each service, test all combinations (machine_type x allowed_region)
        by building a temporary solution and calling evaluate()
      - choose the assignment that minimizes the total cost (according to evaluate)
    """
    placement = Placement()
    # services must be sorted by decreasing CPU (most costly / constrained first)
    services_sorted = sorted(instance.services.values(), key=lambda s: s.cpu, reverse=True)

    for svc in services_sorted:
        s_id = svc.id
        best_cost = math.inf
        best_choice = None

        # Iterate over all available machine types
        for m_id in instance.machines.keys():
            # Iterate over all allowed regions for this service
            for r_id in svc.allowed_regions:
                # Build a temporary copy of the current placement
                temp = placement.copy()

                # Temporarily assign the current service
                temp.placement[s_id] = (m_id, r_id)
                # Default redundancy = 1 (can be extended later)
                temp.redundancy[s_id] = temp.redundancy.get(s_id, 1)

                # Ensure that flows involving s_id have an encryption flag initialized
                # if one side of the communication is already placed
                for f in instance.flows:
                    if (f.src == s_id and f.dst in temp.placement) or (f.dst == s_id and f.src in temp.placement):
                        # respect the flow's request (f.encryption_required) by default
                        temp.encryption[(f.src, f.dst)] = f.encryption_required

                # Evaluate the temporary solution
                cost, _ = evaluate(instance, temp)

                # If evaluate returned math.inf -> infeasible solution, consider it invalid
                if cost is not None and cost < best_cost:
                    best_cost = cost
                    best_choice = (m_id, r_id)

        # After testing all options for the service, set the best one
        if best_choice is not None and best_cost < math.inf:
            placement.placement[s_id] = best_choice
            placement.redundancy[s_id] = placement.redundancy.get(s_id, 1)
            # Update encryption flags for flows where both endpoints are now placed
            for f in instance.flows:
                if f.src in placement.placement and f.dst in placement.placement:
                    # by default respect f.encryption_required
                    placement.encryption[(f.src, f.dst)] = f.encryption_required
        else:
            # here we do not place the service
            # We could also decide to mark redundancy=0 or log the error
            print("Problem assigning the following service: ")
            print(s_id)
        
            pass

    return placement