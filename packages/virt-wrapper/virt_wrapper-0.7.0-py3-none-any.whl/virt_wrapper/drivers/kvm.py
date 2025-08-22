"""KVM drivers"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from random import randint
from xml.etree import ElementTree as ET

import libvirt

STATES = {
    libvirt.VIR_DOMAIN_RUNNING: "Running",
    libvirt.VIR_DOMAIN_BLOCKED: "Blocked",
    libvirt.VIR_DOMAIN_PAUSED: "Paused",
    libvirt.VIR_DOMAIN_SHUTDOWN: "Shutdown",
    libvirt.VIR_DOMAIN_SHUTOFF: "Shutoff",
    libvirt.VIR_DOMAIN_CRASHED: "Crashed",
    libvirt.VIR_DOMAIN_NOSTATE: "No state",
}


def libvirt_callback(userdata, err):  # pylint: disable=unused-argument
    """Avoid printing error messages"""


libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)


def request_cred(user: str, password: str):
    """Callback function for authentication"""

    def inner(credentials: list, user_data):  # pylint: disable=unused-argument
        for credential in credentials:
            if credential[0] == libvirt.VIR_CRED_AUTHNAME:
                credential[4] = user
            elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
                credential[4] = password
        return 0

    return inner


SSH_PRIVATE_KEY = os.environ.get("SSH_PRIVATE_KEY", os.path.join(os.path.expanduser("~"), ".ssh", "id_rsa"))


@dataclass(frozen=True)
class KernelVirtualDriver:
    """Common class for connecting to KVM server"""

    host: str
    auth: tuple[str, str]
    ssh_key: str = field(init=False)
    conn: libvirt.virConnect = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "conn", self._connect())

    def _connect(self):
        user, password = self.auth
        if password:
            authd = [
                [libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE],
                request_cred(user, password),
                None,
            ]
            conn = libvirt.openAuth(
                f"qemu+libssh2://{user}@{self.host}/system?sshauth=password&known_hosts_verify=auto",
                authd,
                0,
            )
        elif self.ssh_key:
            conn = libvirt.open(
                f"qemu+libssh2://{user}@{self.host}/system?sshauth=privkey"
                "&keyfile={self.ssh_key}&known_hosts_verify=auto"
            )
        else:
            raise ValueError("At least one SSH key or password is required")

        if conn is None:
            raise ConnectionError(f"Failed to connect to KVM host {self.host}")
        return conn


@dataclass(frozen=True)
class KernelVirtualMachineDriver(KernelVirtualDriver):
    """Driver for managing the KVM virtual machine"""

    uuid: str
    domain: libvirt.virDomain = field(init=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "domain", self.conn.lookupByUUIDString(self.uuid))
        object.__setattr__(self, "uuid", self.domain.UUIDString())

    def get_name(self) -> str:
        """Get the virtual machine name"""
        try:
            return self.domain.metadata(libvirt.VIR_DOMAIN_METADATA_TITLE, None)
        except libvirt.libvirtError:
            return self.domain.name()

    def get_state(self) -> str:
        """Get the virtual machine state"""
        state, _ = self.domain.state()
        return STATES[state]

    def set_name(self, name: str) -> None:
        """Change the virtual machine name"""
        self.domain.setMetadata(libvirt.VIR_DOMAIN_METADATA_TITLE, name, None, None)

    def get_description(self) -> str | None:
        """Get the virtual machine description"""
        try:
            return self.domain.metadata(libvirt.VIR_DOMAIN_METADATA_DESCRIPTION, None)
        except libvirt.libvirtError:
            return None

    def get_guest_os(self) -> str | None:
        """Get the name of the virtual machine guest operating system"""
        try:
            return self.domain.guestInfo().get("os.pretty-name")
        except libvirt.libvirtError:
            return None

    def get_memory_stat(self) -> dict[str, int]:
        """Get the memory statistic of the virtual machine"""
        if self.domain.state()[0] == libvirt.VIR_DOMAIN_SHUTOFF:
            actual = 0
            demand = 0
        else:
            actual = self.domain.memoryStats().get("actual")
            demand = actual - self.domain.memoryStats().get("unused", actual)

        return {
            "startup": self.domain.info()[2],
            "maximum": self.domain.maxMemory(),
            "demand": demand if demand >= 0 else 0,
            "assigned": actual,
        }

    def get_cpus(self) -> int:
        """Get number of cores"""
        return self.domain.info()[3]

    def set_cpus(self, cpus: int) -> None:
        """Change number of cores"""
        self.domain.setVcpusFlags(cpus, libvirt.VIR_DOMAIN_VCPU_MAXIMUM | libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        self.domain.setVcpusFlags(cpus, libvirt.VIR_DOMAIN_AFFECT_CONFIG)

    def get_snapshots(self) -> list:
        """Get the list of the virtual machine snapshots"""
        ret = []
        for snap in self.domain.listAllSnapshots():
            tree_snap = ET.fromstring(snap.getXMLDesc())

            cpus = tree_snap.find("domain/vcpu")
            ram = tree_snap.find("domain/currentMemory")
            description = tree_snap.find("description")
            created_at_ts = tree_snap.find("creationTime")
            try:
                parent = snap.getParent().getName()
            except libvirt.libvirtError:
                parent = None
            ret.append(
                {
                    "name": snap.getName(),
                    "description": description.text if description is not None else None,
                    "local_id": snap.getName(),
                    "parent_name": parent,
                    "created_at_ts": int(created_at_ts.text or 0) if created_at_ts is not None else 0,
                    "is_applied": snap.getName() == self.domain.snapshotCurrent().getName(),
                    "cpus": int(cpus.text or 0) if cpus is not None else 0,
                    "ram": int(ram.text or 0) if ram is not None else 0,
                    "driver": KernelVirtualSnapshotDriver(domain=self.domain, snapshot_id=snap.getName()),
                }
            )

        return ret

    def get_disks(self) -> list[dict]:
        """Get the list of the virtual machine connected disks"""
        ret = []
        for src in ET.fromstring(self.domain.XMLDesc()).findall("devices/disk/source"):
            try:
                if src.get("pool"):
                    storage_pool = self.conn.storagePoolLookupByName(src.get("pool"))
                    volume = storage_pool.storageVolLookupByName(src.get("volume"))
                else:
                    volume = self.conn.storageVolLookupByPath(src.get("file"))
                    storage_pool = volume.storagePoolLookupByVolume()
                _, size, used = volume.info()

                parent_volume = volume
                volume_xml = ET.fromstringlist(volume.XMLDesc())
                while volume_xml.find("backingStore") is not None:
                    parent_volume = volume_xml.find("backingStore/path")
                    if parent_volume is None:
                        raise Exception("Unable to find parent volume path")
                    parent_volume = self.conn.storageVolLookupByPath(parent_volume.text)
                    volume_xml = ET.fromstringlist(parent_volume.XMLDesc())

                ret.append(
                    {
                        "driver": KernelVirtualDiskDriver(path=volume.path(), domain=self.domain),
                        "name": parent_volume.name(),
                        "path": volume.path(),
                        "storage": storage_pool.name(),
                        "size": size,
                        "used": used,
                    }
                )
            except libvirt.libvirtError:
                continue
        return ret

    def get_networks(self) -> list:
        """Get the list of the virtual machine network adapters"""
        ret = []
        for interface in ET.fromstring(self.domain.XMLDesc()).findall("devices/interface"):
            mac = interface.find("mac")
            mac_address = "" if mac is None else mac.get("address", "")

            source = interface.find("source")
            switch_name = "" if source is None else source.get("bridge", "")

            if self.domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
                try:
                    nets = self.domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT)
                except libvirt.libvirtError:
                    nets = self.domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_ARP)
                addresses = []
                for net in nets:
                    if nets[net].get("hwaddr") == mac_address:
                        addrs = nets[net].get("addrs")
                        address = [addr.get("addr") for addr in addrs]
                        addresses.extend(address)
                        break
            else:
                addresses = []

            ret.append({"mac": mac_address.upper(), "switch": switch_name, "addresses": addresses})
        return ret

    def get_displays(self) -> list[dict]:
        """Get virtual displays"""
        ret = []
        for display in ET.fromstring(self.domain.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE)).findall("devices/graphics"):
            ret.append(
                {
                    "Type": display.get("type"),
                    "Port": display.get("port"),
                    "Password": display.get("passwd"),
                }
            )
        return ret

    def run(self) -> None:
        """Power on the virtual machine"""
        self.domain.create()

    def shutdown(self) -> None:
        """Shutdown the virtual machine"""
        self.domain.shutdown()

    def poweroff(self) -> None:
        """Force off the virtual machine"""
        self.domain.destroy()

    def save(self) -> None:
        """Pause the virtual machine and temporarily saving its memory state to a file"""
        self.domain.managedSave()

    def suspend(self) -> None:
        """Pause the virtual machine and temporarily saving its memory state"""
        self.domain.suspend()

    def resume(self) -> None:
        """Unpause the suspended virtual machine"""
        self.domain.resume()

    def snapshot_create(self, name: str, description: str) -> dict:
        """Create a new snapshot of virtual machine"""
        snapshot_xml_template = f"""<domainsnapshot>
            <name>{name}</name>
            <description>{description}</description>
        </domainsnapshot>"""
        self.domain.snapshotCreateXML(snapshot_xml_template, libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_ATOMIC)
        for snap in self.get_snapshots():
            if snap["name"] == name:
                return snap
        raise Exception("Created snapshot wasn't found")

    def export(self, storage: str) -> str:
        """Export the virtual machine to a storage destination"""
        pool = self.conn.storagePoolLookupByName(storage)
        pool = ET.fromstring(pool.XMLDesc()).find("target/path")
        if pool is None or pool.text is None:
            raise ValueError("Unable to find pool")

        target_pool_path = os.path.join(pool.text, self.get_name())
        target_pool_name = f"export_{self.get_name()}"

        xml_pool = f"""<pool type='dir'>
  <name>{target_pool_name}</name>
  <target>
    <path>{target_pool_path}</path>
    <permissions>
      <mode>0777</mode>
    </permissions>
  </target>
