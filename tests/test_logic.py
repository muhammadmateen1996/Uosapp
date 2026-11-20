import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from defaults import DEFAULT_SETTINGS
import logic

IN = DEFAULT_SETTINGS["countries"]["India"]
PK = DEFAULT_SETTINGS["countries"]["Pakistan"]


@pytest.mark.parametrize("q,label", [
    ("Ludhiana", "HIGH RISK"), ("delhi", "HIGH RISK"), ("kerela", "LOW RISK"),
    ("Chennai", "LOW RISK"), ("Mumbai", "NEEDS REVIEW"), ("zzzzqq", "NOT FOUND"),
])
def test_india(q, label):
    assert logic.check_region("India", IN["regions"], q)["label"] == label


@pytest.mark.parametrize("q", [
    "Bajor", "Bajaur", "Chanab Nager", "Chenab Nagar", "Chinute", "Chiniot",
    "Khyber", "Malakand", "Mardan", "Nowshera",
])
def test_pakistan_restricted(q):
    assert logic.check_region("Pakistan", PK["regions"], q)["label"] == "RESTRICTED"


def test_pakistan_allowed():
    assert logic.check_region("Pakistan", PK["regions"], "Lahore")["tone"] == "green"


def test_search_empty():
    assert logic.search(PK["regions"], "  ") == []


def test_calc_india_percentage():
    r = logic.calculate(IN, 20000, 2000, "Percentage", 50, 0, 110, "Main")
    assert r["net_fee"] == 18000 and r["deposit"] == 9000
    assert r["adjusted_rate"] == 120                      # +10 INR buffer
    assert r["statement_local"] == pytest.approx((9000 + 10539) * 120)


def test_calc_pakistan_manual_london():
    r = logic.calculate(PK, 15000, 0, "Manual", 0, 3000, 370, "London")
    assert r["remaining"] == 12000 and r["adjusted_rate"] == 400   # +30 PKR buffer
    assert r["statement_local"] == pytest.approx((12000 + 13761) * 400)


def test_calc_zero_safe_and_caps():
    r = logic.calculate(PK, None, None, "Manual", 0, 99999, None, "Main")
    assert r["net_fee"] == 0 and r["deposit"] == 0
    r = logic.calculate(PK, 1000, 5000, "Percentage", 10, 0, 100, "Main")
    assert r["net_fee"] == 0
