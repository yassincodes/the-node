"""
The Node — Discovery
Peer discovery on the local network. Presence only.

A node announces it exists. Other nodes on the same network hear it.
No content is exchanged. No central server.

What is revealed by being discoverable:
  - the node ID (itself a truncated fingerprint of the public key)
  - the device's local network address (unavoidable — you cannot be
    found without an address)

What is NOT revealed: any stored entry, the private key, the full public
key, or the user's identity.

Honesty caveat: presence at this stage is UNAUTHENTICATED. A node could
announce any ID it likes. There is no proof here that an announcer
actually holds the matching private key — that proof only happens later,
when keys are exchanged and signatures are checked (the immune system,
not yet built). Treat a discovered node as "a light", not as "verified".

Like a light in the dark. You know someone is there. You do not know
who they are or what they carry.

Built on mDNS (zeroconf) — the same zero-configuration protocol printers
and speakers use to appear on a network. No server to run. No account.
The network itself carries the announcement.
"""

import socket
import time

from node.core import load_node_id, is_active

SERVICE_TYPE = "_thenode._tcp.local."
PRESENCE_PORT = 5050


def _require_zeroconf():
    """Import zeroconf lazily so the rest of the node works without it."""
    try:
        from zeroconf import Zeroconf, ServiceInfo, ServiceBrowser
        return Zeroconf, ServiceInfo, ServiceBrowser
    except ImportError:
        return None


def _local_ip() -> str:
    """Best-effort local IP. No traffic actually sent."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def _build_service_info(ServiceInfo, node_id: str):
    ip = _local_ip()
    # The only thing announced: the node ID (which is itself a truncated
    # fingerprint of the public key) and a protocol version. No entries.
    # No content. No private key. Just: a node with this ID exists here.
    properties = {
        "node_id": node_id,
        "v": "1",
    }
    name = f"{node_id}.{SERVICE_TYPE}"
    return ServiceInfo(
        SERVICE_TYPE,
        name,
        addresses=[socket.inet_aton(ip)],
        port=PRESENCE_PORT,
        properties=properties,
        server=f"{node_id}.local.",
    )


class _PresenceListener:
    """Collects nodes seen on the network. Presence only."""

    def __init__(self, self_id: str):
        self.self_id = self_id
        self.present = {}
        self.ever_seen = {}

    def _decode(self, info):
        props = {}
        for k, v in (info.properties or {}).items():
            try:
                key = k.decode() if isinstance(k, bytes) else k
                val = v.decode() if isinstance(v, bytes) else v
            except Exception:
                continue
            props[key] = val
        return props

    def add_service(self, zeroconf, type_, name):
        info = zeroconf.get_service_info(type_, name)
        if not info:
            return
        props = self._decode(info)
        node_id = props.get("node_id")
        if not node_id or node_id == self.self_id:
            return
        addr = socket.inet_ntoa(info.addresses[0]) if info.addresses else "?"
        record = {
            "node_id": node_id,
            "address": addr,
        }
        first_time = node_id not in self.ever_seen
        self.present[node_id] = record
        self.ever_seen[node_id] = record
        if first_time:
            print(f"  light  {node_id}  ({addr})")

    def update_service(self, zeroconf, type_, name):
        # Required by newer zeroconf versions. Re-resolve as an add.
        self.add_service(zeroconf, type_, name)

    def remove_service(self, zeroconf, type_, name):
        node_id = name.split(".")[0]
        if node_id in self.present:
            del self.present[node_id]
            print(f"  dark   {node_id}  (gone)")


def discover(seconds: int = 10):
    """
    Announce this node and listen for others on the local network.

    For `seconds`, this node says "I exist" and watches for other nodes
    saying the same. Nothing else is exchanged.
    """
    if not is_active():
        print("Node not active. Run ./setup.sh first.")
        return

    deps = _require_zeroconf()
    if deps is None:
        print("Discovery needs the 'zeroconf' package.")
        print("Install it:  pip install zeroconf")
        print("(It is in requirements.txt — pip install -r requirements.txt)")
        return

    Zeroconf, ServiceInfo, ServiceBrowser = deps

    node_id = load_node_id()
    zeroconf = Zeroconf()
    info = _build_service_info(ServiceInfo, node_id)
    listener = _PresenceListener(node_id)

    print(f"\nThis node: {node_id}")
    print(f"Announcing presence on the local network for {seconds}s...")
    print("Other nodes on the same Wi-Fi will appear below. Nothing is shared.\n")

    try:
        zeroconf.register_service(info)
        ServiceBrowser(zeroconf, SERVICE_TYPE, listener)
        time.sleep(seconds)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            zeroconf.unregister_service(info)
        except Exception:
            pass
        zeroconf.close()

    seen_count = len(listener.ever_seen)
    still_present = len(listener.present)
    print()
    if seen_count == 0:
        print("No other nodes seen. You are the only light right now.")
        print("That is not failure. The first cell is always alone.")
    else:
        word = "node" if seen_count == 1 else "nodes"
        print(f"Saw {seen_count} other {word} on this network during this window.")
        if still_present < seen_count:
            print(f"{still_present} still present at the end "
                  f"({seen_count - still_present} went dark before the window closed).")
