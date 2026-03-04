"""Persist named system prompts to a JSON file."""

import json
from pathlib import Path

DEFAULT_PROMPT_NAME = "Default"
DEFAULT_PROMPT_TEXT = (
    "You are a friendly and helpful AI assistant. Keep your answers concise."
)
DEFAULT_STORE_PATH = Path("sys_prompt.json")


def _empty_store() -> dict:
    return {
        "active": DEFAULT_PROMPT_NAME,
        "prompts": {DEFAULT_PROMPT_NAME: DEFAULT_PROMPT_TEXT},
    }


def load_prompts(path: Path = DEFAULT_STORE_PATH) -> dict:
    """Load the prompt store from *path*, creating defaults if missing."""
    if not path.exists():
        return _empty_store()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "prompts" not in data or not data["prompts"]:
            return _empty_store()
        return data
    except (json.JSONDecodeError, KeyError):
        return _empty_store()


def save_prompts(store: dict, path: Path = DEFAULT_STORE_PATH) -> None:
    """Write the prompt store to *path*."""
    path.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")


def save_prompt(name: str, text: str, path: Path = DEFAULT_STORE_PATH) -> dict:
    """Add or update a named prompt and persist."""
    store = load_prompts(path)
    store["prompts"][name] = text
    store["active"] = name
    save_prompts(store, path)
    return store


def delete_prompt(name: str, path: Path = DEFAULT_STORE_PATH) -> dict:
    """Remove a named prompt (cannot delete the last one)."""
    store = load_prompts(path)
    if name in store["prompts"] and len(store["prompts"]) > 1:
        del store["prompts"][name]
        if store["active"] == name:
            store["active"] = next(iter(store["prompts"]))
        save_prompts(store, path)
    return store


def get_active_prompt(path: Path = DEFAULT_STORE_PATH) -> tuple[str, str]:
    """Return ``(name, text)`` of the active prompt."""
    store = load_prompts(path)
    name = store.get("active", DEFAULT_PROMPT_NAME)
    text = store["prompts"].get(name, DEFAULT_PROMPT_TEXT)
    return name, text


def list_prompt_names(path: Path = DEFAULT_STORE_PATH) -> list[str]:
    """Return sorted list of saved prompt names."""
    store = load_prompts(path)
    return sorted(store["prompts"].keys())
