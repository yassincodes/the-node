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

The node has access to all available models — OpenAI, Anthropic, Mistral, Gemini, and whatever exists at the time of the call.

Routing logic before the node knows the user:
- Simple queries go to the lightweight local model on-device
- Complex queries route to external models
- The user pays per external call — energy for the system to run

Routing logic after the node knows the user:
- The node has accumulated the user's documents, voice, notes, life
- It trains on that data locally
- It starts routing based on what it has learned about what this person needs and how they think

The routing room is not fixed. It learns. It gets cheaper over time as the local model gets smarter about this specific person.

---

## Payment model

The user is the energy source.

They pay per external model call. Small, transparent, per use. The lightweight local model handles everything it can for free. External calls happen only when necessary.

Over time, as the node learns from the user's data, external calls become less frequent. The node becomes more self-sufficient. The cost decreases as the relationship deepens.

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
