"""Settings persistence.

Hugging Face free Spaces lose local files on restart, so if the Space has
these secrets/variables, settings are also stored in a private HF *Dataset* repo:
    HF_TOKEN       - a write token (Space secret)
    SETTINGS_REPO  - e.g. "yourname/uos-settings" (private dataset repo)
Without them the app still works, using a local settings.json (not durable on HF).
"""
import copy
import json
import os
import threading

from defaults import DEFAULT_SETTINGS

LOCAL_PATH = os.path.join(os.path.dirname(__file__), "settings.json")
FILENAME = "settings.json"
_lock = threading.Lock()
_cache = None


def _remote_cfg():
    token, repo = os.environ.get("HF_TOKEN"), os.environ.get("SETTINGS_REPO")
    return (token, repo) if token and repo else None


def remote_enabled() -> bool:
    return _remote_cfg() is not None


def _merge_defaults(data):
    base = copy.deepcopy(DEFAULT_SETTINGS)
    for country, cfg in (data.get("countries") or {}).items():
        base["countries"].setdefault(country, {}).update(cfg)
    return base


def load(force=False):
    global _cache
    with _lock:
        if _cache is not None and not force:
            return copy.deepcopy(_cache)
        data = None
        cfg = _remote_cfg()
        if cfg:
            try:
                from huggingface_hub import hf_hub_download
                p = hf_hub_download(cfg[1], FILENAME, repo_type="dataset", token=cfg[0], force_download=True)
                with open(p, encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = None
        if data is None and os.path.exists(LOCAL_PATH):
            try:
                with open(LOCAL_PATH, encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = None
        _cache = _merge_defaults(data) if data else copy.deepcopy(DEFAULT_SETTINGS)
        return copy.deepcopy(_cache)


def save(settings) -> str:
    """Save settings. Returns a status message."""
    global _cache
    with _lock:
        _cache = copy.deepcopy(settings)
        with open(LOCAL_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        cfg = _remote_cfg()
        if not cfg:
            return "Saved locally. ⚠️ Permanent storage is not set up, so changes may be lost when the Space restarts."
        try:
            from huggingface_hub import HfApi
            api = HfApi(token=cfg[0])
            api.create_repo(cfg[1], repo_type="dataset", private=True, exist_ok=True)
            api.upload_file(path_or_fileobj=LOCAL_PATH, path_in_repo=FILENAME,
                            repo_id=cfg[1], repo_type="dataset", commit_message="Update settings")
            return "Saved permanently ✅"
        except Exception as e:  # keep app usable
            return f"Saved locally, but permanent save failed: {e}"
