from tg_remote import ssh
import validators


def wol_power_on(proxmox_macaddress, switch_interface, switch_host, switch_user, switch_pass):
    wol_command = f"/tool wol mac={proxmox_macaddress} interface={switch_interface}"
    valid_macaddress = validators.mac_address(proxmox_macaddress)

    if valid_macaddress:
        try:
            ssh(
                host=switch_host,
                username=switch_user,
                password=switch_pass,
                command=wol_command)
            return "Remote command completed"
        except:
            return 



def power_off(proxmox_host, proxmox_pass, proxmox_user):
    shutdown_command = "/usr/sbin/shutdown -h now"
    remote_cli_status = False

    remote_cli = ssh(
        host=proxmox_host, 
        username=proxmox_user, 
        password=proxmox_pass, 
        command=f"{shutdown_command} > /dev/null 2>&1 &")

    if remote_cli == "":
        remote_cli_status = True

    if remote_cli_status:
        return "Remote command completed"



def uptime(proxmox_host, proxmox_pass, proxmox_user):
    uptime_command = "/usr/bin/uptime"

    remote_cli = ssh(
        host=proxmox_host, 
        username=proxmox_user, 
        password=proxmox_pass, 
        command=f"{uptime_command}")

    return remote_cli
