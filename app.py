import os

import gradio as gr

import logic
import storage
from defaults import COUNTRY_META

ADMIN_PIN = os.environ.get("ADMIN_PIN", "1234")

CSS = """
:root { --uos-navy:#0b1f3a; --uos-teal:#00a3ad; --uos-bg:#f4f6f9; }
.gradio-container { background: var(--uos-bg) !important; max-width: 1100px !important; margin: auto; font-family: 'Segoe UI', Roboto, Arial, sans-serif; }
.uos-header { background: var(--uos-navy); color:#fff; padding:22px 28px; border-radius:14px; border-bottom:5px solid var(--uos-teal); margin-bottom:14px; }
.uos-header, .uos-header * { color:#fff !important; }
.uos-header h1 { margin:0; font-size:1.6rem; }
.uos-header p { margin:4px 0 0; opacity:.85; }
.pick-btn { min-height:150px !important; font-size:1.5rem !important; font-weight:700 !important; background:#fff !important; color:var(--uos-navy) !important; border:2px solid #dde3ea !important; border-radius:16px !important; }
.pick-btn:hover { border-color:var(--uos-teal) !important; box-shadow:0 6px 18px rgba(0,163,173,.25); }
button.primary, .primary-btn { background: var(--uos-teal) !important; color:#fff !important; border:none !important; font-weight:600 !important; border-radius:10px !important; }
.card { background:#fff; border-radius:14px; padding:20px; box-shadow:0 1px 4px rgba(0,0,0,.08); }
.result { border-radius:14px; padding:24px; color:#fff; text-align:center; }
.result, .result * { color:#fff !important; }
.stat.big, .stat.big * { color:#fff !important; }
.result .badge { font-size:1.9rem; font-weight:800; letter-spacing:.04em; }
.result .name { font-size:1.15rem; margin-top:6px; }
.result .sub { opacity:.9; margin-top:4px; }
.tone-red { background:#c62839; } .tone-green { background:#1e8e5a; } .tone-amber { background:#d98a00; } .tone-grey { background:#6b7785; }
.stat-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; }
.stat { background:#fff; border-radius:12px; padding:14px 16px; border-left:5px solid var(--uos-teal); box-shadow:0 1px 4px rgba(0,0,0,.08); }
.stat.big { background:var(--uos-navy); color:#fff; border-left-color:#f5b400; grid-column:1/-1; }
.stat .k { font-size:.8rem; text-transform:uppercase; letter-spacing:.05em; opacity:.7; }
.stat .v { font-size:1.35rem; font-weight:700; margin-top:2px; }
.note { color:#5b6673; font-size:.9rem; }
"""


def fmt(n, ccy):
    return f"{n:,.2f} {ccy}"


# ---------- Region check ----------
def suggest(country, text):
    regions = storage.load()["countries"][country]["regions"]
    names = [r["name"] for _, r in logic.search(regions, text, limit=10)]
    return gr.update(choices=names, value=None)


def show_result(country, typed, picked):
    regions = storage.load()["countries"][country]["regions"]
    query = picked or typed
    if not (query or "").strip():
        return "<div class='note'>Type a state, city or district above.</div>"
    r = logic.check_region(country, regions, query)
    others = ""
    if r["others"]:
        others = f"<div class='sub'>Also similar: {', '.join(r['others'])}</div>"
    return (f"<div class='result tone-{r['tone']}'><div class='badge'>{r['label']}</div>"
            f"<div class='name'>{r['name']}</div><div class='sub'>{r['text']}</div>{others}</div>")


# ---------- Calculator ----------
def toggle_deposit(mode):
    return gr.update(visible=mode == "Percentage"), gr.update(visible=mode == "Manual")


def run_calc(country, total, schol, mode, pct, manual, rate, campus):
    cfg = storage.load()["countries"][country]
    ccy = COUNTRY_META[country]["currency"]
    r = logic.calculate(cfg, total, schol, mode, pct, manual, rate, campus)
    stat = lambda k, v, cls="": f"<div class='stat {cls}'><div class='k'>{k}</div><div class='v'>{v}</div></div>"
    return (
        "<div class='stat-grid'>"
        + stat("Net fee", fmt(r["net_fee"], "GBP"))
        + stat("Initial deposit", fmt(r["deposit"], "GBP"))
        + stat(f"Initial deposit ({ccy}, original rate)", fmt(r["deposit_local"], ccy))
        + stat("Remaining tuition fee", fmt(r["remaining"], "GBP"))
        + stat(f"Living cost ({campus})", fmt(r["living"], "GBP"))
        + stat("Adjusted rate", f"{r['adjusted_rate']:,.2f} {ccy}/GBP")
        + stat(f"Required bank statement ({ccy}, adjusted rate)", fmt(r["statement_local"], ccy), "big")
        + "</div>"
    )