</pool>
"""
        target_pool = self.domain.connect().storagePoolCreateXML(xml_pool, libvirt.VIR_STORAGE_POOL_CREATE_WITH_BUILD)
        try:
            for disk in self.get_disks():
                volume = self.conn.storageVolLookupByPath(disk["path"])
                xml_vol = f"""<volume>
  <name>{volume.name()}</name>
  <target>
    <permissions>
      <mode>0644</mode>
      <label>virt_image_t</label>
    </permissions>
  </target>
</volume>"""
                target_pool.createXMLFrom(xml_vol, volume, 0)
        finally:
            target_pool.destroy()

        with open(os.path.join(target_pool_path, "config.xml"), "w", encoding="utf-8") as config:
            config.write(
                self.domain.XMLDesc(
                    libvirt.VIR_DOMAIN_XML_INACTIVE
                    | libvirt.VIR_DOMAIN_XML_UPDATE_CPU
                    | libvirt.VIR_DOMAIN_XML_MIGRATABLE
                )
            )
        return target_pool_path


class KernelVirtualHostDriver(KernelVirtualDriver):
    """Driver for managing KVM server"""

    def get_vms_id(self) -> list[str]:
        """Get list of virtual machines on the hypervisor"""
        return [domain.UUIDString() for domain in self.conn.listAllDomains()]

    def import_vm(self, source: str, storage: str, name: str) -> str:
        """Import a virtual machine from the source"""
        xml_pool = f"""<pool type='dir'>
  <name>import_{name}</name>
  <target>
    <path>{source}</path>
  </target>
