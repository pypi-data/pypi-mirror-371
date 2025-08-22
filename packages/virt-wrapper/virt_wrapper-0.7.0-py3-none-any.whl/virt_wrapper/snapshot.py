"""Virtual machine snapshots management module"""

from dataclasses import InitVar, dataclass, field
from datetime import datetime

from .drivers.hyperv import HyperVirtualSnapshotDriver
from .drivers.kvm import KernelVirtualSnapshotDriver


@dataclass(frozen=True)
class VirtualSnapshot:
    """Data structure that contains the virtual machine snapshot info"""

    driver: HyperVirtualSnapshotDriver | KernelVirtualSnapshotDriver = field(repr=False)
    created_at: datetime = field(init=False)
    created_at_ts: InitVar[int]
    local_id: str
    name: str
    parent_name: str
    is_applied: bool
    cpus: int
    ram: int
    description: str | None = None

    def __post_init__(self, created_at_ts: int):
        object.__setattr__(self, "created_at", datetime.fromtimestamp(created_at_ts))

    def apply(self) -> None:
        """Apply the snapshot"""
        self.driver.apply()

    def destroy(self) -> None:
        """Destroy the snapshot"""
        self.driver.destroy()