# ---------- Settings ----------
def unlock(pin):
    ok = pin == ADMIN_PIN
    msg = "" if ok else "❌ Wrong PIN"
    return gr.update(visible=ok), gr.update(visible=not ok), msg


def region_rows(country):
    regs = storage.load()["countries"][country]["regions"]
    cats = COUNTRY_META[country]["categories"]
    # For Pakistan show only the restricted list; India shows everything.
    return [[r["name"], r["category"], ", ".join(r.get("aliases", []))] for r in regs]


def refresh_settings(country, filter_text=""):
    s = storage.load()["countries"][country]
    cats = list(COUNTRY_META[country]["categories"])
    rows = region_rows(country)
    if filter_text:
        rows = [r for r in rows if filter_text.lower() in (r[0] + " " + r[2]).lower()]
    names = [r["name"] for r in storage.load()["countries"][country]["regions"]]
    return (rows, gr.update(choices=cats, value=cats[0]), gr.update(choices=names, value=None),
            s["buffer"], s["living"]["London"], s["living"]["Main"],
            f"Add a region for **{country}**", storage.remote_enabled() and "🟢 Permanent storage on"
            or "🟡 Permanent storage not set up (see README)")


def add_region(country, name, category, aliases, filter_text):
    name = (name or "").strip()
    if not name:
        return gr.update(), "Enter a region name.", *([gr.update()] * 2)
    st = storage.load()
    regs = st["countries"][country]["regions"]
    al = [a.strip() for a in (aliases or "").split(",") if a.strip()]
    for r in regs:
        if r["name"].lower() == name.lower():
            r["category"], r["aliases"] = category, al
            break
    else:
        regs.append({"name": name, "category": category, "aliases": al})
    msg = storage.save(st)
    rows, _, dd, *_ = refresh_settings(country, filter_text)
    return rows, f"✅ {name} → {category}. {msg}", dd, ""


def remove_region(country, name, filter_text):
    if not name:
        return gr.update(), "Pick a region to remove.", gr.update()
    st = storage.load()
    c = st["countries"][country]
    c["regions"] = [r for r in c["regions"] if r["name"] != name]
    msg = storage.save(st)
    rows, _, dd, *_ = refresh_settings(country, filter_text)
    return rows, f"🗑️ Removed {name}. {msg}", dd


def save_rates(country, buffer, london, main):
    st = storage.load()
    c = st["countries"][country]
    c["buffer"], c["living"] = float(buffer or 0), {"London": float(london or 0), "Main": float(main or 0)}
    return storage.save(st)