</pool>"""
        root = ET.parse(os.path.join(source, "config.xml")).getroot()

        uuid = root.find("uuid")
        if uuid is not None:
            root.remove(uuid)

        xml_name = root.find("name")
        if xml_name is None:
            xml_name = ET.SubElement(root, "name")
            root.insert(3, xml_name)
        xml_name.text = name

        xml_title = root.find("title")
        if xml_title is None:
            xml_title = ET.SubElement(root, "title")
            root.insert(3, xml_title)
        xml_title.text = name

        def random_suffix():
            timestamp = int((datetime.now() - datetime(1970, 1, 1)).total_seconds())
            rand_hex = "".join(f"{randint(0x00, 0xFF):02x}" for _ in range(10))
            return f"_{timestamp}_{rand_hex}"

        target_pool = self.conn.storagePoolLookupByName(storage)
        import_pool = self.conn.storagePoolCreateXML(xml_pool, libvirt.VIR_STORAGE_POOL_CREATE_WITH_BUILD)
        imported_volumes = []
        try:
            for src in root.iterfind("devices/disk/source"):
                source_file = src.get("file") or src.get("volume")
                if source_file is None:
                    raise ValueError("Unable to find virtual disk")
                orig_filename = os.path.basename(source_file)
                import_vol = import_pool.storageVolLookupByName(orig_filename)

                disk_suffix = random_suffix()
                filename = orig_filename
                while filename in target_pool.listVolumes():
                    filename = name + disk_suffix + os.path.splitext(orig_filename)[-1]
                    disk_suffix = random_suffix()

                xml_vol = f"""<volume>
  <name>{filename}</name>
  <target>
    <format type='qcow2'/>
    <permissions>
      <mode>0600</mode>
      <label>virt_image_t</label>
    </permissions>
  </target>
