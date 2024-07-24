import argparse
import os
from colorama import Fore, Style

def read_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def generate_php_shell(ip, port, output_file):
    try:
        template_path = 'php_reverse_shell_template.php'
        shell_code = read_template(template_path).format(ip=ip, port=port)
        
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(output_file, 'w') as file:
            file.write(shell_code)
        print(Fore.GREEN + Style.BRIGHT + f"PHP reverse shell saved to {output_file}" + Style.RESET_ALL)
    except PermissionError:
        print(Fore.RED + Style.BRIGHT + f"ERROR: Permission denied. Cannot  write to {output_file}. Please check your permissions." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"ERROR: An unexpected error occurred: {e}" + Style.RESET_ALL)

def generate_php_single_line_shell(ip, port):
    try:
        template_path = 'php_single_line_shell_template.txt'
        shell_code = read_template(template_path).format(ip=ip, port=port)
        print("")
        print(Fore.CYAN + Style.BRIGHT + "    PHP Reverse Shell Command        \n" + Style.RESET_ALL)
        print(Fore.GREEN + shell_code + Style.RESET_ALL)
        
    except FileNotFoundError:
        print(Fore.RED + Style.BRIGHT + f"ERROR: Template file '{template_path}' not found." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"ERROR: An unexpected error occurred: {e}" + Style.RESET_ALL)

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

def main():
    parser = argparse.ArgumentParser(description='RickShell - A tool to generate reverse shells for educational purposes.')
    parser.add_argument('-p', '--platform', type=str, required=True, help='Platform for the reverse shell (e.g., php).')
    parser.add_argument('-o', '--output', type=str, help='Output file name for the reverse shell.')
    parser.add_argument('-ip', type=str, required=True, help='IP address for the reverse shell connection.')
    parser.add_argument('-port', type=int, required=True, help='Port for the reverse shell connection.')

    args = parser.parse_args()

    if not validate_ip(args.ip):
        print(Fore.RED + Style.BRIGHT + "ERROR: Invalid IP address format." + Style.RESET_ALL)
        return

    if args.platform.lower() == 'php':
        if args.output:
            generate_php_shell(args.ip, args.port, args.output)
        else:
            generate_php_single_line_shell(args.ip, args.port)
    else:
        print(Fore.RED + Style.BRIGHT + "Unsupported platform. Currently, only PHP is supported." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
