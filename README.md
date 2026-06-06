# The Node

A personal node. Local. Encrypted. Yours.

---

## What it does

- Activates with a local cryptographic keypair — private key never leaves your device
- Stores natural language input you choose to feed it
- Signs every entry so origin is verifiable
- Routes queries to external AI models using your stored context
- Shows a presence page — other nodes can see you exist, nothing more

## What it does not do

- Send your data anywhere automatically
- Connect to a central server
- Share anything without your explicit choice

---

## Install

```bash
git clone https://github.com/yassincodes/the-node
cd the-node
pip install cryptography
```

---

## Usage

```bash
# Activate your node
python main.py activate

# Store something
python main.py store "today I worked on the routing system"

# Read your entries
python main.py read

# Check status
python main.py status

# Ask a question — routes through your stored context (via OpenRouter)
# Open .env in this folder and paste your OpenRouter key there.
python main.py ask "what have I been working on?"
```

---

## Presence page

Open `presence/index.html` in your browser. It shows your node is active. Nothing else.

---

## Structure

```
the-node/
├── main.py              # CLI entry point
├── node/
│   └── core.py          # Activation, storage, signing
├── routing/
│   └── router.py        # Query routing to external models
├── presence/
│   └── index.html       # Presence page
└── docs/
    ├── the-node.md      # The philosophy
    └── the-node-spec.md # Technical decisions
```

---

## Philosophy

Every human gets a node. The node stores what they choose to feed it. It connects to others only when they choose. The data is signed, verifiable, and owned by the person carrying it.

Read the full thought: [docs/the-node.md](docs/the-node.md)

---

## Open source

All structural code is public. No hidden logic. No black box.

---

*Built June 6, 2026.*
