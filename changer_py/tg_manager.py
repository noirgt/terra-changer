from tg_remote import ssh
import validators



def proxmox_list(proxmox_host, proxmox_pass, proxmox_user):
    vm_dict = {}
    
    lxc_list = ssh(
        host=proxmox_host, 
        username=proxmox_user, 
        password=proxmox_pass, 
        command="grep 'hostname: ' /etc/pve/lxc/* \
                | sed 's/\.conf\:hostname//g'").split("\n")[0:-1]
    
    lxc_run_list = ssh(
        host=proxmox_host, 
        username=proxmox_user, 
        password=proxmox_pass, 
        command="lxc-ls --running").split(" \n")[0:-1]

    qm_list = ssh(
        host=proxmox_host, 
        username=proxmox_user, 
        password=proxmox_pass, 
        command="qm list | awk '{{print $1, $2, $3}}'").split("\n")[1:-1]

    for lxc in lxc_list:
        lxc = lxc.split(":")
        lxc_id = lxc[0].split("/")[-1]
        lxc_name = lxc[1].strip()
        if lxc_id in lxc_run_list:
            lxc_status = "On"
        else:
            lxc_status = "Off"
        vm_dict[lxc_name] = {"id": lxc_id, "status": lxc_status, "type": "lxc"}

    for qm in qm_list:
        qm_id = qm.split()[0].strip()
        qm_name = qm.split()[1].strip()
        qm_status = qm.split()[2].strip()
        if qm_status != "stopped":
            qm_status = "On"
        else:
            qm_status = "Off"
        vm_dict[qm_name] = {"id": qm_id, "status": qm_status, "type": "qemu"}

    return vm_dict



def vm_launch_manager(command, proxmox_host, proxmox_user, proxmox_pass):
    proxmox_dict = proxmox_list(
        proxmox_host=proxmox_host, 
        proxmox_pass=proxmox_pass, 
        proxmox_user=proxmox_user)

    vm_header = command.split(":")[0].strip()
    vm_type = vm_header.split(" ")[0].strip()
    vm_action = vm_header.split(" ")[1].strip()
    vm_names = command.split(":")[1].strip()
    vm_names_list = vm_names.split(",")
    remote_cli_status = False

    for vm_name in vm_names_list:
        vm_name = vm_name.strip()
        vm_name = f"{vm_type}-{vm_name}"
        valid_vm_name = validators.domain(f"{vm_name}.vm")

        if valid_vm_name and vm_name in proxmox_dict \
            and proxmox_dict[vm_name]['type'] == vm_type:
            cli_dict = {
                "lxc": {
                    "start": "lxc-start",
                    "stop": "lxc-stop"
                    },
                "qemu": {
                    "start": "qm start",
                    "stop": "qm stop"
                    }
                }

            vm_id = proxmox_dict[vm_name]['id']
            cli = f"{cli_dict[vm_type][vm_action]} {vm_id}"

            remote_cli = ssh(
                host=proxmox_host, 
                username=proxmox_user, 
                password=proxmox_pass, 
                command=f"{cli} > /dev/null 2>&1 &")
            
            if remote_cli == "":
                remote_cli_status = True

    if remote_cli_status:
        return "Remote command completed"
