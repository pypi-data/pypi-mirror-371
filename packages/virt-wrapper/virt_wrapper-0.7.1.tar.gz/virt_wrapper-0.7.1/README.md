# Description

Python wrapper for managing virtual infrastructure based on Hyper-V or KVM (libvirt)

# Example usage
## Get access to particular VM by UUID
```python
from virt_wrapper import *

kvm = VirtualMachine(
    host="linux-server.lan",
    uuid="c7c2f567-064f-464e-9843-1ed55c04f35e",
    platform=HypervisorPlatform.KVM,
    auth=("user", "123456")
)

hvm = VirtualMachine(
    host="windows-server.lan",
    uuid="37a6cee8-f6ce-48c4-a635-7145e8770cca",
    platform=HypervisorPlatform.HYPERV,
    auth=("user", "123456")
)

print(f"Virtual machine on Linux has name: {kvm.name()}\nVirtual machine on Windows has name: {hvm.name()}")

```

## Get all VMs on particular hypervisor
```python
from virt_wrapper import *

hypervisor = Hypervisor(
    host="windows-server.lan",
    platform=HypervisorPlatform.HYPERV,
    auth=("user", "123456")
)

# OR

hypervisor = Hypervisor(
    host="linux-server.lan",
    platform=HypervisorPlatform.KVM,
    auth=("user", "123456")
)

for vm in hypervisor.virtual_machines():
    print(vm.name())
```


# Requirements
## KVM

- SSH-key must be imported on target server
- User must have full access to libvirt
```sh
usermod <your_user> -aG libvirt
systemctl restart libvirtd
```

## Hyper-V
- User must have full access to Hyper-V
- WinRM must be enabled with this parameters
    - HTTPS
    - Basic auth

```powershell
# Enables the WinRM service and sets up the HTTP listener
Enable-PSRemoting -Force

# Create HTTPS listener
$httpsParams = @{
    ResourceURI = 'winrm/config/listener'
    SelectorSet = @{
        Transport = "HTTPS"
        Address   = "*"
    }
    ValueSet = @{
        CertificateThumbprint = ""
        Enabled               = $true
    }
}
New-WSManInstance @httpsParams

# Enable basic auth
Set-Item -Path WSMan:\localhost\Service\Auth\Basic -Value $true

# Opens port 5986 for all profiles
$firewallParams = @{
    Action      = 'Allow'
    Description = 'Inbound rule for Windows Remote Management via WS-Management. [TCP 5986]'
    Direction   = 'Inbound'
    DisplayName = 'Windows Remote Management (HTTPS-In)'
    LocalPort   = 5986
    Profile     = 'Any'
    Protocol    = 'TCP'
}
New-NetFirewallRule @firewallParams
```

# Available functions:
- [x] Managing snapshots
- [x] Managing virtual disks
- [x] Managing networks
- [x] Getting info about VM (state, description, guest OS, etc.)
- [x] Controling VM (run, shutdown, pause, etc)
- [x] Export/Import virtual machines
- [ ] Migrating
- [ ] Cloning
