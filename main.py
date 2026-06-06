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


def help():
    print("""
The Node — commands:

  activate              Activate your node. Generates your local keypair.
  store "your text"     Store something in your node.
  read                  Read your last 10 entries.
  search "keyword"      Search your stored entries.
  summary               What your node knows about you so far.
  verify                Check signatures on all stored entries.
  discover [seconds]    Announce presence and see other nodes on your
                        local network. Presence only — nothing shared.
  status                Show your node status.
  ask "question"        Answer a question from your node, using a model
                        running on your own machine. Nothing leaves the device.
  serve                 Start local server for the presence page.
  help                  Show this.
""")


def main():
    args = sys.argv[1:]

    if not args or args[0] == "help":
        help()
        return

    cmd = args[0]

    if cmd == "activate":
        activate()

    elif cmd == "store":
        if len(args) < 2:
            print('Usage: python main.py store "your text"')
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
            print('Usage: python main.py search "keyword"')
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
            print("Node not active.")
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
                print("Usage: python main.py discover [seconds]")
                return
        discover(seconds)

    elif cmd == "ask":
        if len(args) < 2:
            print('Usage: python main.py ask "your question"')
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
