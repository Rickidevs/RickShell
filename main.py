
import argparse
import os
import subprocess
import socket
from colorama import Fore, Style, init
import sys

init(autoreset=True)

def read_template(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(Fore.RED + Style.BRIGHT + f"ERROR: Template file '{file_path}' not found." + Style.RESET_ALL)
        return None
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"ERROR: An unexpected error occurred while reading the template file: {e}" + Style.RESET_ALL)
        return None

def generate_shell(template_path, ip, port):
    shell_code = read_template(template_path)
    if shell_code is None:
        return None
    try:
        shell_code = shell_code.format(ip=ip, port=port)
        return shell_code
    except KeyError as e:
        print(Fore.RED + Style.BRIGHT + f"ERROR: Missing placeholder in template file: {e}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"ERROR: An unexpected error occurred while generating the shell: {e}" + Style.RESET_ALL)
    return None

def apply_ue_option(shell_code, ue_option):
    if ue_option:
        return shell_code.replace(' ', '+')
    return shell_code

def print_shell_command(title, shell_code, ue_option, border_needed):
    if shell_code is None:
        return

    shell_code = apply_ue_option(shell_code, ue_option)

    if border_needed:
        border_length = max(len(title), max(len(line) for line in shell_code.split('\n'))) + 4
        border = "+" + "-" * border_length + "+"
        title_line = f"| {title.center(border_length - 2)} |"
        shell_border = "+" + "-" * border_length + "+"

        print("")
        print(Fore.CYAN + Style.BRIGHT + border + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + title_line + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + border + Style.RESET_ALL)
        print("")

        print(Fore.GREEN + Style.BRIGHT + shell_border)
        shell_lines = shell_code.split('\n')
        for line in shell_lines:
            print(Fore.GREEN + Style.BRIGHT + f"| {line.ljust(border_length - 2)} |")
        print(Fore.GREEN + Style.BRIGHT + shell_border)
        print("")
    else:
        print(Fore.GREEN + Style.BRIGHT + f"{title}:")
        print(Fore.GREEN + Style.BRIGHT + shell_code)
        print("")

def get_local_ip():
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        ip = result.stdout.strip().split()[0]
        return ip
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"ERROR: An unexpected error occurred while fetching local IP: {e}" + Style.RESET_ALL)
        return '127.0.0.1'

def validate_ip(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        num = int(part)
        if num < 0 or num > 255:
            return False
    return True

def print_most_used_commands(ip, port, ue_option):
    commands = read_template('/opt/RickShell/Shell/MostUsed.txt')
    if commands is None:
        return
    try:
        commands = commands.format(ip=ip, port=port)
        title = "Most Used Reverse Shell Commands"
        print_shell_command(title, commands, ue_option, True)
    except KeyError as e:
        print(Fore.RED + Style.BRIGHT + f"ERROR: Missing placeholder in 'MostUsed.txt': {e}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"ERROR: An unexpected error occurred while formatting 'MostUsed.txt': {e}" + Style.RESET_ALL)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return False
        except OSError:
            return True

def generate_sequential_port():
    ports = [4444, 4242, 4040, 445, 8080, 80, 139]
    for port in ports:
        if not is_port_in_use(port):
            return port
    return None

def custom_help_message():
    help_message = f"""
     Usage: RickShell [options]

      {Fore.YELLOW}More: github.com/Rickidevs/RickShell{Fore.RESET}
                 
      -h                Show this help message and exit
      -p,               Platform for the reverse shell (e.g., php, nc, python, bash, perl).
      -ip               IP address for the reverse shell connection.
      -ue               Replace spaces with "+" in the shell code.
      --port            Port for the reverse shell connection.

      no arguments      the most used shell for you, also selects the most appropriate ip and port.

    """
    print(help_message)
    sys.exit()

def get_vpn_ip():
    try:
        result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
        interfaces = result.stdout.splitlines()
        for line in interfaces:
            # 'tun' veya 'tap' arayüzlerini arıyoruz
            if 'tun' in line or 'tap' in line:
                index = interfaces.index(line)
                for subline in interfaces[index:]:
                    if 'inet' in subline:
                        ip = subline.split()[1].split('/')[0]
                        return ip
        print(Fore.RED + Style.BRIGHT + "ERROR: No VPN interface (tun/tap) found." + Style.RESET_ALL)
        return None
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"ERROR: Unable to retrieve VPN IP address: {e}" + Style.RESET_ALL)
        return None


def main():
    parser = argparse.ArgumentParser(add_help=False, description='RickShell - A tool to generate reverse shells for educational purposes.')

    parser.add_argument('-h', '--help', action='store_true', help='Show help message and exit')
    parser.add_argument('-p', '--platform', type=str, help='Platform for the reverse shell (e.g., php, nc, python, bash).')
    parser.add_argument('-ip', type=str, help='IP address for the reverse shell connection.')
    parser.add_argument('--port', type=int, help='Port for the reverse shell connection.')
    parser.add_argument('-ue', action='store_true', help='Replace spaces with "+" in the shell code.')
    parser.add_argument('-vpn', action='store_true', help='Use VPN (tun) interface for the reverse shell connection.')

    args = parser.parse_args()

    if args.help:
        custom_help_message()

    # VPN argümanı verildiyse VPN IP'sini al
    if args.vpn:
        ip = get_vpn_ip()
        if ip is None:
            return
    else:
        ip = args.ip if args.ip else get_local_ip()

    port = args.port if args.port else generate_sequential_port()

    if not validate_ip(ip):
        print(Fore.RED + Style.BRIGHT + "ERROR: Invalid IP address format." + Style.RESET_ALL)
        return

    ue_option = args.ue

    if args.platform:
        platforms = {
            'php': '/opt/RickShell/Shell/php.txt',
            'nc': '/opt/RickShell/Shell/netcat.txt',
            'netcat': '/opt/RickShell/Shell/netcat.txt',
            'python': '/opt/RickShell/Shell/python.txt',
            'bash': '/opt/RickShell/Shell/bash.txt',
            'java': '/opt/RickShell/Shell/java.txt',
            'powershell': '/opt/RickShell/Shell/powershell.txt',
            'ruby': '/opt/RickShell/Shell/ruby.txt',
            'telnet': '/opt/RickShell/Shell/telnet.txt',
        }

        platform = args.platform.lower()

        if platform in platforms:
            template_path = platforms[platform]
            shell_code = generate_shell(template_path, ip, port)
            if shell_code:
                title = f"{platform.capitalize()} Reverse Shell Command"
                border_needed = platform not in ['python', 'powershell']
                print_shell_command(title, shell_code, ue_option, border_needed)
        else:
            print(Fore.RED + Style.BRIGHT + "Unsupported platform. Supported platforms are: php, netcat, python, bash, java, powershell, telnet." + Style.RESET_ALL)
    else:
        if port is None:
            print(Fore.RED + Style.BRIGHT + "ERROR: All ports are in use. Please free up some ports and try again." + Style.RESET_ALL)
            return
        print_most_used_commands(ip, port, ue_option)

if __name__ == "__main__":
    main()
