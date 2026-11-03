# Ambience Inpatient Chorus — Pediatric Ward Multi-Archetype Action Engine

Prototype Streamlit app for **Unit 4B attending handoff**: protocol-gated clinical decision support, zero-click EHR verification, point-of-care AutoCDI capture, and Human-in-the-Loop Epic order staging across four pediatric archetypes.

## Product Thesis

Inpatient attending-to-attending handoffs fail when synthesis, verification, documentation, and ordering live in separate systems. This prototype bridges **Day Attending** synthesis and **Night Attending** cross-cover into one action surface:

- **Protocol-gated CDS** — archetype-specific gates (MTX nomogram, IV→PO stewardship, refeeding labs, Incomplete KD AHA pathway) drive the next clinical move.
- **Zero-click raw EHR verification** — MAR, Lab, Urine, and Pharm evidence popovers sit beside every handoff item so attendings can attest without leaving the queue.
- **Point-of-care AutoCDI** — CC/MCC language (AKI, antineoplastic adverse effect, refeeding hypophosphatemia, Incomplete KD) is reviewed in the same HITL dialog as orders.
- **Strict Human-in-the-Loop Epic staging** — no silent write-back; every order is signed à la carte or as a bundle, then mirrored into Day/Night checklists and telemetry tile state.

## The 4 Clinical Archetypes

- **Emma Rodriguez (4B-10) — HD-MTX Hour-48 delayed clearance & AKI**  
  High-risk B-ALL on COG AALL1131; Hour-48 MTX 4.20 µmol/L (10.5× cutoff), creatinine +70%, acidic urine pH → leucovorin escalation, hyperhydration, NaHCO₃ bolus, Voraxaze standby.

- **Maya Patel (4B-12) — IV-to-PO pyelonephritis stewardship gate**  
  Afebrile ≥24h with pansensitive *E. coli*; unlocks PO Cephalexin switch, PIV/IVF discontinuation, and discharge instructions with 48h PCP follow-up.

- **Chloe Miller (4B-14) — Refeeding syndrome (severe hypophosphatemia & sinus bradycardia)**  
  Day-3 refeeding with HR nadir 38 and Phos 1.9 → continuous telemetry + calorie hold, IV NaPhos repletion, bedrest/orthostatic precautions + thiamine.

- **Leo Kim (4B-16) — Incomplete Kawasaki Disease (AHA algorithmic trigger)**  
  Fever Day 6 with only 2/5 clinical criteria; CRP/ESR + ≥3 supplemental labs confirm Incomplete KD → IVIG + high-dose ASA, STAT coronary echo, infusion-reaction / 36h fever clock.

## Core Product Guardrails

- **À la carte vs. bundle Epic signing** — “Send to Epic for Signature” opens a HITL composer where each order can be signed independently (`⚡ Sign Order` / undo) or via **Sign All**; progress is reflected on the CTA (`0/4`, `2/4 · In Progress`, `4/4 · Dr. Patel`).
- **Automatic handoff checklist sync** — signing an order checks the linked Day and Night queue items and flips only the corresponding Core Telemetry tile(s) to addressed green.
- **Zero-click verification pills** — Lab, Urine, MAR, and Pharm popovers expose structured evidence without leaving the action queue.
- **Night Attending dark mode** — selecting **Night Attending** applies a cohesive midnight navy-slate theme for eye-friendly cross-cover without washing out critical red/green badges.

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints (typically `http://localhost:8501`). Use the left census rail to switch patients and the top segmented control to toggle **Day Attending** vs **Night Attending**.

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub (ensure `.env` and `.streamlit/secrets.toml` are not committed).
2. In [Share.streamlit.io](https://share.streamlit.io), create a new app pointing at `app.py`.
3. Set Python to a 3.10–3.12 runtime if prompted; Cloud will install from `requirements.txt`.
