#!/usr/bin/env python3
"""
The Node — CLI
Run from terminal. Simple commands.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from node.core import activate, store, read, status, is_active
from node.memory import search, summary
from routing.router import route

ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")


def load_api_key():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                if key.strip() == "OPENROUTER_API_KEY":
                    value = value.strip().strip('"').strip("'")
                    if value and value != "paste-your-key-here":
                        return value
    return os.environ.get("OPENROUTER_API_KEY")


def help():
    print("""
The Node — commands:

  activate              Activate your node. Generates your local keypair.
  store "your text"     Store something in your node.
  read                  Read your last 10 entries.
  search "keyword"      Search your stored entries.
  summary               What your node knows about you so far.
  status                Show your node status.
  ask "question"        Route a question through your node context.
                        Put your key in .env (in this folder).
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

    elif cmd == "ask":
        if len(args) < 2:
            print('Usage: python main.py ask "your question"')
            return
        api_key = load_api_key()
        if not api_key:
            print(f"Add your OpenRouter key to: {ENV_FILE}")
            return
        query = " ".join(args[1:])
        print("\nRouting...\n")
        answer = route(query, api_key)
        print(answer)

    elif cmd == "serve":
        import server
        server.run()

    else:
        print(f"Unknown command: {cmd}")
        help()


if __name__ == "__main__":
    main()
