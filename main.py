import sys
import os
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
sys.path.append(rf'{__location__}/changer_py')
from tg_changer import vms_list_creator, vms_changer
from tg_manager import vm_launch_manager
from tg_vm_list import vm_list
from tg_powermanager import wol_power_on, power_off, uptime
from subprocess import check_output
import telebot
import telegram
import time
import os
import yaml
import validators
from kazoo.client import KazooClient

with open(os.path.join(__location__, 'config.yml')) as conf_file:
    changer_conf = yaml.full_load(conf_file)
print(changer_conf)

tele_bot = changer_conf["telebot"]
tele_group = int(changer_conf["telegroup"])
all_vms_files = changer_conf["all_vms_files"]
terra_project_name = changer_conf["terra_project_name"]

bot = telebot.TeleBot(tele_bot)
group_id = tele_group

proxmox_user = os.environ['PROXMOX_USER']
proxmox_pass = os.environ['PROXMOX_PASS']
proxmox_host = os.environ['PROXMOX_HOST']
proxmox_macaddress = os.environ['PROXMOX_MACADDRESS']
switch_user = os.environ['SWITCH_USER']
switch_pass = os.environ['SWITCH_PASS']
switch_host = os.environ['SWITCH_HOST']
switch_interface = os.environ['SWITCH_INTERFACE']
zookeeper_hosts = os.environ['ZOOKEEPER_HOSTS']
zk = KazooClient(hosts=zookeeper_hosts)

help_bot = """
Добавление VM: `[qemu|lxc] add: <name1>/<cores>/<ram>, <name2>/<cores>/<ram>`
Удаление VM: `[qemu|lxc] delete: <name1>, <name2>`
Запуск/остановка VM: `[qemu|lxc] [start|stop]: <name1>, <name2>`

Проверить бота: `check bot`
Проверить версию бота `version bot`
Вызов справки: `help bot`

Список всех VM: `vm list`
Подробный список всех VM: `vm list raw`

Вкл/выкл Proxmox: `power [on|off]`
Время работы Proxmox: `uptime`
"""

@bot.message_handler(content_types=["text"])



def main(message):
    if (group_id == message.chat.id):
        command = message.text



        def command_changer():
            try:
                git_pull = os.popen(
                    f"cd ./{terra_project_name} && git pull").read()
                print(git_pull)
                bot.send_message(
                    message.chat.id, vms_changer(command, all_vms_files))
                git_push = os.popen(
                    f"cd ./{terra_project_name} && git add -A && \
                    git commit -m 'Telegram: {command}' && git push").read()
                print(git_push)

            except:
                bot.send_message(message.chat.id, "Invalid input.")



        # VM ADD/CHANGE
        if command.split(":")[0].strip() in ["lxc add", "qemu add"]:
            all_vm_params = command.split(":")[1].strip()
            all_vm_params = all_vm_params.split(",")
            for vm_params in all_vm_params:
                vm_params = vm_params.split("/")
                vm_name = vm_params[0].strip()
                vm_cpu = vm_params[1]
                vm_mem = vm_params[2]

                def isfloat(num):
                    try:
                        float(num)
                        return True
                    except ValueError:
                        return False

                valid_vm_name = validators.domain(f"{vm_name}.vm")
                valid_vm_cpu = vm_cpu.isdigit()
                valid_vm_mem = vm_mem.isdigit() or isfloat(vm_mem)
                
                if valid_vm_name and valid_vm_cpu and valid_vm_mem:
                    if float(vm_cpu) >= 0 and float(vm_cpu) < 100 \
                        and float(vm_mem) >= 0 and float(vm_mem) < 100:
                        print(f"{vm_name} - is valid")
                    else:
                        return
                
            print(command)
            command_changer()
        
        # VM DELETE
        elif command.split(":")[0].strip() in ["lxc delete", "qemu delete"]:
            print(command)
            command_changer()

        # VM LAUNCH MANAGER
        elif command.split(":")[0].strip() in [
            "lxc start", 
            "lxc stop", 
            "qemu start", 
            "qemu stop"]:
            remote_command = vm_launch_manager(
                command=command,
                proxmox_host=proxmox_host,
                proxmox_pass=proxmox_pass,
                proxmox_user=proxmox_user
        )

            print(remote_command)
            bot.send_message(message.chat.id, remote_command)

        # VM LIST
        elif command == "vm list":
            git_pull = os.popen(f"cd ./{terra_project_name} && git pull").read()
            print(git_pull)

            vm_table = vm_list(
                all_vms_files=all_vms_files,
                proxmox_host=proxmox_host,
                proxmox_pass=proxmox_pass,
                proxmox_user=proxmox_user
            )

            bot.send_message(message.chat.id, "```\n" + vm_table + "\n```", 
            parse_mode=telegram.ParseMode.MARKDOWN)

        # VM LIST RAW
        elif command == "vm list raw":
            git_pull = os.popen(f"cd ./{terra_project_name} && git pull").read()
            print(git_pull)
            for vm_type in ["qemu", "lxc"]:
                vm_type_length = (len(vm_type) + 1)* '-'
                bot.send_message(message.chat.id, f"{vm_type}:\
                        \n{vm_type_length}\n\
                        {vms_list_creator(all_vms_files[vm_type], vm_type)}")

        # VM POWER MANAGER
        elif command.split()[0].strip() == "power":
            power_action = command.split()[1].strip()
            if power_action == "on":
                remote_command = wol_power_on(
                    proxmox_macaddress = proxmox_macaddress,
                    switch_interface = switch_interface,
                    switch_host = switch_host,
                    switch_pass = switch_pass,
                    switch_user = switch_user
                )
            
            elif power_action == "off":
                remote_command = power_off(
                    proxmox_host=proxmox_host,
                    proxmox_pass=proxmox_pass,
                    proxmox_user=proxmox_user     
                )
            bot.send_message(message.chat.id, remote_command)

        # PROXMOX UPTIME
        elif command == "uptime":
            remote_command = uptime(
                proxmox_host=proxmox_host,
                proxmox_pass=proxmox_pass,
                proxmox_user=proxmox_user     
            )
            bot.send_message(message.chat.id, remote_command)

        # CHECK BOT
        elif command == "check bot":
            bot.send_message(message.chat.id, check_output("date", shell = True))

        # VERSION BOT
        elif command == "version bot":
            bot.send_message(message.chat.id, os.environ['CHANGER_VERSION'])

        # HELP BOT
        elif command == "help bot":
            bot.send_message(message.chat.id, help_bot.strip(), 
            parse_mode=telegram.ParseMode.MARKDOWN)



if __name__ == '__main__':
    zk.start()
    lock = zk.Lock("/changer", "lock-ident")
    while True:
        try:
            lock.acquire(blocking=True, timeout=10, ephemeral=True)
            bot.polling(none_stop=True)
            lock.release()
        except:
            lock.release()
            time.sleep(10)
