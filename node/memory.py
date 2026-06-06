"""
The Node — Memory
Retrieval layer. Makes the node learn from stored history.
Simple keyword and recency based — no external dependencies.
"""

import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from node.core import read, DATA_FILE


def search(query: str, limit: int = 5) -> list:
    """
    Search stored entries by keyword relevance.
    No external model needed — runs fully local.
    """
    entries = read(limit=9999)
    if not entries:
        return []

    query_words = set(query.lower().split())

    scored = []
    for entry in entries:
        content_words = set(entry["content"].lower().split())
        overlap = len(query_words & content_words)
        if overlap > 0:
            scored.append((overlap, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:limit]]


def recent(limit: int = 5) -> list:
    """Return most recent entries."""
    return read(limit=limit)


def build_context(query: str, recent_count: int = 5, search_count: int = 5) -> str:
    """
    Build rich context for routing.
    Combines recent entries + relevant search results.
    Deduplicates. Returns clean natural language block.
    """
    recent_entries = recent(recent_count)
    relevant_entries = search(query, search_count)

    # Deduplicate by entry id
    seen = set()
    combined = []
    for entry in recent_entries + relevant_entries:
        if entry["id"] not in seen:
            seen.add(entry["id"])
            combined.append(entry)

    if not combined:
        return ""

    lines = []
    for e in combined:
        lines.append(f"[{e['timestamp'][:10]}] {e['content']}")

    return "\n".join(lines)


def summary() -> dict:
    """
    Basic summary of what the node knows.
    No external model — purely from stored data.
    """
    entries = read(limit=9999)
    if not entries:
        return {"total": 0, "topics": [], "first": None, "last": None}

    # Extract most common words as rough topics
    word_count = {}
    stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at",
                 "to", "for", "of", "with", "is", "it", "i", "my", "that",
                 "this", "was", "be", "are", "have", "has", "had", "not",
                 "so", "if", "we", "he", "she", "they", "you", "do", "did"}

    for entry in entries:
        for word in entry["content"].lower().split():
            word = word.strip(".,!?\"'")
            if len(word) > 3 and word not in stopwords:
                word_count[word] = word_count.get(word, 0) + 1

    top_topics = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total": len(entries),
        "topics": [w for w, _ in top_topics],
        "first": entries[0]["timestamp"][:10],
        "last": entries[-1]["timestamp"][:10]
    }
