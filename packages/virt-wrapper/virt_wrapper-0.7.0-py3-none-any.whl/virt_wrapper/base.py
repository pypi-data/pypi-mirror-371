"""Base module"""

import enum
from dataclasses import dataclass, field
from typing import Any

from .drivers.hyperv import HyperVirtualHostDriver, HyperVirtualMachineDriver
from .drivers.kvm import KernelVirtualHostDriver, KernelVirtualMachineDriver


@enum.unique
class HypervisorPlatform(enum.Enum):
    KVM = "kvm"
    HYPERV = "hyperv"


HostDriverType = (
    KernelVirtualHostDriver | HyperVirtualHostDriver | KernelVirtualMachineDriver | HyperVirtualMachineDriver
)


@dataclass(frozen=True)
class Base:
    host: str
    platform: HypervisorPlatform
    auth: tuple[str, str]
    driver: Any = field(init=False, repr=False)

    __driver_map__: dict[HypervisorPlatform, Any] = field(init=False, repr=False)

    def __post_init__(self):
        if not hasattr(self, "__driver_map__") or not self.__driver_map__:
            raise NotImplementedError("Subclasses must define 'DRIVER_MAP' or override __post_init__")

        driver_cls = self.__driver_map__.get(self.platform)
        if not driver_cls:
            raise ValueError("Unknown type of hypervisor")
        object.__setattr__(self, "__driver_cls__", driver_cls)
