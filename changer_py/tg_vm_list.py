from tg_manager import proxmox_list
from tg_changer import vms_list_creator



def vm_list(all_vms_files, proxmox_host, proxmox_pass, proxmox_user):
    proxmox_dict = proxmox_list(
        proxmox_host=proxmox_host, 
        proxmox_pass=proxmox_pass, 
        proxmox_user=proxmox_user)
    vm_list = vms_list_creator(all_vms_files["qemu"], "qemu") + \
        vms_list_creator(all_vms_files["lxc"], "lxc")

    lengt_vm_name = 0
    for vm in vm_list:
        if "name" in vm:
            if len(vm["name"]) > lengt_vm_name:
                lengt_vm_name = len(vm["name"])

    vm_table = "Name".ljust(lengt_vm_name, " ") \
        + "\tCPU".ljust(7, " ") + "Mem".ljust(7, " ") + "Type".ljust(7, " ") + "Status"
    vm_table = vm_table + f"\n{'-' * len(vm_table)}"

    for vm in vm_list:
        if "name" in vm:
            vm_status = "None"
            full_vm_name = f"{vm['type']}-{vm['name']}"
            if full_vm_name in proxmox_dict:
                if proxmox_dict[full_vm_name]['type'] == vm['type']:
                    vm_status = proxmox_dict[full_vm_name]['status']

            vm_table = vm_table + f"\n{vm['name']}".ljust(lengt_vm_name + 1, " ") + \
                f"\t{vm['conf']['cores']}".ljust(7, " ") + \
                    f"{float(vm['conf']['memory'])}".ljust(7, " ") + \
                        f"{vm['type']}".ljust(7, " ") + vm_status
    
    return vm_table
