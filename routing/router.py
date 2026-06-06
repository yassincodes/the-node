"""
The Node — Routing
Routes queries to external models via OpenRouter.
User provides their own API key. Node pays per call.
"""

import json
import urllib.request
import urllib.error
from node.core import is_active
from node.memory import build_context

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "anthropic/claude-sonnet-4"


def route(query: str, api_key: str, model: str = DEFAULT_MODEL) -> str:
    """
    Route a query to an external model via OpenRouter.
    Uses node's stored data as context.
    User pays per call.
    """
    if not is_active():
        return "Node not active. Run activate() first."

    context = build_context(query)

    system_prompt = "You are a routing assistant for a personal node. Answer based on the user's actual stored context when relevant."

    if context:
        user_content = f"My personal context:\n{context}\n\nMy question: {query}"
    else:
        user_content = query

    payload = json.dumps({
        "model": model,
        "max_tokens": 1000,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    }).encode()

    req = urllib.request.Request(
        OPENROUTER_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "The Node",
        },
    )

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return f"Routing error: {e.code} {e.reason}\n{body}"
    except Exception as e:
        return f"Routing error: {str(e)}"
