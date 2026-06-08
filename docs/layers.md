# Layers

*What exists. What each piece does. What it does not do.*

This is not a design doc. It is the node describing itself from the code that is running today.

---

## Layer 1 — You

**Hardware:** your device. Your life. Your choice to feed the node.

Nothing is stored until you run:

```bash
./thenode store "your words here"
```

Nothing is shared automatically. Ever. The node does nothing on its own.

---

## Layer 2 — Identity

**File:** `node/core.py`  
**On disk:** `~/.thenode/private.pem`, `public.pem`, `node_id.txt`

```bash
./thenode activate
```

What happens:
- Generates an RSA keypair on your machine
- Private key stays in `~/.thenode/` — never sent anywhere
- Node ID is derived from your public key (first 16 chars of its hash)

What leaves the device: **nothing**

```bash
./thenode verify
```

Checks every stored entry against your public key. Pass or fail. No trust required — math.

---

## Layer 3 — Memory

**Files:** `node/core.py`, `node/memory.py`  
**On disk:** `~/.thenode/data.json`

```bash
./thenode store "..."
./thenode read
./thenode search "keyword"
./thenode summary
```

What happens:
- Your words are stored in encrypted JSON at `~/.thenode/data.enc` (private key in `private.enc`)
- Each entry is signed with your private key at store time
- Search and summary run locally — no model, no network

What leaves the device: **nothing**

Passphrase-derived vault (Argon2id → Fernet). Only the salt lives in `~/.thenode/.vault`.

Your passphrase is the only door. Make it real — the code enforces eight characters, not a strong secret.

---

## Layer 4 — Voice

**File:** `routing/router.py`  
**Calls:** `http://localhost:11434` only (Ollama, on your machine)

```bash
./thenode ask "your question"
```

What happens:
- Pulls relevant entries from your memory (`node/memory.py`)
- Sends them to a model running **on this device**
- Returns an answer

What leaves the device: **nothing**

If no local model is running:
- The node stays silent
- It says so
- It does not fall back to any external API — that path does not exist in the code

```python
# routing/router.py
OLLAMA_URL = "http://localhost:11434/api/chat"
```

That is the whole routing layer. One URL. Localhost.

---

## Layer 5 — Presence

**Files:** `node/discovery.py`, `server.py`, `presence/index.html`

Two ways to say *I exist*:

```bash
./thenode discover      # other nodes on your Wi-Fi see you
```bash
./thenode serve         # this machine only — not on Wi-Fi
./thenode receive       # 5 min window + pairing code to accept one share
```
```

What `discover` announces (mDNS, no server):
- your node ID
- your local network address

What `serve` returns at `/status` (signed — proves key matches node ID):
```json
{"active": true, "node_id": "abc...", "record": {...}, "public_key": "...", "presence_signature": "..."}
```

What neither reveals: your entries, your keys, your identity

What leaves the device: node ID + local IP (already public by being discoverable)

What is not built yet: proof that a discovered node holds the matching private key

---

## Layer 6 — Connection

**File:** `node/share.py`  
**Endpoint:** `POST /share` only while `./thenode receive` is running

```bash
# Receiving node — opens Wi-Fi for ~5 min, shows pairing code:
./thenode receive

# Your node — one entry, their IP, their code:
./thenode share <entry-id> <host> <pairing-code>
```

What happens:
- Wi-Fi port is **closed by default**. Only opens during `receive`, with TLS + pairing code.
- Closes after one entry or when time runs out.
- Package is signed; receiver verifies before storing.

What leaves your device: **one entry you chose**, to **one host you named**, with **their code**

What does not happen: auto-sync, bulk export, sharing without your command

```bash
./thenode verify
```

Works on received entries too — using the origin public key stored with them.

---

## The stack, bottom to top

```
You                          ← layer 1: the person, the hardware
  ↓
Identity (keypair, sign)     ← layer 2: node/core.py
  ↓
Memory (store, search)       ← layer 3: node/core.py + memory.py
  ↓
Voice (ask, local model)     ← layer 4: routing/router.py → localhost only
  ↓
Presence (discover, serve)   ← layer 5: node/discovery.py + server.py
  ↓
Connection (share)           ← layer 6: node/share.py → POST /share
```

Each layer only talks to the layer below it, except share — which only fires when **you** run it, to **one** host, with **one** entry.

---

## What this is not

- Not a cloud product — there is no cloud
- Not an API you call — you run it
- Not alignment written on top — the structure is the alignment
- Hardened — encrypted at rest, signed presence, pairing-code receive window, TLS on Wi-Fi. Not unhackable — malware and stolen unlocked devices remain

---

## How to read this repo

| Layer | File | Command |
|-------|------|---------|
| 2 | `node/core.py` | `activate`, `store`, `verify` |
| 3 | `node/memory.py` | `read`, `search`, `summary` |
| 4 | `routing/router.py` | `ask` |
| 5 | `node/discovery.py` | `discover` |
| 5 | `server.py` | `serve` |
| 6 | `node/share.py` | `share` |

Open any file. Read it. That is what the node does.

---

*This document describes v1 as built. It updates when the code updates.*
