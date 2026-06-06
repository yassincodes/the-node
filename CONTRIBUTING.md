# Contributing to the-node

This is an open source project. If you believe in the idea, here is what needs to be built.

---

## What exists right now

- Local node activation with keypair generation
- Natural language storage in `~/.thenode/`, signed by private key
- Keyword search, memory retrieval, and `verify` for signatures
- Answering questions locally via `ask` (Ollama, on-device — no external calls)
- A local presence page via `serve`
- Local-network peer discovery via `discover` (mDNS, presence only)

---

## Read before you build

- [docs/the-node.md](docs/the-node.md) — the philosophy
- [docs/history.md](docs/history.md) — Hegel, collision, the node as act
- [docs/science.md](docs/science.md) — evolution, society, the mechanism
- [docs/pattern.md](docs/pattern.md) — the weld and the failure modes
- [docs/the-node-spec.md](docs/the-node-spec.md) — technical decisions

---

## What needs to be built next

### 1. Peer discovery

**Local-network discovery is built** (`node/discovery.py`, `python main.py discover`). It uses mDNS — no server — so nodes on the same Wi-Fi see each other's presence. It reveals only a node ID (which is itself a fingerprint of the public key) and the device's local address. No content, no keys, no identity.

What still needs building:
- Authentication of presence — right now a node can announce any ID; nothing proves it holds the matching key until keys are exchanged (this is the immune system, item 5)
- Discovery across different networks (a lightweight signaling server, or DHT)
- WebRTC for peer-to-peer connections without a central server
- NAT traversal so two nodes behind different routers can find each other

The goal stays the same: minimal infrastructure. Ideally no central server at all. Local presence first; reach the wider network without recreating a headquarters.

---

### 2. Controlled share protocol

When two nodes find each other, the user decides what to share.

What it should do:
- User selects specific entries to share with another node
- Those entries get packaged and sent directly
- The receiving node stores them, attributed to their origin node ID
- Nothing transfers without explicit user action

This is the core of how the network grows — person to person, consciously.

---

### 3. Local model integration

**Done.** The node answers fully offline through Ollama (`routing/router.py`). No external APIs, no keys — if no local model is running, the node stays silent rather than route data out.

What could still improve it:
- Let the user pick/manage models more easily (right now: `THE_NODE_MODEL`, default `llama3.2`)
- Stream responses instead of waiting for the whole answer
- Let the node fine-tune or build a local index on the user's own entries over time

Suggested models: llama3.2, phi3, mistral 7B — all run on most laptops.

---

### 4. Omi wearable integration

The Omi device (omi.me) captures ambient audio. This is the most honest input source — unfiltered, always on.

What it should do:
- Connect to Omi SDK
- Pipe transcriptions directly into the node as entries
- Mark entries as source: "omi" vs source: "computer"

---

### 5. The immune system

The hardest and most important one. The science doc names it directly: a network that grows without growing its defenses grows toward collapse. Honest volume does not automatically beat dishonest volume — parasites can win.

What it should do:
- Verify signatures on every received entry, not just local ones
- Make faking expensive: proof-of-origin that a lie cannot cheaply produce
- Keep attribution intact end to end, so a corrupt entry traces back to its source
- Stay decentralized — no central authority deciding what is "true," only verifiable origin and the user's own judgment

This is co-evolution: the immune response has to grow at least as fast as the network. Start small. `verify` already exists for local entries. Extend it outward.

---

### 6. Encryption at rest

Right now entries are signed but stored as plain JSON in `~/.thenode/`. The philosophy says "encrypted." The code does not do that yet.

What it should do:
- Encrypt `data.json` at rest with a key derived from a user passphrase
- Keep the private key protected, not stored in plaintext
- Never weaken the signing or verification that already works

Close the gap between what the philosophy claims and what the disk actually holds.

---

## How to contribute

1. Fork the repo
2. Pick one of the above
3. Build the smallest version that works honestly
4. Open a pull request with a clear description of what it does and what it doesn't do yet

No overengineering. No new dependencies unless absolutely necessary. Keep it as simple as the existing code.

---

## Philosophy

Read [docs/the-node.md](docs/the-node.md), [docs/history.md](docs/history.md), and [docs/science.md](docs/science.md) before building anything.

The code should reflect the philosophy. Simple, honest, open. If you find yourself adding complexity that the docs don't justify, stop and ask why.

---

*This project is early. What matters right now is that each piece works honestly, not that everything is built fast.*
