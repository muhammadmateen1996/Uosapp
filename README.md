---
title: UoS Agent Tools
emoji: 🎓
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.34.1
app_file: app.py
pinned: false
short_description: Region risk check and bank statement calculator
---

# UoS Agent Tools

Region risk check + bank statement calculator for University of Sunderland agents (India & Pakistan).

## Deploy on Hugging Face (free)
1. Create a new Space (SDK: Gradio) and upload all files from this repo.
2. In Space **Settings → Variables and secrets** add:
   - `ADMIN_PIN` (secret) – PIN for the Settings tab (default `1234`, change it!)
   - `HF_TOKEN` (secret) – a *write* token from your HF account
   - `SETTINGS_REPO` (variable) – e.g. `yourname/uos-settings` (private dataset repo, created automatically)
   
   Without the last two, settings changes are lost when the Space restarts.

## Files
- `app.py` UI · `logic.py` matching & calculation · `defaults.py` starting regions/rates · `storage.py` saving settings