# ---------- App ----------
with gr.Blocks(css=CSS, title="UoS Agent Tools", theme=gr.themes.Soft(primary_hue="teal")) as demo:
    country = gr.State("")
    unlocked_label = gr.State(False)

    gr.HTML("<div class='uos-header'><h1>🎓 University of Sunderland – Agent Tools</h1>"
            "<p>Region risk check &amp; bank statement calculator</p></div>")

    # Screen 1
    with gr.Column(visible=True) as picker:
        gr.Markdown("### Select your country")
        with gr.Row():
            btn_in = gr.Button("🇮🇳  India", elem_classes="pick-btn")
            btn_pk = gr.Button("🇵🇰  Pakistan", elem_classes="pick-btn")

    # Screen 2
    with gr.Column(visible=False) as workspace:
        with gr.Row():
            title = gr.Markdown("")
            switch = gr.Button("↩ Switch country", size="sm", scale=0)

        with gr.Tabs():
            with gr.Tab("📍 Region Check"):
                with gr.Column(elem_classes="card"):
                    q = gr.Textbox(label="Type a state, city or district",
                                   placeholder="e.g. Ludhiana, Kerala, Chanab Nager…")
                    pick = gr.Radio(label="Suggestions – tap one to check", choices=[], interactive=True)
                    go = gr.Button("Check region", elem_classes="primary-btn")
                result = gr.HTML("<div class='note'>Type a state, city or district above.</div>")

            with gr.Tab("🧮 Statement Calculator"):
                with gr.Column(elem_classes="card"):
                    with gr.Row():
                        total = gr.Number(label="Total fee (GBP)", value=0)
                        schol = gr.Number(label="Scholarship (GBP)", value=0)
                    with gr.Row():
                        rate = gr.Number(label="GBP → local currency rate (market rate)", value=0)
                        campus = gr.Radio(["London", "Main"], label="Campus", value="Main")
                    mode = gr.Radio(["Percentage", "Manual"], label="Deposit entry", value="Percentage")
                    pct = gr.Slider(0, 100, step=5, value=0, label="Deposit percentage (%)")
                    manual = gr.Number(label="Manual deposit (GBP)", value=0, visible=False)
                    calc = gr.Button("Calculate", elem_classes="primary-btn")
                calc_out = gr.HTML()

            with gr.Tab("⚙️ Settings"):
                with gr.Column(visible=True, elem_classes="card") as lock:
                    pin = gr.Textbox(label="Admin PIN", type="password")
                    unlock_btn = gr.Button("Unlock", elem_classes="primary-btn")
                    pin_msg = gr.Markdown("")
                with gr.Column(visible=False) as admin:
                    storage_note = gr.Markdown("")
                    with gr.Column(elem_classes="card"):
                        gr.Markdown("#### Regions")
                        flt = gr.Textbox(label="Filter list", placeholder="type to filter…")
                        table = gr.Dataframe(headers=["Region", "Category", "Alternate spellings"],
                                             interactive=False, wrap=True, max_height=320)
                        add_title = gr.Markdown("")
                        with gr.Row():
                            n_name = gr.Textbox(label="Region name")
                            n_cat = gr.Dropdown(label="Category", choices=[])
                            n_alias = gr.Textbox(label="Alternate spellings (comma separated)")
                        add_btn = gr.Button("Add / update region", elem_classes="primary-btn")
                        with gr.Row():
                            rm_name = gr.Dropdown(label="Remove a region", choices=[], filterable=True)
                            rm_btn = gr.Button("Remove", variant="stop", scale=0)
                        set_msg = gr.Markdown("")
                    with gr.Column(elem_classes="card"):
                        gr.Markdown("#### Calculator settings")
                        with gr.Row():
                            s_buf = gr.Number(label="Rate buffer added to market rate (local currency)")
                            s_lon = gr.Number(label="Living cost – London (GBP)")
                            s_main = gr.Number(label="Living cost – Main (GBP)")
                        save_btn = gr.Button("Save calculator settings", elem_classes="primary-btn")
                        save_msg = gr.Markdown("")

    # --- wiring ---
    def choose(c):
        meta = COUNTRY_META[c]
        return (c, gr.update(visible=False), gr.update(visible=True),
                f"## {meta['flag']} {c}", "", gr.update(choices=[], value=None),
                "<div class='note'>Type a state, city or district above.</div>", "",
                gr.update(visible=True), gr.update(visible=False))

    pick_outputs = [country, picker, workspace, title, q, pick, result, calc_out, lock, admin]
    btn_in.click(lambda: choose("India"), None, pick_outputs)
    btn_pk.click(lambda: choose("Pakistan"), None, pick_outputs)
    switch.click(lambda: ("", gr.update(visible=True), gr.update(visible=False)), None,
                 [country, picker, workspace])

    q.change(suggest, [country, q], pick)
    pick.input(show_result, [country, q, pick], result)
    go.click(show_result, [country, q, pick], result)
    q.submit(show_result, [country, q, pick], result)

    mode.change(toggle_deposit, mode, [pct, manual])
    calc.click(run_calc, [country, total, schol, mode, pct, manual, rate, campus], calc_out)

    settings_outs = [table, n_cat, rm_name, s_buf, s_lon, s_main, add_title, storage_note]
    unlock_btn.click(unlock, pin, [admin, lock, pin_msg]).then(
        refresh_settings, [country, flt], settings_outs)
    flt.change(lambda c, f: refresh_settings(c, f)[0], [country, flt], table)
    add_btn.click(add_region, [country, n_name, n_cat, n_alias, flt], [table, set_msg, rm_name, n_name])
    rm_btn.click(remove_region, [country, rm_name, flt], [table, set_msg, rm_name])
    save_btn.click(save_rates, [country, s_buf, s_lon, s_main], save_msg)

if __name__ == "__main__":
    demo.launch()
