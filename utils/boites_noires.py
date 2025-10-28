''' === Placeholders pour les boîtes noires ===
# On doit remplacer ces fonctions par les vraies fonctions fournies (import ou API)
'''

def cost_machine(machine_id, region_id, redundancy_level) -> float:
    # placeholder simple : base cost depends on machine and region
    base = 0.05 * redundancy_level
    return base

def cost_network(bw_gb_per_month, region_src, region_dst, encrypted) -> float:
    # placeholder : cost per GB * volume
    dist_cost = 0.01 if region_src == region_dst else 0.05
    enc_surcharge = 0.002 if encrypted else 0.0
    return (dist_cost + enc_surcharge) * bw_gb_per_month

def cost_storage(volume_gb, region_id, storage_type='standard') -> float:
    rate = 0.02
    return rate * volume_gb

def cost_availability(sla_required: float, redundancy_level: int, region: str) -> float:
    # Exemple simple : coût = factor * (redundancy_level) * sla_required
    if sla_required is None:
        return 0.0
    factor = 10.0  # placeholder $/mois per sla unit
    return factor * redundancy_level * (1.0 if sla_required >= 99.9 else 0.5)

def cost_security_violation(zone_src, zone_dst, encrypted) -> float:
    # returns large penalty if communication forbidden
    # real function may return +inf for forbidden comms
    allowed = True  # placeholder, real code checks instance.security_rules
    if not allowed:
        return 1e9
    if (zone_src != zone_dst) and (not encrypted):
        return 1000.0
    return 0.0

def cost_network_performance_violation(*args, **kwargs) -> float:
    return 0.0

def cost_capacity_violation(*args, **kwargs) -> float:
    return 0.0

def cost_geography_violation(*args, **kwargs) -> float:
    return 0.0

def cost_encryption_violation(flow, encrypted: bool, zone_source: str, zone_dest: str) -> float:
    return 0.0

def cost_cybersecurity(*args, **kwargs) -> float:
    return 0.0