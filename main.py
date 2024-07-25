import argparse
import os
import random
import subprocess
import socket
from colorama import Fore, Style, init
import sys

# Renk ve stil başlatma
init(autoreset=True)

def read_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def generate_shell(template_path, ip, port):
    try:
        shell_code = read_template(template_path).format(ip=ip, port=port)
        return shell_code
    except FileNotFoundError:
        print(Fore.RED + Style.BRIGHT + f"ERROR: Template file '{template_path}' not found." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"ERROR: An unexpected error occurred: {e}" + Style.RESET_ALL)

def print_shell_command(title, shell_code):
    # Başlık ve sınır genişliği ayarları
    border_length = max(len(title), max(len(line) for line in shell_code.split('\n'))) + 4
    border = "+" + "-" * border_length + "+"
    title_line = f"| {title.center(border_length - 2)} |"
    shell_border = "+" + "-" * border_length + "+"

    print("")
    print(Fore.CYAN + Style.BRIGHT + border + Style.RESET_ALL)
    print(Fore.CYAN + Style.BRIGHT + title_line + Style.RESET_ALL)
    print(Fore.CYAN + Style.BRIGHT + border + Style.RESET_ALL)
    print("")

    # Shell komutları için kutu
    print(Fore.GREEN + Style.BRIGHT + shell_border)
    shell_lines = shell_code.split('\n')
    for line in shell_lines:
        # Her komutu sınır içine sığdırmak için hizalama
        print(Fore.GREEN + Style.BRIGHT + f"| {line.ljust(border_length - 2)} |")
    print(Fore.GREEN + Style.BRIGHT + shell_border)
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

def print_most_used_commands(ip, port):
    try:
        commands = read_template('MostUsed.txt').format(ip=ip, port=port)
        title = "Most Used Reverse Shell Commands"
        print_shell_command(title, commands)
    except FileNotFoundError:
        print(Fore.RED + Style.BRIGHT + "ERROR: 'MostUsed.txt' file not found." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"ERROR: An unexpected error occurred: {e}" + Style.RESET_ALL)

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
    help_message = """
    Usage: script.py [options]

    Options:
      -h, --help        Show this help message and exit
      -p, --platform    Platform for the reverse shell (e.g., php, nc, python, bash, perl).
      -ip               IP address for the reverse shell connection.
      --port            Port for the reverse shell connection.

    Description:
      RickShell - A tool to generate reverse shells for educational purposes.
    """
    print(help_message)
    sys.exit()

def main():
    parser = argparse.ArgumentParser(add_help=False, description='RickShell - A tool to generate reverse shells for educational purposes.')

    parser.add_argument('-h', '--help', action='store_true', help='Show help message and exit')
    parser.add_argument('-p', '--platform', type=str, help='Platform for the reverse shell (e.g., php, nc, python, bash, perl).')
    parser.add_argument('-ip', type=str, help='IP address for the reverse shell connection.')
    parser.add_argument('--port', type=int, help='Port for the reverse shell connection.')

    args = parser.parse_args()

    if args.help:
        custom_help_message()

    ip = args.ip if args.ip else get_local_ip()
    port = args.port if args.port else generate_sequential_port()

    if not validate_ip(ip):
        print(Fore.RED + Style.BRIGHT + "ERROR: Invalid IP address format." + Style.RESET_ALL)
        return

    if args.platform:
        platforms = {
            'php': 'php.txt',
            'nc': 'netcat.txt',
            'netcat': 'netcat.txt',
            'python': 'python.txt',
            'bash': 'bash.txt',
            'perl': 'perl.txt',
            'java': 'java.txt',
            'nodejs': 'nodejs.txt',
            'powershell': 'powershell.txt',
            'ruby': 'ruby.txt',
            'telnet': 'telnet.txt',
        }

        platform = args.platform.lower()

        if platform in platforms:
            template_path = platforms[platform]
            shell_code = generate_shell(template_path, ip, port)
            if shell_code:
                title = f"{platform.capitalize()} Reverse Shell Command"
                print_shell_command(title, shell_code)
        else:
            print(Fore.RED + Style.BRIGHT + "Unsupported platform. Supported platforms are: php, nc, netcat, python, bash, perl, java, nodejs, powershell, ruby, telnet." + Style.RESET_ALL)
    else:
        if port is None:
            print(Fore.RED + Style.BRIGHT + "ERROR: All ports are in use. Please free up some ports and try again." + Style.RESET_ALL)
            return
        print_most_used_commands(ip, port)

if __name__ == "__main__":
    main()
