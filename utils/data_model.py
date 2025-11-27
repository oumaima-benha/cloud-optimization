from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

@dataclass
class Service:
    id: str
    cpu: float
    mem: float
    storage: float
    allowed_regions: List[str]
    zone: str    # type of security zone (public, internal, restricted, etc.)
    sla: Optional[float] = None  # e.g., 99.9%

@dataclass
class MachineType:
    id: str
    cpu: float
    mem: float
    storage: float
    bandwidth: float

@dataclass
class Region:
    id: str

@dataclass
class Flow:
    src: str      # service id
    dst: str      # service id
    bw: float     # Mbps
    latency_max: float  # ms
    encryption_required: bool = False

# Elements needed for a computing instance
@dataclass
class Instance:
    services: Dict[str, Service]
    machines: Dict[str, MachineType]
    regions: Dict[str, Region]
    flows: List[Flow]
    latency: Dict[Tuple[str,str], float]  # key is a tuple (region_i, region_j)
    transfer_cost: Dict[Tuple[str,str], float]  # (region_i, region_j) -> $/GB
    security_rules: Dict[Tuple[str,str], bool]  # (zone_i, zone_j) -> communication allowed?

# Candidate solution
@dataclass
class Placement:
    placement: Dict[str, Tuple[str,str]] = field(default_factory=dict)
    redundancy: Dict[str, int] = field(default_factory=dict)
    encryption: Dict[Tuple[str,str], bool] = field(default_factory=dict)

    def copy(self):
        return Placement(
            placement=self.placement.copy(),
            redundancy=self.redundancy.copy(),
            encryption=self.encryption.copy()
        )
'''
Example:
placement = {
  "s1": ("m_small", "r1"),  # service s1 on machine m_small in region r1
  "s2": ("m_medium", "r2")
}
redundancy = {"s1": 2, "s2": 1}
encryption = {("s1","s2"): True}
'''