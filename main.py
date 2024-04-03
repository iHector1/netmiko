import netmiko as nt
import re
import sys

def main():
    sys.stdout = open('resultado.txt', 'w')
    routerInformation = {
        'device_type' : 'cisco_nxos',
        'host' :'sandbox-iosxr-1.cisco.com',
        'username' : 'admin',
        'password' : 'C1sco12345'
    }
    router = nt.ConnectHandler(**routerInformation)
    if isAlive(router):
        changedBanner(router)
        showVersion(router)
        configureInterface(router)
        showInterfaces(router)
    else:
        print("Router is dead")
    
    router.disconnect()
    sys.stdout.close()

def isAlive(router):
    return router.is_alive()

def changedBanner(router):
    router.send_command('conf t')
    router.send_command('banner motd #hola#')
    router.send_command('end')
    bannerNew = router.send_command('show banner motd')
    print(bannerNew)

def showVersion(router):
    version = router.send_command('show version')
    uptime = re.search(r'uptime is (.+)', version)
    if uptime:
        print(uptime.group(1))
    else:
        print("No uptime found")

def configureInterface(router):
    commands = [
        "interface GigabitEthernet0/0/3",
        "description GigabitEthernet0/0/0/3",
        "ip address 10.10.10.2 255.255.255.0",
        "no shutdown",
    ]
    router.send_config_set(commands)
    commands = [
        "interface GigabitEthernet0/0/0/2",
        "description GigabitEthernet0/0/0/2",
        "ip address 10.10.11.2 255.255.255.0",
        "no shutdown",
    ]
    router.send_config_set(commands)

def showInterfaces(router):
    interfaces = router.send_command('show run')
    interface_blocks = interfaces.split('!')
    for block in interface_blocks:
        if block.strip().startswith("interface GigabitEthernet"):
            name = re.search(r"interface (GigabitEthernet.*)", block)
            description = re.search(r"description (.*)", block)
            ip_address = re.search(r"ipv4 address (.*) (.*)", block)
            if name:
                print("------------------------------------")
                print(f"{name.group(1)}")
                print(f"description: {description.group(1) if description else 'No se encontro resultado'}")
                print(f"ip: {ip_address.group(1) if ip_address else 'No se encontro resultado'}")
                print(f"mascara: {ip_address.group(2) if ip_address else 'No se encontro resultado'}") 
                estatus = router.send_command(f"sh interface {name.group(1)}")
                status_regex = r"is (.*),"
                match = re.search(status_regex, estatus)
                if match:
                    status = match.group(1)
                    print(f"estatus: {status}")
                else:
                    print("estatus: no encontrado")

if __name__ == '__main__':
    main()
