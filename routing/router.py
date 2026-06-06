"""
The Node — Routing
The node answers from itself.

Queries go to a model running on this machine (Ollama). No API key.
No external service. Nothing leaves the device — not the query, not the
context the node has stored about you.

If no local model is running, the node says so plainly and sends nothing
anywhere. It does not quietly fall back to a corporate API, because a node
that can silently leak is not a node that speaks from itself.

Set THE_NODE_MODEL to choose which local model to use (default: llama3.2).
Install once:  https://ollama.ai   then:  ollama pull llama3.2
"""

import os
import json
import urllib.request
import urllib.error

from node.core import is_active
from node.memory import build_context

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3.2"

SYSTEM_PROMPT = (
    "You are this person's own node. You answer using only what they have "
    "stored in you, plus plain reasoning. You do not pretend to know things "
    "about them that are not in their context."
)


def _model() -> str:
    return os.environ.get("THE_NODE_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def route(query: str, model: str = None) -> str:
    """
    Answer a query with a local model, using the node's stored context.
    Nothing is sent off the device.
    """
    if not is_active():
        return "Node not active. Run ./setup.sh first."

    model = model or _model()
    context = build_context(query)

    if context:
        user_content = f"What you have stored about me:\n{context}\n\nMy question: {query}"
    else:
        user_content = query

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "stream": False,
    }).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            return data["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        if "not found" in body.lower() or e.code == 404:
            return (
                f"The local model '{model}' is not installed.\n"
                f"Pull it:  ollama pull {model}\n"
                f"Or set another:  export THE_NODE_MODEL=phi3\n"
                "Nothing was sent anywhere."
            )
        return f"Local model error: {e.code}. Nothing was sent anywhere.\n{body}"
    except urllib.error.URLError:
        return (
            "No local model is answering, so the node stays silent.\n"
            "It speaks from itself only — it will not route your data outside.\n\n"
            "To let it answer, run a model on this machine:\n"
            "  1. Install Ollama:  https://ollama.ai\n"
            f"  2. Pull a model:   ollama pull {model}\n"
            "  3. Ask again.\n\n"
            "Nothing was sent anywhere."
        )
    except Exception as e:
        return f"Local model error: {e}. Nothing was sent anywhere."
