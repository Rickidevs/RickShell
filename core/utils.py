import ipaddress
import random
import socket
from typing import Dict

import psutil


def get_network_interfaces() -> Dict[str, str]:
    interfaces: Dict[str, str] = {}

    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                try:
                    ipaddress.ip_address(addr.address)
                    interfaces[iface] = addr.address
                    break
                except ValueError:
                    continue

    if not interfaces:
        try:
            ip = socket.gethostbyname(socket.gethostname())
            interfaces['eth0'] = ip
        except Exception:
            interfaces['lo'] = '127.0.0.1'

    return interfaces


def get_random_port() -> int:
    while True:
        port = random.randint(1024, 65535)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', port))
                return port
        except OSError:
            continue


def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_valid_port(port: str) -> bool:
    try:
        p = int(port)
        return 1 <= p <= 65535
    except ValueError:
        return False