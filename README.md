# \# Confession Preparation

# \### കുമ്പസാര തയ്യാറെടുപ്പ്

# 

# A quiet, private, bilingual (English + Malayalam) web tool for preparing to receive the Sacrament of Reconciliation.

# 

# Built for the Malayalam-speaking Catholic community — and for anyone who wants a gentle way to examine their conscience before confession.

# 

# \---

# 

# \## Why this exists

# 

# > \*"I wanted to confess, but I didn't have the right medium."\*

# 

# We have so many digital tools around us — apps for everything — yet none of them felt right for something as personal and sacred as preparing for confession.

# 

# So the developer prayed about it. Sat with the thought for a long time. And step by step, began to build. What exists today is the answer to that prayer.

# 

# The hope is simple: that this small tool helps someone examine their conscience honestly, prepare their heart with peace, and walk into the confessional with confidence in God's mercy.

# 

# \---

# 

# \## Features

# 

# \- \*\*Bilingual throughout\*\* — every prayer, sin, and instruction is available in English and Malayalam

# \- \*\*Ten Commandments examination of conscience\*\* — the traditional structure, with Scripture verse on each section

# \- \*\*Seven Capital Sins\*\* and \*\*sins against confession itself\*\* included as separate sections

# \- \*\*Per-sin pastoral notes\*\* — clarifications for sins that are easy to misunderstand (anxiety, intrusive thoughts, pride, etc.)

# \- \*\*Prayers of the Penitent\*\* — Confiteor, Act of Contrition, and other prayers shown side by side in both languages

# \- \*\*Global search\*\* — find any sin by English or Malayalam text

# \- \*\*Quick Jump panel\*\* — one-click navigation to any section

# \- \*\*Floating Previous / Next bar\*\* — always accessible on mobile

# \- \*\*Personal notes field\*\* — for your own resolution

# \- \*\*Password-protected PDF download\*\* — a private prep sheet you can bring to confession

# \- \*\*Pastoral guardrails\*\* — gentle reminders throughout that the goal is a contrite heart, not a perfect list

# \- \*\*Safeguarding panel\*\* — crisis line information for those in distress, kept separate from the sin list

# 

# \---

# 

# \## Privacy

# 

# \*\*Your selections, notes, and generated PDF are processed entirely on your device and are not sent to this app's server.\*\*

# 

# \- No accounts. No login.

# \- No tracking. No analytics.

# \- No cookies beyond a `localStorage` entry that saves your personal notes so you don't lose them on refresh.

# \- The PDF is generated entirely in your browser. The password, if you set one, never leaves your device.

# 

# The Flask backend serves only the page and the sin data (`sins.json`). It has no API for receiving user data.

# 

# \*\*Network notes:\*\* The page loads fonts from Google Fonts and the PDF libraries (jsPDF, html2canvas) from public CDNs. These see the page request itself but no user data. Self-hosting these resources is a future improvement.

# 

# \---

# 

# \## Technology

# 

# \- \*\*Backend:\*\* Flask (Python 3.x), Gunicorn

# \- \*\*Frontend:\*\* Vanilla HTML / CSS / JavaScript (no framework)

# \- \*\*Data:\*\* A single `sins.json` file, bilingual from the ground up

# \- \*\*PDF generation:\*\* `jsPDF` + `html2canvas` — with the browser's native Malayalam shaping, captured as PNG, embedded with optional AES encryption

# \- \*\*Hosting:\*\* Railway (auto-deployed from `main`)

# 

# \---

# 

# \## Running locally

# 

# ```bash

# \# 1. Clone the repository

# git clone https://github.com/Edwinton/confession-app.git

# cd confession-app

# 

# \# 2. (Optional) Create a virtual environment

# python -m venv venv

# source venv/bin/activate         # On Windows: venv\\Scripts\\activate

# 

# \# 3. Install dependencies

# pip install -r requirements.txt

# 

# \# 4. Run the development server

# python app.py

# 

# \# 5. Open in your browser

# \# http://127.0.0.1:5000

