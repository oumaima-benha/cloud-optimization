from typing import Tuple
import math
from utils.data_model import Instance, Placement
from utils.evaluate import evaluate

def greedy_place(instance: Instance) -> Placement:
    """
    Calcule un placement par une heuristique gloutonne (greedy)
    Retourne un objet Placement

    Stratégie :
      - trier les services par CPU décroissant (placer d'abord les plus gros)
      - pour chaque service, on va tester toutes les combinaisons (machine_type x region_allowed)
        en construisant une solution temporaire et en appelant evaluate()
      - choisir l'affectation qui minimise le coût total (selon evaluate)
    """
    placement = Placement()
    # services doivent être triés par cpu décroissant (plus coûteux / contraignant d'abord)
    services_sorted = sorted(instance.services.values(), key=lambda s: s.cpu, reverse=True)

    for svc in services_sorted:
        s_id = svc.id
        best_cost = math.inf
        best_choice = None

        # Parcourir tous les types de machines disponibles
        for m_id in instance.machines.keys():
            # Parcourir toutes les régions autorisées pour ce service
            for r_id in svc.allowed_regions:
                # Construire une copie temporaire du placement actuel
                temp = placement.copy()

                # Affecter temporairement le service courant
                temp.placement[s_id] = (m_id, r_id)
                # Par défaut redondance = 1 (on peut étendre plus tard)
                temp.redundancy[s_id] = temp.redundancy.get(s_id, 1)

                # S'assurer que les flux impliquant s_id ont un flag encryption initialisé
                # si l'un des côtés de la communication est déjà placé
                for f in instance.flows:
                    if (f.src == s_id and f.dst in temp.placement) or (f.dst == s_id and f.src in temp.placement):
                        # respecter la demande du flux (f.encryption_required) par défaut
                        temp.encryption[(f.src, f.dst)] = f.encryption_required

                # Évaluer la solution temporaire
                cost, _ = evaluate(instance, temp)

                # Si evaluate a retourné math.inf -> solution infaisable, on la considère comme non valide
                if cost is not None and cost < best_cost:
                    best_cost = cost
                    best_choice = (m_id, r_id)

        # Après avoir testé toutes les options pour le service, on fixe la meilleure
        if best_choice is not None and best_cost < math.inf:
            placement.placement[s_id] = best_choice
            placement.redundancy[s_id] = placement.redundancy.get(s_id, 1)
            # Mise à jour des flags encryption pour les flux où les deux extrémités sont maintenant placées
            for f in instance.flows:
                if f.src in placement.placement and f.dst in placement.placement:
                    # par défaut on respecte f.encryption_required
                    placement.encryption[(f.src, f.dst)] = f.encryption_required
        else:
            # ici on ne place pas le service
            # On pourrait aussi décider de marquer redondance=0 ou logger l'erreur
            print("problème d'affectation du service suivant : ")
            print(s_id)
        
            pass

    return placement