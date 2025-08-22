"""Hypervisors management module"""

from dataclasses import dataclass, field

from .base import Base, HypervisorPlatform
from .drivers.hyperv import HyperVirtualHostDriver
from .drivers.kvm import KernelVirtualHostDriver
from .storage import Storage
from .vm import VirtualMachine


@dataclass(frozen=True)
class Hypervisor(Base):
    """Essential class for managing the hypervisor"""

    __driver_map__ = {
        HypervisorPlatform.KVM: KernelVirtualHostDriver,
        HypervisorPlatform.HYPERV: HyperVirtualHostDriver,
    }
    __driver_cls__: type[KernelVirtualHostDriver] | type[HyperVirtualHostDriver] = field(init=False, repr=False)

    driver: KernelVirtualHostDriver | HyperVirtualHostDriver = field(init=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()

        object.__setattr__(self, "driver", self.__driver_cls__(host=self.host, auth=self.auth))

    def virtual_machines(self) -> list[VirtualMachine]:
        """Get list of virtual machines on the hypervisor"""
        return [
            VirtualMachine(host=self.host, uuid=uuid, platform=self.platform, auth=self.auth)
            for uuid in self.driver.get_vms_id()
        ]

    def import_vm(self, source: str, storage: str, name: str) -> VirtualMachine:
        """Import a virtual machine from a source path"""
        return VirtualMachine(
            host=self.host,
            uuid=self.driver.import_vm(source=source, storage=storage, name=name),
            platform=self.platform,
            auth=self.auth,
        )

    def storages(self) -> list[Storage]:
        """Get information about the host storage systems"""
        return [Storage(**storage) for storage in self.driver.get_storages()]
