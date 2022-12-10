## Пример конфигурации:
1. Определяем переменные окружения:
```bash
export PROXMOX_USER="<your_proxmox_user>"
export PROXMOX_PASS="<your_proxmox_password>"
export PROXMOX_HOST="<your_proxmox_ip_address>"
export PROXMOX_MACADDRESS="<proxmox_mac_interface_connected_to_mikrotik>"
export SWITCH_USER="<your_mikrotik_user>"
export SWITCH_PASS="<your_mikrotik_password>"
export SWITCH_HOST="<your_mikrotik_ip_address>"
export SWITCH_INTERFACE="<mikrotik_name_interface_connected_to_proxmox>"
export ZOOKEEPER_HOSTS="<zookeeper_hosts>"
```
2. Редактируем файл `config.yml` в корне проекта:
```yaml
telebot: "<your_telegram_bot_id>"
telegroup: "<your_telegram_group_id>"
terra_project_name: "<your_bot_project-name>"

all_vms_files:
  qemu: "/changer/terra-infra/terraform/qemus.tf"
  lxc: "/changer/terra-infra/terraform/lxcs.tf"
```

## Пример запуска:
```sh
docker run -d --restart=always --name "changer" \
-v "${PWD}/config.yml:/changer/config.yml" \
-v "/root/.ssh:/root/.ssh" noirgt/changer
```

## Главный проект:
https://gitlab.com/noirgt-proxmox/terra-infra
