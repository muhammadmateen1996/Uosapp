"""Pure logic: region matching + fee calculation. No UI code here."""
import re
from difflib import SequenceMatcher

from defaults import COUNTRY_META


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", (s or "").lower()).strip()


def _score(q: str, cand: str) -> float:
    c = _norm(cand)
    if not q or not c:
        return 0.0
    if c == q:
        return 1.0
    if c.startswith(q):
        return 0.95
    if q in c:
        return 0.88
    # compare against the whole string and each word (handles "chenab nagar" vs "nagar chenab")
    best = SequenceMatcher(None, q, c).ratio()
    for w in c.split():
        best = max(best, SequenceMatcher(None, q, w).ratio() * 0.95)
    return best


def search(regions, query, limit=8, cutoff=0.62):
    """Return [(score, region)] best first. Matches names and aliases (typo tolerant)."""
    q = _norm(query)
    if not q:
        return []
    hits = []
    for r in regions:
        s = max(_score(q, r["name"]), *(_score(q, a) for a in r.get("aliases", [])), 0.0)
        if s >= cutoff:
            hits.append((s, r))
    hits.sort(key=lambda x: (-x[0], x[1]["name"]))
    return hits[:limit]


def check_region(country, regions, query):
    """Return dict(label, tone, name, text) describing the result."""
    meta = COUNTRY_META[country]
    hits = search(regions, query)
    if not hits:
        u = meta["unknown"]
        return {"label": u["label"], "tone": u["tone"], "name": query.strip() or "—", "text": u["text"], "others": []}
    score, top = hits[0]
    cat = meta["categories"].get(top["category"], {"label": top["category"].upper(), "tone": "grey"})
    exact = score >= 0.88
    text = f"Category: {top['category']}"
    if not exact:
        text = f"Closest match to “{query.strip()}”. {text}"
    others = [h[1]["name"] for h in hits[1:4] if h[1]["category"] != top["category"] or True]
    return {"label": cat["label"], "tone": cat["tone"], "name": top["name"], "text": text, "others": others}


def calculate(country_cfg, total_fee, scholarship, deposit_mode, deposit_percent,
              manual_deposit, rate, campus):
    total_fee, scholarship = float(total_fee or 0), float(scholarship or 0)
    rate, manual_deposit = float(rate or 0), float(manual_deposit or 0)
    net_fee = max(total_fee - scholarship, 0)
    if deposit_mode == "Percentage":
        deposit = net_fee * (float(deposit_percent or 0) / 100)
    else:
        deposit = min(manual_deposit, net_fee)
    living = float(country_cfg["living"].get(campus, 0))
    adjusted_rate = rate + float(country_cfg["buffer"])
    remaining = max(net_fee - deposit, 0)
    required_gbp = remaining + living
    return {
        "net_fee": net_fee, "deposit": deposit, "deposit_local": deposit * rate,
        "remaining": remaining, "living": living, "required_gbp": required_gbp,
        "adjusted_rate": adjusted_rate, "statement_local": required_gbp * adjusted_rate,
    }
