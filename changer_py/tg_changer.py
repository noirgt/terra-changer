import os
import json
from jinja2 import Template



def vms_list_creator(vms_file, vms_type):
    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

    vms_file = open(os.path.join(__location__, vms_file), "r")
    vms_list = []
    for vm in vms_file.readlines():
        vm = vm.strip()
        if vm[0] == '"':
            vm = vm.split("{")
            vm_name = vm[0].strip('" :')
            vm_conf = json.loads("{" + vm[1].rstrip(','))
            vms_list.append(
                {
                    "name": vm_name,
                    "conf": vm_conf,
                    "type": vms_type
                }
            )
    return(vms_list)



def vms_writer(vms_type, vms_list, image, dict_vms_files):
    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
    j2_template = open(os.path.join(__location__, "template.j2"), "r").read()
    new_vms_text = Template(j2_template)
    vms_file = dict_vms_files[vms_type]
    vms_type = vms_type + "s"
    new_vms_text = new_vms_text.render(
        vms_type=vms_type,
        vms_list=vms_list,
        image=image
        )

    with open(os.path.join(__location__, vms_file), "w") as vms_file:
        vms_file.write(new_vms_text)



def vms_changer(vms_string, dict_vms_files):
    new_vm_image = "Debian10x64-terraform"
    vms_string = vms_string.strip().split(":")
    vms_prefix = vms_string[0].strip().split()

    new_vms_list = vms_string[1].strip().split(",")
    vms_type = vms_prefix[0].strip()
    vms_action = vms_prefix[1].strip()
    vms_file = dict_vms_files[vms_type]
    file_vms_list = vms_list_creator(vms_file, vms_type)

    if vms_action == "add":
        for new_vm in new_vms_list:
            new_vm = new_vm.strip()
            new_vm_name = new_vm.split("/")[0]
            new_vm_conf = {
                'cores': new_vm.split("/")[1],
                'memory': new_vm.split("/")[2]}
            if vms_type == "qemu":
                new_vm_conf['image'] = new_vm_image
            new_vm_exists = False

            for file_vm in file_vms_list:
                if new_vm_name == file_vm["name"]:
                    file_vm["conf"]["cores"] = new_vm_conf["cores"]
                    file_vm["conf"]["memory"] = new_vm_conf["memory"]
                    new_vm_exists = True
                    break

            if not new_vm_exists:
                file_vms_list.append({
                    'name': new_vm_name,
                    'conf': new_vm_conf,
                    'type': vms_type
                })

    elif vms_action == "delete":
        new_file_vms_list = []
        new_vms_list = [s.strip() for s in new_vms_list]
 
        for file_vm in file_vms_list:
            if file_vm["name"] in new_vms_list:
                continue
            new_file_vms_list.append(file_vm)
        
        file_vms_list = new_file_vms_list

    vms_writer(
        vms_type=vms_type,
        vms_list=file_vms_list,
        image=new_vm_image,
        dict_vms_files=dict_vms_files
        )

    return "Successfully. The Terraform configuration has been changed."
