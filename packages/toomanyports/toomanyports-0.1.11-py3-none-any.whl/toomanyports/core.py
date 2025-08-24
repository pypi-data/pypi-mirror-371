import os
import socket
import psutil
from typing import List, Tuple, Optional, Dict, Set
from loguru import logger as log


class PortManager:
    """Port allocation, availability checks, process cleanup, and usage reporting."""

    # Class variable to track reserved ports
    _reserved_ports: Set[int] = set()

    def __repr__(self):
        return "[TooManyPorts]"

    @staticmethod
    def is_available(port: int) -> bool:
        """Return True if the port can be bound (i.e., is free) and not reserved."""
        # Check if port is reserved by us
        if port in PortManager._reserved_ports:
            return False

        try:
            with socket.socket() as sock:
                sock.bind(("", port))
            return True
        except OSError:
            return False

    @classmethod
    def find(cls, start: int = 3000, count: int = 1) -> List[int]:
        """Find `count` available ports, searching from `start` upward."""
        out: List[int] = []
        p = start
        while len(out) < count and p < 65535:
            if cls.is_available(p):
                out.append(p)
                cls._reserved_ports.add(p)  # Reserve the port
            p += 1
        if len(out) < count:
            raise RuntimeError(f"{cls}: could not find {count} ports from {start}")
        return out

    @classmethod
    def reserve_port(cls, port: int) -> bool:
        """Manually reserve a specific port."""
        if cls.is_available(port):
            cls._reserved_ports.add(port)
            return True
        return False

    @classmethod
    def release_port(cls, port: int) -> None:
        """Release a reserved port back to the pool."""
        cls._reserved_ports.discard(port)

    @classmethod
    def get_reserved_ports(cls) -> Set[int]:
        """Get all currently reserved ports."""
        return cls._reserved_ports.copy()

    @staticmethod
    def kill(port: int, force: bool = True) -> bool:
        """Kill the process listening on `port`. Skip if it's the current process."""
        me = os.getpid()
        found = False
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                found = True
                pid = conn.pid
                if pid == me:
                    log.warning(f"{PortManager}: skipping kill of current process (pid={me}) on port {port}")
                    continue
                proc = psutil.Process(pid)
                try:
                    if force:
                        proc.kill()
                    else:
                        proc.terminate()
                except Exception as e:
                    log.error(f"{PortManager}: failed killing pid {pid}: {e}")
                    return False
                else:
                    log.success(f"{PortManager}: killed pid {pid} on port {port}")
                    # Release the port when we kill the process
                    PortManager.release_port(port)
                    return True
        if not found:
            log.debug(f"{PortManager}: no listener found on port {port}")
        return found

    @classmethod
    def kill_all(cls, ports: List[int]) -> Dict[int, bool]:
        """Kill processes listening on each port in `ports`."""
        return {p: cls.kill(p) for p in ports}

    @classmethod
    def list_usage(cls, port_range: Tuple[int, int] = (3000, 3010)) -> Dict[int, Optional[int]]:
        """Map each port in the given range to a PID or None."""
        return {
            p: next(
                (conn.pid for conn in psutil.net_connections(kind='inet')
                 if conn.laddr.port == p and conn.status == psutil.CONN_LISTEN),
                None
            )
            for p in range(port_range[0], port_range[1] + 1)
        }

    @classmethod
    def random_port(cls) -> int:
        """Get a random available port and reserve it."""
        with socket.socket() as sock:
            sock.bind(("", 0))
            port = sock.getsockname()[1]

        # Check if this random port is already reserved
        if port in cls._reserved_ports:
            # If it's already reserved, use find() to get a different one
            return cls.find(start=port + 1, count=1)[0]

        # Reserve the port
        cls._reserved_ports.add(port)
        return port

    def __call__(self, start: int = 3000) -> int:
        """Shortcut: find and return one free port starting from `start`."""
        return self.find(start, 1)[0]