</volume>"""
                target_vol = target_pool.createXMLFrom(xml_vol, import_vol, 0)
                if src.get("file"):
                    src.set("file", target_vol.path())
                elif src.get("volume"):
                    src.set("pool", target_pool.name())
                    src.set("volume", target_vol.name())

                imported_volumes.append(target_vol)
        except Exception as e:
            for volume in imported_volumes:
                volume.destroy()
            raise e
        finally:
            import_pool.destroy()

        for interface in root.findall("devices/interface"):
            for remove_target in ("mac", "address"):  # Remove some options, they will be chosen automatically
                interface_to_remove = interface.find(remove_target)
                if interface_to_remove is None:
                    continue
                interface.remove(interface_to_remove)

        result_domain = self.conn.defineXML(ET.tostring(root, encoding="unicode"))
        return result_domain.UUIDString()

    def get_storages(self) -> list[dict]:
        """Get information about the host storage systems"""
        result = []
        for pool in self.conn.listAllStoragePools():
            info = pool.info()
            result.append(
                {
                    "name": pool.name(),
                    "size": info[1],
                    "used": info[1] - info[3],
                }
            )
        return result


@dataclass(frozen=True)
class KernelVirtualSnapshotDriver:
    """Driver for managing the KVM snapshot"""

    domain: libvirt.virDomain
    snapshot_id: str

    snapshot: libvirt.virDomainSnapshot = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "snapshot", self.domain.snapshotLookupByName(self.snapshot_id))

    def apply(self) -> None:
        """Apply the snapshot"""
        self.domain.revertToSnapshot(self.snapshot)

    def destroy(self) -> None:
        """Destroy the snapshot"""
        self.snapshot.delete()


@dataclass(frozen=True)
class KernelVirtualDiskDriver:
    """Driver for managing the KVM virtual disk"""

    domain: libvirt.virDomain
    path: str
    volume: libvirt.virStorageVol = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "volume", self.domain.connect().storageVolLookupByPath(self.path))

    def resize(self, required_size: int) -> int:
        """Resize the virtual disk"""
        if self.domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
            self.domain.blockResize(self.volume.path(), required_size)
        else:
            self.volume.resize(required_size, libvirt.VIR_STORAGE_VOL_RESIZE_SHRINK)

        return self.volume.info()[1]
