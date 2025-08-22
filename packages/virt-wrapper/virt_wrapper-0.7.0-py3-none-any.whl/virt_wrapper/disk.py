"""Virtual machine disks management module"""

from dataclasses import dataclass, field
from pathlib import Path

from .drivers.hyperv import HyperVirtualDiskDriver
from .drivers.kvm import KernelVirtualDiskDriver


@dataclass(frozen=True)
class VirtualDisk:
    """Data structure that contains the virtual machine disk info"""

    driver: HyperVirtualDiskDriver | KernelVirtualDiskDriver = field(repr=False)
    name: str
    path: str | Path
    storage: str
    size: int
    used: int

    def __post_init__(self):
        object.__setattr__(self, "path", Path(self.path))

    def resize(self, required_size: int) -> None:
        """Resize the virtual disk"""
        new_size = self.driver.resize(required_size)
        object.__setattr__(self, "size", new_size)
