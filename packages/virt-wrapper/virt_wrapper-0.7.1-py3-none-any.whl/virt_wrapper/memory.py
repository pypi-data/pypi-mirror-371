"""Virtual machine memory management module"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryStat:
    """Data structure that contains the virtual machine memory statistic"""

    startup: int
    maximum: int
    demand: int
    assigned: int
