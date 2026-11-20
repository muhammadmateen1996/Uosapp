import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import storage


def test_save_and_reload(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "LOCAL_PATH", str(tmp_path / "s.json"))
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.delenv("SETTINGS_REPO", raising=False)
    storage._cache = None
    s = storage.load(force=True)
    s["countries"]["Pakistan"]["regions"].append({"name": "Swat", "category": "Restricted", "aliases": ["Swaat"]})
    assert "locally" in storage.save(s)
    storage._cache = None
    names = [r["name"] for r in storage.load(force=True)["countries"]["Pakistan"]["regions"]]
    assert "Swat" in names and "Bajaur" in names
