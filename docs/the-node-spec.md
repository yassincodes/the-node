# The Node — Technical Spec

*This is not a whitepaper. It is a set of decisions made clearly.*

---

## What the node stores

Anything the user chooses to feed it.

Keystrokes, social media exports, voice from the Omi, documents, notes, files. The user decides what goes in. The user decides what stays private. The user decides what gets shared with other nodes.

Format: natural language, primarily. The node stores what humans actually produce — not structured data, not forms, not categories someone else decided. Raw human output.

---

## Target devices

**Primary: Omi wearable**
Ambient, always on, unfiltered. The user is not curating when they wear it. It captures life as it happens. This is the most honest input the node receives. The Omi is not just a device — it is the honesty layer by design.

**Secondary: Computer**
Filtered, conscious input. The user chooses what to type and what to feed. Still honest, just more deliberate. Needed for scale and accessibility.

The system knows which data came from which source. Omi data is weighted as unfiltered. Computer data is weighted as conscious. Both are real.

---

## Activation

The user activates their node intentionally. Not through a signup flow. Not through an email. A deliberate act.

On activation, the device generates a local cryptographic keypair. The private key never leaves the device. The public key is what other nodes can see — not the user's identity, not their data. Just: this node exists.

---

## How nodes find each other

Presence only.

Your node announces it exists. Other nodes hear it. No content is exchanged automatically. No data transfers without the user's explicit choice.

Like seeing a light in the dark. You know someone is there. You do not know who or what they carry.

---

## How sharing works

User controlled. Entirely.

You decide what another node receives from yours. They decide what you receive from theirs. There is no automatic sync. There is no merge that happens without consent.

Think of it like the first social networks — you post what you choose to post. Except here, what you share goes directly to a specific person's node, not a public feed.

The controlled share is also how the network grows. Person to person. Trust extended deliberately.

---

## The routing room

The node answers from itself.

Queries go to a model running on the user's own machine. No external service. No API key. Nothing — not the question, not the stored context — leaves the device.

If no local model is running, the node stays silent and says so. It does not quietly fall back to a corporate API. A node that can leak silently is not a node that speaks from itself, so the ability to leak is simply not there.

As the node accumulates the user's life, the local model has more to draw on. It gets more useful over time without ever reaching outside.

---

## Payment model

The user is the energy source — literally. The compute is their own machine.

There is nothing to pay because there is no external call. No per-use billing, no metered API, no company in the loop. The cost is the electricity already running the device the node lives on.

This is not a discount. It is the absence of a middleman. The node runs on the hardware of the person carrying it, and answers from it.

---

## The honesty layer

There is no separate honesty layer built on top.

The Omi is the honesty layer. Ambient capture of unfiltered life is structurally more honest than anything a user consciously constructs. The architecture itself enforces honesty at the primary input level.

The cryptographic keypair enforces honesty at the identity level — data is signed by the device that generated it and cannot be tampered with without detection.

The user-controlled share enforces honesty at the social level — people only share what they are willing to stand behind.

Honesty is not a feature added on top. It is built into the three layers of the system: input, identity, sharing.

---

## What this is not

- Not a social network
- Not a cloud product
- Not a company's database
- Not a surveillance tool
- Not an assistant that lives on someone else's server

It is a personal node. It belongs to the person carrying it. It runs on their device. It learns from their life. It connects to others only when they choose.

---

## Open source commitment

All structural code is public. Readable by anyone. Written with clarity so that someone who cannot read code can still understand what it does from the documentation alone.

No hidden logic. No black box. The code should be able to explain itself.

---

*Spec version 1. June 6, 2026.*
*Decisions made. Ready to build.*

---

## Current implementation (v1)

What the code does today — honestly:

- **Storage:** entries in plain JSON at `~/.thenode/data.json`, each signed with the node's private key
- **Verification:** `python main.py verify` checks all signatures
- **Encryption at rest:** not yet — planned; v1 is signed, not encrypted
- **Network:** local discovery (`discover`), controlled share (`share` + `serve`). Share verifies signature and node ID. No internet-wide discovery yet
- **External calls:** none. `ask` uses a local model (Ollama). If none is running, the node stays silent and sends nothing anywhere
- **Presence:** local only via `python main.py serve` on port 5050

The philosophy describes the direction. This section describes what is built.

For how the philosophy, history, and science fit into one move — and where that move can fail — read [pattern.md](pattern.md).
