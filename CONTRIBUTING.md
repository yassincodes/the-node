# Contributing to the-node

This is an open source project. If you believe in the idea, here is what needs to be built.

---

## What exists right now

- Local node activation with keypair generation
- Natural language storage, signed by private key
- Keyword search and memory retrieval
- Routing queries to external AI models using stored context
- A presence page (static, no live network yet)

---

## What needs to be built next

### 1. Peer discovery

Nodes need to find each other. Right now every node is isolated.

What it should do:
- A node can announce its presence on a local network
- Other nodes on the same network can see it exists
- No content is shared automatically — just presence

Options to explore:
- mDNS for local network discovery (no server needed)
- A lightweight signaling server for nodes across different networks
- WebRTC for peer-to-peer connections without a central server

The goal is minimal infrastructure. Ideally no central server at all.

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

Right now the node routes to external AI APIs. The goal is for it to work fully offline.

What it should do:
- Integrate with Ollama (ollama.ai) for local model inference
- Route simple queries to the local model first
- Only call external APIs when the local model isn't sufficient
- User controls which models are available

Suggested starting models: phi3, mistral 7B — both run on most laptops.

---

### 4. Omi wearable integration

The Omi device (omi.me) captures ambient audio. This is the most honest input source — unfiltered, always on.

What it should do:
- Connect to Omi SDK
- Pipe transcriptions directly into the node as entries
- Mark entries as source: "omi" vs source: "computer"

---

## How to contribute

1. Fork the repo
2. Pick one of the above
3. Build the smallest version that works honestly
4. Open a pull request with a clear description of what it does and what it doesn't do yet

No overengineering. No new dependencies unless absolutely necessary. Keep it as simple as the existing code.

---

## Philosophy

Read `docs/the-node.md` before building anything.

The code should reflect the philosophy. Simple, honest, open. If you find yourself adding complexity that the docs don't justify, stop and ask why.

---

*This project is early. What matters right now is that each piece works honestly, not that everything is built fast.*
