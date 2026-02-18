import socket
import threading
from typing import Callable, Optional

from core.session_manager import SessionManager
from interface.colors import Colors

BIND_HOST = '0.0.0.0'


class Listener(threading.Thread):
    def __init__(
        self,
        host: str,
        port: int,
        session_manager: SessionManager,
        on_connect: Optional[Callable[[int, str, int], None]] = None,
    ):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.session_manager = session_manager
        self.on_connect = on_connect
        self._running = False
        self._server_socket: Optional[socket.socket] = None

    def run(self) -> None:
        self._running = True
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self._server_socket.bind((BIND_HOST, self.port))
            self._server_socket.listen(10)
            print(
                f"\n{Colors.success(f'[*] Listener started — binding {BIND_HOST}:{self.port}, payload LHOST: {self.host}')}"
            )
            print(Colors.dim(f"    Waiting for incoming connections...\n"))

            while self._running:
                try:
                    self._server_socket.settimeout(1.0)
                    conn, addr = self._server_socket.accept()
                    session_id = self.session_manager.add_session(conn, addr)
                    print(
                        f"\n{Colors.bold(Colors.GREEN + '[+]' + Colors.ENDC)} "
                        f"New connection from {Colors.info(addr[0])}:{Colors.warn(str(addr[1]))} "
                        f"— {Colors.bold('Session ID:')} {Colors.success(str(session_id))}"
                    )
                    if self.on_connect:
                        self.on_connect(session_id, addr[0], addr[1])
                except socket.timeout:
                    continue
                except OSError:
                    break
        except Exception as exc:
            print(Colors.error(f"[!] Listener error: {exc}"))
        finally:
            if self._server_socket:
                try:
                    self._server_socket.close()
                except Exception:
                    pass

    def stop(self) -> None:
        self._running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass

    @property
    def is_running(self) -> bool:
        return self._running and self.is_alive()