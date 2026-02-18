import socket
import threading
from typing import Any, Dict, List, Optional


class Session:
    def __init__(self, session_id: int, conn: socket.socket, addr: tuple):
        self.id = session_id
        self.conn = conn
        self.addr = addr
        self.ip: str = addr[0]
        self.port: int = addr[1]

    def send(self, data: str) -> None:
        self.conn.sendall((data + '\n').encode())

    def recv(self, timeout: float = 3.0) -> str:
        self.conn.settimeout(timeout)
        response = b''
        try:
            while True:
                chunk = self.conn.recv(4096)
                if not chunk:
                    break
                response += chunk
        except Exception:
            pass
        finally:
            self.conn.settimeout(None)
        return response.decode(errors='replace')

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass


class SessionManager:
    def __init__(self):
        self._sessions: Dict[int, Session] = {}
        self._counter: int = 0
        self._lock = threading.Lock()

    def add_session(self, conn: socket.socket, addr: tuple) -> int:
        with self._lock:
            session_id = self._counter
            self._sessions[session_id] = Session(session_id, conn, addr)
            self._counter += 1
            return session_id

    def get_session(self, session_id: int) -> Optional[Session]:
        with self._lock:
            return self._sessions.get(session_id)

    def remove_session(self, session_id: int) -> None:
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].close()
                del self._sessions[session_id]

    def list_sessions(self) -> List[Session]:
        with self._lock:
            return list(self._sessions.values())

    def close_all(self) -> None:
        with self._lock:
            for session in self._sessions.values():
                session.close()
            self._sessions.clear()