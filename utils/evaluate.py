from typing import Tuple, Dict, List
from utils.data_model import Instance, Placement
import math
from utils.boites_noires import *


''' ================================================= Évaluation complète =================================================
    Ce code évalue une solution et renvoie 
    (total_cost, details_dict)
    Et si une boîte-noire retourne math.inf, la fonction retourne (math.inf, details)
'''
def evaluate(instance: Instance, placement: Placement) -> Tuple[float, dict]:
    total = 0.0
    details: Dict[str, float] = {}

    # --- 1) coût machines (somme par service) ---
    machine_cost = 0.0
    for s_id, (m_id, r_id) in placement.placement.items():
        red = placement.redundancy.get(s_id, 1)
        c = cost_machine(m_id, r_id, red)
        if c == math.inf:
            details['error'] = f"machine cost inf for {s_id}"
            return math.inf, details
        machine_cost += c
    details['machine_cost'] = machine_cost
    total += machine_cost

    # --- 2) coût stockage ---
    storage_cost = 0.0
    for s in instance.services.values():
        _, r = placement.placement.get(s.id, (None, None))
        if r is None:
            # ajouter une pénalité si non placé
            storage_cost += 1e6
        else:
            c = cost_storage(s.storage, r)
            if c == math.inf:
                details['error'] = f"storage cost inf for {s.id}"
                return math.inf, details
            storage_cost += c
    details['storage_cost'] = storage_cost
    total += storage_cost

    # --- 3) réseau / flux : coût réseau + sécurité + encryption + performance penalties ---
    network_cost = 0.0
    sec_penalty = 0.0
    perf_penalty = 0.0
    encryption_penalty = 0.0

    # calculer le cout pour chaque flux 
    for f in instance.flows:
        src_place = placement.placement.get(f.src) #c'est le tuple (machiine, région)
        dst_place = placement.placement.get(f.dst)
        if src_place is None or dst_place is None:
            # ajouter une pénalité si non placé
            perf_penalty += 1e6
            continue
        m_src, r_src = src_place
        _, r_dst = dst_place

        # Calcul du trafic mensuel approximatif en Go :
        # bande passante (en Mbit/s) × secondes par mois / 8 (bits -> octets) / 1024 (Mo -> Go) 
        bw_gb_month = f.bw * 3600 * 24 * 30 / 8 / 1024

        enc = placement.encryption.get((f.src, f.dst), f.encryption_required)

        # network cost
        netc = cost_network(bw_gb_month, r_src, r_dst, enc)
        if netc == math.inf:
            details['error'] = f"network cost inf for flow {f.src}->{f.dst}"
            return math.inf, details
        network_cost += netc

        # security penalty (uses instance.rules)
        secp = cost_security_violation(instance.services[f.src].zone,
                                       instance.services[f.dst].zone, enc)
        if secp == math.inf:
            details['error'] = f"security violation inf for flow {f.src}->{f.dst}"
            return math.inf, details
        sec_penalty += secp

        # encryption-specific penalty (if flow requires encryption but not provided)
        encp = cost_encryption_violation(f, enc, instance.services[f.src].zone, instance.services[f.dst].zone)
        if encp == math.inf:
            details['error'] = f"encryption violation inf for flow {f.src}->{f.dst}"
            return math.inf, details
        encryption_penalty += encp

        # performance (latency / bandwidth) penalty
        perfp = cost_network_performance_violation(f.bw, f.latency_max, r_src, r_dst, m_id)
        if perfp == math.inf:
            details['error'] = f"performance violation inf for flow {f.src}->{f.dst}"
            return math.inf, details
        perf_penalty += perfp

    details['network_cost'] = network_cost
    details['security_penalty'] = sec_penalty
    details['encryption_penalty'] = encryption_penalty
    details['performance_penalty'] = perf_penalty
    total += (network_cost + sec_penalty + encryption_penalty + perf_penalty)

    # --- 4) disponibilité / availability cost (par service) ---
    avail_cost_sum = 0.0
    for s in instance.services.values():
        _, r = placement.placement.get(s.id, (None, None))
        red = placement.redundancy.get(s.id, 1)
        sla_required = s.sla
        if r is None:
            # ajouter une pénalité si non placé
            avail_cost_sum += 1e6
        else:
            ac = cost_availability(sla_required, red, r)
            if ac == math.inf:
                details['error'] = f"availability inf for {s.id}"
                return math.inf, details
            avail_cost_sum += ac
    details['availability_cost'] = avail_cost_sum
    total += avail_cost_sum

    # --- 5) couut de capacité  ---
    # On regroupe d’abord tous les services affectés à la même combinaison (machine_type, région)
    machine_alloc: Dict[Tuple[str, str], List[str]] = {}
    for s_id, (m_id, r_id) in placement.placement.items():
        key = (m_id, r_id)
        machine_alloc.setdefault(key, []).append(s_id)

    capacity_penalty = 0.0
    for (m_id, r_id), svc_list in machine_alloc.items():
        cp = cost_capacity_violation(svc_list, m_id)
        if cp == math.inf:
            details['error'] = f"capacity inf for machine {m_id} in {r_id}"
            return math.inf, details
        capacity_penalty += cp
    details['capacity_penalty'] = capacity_penalty
    total += capacity_penalty

    # --- 6) cyber costs ---
    cyber_cost = cost_cybersecurity(placement, None, instance.flows) #j'ai mis None pour la topology
    if cyber_cost == math.inf:
        details['error'] = "cybersecurity cost inf"
        return math.inf, details
    details['cyber_cost'] = cyber_cost
    total += cyber_cost

    # --- 7) géographie (conformité) penalties par service ---
    # on prépare le mapping des régions d'affectation : {service_id: region_id}
    other_services_regions = {
        s_id: r_id for s_id, (_, r_id) in placement.placement.items()
    }

    geography_penalty = 0.0
    for s_id, (m_id, r_id) in placement.placement.items():
        service = instance.services[s_id]
        gp = cost_geography_violation(service, r_id, other_services_regions)
        if gp == math.inf:
            details['error'] = f"geography inf for {s_id} in {r_id}"
            return math.inf, details
        geography_penalty += gp

    details['geography_penalty'] = geography_penalty
    total += geography_penalty
    
    
    details['total'] = total
    return total, details