#!/usr/bin/env python3
"""
The Node — CLI
Run from terminal. Simple commands.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from node.core import activate, store, read, status, is_active, verify_all
from node.memory import search, summary
from routing.router import route


def welcome():
    if not is_active():
        print("""
  Your node is not set up yet.

  Run once:

    ./setup.sh

  That installs everything and activates your node.
  After that, use ./thenode for all commands.
""")
        return

    status()
    print("""
  Try:

    ./thenode store "something from your day"
    ./thenode read
    ./thenode ask "what do I know?"

  More: ./thenode help
""")


def help():
    print("""
The Node — commands:

  store "your text"     Store something in your node.
  read                  Read your last 10 entries.
  search "keyword"      Search your stored entries.
  summary               What your node knows about you so far.
  ask "question"        Answer from your memory. Local model only.
  status                Show your node status.
  verify                Check signatures on all stored entries.
  discover [seconds]    See other nodes on your local network.
  share <id> <host>     Send one entry to another node.
  serve                 Start local presence server.
  activate              Regenerate keypair (rare — setup does this).
  help                  Show this.
""")


def main():
    args = sys.argv[1:]

    if not args or args[0] == "help":
        if not args:
            welcome()
        else:
            help()
        return

    cmd = args[0]

    if cmd == "activate":
        activate()

    elif cmd == "store":
        if len(args) < 2:
            print('Usage: ./thenode store "your text"')
            return
        store(" ".join(args[1:]))

    elif cmd == "read":
        entries = read()
        if not entries:
            print("No entries yet.")
            return
        for e in entries:
            print(f"\n[{e['timestamp']}] ({e['source']})")
            print(f"  {e['content']}")

    elif cmd == "search":
        if len(args) < 2:
            print('Usage: ./thenode search "keyword"')
            return
        query = " ".join(args[1:])
        results = search(query)
        if not results:
            print("Nothing found.")
            return
        for e in results:
            print(f"\n[{e['timestamp']}] ({e['source']})")
            print(f"  {e['content']}")

    elif cmd == "summary":
        s = summary()
        if s["total"] == 0:
            print("No entries yet.")
            return
        print(f"\n--- Node Summary ---")
        print(f"Total entries : {s['total']}")
        print(f"First entry   : {s['first']}")
        print(f"Last entry    : {s['last']}")
        print(f"Top topics    : {', '.join(s['topics'])}\n")

    elif cmd == "status":
        status()

    elif cmd == "verify":
        if not is_active():
            print("Node not active. Run ./setup.sh first.")
            return
        valid, invalid = verify_all()
        total = valid + invalid
        if total == 0:
            print("No entries to verify.")
            return
        print(f"\nVerified {valid}/{total} entries.")
        if invalid:
            print(f"WARNING: {invalid} entries failed verification.")

    elif cmd == "discover":
        from node.discovery import discover
        seconds = 10
        if len(args) > 1:
            try:
                seconds = int(args[1])
            except ValueError:
                print("Usage: ./thenode discover [seconds]")
                return
        discover(seconds)

    elif cmd == "share":
        if len(args) < 3:
            print("Usage: ./thenode share <entry-id> <host>")
            print("Example: ./thenode share a1b2c3d4 192.168.1.15")
            print("The other node must be running: ./thenode serve")
            return
        from node.share import send
        print(send(args[1], args[2]))

    elif cmd == "ask":
        if len(args) < 2:
            print('Usage: ./thenode ask "your question"')
            return
        query = " ".join(args[1:])
        print("\nThinking locally...\n")
        answer = route(query)
        print(answer)

    elif cmd == "serve":
        import server
        server.run()

    else:
        print(f"Unknown command: {cmd}")
        help()


if __name__ == "__main__":
    main()
