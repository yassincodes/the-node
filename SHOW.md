# Show someone in 5 minutes

No philosophy. Just the node.

---

## Before they arrive

```bash
cd the-node
chmod +x setup.sh thenode   # only if "permission denied"
./setup.sh
```

---

## In the room (their machine)

**1. Setup** (once)

```bash
./setup.sh
```

They see: *Node activated. ID: …*

**2. Store something real**

Don't use your words. Ask them:

> *"What's one thing from today that's actually yours?"*

```bash
./thenode store "their words here"
```

They see: *Stored. Entry ID: …*

**3. Read it back**

```bash
./thenode read
```

Pause. Let it land. Their words. Their device. Signed.

**4. Status**

```bash
./thenode
```

They see: ID, record depth (entries · days · verified), where it lives.

**5. Optional — presence**

Terminal 1:

```bash
./thenode serve
```

Open **http://localhost:5050** in a browser. Green pulse. Node ID. Record depth. No entries shown.

---

## Two people (same Wi‑Fi)

**Person A:** `./thenode serve` (leave running)

**Person B:**

```bash
./thenode discover
./thenode share <entry-id> <person-a-ip>
```

Person A:

```bash
./thenode read
```

One entry crossed. Chosen. Verified. That's the network in miniature.

---

## If they ask questions

| Question | Answer |
|----------|--------|
| Where does my data go? | Nowhere. `~/.thenode/` on your machine. |
| Who can see it? | Only you, unless you share one entry. |
| Does it need the internet? | No. Setup and daily use work offline. |
| What about AI? | Optional. Local Ollama only. Nothing leaves the device. |
| What's the big vision? | One node first. The rest emerges when enough people carry these. |

---

## One sentence

> *A place on your device that remembers your life — signed by you, owned by you, connectable to others when you choose.*

---

*the-node — open source*
