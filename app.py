"""Multi-condition inpatient floor attending handoff & action-engine."""

from __future__ import annotations

import html
import json
import re
import uuid
from datetime import datetime, timedelta

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Unit 4B Attending Handoff",
    page_icon=":material/medical_services:",
    layout="wide",
)

# Ambience / Commure enterprise clinical chrome
st.html(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
  --amb-alabaster: #F7F6F2;
  --amb-card: #FFFFFF;
  --amb-stone: #EFECE6;
  --amb-border: #E4E4E0;
  --amb-border-strong: #CBD5E1;
  --amb-ink: #0F172A;
  --amb-muted: #475569;
  --amb-subtle: #64748B;
  --amb-forest: #0D5C46;
  --amb-forest-hover: #064E3B;
  --amb-forest-soft: #ECFDF5;
  --amb-forest-text: #047857;
  --amb-forest-border: #A7F3D0;
  --amb-crimson: #BE123C;
  --amb-crimson-soft: #FFF1F2;
  --amb-crimson-border: #FECDD3;
  --amb-crimson-bar: #E11D48;
  --amb-amber: #B45309;
  --amb-amber-soft: #FFFBEB;
  --amb-amber-border: #FDE68A;
  --amb-amber-bar: #D97706;
  --amb-emerald: #047857;
  --amb-emerald-soft: #ECFDF5;
  --amb-emerald-border: #A7F3D0;
  --amb-emerald-bar: #10B981;
  --amb-obsidian: #0B0F17;
  --amb-carbon: #111827;
  --amb-pearl: #F8FAFC;
  --amb-night-border: #1E293B;
  --amb-radius: 14px;
  --amb-shadow: 0 1px 3px rgba(15, 23, 42, 0.03), 0 6px 16px -4px rgba(15, 23, 42, 0.04);
  --amb-shadow-hover: 0 4px 20px -2px rgba(15, 23, 42, 0.07);
  --amb-font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --amb-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
}

/* Apply Inter to text only — never blanket-override icon spans */
html, body, [data-testid="stAppViewContainer"], .stApp,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"],
p, div, label, h1, h2, h3, h4, h5, h6, button, input, textarea, select,
table, th, td {
  font-family: var(--amb-font) !important;
}
code, pre, .mono, .jb-mono, .cha-metric-value, .ah-tile-value,
.ah-tile-ts, .ah-delta-crit, .ah-delta-ok, .ah-delta-warn,
.lab-pill, .supp-lab-pill, .room-pill, .icd-pill,
[data-testid="stMetricValue"] {
  font-family: var(--amb-mono) !important;
}

/* Restore Material Icons so expand_more / expand_less never render as words */
[data-testid="stIconMaterial"],
.material-symbols-rounded,
.material-icons,
summary span[data-testid="stIconMaterial"],
[data-testid="stExpanderToggleIcon"],
[data-testid="stExpander"] span[data-testid="stIconMaterial"],
[data-testid="stPopover"] span[data-testid="stIconMaterial"],
[data-testid="stBaseButton-header"] span[data-testid="stIconMaterial"],
span[data-testid="stIconMaterial"] {
  font-family: "Material Symbols Rounded", "Material Icons" !important;
  font-weight: normal !important;
  font-style: normal !important;
  font-size: 1.25rem !important;
  line-height: 1 !important;
  letter-spacing: normal !important;
  text-transform: none !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  white-space: nowrap !important;
  word-wrap: normal !important;
  direction: ltr !important;
  -webkit-font-smoothing: antialiased !important;
  flex-shrink: 0 !important;
}

/* Expander & popover header flex — icons and titles never collide */
[data-testid="stExpander"] details > summary {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 12px !important;
  padding: 12px 16px !important;
  line-height: 1.4 !important;
  height: auto !important;
  min-height: 48px !important;
}
[data-testid="stExpander"] details > summary p {
  margin: 0 !important;
  line-height: 1.4 !important;
  word-break: break-word !important;
}
[data-testid="stPopover"] > button,
[data-testid="stPopoverButton"] {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 8px !important;
  height: auto !important;
  min-height: 38px !important;
  padding: 8px 12px !important;
  line-height: 1.35 !important;
  white-space: normal !important;
}

#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
header[data-testid="stHeader"] {
  background: transparent !important;
  background-color: transparent !important;
  height: 0px !important;
  min-height: 0px !important;
  border: none !important;
  box-shadow: none !important;
  pointer-events: none !important;
}
div[data-testid="stToolbar"],
div[data-testid="stDecoration"] {
  display: none !important;
}
.block-container {
  padding-top: 1.5rem !important;
  padding-bottom: 2rem !important;
  max-width: 1520px !important;
}
[data-testid="stAppViewContainer"] > .main,
[data-testid="stAppViewContainer"] {
  background-color: var(--amb-alabaster) !important;
  color: var(--amb-ink) !important;
}
[data-testid="stVerticalBlockBorderWrapper"] {
  background-color: var(--amb-card) !important;
  border: 1px solid var(--amb-border) !important;
  border-radius: var(--amb-radius) !important;
  box-shadow: var(--amb-shadow) !important;
  padding: 18px 20px !important;
  transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color: var(--amb-border-strong) !important;
  box-shadow: var(--amb-shadow-hover) !important;
}

/* Zone A — Linear-style ward census rail (outer shell only; cards styled below) */
.st-key-ward_census_rail,
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div .st-key-ward_census_rail),
div[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-ward_census_rail):not(:has(.census-card-marker)) {
  background: #F3F2EE !important;
  border: 1px solid #E4E3DD !important;
  border-radius: 12px !important;
  padding: 10px 8px !important;
  box-shadow: none !important;
}
.st-key-ward_census_rail {
  background: #F3F2EE !important;
  border: 1px solid #E4E3DD !important;
  border-radius: 12px !important;
  padding: 10px 8px !important;
  box-shadow: none !important;
}
.linear-rail-header {
  font-family: 'Inter', sans-serif !important;
  font-size: 0.68rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  color: #64748B !important;
  padding: 4px 10px 8px 10px !important;
  margin-bottom: 4px !important;
  border-bottom: 1px solid #E4E3DD !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
}
.linear-rail-footer {
  border-top: 1px solid #E4E3DD;
  margin-top: 8px;
  padding-top: 8px;
  font-family: var(--amb-mono) !important;
  font-size: 0.68rem !important;
  color: #64748B !important;
  line-height: 1.35;
  padding-left: 10px;
  padding-right: 10px;
}
.pill-room {
  font-family: var(--amb-mono) !important;
  font-size: 0.70rem !important;
  font-weight: 600 !important;
  color: #475569 !important;
  background: #E2E8F0 !important;
  padding: 1px 5px !important;
  border-radius: 4px !important;
  margin-right: 6px !important;
  display: inline-block !important;
}
.pill-crit {
  font-family: var(--amb-mono) !important;
  font-size: 0.68rem !important;
  font-weight: 600 !important;
  color: #BE123C !important;
  background: #FFE4E6 !important;
  border: 1px solid #FECDD3 !important;
  padding: 1px 6px !important;
  border-radius: 4px !important;
  display: inline-block !important;
  margin-right: 4px !important;
  margin-top: 2px !important;
}
.pill-ok {
  font-family: var(--amb-mono) !important;
  font-size: 0.68rem !important;
  font-weight: 600 !important;
  color: #047857 !important;
  background: #D1FAE5 !important;
  border: 1px solid #A7F3D0 !important;
  padding: 1px 6px !important;
  border-radius: 4px !important;
  display: inline-block !important;
  margin-right: 4px !important;
  margin-top: 2px !important;
}
.pill-muted {
  font-family: var(--amb-mono) !important;
  font-size: 0.68rem !important;
  font-weight: 600 !important;
  color: #64748B !important;
  background: #F1F5F9 !important;
  border: 1px solid #E2E8F0 !important;
  padding: 1px 6px !important;
  border-radius: 4px !important;
  display: inline-block !important;
  margin-right: 4px !important;
  margin-top: 2px !important;
}
.linear-nav-pills {
  padding: 0 !important;
  margin-top: 6px !important;
  line-height: 1.45 !important;
}

/* Full-card clickable census patient rows */
.census-card-wrapper,
.census-card-marker {
  position: relative !important;
  border-radius: 12px !important;
  cursor: pointer !important;
}
.census-card-top {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 8px !important;
}
.census-card-top-left {
  display: flex !important;
  align-items: center !important;
  gap: 0 !important;
  min-width: 0 !important;
  flex: 1 1 auto !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.86rem !important;
  font-weight: 600 !important;
  color: #0F172A !important;
  line-height: 1.3 !important;
}
/* Default/Inactive Patient Card: Light Grey, flat */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.census-card-marker),
div:has(> div > div > .census-card-marker) {
  position: relative !important;
  padding: 12px 14px !important;
  margin-bottom: 8px !important;
  border-radius: 12px !important;
  background-color: #F8FAFC !important; /* Recessed light grey */
  border: 1px solid #E2E8F0 !important;
  transition: all 0.15s ease-in-out !important;
  cursor: pointer !important;
  user-select: none !important;
  overflow: hidden !important;
  box-shadow: none !important;
}
/* Hover state for inactive cards */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.census-card-marker):hover {
  background-color: #F1F5F9 !important;
  border-color: #CBD5E1 !important;
}
/* Active/Selected Patient Card: Soft Light Purple with Purple Accent Border */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.census-card-active),
div:has(> div > div > .census-card-active) {
  background-color: #F3E8FF !important; /* Light lavender purple */
  border: 1.5px solid #7C3AED !important; /* Crisp violet border */
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.12) !important;
}
.census-card-marker, .census-card-marker * {
  cursor: pointer !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.census-card-marker)
  > div[data-testid="stVerticalBlock"] {
  gap: 0 !important;
  position: relative !important;
}
/* Completely collapse the hidden trigger button row — no empty box */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.census-card-marker)
  div[data-testid="stButton"],
div[data-testid="stElementContainer"]:has(.census-card-marker)
  + div[data-testid="stElementContainer"],
div.element-container:has(.census-card-marker) + div.element-container {
  height: 0px !important;
  min-height: 0px !important;
  max-height: 0px !important;
  margin: 0px !important;
  padding: 0px !important;
  overflow: hidden !important;
  opacity: 0 !important;
  pointer-events: none !important;
  position: absolute !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.census-card-marker)
  div[data-testid="stButton"] > button {
  height: 0px !important;
  min-height: 0px !important;
  opacity: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
}
/* Hide the census click-binder host element from layout */
.census-click-binder-host,
.shift-toggle-style-host {
  display: none !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}

/* Sticky roster column */
div[data-testid="stHorizontalBlock"]:has(.st-key-ward_census_rail)
  > div[data-testid="stColumn"]:first-child,
div[data-testid="stHorizontalBlock"]:has(.st-key-ward_census_rail)
  > div[data-testid="column"]:first-child {
  position: sticky !important;
  top: 1.25rem !important;
  height: calc(100vh - 2.5rem) !important;
  align-self: flex-start !important;
  display: flex !important;
  flex-direction: column !important;
  overflow: visible !important;
}
/* Hide bulky radio circles if any remain in sidebar */
[data-testid="stRadio"] input[type="radio"] + div {
  display: none !important;
}

/* Apple Health Summary Tile Container — identical for all 4 telemetry cards */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.ah-tile-body) {
  background-color: #FFFFFF !important;
  border: 1px solid #E5E5EA !important;
  border-radius: 16px !important;
  padding: 14px 14px 16px 14px !important;
  padding-bottom: 16px !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03), 0 1px 2px rgba(0, 0, 0, 0.02) !important;
  overflow: visible !important;
  height: auto !important;
  min-height: 0 !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease !important;
  position: relative !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.ah-tile-body):hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06) !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.ah-tile-body)
  > div[data-testid="stVerticalBlock"] {
  gap: 10px !important;
  height: auto !important;
  min-height: 100% !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-between !important;
  overflow: visible !important;
}

/* Core telemetry tile body — same min-height + footer gap on every card */
.ah-tile-body {
  min-height: 115px !important;
  height: auto !important;
  margin-bottom: 12px !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-between !important;
  padding-bottom: 0 !important;
  color: #0F172A !important;
  flex-shrink: 0 !important;
}
.ah-tile-head {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 8px !important;
}
.ah-tile-cat {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  min-width: 0 !important;
  flex: 1 1 auto !important;
}
.ah-dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  flex-shrink: 0;
  display: inline-block;
}
.ah-tile-body.tier-red .ah-dot { background: #E11D48; }
.ah-tile-body.tier-amber .ah-dot { background: #D97706; }
.ah-tile-body.tier-green .ah-dot { background: #059669; }
.ah-cat-label {
  font-family: 'Inter', sans-serif !important;
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  white-space: nowrap !important;
  overflow: visible !important;
  text-overflow: unset !important;
}
.ah-tile-body.tier-red .ah-cat-label { color: #E11D48 !important; }
.ah-tile-body.tier-amber .ah-cat-label { color: #D97706 !important; }
.ah-tile-body.tier-green .ah-cat-label { color: #059669 !important; }
.ah-tile-ts {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.68rem !important;
  color: #94A3B8 !important;
  font-weight: 500 !important;
  flex-shrink: 0 !important;
}
.ah-tile-hero {
  margin: 6px 0 2px 0 !important;
  display: flex !important;
  align-items: baseline !important;
  gap: 4px !important;
  min-width: 0 !important;
}
.ah-tile-value {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 1.85rem !important;
  font-weight: 700 !important;
  letter-spacing: -0.04em !important;
  line-height: 1.05 !important;
  color: #0F172A !important;
  white-space: nowrap !important;
}
.ah-tile-value.crit { color: #BE123C !important; }
.ah-tile-unit {
  font-family: 'Inter', sans-serif !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  color: #64748B !important;
  white-space: nowrap !important;
}
.ah-tile-ctx {
  font-family: 'Inter', sans-serif !important;
  font-size: 0.76rem !important;
  font-weight: 500 !important;
  color: #475569 !important;
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: unset !important;
  line-height: 1.35 !important;
}
.mar-detail-card {
  border-radius: 12px;
  padding: 12px 14px;
  margin: 0 0 12px 0;
  border: 1.5px solid #A7F3D0;
  background: #ECFDF5;
  color: #064E3B;
}
.mar-detail-card.pending {
  border-color: #FECDD3;
  background: #FFF1F2;
  color: #9F1239;
}
.mar-detail-title {
  font-family: 'Inter', sans-serif;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin: 0 0 8px 0;
  color: #047857;
}
.mar-detail-card.pending .mar-detail-title { color: #BE123C; }
.mar-detail-section {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid rgba(16, 185, 129, 0.25);
}
.mar-detail-card.pending .mar-detail-section {
  border-top-color: rgba(244, 63, 94, 0.25);
}
.mar-detail-heading {
  font-family: 'Inter', sans-serif;
  font-size: 0.78rem;
  font-weight: 700;
  margin: 0 0 6px 0;
}
.mar-detail-row {
  display: grid;
  grid-template-columns: 7.5rem 1fr;
  gap: 6px 10px;
  margin: 0 0 4px 0;
  font-size: 0.80rem;
  line-height: 1.4;
}
.mar-detail-key {
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  color: #334155;
}
.mar-detail-val {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.74rem;
  font-weight: 500;
  color: #0F172A;
}
/* Day defensive: light-tinted provenance / intervention surfaces keep dark text */
.mar-detail-card,
.mar-detail-card.pending,
[style*="background:#FEF2F2"],
[style*="background: #FEF2F2"],
[style*="background:#FFF1F2"],
[style*="background: #FFF1F2"],
[style*="background:#F0FDF4"],
[style*="background: #F0FDF4"],
[style*="background:#EFF6FF"],
[style*="background: #EFF6FF"],
[style*="background:#FFFBEB"],
[style*="background: #FFFBEB"],
[style*="background:#ECFDF5"],
[style*="background: #ECFDF5"],
.protocol-scroll-box tbody tr.row-red td,
.protocol-scroll-box tbody tr.row-amber td {
  color: #0F172A !important;
}
.mar-detail-card .mar-detail-key { color: #334155 !important; }
.mar-detail-card .mar-detail-val { color: #0F172A !important; }
.mar-detail-card .mar-detail-title { color: #047857 !important; }
.mar-detail-card.pending .mar-detail-title { color: #BE123C !important; }
.mar-detail-card .mar-detail-heading { color: #0F172A !important; }
.ah-delta-crit {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.70rem !important;
  font-weight: 600 !important;
  color: #BE123C !important;
  background: #FFE4E6 !important;
  padding: 1px 5px !important;
  border-radius: 4px !important;
  margin-right: 4px !important;
  display: inline-block !important;
}
.ah-delta-ok {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.70rem !important;
  font-weight: 600 !important;
  color: #047857 !important;
  background: #D1FAE5 !important;
  padding: 1px 5px !important;
  border-radius: 4px !important;
  margin-right: 4px !important;
  display: inline-block !important;
}
.ah-delta-warn {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.70rem !important;
  font-weight: 600 !important;
  color: #B45309 !important;
  background: #FEF3C7 !important;
  padding: 1px 5px !important;
  border-radius: 4px !important;
  margin-right: 4px !important;
  display: inline-block !important;
}

/* Telemetry card shell — equal padding/overflow on cols 0–3 (no first-child carve-outs) */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.ah-tile-body) {
  padding: 14px 14px 16px 14px !important;
  padding-bottom: 16px !important;
  overflow: visible !important;
  height: auto !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.ah-tile-body)
  > div[data-testid="stVerticalBlock"] {
  gap: 0 !important;
  height: auto !important;
  overflow: visible !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.ah-tile-body)
  [data-testid="stPopover"] {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
  flex-shrink: 0 !important;
}
/* Neutralize any accidental first-column negative margins on telemetry popovers */
div[data-testid="stHorizontalBlock"]:has(.ah-tile-body)
  > div[data-testid="stColumn"] [data-testid="stPopover"] button,
div[data-testid="stHorizontalBlock"]:has(.ah-tile-body)
  > div[data-testid="stColumn"]:first-child [data-testid="stPopover"] button {
  margin-bottom: 0 !important;
  border-radius: 8px !important;
  padding: 0 12px !important;
}

/* Unify ALL popover buttons — single line, identical slate-blue chip */
div[data-testid="stPopover"] > div > button,
div[data-testid="stPopover"] button {
  background-color: #EFF6FF !important;
  color: #1E3A8A !important;
  border: 1px solid #BFDBFE !important;
  border-radius: 8px !important;
  height: 36px !important;
  min-height: 36px !important;
  max-height: 36px !important;
  padding: 0 12px !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  box-shadow: none !important;
}
div[data-testid="stPopover"] button p {
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  margin: 0 !important;
  color: #1E3A8A !important;
}

.telemetry-section-header {
  font-family: 'Inter', sans-serif !important;
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
  color: #64748B !important;
  margin: 12px 0 6px 2px !important;
}
.delta-new {
  background: #FFFBEB;
  border-left: 3px solid #D97706;
  color: #0F172A;
  padding: 2px 6px;
  border-radius: 4px;
}
.delta-crit {
  background: #FFF1F2;
  border-left: 3px solid #E11D48;
  color: #0F172A;
  padding: 2px 6px;
  border-radius: 4px;
}
.delta-good {
  background: #ECFDF5;
  border-left: 3px solid #10B981;
  color: #0F172A;
  padding: 2px 6px;
  border-radius: 4px;
}

/* Semantic lab value pills (AHA / pediatric cutoffs) */
.lab-pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  margin: 0.35rem 0 0.15rem 0;
}
.lab-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  line-height: 1.25;
  white-space: nowrap;
  border: 1px solid transparent;
}
.lab-pill.red {
  color: #BE123C;
  background: #FFF1F2;
  border-color: #FECDD3;
  font-family: var(--amb-mono) !important;
}
.lab-pill.amber {
  color: #B45309;
  background: #FFFBEB;
  border-color: #FDE68A;
  font-family: var(--amb-mono) !important;
}
.lab-pill.green {
  color: #047857;
  background: #ECFDF5;
  border-color: #A7F3D0;
  font-family: var(--amb-mono) !important;
}
.maya-rx-badge {
  display: block;
  margin-top: 8px;
  padding: 8px 10px;
  border-radius: 10px;
  font-size: 0.72rem;
  font-weight: 650;
  line-height: 1.35;
  border: 1px solid #A7F3D0;
  background: #ECFDF5;
  color: #0D5C46 !important;
}
.maya-rx-badge.switched {
  background: #D1FAE5;
  border-color: #0D5C46;
  color: #064E3B !important;
}
.mic-table-wrap {
  width: 100%;
  overflow-x: auto;
  margin: 4px 0 12px;
}
.mic-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 6px;
  font-size: 0.78rem;
  color: #0F172A;
}
.mic-table th {
  text-align: left;
  font-size: 0.68rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #475569;
  padding: 6px 10px;
  background: #F1F0EC;
  border: 1px solid #E4E4E0;
}
.mic-table th:first-child { border-radius: 8px 0 0 8px; }
.mic-table th:last-child { border-radius: 0 8px 8px 0; }
.mic-table td {
  padding: 10px;
  background: #FFFFFF;
  border-top: 1px solid #E4E4E0;
  border-bottom: 1px solid #E4E4E0;
  vertical-align: top;
  line-height: 1.4;
}
.mic-table td:first-child {
  border-left: 1px solid #E4E4E0;
  border-radius: 10px 0 0 10px;
  font-weight: 650;
}
.mic-table td:last-child {
  border-right: 1px solid #E4E4E0;
  border-radius: 0 10px 10px 0;
}
.mic-table .mono {
  font-family: var(--amb-mono) !important;
  font-weight: 600;
}
.mic-table tr.row-active td {
  background: #ECFDF5 !important;
  border-color: #0D5C46 !important;
  border-top-width: 2px !important;
  border-bottom-width: 2px !important;
}
.mic-table tr.row-active td:first-child { border-left: 2px solid #0D5C46 !important; }
.mic-table tr.row-active td:last-child { border-right: 2px solid #0D5C46 !important; }
.mic-table tr.row-target td {
  background: #F0FDF4 !important;
  border-style: dashed !important;
  border-color: #0D5C46 !important;
  border-top-width: 2px !important;
  border-bottom-width: 2px !important;
}
.mic-table tr.row-target td:first-child {
  border-left: 2px dashed #0D5C46 !important;
}
.mic-table tr.row-target td:last-child {
  border-right: 2px dashed #0D5C46 !important;
}
.mic-table tr.row-chosen td {
  background: #D1FAE5 !important;
  border-color: #0D5C46 !important;
  border-top-width: 2px !important;
  border-bottom-width: 2px !important;
  font-weight: 700;
}
.mic-table tr.row-chosen td:first-child { border-left: 2px solid #0D5C46 !important; }
.mic-table tr.row-chosen td:last-child { border-right: 2px solid #0D5C46 !important; }
.mic-table tr.row-warn td {
  background: #FFFBEB !important;
  color: #B45309 !important;
  border-color: #FDE68A !important;
}
.mic-status-badge {
  display: inline-block;
  margin-top: 4px;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 700;
  background: #FFFFFF;
  border: 1px solid #A7F3D0;
  color: #0D5C46;
}
.mic-status-badge.muted {
  background: #F8FAFC;
  border-color: #E2E8F0;
  color: #64748B;
  font-weight: 600;
}
.mic-footnote {
  font-size: 0.72rem;
  color: #64748B !important;
  margin-top: 6px;
  line-height: 1.35;
}
.lab-legend {
  font-size: 0.78rem;
  color: #334155;
  margin: 0.15rem 0 0.4rem 0;
  line-height: 1.35;
}
.lab-detail-row {
  display: grid;
  grid-template-columns: 145px max-content 1fr;
  column-gap: 16px;
  row-gap: 0.35rem;
  align-items: center;
  padding: 0.55rem 0;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.84rem;
  color: #0f172a;
  height: auto !important;
  min-height: fit-content !important;
  line-height: 1.45 !important;
  overflow-wrap: break-word !important;
}
.lab-detail-row:last-child { border-bottom: none; }
.lab-detail-name { font-weight: 650; color: #334155; line-height: 1.35; }
.lab-detail-pill {
  flex-shrink: 0 !important;
  white-space: nowrap !important;
  overflow: visible !important;
  display: inline-flex !important;
  align-items: center !important;
}
.lab-detail-pill .lab-pill {
  flex-shrink: 0 !important;
  white-space: nowrap !important;
  overflow: visible !important;
}
.lab-detail-cut {
  color: #475569;
  font-size: 0.78rem;
  line-height: 1.4 !important;
  word-wrap: break-word;
  overflow-wrap: anywhere;
  min-width: 0;
}

/* Supplemental AHA lab cards — spacious 2-col responsive grid */
.supp-lab-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 10px;
  margin-bottom: 12px;
  width: 100%;
}
.supp-lab-card {
  padding: 12px 14px;
  border-radius: 8px;
  height: auto !important;
  min-height: fit-content !important;
  overflow: visible !important;
  display: flex;
  flex-direction: column;
  gap: 6px;
  border: 1px solid transparent;
  box-sizing: border-box;
}
.supp-lab-card.red {
  background: #fef2f2;
  border-color: #fca5a5;
}
.supp-lab-card.green {
  background: #ecfdf5;
  border-color: #6ee7b7;
}
.supp-lab-card.amber {
  background: #fffbeb;
  border-color: #fcd34d;
}
.supp-lab-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}
.supp-lab-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.3;
}
.supp-lab-pill {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
  border: 1px solid transparent;
}
.supp-lab-card.red .supp-lab-pill {
  color: #b91c1c;
  background: #fff;
  border-color: #fca5a5;
}
.supp-lab-card.green .supp-lab-pill {
  color: #047857;
  background: #fff;
  border-color: #6ee7b7;
}
.supp-lab-card.amber .supp-lab-pill {
  color: #b45309;
  background: #fff;
  border-color: #fcd34d;
}
.supp-lab-cut {
  font-size: 0.78rem;
  color: #334155;
  line-height: 1.4;
  word-wrap: break-word;
  overflow-wrap: anywhere;
  margin-top: 2px;
}
@media (max-width: 700px) {
  .supp-lab-grid { grid-template-columns: 1fr; }
}

/* Checklist EHR evidence source cards */
.ehr-ev-card {
  background: #ffffff;
  border: 1.5px solid #cbd5e1;
  border-radius: 10px;
  padding: 12px 14px;
  color: #0f172a !important;
  line-height: 1.45 !important;
  height: auto !important;
  overflow-wrap: break-word !important;
}
.ehr-ev-header {
  font-size: 0.84rem;
  font-weight: 800;
  color: #0f172a !important;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 8px 10px;
  margin-bottom: 10px;
  line-height: 1.4 !important;
}
.ehr-ev-section {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #0369a1 !important;
  margin: 8px 0 4px;
}
.ehr-ev-body {
  font-size: 0.82rem;
  color: #0f172a !important;
  background: #f8fafc;
  border-left: 3px solid #94a3b8;
  padding: 8px 10px;
  border-radius: 0 8px 8px 0;
  white-space: normal;
  line-height: 1.45 !important;
}
.ehr-ev-subhead {
  font-size: 0.78rem;
  font-weight: 800;
  color: #0369a1 !important;
  margin: 10px 0 4px;
}
.ehr-ev-rxn {
  margin: 6px 0 8px;
  padding: 8px 10px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}
.ehr-ev-rxn-title {
  font-weight: 800;
  color: #0f172a !important;
  margin-bottom: 4px;
  font-size: 0.8rem;
}
.ehr-ev-why {
  font-size: 0.82rem;
  color: #0f172a !important;
  background: #fffbeb;
  border-left: 3px solid #d97706;
  padding: 8px 10px;
  border-radius: 0 8px 8px 0;
  line-height: 1.45 !important;
  margin-top: 4px;
}
/* Met / positive clinical criteria inside Verbatim EHR excerpts */
.crit-met-red {
  background-color: #FFF1F2;
  color: #BE123C !important;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #FECDD3;
  display: inline;
  line-height: 1.55;
}
.crit-met-green {
  background-color: #D1FAE5;
  color: #065f46 !important;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 5px;
  border: 1px solid #6EE7B7;
  display: inline-block;
  line-height: 1.45;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.72rem !important;
}
.ah-tile-ctx .crit-met-red {
  background: #FFE4E6;
  color: #BE123C !important;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 5px;
  border: 1px solid #FECDD3;
  display: inline-block;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.72rem !important;
}
/* Critical / addressed tile border accents */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.ah-tile-body.tier-red) {
  border-left: 3px solid #E11D48 !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.ah-tile-body.addressed),
div[data-testid="stVerticalBlockBorderWrapper"]:has(.ah-tile-body.tier-green.addressed) {
  border-left: 3px solid #10B981 !important;
}
.ah-tile-body.addressed .ah-dot { background: #047857 !important; }
.ah-tile-body.addressed .ah-cat-label { color: #047857 !important; }
.ah-tile-value.pathogen {
  color: #BE123C !important;
  font-size: 1.75rem !important;
}
.ah-tile-unit.subtle {
  font-size: 1.05rem !important;
  color: #475569 !important;
  font-weight: 600 !important;
}
.crit-absent {
  color: #64748b !important;
  font-weight: 500;
}
[class*="st-key-ehr_src_"] button,
[class*="st-key-ehr_src_"] [data-testid="stPopoverButton"] {
  background-color: #ECFDF5 !important;
  color: #0D5C46 !important;
  border: 1px solid #A7F3D0 !important;
  font-weight: 650 !important;
  font-size: 0.78rem !important;
  border-radius: 999px !important;
}
[class*="st-key-ehr_src_"] button p,
[class*="st-key-ehr_src_"] button span {
  color: #0D5C46 !important;
}

/* Legacy cha-metric aliases (redirected to Apple Health tiles) */
.cha-metric { color: #0F172A !important; }

/* Command bar + live sync pulse */
.amb-command-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 16px;
  background: #FFFFFF;
  border: 1px solid #E4E4E0;
  border-radius: 14px;
  box-shadow: var(--amb-shadow);
  margin-bottom: 12px;
}
.amb-live-sync {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.78rem;
  font-weight: 600;
  color: #0D5C46;
  letter-spacing: 0.01em;
}
.amb-live-dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  background: #10B981;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.55);
  animation: amb-pulse 1.8s infinite;
}
@keyframes amb-pulse {
  0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.55); }
  70% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
  100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}
.patient-hero {
  border-radius: 14px !important;
  border: 1px solid #E4E4E0 !important;
  background: #FFFFFF !important;
  box-shadow: var(--amb-shadow) !important;
  padding: 4px 2px !important;
}
.patient-hero.critical { border-left: 4px solid #E11D48 !important; }
.patient-hero.stable { border-left: 4px solid #10B981 !important; }
.patient-hero-name {
  font-size: 1.45rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #0F172A;
  margin: 0;
  line-height: 1.2;
}
.room-pill, .chip-pill {
  display: inline-flex;
  align-items: center;
  font-family: var(--amb-mono) !important;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid #E4E4E0;
  background: #F1F0EC;
  color: #0F172A;
  margin-right: 6px;
}
.chip-pill.allergy {
  background: #FFF1F2;
  border-color: #FECDD3;
  color: #BE123C;
}
.chip-pill.code {
  background: #ECFDF5;
  border-color: #A7F3D0;
  color: #047857;
}
.bento-zone-title {
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #475569;
  margin: 0 0 8px 0;
}
.st-key-checklist_bento [data-testid="stHorizontalBlock"] {
  background: #FAF9F6 !important;
  border: 1px solid #E4E4E0 !important;
  border-radius: 10px !important;
  padding: 10px 12px !important;
  margin-bottom: 8px !important;
}
.st-key-night_workspace [data-testid="stVerticalBlockBorderWrapper"],
.st-key-night_banner {
  background: #111827 !important;
  border: 1px solid #1E293B !important;
  color: #F8FAFC !important;
}
.st-key-night_banner .bento-zone-title,
.st-key-night_workspace .bento-zone-title {
  color: #E2E8F0 !important;
}
/* Night synthesis — pearl text on navy (override global dark p rule) */
.night-synthesis-card,
.night-synthesis-card p,
.night-synthesis-card div,
.night-synthesis-card span,
.st-key-night_banner .synth-one-liner,
.st-key-night_banner .synth-block-label,
.st-key-night_banner .synth-running,
.st-key-night_banner .synth-running li {
  color: #F8FAFC !important;
}
.st-key-night_banner .synth-one-liner {
  font-size: 0.92rem !important;
  line-height: 1.55 !important;
  font-weight: 400 !important;
}
.st-key-night_banner .synth-running {
  background-color: #1E293B !important;
  border: 1px solid #334155 !important;
  color: #F1F5F9 !important;
  border-radius: 10px !important;
  padding: 12px 14px !important;
}
.st-key-night_banner .synth-escalate {
  background-color: #4C0519 !important;
  border: 1px solid #F43F5E !important;
  color: #FFE4E6 !important;
}
.st-key-night_banner .synth-escalate.green {
  background-color: #064E3B !important;
  border: 1px solid #10B981 !important;
  color: #ECFDF5 !important;
}
/* Checklist header stays high-contrast on light card (even in Night mode) */
.st-key-checklist_bento .bento-zone-title {
  color: #334155 !important;
  font-weight: 700 !important;
}
[class*="st-key-open_pathway_"] button,
[class*="st-key-open_pathway_"] [data-testid="stBaseButton-secondary"] {
  background: #ECFDF5 !important;
  color: #0D5C46 !important;
  border: 1px solid #A7F3D0 !important;
  font-weight: 650 !important;
  border-radius: 999px !important;
}
[class*="st-key-open_pathway_"] button:hover {
  background: #D1FAE5 !important;
  border-color: #0D5C46 !important;
}
[data-testid="stBaseButton-primary"] {
  background: #0D5C46 !important;
  border-color: #0D5C46 !important;
  color: #FFFFFF !important;
}
[data-testid="stBaseButton-primary"]:hover {
  background: #064E3B !important;
  border-color: #064E3B !important;
}

/* Citation pills — soft sky bg + dark blue text */
[class*="st-key-cite_"] button,
[class*="st-key-cite_"] [data-testid="stPopoverButton"] {
  background-color: #e0f2fe !important;
  color: #0369a1 !important;
  border: 1px solid #7dd3fc !important;
  font-weight: 600 !important;
}
[class*="st-key-cite_"] button p,
[class*="st-key-cite_"] button span {
  color: #0369a1 !important;
}

/* Disable overflow clipping / fade masks on Day-Night radio & segmented toggle */
div[data-testid="stRadio"],
div[data-testid="stRadio"] > div,
div[data-testid="stRadio"] > div[role="radiogroup"],
.st-key-shift_view,
.st-key-shift_view > div,
.st-key-shift_view [data-testid="stSegmentedControl"],
.st-key-shift_view [data-testid="stSegmentedControl"] > div,
.st-key-shift_view [data-baseweb="button-group"],
.st-key-shift_view div[role="radiogroup"] {
  overflow: visible !important;
  mask-image: none !important;
  -webkit-mask-image: none !important;
}
div[data-testid="stRadio"]::before,
div[data-testid="stRadio"]::after,
div[data-testid="stRadio"] > div::before,
div[data-testid="stRadio"] > div::after,
div[data-testid="stRadio"] > div[role="radiogroup"]::before,
div[data-testid="stRadio"] > div[role="radiogroup"]::after,
.st-key-shift_view::before,
.st-key-shift_view::after,
.st-key-shift_view [data-testid="stSegmentedControl"]::before,
.st-key-shift_view [data-testid="stSegmentedControl"]::after,
.st-key-shift_view [data-testid="stSegmentedControl"] > div::before,
.st-key-shift_view [data-testid="stSegmentedControl"] > div::after,
.st-key-shift_view [data-baseweb="button-group"]::before,
.st-key-shift_view [data-baseweb="button-group"]::after {
  display: none !important;
  content: none !important;
  background: none !important;
}

/* Day / Night track — grow to fully enclose both option pills */
div[data-testid="stRadio"],
div[data-testid="stRadio"] > div,
.st-key-shift_view,
.st-key-shift_view > div,
.st-key-shift_view [data-testid="stSegmentedControl"],
.st-key-shift_view [data-testid="stSegmentedControl"] > div {
  width: auto !important;
  max-width: none !important;
  overflow: visible !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"],
.st-key-shift_view div[role="radiogroup"],
.st-key-shift_view [data-testid="stSegmentedControl"],
.st-key-shift_view [data-baseweb="button-group"] {
  background-color: #EEF2F6 !important;
  padding: 5px 8px !important;
  border-radius: 999px !important;
  border: 1px solid #CBD5E1 !important;
  display: inline-flex !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  gap: 6px !important;
  width: max-content !important;
  min-width: max-content !important;
  max-width: none !important;
  box-sizing: border-box !important;
  overflow: visible !important;
  mask-image: none !important;
  -webkit-mask-image: none !important;
}
.st-key-shift_view div[role="radiogroup"] > label > div:first-child,
.st-key-shift_view input[type="radio"] {
  width: 0px !important;
  height: 0px !important;
  overflow: hidden !important;
  opacity: 0 !important;
  margin: 0px !important;
  padding: 0px !important;
  position: absolute !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label,
.st-key-shift_view div[role="radiogroup"] > label,
.st-key-shift_view [data-testid="stSegmentedControl"] label,
.st-key-shift_view [data-baseweb="button-group"] > button,
.st-key-shift_view button {
  flex: 0 0 auto !important;
  width: max-content !important;
  background-color: transparent !important;
  border: 1.5px solid transparent !important;
  border-radius: 999px !important;
  padding: 6px 16px !important;
  margin: 0px !important;
  color: #64748B !important;
  font-weight: 500 !important;
  transition: all 0.15s ease !important;
  cursor: pointer !important;
  box-shadow: none !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-sizing: border-box !important;
  white-space: nowrap !important;
}
.st-key-shift_view div[role="radiogroup"] > label p,
.st-key-shift_view div[role="radiogroup"] > label span,
.st-key-shift_view button p,
.st-key-shift_view button span {
  margin-bottom: 0 !important;
  color: #64748B !important;
  font-weight: 500 !important;
  white-space: nowrap !important;
}

/* Pathway critical-action hover pills */
.crit-action-pill {
  position: relative;
  display: inline-block;
  margin-left: 6px;
  padding: 1px 7px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  cursor: help;
  vertical-align: middle;
  white-space: nowrap;
}
.crit-action-pill.red {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #dc2626;
}
.crit-action-pill.amber {
  background: #fffbeb;
  color: #b45309;
  border: 1px solid #d97706;
}
.crit-action-pill.green {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #059669;
}
.crit-action-pill .crit-tip {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  z-index: 1000;
  left: 0;
  bottom: calc(100% + 8px);
  width: 280px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #0f172a;
  color: #f8fafc;
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1.35;
  box-shadow: 0 8px 24px rgba(0,0,0,0.35);
  transition: opacity 0.15s ease, visibility 0.15s ease;
  white-space: normal;
  pointer-events: none;
}
.crit-action-pill:hover .crit-tip {
  visibility: visible;
  opacity: 1;
}
.pw-val-red { color: #b91c1c !important; font-weight: 700; }
.pw-val-amber { color: #b45309 !important; font-weight: 700; }
.pw-val-green { color: #047857 !important; font-weight: 700; }

/* Protocol comparison / table headers — light readable bar */
.protocol-scroll-box {
  max-height: 60vh;
  overflow-y: auto;
  position: relative;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
}
.protocol-scroll-box thead th {
  position: sticky;
  top: 0;
  z-index: 50;
  background-color: #F1F0EC !important;
  color: #0F172A !important;
  border-bottom: 1px solid #E4E4E0 !important;
  padding: 10px 12px !important;
  font-weight: 700 !important;
}
.protocol-scroll-box tbody td {
  background: #ffffff;
  color: #0F172A !important;
  padding: 8px 12px;
  border-bottom: 1px solid #E4E4E0 !important;
  font-family: var(--amb-mono) !important;
  font-size: 0.8rem !important;
}
.protocol-scroll-box tbody tr.row-red td { background: #FFF1F2; }
.protocol-scroll-box tbody tr.row-amber td { background: #FFFBEB; }
.protocol-scroll-box tbody tr.row-green td { background: #ECFDF5; }

/* Branching decision-tree flowchart — light theme, high contrast */
.ftree {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0;
  padding: 8px 4px 4px;
  font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
  color: #0f172a;
}
.ftree-title {
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: #334155;
  margin: 0 0 10px;
  text-align: center;
}
.fnode {
  position: relative;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 0.78rem;
  line-height: 1.35;
  text-align: center;
}
.fnode.root {
  opacity: 1 !important;
  filter: none !important;
  border: 1.5px solid #94a3b8;
  background: #f8fafc;
  color: #0f172a !important;
  font-weight: 650;
  box-shadow: none;
}
/* Unselected paths the patient did NOT go down */
.branch-watermarked,
.fnode.branch-watermarked,
.fbranch.branch-watermarked .fnode,
.fbranch.branch-watermarked .fbranch-label {
  opacity: 0.70 !important;
  filter: grayscale(65%) !important;
  position: relative !important;
  transition: all 0.2s ease-in-out !important;
  box-shadow: none !important;
}
.branch-watermarked,
.fnode.branch-watermarked,
.fbranch.branch-watermarked .fnode {
  background: repeating-linear-gradient(
    -45deg,
    #F8FAFC,
    #F8FAFC 10px,
    #F1F5F9 10px,
    #F1F5F9 20px
  ) !important;
  border: 1px dashed #CBD5E1 !important;
  color: #334155 !important;
  opacity: 0.70 !important;
}
.branch-watermarked:hover,
.fnode.branch-watermarked:hover,
.fbranch.branch-watermarked:hover .fnode,
.fbranch.branch-watermarked:hover .fbranch-label,
.fbranch.branch-watermarked:hover .farrow {
  opacity: 0.95 !important;
  filter: grayscale(0%) !important;
}
.farrow.farrow-watermarked,
.fbranch.branch-watermarked .farrow {
  opacity: 0.70 !important;
  color: #64748b !important;
  filter: grayscale(65%) !important;
}
/* Overflow / line-height safeguard — never clip multi-line badges */
.branch-taken,
.branch-watermarked,
.fnode.branch-taken,
.fnode.branch-watermarked,
.fbranch.branch-taken .fnode,
.fbranch.branch-watermarked .fnode,
.fcmp,
.fcmp-req,
.fcmp-act,
.protocol-scroll-box tbody td {
  height: auto !important;
  min-height: fit-content !important;
  line-height: 1.45 !important;
  overflow-wrap: break-word !important;
  overflow: visible !important;
}

/* Patient's actual taken path — full clinical contrast */
.branch-taken,
.fnode.branch-taken {
  opacity: 1.0 !important;
  filter: none !important;
  color: #0F172A !important;
  font-weight: 700;
  box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.08) !important;
}
.fnode.branch-taken.red,
.fbranch.branch-taken.red .fnode {
  border: 2px solid #BE123C !important;
  background: #FFF1F2 !important;
  color: #0F172A !important;
}
.fnode.branch-taken.amber,
.fnode.branch-taken.watch,
.fbranch.branch-taken.amber .fnode,
.fbranch.branch-taken.watch .fnode {
  border: 2px solid #D97706 !important;
  background: #FFFBEB !important;
  color: #0F172A !important;
}
.fnode.branch-taken.green,
.fbranch.branch-taken.green .fnode {
  border: 2px solid #047857 !important;
  background: #ECFDF5 !important;
  color: #0F172A !important;
}
.fnode.branch-taken strong { color: #0f172a !important; }
.fnode.diamond {
  clip-path: none;
  border-radius: 12px;
  border-style: solid;
  transform: none;
}
.fnode.diamond::before {
  content: "◆ ";
  color: #0369a1;
  font-weight: 700;
}
.farrow {
  display: flex;
  justify-content: center;
  align-items: center;
  color: #475569;
  font-size: 1.05rem;
  line-height: 1;
  padding: 4px 0;
  user-select: none;
}
.farrow.farrow-taken.red,
.fbranch.branch-taken.red .farrow { color: #dc2626 !important; font-weight: 700; opacity: 1 !important; filter: none !important; }
.farrow.farrow-taken.amber,
.farrow.farrow-taken.watch,
.fbranch.branch-taken.amber .farrow,
.fbranch.branch-taken.watch .farrow { color: #d97706 !important; font-weight: 700; opacity: 1 !important; filter: none !important; }
.farrow.farrow-taken.green,
.fbranch.branch-taken.green .farrow { color: #059669 !important; font-weight: 700; opacity: 1 !important; filter: none !important; }
.fbranches {
  display: grid;
  gap: 8px;
  margin-top: 2px;
}
.fbranches.cols-2 { grid-template-columns: 1fr 1fr; }
.fbranches.cols-3 { grid-template-columns: 1fr 1fr 1fr; }
.fbranches.cols-4 { grid-template-columns: 1fr 1fr 1fr 1fr; }
.fbranch {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.fbranch-label {
  text-align: center;
  font-size: 0.68rem;
  color: #475569 !important;
  margin-bottom: 4px;
  font-weight: 600;
}
.fbranch.branch-taken.red .fbranch-label { color: #b91c1c !important; font-weight: 700; opacity: 1 !important; filter: none !important; }
.fbranch.branch-taken.amber .fbranch-label,
.fbranch.branch-taken.watch .fbranch-label { color: #b45309 !important; font-weight: 700; opacity: 1 !important; filter: none !important; }
.fbranch.branch-taken.green .fbranch-label { color: #047857 !important; font-weight: 700; opacity: 1 !important; filter: none !important; }
.ford-delta {
  margin-top: 8px;
  text-align: left;
  font-size: 0.72rem;
  line-height: 1.35;
  border-top: 1px dashed #cbd5e1;
  padding-top: 6px;
}
.ford-cur { color: #334155 !important; margin-bottom: 4px; }
.ford-chg { color: #0f172a !important; font-weight: 650; }
.ford-cur strong, .ford-chg strong { color: #0f172a !important; }
.frail {
  height: 1px;
  background: linear-gradient(90deg, transparent, #cbd5e1, transparent);
  margin: 6px 8% 2px;
}
.fchain {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0;
}
@media (max-width: 900px) {
  .fbranches.cols-4 { grid-template-columns: 1fr 1fr; }
  .fbranches.cols-3 { grid-template-columns: 1fr; }
  .fcmp-grid { grid-template-columns: 1fr; }
}
/* Side-by-side AHA requirement vs patient-positive criteria */
.fcmp {
  margin: 8px 0 4px;
  border: 1.5px solid #94a3b8;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
  text-align: left;
}
.fcmp-head {
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: #F1F0EC;
  color: #0F172A !important;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  border-bottom: 1px solid #E4E4E0;
}
.fcmp-head > div { padding: 8px 10px; }
.fcmp-head > div:last-child { border-left: 1px solid #E4E4E0; }
.fcmp-grid { display: grid; grid-template-columns: 1fr 1fr; }
.fcmp-row {
  display: contents;
}
.fcmp-row > div {
  padding: 7px 10px;
  font-size: 0.78rem;
  line-height: 1.35;
  color: #0f172a !important;
  border-top: 1px solid #e2e8f0;
  vertical-align: top;
}
.fcmp-row > div:last-child { border-left: 1px solid #e2e8f0; }
.fcmp-row.gate > div { background: #fef2f2; font-weight: 650; }
.fcmp-row.met > div:last-child { background: #ecfdf5; }
.fcmp-req { color: #334155 !important; }
.fcmp-act { color: #0f172a !important; font-weight: 650; }
.fcmp-summary {
  padding: 8px 10px;
  background: #fef2f2;
  border-top: 1px solid #fca5a5;
  color: #b91c1c !important;
  font-size: 0.8rem;
  font-weight: 750;
}
.fcmp-grid > .fcmp-req,
.fcmp-grid > .fcmp-act {
  padding: 8px 10px;
  font-size: 0.76rem;
  line-height: 1.4;
  color: #0f172a !important;
  text-align: left;
  vertical-align: top;
}
.fcmp-grid > .fcmp-act {
  border-left: 1px solid #e2e8f0;
  background: #f8fafc;
}
.fcmp h4 {
  margin: 0 0 6px 0;
  font-size: 0.78rem;
  font-weight: 800;
  color: #0f172a !important;
}
.fcmp ol, .fcmp ul {
  margin: 4px 0 0 1.15rem;
  padding: 0;
  color: #0f172a !important;
}
.fcmp li { margin: 3px 0; color: #0f172a !important; }
.fcmp-badge-red {
  color: #b91c1c !important;
  font-weight: 800;
}
.fcmp-badge-green {
  color: #047857 !important;
  font-weight: 800;
}
.fcmp-badge-amber {
  color: #b45309 !important;
  font-weight: 800;
}
.fnode:has(.fcmp) {
  text-align: left !important;
  padding: 10px 10px 12px;
}
.fnode .fcmp { margin-top: 6px; }

/* KD diagnostic rule + principal-criteria side-by-side */
.kd-rule-box {
  background: #f8fafc;
  border: 1.5px solid #94a3b8;
  border-radius: 10px;
  padding: 12px 14px;
  margin: 8px 0 12px;
  color: #0f172a;
  height: auto !important;
  line-height: 1.45 !important;
  overflow-wrap: break-word !important;
}
.kd-rule-text {
  font-size: 0.86rem;
  font-weight: 650;
  color: #0f172a !important;
  line-height: 1.45 !important;
  margin-bottom: 8px;
}
.kd-rule-foot {
  font-size: 0.78rem;
  color: #334155 !important;
  line-height: 1.45 !important;
  font-style: italic;
  margin-bottom: 10px;
  padding-top: 6px;
  border-top: 1px dashed #cbd5e1;
}
.kd-rule-leo {
  font-size: 0.84rem;
  font-weight: 750;
  color: #b91c1c !important;
  background: #fef2f2;
  border: 1px solid #fca5a5;
  border-radius: 8px;
  padding: 8px 10px;
  line-height: 1.45 !important;
}
.kd-crit-grid {
  border: 1.5px solid #94a3b8;
  border-radius: 10px;
  overflow: hidden;
  background: #ffffff;
  margin: 8px 0 12px;
}
.kd-crit-head {
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: #0f172a;
  color: #f8fafc !important;
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.kd-crit-head > div { padding: 10px 12px; }
.kd-crit-head > div:last-child { border-left: 1px solid #334155; }
.kd-crit-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-top: 1px solid #e2e8f0;
  height: auto !important;
  min-height: fit-content !important;
}
.kd-crit-row > div {
  padding: 10px 12px;
  font-size: 0.82rem;
  line-height: 1.45 !important;
  color: #0f172a !important;
  height: auto !important;
  overflow-wrap: break-word !important;
  word-wrap: break-word;
}
.kd-crit-row > div:last-child {
  border-left: 1px solid #e2e8f0;
  background: #f8fafc;
  font-weight: 650;
}
@media (max-width: 700px) {
  .kd-crit-head, .kd-crit-row { grid-template-columns: 1fr; }
  .kd-crit-head > div:last-child,
  .kd-crit-row > div:last-child { border-left: none; border-top: 1px solid #e2e8f0; }
}

/* Checklist labels — never truncate with ellipsis */
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] label p,
[data-testid="stCheckbox"] div[data-testid="stMarkdownContainer"] p {
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: unset !important;
  word-break: break-word !important;
  line-height: 1.4 !important;
  font-size: 0.88rem !important;
  color: #0F172A !important;
}
.st-key-checklist_bento [data-testid="stCheckbox"] {
  align-items: flex-start !important;
}


/* Census critical alert pills — crimson (Maya ready stays green) */
.roster-flag-crit {
  display: inline-block;
  color: #BE123C !important;
  background: #FFE4E6 !important;
  padding: 1px 5px !important;
  border-radius: 4px !important;
  font-weight: 700 !important;
  font-family: var(--amb-mono) !important;
  font-size: 0.68rem !important;
  margin-left: 4px;
}
.roster-flag-ready {
  display: inline-block;
  color: #047857 !important;
  background: #ECFDF5 !important;
  padding: 1px 5px !important;
  border-radius: 4px !important;
  font-weight: 700 !important;
  font-size: 0.68rem !important;
  margin-left: 4px;
}

/* Unified patient header — single card, no nested box */
div[class*="st-key-patient_hero_"] [data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stVerticalBlockBorderWrapper"]:has(
  [class*="st-key-patient_hero_"]
) {
  border-left: 4px solid #E11D48 !important;
  padding: 12px 16px !important;
}
div[class*="st-key-patient_hero_maya"] [data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stVerticalBlockBorderWrapper"]:has(
  [class*="st-key-patient_hero_maya"]
) {
  border-left-color: #10B981 !important;
}
.patient-banner-head {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  flex-wrap: wrap !important;
  margin: 0 !important;
}
.patient-banner-name {
  font-family: 'Inter', sans-serif !important;
  font-size: 1.35rem !important;
  font-weight: 700 !important;
  color: #0F172A !important;
  line-height: 1.2 !important;
  margin: 0 !important;
}
.banner-pill {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.70rem !important;
  font-weight: 600 !important;
  color: #475569 !important;
  background: #E2E8F0 !important;
  padding: 2px 7px !important;
  border-radius: 999px !important;
  display: inline-block !important;
  white-space: nowrap !important;
}
.banner-pill.allergy-warn {
  color: #BE123C !important;
  background: #FFE4E6 !important;
}
.patient-banner-meta {
  font-family: 'Inter', sans-serif !important;
  font-size: 0.80rem !important;
  font-weight: 500 !important;
  color: #475569 !important;
  line-height: 1.35 !important;
  margin-top: 4px !important;
}
.patient-banner-meta strong {
  color: #0F172A !important;
  font-weight: 600 !important;
}
div[class*="st-key-patient_hero_"] > div[data-testid="stVerticalBlock"] {
  gap: 0.35rem !important;
}
.synth-one-liner {
  font-size: 0.92rem;
  line-height: 1.45;
  color: #0F172A;
  margin: 0 0 10px 0;
}
.synth-running {
  margin: 0 0 12px 0;
  padding: 10px 12px;
  background: #F8FAFC;
  border: 1px solid #E4E4E0;
  border-radius: 10px;
}
.synth-running li {
  font-family: var(--amb-mono) !important;
  font-size: 0.78rem;
  line-height: 1.55;
  color: #0F172A;
}
.synth-escalate {
  margin: 0 0 12px 0;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #FECDD3;
  background: #FFF1F2;
  color: #BE123C;
  font-size: 0.84rem;
  line-height: 1.4;
  font-weight: 650;
}
.synth-escalate.green {
  border-color: #A7F3D0;
  background: #ECFDF5;
  color: #047857;
}
.census-card-identity {
  padding: 0;
  text-align: left;
  position: relative;
  z-index: 1;
  pointer-events: none;
}
.census-card-name .pill-room {
  margin-right: 6px;
}
.synth-block-label {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #64748B;
  margin: 0 0 6px 0;
}
</style>
"""
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ATTENDING = "Dr. Patel (Peds Floor Attending)"
ACUITY_RED = "#BE123C"
ACUITY_AMBER = "#B45309"
ACUITY_GREEN = "#047857"
ACUITY_COLORS = {
    "red": ACUITY_RED,
    "amber": ACUITY_AMBER,
    "green": ACUITY_GREEN,
}

DAY = "☀️ Day Attending"
NIGHT = "🌙 Night Attending"

MTX_CUTOFFS = {24: 10.0, 48: 1.0, 72: 0.1}

# ---------------------------------------------------------------------------
# Four clinical archetypes (room-sorted census)
# ---------------------------------------------------------------------------
PATIENTS: list[dict] = [
    {
        "id": "emma",
        "name": "Emma Rodriguez",
        "age": "8y",
        "sex": "F",
        "mrn": "Peds-ONC-4821",
        "room": "4B-10",
        "archetype": "mtx",
        "archetype_label": "Protocol / threshold logic",
        "diagnosis": "High-risk B-ALL · Interim Maintenance I",
        "protocol": "COG AALL1131 (High-Risk B-ALL 5 g/m² HD-MTX)",
        "pathway_short": "COG AALL1131 5 g/m² HD-MTX",
        "day": "Interim Maintenance I · Hour 48",
        "bsa": 0.98,
        "wt": 26.0,
        "hour": 48,
        "mtx": 4.20,
        "mtx_cutoff_h48": 0.40,
        "cr": 0.68,
        "cr_base": 0.40,
        "urine_ph": 6.8,
        "flags": ["!MTX", "!Cr"],
        "critical": True,
        "badge": None,
        "access": "Right chest port",
        "status": (
            "Hour 48 critical gate — MTX 4.20 (10.5× cutoff), AKI +70%, "
            "acidic urine pH 6.8"
        ),
        "labs": dict(
            wbc=0.8, anc=120, hgb=7.6, plt=18, na=138, cr=0.68, k=4.1, phos=4.2, ua=2.1
        ),
        "banner_line": (
            "High-Risk B-ALL · COG AALL1131 (HD-MTX 5 g/m²) · "
            "Hour 48 Post-Infusion"
        ),
        "citations": {
            "bmp": {
                "label": "📊 Renal & BMP",
                "title": "BMP · 04:15",
                "body": (
                    "Source: Epic Lab · Drawn 04:15\n"
                    "Cr 0.68 mg/dL (baseline 0.40, +70%)\n"
                    "K 4.1 · Phos 4.2 · UA 2.1 · Na 138"
                ),
                "note": "Source: Epic Lab · Drawn 04:15",
            },
            "mtx": {
                "label": "🧪 MTX Nomogram",
                "title": "MTX level · Hour 48",
                "body": (
                    "Source: Epic Lab · Hour 48 MTX\n"
                    "Result: 4.20 µmol/L (cutoff ≤ 0.40)\n"
                    "Hour 42: 5.2 · Hour 36: 8.4 · Hour 24: 118.0"
                ),
                "note": "Source: Epic Lab · Hour 48 MTX series",
            },
            "vitals": {
                "label": "📈 pH & BP Curve",
                "title": "Vitals · 06:00",
                "body": (
                    "HR 92 · BP 98/58 · RR 18 · SpO₂ 99% RA · T 36.9°C\n"
                    "Urine pH 6.8 (qVoid flowsheet)"
                ),
            },
            "exam": {
                "label": "📋 Protocol Info",
                "title": "Attending exam · 07:30",
                "body": (
                    "Alert, mild mucositis, port site clean, "
                    "lungs clear, UOP 1.8 mL/kg/hr"
                ),
            },
        },
        "narrative_full": (
            "Emma Rodriguez is an 8y F (26.0 kg, BSA 0.98 m²) with high-risk "
            "B-ALL on Interim Maintenance I receiving COG AALL1131 5 g/m² "
            "HD-MTX (24h infusion). Hour 48 MTX is :red[**4.20 µmol/L**] "
            "(cutoff ≤ 0.40; 10.5×) — :red[**!MTX**]. Creatinine rose from "
            "0.40 → 0.68 mg/dL (+70%) — :red[**!Cr**] Stage 1 AKI. Urine pH "
            "6.8 is acidic (precipitation risk). Active path: Leucovorin "
            "100 mg/m² (98 mg) IV q6h, hyperhydration 200 mL/m²/hr "
            "(196 mL/hr), STAT NaHCO₃ 26 mEq, glucarpidase borderline watch."
        ),
        "narrative_delta": "",
        "day_tasks": [
            (
                "d1",
                "Hour 48 :red[MTX] 4.20 vs ≤0.40 — escalate Leucovorin to "
                "100 mg/m² (98 mg) IV q6h until MTX < 0.10.",
                "mtx",
            ),
            (
                "d2",
                "Escalate hydration to 200 mL/m²/hr (196 mL/hr) for :red[CMP/Cr] "
                "AKI (+70% · 0.68 vs 0.40).",
                "bmp",
            ),
            (
                "d3",
                "STAT NaHCO₃ 1 mEq/kg (26 mEq) for acidic :red[urine pH] 6.8; "
                "raise bag to 60 mEq/L; recheck pH in 1h.",
                "vitals",
            ),
            (
                "d4",
                "Glucarpidase borderline watch (Hour 42 MTX 5.2; Cr +70%) — "
                "evaluate 50 U/kg = 1,300 Units.",
                "mtx",
            ),
            (
                "d5",
                "Hold nephrotoxins / OAT1–OAT3 meds until MTX < 0.10 µmol/L.",
                "mtx",
            ),
            (
                "d6",
                "Family update on delayed clearance; no overnight discharge.",
                "exam",
            ),
        ],
        "night_tasks": [
            (
                "n1",
                "Hour 54 STAT :red[MTX] + BMP; continue q6h levels to < 0.10.",
                "mtx",
            ),
            (
                "n2",
                "qVoid :red[urine pH] ≥ 7.0; 1h recheck after NaHCO₃ 26 mEq.",
                "vitals",
            ),
            (
                "n3",
                "Strict q4h I&Os / weights on 196 mL/hr; furosemide if > +2 kg.",
                "vitals",
            ),
            (
                "n4",
                "Call if MTX plateaus, oliguria, or Cr rises further — "
                "glucarpidase screen.",
                "exam",
            ),
        ],
        "stage_order": {
            "title": "Hour 48 triple rescue — LV + hyperhydration + NaHCO₃",
            "orders": [
                "Leucovorin 100 mg/m² = 98 mg IV q6h until MTX < 0.10 µmol/L",
                "D5 0.2NS + 40→60 mEq/L NaHCO₃ at 200 mL/m²/hr = 196 mL/hr",
                "NaHCO₃ 26 mEq IV bolus over 1h ×1 (urine pH 6.8)",
                "q6h MTX + daily BMP through Hour 54 / 60 / 72 until clear",
            ],
            "cdi_code": "N17.9 + T45.1X5A",
            "cdi_label": (
                "N17.9 Acute Kidney Injury [CC] + T45.1X5A Adverse effect of "
                "antineoplastic therapy [MCC]"
            ),
            "cdi_note": (
                "Linked to Cr 0.68 mg/dL (+70% from 0.40 baseline) & "
                "Hour-48 MTX 4.20 µmol/L"
            ),
        },
    },
    {
        "id": "maya",
        "name": "Maya Patel",
        "age": "4y",
        "sex": "F",
        "mrn": "Peds-ID-2201",
        "room": "4B-12",
        "archetype": "pyelo",
        "archetype_label": "De-escalation & discharge readiness",
        "diagnosis": "Acute pyelonephritis",
        "protocol": "AAP/IDSA Pediatric Pyelonephritis IV-to-PO Switch Pathway",
        "pathway_short": "AAP/IDSA Pyelo IV→PO Switch",
        "day": "Hospital Day 3",
        "wt": 16.0,
        "flags": [],
        "critical": False,
        "badge": ":green[**Ready for PO Cephalexin**]",
        "access": "PIV right hand",
        "status": "30h afebrile; pansensitive E. coli; tolerating PO",
        "afebrile_hours": 30,
        "urine_cx": "E. coli pansensitive",
        "po_intake": "Good — full diet",
        "cr": 0.32,
        "cr_base": 0.30,
        "citations": {
            "cx": {
                "label": "📊 Urine Cx 22:10",
                "title": "Urine culture · finalized 22:10",
                "body": (
                    "E. coli — pansensitive\n"
                    "Ceftriaxone S · Cephalexin S · TMP-SMX S · Nitrofurantoin S"
                ),
            },
            "vitals": {
                "label": "📈 Vitals 06:00",
                "title": "Vitals · 06:00",
                "body": (
                    "Afebrile × 30h (last Tmax 38.4°C HD1)\n"
                    "HR 98 · BP 92/56 · SpO₂ 99% · comfortable"
                ),
            },
            "exam": {
                "label": "⚡ Stage PO Switch",
                "title": "Exam · 07:45",
                "body": (
                    "Non-toxic, eating breakfast, mild residual CVA "
                    "tenderness, PIV intact"
                ),
            },
            "bmp": {
                "label": "📊 Renal & WBC Recovery",
                "title": "BMP · 05:00",
                "body": "Cr 0.32 (baseline 0.30) · electrolytes normal",
                "note": "Near-baseline Cr · electrolytes within pediatric reference",
            },
        },
        "narrative_full": (
            "Maya Patel is a 4y F admitted for acute pyelonephritis. She has "
            "been :green[**afebrile for 30 hours**], urine culture grew "
            "pansensitive E. coli, and she is tolerating full PO intake. "
            "Cr stable at 0.32. She meets de-escalation criteria for "
            ":green[**PO cephalexin**] with anticipated same-day discharge "
            "if family teaching and Rx completed."
        ),
        "narrative_delta": (
            "⚡ **Delta since 07:00**\n\n"
            "- <span class='delta-good'>Still afebrile (30h timer)</span>\n"
            "- <span class='delta-good'>Ate 100% breakfast; no emesis</span>\n"
            "- <span class='delta-new'>Pharmacy verified cephalexin suspension "
            "coverage</span>"
        ),
        "day_tasks": [
            (
                "d1",
                "Confirm 30h afebrile timer & clinical stability for PO switch.",
                "vitals",
            ),
            (
                "d2",
                "Review pansensitive E. coli susceptibilities → stage PO cephalexin.",
                "cx",
            ),
            (
                "d3",
                "Verify PO intake / no vomiting; Cr near baseline (0.32).",
                "bmp",
            ),
            (
                "d4",
                "Discharge barriers: Rx filled, family teaching, PCP follow-up.",
                "exam",
            ),
            (
                "d5",
                "Discontinue PIV after first PO dose tolerated.",
                "exam",
            ),
            (
                "d6",
                "Update family on home antibiotic course (7–10 days total).",
                "exam",
            ),
        ],
        "night_tasks": [
            (
                "n1",
                "If fever returns ≥38.0°C → hold discharge; notify day team.",
                "vitals",
            ),
            (
                "n2",
                "Ensure first PO cephalexin dose given before overnight if staged.",
                "cx",
            ),
            (
                "n3",
                "Pain control / PO fluids; call if emesis after PO antibiotic.",
                "exam",
            ),
            (
                "n4",
                "No routine overnight labs unless clinical change.",
                "bmp",
            ),
        ],
        "stage_order": {
            "title": "Switch IV Ceftriaxone → PO Cephalexin",
            "orders": [
                "Discontinue IV Ceftriaxone",
                "Cephalexin 25 mg/kg/dose PO TID "
                f"(= {round(25 * 16)} mg PO TID) × complete 10-day course",
                "Pharmacy to verify suspension & discharge Rx",
                "DC PIV after first PO dose tolerated",
            ],
            "cdi_code": "N10",
            "cdi_label": (
                "N10 Acute Tubulo-Interstitial Nephritis / Pyelonephritis "
                "(E. coli)"
            ),
            "cdi_note": (
                "Documented 30h afebrile IV-to-PO transition readiness"
            ),
        },
    },
    {
        "id": "chloe",
        "name": "Chloe Miller",
        "age": "15y",
        "sex": "F",
        "mrn": "Peds-ADOL-8840",
        "room": "4B-14",
        "archetype": "refeeding",
        "archetype_label": "Cross-parameter safety logic",
        "diagnosis": "Severe restrictive anorexia nervosa",
        "protocol": "Junior MARSIPAN / SAHM Refeeding Syndrome Pathway",
        "pathway_short": "Junior MARSIPAN / SAHM Refeeding",
        "day": "Refeeding Day 3 · 1,600 kcal",
        "wt": 38.0,
        "flags": ["!HR", "!Phos"],
        "critical": True,
        "badge": None,
        "access": "PIV",
        "status": "Refeeding syndrome warning — bradycardia + falling Phos",
        "hr_nadir": 38,
        "phos": 1.9,
        "k": 3.2,
        "mg": 1.5,
        "orthostatic": True,
        "kcal": 1600,
        "citations": {
            "vitals": {
                "label": "📈 Vitals 02:15",
                "title": "Overnight vitals · HR nadir",
                "body": (
                    "HR nadir 38 bpm at 02:15 (telemetry)\n"
                    "Orthostatics AM: +28 HR / −22 systolic — positive"
                ),
            },
            "bmp": {
                "label": "🧪 Refeeding Electrolytes",
                "title": "Chem · 05:30",
                "body": (
                    "Phos 1.9 mg/dL (was 2.6 yesterday) — critical low\n"
                    "K 3.2 · Mg 1.5 · Glucose 78"
                ),
                "note": (
                    "Refeeding electrolyte pattern: critical Phos with low K/Mg"
                ),
            },
            "exam": {
                "label": "🫀 Orthostatics & ECG",
                "title": "Exam · 07:20",
                "body": (
                    "Orthostatics AM: +28 HR / −22 systolic — positive\n"
                    "Cachectic, cool extremities, supervised meals, "
                    "sitters present, no SI overnight"
                ),
            },
            "intake": {
                "label": "⚡ Stage Telemetry & Phos",
                "title": "Caloric stage · Day 3",
                "body": "Target 1,600 kcal · 92% completed overnight + breakfast",
            },
        },
        "narrative_full": (
            "Chloe Miller is a 15y F with severe restrictive anorexia nervosa "
            "on Refeeding Day 3 (1,600 kcal). Overnight telemetry showed "
            "HR nadir :red[**!38 bpm**]. AM labs: Phos :red[**!1.9 mg/dL**] "
            "(down from 2.6), K 3.2, Mg 1.5; orthostatics positive. "
            "Cross-parameter pattern indicates emergent refeeding syndrome "
            "risk — hold kcal advance, replete Phos/K/Mg IV, continuous "
            "cardiorespiratory monitoring, notify adolescent medicine."
        ),
        "narrative_delta": (
            "⚡ **Delta since 07:00**\n\n"
            "- <span class='delta-crit'>HR nadir 38 bpm @ 02:15 (new)</span>\n"
            "- <span class='delta-crit'>Phos 1.9 down from 2.6 @ 05:30</span>\n"
            "- <span class='delta-crit'>Positive orthostatics AM</span>\n"
            "- <span class='delta-new'>Completed 92% of 1,600 kcal stage</span>"
        ),
        "day_tasks": [
            (
                "d1",
                "Emergent refeeding warning: address :red[HR] nadir 38 & "
                ":red[Phos] 1.9 — do not advance calories.",
                "vitals",
            ),
            (
                "d2",
                "Stage IV sodium phosphate repletion; recheck Phos/K/Mg in 4–6h.",
                "bmp",
            ),
            (
                "d3",
                "Continuous telemetry; orthostatic precautions; bedrest if symptomatic.",
                "vitals",
            ),
            (
                "d4",
                "Hold caloric advance at 1,600 kcal until Phos ≥ 2.5 & HR stable.",
                "intake",
            ),
            (
                "d5",
                "Adolescent medicine / nutrition co-management huddle today.",
                "exam",
            ),
            (
                "d6",
                "Family update on refeeding syndrome risk & monitoring plan.",
                "exam",
            ),
        ],
        "night_tasks": [
            (
                "n1",
                "If HR < 40 or symptomatic bradycardia → notify senior / consider ICU.",
                "vitals",
            ),
            (
                "n2",
                "04:00 Phos/K/Mg recheck after IV phosphate; call if Phos < 2.0.",
                "bmp",
            ),
            (
                "n3",
                "Supervised overnight snacks per protocol; no unsupervised bathroom.",
                "intake",
            ),
            (
                "n4",
                "Q2h neuro/cardiac checks while Phos critically low.",
                "exam",
            ),
        ],
        "stage_order": {
            "title": "IV sodium phosphate repletion + hold kcal advance",
            "orders": [
                "Sodium phosphate 0.16–0.32 mmol/kg IV over 4–6h "
                f"(≈ {round(0.25 * 38, 1)} mmol IV ×1 now)",
                "Recheck Phos / K / Mg 4h post-infusion",
                "KCl / MgSO₄ repletion per protocol if still low",
                "HOLD caloric advance — remain at 1,600 kcal",
                "Continuous telemetry; orthostatic precautions",
            ],
            "cdi_code": "E43 + E83.39",
            "cdi_label": (
                "E43 Unspecified Severe Protein-Calorie Malnutrition [MCC] + "
                "E83.39 Refeeding Hypophosphatemia [CC]"
            ),
            "cdi_note": (
                "Linked to Phos 1.9 mg/dL & HR nadir 38 bpm"
            ),
        },
    },
    {
        "id": "leo",
        "name": "Leo Kim",
        "age": "2y",
        "sex": "M",
        "mrn": "Peds-CARD-3310",
        "room": "4B-16",
        "archetype": "kawasaki",
        "archetype_label": "Time-window & diagnostic criteria",
        "diagnosis": (
            "Incomplete Kawasaki Disease (Day 6 Fever · 2/5 Clinical Signs · "
            "5/6 Supplemental Labs)"
        ),
        "protocol": "Evaluation of Suspected Kawasaki Disease",
        "pathway_short": "Evaluation of Suspected Kawasaki Disease",
        "day": "Fever Day 6 · Incomplete KD · Pre-IVIG",
        "wt": 13.0,
        "flags": ["!Fevers", "!CRP", "!Labs"],
        "critical": True,
        "badge": ":orange[**Incomplete KD**]",
        "access": "PIV",
        "status": (
            "Day 6 unexplained fever; 2/5 clinical criteria "
            "(conjunctivitis + rash); CRP 14.2 / ESR 78; "
            "5/6 supplemental labs → Incomplete KD; Echo pending; pre-IVIG"
        ),
        "fever_day": 6,
        "tmax": 39.4,
        "criteria_met": 2,
        "supp_labs_met": 5,
        "crp": 14.2,
        "esr": 78,
        "echo": "Pending — do not delay IVIG for echo",
        "hgb": 9.8,
        "albumin": 2.7,
        "alt": 68,
        "wbc": 17400,
        "plt": 390000,
        "ua_wbc": 24,
        "maint_ivf": 46,
        "criteria": [
            "Bilateral bulbar conjunctival injection — Present (Day 2)",
            "Polymorphous rash — Present (Day 3)",
            "Oral mucous membrane changes — Absent",
            "Peripheral extremity changes — Absent",
            "Cervical lymphadenopathy ≥1.5 cm — Absent (shotty <0.8 cm only)",
        ],
        "citations": {
            "vitals": {
                "label": "📈 Vitals 06:30",
                "title": "Vitals · 06:30",
                "body": "T 39.4°C · HR 142 · irritable · Day 6 unremitting fever",
            },
            "labs": {
                "label": "🧪 5/6 Suppl. Labs (+)",
                "title": "Inflammatory markers · 05:00",
                "body": (
                    "CRP 14.2 mg/dL · ESR 78 mm/h · WBC 17.4k · Hgb 9.8 · "
                    "Albumin 2.7 · ALT 68 · Plt 390k · UA 24 WBC/hpf"
                ),
                "note": (
                    "Incomplete KD lab pathway: CRP/ESR both above AHA cutoffs; "
                    "5/6 supplemental labs positive (Plt still normal on Day 6)."
                ),
            },
            "exam": {
                "label": "📋 2/5 KD Scorecard",
                "title": "KD criteria exam · 07:40",
                "body": (
                    "2/5 AHA principal features only: limbal-sparing "
                    "conjunctivitis (Day 2) + polymorphous truncal/groin rash "
                    "(Day 3). Absent: oral mucosal changes, extremity edema/"
                    "erythema, and ≥1.5 cm cervical adenopathy (shotty <0.8 cm). "
                    "Enters Incomplete KD CRP/ESR + supplemental lab algorithm."
                ),
            },
            "echo": {
                "label": "⚡ Stage IVIG + ASA",
                "title": "Echocardiogram",
                "body": (
                    "Baseline coronary echo ordered — do not delay IVIG waiting "
                    "for echo; Incomplete KD treatment triggered by ≥3 "
                    "supplemental labs"
                ),
            },
        },
        "narrative_full": (
            "Leo Kim is a 2y M (13.0 kg) with **incomplete Kawasaki disease** "
            "on fever Day 6 (Tmax 39.4°C). He meets **only 2/5** AHA principal "
            "clinical criteria (bilateral non-exudative conjunctivitis + "
            "polymorphous rash). Because clinical criteria are 2–3, the "
            "Incomplete KD algorithm applies: CRP 14.2 / ESR 78 both exceed "
            "cutoffs and **5/6 supplemental lab criteria** are positive → "
            "**Incomplete KD confirmed**. Echo is pending. He is **pre-IVIG** "
            "— stage weight-based IVIG 2 g/kg (**26 g**) plus high-dose "
            "aspirin 80–100 mg/kg/day (260 mg PO q6h) without delaying for echo."
        ),
        "narrative_delta": (
            "⚡ **Delta since 07:00**\n\n"
            "- <span class='delta-crit'>Tmax 39.4°C overnight (Day 6)</span>\n"
            "- <span class='delta-crit'>Only 2/5 clinical criteria "
            "(conjunctivitis + rash) — Incomplete KD pathway</span>\n"
            "- <span class='delta-new'>CRP 14.2 / ESR 78 + 5/6 supplemental "
            "labs → treat as Incomplete KD</span>\n"
            "- <span class='delta-new'>Echo ordered — still pending "
            "(do not delay IVIG)</span>"
        ),
        "day_tasks": [
            (
                "d1",
                "Confirm Incomplete KD scorecard: Day 6 fever + only 2/5 clinical "
                "signs (conjunctivitis + rash) → lab algorithm.",
                "exam",
            ),
            (
                "d2",
                "Stage IVIG 2 g/kg = 26 g IV ×1 + high-dose ASA 260 mg PO q6h "
                "(triggered by 5/6 supplemental labs).",
                "labs",
            ),
            (
                "d3",
                "Ensure echo completed / pending coronary assessment documented "
                "(do not delay IVIG for Incomplete KD).",
                "echo",
            ),
            (
                "d4",
                "ID / cardiology awareness; monitor for IVIG infusion reactions.",
                "exam",
            ),
            (
                "d5",
                "Fever curve q4h; set 36h post-IVIG refractory fever clock.",
                "vitals",
            ),
            (
                "d6",
                "Family counseling on Incomplete KD, IVIG/ASA, and follow-up echos.",
                "exam",
            ),
        ],
        "night_tasks": [
            (
                "n1",
                "If IVIG running: q1h vitals during infusion; pause for reaction.",
                "vitals",
            ),
            (
                "n2",
                "Document ongoing fever day count; call if hypotension / irritability ↑.",
                "vitals",
            ),
            (
                "n3",
                "ASA first dose given; watch for bleeding / GI upset.",
                "labs",
            ),
            (
                "n4",
                "Echo still pending overnight → hand off to AM cardiology slot.",
                "echo",
            ),
        ],
        "stage_order": {
            "title": "IVIG 26 g IV + High-Dose ASA + Echo",
            "orders": [
                "IVIG 2 g/kg = 26 g IV ×1 (infuse over 10–12h per pharmacy)",
                "Aspirin 80–100 mg/kg/day = 260 mg PO q6h (high-dose)",
                "Continuous pulse ox / q1h vitals during IVIG",
                "STAT baseline coronary echocardiogram "
                "(do not delay IVIG waiting for echo)",
                "Diphenhydramine / acetaminophen PRN infusion reaction",
            ],
            "cdi_code": "M30.3",
            "cdi_label": (
                "M30.3 Mucocutaneous Lymph Node Syndrome "
                "[Incomplete Kawasaki Disease - MCC]"
            ),
            "cdi_note": (
                "Linked to Day 6 fever + 2/5 clinical criteria + CRP/ESR "
                "elevated + 5/6 supplemental labs (Incomplete KD pathway)"
            ),
        },
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def room_sort_key(p: dict) -> tuple:
    room = str(p.get("room", ""))
    unit, _, num = room.partition("-")
    try:
        return (unit, int(num))
    except ValueError:
        return (room, 0)


def patient_by_id(pid: str, census: list[dict]) -> dict:
    for p in census:
        if p["id"] == pid:
            return p
    return census[0]


def roster_label(p: dict) -> str:
    """Legacy census label helper (Linear rail uses census_rail_pills_html)."""
    flag_bits = " ".join(f":red[**{f}**]" for f in p.get("flags", []))
    badge_raw = p.get("badge") or ""
    if badge_raw and not badge_raw.startswith(":"):
        badge_raw = f":green[**{badge_raw}**]"
    base = f"**{p['room']}** · {p['name']}"
    extras = "  ".join(x for x in (flag_bits, badge_raw.strip()) if x)
    return f"{base}  {extras}".rstrip() if extras else base


def census_rail_pills_html(p: dict) -> str:
    """Compact monospace alert pills for the Linear census rail."""
    arch = p.get("archetype")
    pills: list[str] = []
    if arch == "mtx":
        pills = [
            '<span class="pill-crit">!MTX</span>',
            '<span class="pill-crit">!Cr</span>',
            '<span class="pill-muted">HD-MTX Hr 48</span>',
        ]
    elif arch == "pyelo":
        pills = ['<span class="pill-ok">✓ PO Switch Ready</span>']
    elif arch == "refeeding":
        hr = p.get("hr_nadir", 38)
        phos = p.get("phos", 1.9)
        pills = [
            f'<span class="pill-crit">!HR {hr}</span>',
            f'<span class="pill-crit">!Phos {phos}</span>',
        ]
    elif arch == "kawasaki":
        day = p.get("fever_day", 6)
        pills = [
            f'<span class="pill-crit">!Fever {day}d</span>',
            '<span class="pill-crit">!CRP</span>',
            '<span class="pill-muted">Incomplete KD</span>',
        ]
    else:
        pills = [
            f'<span class="pill-crit">{html.escape(f)}</span>'
            for f in p.get("flags", [])
        ]
    return f'<div class="linear-nav-pills">{"".join(pills)}</div>'


def render_census_rail(census: list[dict]) -> None:
    """Linear-style ward census — entire patient card is clickable via JS forwarder."""
    active_id = st.session_state.get("selected_patient", census[0]["id"])
    n_crit = sum(1 for p in census if p.get("critical"))
    n_ready = sum(
        1 for p in census if p.get("archetype") == "pyelo" or "Ready" in str(p.get("badge", ""))
    )
    with st.container(border=True, key="ward_census_rail"):
        st.html(
            '<div class="linear-rail-header">'
            "<span>🏥 Pediatric Ward 4B · Live Census</span>"
            f"<span style=\"font-family:var(--amb-mono);font-weight:600;\">"
            f"{len(census)}</span></div>"
        )
        for idx, p in enumerate(census):
            pt_id = p["id"]
            is_active = pt_id == active_id
            btn_label = f"SELECT_PT_{pt_id}"
            marker_cls = (
                "census-card-marker census-card-active"
                if is_active
                else "census-card-marker"
            )
            with st.container(border=True, key=f"census_patient_card_{pt_id}"):
                st.html(
                    f'<div class="{marker_cls}" data-pt-index="{idx}" '
                    f'data-pt-btn-label="{html.escape(btn_label)}">'
                    '<div class="census-card-identity">'
                    '<div class="census-card-top">'
                    '<div class="census-card-top-left">'
                    f'<span class="pill-room">{html.escape(str(p["room"]))}</span>'
                    f"{html.escape(p['name'])}"
                    "</div>"
                    "</div>"
                    f"{census_rail_pills_html(p)}"
                    "</div></div>"
                )
                # Hidden Streamlit trigger — collapsed by CSS; clicked by JS forwarder
                if st.button(
                    btn_label,
                    key=f"select_pt_{pt_id}",
                    width="stretch",
                    type="secondary",
                ):
                    st.session_state.selected_patient = pt_id
                    st.rerun()
        st.html(
            '<div class="linear-rail-footer">'
            f"{len(census)} Beds Active · {n_crit} Critical Gates · "
            f"{n_ready} Discharge Ready</div>"
        )
        # Click forwarder in the main document (st.html + JS). Prefer this over
        # deprecated components.v1.html / height-0 iframes for the same pattern.
        st.html(
            """
            <div class="census-click-binder-host" aria-hidden="true"></div>
            <script>
            (function() {
                function bindCensusCards() {
                    const doc = document;
                    const buttons = Array.from(doc.querySelectorAll('button'));
                    const ptButtons = {};
                    buttons.forEach(btn => {
                        const txt = (btn.innerText || btn.textContent || '').trim();
                        if (txt.startsWith('SELECT_PT_')) {
                            ptButtons[txt] = btn;
                            const wrapper =
                                btn.closest('[data-testid="stElementContainer"]') ||
                                btn.closest('.element-container') ||
                                btn.parentElement;
                            if (wrapper) {
                                wrapper.style.position = 'absolute';
                                wrapper.style.height = '0px';
                                wrapper.style.minHeight = '0px';
                                wrapper.style.maxHeight = '0px';
                                wrapper.style.overflow = 'hidden';
                                wrapper.style.opacity = '0';
                                wrapper.style.margin = '0px';
                                wrapper.style.padding = '0px';
                                wrapper.style.pointerEvents = 'none';
                                wrapper.style.display = 'none';
                            }
                            btn.style.display = 'none';
                        }
                    });

                    const markers = doc.querySelectorAll('.census-card-marker');
                    markers.forEach(marker => {
                        const targetLabel = marker.getAttribute('data-pt-btn-label');
                        const cardBox =
                            marker.closest('[data-testid="stVerticalBlockBorderWrapper"]') ||
                            marker.parentElement;
                        if (!cardBox || cardBox.dataset.censusBound === 'true') {
                            return;
                        }
                        cardBox.dataset.censusBound = 'true';
                        cardBox.style.cursor = 'pointer';
                        cardBox.addEventListener('click', function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            const btn =
                                ptButtons[targetLabel] ||
                                Array.from(doc.querySelectorAll('button')).find(b =>
                                    (b.innerText || b.textContent || '').trim() === targetLabel
                                );
                            if (btn) {
                                btn.click();
                            }
                        });
                    });
                }
                bindCensusCards();
                setTimeout(bindCensusCards, 150);
                setTimeout(bindCensusCards, 500);
            })();
            </script>
            """,
            unsafe_allow_javascript=True,
        )


def has_critical_flag(p: dict) -> bool:
    return bool(p.get("critical"))


def day_key(pid: str, tid: str) -> str:
    return f"day_{pid}_{tid}"


def night_key(pid: str, tid: str) -> str:
    return f"night_{pid}_{tid}"


# Unified staged-order → Day/Night checklist sync map
ORDER_CHECKLIST_MAP: dict[str, dict] = {
    "emma_leucovorin": {
        "pid": "emma",
        "day": ["d1"],
        "night": ["n1"],
        "badge": (
            "✅ [STAGED IN EPIC: Leucovorin increased 29 → 98 mg IV q6h]"
        ),
        "banner": "Leucovorin staged 29 → 98 mg IV q6h",
    },
    "emma_fluids": {
        "pid": "emma",
        "day": ["d2"],
        "night": ["n3"],
        "badge": (
            "✅ [STAGED IN EPIC: Fluids increased 147 → 196 mL/hr]"
        ),
        "banner": "Hyperhydration staged 147 → 196 mL/hr",
    },
    "emma_bicarb": {
        "pid": "emma",
        "day": ["d3"],
        "night": ["n2"],
        "badge": (
            "✅ [STAGED IN EPIC: STAT NaHCO₃ 26 mEq bolus + bag → 60 mEq/L]"
        ),
        "banner": "NaHCO₃ bolus staged · bag → 60 mEq/L",
    },
    "emma_voraxaze": {
        "pid": "emma",
        "day": ["d4"],
        "night": ["n4"],
        "badge": (
            "✅ [STAGED IN EPIC: q6h MTX + BMP through Hr 54/60/72 · "
            "Voraxaze standby]"
        ),
        "banner": "Hour-54 MTX draw + Voraxaze standby staged",
    },
    "emma_bundle": {
        "pid": "emma",
        "day": ["d1", "d2", "d3", "d4"],
        "night": ["n1", "n2", "n3", "n4"],
        "badge": (
            "✅ [STAGED IN EPIC: Hour-48 rescue bundle — LV 98 mg + "
            "196 mL/hr + NaHCO₃ 26 mEq + Voraxaze watch]"
        ),
        "banner": "Hour-48 rescue bundle staged in Epic cart",
        "also_stage": [
            "emma_leucovorin",
            "emma_fluids",
            "emma_bicarb",
            "emma_voraxaze",
        ],
    },
    "maya_po_switch": {
        "pid": "maya",
        "day": ["d2"],
        "night": ["n2"],
        "badge": (
            "✅ [STAGED IN EPIC: IV Ceftriaxone → PO Cephalexin 400 mg TID]"
        ),
        "banner": "IV→PO Cephalexin switch staged",
    },
    "maya_piv_dc": {
        "pid": "maya",
        "day": ["d5"],
        "night": ["n3"],
        "badge": (
            "✅ [STAGED IN EPIC: DC Ceftriaxone IV · saline-lock PIV · "
            "stop maintenance IVF]"
        ),
        "banner": "IVF discontinued · PIV saline-locked",
    },
    "maya_discharge": {
        "pid": "maya",
        "day": ["d4", "d6"],
        "night": ["n4"],
        "badge": (
            "✅ [STAGED IN EPIC: Pyelo discharge instructions + 48h PCP f/u]"
        ),
        "banner": "Discharge summary + 48h PCP follow-up staged",
    },
    "chloe_telemetry": {
        "pid": "chloe",
        "day": ["d4"],
        "night": ["n1"],
        "badge": (
            "✅ [STAGED IN EPIC: Hold 1,600 kcal advance + continuous telemetry]"
        ),
        "banner": "Telemetry + calorie hold staged",
    },
    "chloe_phos": {
        "pid": "chloe",
        "day": ["d2"],
        "night": ["n2"],
        "badge": (
            "✅ [STAGED IN EPIC: IV NaPhos 0.5 mmol/kg over 6h]"
        ),
        "banner": "IV NaPhos repletion staged",
    },
    "chloe_bedrest": {
        "pid": "chloe",
        "day": ["d3"],
        "night": ["n3"],
        "badge": (
            "✅ [STAGED IN EPIC: Strict bedrest 1:1 + Thiamine 100 mg daily]"
        ),
        "banner": "Bedrest + Thiamine + orthostatic precautions staged",
    },
    "leo_ivig": {
        "pid": "leo",
        "day": ["d2"],
        "night": ["n1", "n3"],
        "badge": (
            "✅ [STAGED IN EPIC: IVIG 26 g IV + High-Dose ASA 260 mg q6h]"
        ),
        "banner": "IVIG 26 g + high-dose ASA staged",
    },
    "leo_echo": {
        "pid": "leo",
        "day": ["d3"],
        "night": ["n4"],
        "badge": (
            "✅ [STAGED IN EPIC: STAT baseline TTE with coronary Z-scores]"
        ),
        "banner": "STAT baseline echo with coronary Z-scores staged",
    },
    "leo_infusion_monitor": {
        "pid": "leo",
        "day": ["d4", "d5"],
        "night": ["n2"],
        "badge": (
            "✅ [STAGED IN EPIC: IVIG reaction vitals q15–30m + 36h fever clock]"
        ),
        "banner": "IVIG reaction protocol + 36h fever clock staged",
    },
}


# Per-patient Epic composer rows (HITL dialog) — order_id keys session state
EPIC_COMPOSER_ORDERS: dict[str, list[dict]] = {
    "emma": [
        {
            "ord_key": "emma_ord_1",
            "order_id": "emma_leucovorin",
            "label": (
                "Leucovorin 100 mg/m² = 98 mg IV q6h until MTX < 0.10 µmol/L"
            ),
        },
        {
            "ord_key": "emma_ord_2",
            "order_id": "emma_fluids",
            "label": (
                "D5 0.2NS + 40→60 mEq/L NaHCO₃ at 200 mL/m²/hr = 196 mL/hr"
            ),
        },
        {
            "ord_key": "emma_ord_3",
            "order_id": "emma_bicarb",
            "label": (
                "NaHCO₃ 26 mEq (1 mEq/kg) IV bolus over 1h ×1 (urine pH 6.8)"
            ),
        },
        {
            "ord_key": "emma_ord_4",
            "order_id": "emma_voraxaze",
            "label": (
                "q6h MTX + daily BMP through Hour 54 / 60 / 72 until clear "
                "& Voraxaze standby"
            ),
        },
    ],
    "maya": [
        {
            "ord_key": "maya_ord_1",
            "order_id": "maya_po_switch",
            "label": (
                "Start Cephalexin (Keflex) 25 mg/kg = 400 mg PO TID × 8 days"
            ),
        },
        {
            "ord_key": "maya_ord_2",
            "order_id": "maya_piv_dc",
            "label": (
                "Discontinue Ceftriaxone IV & saline-lock PIV; "
                "discontinue maintenance IVF"
            ),
        },
        {
            "ord_key": "maya_ord_3",
            "order_id": "maya_discharge",
            "label": (
                "Release pediatric pyelonephritis discharge instructions "
                "& 48h PCP follow-up"
            ),
        },
    ],
    "chloe": [
        {
            "ord_key": "chloe_ord_1",
            "order_id": "chloe_telemetry",
            "label": (
                "Continuous 5-lead cardiac telemetry + hold nutrition "
                "at 1,600 kcal/day"
            ),
        },
        {
            "ord_key": "chloe_ord_2",
            "order_id": "chloe_phos",
            "label": (
                "Sodium Phosphate 0.5 mmol/kg = 19 mmol IV over 6h + "
                "repeat Phos/K/Mg 4h post"
            ),
        },
        {
            "ord_key": "chloe_ord_3",
            "order_id": "chloe_bedrest",
            "label": (
                "Strict bedrest with 1:1 observation + Thiamine 100 mg PO/IV daily"
            ),
        },
    ],
    "leo": [
        {
            "ord_key": "leo_ord_1",
            "order_id": "leo_ivig",
            "label": (
                "IVIG (Gamunex-C 10%) 2 g/kg = 26 g IV over 10–12h + "
                "High-Dose ASA 260 mg PO q6h"
            ),
        },
        {
            "ord_key": "leo_ord_2",
            "order_id": "leo_echo",
            "label": (
                "STAT Baseline Transthoracic Echocardiogram with coronary "
                "Z-scores (LMCA, LAD, RCA)"
            ),
        },
        {
            "ord_key": "leo_ord_3",
            "order_id": "leo_infusion_monitor",
            "label": (
                "IVIG infusion reaction protocol: vitals q15m ×1h, then q30m "
                "+ 36h fever clock"
            ),
        },
    ],
}


def _staged_orders_key(pid: str) -> str:
    return f"staged_orders_{pid}"


def order_is_staged(pid: str, order_id: str) -> bool:
    """True only when this order (or Emma bundle covering it) is in the Epic cart."""
    bag = st.session_state.get(_staged_orders_key(pid), {})
    if order_id in bag:
        return True
    if order_id.startswith("emma_") and order_id != "emma_bundle" and "emma_bundle" in bag:
        return True
    return False


def order_is_addressed(pid: str, order_id: str) -> bool:
    """True when order is staged in Epic cart OR linked checklist items are checked."""
    if order_is_staged(pid, order_id):
        return True
    meta = ORDER_CHECKLIST_MAP.get(order_id)
    if not meta or meta.get("pid") != pid:
        return False
    for tid in meta.get("day", []):
        if st.session_state.get(day_key(pid, tid)):
            return True
    for tid in meta.get("night", []):
        if st.session_state.get(night_key(pid, tid)):
            return True
    return False


def order_addressed_at(
    pid: str,
    order_id: str,
    *,
    default: str = "07:12",
) -> str:
    """Timestamp from staged order bag, else demo default."""
    bag = st.session_state.get(_staged_orders_key(pid), {})
    for oid in (order_id, "emma_bundle"):
        entry = bag.get(oid)
        if entry and entry.get("at"):
            return str(entry["at"])
    return default


def patient_composer_orders(pid: str) -> list[dict]:
    return list(EPIC_COMPOSER_ORDERS.get(pid, []))


def patient_signing_progress(pid: str) -> tuple[int, int]:
    """Return (signed_count, total) for Epic composer rows."""
    rows = patient_composer_orders(pid)
    if not rows:
        return (0, 0)
    signed = sum(1 for r in rows if order_is_staged(pid, r["order_id"]))
    return (signed, len(rows))


def addressed_badge(text: str) -> str:
    """Green resolution pill for addressed critical telemetry tiles."""
    return f'<span class="crit-met-green">{html.escape(text)}</span>'


def breach_badge(text: str) -> str:
    """Red critical alert pill for unaddressed threshold breaches."""
    return f'<span class="crit-met-red">{html.escape(text)}</span>'


def _tid_covered_by_other_staged(
    pid: str, tid: str, *, shift: str, exclude: str
) -> bool:
    """True if another staged order for this patient still claims this checklist id."""
    bag = st.session_state.get(_staged_orders_key(pid), {})
    for oid, entry in bag.items():
        if oid == exclude or not entry:
            continue
        meta = ORDER_CHECKLIST_MAP.get(oid)
        if not meta or meta.get("pid") != pid:
            continue
        if tid in meta.get(shift, []):
            return True
    return False


def commit_staged_order(
    order_id: str,
    *,
    title: str,
    cdi: str = "",
    cdi_label: str = "",
    cdi_note: str = "",
    widget_key: str | None = None,
    also_stage: bool = True,
) -> None:
    """Record staged order, check off Day+Night checklist items, set badges."""
    meta = ORDER_CHECKLIST_MAP.get(order_id)
    if not meta:
        return
    pid = meta["pid"]
    now = datetime.now().strftime("%H:%M")
    if widget_key:
        st.session_state[f"staged_flag_{widget_key}"] = True
    st.session_state[f"order_committed_{pid}"] = {
        "at": now,
        "title": title,
        "cdi": cdi,
        "cdi_label": cdi_label,
        "cdi_note": cdi_note,
        "order_id": order_id,
    }
    bag = st.session_state.setdefault(_staged_orders_key(pid), {})
    bag[order_id] = {
        "at": now,
        "title": title,
        "badge": meta["badge"],
        "banner": meta["banner"],
    }
    for tid in meta.get("day", []):
        st.session_state[day_key(pid, tid)] = True
    for tid in meta.get("night", []):
        st.session_state[night_key(pid, tid)] = True
    # Nested bundle also marks component orders staged
    if also_stage:
        for nested in meta.get("also_stage", []):
            nmeta = ORDER_CHECKLIST_MAP.get(nested)
            if not nmeta:
                continue
            bag[nested] = {
                "at": now,
                "title": nmeta["banner"],
                "badge": nmeta["badge"],
                "banner": nmeta["banner"],
            }
            for tid in nmeta.get("day", []):
                st.session_state[day_key(pid, tid)] = True
            for tid in nmeta.get("night", []):
                st.session_state[night_key(pid, tid)] = True
    st.session_state[f"status_overlay_{pid}"] = meta["banner"]


def uncommit_staged_order(order_id: str) -> None:
    """Undo a single staged order and uncheck checklist items it uniquely owns."""
    meta = ORDER_CHECKLIST_MAP.get(order_id)
    if not meta:
        return
    pid = meta["pid"]
    bag = st.session_state.setdefault(_staged_orders_key(pid), {})
    bag.pop(order_id, None)
    # Undoing a component also drops the Emma umbrella bundle
    if order_id.startswith("emma_") and order_id != "emma_bundle":
        bag.pop("emma_bundle", None)
    for tid in meta.get("day", []):
        if not _tid_covered_by_other_staged(pid, tid, shift="day", exclude=order_id):
            st.session_state[day_key(pid, tid)] = False
    for tid in meta.get("night", []):
        if not _tid_covered_by_other_staged(pid, tid, shift="night", exclude=order_id):
            st.session_state[night_key(pid, tid)] = False
    st.session_state.pop(f"staged_flag_{order_id}", None)
    # Keep patient-level committed flag while any composer row remains signed
    remaining = [
        r for r in patient_composer_orders(pid) if order_is_staged(pid, r["order_id"])
    ]
    if remaining:
        last = remaining[-1]
        entry = bag.get(last["order_id"], {})
        st.session_state[f"order_committed_{pid}"] = {
            "at": entry.get("at", datetime.now().strftime("%H:%M")),
            "title": entry.get("title", last["label"]),
            "cdi": "",
            "cdi_label": "",
            "cdi_note": "",
            "order_id": last["order_id"],
        }
        st.session_state[f"status_overlay_{pid}"] = entry.get(
            "banner", meta.get("banner", "")
        )
    else:
        st.session_state.pop(f"order_committed_{pid}", None)
        st.session_state.pop(f"status_overlay_{pid}", None)


def sign_all_patient_orders(p: dict) -> None:
    """Sign every composer order for this patient."""
    so = p.get("stage_order") or {}
    for row in patient_composer_orders(p["id"]):
        if order_is_staged(p["id"], row["order_id"]):
            continue
        commit_staged_order(
            row["order_id"],
            title=row["label"],
            cdi=so.get("cdi_code", ""),
            cdi_label=so.get("cdi_label", ""),
            cdi_note=so.get("cdi_note", ""),
            also_stage=False,
        )
    st.session_state[f"status_overlay_{p['id']}"] = (
        f"All Epic orders signed · {so.get('title', 'bundle')}"
    )


def reset_all_patient_orders(p: dict) -> None:
    """Reset every composer order for interview walkthrough demos."""
    for row in patient_composer_orders(p["id"]):
        if order_is_staged(p["id"], row["order_id"]):
            uncommit_staged_order(row["order_id"])
    bag = st.session_state.setdefault(_staged_orders_key(p["id"]), {})
    bag.clear()
    st.session_state.pop(f"order_committed_{p['id']}", None)
    st.session_state.pop(f"status_overlay_{p['id']}", None)


def checklist_label_with_stage(pid: str, tid: str, base_label: str) -> str:
    """Append green staged badge when a linked order was signed to cart."""
    bag = st.session_state.get(_staged_orders_key(pid), {})
    # Prefer specific component orders before umbrella bundles
    preferred = (
        "emma_leucovorin",
        "emma_fluids",
        "emma_bicarb",
        "emma_voraxaze",
        "maya_po_switch",
        "maya_piv_dc",
        "maya_discharge",
        "chloe_telemetry",
        "chloe_phos",
        "chloe_bedrest",
        "leo_ivig",
        "leo_echo",
        "leo_infusion_monitor",
        "emma_bundle",
    )
    for oid in preferred:
        meta = ORDER_CHECKLIST_MAP.get(oid)
        if not meta or meta.get("pid") != pid:
            continue
        if tid not in meta.get("day", []) and tid not in meta.get("night", []):
            continue
        if oid in bag:
            return f"{base_label}  \n:green[**{bag[oid]['badge']}**]"
    return base_label


def _ev(button: str, header: str, evidence: str, why: str) -> dict:
    return {
        "button": button,
        "header": header,
        "evidence": evidence,
        "why": why,
    }


def _cm_red(text: str) -> str:
    """Inline pill for met / positive / critical criteria in EHR excerpts."""
    return f'<span class="crit-met-red">{text}</span>'


def _cm_green(text: str) -> str:
    """Inline pill for met de-escalation / clearance criteria in EHR excerpts."""
    return f'<span class="crit-met-green">{text}</span>'


def _cm_absent(text: str) -> str:
    """Muted slate for absent / negative criteria (do not highlight)."""
    return f'<span class="crit-absent">{text}</span>'


def _leo_ivig_reaction_evidence_html() -> str:
    """Structured IVIG titration + reaction classification for Leo checklist."""
    return (
        '<div class="ehr-ev-subhead">A · Active Infusion Titration &amp; '
        "Pre-Medication Order</div>"
        "<div>Total Dose: "
        + _cm_green(
            "✅ IVIG 2 g/kg = 26 g (260 mL of 10% solution) IV over 10–12 hours"
        )
        + ". Pre-medicate 30 min prior with Diphenhydramine 1 mg/kg (13 mg) "
        "PO/IV + Acetaminophen 15 mg/kg (195 mg) PO. Titrate rate sequentially: "
        + _cm_green(
            "0.5 mL/kg/hr (6.5 mL/hr) × 30 min → 1.0 mL/kg/hr (13 mL/hr) × "
            "30 min → 2.0 mL/kg/hr (26 mL/hr) → max 3.0 mL/kg/hr (39 mL/hr)"
        )
        + " with q15m vitals for the first hour, then q30–60m.</div>"
        '<div class="ehr-ev-subhead">B · Classification of IVIG Infusion '
        "Reactions (What to Monitor For at Bedside)</div>"
        '<div class="ehr-ev-rxn">'
        '<div class="ehr-ev-rxn-title">1. Common Rate-Related / Mild-to-Moderate '
        "Reactions</div>"
        "<div>Occurs in 5–15% of infusions; usually within first 30–60 min of "
        "rate escalation.</div>"
        "<div><strong>Clinical Signs:</strong> "
        + _cm_red(
            "⚠️ Flushing, rigors/chills, low-grade fever spike, headache, "
            "myalgias, lower back/abdominal pain, nausea/vomiting, or mild "
            "tachycardia"
        )
        + " (caused by complement activation from IgG aggregates).</div>"
        "<div><strong>Bedside Action:</strong> "
        + _cm_green("Slow or pause infusion for 15–30 minutes")
        + ", administer PRN Diphenhydramine / Acetaminophen, and resume at "
        "50% of the prior tolerated rate once symptoms resolve.</div>"
        "</div>"
        '<div class="ehr-ev-rxn">'
        '<div class="ehr-ev-rxn-title">2. Anaphylactoid / Severe Hypersensitivity '
        "Reactions (Immediate / IgA-Mediated)</div>"
        "<div><strong>Clinical Signs:</strong> "
        + _cm_red(
            "🚨 Generalized urticaria, angioedema, bronchospasm/wheezing, "
            "stridor, dyspnea, hypoxemia, or hypotensive shock"
        )
        + ".</div>"
        "<div><strong>Bedside Action:</strong> "
        + _cm_red("STOP IVIG IMMEDIATELY")
        + ", maintain airway, administer "
        + _cm_red("IM Epinephrine 0.01 mg/kg (0.13 mg of 1 mg/mL)")
        + ", NS 20 mL/kg IV bolus, IV Methylprednisolone 1–2 mg/kg, and "
        "Diphenhydramine.</div>"
        "</div>"
        '<div class="ehr-ev-rxn">'
        '<div class="ehr-ev-rxn-title">3. Delayed Aseptic Meningitis Syndrome '
        "(AMS — Occurs 12–48 hours post-infusion)</div>"
        "<div><strong>Clinical Signs:</strong> "
        + _cm_red(
            "⚠️ Severe intractable headache, nuchal rigidity/neck stiffness, "
            "photophobia, high fever, and vomiting"
        )
        + " (CSF shows pleocytosis with negative cultures; higher risk with "
        "high-dose 2 g/kg IVIG).</div>"
        "<div><strong>Bedside Action:</strong> Supportive management with IV "
        "hydration, scheduled analgesics/antiemetics, and slow infusion rate "
        "if still running (self-resolves in 2–5 days).</div>"
        "</div>"
        '<div class="ehr-ev-rxn">'
        '<div class="ehr-ev-rxn-title">4. Volume Overload, Hemolysis &amp; '
        "Hyperviscosity / Renal Toxicity Risks</div>"
        "<div><strong>Clinical Signs:</strong> "
        + _cm_red(
            "⚠️ Tachycardia, new rales/hepatomegaly, or BP spike from oncotic "
            "fluid shift"
        )
        + " (260 mL colloid load); "
        + _cm_red("Coombs-positive hemolytic anemia")
        + " (from passive anti-A/anti-B isohemagglutinins in non-type-O "
        "patients — monitor Hgb drops 48–72h post-IVIG); or "
        + _cm_red("osmotic nephrosis / AKI")
        + " (use sucrose-free IVIG product).</div>"
        "</div>"
        '<div class="ehr-ev-subhead">C · ID &amp; Cardiology Escalation '
        "Triggers</div>"
        "<div>Page Pediatric Cardiology &amp; Infectious Disease if "
        + _cm_red(
            "fever ≥ 38.0°C (100.4°F) persists or recurs ≥ 36 hours after "
            "IVIG completion (IVIG-Refractory KD)"
        )
        + " to initiate 2nd-line rescue therapy (2nd IVIG 2 g/kg dose, "
        "Infliximab 5–10 mg/kg IV, or IV Methylprednisolone).</div>"
    )


# Task-specific EHR evidence for Day + Night checklist source popovers
CHECKLIST_EHR_EVIDENCE: dict[str, dict[str, dict]] = {
    "emma": {
        "d1": _ev(
            "📄 Source: Hr-48 MTX Lab (06:42)",
            "🧪 Therapeutic Drug Monitoring — Hour 48 Serum Methotrexate · 06:42",
            (
                f"{_cm_red('✅ Serum MTX (Hr 48): 4.20 µmol/L [CRITICAL HIGH — COG AALL1131 Hr-48 Target ≤ 0.40 µmol/L; 10.5x cutoff]')}. "
                "Prior trajectory: Hr 24 = 118.0 µmol/L → Hr 36 = 8.40 µmol/L → Hr 42 = 5.20 µmol/L → Hr 48 = 4.20 µmol/L."
            ),
            "COG AALL1131 Bleyer Nomogram mandates escalating IV Leucovorin from 30 mg/m² (29 mg) to 100 mg/m² (98 mg) IV q6h (infused over 15 min due to Ca²⁺ limit) when Hr-48 MTX is between 2.0 and 19.9 µmol/L.",
        ),
        "d2": _ev(
            "📄 Source: BMP & MAR Flowsheet (06:15)",
            "📊 Basic Metabolic Panel (06:15) & Nursing I&O / MAR Flowsheet (06:30)",
            (
                f"{_cm_red('✅ Serum Creatinine: 0.68 mg/dL [HIGH — Baseline 0.40 mg/dL at Hr 0; +70% rise meets KDIGO Stage 1 AKI ≥50% cutoff]')}. "
                "BUN: 18 mg/dL, K: 4.1 mEq/L, CO₂: 24 mEq/L. Active MAR Infusion: D5 0.2NS + 40 mEq/L NaHCO₃ currently running at 147 mL/hr (150 mL/m²/hr). "
                "Net 24h I&O: +420 mL; Daily Weight: 26.4 kg (+0.4 kg from 26.0 kg baseline)."
            ),
            "Cr rise ≥ 50% above baseline requires immediate fluid escalation to 200 mL/m²/hr (196 mL/hr) to clear intratubular MTX precipitates.",
        ),
        "d3": _ev(
            "📄 Source: Point-of-Care Urine Dipstick (06:30)",
            "🚽 Bedside Point-of-Care Urinalysis — Nursing Flowsheet · 06:30 (RN S. Jenkins)",
            (
                f"{_cm_red('✅ Urine pH: 6.8 [CRITICAL LOW — HD-MTX Protocol Target ≥ 7.0]')}. "
                "Specific Gravity: 1.012. Prior Urine pH: Hr 36 = 7.0 → Hr 42 = 6.9 → Hr 48 = 6.8."
            ),
            "Methotrexate solubility drops 10-fold as urine pH falls below 7.0; requires STAT 1 mEq/kg (26 mEq) IV NaHCO₃ bolus, bag increase to 60 mEq/L, and repeat dipstick in 1 hour.",
        ),
        "d4": _ev(
            "📄 Source: Onc Pharm Consult Note (07:00)",
            "💊 Oncology Clinical Pharmacy Note — PharmD K. Chen · 07:00",
            (
                "'Patient at Hour 48 post-HD-MTX with serum MTX 4.20 µmol/L and Stage 1 AKI (Cr 0.68 mg/dL). "
                f"Inpatient pharmacy has verified {_cm_red('✅ 2 vials of Glucarpidase (Voraxaze 50 U/kg = 1,300 Units IV) verified on standby if Hr-54 MTX > 2.0–5.0 µmol/L with worsening Cr')}. "
                "If Hour-54 (14:00) MTX remains in that range with worsening Cr, administer Voraxaze and hold Leucovorin within 2h before/after.'"
            ),
            "Voraxaze standby + confirmed Hour-54 STAT MTX draw are required before overnight handoff when Hr-48 MTX remains critically elevated with AKI.",
        ),
        "d5": _ev(
            "📄 Source: Med Rec / OAT Alert (06:50)",
            "💊 Pharmacy Medication Reconciliation — High-Alert OAT1/OAT3 Flag · 06:50",
            "Active home/inpatient meds screened: no NSAIDs, TMP-SMX, PPIs, or penicillins currently scheduled. Alert posted: Hold nephrotoxins and OAT1–OAT3 inhibitors until serum MTX < 0.10 µmol/L.",
            "OAT competition prolongs MTX clearance; medication hold protects the delayed-clearance rescue pathway.",
        ),
        "d6": _ev(
            "📄 Source: Family Update Note (07:20)",
            "👨‍👩‍👧 Attending Family Communication Note · 07:20",
            "'Parents updated on Hour-48 delayed MTX clearance (4.20 µmol/L), Stage 1 AKI, and overnight monitoring plan. Counseled that discharge is not appropriate until MTX < 0.10 µmol/L and Cr trend improves.'",
            "Shared mental model with family prevents premature discharge pressure during critical delayed-clearance window.",
        ),
        "n1": _ev(
            "📄 Source: Hr-54 MTX Draw Order (14:00)",
            "🧪 Scheduled Therapeutic Drug Monitoring — Hour 54 STAT MTX + BMP · Due 14:00",
            (
                f"Order active: STAT Serum MTX + BMP at Hour 54 (14:00). Prior "
                f"{_cm_red('✅ Serum MTX (Hr 48): 4.20 µmol/L [CRITICAL HIGH — COG AALL1131 Hr-48 Target ≤ 0.40 µmol/L; 10.5x cutoff]')}. "
                "Trigger threshold: if MTX still > 2.0–5.0 µmol/L with rising Cr → escalate to Glucarpidase pathway per Onc Pharm note."
            ),
            "Night cross-cover must obtain and review Hour-54 MTX/BMP before continuing q6h monitoring to < 0.10 µmol/L.",
        ),
        "n2": _ev(
            "📄 Source: Point-of-Care Urine Dipstick (06:30)",
            "🚽 Bedside Point-of-Care Urinalysis — Nursing Flowsheet · 06:30 (RN S. Jenkins)",
            (
                f"{_cm_red('✅ Urine pH: 6.8 [CRITICAL LOW — HD-MTX Protocol Target ≥ 7.0]')}. "
                "Post-bolus 1h recheck pending after NaHCO₃ 26 mEq IV."
            ),
            "qVoid urine pH ≥ 7.0 is mandatory overnight; recheck 1h after NaHCO₃ bolus and escalate bag alkalinization if still acidic.",
        ),
        "n3": _ev(
            "📄 Source: BMP & MAR Flowsheet (06:15)",
            "📊 Nursing I&O / Weight Flowsheet on 196 mL/hr Target · Updated 06:30",
            (
                f"{_cm_red('✅ Serum Creatinine: 0.68 mg/dL [HIGH — Baseline 0.40 mg/dL at Hr 0; +70% rise meets KDIGO Stage 1 AKI ≥50% cutoff]')}. "
                "Net 24h I&O: +420 mL; Daily Weight: 26.4 kg (+0.4 kg from 26.0 kg). Hydration target after escalation: 196 mL/hr (200 mL/m²/hr)."
            ),
            "Strict q4h I&Os/weights on hyperhydration; call for furosemide consideration if cumulative gain > +2 kg.",
        ),
        "n4": _ev(
            "📄 Source: Onc Pharm Consult Note (07:00)",
            "💊 Oncology Clinical Pharmacy — Glucarpidase Standby Pathway · 07:00",
            (
                f"{_cm_red('✅ 2 vials of Glucarpidase (Voraxaze 50 U/kg = 1,300 Units IV) verified on standby if Hr-54 MTX > 2.0–5.0 µmol/L with worsening Cr')}. "
                "Night trigger: MTX plateau, oliguria, or further Cr rise → screen for immediate Glucarpidase."
            ),
            "Cross-cover escalation criteria are pre-defined so delayed clearance does not wait until morning rounds.",
        ),
    },
    "maya": {
        "d1": _ev(
            "📄 Source: Vitals & Nursing I&O Note (06:00)",
            "📈 Nursing Vitals & Intake/Output Flowsheet · 06:00 (RN M. Torres)",
            (
                f"{_cm_green('✅ 30 hours afebrile (Tmax 37.1°C / 98.8°F; meets ≥ 24h afebrile cutoff)')}. "
                "Last fever ≥ 38.0°C (100.4°F) was 30 hours ago (38.8°C at 00:00 yesterday). Last PRN antipyretic given 32 hours ago. "
                f"{_cm_green('✅ Tolerating 100% PO fluids (1,150 mL/24h, 0 emesis)')}; brisk urine output at 2.4 mL/kg/hr."
            ),
            "Meets AAP Pyelonephritis IV-to-PO switch criteria (afebrile ≥ 24h + tolerating full PO fluids and medications).",
        ),
        "d2": _ev(
            "📄 Source: Final Urine Cx & MIC Table (05:30)",
            "🦠 Microbiology Final Report — Catheterized Urine Culture · 05:30",
            (
                f"Organism: {_cm_green('✅ >100,000 CFU/mL Pansensitive E. coli — Cefazolin [S, MIC ≤ 1 µg/mL — predicts oral Cephalexin susceptibility]')}. "
                "Full susceptibilities: Ampicillin [S, MIC ≤ 2], Cefazolin [S, MIC ≤ 1], Ceftriaxone [S, MIC ≤ 0.25], Gentamicin [S], TMP-SMX [S], Nitrofurantoin [S]."
            ),
            "Pansensitive E. coli with Cefazolin MIC ≤ 1 µg/mL allows narrow-spectrum de-escalation from IV Ceftriaxone to first-generation PO Cephalexin.",
        ),
        "d3": _ev(
            "📄 Source: Blood Cx & Renal US Report (05:45)",
            "🩻 Pediatric Radiology Renal Ultrasound & 48h Blood Culture · 05:45",
            (
                f"{_cm_green('✅ 48h Blood Culture: No growth to date (Negative)')}. "
                f"{_cm_green('✅ Renal Ultrasound: Normal bilateral kidneys, no hydronephrosis or abscess')}. "
                "Full report: 'Normal bilateral renal cortical echogenicity and kidney lengths. No hydronephrosis, hydroureter, renal abscess, or perinephric fluid collection. Normal bladder wall.' "
                "Serum Cr improved from 0.48 to 0.34 mg/dL; WBC down from 18.2k to 9.4k."
            ),
            "Rules out bacteremia and anatomic urinary tract obstruction, clearing patient for outpatient PO completion.",
        ),
        "d4": _ev(
            "📄 Source: DC Planning Note (07:10)",
            "🏠 Care Coordination / Discharge Planning Note · 07:10",
            "Cephalexin suspension Rx verified with outpatient pharmacy; PCP follow-up scheduled; family teaching packet on fever return precautions printed.",
            "Discharge barriers must be cleared before signing the summary once IV→PO switch is complete.",
        ),
        "d5": _ev(
            "📄 Source: Vitals & Nursing I&O Note (06:00)",
            "📈 Nursing Flowsheet — PO Tolerance & PIV Status · 06:00",
            "PO intake 100% of maintenance; 0 emesis; PIV intact right hand. Ready to saline-lock/DC PIV after first PO cephalexin dose tolerated.",
            "Discontinue PIV only after confirmed PO antibiotic tolerance to avoid line-related risk after de-escalation.",
        ),
        "d6": _ev(
            "📄 Source: Family Teaching Note (07:25)",
            "👨‍👩‍👧 Nursing/Attending Family Teaching · 07:25",
            "'Family taught 7–10 day total antibiotic course, fever precautions, and return precautions for flank pain/emesis.'",
            "Home antibiotic adherence counseling closes the pyelo discharge pathway.",
        ),
        "n1": _ev(
            "📄 Source: Vitals & Nursing I&O Note (06:00)",
            "📈 Night Contingency — Fever Recurrence Gate",
            (
                f"Baseline: {_cm_green('✅ 30 hours afebrile (Tmax 37.1°C / 98.8°F; meets ≥ 24h afebrile cutoff)')}. "
                "Night rule: if T ≥ 38.0°C → hold discharge and notify day team."
            ),
            "Fever recurrence voids same-day discharge readiness after IV→PO switch.",
        ),
        "n2": _ev(
            "📄 Source: Final Urine Cx & MIC Table (05:30)",
            "🦠 Microbiology + MAR — First PO Cephalexin Dose",
            (
                f"{_cm_green('✅ >100,000 CFU/mL Pansensitive E. coli — Cefazolin [S, MIC ≤ 1 µg/mL — predicts oral Cephalexin susceptibility]')}. "
                "Cephalexin 400 mg PO TID staged. Night action: ensure first PO dose given before overnight if order signed."
            ),
            "First inpatient PO dose documents tolerance before overnight cross-cover.",
        ),
        "n3": _ev(
            "📄 Source: Vitals & Nursing I&O Note (06:00)",
            "📈 Nursing Comfort / Emesis Watch · Overnight",
            (
                f"{_cm_green('✅ Tolerating 100% PO fluids (1,150 mL/24h, 0 emesis)')}. "
                "Call trigger: emesis after PO antibiotic → hold further PO doses and notify."
            ),
            "Post-dose emesis threatens oral step-down success and may require IV fallback.",
        ),
        "n4": _ev(
            "📄 Source: Blood Cx & Renal US Report (05:45)",
            "🧪 Night Labs Guidance",
            (
                f"{_cm_green('✅ 48h Blood Culture: No growth to date (Negative)')}. "
                f"{_cm_green('✅ Renal Ultrasound: Normal bilateral kidneys, no hydronephrosis or abscess')}. "
                "Cr improved to 0.34 mg/dL. No routine overnight labs unless clinical change."
            ),
            "Avoid unnecessary nocturnal phlebotomy when trajectory is already reassuring.",
        ),
    },
    "chloe": {
        "d1": _ev(
            "📄 Source: Overnight Telemetry & Vitals (03:45)",
            "🫀 Overnight Vital Signs & Bedside Monitor Log · 03:45 (RN L. Davis)",
            (
                f"{_cm_red('✅ Sleeping Heart Rate Nadir: 38 bpm at 03:45 [CRITICAL BRADYCARDIA — Cutoff < 45 bpm]')}. "
                "Morning Orthostatics (06:00): Supine HR 44 bpm, BP 84/48 mmHg → Standing HR 72 bpm, Standing BP 78/44 mmHg with dizziness. "
                f"{_cm_red('✅ Orthostatic ΔHR +28 bpm (Supine 44 -> Standing 72 bpm; meets ≥ 20 bpm cutoff)')}. "
                "Current Diet Order: Scheduled to advance from 1,600 kcal/day to 1,900 kcal/day at 08:00."
            ),
            "HR < 45 bpm with positive orthostatics and active refeeding hypophosphatemia requires holding caloric advancement and continuous cardiac monitoring to prevent arrhythmia/sudden cardiac arrest.",
        ),
        "d2": _ev(
            "📄 Source: Refeeding Electrolyte Panel (05:15)",
            "🧪 Morning Refeeding Metabolic Panel — Core Lab · 05:15",
            (
                f"{_cm_red('✅ Serum Phosphorus: 1.9 mg/dL [CRITICAL LOW — Refeeding Cutoff < 2.5 mg/dL]')} "
                "(dropped from 3.1 mg/dL on Day 1 → 2.4 mg/dL on Day 2 → 1.9 mg/dL on Day 3). "
                f"{_cm_red('✅ Potassium: 3.3 mEq/L [LOW < 3.5]')}. "
                f"{_cm_red('✅ Magnesium: 1.6 mg/dL [LOW < 1.8]')}. "
                "Glucose: 76 mg/dL."
            ),
            "Insulin surge from carbohydrate refeeding drives intracellular phosphate shift, depleting myocardial ATP; Phos < 2.0 mg/dL requires immediate IV Sodium Phosphate replacement rather than PO packets alone.",
        ),
        "d3": _ev(
            "📄 Source: Overnight Telemetry & Vitals (03:45)",
            "🫀 Continuous Telemetry Indication — SAHM/NICE Bradycardia Gate",
            (
                f"{_cm_red('✅ Sleeping Heart Rate Nadir: 38 bpm at 03:45 [CRITICAL BRADYCARDIA — Cutoff < 45 bpm]')}; "
                f"{_cm_red('✅ Orthostatic ΔHR +28 bpm (Supine 44 -> Standing 72 bpm; meets ≥ 20 bpm cutoff)')}. "
                "Continuous telemetry and orthostatic precautions ordered pending Phos recovery."
            ),
            "Bedrest/telemetry while symptomatic bradycardia and critical hypophosphatemia coexist.",
        ),
        "d4": _ev(
            "📄 Source: Overnight Telemetry & Vitals (03:45)",
            "🥗 Calorie Hold Gate — Linked to HR 38 & Phos 1.9",
            (
                f"{_cm_red('✅ Sleeping Heart Rate Nadir: 38 bpm at 03:45 [CRITICAL BRADYCARDIA — Cutoff < 45 bpm]')}. "
                "Diet currently set to advance 1,600 → 1,900 kcal at 08:00. Hold at 1,600 kcal until Phos ≥ 2.5 mg/dL and HR stable."
            ),
            "Caloric advancement during active refeeding crisis worsens intracellular phosphate shift and arrhythmia risk.",
        ),
        "d5": _ev(
            "📄 Source: Registered Dietitian Note (06:50)",
            "🥗 Adolescent Medicine & Clinical Nutrition Note — RD A. Brooks · 06:50",
            (
                f"'15y F (Weight 38.0 kg). {_cm_red('✅ Severe Protein-Calorie Malnutrition (71% median BMI) — Hold caloric advancement at 1,600 kcal/day until Phos > 2.5 mg/dL')}. "
                "Given Day 3 phosphorus drop to 1.9 mg/dL and HR nadir 38 bpm, continue Thiamine 100 mg daily + multivitamin prior to morning feeds, and maintain 1:1 bathroom/post-meal observation.'"
            ),
            "Nutrition + Behavioral Health 1:1 meal supervision and thiamine are mandatory co-interventions with electrolyte rescue.",
        ),
        "d6": _ev(
            "📄 Source: Registered Dietitian Note (06:50)",
            "👨‍👩‍👧 Family Update — Refeeding Syndrome Monitoring Plan · 06:50",
            (
                f"{_cm_red('✅ Severe Protein-Calorie Malnutrition (71% median BMI) — Hold caloric advancement at 1,600 kcal/day until Phos > 2.5 mg/dL')}. "
                "Family counseled on why calories are held, IV phosphate plan, telemetry, and 1:1 supervision until Phos/HR recover."
            ),
            "Family alignment reduces conflict around meal plan plateau during crisis monitoring.",
        ),
        "n1": _ev(
            "📄 Source: Overnight Telemetry & Vitals (03:45)",
            "🫀 Night Escalation Rule — HR < 40",
            (
                f"{_cm_red('✅ Sleeping Heart Rate Nadir: 38 bpm at 03:45 [CRITICAL BRADYCARDIA — Cutoff < 45 bpm]')}. "
                "If HR < 40 or symptomatic bradycardia overnight → notify senior / consider ICU."
            ),
            "Pre-defined cross-cover trigger prevents delayed response to malignant bradycardia.",
        ),
        "n2": _ev(
            "📄 Source: Refeeding Electrolyte Panel (05:15)",
            "🧪 Post-IV Phosphate Recheck Plan — Due ~04:00 window",
            (
                f"Baseline {_cm_red('✅ Serum Phosphorus: 1.9 mg/dL [CRITICAL LOW — Refeeding Cutoff < 2.5 mg/dL]')} / "
                f"{_cm_red('✅ Potassium: 3.3 mEq/L [LOW < 3.5]')} / "
                f"{_cm_red('✅ Magnesium: 1.6 mg/dL [LOW < 1.8]')}. "
                "Recheck Phos/K/Mg 4h after IV sodium phosphate; call if Phos < 2.0."
            ),
            "Night labs confirm whether IV repletion closed the critical hypophosphatemia gap.",
        ),
        "n3": _ev(
            "📄 Source: Registered Dietitian Note (06:50)",
            "🥗 Overnight Meal Supervision Protocol",
            (
                f"{_cm_red('✅ Severe Protein-Calorie Malnutrition (71% median BMI) — Hold caloric advancement at 1,600 kcal/day until Phos > 2.5 mg/dL')}. "
                "1:1 bathroom/post-meal observation continues overnight; supervised snacks only per 1,600 kcal plateau."
            ),
            "Unsupervised bathroom access risks purging and destabilizes refeeding safety plan.",
        ),
        "n4": _ev(
            "📄 Source: Overnight Telemetry & Vitals (03:45)",
            "🫀 Q2h Neuro/Cardiac Checks While Phos Critically Low",
            (
                f"{_cm_red('✅ Serum Phosphorus: 1.9 mg/dL [CRITICAL LOW — Refeeding Cutoff < 2.5 mg/dL]')} + "
                f"{_cm_red('✅ Sleeping Heart Rate Nadir: 38 bpm at 03:45 [CRITICAL BRADYCARDIA — Cutoff < 45 bpm]')}. "
                "Q2h checks for arrhythmia symptoms, weakness, or altered mentation."
            ),
            "Critical hypophosphatemia can progress to respiratory/cardiac failure without frequent reassessment.",
        ),
    },
    "leo": {
        "d1": _ev(
            "📄 Source: H&P & 2/5 Exam Note (06:00)",
            "🩺 Pediatric Attending Admission H&P & Physical Exam · 06:00",
            (
                f"{_cm_red('Fever Duration: Day 6 unexplained fever, Tmax 39.4°C (102.9°F)')}. "
                "Physical Exam — ONLY 2 of 5 AHA Principal Criteria Positive: "
                f"{_cm_red('(1) ✅ Bilateral non-exudative bulbar conjunctival injection with limbal sparing (Day 2)')}; "
                f"{_cm_red('(2) ✅ Diffuse maculopapular polymorphous truncal & groin rash (Day 3)')}. "
                f"{_cm_absent('ABSENT: oral mucosal changes (lips moist/intact, no strawberry tongue); peripheral extremity erythema/edema; cervical node ≥1.5 cm (shotty <0.8 cm only)')}. "
                "Impression: Incomplete KD — enter CRP/ESR + supplemental lab algorithm."
            ),
            "Day 6 fever + only 2/5 principal signs triggers the AHA Incomplete KD pathway (not Complete KD ≥4). Lab confirmation (CRP/ESR + ≥3 supplemental labs) is required before treatment.",
        ),
        "d2": _ev(
            "📄 Source: Inflammatory & Supplemental Labs (05:00)",
            "🧪 Rheumatology / Inflammatory Lab Panel · 05:00",
            (
                f"{_cm_red('✅ CRP: 14.2 mg/dL [CRITICAL HIGH — AHA cutoff ≥ 3.0 mg/dL]')}. "
                f"{_cm_red('✅ ESR: 78 mm/h [HIGH — AHA cutoff ≥ 40 mm/h]')}. "
                "Supplemental Labs (5/6 Positive): "
                f"{_cm_red('(1) ✅ WBC 17.4k/µL (≥15k)')}, "
                f"{_cm_red('(2) ✅ Hgb 9.8 g/dL (anemia for age)')}, "
                f"{_cm_red('(3) ✅ Albumin 2.7 g/dL (≤3.0)')}, "
                f"{_cm_red('(4) ✅ ALT 68 U/L (elevated)')}, and "
                f"{_cm_red('(5) ✅ Urinalysis 24 WBC/hpf (sterile pyuria ≥10 WBC/hpf)')}. "
                "Platelets: 390k/µL (normal on Day 6). Viral/Strep/Blood Cx negative; normal Troponin & BNP (excludes MIS-C)."
            ),
            "With only 2/5 clinical criteria, CRP 14.2, ESR 78, and 5/6 positive supplemental labs confirm Incomplete Kawasaki Disease requiring immediate IVIG 2 g/kg + high-dose ASA (do not delay for echo).",
        ),
        "d3": _ev(
            "📄 Source: Pediatric Cardiology Consult (06:45)",
            "🫀 Pediatric Cardiology Consult Note — Dr. R. Arman · 06:45",
            (
                "'2y M (13.0 kg) with Day 6 Incomplete Kawasaki Disease (2/5 clinical criteria; CRP/ESR elevated; 5/6 supplemental labs positive). "
                "Portable bedside TTE scheduled for baseline LMCA/LAD/RCA Z-scores. "
                f"{_cm_red('Positive Echo defined by LAD or RCA Z-score ≥ 2.5, coronary artery aneurysm, or ≥ 3 suggestive features')}. "
                f"{_cm_red('Do NOT hold IVIG infusion while awaiting baseline echo')} — treatment already indicated by ≥3 supplemental labs.'"
            ),
            "Echo documents coronary baseline, but Incomplete KD treatment is already triggered by the supplemental lab gate.",
        ),
        "d4": _ev(
            "📄 Source: IVIG Reaction Protocol & ID/Cards Note (07:10)",
            "💊 Inpatient Pharmacy & ID/Cardiology Co-Management Note — IVIG 2 g/kg (26 g) Infusion & Reaction Protocol · 07:10",
            _leo_ivig_reaction_evidence_html(),
            "Bedside IVIG reaction recognition + titration protocol for Incomplete KD; escalate ID/Cards for IVIG-refractory fever ≥36h post-infusion.",
        ),
        "d5": _ev(
            "📄 Source: Inflammatory & Supplemental Labs (05:00)",
            "📈 Fever Curve / 36h Post-IVIG Refractory Clock",
            (
                f"{_cm_red('Fever Duration: Day 6 unexplained fever, Tmax 39.4°C (102.9°F)')}. "
                f"{_cm_red('✅ CRP: 14.2 mg/dL [CRITICAL HIGH — AHA cutoff ≥ 3.0 mg/dL]')}. "
                "Continue q4h temps; after IVIG completes, start 36h refractory-fever clock (persistent fever ≥36h → 2nd-line rescue)."
            ),
            "Baseline CRP/ESR also track post-IVIG inflammatory response in Incomplete KD.",
        ),
        "d6": _ev(
            "📄 Source: H&P & 2/5 Exam Note (06:00)",
            "👨‍👩‍👧 Family Counseling — Incomplete KD / IVIG / Follow-up Echos",
            (
                f"Family counseled that Leo has Incomplete KD: {_cm_red('Fever Duration: Day 6 unexplained fever, Tmax 39.4°C (102.9°F)')} + "
                f"{_cm_red('(1) ✅ Bilateral non-exudative bulbar conjunctival injection with limbal sparing (Day 2)')} + "
                f"{_cm_red('(2) ✅ Diffuse maculopapular polymorphous truncal & groin rash (Day 3)')}, "
                "confirmed by labs — why IVIG/ASA still start today, and why serial echos are needed even if Week 1 study is normal."
            ),
            "Clear Incomplete vs Complete KD explanation improves adherence when classic mucocutaneous features are incomplete.",
        ),
        "n1": _ev(
            "📄 Source: IVIG Reaction Protocol & ID/Cards Note (07:10)",
            "💊 Inpatient Pharmacy & ID/Cardiology Co-Management Note — IVIG 2 g/kg (26 g) Infusion & Reaction Protocol · 07:10",
            _leo_ivig_reaction_evidence_html(),
            "Night cross-cover owns IVIG titration, reaction recognition (mild → anaphylaxis → AMS → volume/hemolysis/AKI), and refractory-fever escalation.",
        ),
        "n2": _ev(
            "📄 Source: Inflammatory & Supplemental Labs (05:00)",
            "📈 Ongoing Fever Day Count / Irritability Watch",
            (
                f"{_cm_red('Fever Duration: Day 6 unexplained fever, Tmax 39.4°C (102.9°F)')}. "
                f"{_cm_red('✅ CRP: 14.2 mg/dL [CRITICAL HIGH — AHA cutoff ≥ 3.0 mg/dL]')}. "
                "Document ongoing fever day count. Call if hypotension or irritability escalates."
            ),
            "Clinical deterioration overnight may signal shock/MIS-C mimic or infusion complication.",
        ),
        "n3": _ev(
            "📄 Source: Inflammatory & Supplemental Labs (05:00)",
            "💊 High-Dose ASA First-Dose Safety Check",
            (
                f"{_cm_red('✅ CRP: 14.2 mg/dL [CRITICAL HIGH — AHA cutoff ≥ 3.0 mg/dL]')} · "
                f"{_cm_red('✅ ESR: 78 mm/h [HIGH — AHA cutoff ≥ 40 mm/h]')}. "
                "ASA 260 mg PO q6h staged with IVIG for Incomplete KD. Watch for bleeding / GI upset after first doses."
            ),
            "Night team confirms anti-inflammatory ASA start and monitors early adverse effects.",
        ),
        "n4": _ev(
            "📄 Source: Pediatric Cardiology Consult (06:45)",
            "🫀 Echo Pending Overnight — AM Cardiology Slot Handoff",
            (
                f"{_cm_red('Positive Echo defined by LAD or RCA Z-score ≥ 2.5, coronary artery aneurysm, or ≥ 3 suggestive features')}. "
                f"{_cm_red('Do NOT hold IVIG infusion while awaiting baseline echo')}. "
                "If still pending overnight → hand off to AM cardiology slot."
            ),
            "Explicit echo handoff prevents lost imaging while Incomplete KD treatment proceeds.",
        ),
    },
}


def ehr_evidence_card_html(ev: dict) -> str:
    """High-contrast EHR evidence card for checklist source popovers.

    Evidence may include trusted inline HTML highlight spans
    (``.crit-met-red`` / ``.crit-met-green`` / ``.crit-absent``).
    """
    return (
        '<div class="ehr-ev-card">'
        f'<div class="ehr-ev-header">{html.escape(ev["header"])}</div>'
        '<div class="ehr-ev-section">Verbatim EHR excerpt</div>'
        f'<div class="ehr-ev-body">{ev["evidence"]}</div>'
        '<div class="ehr-ev-section">Protocol / clinical link</div>'
        f'<div class="ehr-ev-why">{html.escape(ev["why"])}</div>'
        "</div>"
    )


def _short_ehr_source_label(button: str) -> str:
    """Crisp ≤10-char badges so checklist source pills never truncate."""
    pairs = (
        ("Hr-48 MTX", "📄 Lab"),
        ("Hr-54 MTX", "📄 Lab"),
        ("BMP & MAR", "📄 MAR"),
        ("Point-of-Care Urine", "📄 Urine"),
        ("Onc Pharm", "📄 Pharm"),
        ("Med Rec", "📄 MedRec"),
        ("Family Update", "📄 Family"),
        ("Family Teaching", "📄 Family"),
        ("Final Urine Cx", "📄 Micro"),
        ("Blood Cx & Renal", "📄 Imaging"),
        ("Vitals & Nursing", "📄 Vitals"),
        ("DC Planning", "📄 DC"),
        ("Overnight Telemetry", "📄 Tele"),
        ("Refeeding Electrolyte", "📄 Lytes"),
        ("Registered Dietitian", "📄 Nutrition"),
        ("H&P & 2/5", "📄 Exam"),
        ("Inflammatory & Supplemental", "📄 Labs"),
        ("Pediatric Cardiology", "📄 Cards"),
        ("IVIG Reaction Protocol", "📄 IVIG"),
    )
    for needle, short in pairs:
        if needle in button:
            return short
    return "📄 Source"


def checklist_source_popover(
    p: dict,
    tid: str,
    cite_key: str,
    *,
    loc: str,
) -> None:
    """Task-specific EHR evidence popover, with citation fallback."""
    ev = CHECKLIST_EHR_EVIDENCE.get(p["id"], {}).get(tid)
    if not ev:
        citation_pill(p, cite_key, loc=loc)
        return
    pop = st.popover(
        _short_ehr_source_label(ev["button"]),
        width="stretch",
        key=f"ehr_src_{p['id']}_{tid}_{loc}",
        on_change="rerun",
    )
    with pop:
        if pop.open:
            st.html(ehr_evidence_card_html(ev))


def reset_tasks(pid: str, tasks: list) -> None:
    """Clear Day+Night checkboxes and all staged orders for this patient."""
    p = next((x for x in PATIENTS if x["id"] == pid), None)
    all_tasks = list(tasks)
    if p:
        # Reset both shift checklists so demo restarts cleanly
        all_tasks = list(p.get("day_tasks", [])) + list(p.get("night_tasks", []))
    seen: set[str] = set()
    for tid, *_rest in all_tasks:
        if tid in seen:
            continue
        seen.add(tid)
        st.session_state[day_key(pid, tid)] = False
        st.session_state[night_key(pid, tid)] = False
    st.session_state[_staged_orders_key(pid)] = {}
    st.session_state.pop(f"order_committed_{pid}", None)
    st.session_state.pop(f"status_overlay_{pid}", None)
    # Clear smart custom tasks + simulated result flips for this patient
    customs = st.session_state.setdefault("custom_tasks", {})
    customs[pid] = []
    for k in list(st.session_state.keys()):
        if isinstance(k, str) and (
            k.startswith(f"sim_result_{pid}_")
            or k.startswith(f"custom_chk_{pid}_")
            or k.startswith(f"new_task_input_{pid}_")
        ):
            st.session_state.pop(k, None)
    # Clear stage widget flags for this patient
    for k in list(st.session_state.keys()):
        if isinstance(k, str) and (
            k.startswith("staged_flag_") and pid in k
            or k.startswith("ft_") and pid in k and k.endswith("_sign")
        ):
            st.session_state.pop(k, None)


# ---------------------------------------------------------------------------
# Smart checklist: keyword → EHR auto-linker
# ---------------------------------------------------------------------------
def _smart_src(
    *,
    label: str,
    badge: str,
    tier: str,
    summary: str,
    pending: bool = False,
    pending_label: str = "",
    simulated: dict | None = None,
) -> dict:
    return {
        "label": label,
        "badge": badge,
        "tier": tier,
        "summary": summary,
        "pending": pending,
        "pending_label": pending_label,
        "simulated": simulated or {},
    }


# Ordered keyword groups (specific drug/imaging before short electrolyte tokens)
EHR_SMART_LINK_GROUPS: list[dict] = [
    {
        "key": "mtx",
        "patterns": [r"\bmethotrexate\b", r"\bbleyer\b", r"\bleucovorin\b", r"\bmtx\b"],
        "patients": {
            "emma": _smart_src(
                label="MTX",
                badge="MTX (4.20 🔴)",
                tier="red",
                summary=(
                    "🧪 TDM Lab: "
                    + _cm_red(
                        "✅ Serum MTX (Hr 48): 4.20 µmol/L [CRITICAL HIGH — "
                        "COG AALL1131 Hr-48 Target ≤ 0.40 µmol/L; 10.5x cutoff]"
                    )
                    + " · Next Draw: Hr-54 due at 14:00"
                ),
                pending=True,
                pending_label="⏳ Pending: Hour-54 STAT MTX draw due 14:00",
                simulated={
                    "badge": "MTX (1.85 🟡)",
                    "tier": "amber",
                    "summary": (
                        "🔔 RESULT POPULATED JUST NOW — Hr-54 Serum MTX = 1.85 µmol/L "
                        "(down from 4.20; still above 0.10 clear threshold; continue "
                        "escalated leucovorin; Voraxaze threshold not met)"
                    ),
                },
            ),
        },
    },
    {
        "key": "voraxaze",
        "patterns": [r"\bvoraxaze\b", r"\bglucarpidase\b"],
        "patients": {
            "emma": _smart_src(
                label="Voraxaze",
                badge="Voraxaze standby 🟢",
                tier="green",
                summary=(
                    "💊 Onc Pharm: "
                    + _cm_red(
                        "✅ 2 vials of Glucarpidase (Voraxaze 50 U/kg = 1,300 Units IV) "
                        "verified on standby if Hr-54 MTX > 2.0–5.0 µmol/L with "
                        "worsening Cr"
                    )
                ),
            ),
        },
    },
    {
        "key": "ivig",
        "patterns": [r"\bivig\b", r"\basa\b", r"\baspirin\b"],
        "patients": {
            "leo": _smart_src(
                label="IVIG/ASA",
                badge="IVIG 26 g + ASA 🔴",
                tier="red",
                summary=(
                    "⚡ Incomplete KD treatment gate: IVIG 2 g/kg (26 g) IV over "
                    "10–12h + High-Dose ASA 260 mg PO q6h — triggered by 5/6 "
                    "supplemental labs. "
                    + _cm_red(
                        "Do NOT hold IVIG infusion while awaiting baseline echo"
                    )
                ),
            ),
        },
    },
    {
        "key": "echo",
        "patterns": [
            r"\bechocardiogram\b",
            r"\becho\b",
            r"\bz[- ]?score\b",
            r"\bcoronary\b",
            r"\blad\b",
            r"\brca\b",
            r"\baneurysm\b",
            r"\bcards\b",
            r"\bcardiology\b",
        ],
        "patients": {
            "leo": _smart_src(
                label="Echo",
                badge="Echo ⏳ Pending",
                tier="amber",
                summary=(
                    "🫀 Pediatric TTE ordered — baseline LMCA/LAD/RCA Z-scores "
                    "pending. "
                    + _cm_red(
                        "Positive Echo defined by LAD or RCA Z-score ≥ 2.5, "
                        "coronary artery aneurysm, or ≥ 3 suggestive features"
                    )
                    + " · "
                    + _cm_red(
                        "Do NOT hold IVIG infusion while awaiting baseline echo"
                    )
                ),
                pending=True,
                pending_label="⏳ Pending: Baseline transthoracic echocardiogram",
                simulated={
                    "badge": "Echo (LAD Z +2.6 🔴)",
                    "tier": "red",
                    "summary": (
                        "🔔 RESULT POPULATED JUST NOW — Pediatric Transthoracic "
                        "Echocardiogram: LVEF 64% (Normal) · LMCA Z-score +1.4 · "
                        + _cm_red(
                            "Proximal LAD Z-score +2.6 (🔴 POSITIVE ECHO ≥2.5 AHA "
                            "cutoff: 2.4 mm dilation)"
                        )
                        + " · RCA Z-score +1.9 · Trace pericardial effusion, no "
                        "mitral regurgitation → Confirms coronary involvement; "
                        "continue IVIG 2 g/kg + High-Dose ASA"
                    ),
                },
            ),
            "chloe": _smart_src(
                label="Echo/ECG",
                badge="ECG/Echo bradycardia 🔴",
                tier="red",
                summary=(
                    "🫀 Cardiology / Echo & ECG Status: "
                    + _cm_red(
                        "✅ Sleeping Heart Rate Nadir: 38 bpm at 03:45 "
                        "[CRITICAL BRADYCARDIA — Cutoff < 45 bpm]"
                    )
                    + ", QTc 448 ms (borderline), normal structural anatomy"
                ),
            ),
        },
    },
    {
        "key": "ecg",
        "patterns": [
            r"\bekg\b",
            r"\becg\b",
            r"\btelemetry\b",
            r"\bbradycardia\b",
            r"\borthostatic\b",
            r"\bhr\b",
        ],
        "patients": {
            "chloe": _smart_src(
                label="ECG/Telemetry",
                badge="HR 38 🔴 · Ortho+ 🔴",
                tier="red",
                summary=(
                    "📈 12-Lead ECG & Telemetry (06:10): "
                    + _cm_red(
                        "✅ Sleeping Heart Rate Nadir: 38 bpm at 03:45 "
                        "[CRITICAL BRADYCARDIA — Cutoff < 45 bpm]"
                    )
                    + " · QTc 448 ms · Flat T-waves in V4-V6 · "
                    + _cm_red(
                        "✅ Orthostatic ΔHR +28 bpm (Supine 44 -> Standing 72 bpm; "
                        "meets ≥ 20 bpm cutoff)"
                    )
                ),
            ),
        },
    },
    {
        "key": "phos_mg",
        "patterns": [
            r"\bphosphorus\b",
            r"\bphosphate\b",
            r"\bphos\b",
            r"\bmagnesium\b",
            r"\bmag\b",
            r"\bmg\b",
            r"\bcalcium\b",
            r"\bca\b",
        ],
        "patients": {
            "chloe": _smart_src(
                label="Phos/Mg",
                badge="Phos 1.9 🔴 · Mg 1.6 🔴",
                tier="red",
                summary=(
                    "🧪 Refeeding Electrolytes (05:15): "
                    + _cm_red(
                        "✅ Serum Phosphorus: 1.9 mg/dL [CRITICAL LOW — "
                        "Refeeding Cutoff < 2.5 mg/dL]"
                    )
                    + " (dropped from 3.1 → 2.4 → 1.9) · "
                    + _cm_red("✅ Magnesium: 1.6 mg/dL [LOW < 1.8]")
                    + " · "
                    + _cm_red("✅ Potassium: 3.3 mEq/L [LOW < 3.5]")
                    + " · Ca 8.9 mg/dL (🟢) · Next Recheck: Due 4h post-IV NaPhos"
                ),
                pending=True,
                pending_label="⏳ Pending: 4h post-IV NaPhos Phos/K/Mg recheck",
                simulated={
                    "badge": "Phos 2.6 🟢",
                    "tier": "green",
                    "summary": (
                        "🔔 RESULT POPULATED JUST NOW — Post-infusion Phos 2.6 mg/dL "
                        "(🟢 ≥2.5 target) · K 3.6 mEq/L (🟢) · Mg 1.9 mg/dL (🟢). "
                        "Continue hold at 1,600 kcal; telemetry until HR stable."
                    ),
                },
            ),
            "emma": _smart_src(
                label="Extended lytes",
                badge="Phos/Mg/Ca 🟢",
                tier="green",
                summary=(
                    "🧪 Extended Lytes: Phos 4.1 mg/dL (🟢) · Mg 2.0 mg/dL (🟢) · "
                    "Ca 9.2 mg/dL (🟢)"
                ),
            ),
            "maya": _smart_src(
                label="Extended lytes",
                badge="Phos/Mg/Ca 🟢",
                tier="green",
                summary=(
                    "🧪 Extended Lytes: Phos 4.0 mg/dL (🟢) · Mg 2.1 mg/dL (🟢) · "
                    "Ca 9.4 mg/dL (🟢)"
                ),
            ),
            "leo": _smart_src(
                label="Extended lytes",
                badge="Phos/Mg/Ca 🟢",
                tier="green",
                summary=(
                    "🧪 Extended Lytes: Phos 4.2 mg/dL (🟢) · Mg 2.0 mg/dL (🟢) · "
                    "Ca 9.1 mg/dL (🟢)"
                ),
            ),
        },
    },
    {
        "key": "bmp",
        "patterns": [
            r"\bcreatinine\b",
            r"\belectrolyte\b",
            r"\bsodium\b",
            r"\bpotassium\b",
            r"\bbicarb\b",
            r"\brenal\b",
            r"\bbmp\b",
            r"\bchem\b",
            r"\baki\b",
            r"\bbun\b",
            r"\bna\b",
            r"\bk\b",
            r"\bcl\b",
            r"\bco2\b",
            r"\bcr\b",
        ],
        "patients": {
            "emma": _smart_src(
                label="BMP",
                badge="Cr 0.68 🔴 · K 4.1 🟢",
                tier="red",
                summary=(
                    "📊 BMP (06:15): Na 139 mEq/L (🟢) · K 4.1 mEq/L (🟢) · "
                    "Cl 102 mEq/L (🟢) · CO₂ 26 mEq/L (🟢) · BUN 18 mg/dL · "
                    + _cm_red(
                        "✅ Serum Creatinine: 0.68 mg/dL [HIGH — Baseline 0.40 "
                        "mg/dL at Hr 0; +70% rise meets KDIGO Stage 1 AKI ≥50% cutoff]"
                    )
                ),
            ),
            "maya": _smart_src(
                label="BMP",
                badge="Cr 0.34 🟢",
                tier="green",
                summary=(
                    "📊 BMP (05:30): Na 138 mEq/L (🟢) · K 4.2 mEq/L (🟢) · "
                    "CO₂ 22 mEq/L (🟢) · Cr 0.34 mg/dL (🟢 improved from 0.48)"
                ),
            ),
            "chloe": _smart_src(
                label="Chem",
                badge="K 3.3 🔴",
                tier="red",
                summary=(
                    "📊 Refeeding Chem Panel (05:15): Na 136 mEq/L (🟢) · "
                    + _cm_red("✅ Potassium: 3.3 mEq/L [LOW < 3.5]")
                    + " · Cl 100 mEq/L · CO₂ 25 mEq/L · Glucose 76 mg/dL · "
                    "Cr 0.52 mg/dL"
                ),
            ),
            "leo": _smart_src(
                label="BMP/Hepatic",
                badge="Alb 2.7 🔴 · ALT 68 🔴",
                tier="red",
                summary=(
                    "📊 BMP & Hepatic Panel (05:00): Na 133 mEq/L "
                    "(🟡 Mild hyponatremia) · K 4.0 mEq/L (🟢) · "
                    "Cr 0.31 mg/dL (🟢) · "
                    + _cm_red("(3) ✅ Albumin 2.7 g/dL (≤3.0)")
                    + " · "
                    + _cm_red("(4) ✅ ALT 68 U/L (elevated)")
                ),
            ),
        },
    },
    {
        "key": "urine",
        "patterns": [
            r"\bdipstick\b",
            r"\bpyuria\b",
            r"\burine\b",
            r"\bua\b",
            r"\bph\b",
        ],
        "patients": {
            "emma": _smart_src(
                label="Urine pH",
                badge="pH 6.8 🔴",
                tier="red",
                summary=(
                    "🚽 Bedside Urine Dipstick (06:30): "
                    + _cm_red(
                        "✅ Urine pH: 6.8 [CRITICAL LOW — HD-MTX Protocol "
                        "Target ≥ 7.0]"
                    )
                    + " · SpGrav 1.012 · Repeat dipstick due 1h post-NaHCO₃ bolus"
                ),
            ),
            "maya": _smart_src(
                label="UA",
                badge="UA improving 🟢",
                tier="green",
                summary=(
                    "🚽 Admission UA & Microscopy: >50 WBC/hpf, Positive "
                    "Leukocyte Esterase & Nitrites → Resolved clinically"
                ),
            ),
            "leo": _smart_src(
                label="UA",
                badge="UA 24 WBC 🔴",
                tier="red",
                summary=(
                    "🚽 Urinalysis (05:00): "
                    + _cm_red(
                        "(5) ✅ Urinalysis 24 WBC/hpf (sterile pyuria ≥10 WBC/hpf)"
                    )
                    + " · Urine Cx negative"
                ),
            ),
        },
    },
    {
        "key": "inflam",
        "patterns": [
            r"\binflammatory\b",
            r"\balbumin\b",
            r"\banemia\b",
            r"\bplatelet\b",
            r"\bcrp\b",
            r"\besr\b",
            r"\bwbc\b",
            r"\bcbc\b",
            r"\bhgb\b",
            r"\bplt\b",
            r"\balt\b",
        ],
        "patients": {
            "leo": _smart_src(
                label="Inflammatory/§",
                badge="CRP 14.2 🔴 · ESR 78 🔴",
                tier="red",
                summary=(
                    "🧪 AHA Inflammatory & Supplemental Panel (05:00): "
                    + _cm_red(
                        "✅ CRP: 14.2 mg/dL [CRITICAL HIGH — AHA cutoff ≥ 3.0 mg/dL]"
                    )
                    + " · "
                    + _cm_red(
                        "✅ ESR: 78 mm/h [HIGH — AHA cutoff ≥ 40 mm/h]"
                    )
                    + " · "
                    + _cm_red("(1) ✅ WBC 17.4k/µL (≥15k)")
                    + " · "
                    + _cm_red("(2) ✅ Hgb 9.8 g/dL (anemia for age)")
                    + " · "
                    + _cm_red("(3) ✅ Albumin 2.7 g/dL (≤3.0)")
                    + " · "
                    + _cm_red("(4) ✅ ALT 68 U/L (elevated)")
                    + " · "
                    + _cm_red(
                        "(5) ✅ Urinalysis 24 WBC/hpf (sterile pyuria ≥10 WBC/hpf)"
                    )
                    + " · Platelets: 390k/µL (normal on Day 6)"
                ),
            ),
            "maya": _smart_src(
                label="CBC",
                badge="WBC 9.4k 🟢",
                tier="green",
                summary=(
                    "🧪 CBC Trend: WBC 9.4k/µL (🟢 improved from 18.2k on "
                    "admission) · Hgb 11.8 g/dL · Plt 285k/µL"
                ),
            ),
            "emma": _smart_src(
                label="CBC",
                badge="ANC 1.4k 🟢",
                tier="green",
                summary=(
                    "🧪 CBC (06:15): WBC 3.8k/µL · ANC 1,420/µL (🟢 ≥500) · "
                    "Hgb 10.4 g/dL · Plt 112k/µL (🟢 ≥75k)"
                ),
            ),
        },
    },
    {
        "key": "micro",
        "patterns": [
            r"\bsensitivities\b",
            r"\bcephalexin\b",
            r"\bceftriaxone\b",
            r"\bculture\b",
            r"\bmicro\b",
            r"\bucx\b",
            r"\bbcx\b",
            r"\bmic\b",
            r"\bcx\b",
        ],
        "patients": {
            "maya": _smart_src(
                label="Micro",
                badge="E. coli S · BCx− 🟢",
                tier="green",
                summary=(
                    "🦠 Final Microbiology (05:30): "
                    + _cm_green(
                        "✅ >100,000 CFU/mL Pansensitive E. coli — Cefazolin "
                        "[S, MIC ≤ 1 µg/mL — predicts oral Cephalexin susceptibility]"
                    )
                    + " · "
                    + _cm_green(
                        "✅ 48h Blood Culture: No growth to date (Negative)"
                    )
                ),
            ),
        },
    },
    {
        "key": "imaging",
        "patterns": [
            r"\brenals?\s*us\b",
            r"\bultrasound\b",
            r"\bimaging\b",
            r"\bus\b",
        ],
        "patients": {
            "maya": _smart_src(
                label="Renal US",
                badge="Renal US 🟢",
                tier="green",
                summary=(
                    "🩻 Renal & Bladder Ultrasound (05:45): "
                    + _cm_green(
                        "✅ Renal Ultrasound: Normal bilateral kidneys, no "
                        "hydronephrosis or abscess"
                    )
                ),
            ),
        },
    },
    {
        "key": "vitals",
        "patterns": [
            r"\bvitals?\b",
            r"\bfever\b",
            r"\btemp\b",
            r"\bi\s*&\s*o\b",
            r"\bweight\b",
            r"\bfluid\b",
            r"\bbp\b",
        ],
        "patients": {
            "emma": _smart_src(
                label="Vitals/I&O",
                badge="Wt +0.4 · I&O +420",
                tier="amber",
                summary=(
                    "📈 Vitals/I&O: T 36.9°C · HR 92 · BP 98/58 (in-band) · "
                    "Net 24h I&O +420 mL · Weight 26.4 kg (+0.4 from baseline) "
                    "on hyperhydration trajectory"
                ),
            ),
            "maya": _smart_src(
                label="Vitals",
                badge="Afebrile 30h 🟢",
                tier="green",
                summary=(
                    "📈 Vitals: "
                    + _cm_green(
                        "✅ 30 hours afebrile (Tmax 37.1°C / 98.8°F; meets ≥ 24h "
                        "afebrile cutoff)"
                    )
                    + " · HR 98 · BP 92/56 · "
                    + _cm_green(
                        "✅ Tolerating 100% PO fluids (1,150 mL/24h, 0 emesis)"
                    )
                    + " · UOP 2.4 mL/kg/hr"
                ),
            ),
            "chloe": _smart_src(
                label="Vitals",
                badge="HR nadir 38 🔴",
                tier="red",
                summary=(
                    "📈 Vitals/Telemetry: "
                    + _cm_red(
                        "✅ Sleeping Heart Rate Nadir: 38 bpm at 03:45 "
                        "[CRITICAL BRADYCARDIA — Cutoff < 45 bpm]"
                    )
                    + " · "
                    + _cm_red(
                        "✅ Orthostatic ΔHR +28 bpm (Supine 44 -> Standing 72 bpm; "
                        "meets ≥ 20 bpm cutoff)"
                    )
                    + " · "
                    + _cm_red(
                        "✅ Severe Protein-Calorie Malnutrition (71% median BMI) — "
                        "Hold caloric advancement at 1,600 kcal/day until "
                        "Phos > 2.5 mg/dL"
                    )
                ),
            ),
            "leo": _smart_src(
                label="Fever/Vitals",
                badge="Day 6 Tmax 39.4 🔴",
                tier="red",
                summary=(
                    "📈 Vitals: "
                    + _cm_red(
                        "Fever Duration: Day 6 unexplained fever, Tmax 39.4°C "
                        "(102.9°F)"
                    )
                    + " · HR 142 · irritable · BP in-band for age"
                ),
            ),
        },
    },
]


def match_task_to_ehr_results(patient_id: str, task_text: str) -> list[dict]:
    """Case-insensitive keyword match → per-patient EHR source cards."""
    text = (task_text or "").lower()
    matched: list[dict] = []
    seen: set[str] = set()
    for group in EHR_SMART_LINK_GROUPS:
        if group["key"] in seen:
            continue
        hit = any(re.search(pat, text, flags=re.I) for pat in group["patterns"])
        if not hit:
            continue
        src = group["patients"].get(patient_id)
        if not src:
            continue
        seen.add(group["key"])
        matched.append({"group_key": group["key"], **src})
    return matched


def _ensure_custom_tasks() -> dict:
    return st.session_state.setdefault("custom_tasks", {})


def add_smart_custom_task(pid: str, shift: str, text: str) -> None:
    text = (text or "").strip()
    if not text:
        return
    bag = _ensure_custom_tasks().setdefault(pid, [])
    tid = f"ct_{uuid.uuid4().hex[:8]}"
    bag.append(
        {
            "id": tid,
            "text": text,
            "checked": False,
            "shift": shift,
            "matched_sources": match_task_to_ehr_results(pid, text),
        }
    )


def delete_smart_custom_task(pid: str, tid: str) -> None:
    bag = _ensure_custom_tasks().setdefault(pid, [])
    _ensure_custom_tasks()[pid] = [t for t in bag if t["id"] != tid]
    st.session_state.pop(f"custom_chk_{pid}_{tid}", None)
    for k in list(st.session_state.keys()):
        if isinstance(k, str) and k.startswith(f"sim_result_{pid}_{tid}_"):
            st.session_state.pop(k, None)


def _smart_source_live(pid: str, task_id: str, src: dict) -> dict:
    """Return live or simulated source payload for display."""
    sim_key = f"sim_result_{pid}_{task_id}_{src['group_key']}"
    if src.get("pending") and st.session_state.get(sim_key):
        sim = src.get("simulated") or {}
        return {
            **src,
            "badge": sim.get("badge", src["badge"]),
            "tier": sim.get("tier", "green"),
            "summary": sim.get("summary", src["summary"]),
            "populated": True,
        }
    return {**src, "populated": False}


def render_smart_link_popover(pid: str, task: dict, *, loc: str) -> None:
    """Popover showing auto-linked EHR feeds + simulate pending results."""
    sources = task.get("matched_sources") or []
    if not sources:
        st.caption("No EHR keywords detected")
        return
    live = [_smart_source_live(pid, task["id"], s) for s in sources]
    badge_bits = " · ".join(s["badge"] for s in live)
    label = f"🔗 Auto-Linked: {badge_bits}"
    if len(label) > 72:
        label = f"🔗 Auto-Linked: {len(live)} EHR result(s)"
    pop = st.popover(
        label,
        help="Auto-linked EHR lab/study feed for keywords in this task",
        width="stretch",
        key=f"smart_pop_{pid}_{task['id']}_{loc}",
        on_change="rerun",
    )
    with pop:
        if not pop.open:
            return
        st.markdown("**⚡ Auto-Linked EHR Result Feed**")
        for src in live:
            tier = src.get("tier", "amber")
            border = {
                "red": "#fca5a5",
                "amber": "#fcd34d",
                "green": "#6ee7b7",
            }.get(tier, "#cbd5e1")
            bg = {
                "red": "#fef2f2",
                "amber": "#fffbeb",
                "green": "#ecfdf5",
            }.get(tier, "#f8fafc")
            status = (
                "🔔 RESULT POPULATED JUST NOW"
                if src.get("populated")
                else (
                    src.get("pending_label")
                    if src.get("pending")
                    else "✅ Available result"
                )
            )
            st.html(
                f'<div class="ehr-ev-card" style="background:{bg};'
                f'border-color:{border};margin-bottom:8px;">'
                f'<div class="ehr-ev-header">{html.escape(src["label"])} — '
                f'{html.escape(src["badge"])}</div>'
                f'<div class="ehr-ev-section">{html.escape(status)}</div>'
                f'<div class="ehr-ev-body">{src["summary"]}</div>'
                "</div>"
            )
            if src.get("pending") and not src.get("populated"):
                sim_key = f"sim_result_{pid}_{task['id']}_{src['group_key']}"
                if st.button(
                    f"🔄 Simulate Result Populating Now — {src['label']}",
                    key=f"sim_btn_{pid}_{task['id']}_{src['group_key']}_{loc}",
                    type="primary",
                    width="stretch",
                ):
                    st.session_state[sim_key] = True
                    st.rerun()


def render_smart_task_composer(p: dict, *, is_night: bool) -> None:
    """Input bar that creates custom tasks with EHR auto-links."""
    shift = "night" if is_night else "day"
    pid = p["id"]
    in_key = f"new_task_input_{pid}_{shift}"
    btn_key = f"add_task_btn_{pid}_{shift}"
    c1, c2 = st.columns([0.74, 0.26], vertical_alignment="bottom")
    with c1:
        st.text_input(
            "Add smart handoff task",
            key=in_key,
            label_visibility="collapsed",
            placeholder=(
                "➕ Add custom task (e.g., 'Follow up on Na, K, MTX, or Echo')"
            ),
            help=(
                "Auto-links keywords: Na, K, Cr, Phos, Mg, MTX, pH, CRP, ESR, "
                "WBC, Hgb, Plt, Albumin, ALT, UA, Cx, Echo, ECG, HR, BP, Fever, "
                "Voraxaze, IVIG"
            ),
        )
    with c2:
        if st.button(
            "➕ Add Task",
            key=btn_key,
            width="stretch",
            type="secondary",
        ):
            add_smart_custom_task(pid, shift, st.session_state.get(in_key, ""))
            st.session_state[in_key] = ""
            st.rerun()


def render_smart_custom_tasks(p: dict, *, is_night: bool) -> None:
    """Render custom auto-linked checklist items for this shift."""
    shift = "night" if is_night else "day"
    pid = p["id"]
    bag = [t for t in _ensure_custom_tasks().get(pid, []) if t.get("shift") == shift]
    if not bag:
        return
    st.caption("Smart custom tasks (keyword-linked to EHR)")
    for task in bag:
        chk_key = f"custom_chk_{pid}_{task['id']}"
        if chk_key not in st.session_state:
            st.session_state[chk_key] = bool(task.get("checked"))
        row = st.columns([0.70, 0.22, 0.08], gap="small", vertical_alignment="top")
        with row[0]:
            checked = st.checkbox(task["text"], key=chk_key)
            task["checked"] = checked
        with row[1]:
            render_smart_link_popover(pid, task, loc=shift)
        with row[2]:
            if st.button(
                "🗑️",
                key=f"del_ct_{pid}_{task['id']}_{shift}",
                help="Delete custom task",
                width="stretch",
            ):
                delete_smart_custom_task(pid, task["id"])
                st.rerun()


def _delta_html(current: str, change: str) -> str:
    """Current Running Order → Recommended Change block for flowchart nodes."""
    return (
        '<div class="ford-delta">'
        f'<div class="ford-cur"><strong>Current Running Order:</strong> '
        f"{current}</div>"
        f'<div class="ford-chg"><strong>Recommended Change:</strong> '
        f"{change}</div>"
        "</div>"
    )


def _ah_delta_pill(text: str, *, tone: str = "crit") -> str:
    cls = {
        "crit": "ah-delta-crit",
        "ok": "ah-delta-ok",
        "warn": "ah-delta-warn",
    }.get(tone, "ah-delta-crit")
    return f'<span class="{cls}">{html.escape(text)}</span>'


def mar_detail_card_html(
    *,
    addressed: bool,
    sections: list[dict],
    title: str = "💊 Active Intervention & MAR Administration Detail",
) -> str:
    """High-contrast MAR card for telemetry tile popovers."""
    tone = "" if addressed else " pending"
    blocks: list[str] = []
    for i, sec in enumerate(sections):
        heading = sec.get("heading")
        rows_html = "".join(
            '<div class="mar-detail-row">'
            f'<div class="mar-detail-key">{html.escape(k)}</div>'
            f'<div class="mar-detail-val">{html.escape(v)}</div>'
            "</div>"
            for k, v in sec.get("rows", [])
        )
        wrap = (
            f'<div class="mar-detail-section">'
            f'<div class="mar-detail-heading">{html.escape(heading)}</div>'
            f"{rows_html}</div>"
            if heading and i > 0
            else (
                (
                    f'<div class="mar-detail-heading">'
                    f"{html.escape(heading)}</div>"
                    if heading
                    else ""
                )
                + rows_html
            )
        )
        blocks.append(wrap)
    return (
        f'<div class="mar-detail-card{tone}">'
        f'<div class="mar-detail-title">{html.escape(title)}</div>'
        + "".join(blocks)
        + "</div>"
    )


def render_apple_health_tile(
    *,
    category: str,
    tier: str,
    timestamp: str = "",
    timestamp_html: str | None = None,
    value: str = "",
    unit: str = "",
    value_html: str | None = None,
    unit_html: str | None = None,
    context_html: str,
    value_critical: bool | None = None,
    addressed: bool = False,
) -> None:
    """Apple Health-style metric body; flips to green when addressed in handoff."""
    base_tier = tier if tier in ("red", "amber", "green") else "amber"
    # Addressed critical tiles keep the abnormal figure but go emerald in chrome
    tier_cls = "green" if addressed else base_tier
    addressed_cls = " addressed" if addressed else ""
    # Short label only — never append "· Addressed" (truncates against timestamp)
    cat_label = f"✓ {category}" if addressed else category
    crit = (
        value_critical
        if value_critical is not None
        else (base_tier == "red" and not addressed)
    )
    # Keep pathogen / critical numerals visible even after addressing
    if value_critical is True:
        crit = True
    value_cls = "ah-tile-value crit" if crit else "ah-tile-value"
    ts_block = (
        timestamp_html
        if timestamp_html is not None
        else f'<span class="ah-tile-ts">{html.escape(timestamp)}</span>'
    )
    if value_html is not None:
        hero_value = value_html
    else:
        hero_value = (
            f'<span class="{value_cls}">{html.escape(value)}</span>'
        )
    if unit_html is not None:
        hero_unit = unit_html
    else:
        hero_unit = (
            f'<span class="ah-tile-unit">{html.escape(unit)}</span>'
            if unit
            else ""
        )
    st.html(
        f"""
        <div class="ah-tile-body tier-{html.escape(tier_cls)}{addressed_cls}">
          <div class="ah-tile-head">
            <div class="ah-tile-cat">
              <span class="ah-dot" aria-hidden="true"></span>
              <span class="ah-cat-label">{html.escape(cat_label)}</span>
            </div>
            {ts_block}
          </div>
          <div class="ah-tile-hero">
            {hero_value}
            {hero_unit}
          </div>
          <div class="ah-tile-ctx">{context_html}</div>
        </div>
        """
    )


def render_compact_metric(
    title: str,
    value: str,
    tier: str,
    caption: str,
    *,
    value_size: str = "1.55rem",
    value_color: str | None = None,
) -> None:
    """Backward-compatible shim → Apple Health tile body."""
    del value_size, value_color
    # Split "4.20 µmol/L" style values into figure + unit when possible
    parts = value.split(" ", 1)
    figure, unit = (parts[0], parts[1]) if len(parts) == 2 else (value, "")
    render_apple_health_tile(
        category=title,
        tier=tier,
        timestamp="Live",
        value=figure,
        unit=unit,
        context_html=html.escape(caption),
    )


def _lab_tier_icon(tier: str) -> str:
    if tier == "red":
        return "🔴"
    if tier == "amber":
        return "🟡"
    return "🟢"


def lab_pill_html(label: str, tier: str = "green") -> str:
    """Single high-contrast semantic lab pill."""
    safe = html.escape(label)
    return (
        f'<span class="lab-pill {html.escape(tier)}">'
        f"{_lab_tier_icon(tier)} {safe}</span>"
    )


def lab_pills_html(items: list[dict]) -> str:
    """Inline row of semantic lab pills."""
    pills = "".join(
        lab_pill_html(it["label"], it.get("tier", "green")) for it in items
    )
    return f'<div class="lab-pill-row">{pills}</div>'


def lab_legend_html() -> str:
    return (
        '<div class="lab-legend">'
        "🔴 Positive AHA KD Criterion / Out of Range"
        "&nbsp;&nbsp;|&nbsp;&nbsp;"
        "🟢 Within Normal Range"
        "&nbsp;&nbsp;|&nbsp;&nbsp;"
        "🟡 Borderline / Evolving"
        "</div>"
    )


def lab_detail_panel_html(items: list[dict]) -> str:
    """Name | colored value | cutoff reference for each lab."""
    rows = []
    for it in items:
        rows.append(
            '<div class="lab-detail-row">'
            f'<div class="lab-detail-name">{html.escape(it["name"])}</div>'
            '<div class="lab-detail-pill">'
            f'{lab_pill_html(it["label"], it.get("tier", "green"))}</div>'
            f'<div class="lab-detail-cut">{html.escape(it.get("cutoff", ""))}</div>'
            "</div>"
        )
    return lab_legend_html() + "".join(rows)


def leo_supplemental_lab_cards_html(p: dict) -> str:
    """Spacious 2×3 card grid for Leo's 6 AHA supplemental labs."""
    wbc_k = round(float(p.get("wbc", 17400)) / 1000, 1)
    plt_k = int(round(float(p.get("plt", 390000)) / 1000))
    cards = [
        {
            "name": "WBC",
            "pill": f"🔴 {wbc_k}k /µL",
            "tier": "red",
            "cutoff": "AHA supplemental cutoff ≥ 15.0k /µL",
        },
        {
            "name": "Hemoglobin (Hgb)",
            "pill": f"🔴 {p.get('hgb', 9.8)} g/dL",
            "tier": "red",
            "cutoff": "Normocytic anemia for age · normal 2y M ≥ 11.0 g/dL",
        },
        {
            "name": "Albumin",
            "pill": f"🔴 {p.get('albumin', 2.7)} g/dL",
            "tier": "red",
            "cutoff": "AHA supplemental cutoff ≤ 3.0 g/dL",
        },
        {
            "name": "ALT",
            "pill": f"🔴 {p.get('alt', 68)} U/L",
            "tier": "red",
            "cutoff": "Elevated transaminase · normal < 45 U/L",
        },
        {
            "name": "Platelets",
            "pill": f"🟢 {plt_k}k /µL",
            "tier": "green",
            "cutoff": (
                "Within normal 150k–400k now · AHA ≥ 450k peaks after Day 7"
            ),
        },
        {
            "name": "Urine WBC (UA)",
            "pill": f"🔴 {p.get('ua_wbc', 24)} WBC/hpf",
            "tier": "red",
            "cutoff": "Sterile pyuria · AHA supplemental cutoff ≥ 10 WBC/hpf",
        },
    ]
    parts = ['<div class="supp-lab-grid">']
    for card in cards:
        parts.append(
            f'<div class="supp-lab-card {html.escape(card["tier"])}">'
            '<div class="supp-lab-head">'
            f'<span class="supp-lab-name">{html.escape(card["name"])}</span>'
            f'<span class="supp-lab-pill">{html.escape(card["pill"])}</span>'
            "</div>"
            f'<div class="supp-lab-cut">{html.escape(card["cutoff"])}</div>'
            "</div>"
        )
    parts.append("</div>")
    return "".join(parts)


def leo_inflam_lab_panel_html(p: dict) -> str:
    """CRP/ESR pills + spacious 6-card supplemental AHA lab grid."""
    primary = leo_inflam_lab_items(p)[:2]
    return (
        lab_legend_html()
        + '<div style="margin:6px 0 4px;font-size:0.8rem;font-weight:700;'
        'color:#0f172a;">Primary inflammatory markers</div>'
        + lab_pills_html(primary)
        + '<div style="margin:10px 0 0;font-size:0.8rem;font-weight:700;'
        'color:#0f172a;">Supplemental AHA labs (6 criteria)</div>'
        + leo_supplemental_lab_cards_html(p)
    )


def leo_inflam_lab_items(p: dict) -> list[dict]:
    """Leo AHA inflammatory + supplemental labs with semantic tiers."""
    wbc_k = round(float(p.get("wbc", 17400)) / 1000, 1)
    plt_k = int(round(float(p.get("plt", 390000)) / 1000))
    return [
        {
            "name": "CRP",
            "label": f"{p['crp']} mg/dL",
            "tier": "red",
            "cutoff": "AHA cutoff ≥ 3.0 mg/dL · 4.7× threshold",
        },
        {
            "name": "ESR",
            "label": f"{p['esr']} mm/h",
            "tier": "red",
            "cutoff": "AHA cutoff ≥ 40 mm/h",
        },
        {
            "name": "WBC",
            "label": f"{wbc_k}k /µL",
            "tier": "red",
            "cutoff": "AHA supplemental cutoff ≥ 15.0k /µL",
        },
        {
            "name": "Hgb",
            "label": f"{p.get('hgb', 9.8)} g/dL",
            "tier": "red",
            "cutoff": "Normocytic anemia for age · normal 2y M ≥ 11.0 g/dL",
        },
        {
            "name": "Albumin",
            "label": f"{p.get('albumin', 2.7)} g/dL",
            "tier": "red",
            "cutoff": "AHA supplemental cutoff ≤ 3.0 g/dL",
        },
        {
            "name": "ALT",
            "label": f"{p.get('alt', 68)} U/L",
            "tier": "red",
            "cutoff": "Elevated transaminase · normal < 45 U/L",
        },
        {
            "name": "Platelets",
            "label": f"{plt_k}k /µL",
            "tier": "green",
            "cutoff": (
                "Within normal 150k–400k now · AHA thrombocytosis ≥ 450k "
                "typically peaks after Day 7"
            ),
        },
        {
            "name": "UA WBC",
            "label": f"{p.get('ua_wbc', 24)} WBC/hpf",
            "tier": "red",
            "cutoff": "Sterile pyuria · AHA supplemental cutoff ≥ 10 WBC/hpf",
        },
    ]


def patient_lab_items(p: dict, panel: str) -> list[dict] | None:
    """Structured color-coded labs for citation / metric popovers."""
    pid = p.get("id")
    if pid == "leo" and panel == "labs":
        return leo_inflam_lab_items(p)
    if pid == "emma" and panel == "bmp":
        return [
            {
                "name": "Creatinine",
                "label": f"{p['cr']:.2f} mg/dL",
                "tier": "red",
                "cutoff": f"Baseline {p['cr_base']:.2f} · +70% Stage 1 AKI",
            },
            {
                "name": "Potassium",
                "label": f"{p['labs']['k']} mEq/L",
                "tier": "green",
                "cutoff": "Normal pediatric range ~3.5–5.0 mEq/L",
            },
            {
                "name": "Phosphorus",
                "label": f"{p['labs']['phos']} mg/dL",
                "tier": "green",
                "cutoff": "Within normal for age",
            },
            {
                "name": "Uric acid",
                "label": f"{p['labs']['ua']} mg/dL",
                "tier": "amber",
                "cutoff": "Watch with HD-MTX / TLS risk",
            },
            {
                "name": "Sodium",
                "label": f"{p['labs']['na']} mEq/L",
                "tier": "green",
                "cutoff": "Normal 135–145 mEq/L",
            },
        ]
    if pid == "emma" and panel == "mtx":
        cut = float(p.get("mtx_cutoff_h48", MTX_CUTOFFS.get(p.get("hour", 48), 0.4)))
        return [
            {
                "name": "MTX Hour 48 (04:15)",
                "label": f"{p['mtx']:.2f} µmol/L",
                "tier": "red",
                "cutoff": f"Cutoff ≤ {cut:.2f} µmol/L · {p['mtx']/cut:.1f}× threshold",
            },
            {
                "name": "Hour 42 (22:15)",
                "label": "5.20 µmol/L",
                "tier": "red",
                "cutoff": "Prior delayed-clearance trend",
            },
            {
                "name": "Hour 36 (16:15)",
                "label": "8.40 µmol/L",
                "tier": "red",
                "cutoff": "Prior delayed-clearance trend",
            },
            {
                "name": "Hour 24 (04:15)",
                "label": "118.0 µmol/L",
                "tier": "amber",
                "cutoff": "End-infusion level (≤150 typical gate)",
            },
        ]
    if pid == "maya" and panel == "bmp":
        return [
            {
                "name": "Creatinine",
                "label": f"{p['cr']:.2f} mg/dL",
                "tier": "green",
                "cutoff": f"Baseline {p['cr_base']:.2f} · near baseline / stable",
            },
            {
                "name": "Electrolytes",
                "label": "WNL",
                "tier": "green",
                "cutoff": "Na / K / Cl / CO₂ within pediatric reference",
            },
        ]
    if pid == "chloe" and panel == "bmp":
        return [
            {
                "name": "Phosphorus",
                "label": f"{p['phos']:.1f} mg/dL",
                "tier": "red",
                "cutoff": "Critical low · was 2.6 yesterday · gate < 2.5",
            },
            {
                "name": "Potassium",
                "label": f"{p['k']} mEq/L",
                "tier": "red",
                "cutoff": "Hypokalemia · refeeding risk · goal ≥ 3.5",
            },
            {
                "name": "Magnesium",
                "label": f"{p['mg']} mg/dL",
                "tier": "red",
                "cutoff": "Hypomagnesemia · refeeding risk · goal ≥ 1.6",
            },
            {
                "name": "Glucose",
                "label": "78 mg/dL",
                "tier": "green",
                "cutoff": "Within normal fasting/random range",
            },
        ]
    return None


def citation_pill(
    p: dict,
    cite_key: str,
    *,
    loc: str = "main",
    label: str | None = None,
    mar_html: str | None = None,
) -> None:
    cites = p.get("citations") or {}
    cite = cites.get(cite_key)
    if not cite:
        return
    pop = st.popover(
        label or cite["label"],
        width="stretch",
        key=f"cite_{p['id']}_{cite_key}_{loc}",
        on_change="rerun",
    )
    with pop:
        if pop.open:
            if mar_html:
                st.html(mar_html)
            st.markdown(f"**{cite['title']}**")
            labs = cite.get("labs") or patient_lab_items(p, cite_key)
            if p.get("id") == "leo" and cite_key == "labs":
                st.html(leo_inflam_lab_panel_html(p))
                if cite.get("note"):
                    st.caption(cite["note"])
            elif labs:
                st.html(lab_detail_panel_html(labs))
                if cite.get("note"):
                    st.caption(cite["note"])
            elif cite.get("body_html"):
                st.html(cite["body_html"])
            else:
                st.text(cite["body"])


def render_citation_row(p: dict, keys: list[str], *, loc: str = "narr") -> None:
    cols = st.columns(len(keys))
    for col, key in zip(cols, keys):
        with col:
            citation_pill(p, key, loc=loc)


# ---------------------------------------------------------------------------
# Archetype metric cards
# ---------------------------------------------------------------------------
def _metrics_emma(p: dict) -> None:
    cut = float(p.get("mtx_cutoff_h48", MTX_CUTOFFS.get(p["hour"], 0.4)))
    mtx_breach = p["mtx"] > cut
    rise = (p["cr"] - p["cr_base"]) / p["cr_base"] * 100
    cr_breach = rise >= 50
    ph_breach = p["urine_ph"] < 7.0
    over = p["mtx"] / cut if cut else 0
    pid = p["id"]
    mtx_ok = order_is_addressed(pid, "emma_leucovorin")
    cr_ok = order_is_addressed(pid, "emma_fluids")
    ph_ok = order_is_addressed(pid, "emma_bicarb")
    mtx_at = order_addressed_at(pid, "emma_leucovorin")
    cr_at = order_addressed_at(pid, "emma_fluids")
    ph_at = order_addressed_at(pid, "emma_bicarb")
    mar_mtx = mar_detail_card_html(
        addressed=mtx_ok,
        sections=[{
            "rows": [
                ("Medication", "Leucovorin Calcium (Folinic Acid)"),
                (
                    "Dosage",
                    "100 mg/m²/dose = 98 mg (escalated from 30 mg/m² = 29 mg)",
                ),
                ("Route", "IV Piggyback (Central Port)"),
                (
                    "Administered",
                    f"{mtx_at} (Scheduled q6h: 07:00 / 13:00 / 19:00 / 01:00)",
                ),
                (
                    "Drip Run Time",
                    "Infuse over 15 minutes (Max rate ≤ 160 mg/min due to Ca²⁺)",
                ),
            ],
        }],
    )
    mar_cr = mar_detail_card_html(
        addressed=cr_ok,
        sections=[{
            "rows": [
                (
                    "Medication",
                    "D5 0.2% NaCl + NaHCO₃ 60 mEq/L (Alkalinized Hyperhydration)",
                ),
                (
                    "Dosage / Rate",
                    "200 mL/m²/hr = 196 mL/hr (escalated from 150 mL/m²/hr = 147 mL/hr)",
                ),
                ("Route", "IV Continuous Infusion (Central Port)"),
                ("Administered", f"Rate increased at {cr_at}"),
                (
                    "Drip Run Time",
                    "Continuous 24-hour infusion until Serum MTX < 0.10 µmol/L",
                ),
            ],
        }],
    )
    mar_ph = mar_detail_card_html(
        addressed=ph_ok,
        sections=[{
            "rows": [
                ("Medication", "Sodium Bicarbonate 8.4% (NaHCO₃)"),
                (
                    "Dosage",
                    "1 mEq/kg = 26 mEq STAT Bolus (diluted in 50 mL sterile water)",
                ),
                ("Route", "IV Piggyback"),
                ("Administered", ph_at),
                (
                    "Drip Run Time",
                    "Infuse over 30 minutes (Repeat POC urine pH dipstick at 08:15)",
                ),
            ],
        }],
    )
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        with st.container(border=True):
            render_apple_health_tile(
                category="MTX Level",
                tier="red" if mtx_breach else "green",
                timestamp=f"Hr {p['hour']} · 04:15",
                value=f"{p['mtx']:.2f}",
                unit="µmol/L (Hr 48)",
                context_html=(
                    addressed_badge(f"✓ Leucovorin · {mtx_at}")
                    if mtx_ok
                    else (
                        f"{breach_badge(f'{over:.1f}× cutoff')} "
                        f"Target ≤ {cut:.2f}"
                    )
                ),
                value_critical=mtx_breach,
                addressed=mtx_ok and mtx_breach,
            )
            citation_pill(
                p, "mtx", loc="m1", label="🧪 MTX Nomogram", mar_html=mar_mtx
            )
    with c2:
        with st.container(border=True):
            render_apple_health_tile(
                category="Serum Cr",
                tier="red" if cr_breach else ("amber" if rise > 0 else "green"),
                timestamp="04:15",
                value=f"{p['cr']:.2f}",
                unit="mg/dL",
                context_html=(
                    addressed_badge(f"✓ Hyperhydration · {cr_at}")
                    if cr_ok
                    else (
                        f"{breach_badge(f'{rise:+.0f}% vs base')} "
                        f"Base {p['cr_base']:.2f}"
                    )
                ),
                value_critical=cr_breach,
                addressed=cr_ok and cr_breach,
            )
            citation_pill(
                p, "bmp", loc="m2", label="📊 Renal & BMP", mar_html=mar_cr
            )
    with c3:
        with st.container(border=True):
            render_apple_health_tile(
                category="Urine pH",
                tier="red" if ph_breach else "green",
                timestamp="06:00",
                value=f"{p['urine_ph']:.1f}",
                unit="pH · BP ↑",
                context_html=(
                    addressed_badge(f"✓ NaHCO₃ Bolus · {ph_at}")
                    if ph_ok
                    else (
                        f"{breach_badge('Acidic pH')} "
                        "Target pH ≥ 7.0"
                    )
                ),
                value_critical=ph_breach,
                addressed=ph_ok and ph_breach,
            )
            vitals_trend_popover(
                p,
                key_suffix="emma_bp",
                label="📈 pH & BP Curve",
                show_bp=True,
                show_fever=False,
                title="**📈 Critical fluid-overload BP · Emma Rodriguez**",
                mar_html=mar_ph,
            )
    with c4:
        with st.container(border=True):
            render_apple_health_tile(
                category="Protocol Gate",
                tier="amber",
                timestamp=f"Hr {p['hour']}",
                value="AALL1131",
                unit=f"Hr {p['hour']}",
                context_html=(
                    f"BSA {p['bsa']} m² · Wt {p['wt']} kg"
                ),
                value_critical=False,
            )
            citation_pill(
                p, "exam", loc="m4", label="📋 Protocol Info"
            )


def maya_po_switch_staged(pid: str = "maya") -> bool:
    """True when IV→PO Cephalexin order is in the staged Epic cart."""
    bag = st.session_state.get(_staged_orders_key(pid), {})
    return "maya_po_switch" in bag


def _maya_mic_rows(*, switched: bool) -> list[dict]:
    """Simplified 3-column urine culture susceptibility rows for Maya."""
    return [
        {
            "antibiotic": "Ceftriaxone (IV)",
            "result": "🟢 Sensitive (S)",
            "mic": "≤ 0.25",
            "row_class": "row-active" if not switched else "",
            "badge": (
                "💊 CURRENT ACTIVE THERAPY (800 mg IV q24h)"
                if not switched
                else "✔️ Prior IV Regimen (Discontinued)"
            ),
            "badge_muted": switched,
        },
        {
            "antibiotic": "Cefazolin / Cephalexin (PO)",
            "result": "🟢 Sensitive (S)",
            "mic": "≤ 1.0",
            "row_class": "row-chosen" if switched else "row-target",
            "badge": (
                "✅ ACTIVE CHOSEN PO THERAPY: 400 mg PO TID"
                if switched
                else "🎯 TARGET PO SWITCH: 400 mg PO TID"
            ),
            "badge_muted": False,
        },
        {
            "antibiotic": "Ampicillin",
            "result": "🟢 Sensitive (S)",
            "mic": "≤ 2.0",
            "row_class": "",
            "badge": "",
            "badge_muted": False,
        },
        {
            "antibiotic": "TMP-SMX (Bactrim)",
            "result": "🟢 Sensitive (S)",
            "mic": "≤ 0.5/9.5",
            "row_class": "",
            "badge": "",
            "badge_muted": False,
        },
        {
            "antibiotic": "Gentamicin",
            "result": "🟢 Sensitive (S)",
            "mic": "≤ 1.0",
            "row_class": "",
            "badge": "",
            "badge_muted": False,
        },
        {
            "antibiotic": "Nitrofurantoin",
            "result": "🟢 Sensitive (S)*",
            "mic": "≤ 16.0",
            "row_class": "",
            "badge": "",
            "badge_muted": False,
        },
    ]


def maya_mic_table_html(*, switched: bool) -> str:
    """Clean 3-column susceptibility table with active-regimen highlighting."""
    rows = _maya_mic_rows(switched=switched)
    body = []
    for r in rows:
        badge = ""
        if r["badge"]:
            muted = " muted" if r.get("badge_muted") else ""
            badge = (
                f'<div class="mic-status-badge{muted}">'
                f'{html.escape(r["badge"])}</div>'
            )
        body.append(
            f'<tr class="{html.escape(r["row_class"])}">'
            f"<td>{html.escape(r['antibiotic'])}{badge}</td>"
            f"<td>{html.escape(r['result'])}</td>"
            f'<td class="mono">{html.escape(r["mic"])}</td>'
            "</tr>"
        )
    return (
        '<div class="mic-table-wrap">'
        '<div style="font-size:0.82rem;font-weight:700;color:#0F172A;'
        'margin-bottom:8px;">🦠 Final Urine Culture: &gt;100,000 CFU/mL '
        "Escherichia coli (Catheterized Specimen · Resulted 22:10)</div>"
        '<table class="mic-table"><thead><tr>'
        "<th>Antibiotic</th><th>Sensitivity</th><th>MIC (µg/mL)</th>"
        "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table>"
        '<div class="mic-footnote">*Sensitive in vitro, but not used for '
        "pyelonephritis due to poor renal tissue penetration.</div>"
        "</div>"
    )


def maya_urine_mar_html(*, switched: bool, po_at: str = "07:15") -> str:
    """MAR card for Maya urine culture popover (IV CTX ± PO Cephalexin)."""
    sections = [
        {
            "heading": "Initial Empiric IV Regimen (Addressed at 22:45)",
            "rows": [
                ("Medication", "Ceftriaxone (Rocephin)"),
                ("Dosage", "50 mg/kg/dose = 800 mg q24h"),
                ("Route", "IV Piggyback (Right Hand PIV)"),
                ("Administered", "Last dose given at 22:45"),
                ("Drip Run Time", "Infused over 30 minutes"),
            ],
        }
    ]
    if switched:
        sections.append({
            "heading": f"De-Escalated Oral Regimen (Staged at {po_at})",
            "rows": [
                (
                    "Medication",
                    "Cephalexin (Keflex) 250 mg/5 mL Oral Suspension",
                ),
                ("Dosage", "25 mg/kg/dose = 400 mg (8 mL) TID"),
                ("Route", "PO (Oral)"),
                (
                    "Administered",
                    f"Staged at {po_at} (First PO dose scheduled for 08:00)",
                ),
                (
                    "Course Duration",
                    "8 remaining days (completes 10-day total pyelonephritis course)",
                ),
            ],
        })
    return mar_detail_card_html(addressed=True, sections=sections)


def render_maya_susceptibility_popover(p: dict) -> None:
    """Single urine culture results popover + PO Cephalexin stage CTA."""
    switched = maya_po_switch_staged(p["id"])
    dose = round(25 * float(p["wt"]))
    so = p["stage_order"]
    po_at = order_addressed_at(p["id"], "maya_po_switch", default="07:15")
    pop = st.popover(
        "🦠 Urine Culture",
        width="stretch",
        key=f"maya_mic_pop_{p['id']}",
        on_change="rerun",
    )
    with pop:
        if not pop.open:
            return
        st.html(maya_urine_mar_html(switched=switched, po_at=po_at))
        st.html(maya_mic_table_html(switched=switched))
        if switched:
            st.success(
                f"✅ Staged in Epic Cart: PO Cephalexin {dose} mg TID",
                title="Order staged",
            )
        elif st.button(
            "⚡ Stage Order: Switch to PO Cephalexin 25 mg/kg TID",
            type="primary",
            width="stretch",
            key=f"maya_mic_stage_{p['id']}",
        ):
            commit_staged_order(
                "maya_po_switch",
                title=so["title"],
                cdi=so.get("cdi_code", ""),
                cdi_label=so.get("cdi_label", ""),
                cdi_note=so.get("cdi_note", ""),
                widget_key=f"maya_mic_stage_{p['id']}",
            )
            st.rerun()


def _metrics_maya(p: dict) -> None:
    switched = maya_po_switch_staged(p["id"])
    # Empiric IV CTX is active coverage; PO switch upgrades the resolution badge
    culture_addressed = True
    po_at = order_addressed_at(p["id"], "maya_po_switch", default="07:15")
    piv_ok = order_is_addressed(p["id"], "maya_piv_dc")
    piv_at = order_addressed_at(p["id"], "maya_piv_dc", default="07:15")
    if switched:
        culture_ctx = addressed_badge(f"✓ Cephalexin · {po_at}")
    else:
        culture_ctx = addressed_badge("✓ Ceftriaxone · 22:45")
    if piv_ok:
        afebrile_ctx = addressed_badge(f"✓ IVF DC · PIV locked · {piv_at}")
    else:
        afebrile_ctx = (
            f"{_ah_delta_pill('Gate ✓', tone='ok')} "
            "≥24h · PO switch unlocked"
        )
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        with st.container(border=True):
            render_apple_health_tile(
                category="Afebrile Timer",
                tier="green",
                timestamp="Live",
                value=f"{p['afebrile_hours']}h",
                unit="Afebrile",
                context_html=afebrile_ctx,
                value_critical=False,
                addressed=piv_ok,
            )
            vitals_trend_popover(
                p,
                key_suffix="maya_fever_cleared",
                label="📈 Fever Curve",
                show_bp=False,
                show_fever=True,
                title="**📈 Fever cleared ≥24h · Maya Patel (PO switch gate)**",
            )
    with c2:
        with st.container(border=True):
            render_apple_health_tile(
                category="Urine Culture",
                tier="red",
                timestamp_html=(
                    '<span class="ah-tile-ts">'
                    '<span style="color:#BE123C;font-weight:700;">'
                    "Positive · 22:10</span></span>"
                ),
                value_html=(
                    '<span class="ah-tile-value pathogen">E. coli</span>'
                ),
                unit_html=(
                    '<span class="ah-tile-unit subtle">6/6 S</span>'
                ),
                context_html=culture_ctx,
                value_critical=True,
                addressed=culture_addressed,
            )
            render_maya_susceptibility_popover(p)
    with c3:
        with st.container(border=True):
            render_apple_health_tile(
                category="Renal Recovery",
                tier="green",
                timestamp="05:00",
                value=f"{p['cr']:.2f}",
                unit="mg/dL Cr",
                context_html=(
                    f"{_ah_delta_pill('Stable', tone='ok')} "
                    f"Base {p['cr_base']:.2f}"
                ),
                value_critical=False,
            )
            citation_pill(
                p, "bmp", loc="m3", label="📊 Renal & WBC"
            )


def _metrics_chloe(p: dict) -> None:
    hr_breach = p["hr_nadir"] < 40
    phos_breach = p["phos"] < 2.0
    ortho_breach = bool(p.get("orthostatic"))
    so = p["stage_order"]
    pid = p["id"]
    hr_ok = order_is_addressed(pid, "chloe_telemetry")
    phos_ok = order_is_addressed(pid, "chloe_phos")
    bed_ok = order_is_addressed(pid, "chloe_bedrest")
    hr_at = order_addressed_at(pid, "chloe_telemetry", default="07:10")
    phos_at = order_addressed_at(pid, "chloe_phos", default="07:10")
    bed_at = order_addressed_at(pid, "chloe_bedrest", default="07:10")
    mar_hr = mar_detail_card_html(
        addressed=hr_ok,
        sections=[{
            "rows": [
                (
                    "Intervention",
                    "Continuous 5-Lead Cardiac Telemetry + Nutrition Hold",
                ),
                (
                    "Specification",
                    "Caloric advancement held at 1,600 kcal/day "
                    "(3 meals + 2 snacks); strict bedrest with 1:1 observation",
                ),
                ("Initiated", hr_at),
                (
                    "Duration",
                    "Continuous until sleeping HR > 45 bpm for 24h "
                    "and Phosphorus > 2.5 mg/dL",
                ),
            ],
        }],
    )
    mar_phos = mar_detail_card_html(
        addressed=phos_ok,
        sections=[{
            "rows": [
                (
                    "Medication",
                    "Sodium Phosphate (NaPhos) IV Replacement + Thiamine 100 mg",
                ),
                ("Dosage", "0.5 mmol/kg = 19 mmol diluted in 150 mL D5W"),
                ("Route", "IV Piggyback (Peripheral IV)"),
                ("Administered", phos_at),
                (
                    "Drip Run Time",
                    f"Slow infusion over 6 hours ({phos_at} – 13:10; 25 mL/hr) "
                    "to prevent hypocalcemia/arrhythmia · Repeat Phos/K/Mg "
                    "panel due at 17:10 (4h post-infusion)",
                ),
            ],
        }],
    )
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        with st.container(border=True):
            render_apple_health_tile(
                category="HR Nadir",
                tier="red" if hr_breach else "amber",
                timestamp="02:15",
                value=str(p["hr_nadir"]),
                unit="bpm Nadir",
                context_html=(
                    addressed_badge(f"✓ Telemetry + Hold · {hr_at}")
                    if hr_ok
                    else (
                        f"{breach_badge('<45 critical')} "
                        "BP 84/48 · &lt;5th %ile"
                    )
                ),
                value_critical=hr_breach,
                addressed=hr_ok and hr_breach,
            )
            vitals_trend_popover(
                p,
                key_suffix="chloe_hr_bp",
                label="📈 HR & BP Curve",
                show_bp=True,
                show_fever=False,
                title=(
                    "**📈 Critical bradycardia & hypotensive BP · "
                    "Chloe Miller**"
                ),
                mar_html=mar_hr,
            )
    with c2:
        with st.container(border=True):
            render_apple_health_tile(
                category="Serum Phos",
                tier="red" if phos_breach else "amber",
                timestamp="05:30",
                value=f"{p['phos']:.1f}",
                unit="mg/dL Phos",
                context_html=(
                    addressed_badge(f"✓ Na Phosphate · {phos_at}")
                    if phos_ok
                    else (
                        f"{breach_badge('↓ from 2.6')} "
                        "Refeeding hypoPhos"
                    )
                ),
                value_critical=phos_breach,
                addressed=phos_ok and phos_breach,
            )
            citation_pill(
                p,
                "bmp",
                loc="m2",
                label="🧪 Refeeding Labs",
                mar_html=mar_phos,
            )
    with c3:
        with st.container(border=True):
            render_apple_health_tile(
                category="Orthostatics",
                tier="red" if ortho_breach else "amber",
                timestamp="07:20",
                value="+28",
                unit="bpm ΔHR",
                context_html=(
                    addressed_badge(f"✓ Bedrest + Telemetry · {bed_at}")
                    if bed_ok
                    else (
                        f"{_ah_delta_pill('Ortho +')} "
                        f"K {p['k']} · Mg {p['mg']}"
                    )
                ),
                value_critical=True,
                addressed=bed_ok and ortho_breach,
            )
            citation_pill(
                p, "exam", loc="m3", label="🫀 ECG & Orthos", mar_html=mar_hr
            )
    with c4:
        with st.container(border=True):
            render_apple_health_tile(
                category="Caloric Stage",
                tier="amber",
                timestamp="Day 3",
                value=f"{p['kcal']:,}",
                unit="kcal Hold",
                context_html=(
                    addressed_badge(f"✓ Telemetry + Hold · {hr_at}")
                    if hr_ok
                    else (
                        f"{_ah_delta_pill('Hold advance', tone='warn')} "
                        "Until Phos ≥ 2.5"
                    )
                ),
                value_critical=False,
                addressed=hr_ok,
            )
            _stage_branch_button(
                key=f"chloe_tile_stage_{p['id']}",
                label="⚡ Stage Orders",
                pid=p["id"],
                title=so["title"],
                cdi=so.get("cdi_code", ""),
                cdi_label=so.get("cdi_label", ""),
                cdi_note=so.get("cdi_note", ""),
                order_lines=so.get("orders"),
                order_id="chloe_phos",
                as_tile_footer=True,
            )


KD_DIAGNOSTIC_RULE = (
    "The diagnosis of KD requires the presence of fever lasting at least "
    "5 days* without any other explanation combined with at least 4 of the "
    "5 following criteria. A significant proportion of children with KD "
    "have a concurrent infection; therefore, ascribing the fever to such "
    "an infection or to KD requires clinical judgment."
)
KD_DIAGNOSTIC_FOOTNOTE = (
    "* If ≥4 of the above criteria are present, a diagnosis of KD can be "
    "made on day 4 of illness. (KD: Kawasaki disease.)"
)


def _leo_kd_principal_criteria() -> list[dict]:
    """Δ Clinical diagnostic criteria + Leo Incomplete KD (2/5) findings."""
    return [
        {
            "criterion": (
                "Bilateral bulbar conjunctival injection without exudate"
            ),
            "leo": _cm_red(
                "(1) ✅ Bilateral non-exudative bulbar conjunctival injection "
                "with limbal sparing (Day 2)"
            ),
            "algo_leo": _cm_red(
                "(1) ✅ Bilateral non-exudative bulbar conjunctival injection "
                "with limbal sparing (Day 2)"
            ),
            "positive": True,
        },
        {
            "criterion": (
                "Polymorphous rash (maculopapular, diffuse erythroderma, or "
                "erythema multiforme-like)"
            ),
            "leo": _cm_red(
                "(2) ✅ Diffuse maculopapular polymorphous truncal &amp; groin "
                "rash (Day 3)"
            ),
            "algo_leo": _cm_red(
                "(2) ✅ Diffuse maculopapular polymorphous truncal &amp; groin "
                "rash (Day 3)"
            ),
            "positive": True,
        },
        {
            "criterion": (
                "Oral mucous membrane changes, including erythema and/or "
                "fissuring of lips, strawberry tongue, and/or erythema of "
                "oropharyngeal mucosa"
            ),
            "leo": _cm_absent(
                "ABSENT: oral mucosal changes (lips moist/intact, no "
                "strawberry tongue)"
            ),
            "algo_leo": _cm_absent("ABSENT — No oral mucosal changes"),
            "positive": False,
        },
        {
            "criterion": (
                "Peripheral extremity changes, including erythema of palms "
                "and/or soles and/or edema of hands and/or feet (acute phase) "
                "and/or periungual desquamation (subacute phase)"
            ),
            "leo": _cm_absent(
                "ABSENT: peripheral extremity erythema/edema"
            ),
            "algo_leo": _cm_absent("ABSENT — No extremity erythema/edema"),
            "positive": False,
        },
        {
            "criterion": (
                "Cervical lymphadenopathy (at least 1 lymph node ≥1.5 cm in "
                "diameter, usually unilateral)"
            ),
            "leo": _cm_absent(
                "ABSENT: cervical node ≥1.5 cm (shotty &lt;0.8 cm only)"
            ),
            "algo_leo": _cm_absent(
                "ABSENT — Shotty nodes &lt;0.8 cm only"
            ),
            "positive": False,
        },
    ]


def _leo_kd_status_line(p: dict) -> str:
    tmax_f = round(float(p["tmax"]) * 9 / 5 + 32, 1)
    return _cm_red(
        f"Fever Duration: Day {p['fever_day']} unexplained fever, "
        f"Tmax {p['tmax']}°C ({tmax_f}°F)"
    ) + (
        f" + only {p['criteria_met']} of 5 Clinical Criteria "
        f"(Incomplete KD lab pathway)"
    )


def leo_kd_rule_banner_html(p: dict) -> str:
    """Top KD fever rule + footnote + Leo adjacent status."""
    return (
        '<div class="kd-rule-box">'
        f'<div class="kd-rule-text">{html.escape(KD_DIAGNOSTIC_RULE)}</div>'
        f'<div class="kd-rule-foot">{html.escape(KD_DIAGNOSTIC_FOOTNOTE)}</div>'
        f'<div class="kd-rule-leo">{_leo_kd_status_line(p)}</div>'
        "</div>"
    )


def leo_kd_criteria_side_by_side_html(*, algorithm: bool = False) -> str:
    """Side-by-side Δ diagnostic criteria vs Leo Incomplete KD (2/5) findings."""
    rows = []
    for i, item in enumerate(_leo_kd_principal_criteria(), 1):
        right = item["algo_leo"] if algorithm else item["leo"]
        left = html.escape(item["criterion"])
        rows.append(
            '<div class="kd-crit-row">'
            f"<div><strong>{i}.</strong> {left}</div>"
            f"<div>{right}</div>"
            "</div>"
        )
    left_head = "Δ 5 Clinical Diagnostic Criteria"
    right_head = "Leo Kim's Findings (2 of 5 Met — Incomplete KD)"
    return (
        '<div class="kd-crit-grid">'
        '<div class="kd-crit-head">'
        f"<div>{html.escape(left_head)}</div>"
        f"<div>{html.escape(right_head)}</div>"
        "</div>"
        + "".join(rows)
        + "</div>"
    )


def leo_supp_labs_side_by_side_html(p: dict) -> str:
    """§ Supplemental labs: AHA list vs Leo 5/6 positives."""
    left = (
        "<strong>§ AHA Supplemental Lab Criteria — Need ≥3 of 6</strong>"
        "<ol>"
        "<li>Anemia for age</li>"
        "<li>Platelet count ≥450,000 after the 7th day of fever</li>"
        "<li>Albumin ≤3.0 g/dL</li>"
        "<li>Elevated ALT level</li>"
        "<li>WBC count ≥15,000/mm³</li>"
        "<li>≥10 WBC/hpf on urinalysis</li>"
        "</ol>"
    )
    wbc = int(p.get("wbc", 17400))
    wbc_k = wbc / 1000
    plt_k = int(round(float(p.get("plt", 390000)) / 1000))
    hgb = p.get("hgb", 9.8)
    alb = p.get("albumin", 2.7)
    alt = p.get("alt", 68)
    ua = p.get("ua_wbc", 24)
    right = (
        '<strong><span class="fcmp-badge-red">🔴 Leo Kim\'s Supplemental Labs '
        "— 5 of 6 Positive (Exceeds ≥3 cutoff)</span></strong>"
        "<ol>"
        f"<li>{_cm_red(f'(2) ✅ Hgb {hgb} g/dL (anemia for age)')}</li>"
        f"<li>Platelets: {plt_k}k/µL (normal on Day 6)</li>"
        f"<li>{_cm_red(f'(3) ✅ Albumin {alb} g/dL (≤3.0)')}</li>"
        f"<li>{_cm_red(f'(4) ✅ ALT {alt} U/L (elevated)')}</li>"
        f"<li>{_cm_red(f'(1) ✅ WBC {wbc_k:.1f}k/µL (≥15k)')}</li>"
        f"<li>{_cm_red(f'(5) ✅ Urinalysis {ua} WBC/hpf (sterile pyuria ≥10 WBC/hpf)')}</li>"
        "</ol>"
    )
    return _flow_compare_html(
        "§ AHA Supplemental Lab Criteria — Need ≥3 of 6",
        left,
        "🔴 Leo Kim's Supplemental Labs — 5 of 6 Positive",
        right,
    )


def render_leo_aha_diagnostic_scorecard(p: dict) -> None:
    """Incomplete KD scorecard: fever gate, 2/5 signs, lab pathway."""
    wt = float(p["wt"])
    ivig = round(2 * wt)
    so = p["stage_order"]
    supp = int(p.get("supp_labs_met", 5))

    st.markdown(
        "### 📋 2/5 Diagnostic Scorecard (Incomplete KD)"
    )
    st.caption(
        f"{p['name']} · {p['age']} {p['sex']} · Room {p['room']} · "
        f"Fever Day {p['fever_day']} · {p['criteria_met']}/5 clinical criteriaΔ "
        f"· {supp}/6 supplemental labs§"
    )

    st.markdown("#### A · Diagnostic Requirement (Fever ≥5 days¶ Gate)")
    st.html(leo_kd_rule_banner_html(p))

    st.markdown(
        "#### B · Δ Clinical Diagnostic Criteria "
        f"(Leo = {p['criteria_met']}/5 — Incomplete KD pathway)"
    )
    st.html(leo_kd_criteria_side_by_side_html())
    st.warning(
        f"**Summary:** {p['criteria_met']} of 5 clinical criteriaΔ met "
        "(conjunctivitis + rash) → **enters Incomplete KD CRP/ESR + "
        "supplemental lab algorithm** (not Complete KD ≥4 path).",
        title="2–3 criteria → Incomplete KD lab gate",
    )

    st.markdown(
        "#### C · AHA Lab Gate (CRP/ESR + § Supplemental Labs) — Treatment Trigger"
    )
    st.html(leo_inflam_lab_panel_html(p))
    st.success(
        f"**Incomplete KD confirmed:** CRP {p['crp']} (≥3) · ESR {p['esr']} "
        f"(≥40) · {supp}/6 supplemental labs positive → "
        "**Start IVIG + ASA** (do not delay for echo).",
        title="≥3 supplemental labs met",
    )

    st.warning(
        "No exudative conjunctivitis/pharyngitis, no discrete intraoral ulcers, "
        "no vesicular/bullous rash, no generalized adenopathy or splenomegaly "
        "(excludes Adenovirus, Scarlet Fever, SJS, and MIS-C).",
        title="Mimics & anti-KD features excluded",
    )

    st.divider()
    stage_key = f"aha_score_ivig_{p['id']}"
    staged_flag = f"staged_flag_{stage_key}"
    already = st.session_state.get(staged_flag) or (
        "leo_ivig" in st.session_state.get(_staged_orders_key(p["id"]), {})
    )
    if already:
        st.success(
            f"✅ Staged in Epic Cart: IVIG {ivig} g IV + High-Dose ASA + Echo",
            title="Order staged",
        )
    elif st.button(
        f"⚡ Stage Order: IVIG {ivig} g IV + High-Dose ASA + Echo",
        type="primary",
        width="stretch",
        key=stage_key,
    ):
        commit_staged_order(
            "leo_ivig",
            title=so["title"],
            cdi=so["cdi_code"],
            cdi_label=so["cdi_label"],
            cdi_note=so["cdi_note"],
            widget_key=stage_key,
        )
        st.rerun()


def _metrics_leo(p: dict) -> None:
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    tmax_f = round(float(p["tmax"]) * 9 / 5 + 32, 1)
    supp = int(p.get("supp_labs_met", 5))
    so = p["stage_order"]
    ivig = round(2 * float(p["wt"]))
    pid = p["id"]
    ivig_ok = order_is_addressed(pid, "leo_ivig")
    echo_ok = order_is_addressed(pid, "leo_echo")
    ivig_at = order_addressed_at(pid, "leo_ivig", default="07:18")
    echo_at = order_addressed_at(pid, "leo_echo", default="07:18")
    ivig_badge = addressed_badge(f"✓ IVIG + Aspirin · {ivig_at}")
    echo_badge = addressed_badge(f"✓ Baseline Echo · {echo_at}")
    kd_badge = addressed_badge(f"✓ Incomplete KD Path · {ivig_at}")
    mar_ivig = mar_detail_card_html(
        addressed=ivig_ok,
        sections=[
            {
                "heading": "IVIG Infusion",
                "rows": [
                    (
                        "Medication",
                        "Immune Globulin Intravenous "
                        "(IVIG, Gamunex-C 10% Sucrose-Free)",
                    ),
                    ("Dosage", f"2 g/kg = {ivig} g (260 mL total volume)"),
                    ("Route", "IV Continuous Titrated Infusion"),
                    (
                        "Administered",
                        "Pre-meds (Diphenhydramine 13 mg IV + Acetaminophen "
                        f"195 mg PO) at 06:45; IVIG started at {ivig_at}",
                    ),
                    (
                        "Drip Run Time",
                        f"10–12 hour ramped infusion ({ivig_at} – 18:30): "
                        "6.5 mL/hr × 30m → 13 mL/hr × 30m → "
                        "26 mL/hr × 30m → max 39 mL/hr",
                    ),
                ],
            },
            {
                "heading": "High-Dose Aspirin",
                "rows": [
                    (
                        "Medication",
                        "Aspirin (ASA, High-Dose Anti-Inflammatory Phase)",
                    ),
                    (
                        "Dosage",
                        "80 mg/kg/day divided q6h = 260 mg q6h",
                    ),
                    ("Route", "PO (Chewable/Crushed with food)"),
                    (
                        "Administered",
                        f"First dose at {ivig_at} (Continue until afebrile "
                        "48–72h, then transition to 3–5 mg/kg/day "
                        "[40–65 mg PO daily])",
                    ),
                ],
            },
        ],
    )
    with c1:
        with st.container(border=True):
            render_apple_health_tile(
                category="Fever Curve",
                tier="red",
                timestamp="06:30",
                value=f"Day {p['fever_day']}",
                unit=f"{tmax_f}°F",
                context_html=(
                    ivig_badge
                    if ivig_ok
                    else (
                        f"{breach_badge(f'Tmax {p['tmax']}°C')} "
                        "AHA entry ≥5 days"
                    )
                ),
                value_critical=True,
                addressed=ivig_ok,
            )
            vitals_trend_popover(
                p,
                key_suffix="leo_fever",
                label="📈 Fever Curve",
                show_bp=True,
                show_fever=True,
                bp_collapsed=True,
                title="**📈 Critical fever curve · Leo Kim (Incomplete KD)**",
                mar_html=mar_ivig,
            )
    with c2:
        with st.container(border=True):
            render_apple_health_tile(
                category="KD Criteria",
                tier="amber",
                timestamp="07:40",
                value=f"{p['criteria_met']}/5",
                unit="Signs Met",
                context_html=(
                    kd_badge
                    if ivig_ok
                    else (
                        f"{_ah_delta_pill('Incomplete KD', tone='warn')} "
                        "2–3 → lab pathway"
                    )
                ),
                value_critical=False,
                addressed=ivig_ok,
            )
            score_pop = st.popover(
                "📋 KD Scorecard",
                width="stretch",
                key=f"leo_aha_scorecard_{p['id']}",
                on_change="rerun",
            )
            with score_pop:
                if score_pop.open:
                    st.html(mar_ivig)
                    render_leo_aha_diagnostic_scorecard(p)
    with c3:
        with st.container(border=True):
            render_apple_health_tile(
                category="Inflammatory Labs",
                tier="red",
                timestamp="05:00",
                value=f"{p['crp']}",
                unit="mg/dL CRP",
                context_html=(
                    ivig_badge
                    if ivig_ok
                    else (
                        f"{breach_badge(f'{supp}/6 Suppl +')} "
                        f"ESR {p['esr']} (≥40)"
                    )
                ),
                value_critical=True,
                addressed=ivig_ok,
            )
            lab_pop = st.popover(
                "🧪 Suppl. Labs",
                width="stretch",
                key=f"leo_inflam_labs_{p['id']}",
                on_change="rerun",
            )
            with lab_pop:
                if lab_pop.open:
                    st.html(mar_ivig)
                    st.markdown("### Incomplete KD Lab Gate")
                    st.caption(
                        f"{p['name']} · Drawn 05:00 · CRP/ESR above cutoffs · "
                        f"{supp}/6 supplemental labs positive → treat"
                    )
                    st.html(leo_inflam_lab_panel_html(p))
                    st.caption(
                        "Platelets remain green (390k within 150–400k on Day 6); "
                        "AHA thrombocytosis ≥ 450k typically peaks after Day 7."
                    )
    with c4:
        with st.container(border=True):
            render_apple_health_tile(
                category="Echo Gate",
                tier="red",
                timestamp="Ready",
                value="IVIG",
                unit=f"{ivig}g Ready",
                context_html=(
                    echo_badge
                    if echo_ok
                    else (
                        f"{breach_badge('Treat now')} "
                        "Do not delay for echo"
                    )
                ),
                value_critical=True,
                addressed=echo_ok,
            )
            _stage_branch_button(
                key=f"leo_tile_ivig_{p['id']}",
                label="⚡ Stage IVIG",
                pid=p["id"],
                title=so["title"],
                cdi=so.get("cdi_code", ""),
                cdi_label=so.get("cdi_label", ""),
                cdi_note=so.get("cdi_note", ""),
                order_lines=so.get("orders"),
                order_id="leo_ivig",
                as_tile_footer=True,
            )


# ---------------------------------------------------------------------------
# Pediatric vitals trend viewer (BP percentile bands + fever curve)
# ---------------------------------------------------------------------------
VITALS_TF_OPTIONS = (
    "1 Day (24h)",
    "2 Days (48h)",
    "1 Week (7d)",
    "1 Month (30d)",
)

# Age/sex/height–typical 5th–95th percentile BP bands (mmHg)
VITALS_BP_BANDS = {
    "emma": {"sbp": (88, 112), "dbp": (50, 74), "label": "8y F · 5th–95th %ile"},
    "maya": {"sbp": (82, 106), "dbp": (44, 66), "label": "4y F · 5th–95th %ile"},
    "chloe": {"sbp": (96, 120), "dbp": (58, 80), "label": "15y F · 5th–95th %ile"},
    "leo": {"sbp": (78, 102), "dbp": (40, 62), "label": "2y M · 5th–95th %ile"},
}


def _vitals_now() -> datetime:
    """Anchor 'now' for demo series (stable within a session hour)."""
    n = datetime.now().replace(minute=0, second=0, microsecond=0)
    return n


def _vitals_timestamps(window: str) -> list[datetime]:
    now = _vitals_now()
    if window.startswith("1 Day"):
        # q4h × 24h
        return [now - timedelta(hours=h) for h in range(24, -1, -4)]
    if window.startswith("2 Days"):
        # q6h × 48h
        return [now - timedelta(hours=h) for h in range(48, -1, -6)]
    if window.startswith("1 Week"):
        # q12h × 7d
        return [now - timedelta(hours=h) for h in range(7 * 24, -1, -12)]
    # 1 Month — daily points + sparse pre-admission baseline
    return [now - timedelta(days=d) for d in range(30, -1, -1)]


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _build_bp_series(p: dict, stamps: list[datetime]) -> pd.DataFrame:
    """Patient SBP/DBP series shaped to clinical archetype."""
    pid = p["id"]
    bands = VITALS_BP_BANDS.get(pid, VITALS_BP_BANDS["emma"])
    sbp_lo, sbp_hi = bands["sbp"]
    dbp_lo, dbp_hi = bands["dbp"]
    n = max(len(stamps) - 1, 1)
    rows: list[dict] = []
    for i, ts in enumerate(stamps):
        t = i / n
        if pid == "emma":
            # Fluid-overload / Stage 1 AKI climb 98/60 → 116/76 (crosses 95th %ile)
            sbp = _lerp(98, 116, t)
            dbp = _lerp(60, 76, t)
        elif pid == "maya":
            # Stable normotensive inside band
            sbp = 94 + (2.0 if i % 3 == 0 else -2.0)  # 92–96
            dbp = 56 + (2.0 if i % 2 == 0 else -2.0)  # 54–58
        elif pid == "chloe":
            # Overnight orthostatic drop below 5th %ile → 84/48
            sbp = _lerp(110, 84, min(1.0, t * 1.2))
            dbp = _lerp(70, 48, min(1.0, t * 1.2))
        else:  # leo — febrile/tachycardic but normotensive
            sbp = 93 + (3 if i % 4 == 0 else -3)  # 90–96
            dbp = 53 + (3 if i % 3 == 0 else -3)  # 50–56
        sbp_r, dbp_r = round(sbp, 1), round(dbp, 1)
        rows.append(
            {
                "time": ts,
                "sbp": sbp_r,
                "dbp": dbp_r,
                "bp_pair": f"{sbp_r:.0f}/{dbp_r:.0f} mmHg",
                "sbp_range": f"{sbp_lo}–{sbp_hi} mmHg",
                "dbp_range": f"{dbp_lo}–{dbp_hi} mmHg",
                "sbp_oor": sbp_r < sbp_lo or sbp_r > sbp_hi,
                "dbp_oor": dbp_r < dbp_lo or dbp_r > dbp_hi,
            }
        )
    return pd.DataFrame(rows)


def _build_fever_series(p: dict, stamps: list[datetime], window: str) -> pd.DataFrame:
    """Temperature °F series with clinical fever / hypothermia patterns."""
    pid = p["id"]
    now = _vitals_now()
    rows: list[dict] = []
    for i, ts in enumerate(stamps):
        hours_ago = (now - ts).total_seconds() / 3600
        if pid == "leo":
            # Unremitting high spikes Day 1–6 (~102.4–103.3°F)
            temp_f = 102.4 + (i % 3) * 0.45  # up to ~103.3
            if hours_ago > 6 * 24 and window.startswith("1 Month"):
                temp_f = 98.6 + (i % 2) * 0.2  # pre-illness baseline
        elif pid == "maya":
            # Crossed below 100.4°F ~30h ago; flat 98.4–98.8 since
            if hours_ago <= 30:
                temp_f = 98.4 + (0.4 if i % 2 == 0 else 0.0)
            elif hours_ago <= 48:
                temp_f = _lerp(103.1, 100.6, (48 - hours_ago) / 18)
            else:
                temp_f = 103.1 - min(1.3, (hours_ago - 48) * 0.02)
        elif pid == "chloe":
            temp_f = 96.8 + (i % 4) * 0.25  # 96.8–97.55
        else:  # emma afebrile / neutropenic watch
            temp_f = 98.2 + (i % 5) * 0.18  # 98.2–99.0
        febrile = temp_f >= 100.4
        rows.append(
            {
                "time": ts,
                "temp_f": round(temp_f, 1),
                "febrile": febrile,
                "status": "≥ 100.4°F" if febrile else "< 100.4°F",
            }
        )
    return pd.DataFrame(rows)


def _bp_percentile_chart(p: dict, bp_df: pd.DataFrame) -> alt.Chart:
    """Dual SBP + DBP 5th–95th %ile bands with overlaid patient trends."""
    bands = VITALS_BP_BANDS.get(p["id"], VITALS_BP_BANDS["emma"])
    sbp_lo, sbp_hi = bands["sbp"]
    dbp_lo, dbp_hi = bands["dbp"]
    t0, t1 = bp_df["time"].min(), bp_df["time"].max()
    y_scale = alt.Scale(domain=[35, 140])
    y_axis = alt.Axis(labelColor="#0f172a", titleColor="#0f172a", title="Blood Pressure (mmHg)")
    x_enc = alt.X(
        "time:T",
        title="Time",
        axis=alt.Axis(labelColor="#0f172a", titleColor="#0f172a", grid=True),
    )

    # Explicit horizontal percentile bands (rect across full X window)
    sbp_band = (
        alt.Chart(
            pd.DataFrame({"x": [t0], "x2": [t1], "y": [sbp_lo], "y2": [sbp_hi]})
        )
        .mark_rect(opacity=0.18, color="#3b82f6")
        .encode(x="x:T", x2="x2:T", y=alt.Y("y:Q", scale=y_scale, axis=y_axis), y2="y2:Q")
    )
    dbp_band = (
        alt.Chart(
            pd.DataFrame({"x": [t0], "x2": [t1], "y": [dbp_lo], "y2": [dbp_hi]})
        )
        .mark_rect(opacity=0.18, color="#10b981")
        .encode(x="x:T", x2="x2:T", y="y:Q", y2="y2:Q")
    )

    def _h_rules(lo: float, hi: float, color: str) -> alt.Chart:
        return (
            alt.Chart(pd.DataFrame({"y": [lo, hi]}))
            .mark_rule(strokeDash=[5, 4], color=color, strokeWidth=1.5)
            .encode(y="y:Q")
        )

    sbp_rules = _h_rules(sbp_lo, sbp_hi, "#1d4ed8")
    dbp_rules = _h_rules(dbp_lo, dbp_hi, "#059669")

    # Right-edge / mid-band labels
    sbp_label = (
        alt.Chart(
            pd.DataFrame(
                {
                    "time": [t1],
                    "y": [(sbp_lo + sbp_hi) / 2],
                    "label": [f"Normal SBP Range: {sbp_lo}–{sbp_hi} mmHg (5th–95th %ile)"],
                }
            )
        )
        .mark_text(align="right", dx=-6, fontSize=11, fontWeight="bold", color="#1d4ed8")
        .encode(x="time:T", y="y:Q", text="label:N")
    )
    dbp_label = (
        alt.Chart(
            pd.DataFrame(
                {
                    "time": [t1],
                    "y": [(dbp_lo + dbp_hi) / 2],
                    "label": [f"Normal DBP Range: {dbp_lo}–{dbp_hi} mmHg (5th–95th %ile)"],
                }
            )
        )
        .mark_text(align="right", dx=-6, fontSize=11, fontWeight="bold", color="#047857")
        .encode(x="time:T", y="y:Q", text="label:N")
    )

    tip = [
        alt.Tooltip("time:T", title="Timestamp"),
        alt.Tooltip("bp_pair:N", title="Patient BP"),
        alt.Tooltip("sbp_range:N", title="Normal SBP Range"),
        alt.Tooltip("dbp_range:N", title="Normal DBP Range"),
    ]
    base = alt.Chart(bp_df).encode(x=x_enc)

    sbp_line = base.mark_line(color="#1d4ed8", strokeWidth=2.75).encode(
        y=alt.Y("sbp:Q", scale=y_scale, axis=y_axis),
        tooltip=tip,
    )
    sbp_pts = base.mark_circle(size=70).encode(
        y="sbp:Q",
        color=alt.condition(
            alt.datum.sbp_oor,
            alt.value("#dc2626"),
            alt.value("#1d4ed8"),
        ),
        tooltip=tip,
    )
    dbp_line = base.mark_line(color="#0f766e", strokeWidth=2.5).encode(
        y="dbp:Q",
        tooltip=tip,
    )
    dbp_pts = base.mark_point(shape="diamond", size=70, filled=True).encode(
        y="dbp:Q",
        color=alt.condition(
            alt.datum.dbp_oor,
            alt.value("#dc2626"),
            alt.value("#0f766e"),
        ),
        tooltip=tip,
    )

    return (
        (
            sbp_band
            + dbp_band
            + sbp_rules
            + dbp_rules
            + dbp_line
            + dbp_pts
            + sbp_line
            + sbp_pts
            + sbp_label
            + dbp_label
        )
        .properties(
            height=300,
            title=alt.TitleParams(
                f"BP trend · {bands['label']}",
                color="#0f172a",
                fontSize=13,
            ),
        )
        .configure_axis(labelColor="#0f172a", titleColor="#0f172a")
        .configure_view(strokeWidth=0)
        .configure_legend(disable=True)
    )


def _fever_curve_chart(fever_df: pd.DataFrame) -> alt.Chart:
    cutoff = (
        alt.Chart(pd.DataFrame({"y": [100.4], "label": ["Fever Cutoff (100.4°F)"]}))
        .mark_rule(strokeDash=[6, 4], color="#dc2626", strokeWidth=2)
        .encode(y="y:Q")
    )
    cutoff_label = (
        alt.Chart(pd.DataFrame({"y": [100.4], "label": ["Fever Cutoff (100.4°F)"]}))
        .mark_text(align="left", dx=4, dy=-6, color="#dc2626", fontWeight="bold", fontSize=11)
        .encode(y="y:Q", text="label:N", x=alt.value(8))
    )
    line = (
        alt.Chart(fever_df)
        .mark_line(color="#334155", strokeWidth=2)
        .encode(
            x=alt.X(
                "time:T",
                title="Time",
                axis=alt.Axis(labelColor="#0f172a", titleColor="#0f172a"),
            ),
            y=alt.Y(
                "temp_f:Q",
                title="Temperature (°F)",
                scale=alt.Scale(domain=[96.5, 104.5]),
                axis=alt.Axis(labelColor="#0f172a", titleColor="#0f172a"),
            ),
            tooltip=[
                alt.Tooltip("time:T", title="Time"),
                alt.Tooltip("temp_f:Q", title="Temp °F"),
                alt.Tooltip("status:N", title="vs 100.4°F"),
            ],
        )
    )
    pts = (
        alt.Chart(fever_df)
        .mark_circle(size=60)
        .encode(
            x="time:T",
            y="temp_f:Q",
            color=alt.condition(
                alt.datum.febrile,
                alt.value("#dc2626"),
                alt.value("#047857"),
            ),
            tooltip=[
                alt.Tooltip("time:T", title="Time"),
                alt.Tooltip("temp_f:Q", title="Temp °F"),
                alt.Tooltip("status:N", title="vs 100.4°F"),
            ],
        )
    )
    return (
        (line + pts + cutoff + cutoff_label)
        .properties(
            height=280,
            title=alt.TitleParams(
                "Fever curve (°F) with 100.4°F (38.0°C) cutoff",
                color="#0f172a",
                fontSize=13,
            ),
        )
        .configure_axis(labelColor="#0f172a", titleColor="#0f172a")
        .configure_view(strokeWidth=0)
    )


def _render_bp_curve_block(p: dict, bp_df: pd.DataFrame) -> None:
    bands = VITALS_BP_BANDS.get(p["id"], VITALS_BP_BANDS["emma"])
    sbp_lo, sbp_hi = bands["sbp"]
    dbp_lo, dbp_hi = bands["dbp"]
    with st.container(border=True):
        st.caption(
            f"🔵 Patient SBP (Normal 5th–95th %ile: {sbp_lo}–{sbp_hi} mmHg)"
            f"  |  🟢 Patient DBP (Normal 5th–95th %ile: {dbp_lo}–{dbp_hi} mmHg)"
            f"  |  🔴 Out-of-Range Flag"
        )
    st.altair_chart(
        _bp_percentile_chart(p, bp_df),
        width="stretch",
        alt=(
            f"{p['name']} blood pressure trend with age-specific "
            "SBP and DBP percentile bands"
        ),
    )
    st.caption(
        f"Blue band = Normal SBP {sbp_lo}–{sbp_hi} mmHg (5th–95th %ile) · "
        f"Emerald band = Normal DBP {dbp_lo}–{dbp_hi} mmHg (5th–95th %ile) · "
        "navy = SBP · teal = DBP · crimson = out of range"
    )


def _render_fever_curve_block(p: dict, fever_df: pd.DataFrame) -> None:
    st.altair_chart(
        _fever_curve_chart(fever_df),
        width="stretch",
        alt=f"{p['name']} fever curve with 100.4°F cutoff",
    )
    st.caption(
        "Red dotted line = fever cutoff 100.4°F (38.0°C) · "
        "crimson points ≥ cutoff · emerald points afebrile"
    )


def render_vitals_trend_viewer(
    p: dict,
    *,
    key_suffix: str = "main",
    show_bp: bool = True,
    show_fever: bool = True,
    bp_collapsed: bool = False,
    title: str | None = None,
) -> None:
    """Exception-focused vitals viewer — only render clinically actionable curves."""
    st.markdown(title or f"**📈 Critical vitals · {p['name']}**")
    tf = st.segmented_control(
        "Vitals time window",
        options=list(VITALS_TF_OPTIONS),
        default=VITALS_TF_OPTIONS[1],
        key=f"vitals_tf_{p['id']}_{key_suffix}",
        width="stretch",
    )
    window = tf or VITALS_TF_OPTIONS[1]
    stamps = _vitals_timestamps(window)
    bp_df = _build_bp_series(p, stamps) if show_bp else None
    fever_df = _build_fever_series(p, stamps, window) if show_fever else None

    if show_fever and show_bp and not bp_collapsed:
        left, right = st.columns(2, gap="medium")
        with left:
            _render_bp_curve_block(p, bp_df)
        with right:
            _render_fever_curve_block(p, fever_df)
        return

    if show_fever and fever_df is not None:
        _render_fever_curve_block(p, fever_df)

    if show_bp and bp_df is not None:
        if bp_collapsed:
            bands = VITALS_BP_BANDS.get(p["id"], VITALS_BP_BANDS["emma"])
            exp = st.expander(
                f"Show normal baseline BP "
                f"({bands.get('label', 'age %ile bands')})",
                expanded=False,
            )
            with exp:
                _render_bp_curve_block(p, bp_df)
        else:
            _render_bp_curve_block(p, bp_df)


def vitals_trend_popover(
    p: dict,
    *,
    key_suffix: str = "card",
    label: str = "📈 Critical vitals curve",
    help_text: str | None = None,
    show_bp: bool = True,
    show_fever: bool = True,
    bp_collapsed: bool = False,
    title: str | None = None,
    mar_html: str | None = None,
) -> None:
    """Single exception-based vitals curve popover (no duplicate source pills)."""
    del help_text  # tooltips removed — they cover neighboring tiles
    pop = st.popover(
        label,
        width="stretch",
        key=f"vitals_pop_{p['id']}_{key_suffix}",
        on_change="rerun",
    )
    with pop:
        if pop.open:
            if mar_html:
                st.html(mar_html)
            render_vitals_trend_viewer(
                p,
                key_suffix=f"pop_{key_suffix}",
                show_bp=show_bp,
                show_fever=show_fever,
                bp_collapsed=bp_collapsed,
                title=title,
            )


def render_core_metrics(p: dict) -> None:
    st.html(
        '<div class="telemetry-section-header">'
        "📈 Core Telemetry & Biomarkers</div>"
    )
    fn = {
        "mtx": _metrics_emma,
        "pyelo": _metrics_maya,
        "refeeding": _metrics_chloe,
        "kawasaki": _metrics_leo,
    }.get(p["archetype"], _metrics_emma)
    fn(p)


# ---------------------------------------------------------------------------
# Clinical Pathway & Decision-Tree modals
# ---------------------------------------------------------------------------
def _pathway_stage_card(
    *,
    title: str,
    status: str,
    cutoffs: str,
    values: str,
    action: str,
    active: bool = False,
    tone: str = "green",
) -> None:
    border = ACUITY_RED if active else (
        ACUITY_AMBER if tone == "amber" else (
            ACUITY_RED if tone == "red" else ACUITY_GREEN
        )
    )
    soft_bg = (
        "#FFF1F2"
        if active or tone == "red"
        else ("#FFFBEB" if tone == "amber" else "#ECFDF5")
    )
    with st.container(border=True):
        st.html(
            f"""
            <div style="border-left:5px solid {border}; background:{soft_bg};
                        margin:-0.35rem -0.35rem 0.45rem -0.35rem;
                        padding:8px 12px; border-radius:6px 6px 0 0;
                        font-weight:700; font-size:0.9rem; color:#0f172a;">
              {html.escape(title)} · {html.escape(status)}
            </div>
            """
        )
        st.markdown(f"**Protocol cutoffs:** {cutoffs}")
        st.markdown(f"**Patient values:** {values}")
        st.markdown(f"**Decision-tree action:** {action}")


def _crit_pill_html(tier: str, tip: str, *, label: str | None = None) -> str:
    """CSS hover pill shown next to flagged values."""
    icon = "🚨 Action ▾" if tier == "red" else (
        "⚠️ Action ▾" if tier == "amber" else "✅ Action ▾"
    )
    if label:
        icon = label
    safe_tip = html.escape(tip).replace("\n", "<br/>")
    return (
        f'<span class="crit-action-pill {tier}">{icon}'
        f'<span class="crit-tip">{safe_tip}</span></span>'
    )


def _flagged_value_html(value: str, tier: str, tip: str | None = None) -> str:
    cls = f"pw-val-{tier}"
    pill = _crit_pill_html(tier, tip) if tip else ""
    return f'<span class="{cls}">{html.escape(value)}</span>{pill}'


def _action_popover(
    *,
    key: str,
    title: str,
    body: str,
    tier: str = "red",
    stage_label: str | None = None,
    stage_payload: dict | None = None,
    pid: str = "",
) -> None:
    """Clickable Action popover with optional one-click Epic stage button."""
    icon = "🚨" if tier == "red" else ("⚠️" if tier == "amber" else "✅")
    pop = st.popover(
        f"{icon} Action",
        help=title,
        width="stretch",
        type="primary" if tier == "red" else "secondary",
        key=key,
        on_change="rerun",
    )
    with pop:
        if pop.open:
            st.markdown(f"**{title}**")
            st.markdown(body)
            if stage_label and stage_payload is not None:
                staged_flag = f"staged_flag_{key}_stage"
                if st.session_state.get(staged_flag):
                    st.success(
                        f"✅ Staged in Epic Cart: "
                        f"{stage_payload.get('title', stage_label)}",
                        title="Order staged",
                    )
                elif st.button(
                    stage_label,
                    type="primary",
                    width="stretch",
                    key=f"{key}_stage",
                ):
                    order_id = stage_payload.get("order_id")
                    if order_id:
                        commit_staged_order(
                            order_id,
                            title=stage_payload.get("title", stage_label),
                            cdi=stage_payload.get("cdi", ""),
                            cdi_label=stage_payload.get("cdi_label", ""),
                            cdi_note=stage_payload.get("cdi_note", ""),
                            widget_key=f"{key}_stage",
                        )
                    else:
                        st.session_state[staged_flag] = True
                        st.session_state[f"order_committed_{pid}"] = {
                            "at": datetime.now().strftime("%H:%M"),
                            **stage_payload,
                        }
                    st.rerun()


def _comparison_header(cols_spec: list[float], labels: list[str]) -> None:
    cols = st.columns(cols_spec, gap="small")
    for col, lab in zip(cols, labels):
        with col:
            st.markdown(f"**{lab}**")


def _flow_tone(state: str) -> str:
    """Map legacy state → semantic tone for taken/watermarked styling."""
    parts = state.split()
    if "green" in parts:
        return "green"
    if "watch" in parts or "amber" in parts:
        return "amber"
    if "active" in parts or "red" in parts:
        return "red"
    if state == "root":
        return "root"
    return "dim"


def _flow_node(
    text: str,
    *,
    state: str = "dim",
    shape: str = "rect",
    here: bool = False,  # deprecated — ignored; contrast marks the path
) -> str:
    """HTML flowchart node. Taken path = crisp; unselected = watermarked."""
    del here  # kept for call-site compat; badges removed
    tone = _flow_tone(state)
    classes = ["fnode"]
    if shape == "diamond":
        classes.append("diamond")
    if tone == "root":
        classes.append("root")
    elif tone == "dim":
        classes.append("branch-watermarked")
    else:
        classes.extend(["branch-taken", tone])
        if tone == "amber":
            classes.append("watch")
    return f'<div class="{" ".join(classes)}">{text}</div>'


def _flow_compare_html(
    left_title: str,
    left_html: str,
    right_title: str,
    right_html: str,
    *,
    summary: str | None = None,
) -> str:
    """Side-by-side AHA threshold vs patient actual values inside a flowchart node."""
    summary_block = (
        f'<div class="fcmp-summary">{summary}</div>' if summary else ""
    )
    return (
        '<div class="fcmp">'
        '<div class="fcmp-head">'
        f"<div>{html.escape(left_title)}</div>"
        f"<div>{html.escape(right_title)}</div>"
        "</div>"
        '<div class="fcmp-grid">'
        f'<div class="fcmp-req">{left_html}</div>'
        f'<div class="fcmp-act">{right_html}</div>'
        "</div>"
        f"{summary_block}"
        "</div>"
    )


def _flow_arrow(state: str = "dim") -> str:
    tone = _flow_tone(state)
    if tone == "root":
        return '<div class="farrow">↓</div>'
    if tone == "dim":
        return '<div class="farrow farrow-watermarked">↓</div>'
    return f'<div class="farrow farrow-taken {tone}">↓</div>'


def _flow_branch(
    gate_label: str,
    outcome_html: str,
    *,
    state: str = "dim",
) -> str:
    tone = _flow_tone(state)
    if tone == "dim":
        wrap = "fbranch branch-watermarked"
    else:
        wrap = f"fbranch branch-taken {tone}"
        if tone == "amber":
            wrap += " watch"
    return (
        f'<div class="{wrap}">'
        f'<div class="fbranch-label">{gate_label}</div>'
        f'{_flow_arrow(state)}'
        f"{outcome_html}"
        f"</div>"
    )


def _flow_tree(title: str, root_html: str, branches_html: str, cols: int) -> str:
    return (
        f'<div class="ftree">'
        f'<div class="ftree-title">{html.escape(title)}</div>'
        f"{root_html}"
        f'{_flow_arrow("root")}'
        f'<div class="frail"></div>'
        f'<div class="fbranches cols-{cols}">{branches_html}</div>'
        f"</div>"
    )


def _autocdi_card(cdi_label: str, cdi_note: str) -> None:
    """Point-of-care AutoCDI capture card (shown inside stage popups only)."""
    st.markdown("**Part 2 — Point-of-Care AutoCDI Capture**")
    st.html(
        f"""
        <div style="background:#f8fafc; border:1.5px solid #0369a1; border-radius:10px;
                    padding:12px 14px; color:#0f172a; line-height:1.45;">
          <div style="font-size:0.72rem; font-weight:800; letter-spacing:0.04em;
                      text-transform:uppercase; color:#0369a1; margin-bottom:6px;">
            AutoCDI · CC / MCC capture
          </div>
          <div style="font-weight:700; font-size:0.92rem; color:#0f172a; margin-bottom:4px;">
            {html.escape(cdi_label)}
          </div>
          <div style="font-size:0.82rem; color:#334155;">
            {html.escape(cdi_note)}
          </div>
          <div style="font-size:0.72rem; color:#475569; margin-top:8px;">
            Optional — include in progress note after clinical attestation.
          </div>
        </div>
        """
    )


def _epic_order_preview(
    *,
    order_title: str,
    order_lines: list[str],
    dosing_basis: str = "",
) -> None:
    """Static bullet preview (pathway branch popovers)."""
    st.markdown("**Part 1 — Epic Order Composer Preview**")
    st.markdown(f"**{order_title}**")
    for line in order_lines:
        st.markdown(f"- {line}")
    if dosing_basis:
        st.caption(dosing_basis)


def _epic_composer_interactive(p: dict, *, dosing_basis: str = "") -> None:
    """HITL dialog: per-order Sign / Undo rows + Sign All / Reset."""
    so = p["stage_order"]
    pid = p["id"]
    rows = patient_composer_orders(pid)
    st.markdown("**Part 1 — Epic Order Composer Preview**")
    st.markdown(f"**{so['title']}**")
    for row in rows:
        oid = row["order_id"]
        ord_key = row["ord_key"]
        signed = order_is_staged(pid, oid)
        signed_at = order_addressed_at(pid, oid, default="07:12")
        left, right = st.columns([0.72, 0.28], vertical_alignment="center")
        with left:
            if signed:
                st.html(
                    f"""
                    <div style="padding:6px 2px 6px 0;line-height:1.4;color:#0f172a;">
                      <div style="font-weight:650;font-size:0.90rem;">
                        {html.escape(row["label"])}
                      </div>
                      <div style="margin-top:4px;display:inline-block;background:#ECFDF5;
                                  color:#065f46;border:1px solid #A7F3D0;border-radius:6px;
                                  padding:2px 8px;font-size:0.74rem;font-weight:700;">
                        ✅ Signed · {html.escape(signed_at)} · Checked off in Handoff
                      </div>
                    </div>
                    """
                )
            else:
                st.html(
                    f"""
                    <div style="padding:6px 2px 6px 0;line-height:1.4;color:#0f172a;">
                      <div style="font-weight:650;font-size:0.90rem;">
                        {html.escape(row["label"])}
                      </div>
                      <div style="margin-top:4px;display:inline-block;background:#FFFBEB;
                                  color:#92400E;border:1px solid #FDE68A;border-radius:6px;
                                  padding:2px 8px;font-size:0.74rem;font-weight:650;">
                        ○ Pending Signature
                      </div>
                    </div>
                    """
                )
        with right:
            if signed:
                if st.button(
                    "✓ Signed (Undo)",
                    key=f"btn_{ord_key}",
                    width="stretch",
                ):
                    uncommit_staged_order(oid)
                    st.rerun()
            elif st.button(
                "⚡ Sign Order",
                key=f"btn_{ord_key}",
                width="stretch",
            ):
                commit_staged_order(
                    oid,
                    title=row["label"],
                    cdi=so.get("cdi_code", ""),
                    cdi_label=so.get("cdi_label", ""),
                    cdi_note=so.get("cdi_note", ""),
                    also_stage=False,
                )
                st.rerun()
    if dosing_basis:
        st.caption(dosing_basis)


def _stage_branch_button(
    *,
    key: str,
    label: str,
    pid: str,
    title: str,
    cdi: str,
    cdi_label: str | None = None,
    cdi_note: str | None = None,
    order_lines: list[str] | None = None,
    dosing_basis: str = "",
    order_id: str | None = None,
    as_tile_footer: bool = False,
) -> None:
    """Clean clinical stage button → popover with Epic preview + AutoCDI card."""
    staged_flag = f"staged_flag_{key}"
    already = st.session_state.get(staged_flag) or (
        order_id
        and order_id in st.session_state.get(_staged_orders_key(pid), {})
    )
    if already and not as_tile_footer:
        st.success(
            f"✅ Staged in Epic Cart: {title}",
            title="Order staged",
        )
        return

    pop_kwargs: dict = {
        "width": "stretch",
        "type": "secondary" if as_tile_footer else "primary",
        "key": key,
        "on_change": "rerun",
    }
    if not as_tile_footer:
        pop_kwargs["help"] = "Review Epic order + AutoCDI, then sign to cart"
    pop = st.popover(
        ("✅ Staged") if already and as_tile_footer else label,
        **pop_kwargs,
    )
    with pop:
        if pop.open:
            if already:
                st.success(
                    f"✅ Staged in Epic Cart: {title}",
                    title="Order staged",
                )
                return
            lines = order_lines or [title]
            _epic_order_preview(
                order_title=title,
                order_lines=lines,
                dosing_basis=dosing_basis,
            )
            st.divider()
            _autocdi_card(
                cdi_label or cdi,
                cdi_note or "AutoCDI hooks attached to this order set.",
            )
            st.checkbox(
                "Attending attests clinical validity of CDI language",
                key=f"cdi_attest_{key}",
            )
            if st.button(
                "Sign & Stage to Epic Shopping Cart",
                type="primary",
                width="stretch",
                key=f"{key}_sign",
            ):
                if order_id:
                    commit_staged_order(
                        order_id,
                        title=title,
                        cdi=cdi,
                        cdi_label=cdi_label or cdi,
                        cdi_note=cdi_note or "",
                        widget_key=key,
                    )
                else:
                    st.session_state[staged_flag] = True
                    st.session_state[f"order_committed_{pid}"] = {
                        "at": datetime.now().strftime("%H:%M"),
                        "title": title,
                        "cdi": cdi,
                        "cdi_label": cdi_label or cdi,
                        "cdi_note": cdi_note or "",
                    }
                st.rerun()


def _checkpoint_expander(
    label: str,
    *,
    key: str,
    expanded: bool = False,
    icon: str | None = None,
):
    """Interactive protocol checkpoint row; body renders only when open."""
    return st.expander(
        label,
        expanded=expanded,
        key=key,
        icon=icon,
        on_change="rerun",
        width="stretch",
    )


def render_emma_pathway(p: dict) -> None:
    bsa, wt = p["bsa"], p["wt"]
    total = round(5000 * bsa)  # 4900
    load = round(500 * bsa)  # 490
    cont = round(4500 * bsa)  # 4410
    cont_rate = round(cont / 23.5, 1)  # mL/hr if 1 mg/mL approx display
    hyd_125 = round(125 * bsa)
    hyd_150 = round(150 * bsa)
    hyd_200 = round(200 * bsa)
    lv_100 = round(100 * bsa)
    bicarb = round(1 * wt)
    gluc = round(50 * wt)

    st.markdown(
        f"**{p['name']}** · {p['age']} {p['sex']} · Wt **{wt} kg** · "
        f"BSA **{bsa} m²** · {p['diagnosis']}"
    )
    st.markdown(f"### 1. Protocol header & dosing mathematics (BSA {bsa} m²)")
    st.info(
        (
            f"**Regimen:** COG AALL1131 — High-Risk B-ALL Interim Maintenance I "
            f"(HD-MTX + Leucovorin Rescue + IT MTX + 6-MP)\n\n"
            f"**Total 24h HD-MTX:** 5,000 mg/m² × {bsa} m² = **{total:,} mg** IV "
            f"over 24 hours\n\n"
            f"**Hour 0–0.5 loading bolus (10%):** 500 mg/m² = **{load} mg** IV "
            f"over 30 minutes\n\n"
            f"**Hour 0.5–24 continuous (90%):** 4,500 mg/m² = **{cont:,} mg** IV "
            f"over 23.5 hours (~**{cont_rate} mL/hr** at 1 mg/mL)\n\n"
            f"**Intrathecal therapy (Day 1 prior to HD-MTX):** Age-based "
            f"IT Methotrexate **12 mg IT × 1**"
        ),
        title="COG AALL1131 dosing",
    )

    st.markdown("### 2. Protocol checkpoints — click any row to expand its decision-tree")
    st.caption(
        "Only the current active gate opens by default · expand prior/future checkpoints on demand"
    )
    pid = p["id"]

    # ---- Checkpoint 1: Hour 0 ----
    exp0 = _checkpoint_expander(
        "Hour 0 (Pre-Infusion Gate) — MTX 0.00 | Cr 0.40 | pH 7.4  ·  ✅ Gate Passed",
        key=f"ck_{pid}_h0",
        expanded=False,
        icon=":material/check_circle:",
    )
    with exp0:
        if exp0.open:
            st.html(
                '<div class="ftree">'
                '<div class="ftree-title">Hour 0 · Pre-Infusion Gate</div>'
                + _flow_node("<strong>Pre-Infusion Checks</strong>", state="root")
                + _flow_arrow("root")
                + _flow_node(
                    "ANC ≥ 500 &amp; Plt ≥ 75k &amp; Bili &lt; 1.5× ULN?",
                    state="active green",
                    shape="diamond",
                )
                + '<div class="fbranches cols-2">'
                + _flow_branch("No", _flow_node("Hold Chemo"))
                + _flow_branch(
                    "Yes ✅",
                    _flow_node("Counts cleared — proceed", state="active green"),
                    state="green",
                )
                + "</div>"
                + _flow_arrow("green")
                + _flow_node(
                    "Nephrotoxins / Bactrim / PPIs Held ≥ 48h?<br/>(Yes ✅)",
                    state="active green",
                    shape="diamond",
                )
                + _flow_arrow("green")
                + _flow_node(
                    "2 Consecutive Voids with Urine pH ≥ 7.0?<br/>(Emma: pH 7.4 ✅)",
                    state="active green",
                    shape="diamond",
                )
                + _flow_arrow("green")
                + _flow_node(
                    f"Spike 5 g/m² (<strong>{total:,} mg</strong>) "
                    f"24h HD-MTX Infusion<br/>+ D5 0.2NS + 40 mEq/L NaHCO₃ at "
                    f"125 mL/m²/hr (<strong>{hyd_125} mL/hr</strong>)",
                    state="active green",
                )
                + "</div>"
            )

    # ---- Checkpoint 2: Hour 24 ----
    exp24 = _checkpoint_expander(
        "Hour 24 (End of 24h Infusion) — MTX 118.0 (≤150) | Cr 0.52 (+30% 🟡) | pH 7.1  ·  ⚠️ Sub-AKI Drift Branch",
        key=f"ck_{pid}_h24",
        expanded=False,
        icon=":material/warning:",
    )
    with exp24:
        if exp24.open:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.html(
                    _flow_tree(
                        "MTX Steady-State Gate",
                        _flow_node("<strong>Hour 24 MTX</strong><br/>118.0 µmol/L", state="root"),
                        "".join(
                            [
                                _flow_branch(
                                    "≤ 150 µmol/L",
                                    _flow_node(
                                        "Steady-state OK<br/>(Emma: 118.0 ✅)",
                                        state="active green",
                                    ),
                                    state="green",
                                ),
                                _flow_branch(
                                    "> 150 µmol/L",
                                    _flow_node("Hold / notify pharmacy"),
                                ),
                            ]
                        ),
                        2,
                    )
                )
            with c2:
                st.html(
                    _flow_tree(
                        "Renal Cr Gate",
                        _flow_node("<strong>Hour 24 Cr</strong><br/>0.52 mg/dL (+30%)", state="root"),
                        "".join(
                            [
                                _flow_branch(
                                    "&lt; 25% rise",
                                    _flow_node("Continue 125 mL/m²/hr"),
                                ),
                                _flow_branch(
                                    "25–49% Cr Drift<br/>(Emma: +30%)",
                                    _flow_node(
                                        f"Escalate hydration 25% to<br/>"
                                        f"<strong>150 mL/m²/hr ({hyd_150} mL/hr)</strong>"
                                        f"<br/>+ Mandatory Hour 36 Level"
                                        + _delta_html(
                                            f"125 mL/m²/hr ({hyd_125} mL/hr)",
                                            f"150 mL/m²/hr ({hyd_150} mL/hr) "
                                            f"(+{hyd_150 - hyd_125} mL/hr)",
                                        ),
                                        state="watch",
                                    ),
                                    state="watch",
                                ),
                                _flow_branch(
                                    "≥ 50% rise",
                                    _flow_node("Stage 1 AKI pathway"),
                                ),
                            ]
                        ),
                        3,
                    )
                )
            with c3:
                st.html(
                    _flow_tree(
                        "Urine pH Gate",
                        _flow_node("<strong>Hour 24 pH</strong><br/>7.1", state="root"),
                        "".join(
                            [
                                _flow_branch(
                                    "pH ≥ 7.0",
                                    _flow_node(
                                        "Alkalinization OK<br/>(Emma: 7.1 ✅)",
                                        state="active green",
                                    ),
                                    state="green",
                                ),
                                _flow_branch(
                                    "pH &lt; 7.0",
                                    _flow_node("NaHCO₃ bolus branch"),
                                ),
                            ]
                        ),
                        2,
                    )
                )

    # ---- Checkpoint 3: Hour 36 ----
    exp36 = _checkpoint_expander(
        "Hour 36 (Mid-Clearance Surveillance) — MTX 8.40 (>3.0 🔴) | Cr 0.58 (+45% 🟡) | pH 7.0  ·  🔴 Early Rescue Branch",
        key=f"ck_{pid}_h36",
        expanded=False,
        icon=":material/emergency:",
    )
    with exp36:
        if exp36.open:
            st.html(
                _flow_tree(
                    "Hour 36 · Mid-Clearance",
                    _flow_node("<strong>Hour 36 STAT Draw</strong><br/>MTX 8.40 · Cr 0.58 · pH 7.0", state="root"),
                    "".join(
                        [
                            _flow_branch(
                                "MTX ≤ 3.0 µmol/L",
                                _flow_node("Wait until Hour 42<br/>for standard Leucovorin"),
                            ),
                            _flow_branch(
                                "MTX &gt; 3.0 µmol/L<br/>(Emma: 8.40)",
                                _flow_node(
                                    "🚨 Initiate Early IV Leucovorin Rescue<br/>"
                                    "<strong>15 mg/m² q6h</strong> Immediately<br/>"
                                    "+ Order Mandatory Hour 42 &amp; Hour 48<br/>Bleyer Levels"
                                    + _delta_html(
                                        "No Leucovorin running (due Hr 42)",
                                        "Start early IV Leucovorin 15 mg/m² q6h",
                                    ),
                                    state="active",
                                ),
                                state="active",
                            ),
                        ]
                    ),
                    2,
                )
            )

    # ---- Checkpoint 4: Hour 42 ----
    exp42 = _checkpoint_expander(
        "Hour 42 (Standard Rescue Gate) — MTX 5.20 (>1.0 🔴) | Cr 0.63 (+58% 🔴) | pH 6.9 (🔴)  ·  🔴 Triple Breach Branch",
        key=f"ck_{pid}_h42",
        expanded=False,
        icon=":material/emergency:",
    )
    with exp42:
        if exp42.open:
            a, b, c = st.columns(3)
            with a:
                st.html(
                    _flow_tree(
                        "MTX Rescue Arm",
                        _flow_node("<strong>Hour 42 MTX</strong><br/>5.20 µmol/L", state="root"),
                        "".join(
                            [
                                _flow_branch("MTX ≤ 1.0", _flow_node("Standard LV 15 mg/m²")),
                                _flow_branch(
                                    "MTX &gt; 1.0 (5.20)",
                                    _flow_node(
                                        "🔴 Escalate Leucovorin to<br/><strong>30 mg/m² IV q6h</strong>",
                                        state="active",
                                    ),
                                    state="active",
                                ),
                            ]
                        ),
                        2,
                    )
                )
            with b:
                st.html(
                    _flow_tree(
                        "Renal Arm",
                        _flow_node("<strong>Hour 42 Cr</strong><br/>0.63 (+58%)", state="root"),
                        "".join(
                            [
                                _flow_branch("&lt; 50% rise", _flow_node("Maintain fluids")),
                                _flow_branch(
                                    "≥ 50% rise (+58%)",
                                    _flow_node(
                                        "🔴 Stage 1 AKI Flagged<br/>— Escalate Hydration",
                                        state="active",
                                    ),
                                    state="active",
                                ),
                            ]
                        ),
                        2,
                    )
                )
            with c:
                st.html(
                    _flow_tree(
                        "pH Arm",
                        _flow_node("<strong>Hour 42 pH</strong><br/>6.9", state="root"),
                        "".join(
                            [
                                _flow_branch("pH ≥ 7.0", _flow_node("Continue bag HCO₃")),
                                _flow_branch(
                                    "pH &lt; 7.0 (6.9)",
                                    _flow_node(
                                        "🔴 Administer NaHCO₃<br/><strong>1 mEq/kg IV Bolus</strong>",
                                        state="active",
                                    ),
                                    state="active",
                                ),
                            ]
                        ),
                        2,
                    )
                )

    # ---- Checkpoint 5: Hour 48 ACTIVE ----
    exp48 = _checkpoint_expander(
        f"👉 Hour 48 (CURRENT ACTIVE GATE) — MTX {p['mtx']:.2f} (>0.40 🔴) | "
        f"Cr {p['cr']:.2f} (+70% 🔴) | pH {p['urine_ph']:.1f} (🔴) ·  🚨 3 ORDERS TO STAGE",
        key=f"ck_{pid}_h48",
        expanded=True,
        icon=":material/crisis_alert:",
    )
    with exp48:
        if exp48.open:
            st.caption(
                "Taken path = crisp semantic border · unselected branches are watermarked (hover to peek)"
            )
            t1, t2, t3 = st.columns(3)
            with t1:
                st.html(
                    _flow_tree(
                        "Tree 1 · Serum MTX",
                        _flow_node(
                            f"<strong>Hour 48 MTX Draw</strong><br/>{p['mtx']:.2f} µmol/L",
                            state="root",
                        ),
                        "".join(
                            [
                                _flow_branch(
                                    "≤ 0.40 µmol/L",
                                    _flow_node(
                                        "Continue Leucovorin<br/>15 mg/m² q6h × 3 doses"
                                    ),
                                ),
                                _flow_branch(
                                    "0.41 – 1.99 µmol/L",
                                    _flow_node("Leucovorin<br/>30 mg/m² IV q6h"),
                                ),
                                _flow_branch(
                                    f"2.0 – 19.9 µmol/L<br/>(Emma: {p['mtx']:.2f})",
                                    _flow_node(
                                        f"🚨 Escalate Leucovorin to<br/>"
                                        f"<strong>100 mg/m² ({lv_100} mg)</strong> IV q6h"
                                        f"<br/>+ STAT Hr 54 Level"
                                        + _delta_html(
                                            f"IV Leucovorin 30 mg/m² "
                                            f"({round(30 * bsa)} mg) IV q6h "
                                            f"(escalated at Hr 42)",
                                            f"Escalate to 100 mg/m² ({lv_100} mg) "
                                            f"IV q6h (+233% dose increase)",
                                        ),
                                        state="active",
                                    ),
                                    state="active",
                                ),
                                _flow_branch(
                                    "> 5.0 µmol/L + AKI",
                                    _flow_node(
                                        f"Glucarpidase (Voraxaze)<br/>"
                                        f"50 U/kg ({gluc:,} U) IV Gate",
                                        state="watch",
                                    ),
                                    state="watch",
                                ),
                            ]
                        ),
                        2,
                    )
                )
                _stage_branch_button(
                    key=f"ft_emma_mtx_{pid}",
                    label=f"⚡ Stage Order: Leucovorin {lv_100} mg IV q6h",
                    pid=pid,
                    title=f"Leucovorin {lv_100} mg IV q6h",
                    cdi="T45.1X5A",
                    cdi_label=(
                        "N17.9 Acute Kidney Injury [CC] + T45.1X5A Adverse "
                        "effect of antineoplastic therapy [MCC]"
                    ),
                    cdi_note=(
                        f"Linked to Cr {p['cr']:.2f} mg/dL (+70% from "
                        f"{p['cr_base']:.2f} baseline) & Hour-48 MTX "
                        f"{p['mtx']:.2f} µmol/L"
                    ),
                    order_lines=[
                        f"Leucovorin 100 mg/m² × {bsa} m² = {lv_100} mg IV q6h",
                        "Infuse over 15 min (Ca²⁺ content)",
                        "Continue until MTX < 0.10 µmol/L",
                        "Draw STAT Hour 54 MTX level",
                    ],
                    dosing_basis=f"BSA {bsa} m² · Wt {wt} kg",
                    order_id="emma_leucovorin",
                )
            with t2:
                cr_rise = round((p["cr"] / p["cr_base"] - 1) * 100)
                st.html(
                    _flow_tree(
                        "Tree 2 · Renal / Serum Cr",
                        _flow_node(
                            f"<strong>Hour 48 Serum Cr</strong><br/>"
                            f"{p['cr']:.2f} mg/dL (+{cr_rise}%)",
                            state="root",
                        ),
                        "".join(
                            [
                                _flow_branch(
                                    "&lt; 50% rise<br/>(&lt; 0.60 mg/dL)",
                                    _flow_node(
                                        "Maintain fluids at<br/>125–150 mL/m²/hr"
                                    ),
                                ),
                                _flow_branch(
                                    f"≥ 50% rise<br/>(Stage 1 AKI: +{cr_rise}%)",
                                    _flow_node(
                                        f"🚨 Escalate Hyperhydration to<br/>"
                                        f"<strong>200 mL/m²/hr ({hyd_200} mL/hr)</strong>"
                                        f"<br/>+ Strict q4h I&amp;O"
                                        + _delta_html(
                                            f"D5 0.2NS + 40 mEq/L NaHCO₃ at "
                                            f"150 mL/m²/hr ({hyd_150} mL/hr)",
                                            f"Escalate to 200 mL/m²/hr "
                                            f"({hyd_200} mL/hr) "
                                            f"(+{hyd_200 - hyd_150} mL/hr increase)",
                                        ),
                                        state="active",
                                    ),
                                    state="active",
                                ),
                            ]
                        ),
                        2,
                    )
                )
                _stage_branch_button(
                    key=f"ft_emma_cr_{pid}",
                    label=f"⚡ Stage Order: Hyperhydration {hyd_200} mL/hr",
                    pid=pid,
                    title=f"Hyperhydration {hyd_200} mL/hr",
                    cdi="N17.9 + T45.1X5A",
                    cdi_label=(
                        "N17.9 Acute Kidney Injury [CC] + T45.1X5A Adverse "
                        "effect of antineoplastic therapy [MCC]"
                    ),
                    cdi_note=(
                        f"Linked to Cr {p['cr']:.2f} mg/dL (+{cr_rise}% from "
                        f"{p['cr_base']:.2f} baseline) & Hour-48 MTX "
                        f"{p['mtx']:.2f} µmol/L"
                    ),
                    order_lines=[
                        f"D5 0.2NS + NaHCO₃ hyperhydration 200 mL/m²/hr "
                        f"× {bsa} m² = {hyd_200} mL/hr",
                        "Strict q4h I&Os & q12h weights",
                        f"Furosemide 0.5 mg/kg = {round(0.5 * wt)} mg IV "
                        "if weight > +1.0 kg",
                        "Hold all nephrotoxins",
                    ],
                    dosing_basis=f"BSA {bsa} m² · Wt {wt} kg",
                    order_id="emma_fluids",
                )
            with t3:
                st.html(
                    _flow_tree(
                        "Tree 3 · Urine Alkalinization",
                        _flow_node(
                            f"<strong>Bedside Urine Dipstick</strong><br/>"
                            f"pH {p['urine_ph']:.1f}",
                            state="root",
                        ),
                        "".join(
                            [
                                _flow_branch(
                                    "Urine pH ≥ 7.0",
                                    _flow_node(
                                        "Continue D5 0.2NS<br/>+ 40 mEq/L NaHCO₃"
                                    ),
                                ),
                                _flow_branch(
                                    f"Urine pH &lt; 7.0<br/>(pH {p['urine_ph']:.1f})",
                                    _flow_node(
                                        f"🚨 STAT NaHCO₃ 1 mEq/kg<br/>"
                                        f"<strong>({bicarb} mEq)</strong> IV Bolus"
                                        f"<br/>+ Increase Bag to 60 mEq/L"
                                        f"<br/>+ Recheck pH in 1h"
                                        + _delta_html(
                                            "Maintenance bag NaHCO₃ 40 mEq/L "
                                            "(Last bolus at Hr 42)",
                                            f"Give STAT NaHCO₃ {bicarb} mEq "
                                            f"(1 mEq/kg) IV Bolus + Increase "
                                            f"bag to 60 mEq/L",
                                        ),
                                        state="active",
                                    ),
                                    state="active",
                                ),
                            ]
                        ),
                        2,
                    )
                )
                _stage_branch_button(
                    key=f"ft_emma_ph_{pid}",
                    label=f"⚡ Stage Order: STAT NaHCO₃ {bicarb} mEq IV Bolus",
                    pid=pid,
                    title=f"STAT NaHCO₃ {bicarb} mEq IV Bolus",
                    cdi="T45.1X5A",
                    cdi_label=(
                        "N17.9 Acute Kidney Injury [CC] + T45.1X5A Adverse "
                        "effect of antineoplastic therapy [MCC]"
                    ),
                    cdi_note=(
                        f"Linked to urine pH {p['urine_ph']:.1f} & Hour-48 "
                        f"MTX {p['mtx']:.2f} µmol/L"
                    ),
                    order_lines=[
                        f"NaHCO₃ 1 mEq/kg × {wt} kg = {bicarb} mEq IV bolus "
                        "over 1 hour",
                        "Increase maintenance fluid NaHCO₃ from 40 to 60 mEq/L",
                        "Repeat urine dipstick pH in 1 hour",
                    ],
                    dosing_basis=f"Wt {wt} kg",
                    order_id="emma_bicarb",
                )
            so = p["stage_order"]
            _stage_branch_button(
                key=f"pw_stage_all_{pid}",
                label="⚡ Stage All Hour-48 Rescue Orders",
                pid=pid,
                title="Hour 48 triple rescue — LV + hyperhydration + NaHCO₃",
                cdi=so["cdi_code"],
                cdi_label=so["cdi_label"],
                cdi_note=so["cdi_note"],
                order_lines=list(so["orders"]),
                dosing_basis=f"BSA {bsa} m² · Wt {wt} kg",
                order_id="emma_bundle",
            )

    # ---- Checkpoint 6: Hour 54 ----
    exp54 = _checkpoint_expander(
        "Hour 54 (Next Scheduled Gate — Due 14:00) — Target MTX ≤ 0.25 | Cr < 0.60 | pH ≥ 7.0  ·  ⏳ Contingency Tree",
        key=f"ck_{pid}_h54",
        expanded=False,
        icon=":material/schedule:",
    )
    with exp54:
        if exp54.open:
            st.html(
                _flow_tree(
                    "Hour 54 · Forward Contingency",
                    _flow_node(
                        "<strong>Hour 54 STAT MTX + BMP</strong><br/>Due 14:00 today",
                        state="root",
                    ),
                    "".join(
                        [
                            _flow_branch(
                                "Branch A<br/>MTX &lt; 2.0 &amp; Cr stable",
                                _flow_node(
                                    f"Continue High-Dose Leucovorin<br/>"
                                    f"<strong>{lv_100} mg IV q6h</strong><br/>"
                                    f"+ {hyd_200} mL/hr Fluids",
                                    state="watch",
                                ),
                                state="watch",
                            ),
                            _flow_branch(
                                "Branch B 🧬<br/>MTX ≥ 2.0–5.0 OR Cr &gt; 0.75",
                                _flow_node(
                                    f"🚨 Administer Glucarpidase (Voraxaze)<br/>"
                                    f"50 U/kg (<strong>{gluc:,} Units</strong>) IV over 5 min<br/>"
                                    f"(Hold Leucovorin 2h Before &amp; After)",
                                    state="active",
                                ),
                                state="active",
                            ),
                        ]
                    ),
                    2,
                )
            )

    # ---- Checkpoint 7: Hour 72+ ----
    exp72 = _checkpoint_expander(
        "Hour 72+ (Final Clearance & Discharge Gate) — Target MTX < 0.10 µmol/L  ·  🏁 Discharge Tree",
        key=f"ck_{pid}_h72",
        expanded=False,
        icon=":material/flag:",
    )
    with exp72:
        if exp72.open:
            st.html(
                _flow_tree(
                    "Hour 72+ · Clearance & Discharge",
                    _flow_node("<strong>q24h MTX &amp; BMP</strong>", state="root"),
                    "".join(
                        [
                            _flow_branch(
                                "MTX ≥ 0.10 µmol/L",
                                _flow_node(
                                    "Continue Inpatient IV Fluids<br/>&amp; q6h Leucovorin"
                                ),
                            ),
                            _flow_branch(
                                "MTX &lt; 0.10 + Cr baseline<br/>+ Tolerating PO",
                                _flow_node(
                                    "🟢 Stop Leucovorin &amp; IV Fluids<br/>→ Cleared for Discharge",
                                    state="active green",
                                ),
                                state="green",
                            ),
                        ]
                    ),
                    2,
                )
            )


def render_maya_pathway(p: dict) -> None:
    dose = round(25 * p["wt"])
    pid = p["id"]
    st.markdown(f"**{p['name']}** · {p['protocol']}")
    st.markdown("### Protocol checkpoints — click any row to expand its decision-tree")
    st.caption("Active IV→PO switch gate opens by default")

    exp0 = _checkpoint_expander(
        "Checkpoint 1: Admission ED Sepsis & IV Ceftriaxone Gate (0h)  ·  ✅ Gate Passed",
        key=f"ck_{pid}_adm",
        expanded=False,
        icon=":material/check_circle:",
    )
    with exp0:
        if exp0.open:
            st.html(
                _flow_tree(
                    "0h · ED Sepsis & Empiric IV",
                    _flow_node(
                        "<strong>ED Presentation</strong><br/>Febrile UTI / pyelo concern",
                        state="root",
                    ),
                    "".join(
                        [
                            _flow_branch(
                                "Sepsis pathway",
                                _flow_node(
                                    "Cultures + fluid bolus<br/>+ Empiric <strong>IV Ceftriaxone</strong>",
                                    state="active green",
                                ),
                                state="green",
                            ),
                            _flow_branch(
                                "Low-risk outpatient",
                                _flow_node("PO first-line (not selected)"),
                            ),
                        ]
                    ),
                    2,
                )
            )

    exp24 = _checkpoint_expander(
        "Checkpoint 2: 24h Fever & Renal Ultrasound Gate (24h)  ·  ✅ Improving",
        key=f"ck_{pid}_24h",
        expanded=False,
        icon=":material/check_circle:",
    )
    with exp24:
        if exp24.open:
            st.html(
                _flow_tree(
                    "24h · Fever & Imaging",
                    _flow_node("<strong>Hospital Day 1</strong><br/>On IV Ceftriaxone", state="root"),
                    "".join(
                        [
                            _flow_branch(
                                "Still febrile / toxic",
                                _flow_node("Broaden coverage / ID consult"),
                            ),
                            _flow_branch(
                                "Defervescing + RUS OK",
                                _flow_node(
                                    "✅ Fever trending down<br/>Renal US without abscess<br/>Continue IV → plan PO switch",
                                    state="active green",
                                ),
                                state="green",
                            ),
                        ]
                    ),
                    2,
                )
            )

    exp48 = _checkpoint_expander(
        f"👉 Checkpoint 3: 48h IV-to-PO Switch & Susceptibility Gate "
        f"({p['afebrile_hours']}h Afebrile + Pansensitive E. coli) ·  🚨 ACTIVE GATE",
        key=f"ck_{pid}_switch",
        expanded=True,
        icon=":material/medication:",
    )
    with exp48:
        if exp48.open:
            st.html(
                '<div class="ftree">'
                '<div class="ftree-title">48h · IV→PO Switch Algorithm</div>'
                + _flow_node(
                    "<strong>Admission Febrile UTI</strong><br/>on IV Ceftriaxone",
                    state="root",
                )
                + _flow_arrow("root")
                + _flow_node(
                    f"Afebrile ≥ 24h?<br/>(Maya: {p['afebrile_hours']}h ✅)",
                    state="active green",
                    shape="diamond",
                )
                + _flow_arrow("green")
                + _flow_node(
                    "Tolerating PO Fluids?<br/>(Maya: Yes ✅)",
                    state="active green",
                    shape="diamond",
                )
                + _flow_arrow("green")
                + _flow_node(
                    "Urine Cx Pansensitive?<br/>(Maya: E. coli Cefazolin S ✅)",
                    state="active green",
                    shape="diamond",
                )
                + _flow_arrow("green")
                + '<div class="fbranches cols-2">'
                + _flow_branch(
                    "If febrile or resistant",
                    _flow_node("Continue IV / Escalate<br/>to Ertapenem"),
                )
                + _flow_branch(
                    "All gates passed",
                    _flow_node(
                        f"🟢 Discontinue IV Ceftriaxone<br/>"
                        f"&amp; Stage <strong>PO Cephalexin<br/>"
                        f"25 mg/kg TID ({dose} mg)</strong><br/>for Discharge"
                        + _delta_html(
                            f"IV Ceftriaxone 50 mg/kg ({round(50 * p['wt'])} mg) "
                            f"IV q24h + Maintenance IVF at 55 mL/hr",
                            f"Discontinue IV Ceftriaxone &amp; Saline Lock PIV → "
                            f"Start PO Cephalexin 25 mg/kg/dose ({dose} mg) TID "
                            f"× 8 remaining days",
                        ),
                        state="active green",
                    ),
                    state="green",
                )
                + "</div></div>"
            )
            so = p["stage_order"]
            _stage_branch_button(
                key=f"ft_maya_po_{pid}",
                label="⚡ Stage Order: Switch to PO Cephalexin 25 mg/kg TID",
                pid=pid,
                title=f"PO Cephalexin {dose} mg TID",
                cdi=so["cdi_code"],
                cdi_label=so["cdi_label"],
                cdi_note=so["cdi_note"],
                order_lines=list(so["orders"]),
                dosing_basis=f"Wt {p['wt']} kg · 25 mg/kg/dose TID = {dose} mg",
                order_id="maya_po_switch",
            )

    exp_dc = _checkpoint_expander(
        "Checkpoint 4: Discharge & 10-Day PO Completion Gate  ·  ⏳ Upcoming Gate",
        key=f"ck_{pid}_dc",
        expanded=False,
        icon=":material/schedule:",
    )
    with exp_dc:
        if exp_dc.open:
            st.html(
                _flow_tree(
                    "Discharge · 10-Day PO Course",
                    _flow_node(
                        f"<strong>PO Cephalexin {dose} mg TID</strong><br/>10 days total",
                        state="root",
                    ),
                    "".join(
                        [
                            _flow_branch(
                                "Fever returns / intolerance",
                                _flow_node("Return precautions · reassess IV"),
                            ),
                            _flow_branch(
                                "Completes 10-day course",
                                _flow_node(
                                    "🟢 Outpatient follow-up<br/>PCP / urology as indicated",
                                    state="active green",
                                ),
                                state="green",
                            ),
                        ]
                    ),
                    2,
                )
            )


def render_chloe_pathway(p: dict) -> None:
    pid = p["id"]
    st.markdown(f"**{p['name']}** · {p['protocol']}")
    st.markdown("### Protocol checkpoints — click any row to expand its decision-tree")
    st.caption("Day 3 cross-parameter crisis gate opens by default")

    exp1 = _checkpoint_expander(
        "Checkpoint 1: Day 1 Admission & 1,200 kcal Initiation Gate  ·  ✅ Gate Passed",
        key=f"ck_{pid}_d1",
        expanded=False,
        icon=":material/check_circle:",
    )
    with exp1:
        if exp1.open:
            st.html(
                _flow_tree(
                    "Day 1 · Refeeding Initiation",
                    _flow_node(
                        "<strong>Admission</strong><br/>Severe malnutrition · start refeeding",
                        state="root",
                    ),
                    "".join(
                        [
                            _flow_branch(
                                "Start 1,200 kcal/day",
                                _flow_node(
                                    "✅ Initiate supervised nutrition<br/>+ daily BMP / Phos / Mg / K<br/>+ orthostatics",
                                    state="active green",
                                ),
                                state="green",
                            ),
                            _flow_branch(
                                "Too unstable",
                                _flow_node("ICU / NPO hold (not selected)"),
                            ),
                        ]
                    ),
                    2,
                )
            )

    exp2 = _checkpoint_expander(
        "Checkpoint 2: Day 2 Caloric Advancement (1,400 kcal) & Electrolyte Gate  ·  ✅ Advanced",
        key=f"ck_{pid}_d2",
        expanded=False,
        icon=":material/check_circle:",
    )
    with exp2:
        if exp2.open:
            st.html(
                _flow_tree(
                    "Day 2 · Caloric Advance",
                    _flow_node("<strong>Day 2</strong><br/>Advance toward 1,400 kcal/day", state="root"),
                    "".join(
                        [
                            _flow_branch(
                                "Electrolytes OK",
                                _flow_node(
                                    "✅ Advance calories<br/>Continue q12–24h labs",
                                    state="active green",
                                ),
                                state="green",
                            ),
                            _flow_branch(
                                "Phos / K / Mg dropping",
                                _flow_node("Hold advance · replete electrolytes"),
                            ),
                        ]
                    ),
                    2,
                )
            )

    exp3 = _checkpoint_expander(
        f"👉 Checkpoint 3: Day 3 Cross-Parameter Crisis Gate "
        f"(HR Nadir {p['hr_nadir']} bpm + Phos {p['phos']} mg/dL) ·  🚨 ACTIVE GATE",
        key=f"ck_{pid}_d3",
        expanded=True,
        icon=":material/crisis_alert:",
    )
    with exp3:
        if exp3.open:
            st.html(
                '<div class="ftree">'
                '<div class="ftree-title">Day 3 · Dual-Gate Crisis Algorithm</div>'
                + _flow_node(
                    f"<strong>Day 3 Refeeding</strong><br/>{p['kcal']:,} kcal/day",
                    state="root",
                )
                + _flow_arrow("root")
                + '<div class="fbranches cols-2">'
                + _flow_branch(
                    "Cardiac branch",
                    (
                        _flow_node(
                            f"<strong>Overnight HR Nadir</strong><br/>{p['hr_nadir']} bpm",
                            state="root",
                        )
                        + _flow_arrow("active")
                        + _flow_node(
                            "🔴 HR &lt; 45 bpm Gate Triggered",
                            state="active",
                            shape="diamond",
                        )
                        + _flow_arrow("active")
                        + _flow_node(
                            "🚨 Continuous Telemetry<br/>+ Hold Caloric Advancement"
                            f"<br/>at {p['kcal']:,} kcal/day<br/>+ 12-Lead ECG"
                            + _delta_html(
                                f"Advancing diet ({p['kcal']:,} → 1,900 kcal/day "
                                f"scheduled) + Q4h routine vitals",
                                f"Hold caloric advancement at {p['kcal']:,} kcal/day "
                                f"+ Place on continuous cardiac telemetry + "
                                f"STAT 12-lead ECG",
                            ),
                            state="active",
                        )
                    ),
                    state="active",
                )
                + _flow_branch(
                    "Electrolyte branch",
                    (
                        _flow_node(
                            f"<strong>Serum Phos</strong><br/>{p['phos']} mg/dL (↓ from 3.1)",
                            state="root",
                        )
                        + _flow_arrow("active")
                        + _flow_node(
                            "🔴 Phos &lt; 2.5 mg/dL Gate Triggered",
                            state="active",
                            shape="diamond",
                        )
                        + _flow_arrow("active")
                        + _flow_node(
                            "🚨 Stage IV Sodium Phosphate<br/>"
                            "<strong>0.5 mmol/kg over 6h</strong><br/>"
                            "+ Recheck in 4h"
                            + _delta_html(
                                "PO Phos-NaK 1 packet TID (Oral maintenance)",
                                f"Escalate to IV Sodium Phosphate 0.5 mmol/kg "
                                f"({round(0.5 * p['wt'])} mmol) IV over 6h + "
                                f"Recheck Phos in 4h",
                            ),
                            state="active",
                        )
                    ),
                    state="active",
                )
                + "</div></div>"
            )
            so = p["stage_order"]
            b1, b2 = st.columns(2)
            with b1:
                _stage_branch_button(
                    key=f"ft_chloe_hr_{pid}",
                    label="⚡ Stage Order: Hold Calorie Advance & Start Telemetry",
                    pid=pid,
                    title="Hold Calorie Advance & Start Telemetry",
                    cdi=so["cdi_code"],
                    cdi_label=so["cdi_label"],
                    cdi_note=so["cdi_note"],
                    order_lines=[
                        f"HOLD caloric advancement at {p['kcal']:,} kcal/day",
                        "Continuous cardiac telemetry",
                        "Obtain 12-lead ECG",
                    ],
                    dosing_basis=f"Wt {p['wt']} kg · Day 3 refeeding",
                    order_id="chloe_telemetry",
                )
            with b2:
                _stage_branch_button(
                    key=f"ft_chloe_phos_{pid}",
                    label="⚡ Stage Order: NaPhos 0.5 mmol/kg IV over 6h",
                    pid=pid,
                    title="NaPhos 0.5 mmol/kg IV over 6h",
                    cdi=so["cdi_code"],
                    cdi_label=so["cdi_label"],
                    cdi_note=so["cdi_note"],
                    order_lines=list(so["orders"]),
                    dosing_basis=f"Wt {p['wt']} kg · Phos {p['phos']} mg/dL",
                    order_id="chloe_phos",
                )

    exp4 = _checkpoint_expander(
        "Checkpoint 4: Stabilization & Telemetry Wean Gate  ·  ⏳ Upcoming Gate",
        key=f"ck_{pid}_wean",
        expanded=False,
        icon=":material/schedule:",
    )
    with exp4:
        if exp4.open:
            st.html(
                _flow_tree(
                    "Stabilization · Telemetry Wean",
                    _flow_node(
                        "<strong>Post-crisis monitoring</strong><br/>Phos / HR / calorie hold",
                        state="root",
                    ),
                    "".join(
                        [
                            _flow_branch(
                                "HR still &lt; 45 or Phos &lt; 2.5",
                                _flow_node("Continue telemetry + repletion"),
                            ),
                            _flow_branch(
                                "HR ≥ 45 &amp; Phos ≥ 2.5 × 24h",
                                _flow_node(
                                    "🟢 Wean telemetry<br/>Cautious caloric restart",
                                    state="active green",
                                ),
                                state="green",
                            ),
                        ]
                    ),
                    2,
                )
            )


KD_UNLIKELY_BOX = (
    "KD unlikely: Perform serial clinical and laboratory re-evaluation if "
    "fever persists and obtain echocardiogram‡ if typical periungual "
    "desquamation develops even if fever has resolved"
)


def _leo_eval_suspected_kd_html(
    p: dict,
    *,
    ivig: int,
    asa_q6h: int,
    apap: int,
    maint: int,
) -> str:
    """3-branch Evaluation of Suspected KD — Incomplete KD center path active."""
    tmax_f = round(float(p["tmax"]) * 9 / 5 + 32, 1)
    supp = int(p.get("supp_labs_met", 5))
    kd_unlikely = _flow_node(KD_UNLIKELY_BOX)
    treat_incomplete_wm = _flow_node("Incomplete KD: Start treatment‡")

    # ---- LEFT: 0–1 criteria (watermarked) ----
    echo_splits = (
        '<div class="fbranches cols-2">'
        + _flow_branch("Positive echocardiogram¥", treat_incomplete_wm)
        + _flow_branch(
            "Negative echocardiogram",
            _flow_node(
                "Suspected incomplete KD: Assess for supplemental laboratory "
                "criteria§ in addition to CRP/ESR and monitor closely including "
                "serial echocardiograms until KD is diagnosed and treatment "
                "started or until patient is afebrile and otherwise well for "
                "48 hours"
            ),
        )
        + "</div>"
    )
    infant_yes = (
        _flow_node("Possible KD: Obtain baseline echocardiogram")
        + _flow_arrow("dim")
        + echo_splits
    )
    left_branch = _flow_branch(
        "0 or 1 clinical criteria<br/>"
        "<em>(Leo: Not taken — 2/5 met)</em>",
        _flow_node("Is the child ≤6 months old◊ with a fever ≥7 days?")
        + _flow_arrow("dim")
        + '<div class="fbranches cols-2">'
        + _flow_branch("Yes", infant_yes)
        + _flow_branch("No", kd_unlikely)
        + "</div>",
    )

    # ---- RIGHT: ≥4 Complete KD (watermarked — not taken) ----
    right_branch = _flow_branch(
        "≥4 clinical criteria¶<br/>"
        "<em>(Leo: Not taken — only 2 of 5 clinical criteria)</em>",
        _flow_node(
            "<strong>Consistent with Complete KD: Start treatment and obtain "
            "baseline echocardiogram</strong><br/><br/>"
            "≥4 clinical criteria¶ → start treatment directly "
            "(No CRP/ESR or supplemental lab algorithm required when ≥4 "
            "clinical criteria are met).<br/><br/>"
            "<em>[Not taken — Leo only meets 2 of 5 clinical criteria].</em>"
        ),
    )

    # ---- CENTER: 2–3 Incomplete KD (ACTIVE taken path) ----
    terminal = _flow_node(
        "🚨 <strong>Incomplete KD Confirmed (≥3 Supplemental Lab Criteria Met) "
        "— Start treatment‡</strong>"
        + leo_supp_labs_side_by_side_html(p)
        + _delta_html(
            f"PRN Acetaminophen 15 mg/kg ({apap} mg) PO q6h + Maintenance D5NS "
            f"at {maint} mL/hr (No disease-modifying therapy started)",
            f"Start Weight-Based IVIG 2 g/kg ({ivig} g) IV over 10–12h + "
            f"High-Dose Aspirin 80–100 mg/kg/day divided q6h ({asa_q6h} mg PO "
            f"q6h) + Obtain Baseline Echocardiogram (Treatment triggered by "
            f"{supp}/6 positive supplemental labs§ without waiting for Echo)",
        ),
        state="active",
    )
    supp_gate = (
        _flow_node(
            "<strong>Assess for supplemental laboratory criteria§ and obtain "
            "echocardiogram</strong>"
            + _flow_compare_html(
                "AHA Requirement",
                "≥3 of 6 supplemental laboratory criteria§ "
                "<strong>or</strong> positive echocardiogram¥",
                "Leo Kim",
                f'<span class="fcmp-badge-red">🔴 {supp} of 6 supplemental '
                "labs positive§</span> (exceeds ≥3 cutoff; echo ordered — "
                "do not delay IVIG)",
            ),
            state="active",
        )
        + _flow_arrow("active")
        + '<div class="fbranches cols-2">'
        + _flow_branch(
            "&lt;3 supplemental laboratory criteria and negative echocardiogram",
            kd_unlikely,
        )
        + _flow_branch(
            "≥3 supplemental laboratory criteria or positive echocardiogram¥",
            terminal,
            state="active",
        )
        + "</div>"
    )
    crp_gate = (
        _flow_node(
            "<strong>Suspected incomplete KD: Assess CRP/ESR</strong>"
            + _flow_compare_html(
                "AHA Cutoff: CRP ≥3.0 mg/dL or ESR ≥40 mm/h",
                "CRP ≥3.0 mg/dL <strong>and/or</strong> ESR ≥40 mm/hour "
                "→ proceed to supplemental labs§ + echo",
                "Leo Kim Actual Values",
                f'<span class="fcmp-badge-red">🔴 Both Positive: '
                f"CRP {p['crp']} mg/dL &amp; ESR {p['esr']} mm/h</span>",
            ),
            state="active",
        )
        + _flow_arrow("active")
        + '<div class="fbranches cols-2">'
        + _flow_branch(
            "CRP &lt;3.0 mg/dL and ESR &lt;40 mm/hour",
            kd_unlikely,
        )
        + _flow_branch(
            "CRP ≥3.0 mg/dL and/or ESR ≥40 mm/hour",
            supp_gate,
            state="active",
        )
        + "</div>"
    )
    center_branch = _flow_branch(
        "2 or 3 clinical criteria and a strong clinical suspicion of KD<br/>"
        f'<span class="fcmp-badge-red">🔴 Leo Kim ACTIVE PATH — '
        f"{p['criteria_met']} of 5 criteria</span>",
        _flow_node(
            "<strong>2 or 3 clinical criteria and a strong clinical suspicion "
            "of KD</strong>"
            + _flow_compare_html(
                "AHA Requirement: 2 or 3 of 5 criteriaΔ",
                "Fever ≥5 days¶ with 2–3 clinical diagnostic criteriaΔ and "
                "strong clinical suspicion → enter Incomplete KD lab algorithm",
                "Leo Kim Clinical Criteria",
                f'<span class="fcmp-badge-red">🔴 Leo Kim: {p["criteria_met"]} '
                "of 5 Positive</span> (Bilateral non-exudative conjunctivitis + "
                "Polymorphous rash; Absent oral, extremity, and ≥1.5 cm node "
                "criteria)",
            ),
            state="active amber",
        )
        + _flow_arrow("active")
        + crp_gate,
        state="active",
    )

    entry = _flow_node(
        "<strong>Child* with a fever for ≥5 days¶ without an alternative "
        "explanation</strong><br/>"
        f'<span class="kd-rule-leo" style="display:inline-block;margin-top:8px;">'
        f"🔴 Leo Kim: Day {p['fever_day']} Unexplained Fever "
        f"(Tmax {p['tmax']}°C / {tmax_f}°F)</span>",
        state="root",
    )
    gate = _flow_node(
        "<strong>How many clinical diagnostic criteriaΔ are met?</strong>"
        + _flow_compare_html(
            "Clinical criteria count",
            "0–1 → infant/echo gate · 2–3 → Incomplete KD lab algorithm · "
            "≥4 → Complete KD treat directly",
            "Leo Kim Status",
            f'<span class="fcmp-badge-red">🔴 Leo: {p["criteria_met"]} of 5 '
            "criteria met</span> (Conjunctivitis + Rash) — "
            "<strong>center Incomplete KD branch is active</strong>",
        ),
        state="root",
    )

    return (
        '<div class="ftree">'
        '<div class="ftree-title">Evaluation of Suspected Kawasaki Disease '
        "(Incomplete KD — Center Branch Active)</div>"
        + entry
        + _flow_arrow("root")
        + gate
        + _flow_arrow("root")
        + '<div class="fbranches cols-3">'
        + left_branch
        + center_branch
        + right_branch
        + "</div></div>"
    )


def render_leo_kd_algorithm_footnotes(p: dict) -> None:
    """Expandable algorithm footnotes (*, ¶, Δ, ◊, §, ¥, ‡)."""
    exp = st.expander(
        "📖 Algorithm Footnotes & Definitions (*, ¶, Δ, ◊, §, ¥, ‡)",
        expanded=False,
        key=f"kd_footnotes_{p['id']}",
        icon=":material/menu_book:",
        on_change="rerun",
        width="stretch",
    )
    with exp:
        if not exp.open:
            return
        st.html(
            '<div class="kd-rule-box">'
            "<strong>Abbreviations</strong><br/>"
            "ALT: alanine aminotransferase; CRP: C-reactive protein; "
            "ESR: erythrocyte sedimentation rate; hpf: high-power field; "
            "KD: Kawasaki disease; WBC: white blood cell."
            "</div>"
        )
        st.markdown(
            "**\\*** KD most commonly occurs in children over 6 months up to "
            "5 years of age, although it can occur in young infants, older "
            "children, and adults."
        )
        st.markdown(
            "**¶** The diagnosis of KD can be made with 4 days of fever if ≥4 "
            "clinical criteria are present, particularly the peripheral "
            "extremity changes. Rarely, an experienced clinician can make the "
            "diagnosis with only 3 days of fever. However, patients who "
            "receive early treatment before 5 days of illness are more likely "
            "to fail initial IVIG therapy. A significant proportion of "
            "children with KD have a concurrent infection; therefore, "
            "ascribing the fever to such an infection or to KD requires "
            "clinical judgment."
        )
        st.markdown("**Δ Clinical diagnostic criteria for KD**")
        for i, item in enumerate(_leo_kd_principal_criteria(), 1):
            st.markdown(f"{i}. {item['criterion']}")
        st.markdown(
            "**◊** Infants ≤6 months of age with KD are more likely to lack "
            "clinical features of KD other than fever and are at increased "
            "risk for coronary artery aneurysms. Thus, there is a lower "
            "threshold for treatment in this population. Some groups include "
            "all infants ≤12 months as high risk, although the risks of an "
            "atypical presentation and of IVIG resistance decrease "
            "significantly between 6 to 12 months of age."
        )
        st.markdown(
            "**§ Supplemental laboratory criteria** (side-by-side with Leo's "
            "color-coded values)"
        )
        st.html(leo_supplemental_lab_cards_html(p))
        st.markdown(
            "**¥** Echocardiogram is considered positive if the Z-score of the "
            "left anterior descending coronary artery or right coronary artery "
            "is ≥2.5, a coronary artery aneurysm is observed, or ≥3 other "
            "suggestive features exist including decreased left ventricular "
            "function, mitral regurgitation, pericardial effusion, or Z-scores "
            "in the left anterior descending coronary artery or right coronary "
            "artery of 2 to 2.5."
        )
        st.markdown(
            "**‡** For patients with incomplete KD and a positive "
            "echocardiogram, treatment should be given if the patient is still "
            "within 10 days of fever onset, the fever is still present after "
            "10 days, the patient has clinical or laboratory signs of ongoing "
            "inflammation, or the coronary arteries are continuing to dilate "
            "despite a lack of fever, inflammation, or clinical signs of KD."
        )


def render_leo_pathway(p: dict) -> None:
    """Evaluation of Suspected Kawasaki Disease — 3-branch clinical algorithm."""
    wt = float(p["wt"])
    ivig = round(2 * wt)  # 26 g at 13.0 kg
    asa_q6h = round(20 * wt)  # 260 mg
    asa_day = round(80 * wt)
    apap = round(15 * wt)  # 195 mg
    maint = int(p.get("maint_ivf", 46))
    pid = p["id"]
    so = p["stage_order"]

    st.markdown(
        f"**{p['name']}** · {p['age']} {p['sex']} · Wt **{wt:g} kg** · "
        f"Room {p['room']} · {p['protocol']}"
    )
    st.caption(
        "Evaluation of suspected Kawasaki disease · "
        "**center Incomplete KD branch** (2–3 criteria → CRP/ESR → ≥3 "
        "supplemental labs) taken at 100% contrast · "
        "0–1 and ≥4 arms watermarked at 70% opacity"
    )

    with st.container(border=True):
        st.markdown("**Diagnostic requirement &amp; Incomplete KD confirmation**")
        st.html(leo_kd_rule_banner_html(p))
        st.html(leo_kd_criteria_side_by_side_html())
        st.warning(
            f"**Summary:** {p['criteria_met']} of 5 clinical criteriaΔ "
            "(conjunctivitis + rash) → Incomplete KD lab pathway; "
            f"CRP {p['crp']} / ESR {p['esr']} + "
            f"{p.get('supp_labs_met', 5)}/6 supplemental labs → "
            "**Start IVIG + ASA**",
            title="Incomplete KD path active",
        )
        st.html(leo_inflam_lab_panel_html(p))

    st.markdown("### Evaluation of Suspected Kawasaki Disease")
    st.html(
        _leo_eval_suspected_kd_html(
            p,
            ivig=ivig,
            asa_q6h=asa_q6h,
            apap=apap,
            maint=maint,
        )
    )
    _stage_branch_button(
        key=f"ft_leo_ivig_{pid}",
        label=f"⚡ Stage Order: IVIG {ivig} g IV + High-Dose ASA + Echo",
        pid=pid,
        title=f"IVIG {ivig} g IV + High-Dose ASA + Echo",
        cdi=so["cdi_code"],
        cdi_label=so["cdi_label"],
        cdi_note=so["cdi_note"],
        order_lines=list(so["orders"]),
        dosing_basis=(
            f"Wt {wt:g} kg · IVIG 2 g/kg = {ivig} g · "
            f"ASA {asa_q6h} mg PO q6h ({asa_day} mg/day)"
        ),
        order_id="leo_ivig",
    )

    render_leo_kd_algorithm_footnotes(p)


@st.dialog("🔗 Clinical Pathway & Decision Tree", width="large")
def pathway_dialog(p: dict) -> None:
    st.caption(p.get("protocol", ""))
    arch = p.get("archetype")
    if arch == "mtx":
        render_emma_pathway(p)
    elif arch == "pyelo":
        render_maya_pathway(p)
    elif arch == "refeeding":
        render_chloe_pathway(p)
    elif arch == "kawasaki":
        render_leo_pathway(p)
    else:
        st.info("No pathway map on file for this patient.")


# ---------------------------------------------------------------------------
# Stage Order + AutoCDI dialog (right drawer)
# ---------------------------------------------------------------------------
@st.dialog(
    "🛡️ Human-in-the-Loop · Send to Epic for Signature",
    width="large",
    position="right",
)
def stage_order_dialog(p: dict) -> None:
    so = p["stage_order"]
    pid = p["id"]
    dosing = f"Wt {p.get('wt', '—')} kg" + (
        f" · BSA {p['bsa']} m²" if p.get("bsa") else ""
    )
    _epic_composer_interactive(p, dosing_basis=dosing)
    st.divider()
    _autocdi_card(so["cdi_label"], so["cdi_note"])
    st.checkbox(
        "Attending attests clinical validity of CDI language",
        key=f"cdi_attest_{pid}",
    )
    signed_n, total_n = patient_signing_progress(pid)
    unsigned_n = max(total_n - signed_n, 0)
    if unsigned_n > 0:
        if st.button(
            f"✍️ Sign All Orders ({unsigned_n} Remaining) & Check Off All Handoff Items",
            type="primary",
            width="stretch",
            key=f"sign_all_{pid}",
        ):
            sign_all_patient_orders(p)
            st.rerun()
    elif st.button(
        "✅ All Orders Signed in Epic (Click to Reset All)",
        width="stretch",
        key=f"reset_all_{pid}",
    ):
        reset_all_patient_orders(p)
        st.rerun()


def _bundle_short_name(p: dict) -> str:
    arch = p.get("archetype")
    if arch == "mtx":
        return "Hour-48 Rescue Bundle"
    if arch == "pyelo":
        return "PO Cephalexin Switch"
    if arch == "refeeding":
        return "IV Phos & Telemetry"
    if arch == "kawasaki":
        return "IVIG + High-Dose ASA"
    return p["stage_order"]["title"]


def _main_stage_label(p: dict) -> str:
    signed_n, total_n = patient_signing_progress(p["id"])
    bundle = _bundle_short_name(p)
    if total_n == 0:
        return f"⚡ Send to Epic for Signature: {bundle}"
    if signed_n <= 0:
        return f"⚡ Send to Epic for Signature: {bundle} (0/{total_n} Signed)"
    if signed_n < total_n:
        return (
            f"⚡ Send to Epic for Signature: {bundle} "
            f"({signed_n}/{total_n} Signed · In Progress)"
        )
    return f"✅ All Orders Signed in Epic ({signed_n}/{total_n} Signed · Dr. Patel)"


def render_stage_order_cta(p: dict) -> None:
    overlay = st.session_state.get(f"status_overlay_{p['id']}")
    signed_n, total_n = patient_signing_progress(p["id"])
    label = _main_stage_label(p)
    btn_type = "primary" if signed_n < total_n else "secondary"
    if st.button(
        label,
        type=btn_type,
        width="stretch",
        key=f"open_stage_{p['id']}",
    ):
        stage_order_dialog(p)
    if signed_n >= total_n > 0:
        st.success(
            f"✅ All {total_n} orders signed in Epic · ready for nursing",
            title="Epic cart complete",
        )
        if overlay:
            st.caption(f":green[**Live intervention:** {overlay}]")
    elif signed_n > 0:
        st.caption(
            f":orange[**In progress:** {signed_n}/{total_n} orders signed — "
            "open composer to finish or undo individual lines.]"
        )
        if overlay:
            st.caption(f":green[**Latest:** {overlay}]")


# ---------------------------------------------------------------------------
# Narrative + checklists
# ---------------------------------------------------------------------------
def _patient_banner_line(p: dict) -> str:
    """Single clean diagnosis/protocol line (no duplicated Day strings)."""
    if p.get("banner_line"):
        return str(p["banner_line"])
    arch = p.get("archetype")
    if arch == "pyelo":
        return (
            f"Febrile Pyelonephritis · IV→PO De-escalation · "
            f"Afebrile {p.get('afebrile_hours', 30)}h"
        )
    if arch == "refeeding":
        return (
            "Anorexia Nervosa · Refeeding Syndrome Crisis · "
            f"Day 3 · {p.get('kcal', 1600):,} kcal plateau"
        )
    if arch == "kawasaki":
        return (
            f"Incomplete Kawasaki Disease · Day {p.get('fever_day', 6)} Fever · "
            "2/5 Criteria → Lab Gate"
        )
    return f"{p.get('diagnosis', '')} · {p.get('protocol', '')}"


def patient_synthesis_blocks(p: dict) -> dict:
    """Structured synthesis: one-liner, running state, escalation callout."""
    arch = p.get("archetype")
    access = p.get("access", "—")
    if arch == "mtx":
        return {
            "one_liner": (
                f"{p['name']} is an {p['age']} {p['sex']} ({p['wt']} kg, "
                f"BSA {p['bsa']} m²) with high-risk B-ALL at Hour {p['hour']} "
                f"post HD-MTX. Serum MTX is critically elevated at "
                f"{p['mtx']:.2f} µmol/L (≤0.40 cutoff) with Stage 1 AKI "
                f"(Cr {p['cr']:.2f}, +70%) and acidic urine pH {p['urine_ph']:.1f}."
            ),
            "running": [
                "Leucovorin: 29 mg IV q6h (escalate → 98 mg)",
                "IVF: D5 0.2NS + 40 mEq/L NaHCO₃ at 147 mL/hr",
                f"Access: {access}",
            ],
            "escalation": (
                "Escalate Leucovorin to 100 mg/m² (98 mg) IV q6h · "
                "Hyperhydrate at 200 mL/m²/hr (196 mL/hr) · "
                "STAT NaHCO₃ 26 mEq + raise bag to 60 mEq/L · "
                "Voraxaze standby if Hr-54 MTX remains >2–5 µmol/L"
            ),
            "tone": "red",
        }
    if arch == "pyelo":
        dose = round(25 * float(p.get("wt", 16)))
        switched = maya_po_switch_staged(p["id"])
        return {
            "one_liner": (
                f"{p['name']} is a {p['age']} {p['sex']} with culture-proven "
                f"E. coli pyelonephritis, now afebrile {p.get('afebrile_hours', 30)}h "
                "and pansensitive — ready for narrow-spectrum PO step-down."
            ),
            "running": [
                (
                    f"Active: Cephalexin {dose} mg PO TID (staged)"
                    if switched
                    else "Active: Ceftriaxone 800 mg IV q24h"
                ),
                "PO intake 100% · 0 emesis · UOP adequate",
                f"Access: {access}",
            ],
            "escalation": (
                f"✅ PO Cephalexin {dose} mg TID already staged — complete "
                "first inpatient dose and DC pathway"
                if switched
                else (
                    f"Discontinue IV Ceftriaxone → start Cephalexin "
                    f"{dose} mg PO TID × remaining course"
                )
            ),
            "tone": "green",
        }
    if arch == "refeeding":
        return {
            "one_liner": (
                f"{p['name']} is a {p['age']} {p['sex']} on Day 3 refeeding with "
                f"critical bradycardia (HR nadir {p['hr_nadir']} bpm) and "
                f"hypophosphatemia (Phos {p['phos']:.1f} mg/dL)."
            ),
            "running": [
                f"Diet: {p.get('kcal', 1600):,} kcal/day (hold advance)",
                "Telemetry continuous · orthostatic precautions",
                f"Access: {access}",
            ],
            "escalation": (
                "Hold caloric advance at 1,600 kcal · IV NaPhos repletion · "
                "continue telemetry until HR ≥45 and Phos ≥2.5"
            ),
            "tone": "red",
        }
    # kawasaki / default
    ivig = round(2 * float(p.get("wt", 13)))
    return {
        "one_liner": (
            f"{p['name']} is a {p['age']} {p['sex']} with Day "
            f"{p.get('fever_day', 6)} Incomplete KD (2/5 criteria; "
            f"{p.get('supp_labs_met', 5)}/6 supplemental labs positive)."
        ),
        "running": [
            f"Pending: IVIG {ivig} g IV over 10–12h + High-Dose ASA",
            "Baseline echo ordered — do not delay IVIG",
            f"Access: {access}",
        ],
        "escalation": (
            f"Start IVIG 2 g/kg ({ivig} g) IV + High-Dose ASA now · "
            "monitor infusion reactions · start 36h refractory-fever clock "
            "after completion"
        ),
        "tone": "red",
    }


def render_patient_header(p: dict) -> None:
    """Compact patient banner: name + pills on one row, tight 2-line meta."""
    wt = p.get("wt", "")
    bsa = p.get("bsa", "")
    demo_bits = " · ".join(
        x
        for x in [
            str(p.get("age", "")),
            str(p.get("sex", "")),
            f"{wt} kg" if wt != "" else "",
            f"BSA {bsa} m²" if bsa not in ("", None) else "",
        ]
        if x
    )
    allergy = p.get("allergies") or p.get("allergy") or "NKDA"
    code_status = p.get("code_status") or "Full Code"
    allergy_cls = "banner-pill allergy-warn" if allergy != "NKDA" else "banner-pill"
    overlay = st.session_state.get(f"status_overlay_{p['id']}")
    status_line = (
        f"✅ [STAGED] {overlay}"
        if overlay
        else (p.get("status") or "")
    )
    with st.container(border=True, key=f"patient_hero_{p['id']}"):
        left, pathway_col = st.columns(
            [0.66, 0.34], vertical_alignment="center"
        )
        with left:
            st.html(
                '<div style="display:flex; align-items:center; gap:10px; '
                'flex-wrap:wrap; margin-bottom:4px;">'
                f'<span class="patient-banner-name">'
                f'{html.escape(p["name"])}</span>'
                f'<span class="banner-pill">'
                f'{html.escape(str(p["room"]))}</span>'
                f'<span class="banner-pill">'
                f'{html.escape(str(code_status))}</span>'
                f'<span class="{allergy_cls}">'
                f'Allergy: {html.escape(str(allergy))}</span>'
                "</div>"
                f'<div class="patient-banner-meta">'
                f"{html.escape(demo_bits)} · MRN {html.escape(str(p['mrn']))}"
                f" · {html.escape(str(ATTENDING))}<br/>"
                f"<strong>{html.escape(_patient_banner_line(p))}</strong>"
                + (
                    f"<br/>{html.escape(status_line)}"
                    if status_line
                    else ""
                )
                + "</div>"
            )
        with pathway_col:
            if st.button(
                "🔗 Open Clinical Pathway",
                help=f"Open {p['protocol']} decision tree",
                width="stretch",
                type="secondary",
                key=f"open_pathway_{p['id']}",
            ):
                pathway_dialog(p)


def render_narrative(p: dict, *, is_night: bool) -> None:
    zone_key = "night_banner" if is_night else f"synth_bento_{p['id']}"
    blocks = patient_synthesis_blocks(p)
    tone = blocks.get("tone", "red")
    esc_cls = "synth-escalate green" if tone == "green" else "synth-escalate"
    esc_label = "⚡ Clinical action triggers &amp; recommended orders"
    running_lis = "".join(
        f"<li>{html.escape(item)}</li>" for item in blocks.get("running", [])
    )
    wrap_cls = "night-synthesis-card" if is_night else "day-synthesis-card"
    with st.container(border=True, key=zone_key):
        st.html(
            f'<div class="{wrap_cls}">'
            '<div class="bento-zone-title">'
            "🧠 AI Clinical Synthesis & Active Protocol State</div>"
            '<div class="synth-block-label">Clinical one-liner</div>'
            f'<div class="synth-one-liner">'
            f'{html.escape(blocks["one_liner"])}</div>'
            '<div class="synth-block-label">'
            "Active running infusions / baseline state</div>"
            f'<ul class="synth-running">{running_lis}</ul>'
            f'<div class="synth-block-label">{esc_label}</div>'
            f'<div class="{esc_cls}">'
            f'{html.escape(blocks["escalation"])}</div>'
            "</div>"
        )
        render_stage_order_cta(p)


def render_checklist(p: dict, *, is_night: bool) -> None:
    tasks = p["night_tasks"] if is_night else p["day_tasks"]
    title = (
        "Night action queue"
        if is_night
        else "Day multidisciplinary checklist"
    )
    with st.container(border=True, key="checklist_bento"):
        st.html(
            '<div class="bento-zone-title">'
            "✅ Multidisciplinary Handoff & Action Queue "
            "(Auto-Synced)</div>"
        )
        top, btn = st.columns([2.2, 1], vertical_alignment="center")
        with top:
            st.markdown(f"**{title}**")
        with btn:
            if st.button(
                "Reset checklist",
                key=f"reset_{p['id']}_{'n' if is_night else 'd'}",
                icon=":material/restart_alt:",
                width="stretch",
            ):
                reset_tasks(p["id"], tasks)
                st.rerun()

        if is_night:
            st.caption("Cross-cover focus — contingencies since 07:00 only.")
        else:
            st.caption("Full course · barriers · handoff actions.")

        for tid, label, cite_key in tasks:
            key = night_key(p["id"], tid) if is_night else day_key(p["id"], tid)
            shown = checklist_label_with_stage(p["id"], tid, label)
            cols = st.columns([0.72, 0.28], gap="small", vertical_alignment="top")
            with cols[0]:
                st.checkbox(shown, key=key)
            with cols[1]:
                checklist_source_popover(
                    p,
                    tid,
                    cite_key,
                    loc=f"task_{'n' if is_night else 'd'}_{tid}",
                )

        render_smart_custom_tasks(p, is_night=is_night)
        render_smart_task_composer(p, is_night=is_night)


def render_patient_workspace(p: dict, *, is_night: bool) -> None:
    workspace_key = "night_workspace" if is_night else f"day_workspace_{p['id']}"
    with st.container(key=workspace_key):
        render_patient_header(p)
        st.markdown("")
        render_core_metrics(p)
        st.markdown("")
        left, right = st.columns([0.42, 0.58], gap="medium")
        with left:
            render_narrative(p, is_night=is_night)
        with right:
            render_checklist(p, is_night=is_night)


def inject_night_mode_styles(is_night: bool) -> None:
    """When Night view is active, restyle the full app to midnight navy-slate."""
    if not is_night:
        st.html(
            """
            <script>
            (function() {
              document.documentElement.classList.remove('unit4b-night');
            })();
            </script>
            """,
            unsafe_allow_javascript=True,
        )
        return
    st.html(
        """
        <script>
        (function() {
          document.documentElement.classList.add('unit4b-night');
        })();
        </script>
        <style>
        /* ========== UNIT 4B NIGHT MODE (html.unit4b-night boosts specificity) ========== */

        /* 1. Full App Background (never paint Streamlit's fixed header) */
        html.unit4b-night .stApp,
        html.unit4b-night [data-testid="stAppViewContainer"],
        html.unit4b-night section.main,
        html.unit4b-night [data-testid="stAppViewContainer"] > .main,
        html.unit4b-night .block-container {
            background-color: #0B1120 !important;
            color: #F8FAFC !important;
        }
        /* Collapse Streamlit top header so it never curtains the command bar */
        html.unit4b-night header[data-testid="stHeader"],
        header[data-testid="stHeader"] {
            background: transparent !important;
            background-color: transparent !important;
            height: 0px !important;
            min-height: 0px !important;
            border: none !important;
            box-shadow: none !important;
            pointer-events: none !important;
        }
        html.unit4b-night div[data-testid="stToolbar"],
        html.unit4b-night div[data-testid="stDecoration"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"] {
            display: none !important;
        }

        /* 2. Bordered card shells (default dark; specialty cards override below) */
        html.unit4b-night div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #111827 !important;
            border-color: #1E293B !important;
            color: #F8FAFC !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
        }

        /* 3. Left Census Rail — beat day #F8FAFC / #F3E8FF rules */
        html.unit4b-night .st-key-ward_census_rail,
        html.unit4b-night div[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-ward_census_rail) {
            background-color: #0F172A !important;
            border-color: #1E293B !important;
        }
        html.unit4b-night .linear-rail-header,
        html.unit4b-night .linear-rail-footer {
            color: #94A3B8 !important;
            border-color: #334155 !important;
        }
        html.unit4b-night div[data-testid="stVerticalBlockBorderWrapper"]:has(.census-card-marker),
        html.unit4b-night div:has(> div > div > .census-card-marker),
        html.unit4b-night [class*="st-key-census_patient_card_"] {
            background-color: #1E293B !important;
            border: 1px solid #334155 !important;
            box-shadow: none !important;
        }
        html.unit4b-night div[data-testid="stVerticalBlockBorderWrapper"]:has(.census-card-marker):hover,
        html.unit4b-night div:has(> div > div > .census-card-marker):hover {
            background-color: #263349 !important;
            border-color: #475569 !important;
        }
        html.unit4b-night div[data-testid="stVerticalBlockBorderWrapper"]:has(.census-card-active),
        html.unit4b-night div:has(> div > div > .census-card-active),
        html.unit4b-night [class*="st-key-census_patient_card_"]:has(.census-card-active) {
            background-color: #2E1065 !important;
            border: 1.5px solid #A855F7 !important;
            box-shadow: 0 4px 14px rgba(168, 85, 247, 0.25) !important;
        }
        html.unit4b-night .census-card-top-left,
        html.unit4b-night .census-card-marker,
        html.unit4b-night .census-card-identity {
            color: #F8FAFC !important;
        }
        html.unit4b-night .census-card-active .census-card-top-left,
        html.unit4b-night .census-card-active {
            color: #FFFFFF !important;
        }
        /* Census alert pills — explicit dark bg + bright text (never wash out) */
        html.unit4b-night .pill-crit {
            background: #4C0519 !important;
            color: #FDA4AF !important;
            border: 1px solid #E11D48 !important;
        }
        html.unit4b-night .pill-ok {
            background: #064E3B !important;
            color: #6EE7B7 !important;
            border: 1px solid #10B981 !important;
        }
        html.unit4b-night .pill-muted,
        html.unit4b-night .pill-room {
            background: #334155 !important;
            color: #E2E8F0 !important;
            border: 1px solid #475569 !important;
        }

        /* 4. Patient header banner */
        html.unit4b-night [class*="st-key-patient_hero_"],
        html.unit4b-night div[data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-patient_hero_"]) {
            background-color: #111827 !important;
            border-color: #1E293B !important;
        }
        html.unit4b-night .patient-banner-name {
            color: #FFFFFF !important;
        }
        html.unit4b-night .patient-banner-meta {
            color: #CBD5E1 !important;
        }
        html.unit4b-night .patient-banner-meta strong {
            color: #F1F5F9 !important;
        }
        html.unit4b-night .banner-pill {
            background: #1E293B !important;
            color: #E2E8F0 !important;
            border: 1px solid #475569 !important;
        }
        html.unit4b-night .banner-pill.allergy-warn {
            background: #4C0519 !important;
            color: #FDA4AF !important;
            border: 1px solid #E11D48 !important;
        }
        html.unit4b-night [class*="st-key-open_pathway_"] button,
        html.unit4b-night [class*="st-key-open_pathway_"] [data-testid="stBaseButton-secondary"] {
            background-color: #1E293B !important;
            color: #C4B5FD !important;
            border: 1px solid #7C3AED !important;
        }
        html.unit4b-night [class*="st-key-open_pathway_"] button p,
        html.unit4b-night [class*="st-key-open_pathway_"] button span {
            color: #C4B5FD !important;
        }

        /* 5. Telemetry tiles + popover triggers */
        html.unit4b-night .ah-tile,
        html.unit4b-night .ah-tile-body {
            background-color: transparent !important;
            color: #F8FAFC !important;
        }
        html.unit4b-night .ah-tile-value { color: #F8FAFC !important; }
        html.unit4b-night .ah-tile-value.crit,
        html.unit4b-night .ah-tile-value.pathogen { color: #FDA4AF !important; }
        html.unit4b-night .ah-tile-unit,
        html.unit4b-night .ah-tile-ts,
        html.unit4b-night .ah-tile-ctx { color: #CBD5E1 !important; }
        html.unit4b-night .ah-tile-body.tier-red .ah-cat-label { color: #FDA4AF !important; }
        html.unit4b-night .ah-tile-body.tier-amber .ah-cat-label { color: #FDE68A !important; }
        html.unit4b-night .ah-tile-body.tier-green .ah-cat-label,
        html.unit4b-night .ah-tile-body.addressed .ah-cat-label { color: #6EE7B7 !important; }
        html.unit4b-night .telemetry-section-header,
        html.unit4b-night .bento-zone-title,
        html.unit4b-night .amb-live-sync { color: #E2E8F0 !important; }

        html.unit4b-night .crit-met-red,
        html.unit4b-night .ah-tile-ctx .crit-met-red {
            background-color: #4C0519 !important;
            color: #FDA4AF !important;
            border: 1px solid #E11D48 !important;
        }
        html.unit4b-night .crit-met-green {
            background-color: #064E3B !important;
            color: #6EE7B7 !important;
            border: 1px solid #10B981 !important;
        }
        html.unit4b-night .crit-met-yellow {
            background-color: rgba(245, 158, 11, 0.22) !important;
            color: #FDE68A !important;
            border: 1px solid rgba(251, 191, 36, 0.45) !important;
        }

        html.unit4b-night div[data-testid="stPopover"] > div > button,
        html.unit4b-night div[data-testid="stPopover"] button,
        html.unit4b-night [class*="st-key-cite_"] button,
        html.unit4b-night [class*="st-key-cite_"] [data-testid="stPopoverButton"] {
            background-color: #1E293B !important;
            color: #93C5FD !important;
            border: 1px solid #334155 !important;
            font-weight: 600 !important;
        }
        html.unit4b-night div[data-testid="stPopover"] button:hover,
        html.unit4b-night [class*="st-key-cite_"] button:hover {
            background-color: #334155 !important;
            color: #DBEAFE !important;
            border-color: #60A5FA !important;
        }
        html.unit4b-night div[data-testid="stPopover"] button p,
        html.unit4b-night div[data-testid="stPopover"] button span,
        html.unit4b-night div[data-testid="stPopover"] button div,
        html.unit4b-night [class*="st-key-cite_"] button p,
        html.unit4b-night [class*="st-key-cite_"] button span,
        html.unit4b-night [class*="st-key-cite_"] button div {
            color: #93C5FD !important;
            font-weight: 600 !important;
        }
        html.unit4b-night div[data-testid="stPopoverBody"],
        html.unit4b-night div[data-baseweb="popover"] > div,
        html.unit4b-night [data-testid="stPopoverBody"] {
            background-color: #0F172A !important;
            border: 1px solid #334155 !important;
            color: #F8FAFC !important;
        }
        /* Lab / telemetry popover secondary text — bright slate, never muted #475569/#64748B/#94A3B8 */
        html.unit4b-night .lab-legend,
        html.unit4b-night [data-testid="stPopoverBody"] .lab-legend,
        html.unit4b-night div[data-baseweb="popover"] .lab-legend {
            color: #E2E8F0 !important;
            font-weight: 500 !important;
        }
        html.unit4b-night .lab-detail-name,
        html.unit4b-night .lab-detail-cut,
        html.unit4b-night .lab-detail-cutoff,
        html.unit4b-night .supp-lab-cut,
        html.unit4b-night .supp-lab-name,
        html.unit4b-night .mic-footnote,
        html.unit4b-night .mic-table th {
            color: #E2E8F0 !important;
            font-weight: 500 !important;
        }
        html.unit4b-night .lab-detail-row {
            border-bottom-color: #334155 !important;
            color: #F8FAFC !important;
        }
        /* Source / footer captions inside popovers (e.g. Epic Lab · Hour 48 MTX series) */
        html.unit4b-night [data-testid="stPopoverBody"] [data-testid="stCaptionContainer"],
        html.unit4b-night [data-testid="stPopoverBody"] [data-testid="stCaptionContainer"] p,
        html.unit4b-night [data-testid="stPopoverBody"] [data-testid="stCaptionContainer"] small,
        html.unit4b-night div[data-baseweb="popover"] [data-testid="stCaptionContainer"],
        html.unit4b-night div[data-baseweb="popover"] [data-testid="stCaptionContainer"] p,
        html.unit4b-night div[data-baseweb="popover"] [data-testid="stCaptionContainer"] small,
        html.unit4b-night [data-testid="stPopoverBody"] .stCaption,
        html.unit4b-night [data-testid="stPopoverBody"] .stMarkdown p,
        html.unit4b-night [data-testid="stPopoverBody"] [data-testid="stMarkdownContainer"] p {
            color: #E2E8F0 !important;
            font-weight: 500 !important;
            opacity: 1 !important;
        }
        /* Keep light-tint status pills crisp with dark semantic text */
        html.unit4b-night .lab-pill.red,
        html.unit4b-night [data-testid="stPopoverBody"] .lab-pill.red,
        html.unit4b-night div[data-baseweb="popover"] .lab-pill.red {
            color: #991B1B !important;
            background: #FFF1F2 !important;
            border-color: #FECDD3 !important;
        }
        html.unit4b-night .lab-pill.amber,
        html.unit4b-night [data-testid="stPopoverBody"] .lab-pill.amber,
        html.unit4b-night div[data-baseweb="popover"] .lab-pill.amber {
            color: #92400E !important;
            background: #FFFBEB !important;
            border-color: #FDE68A !important;
        }
        html.unit4b-night .lab-pill.green,
        html.unit4b-night [data-testid="stPopoverBody"] .lab-pill.green,
        html.unit4b-night div[data-baseweb="popover"] .lab-pill.green {
            color: #047857 !important;
            background: #ECFDF5 !important;
            border-color: #A7F3D0 !important;
        }
        html.unit4b-night .supp-lab-card.red .supp-lab-pill {
            color: #991B1B !important;
            background: #FFFFFF !important;
        }
        html.unit4b-night .supp-lab-card.amber .supp-lab-pill {
            color: #92400E !important;
            background: #FFFFFF !important;
        }
        html.unit4b-night .supp-lab-card.green .supp-lab-pill {
            color: #047857 !important;
            background: #FFFFFF !important;
        }

        /* MAR / intervention provenance cards — dark surfaces (never light tint + light text) */
        html.unit4b-night .mar-detail-card {
            background: #1E293B !important;
            border: 1.5px solid #334155 !important;
            color: #F8FAFC !important;
        }
        html.unit4b-night .mar-detail-card.pending {
            background: #2A1215 !important;
            border-color: #7F1D1D !important;
            color: #F8FAFC !important;
        }
        html.unit4b-night .mar-detail-title {
            color: #FCA5A5 !important;
        }
        html.unit4b-night .mar-detail-card:not(.pending) .mar-detail-title {
            color: #6EE7B7 !important;
        }
        html.unit4b-night .mar-detail-heading {
            color: #FCA5A5 !important;
        }
        html.unit4b-night .mar-detail-card:not(.pending) .mar-detail-heading {
            color: #A7F3D0 !important;
        }
        html.unit4b-night .mar-detail-key {
            color: #E2E8F0 !important;
            font-weight: 500 !important;
        }
        html.unit4b-night .mar-detail-val {
            color: #F8FAFC !important;
            font-weight: 500 !important;
        }
        html.unit4b-night .mar-detail-section {
            border-top-color: #334155 !important;
        }
        html.unit4b-night .mar-detail-card.pending .mar-detail-section {
            border-top-color: rgba(127, 29, 29, 0.55) !important;
        }
        /* Beat day-defensive !important on light-tint cards while night is active */
        html.unit4b-night .mar-detail-card .mar-detail-key,
        html.unit4b-night .mar-detail-card.pending .mar-detail-key {
            color: #E2E8F0 !important;
            font-weight: 500 !important;
        }
        html.unit4b-night .mar-detail-card .mar-detail-val,
        html.unit4b-night .mar-detail-card.pending .mar-detail-val {
            color: #F8FAFC !important;
            font-weight: 500 !important;
        }
        html.unit4b-night .mar-detail-card .mar-detail-title {
            color: #6EE7B7 !important;
        }
        html.unit4b-night .mar-detail-card.pending .mar-detail-title {
            color: #FCA5A5 !important;
        }
        html.unit4b-night .mar-detail-card .mar-detail-heading {
            color: #A7F3D0 !important;
        }
        html.unit4b-night .mar-detail-card.pending .mar-detail-heading {
            color: #FCA5A5 !important;
        }

        /* Night defensive: same light-tint containers → dark surface palette */
        html.unit4b-night [style*="background:#FEF2F2"],
        html.unit4b-night [style*="background: #FEF2F2"],
        html.unit4b-night [style*="background:#FFF1F2"],
        html.unit4b-night [style*="background: #FFF1F2"],
        html.unit4b-night [style*="background:#FEF3C7"],
        html.unit4b-night [style*="background: #FEF3C7"] {
            background: #2A1215 !important;
            background-color: #2A1215 !important;
            border-color: #7F1D1D !important;
            color: #F8FAFC !important;
        }
        html.unit4b-night [style*="background:#F0FDF4"],
        html.unit4b-night [style*="background: #F0FDF4"],
        html.unit4b-night [style*="background:#ECFDF5"],
        html.unit4b-night [style*="background: #ECFDF5"] {
            background: #1E293B !important;
            background-color: #1E293B !important;
            border-color: #334155 !important;
            color: #F8FAFC !important;
        }
        html.unit4b-night [style*="background:#EFF6FF"],
        html.unit4b-night [style*="background: #EFF6FF"],
        html.unit4b-night [style*="background:#FFFBEB"],
        html.unit4b-night [style*="background: #FFFBEB"] {
            background: #1E293B !important;
            background-color: #1E293B !important;
            border-color: #334155 !important;
            color: #F8FAFC !important;
        }
        html.unit4b-night .protocol-scroll-box tbody tr.row-red td {
            background: #2A1215 !important;
            color: #F8FAFC !important;
        }
        html.unit4b-night .protocol-scroll-box tbody tr.row-amber td {
            background: #1E293B !important;
            color: #F8FAFC !important;
        }

        /* 6. Day / Night toggle track */
        html.unit4b-night div[data-testid="stRadio"] > div[role="radiogroup"],
        html.unit4b-night .st-key-shift_view div[role="radiogroup"],
        html.unit4b-night .st-key-shift_view [data-testid="stSegmentedControl"],
        html.unit4b-night .st-key-shift_view [data-baseweb="button-group"] {
            background-color: #1E293B !important;
            border-color: #334155 !important;
        }
        html.unit4b-night .st-key-shift_view [data-baseweb="button-group"] > *:nth-child(1),
        html.unit4b-night .st-key-shift_view [data-testid="stSegmentedControl"] button:nth-of-type(1) {
            background-color: transparent !important;
            border-color: transparent !important;
            color: #94A3B8 !important;
            box-shadow: none !important;
        }
        html.unit4b-night .st-key-shift_view [data-baseweb="button-group"] > *:nth-child(2),
        html.unit4b-night .st-key-shift_view [data-testid="stSegmentedControl"] button:nth-of-type(2) {
            background-color: #3B0764 !important;
            border: 1.5px solid #A855F7 !important;
            color: #F3E8FF !important;
            font-weight: 700 !important;
            box-shadow: 0 2px 8px rgba(168, 85, 247, 0.22) !important;
        }

        /* 7. Handoff queue header, task rows, verify pills, custom task */
        html.unit4b-night .st-key-checklist_bento,
        html.unit4b-night div[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-checklist_bento) {
            background-color: #111827 !important;
            border-color: #1E293B !important;
        }
        html.unit4b-night .st-key-checklist_bento .bento-zone-title,
        html.unit4b-night .st-key-checklist_bento [data-testid="stMarkdownContainer"] p,
        html.unit4b-night .st-key-checklist_bento [data-testid="stMarkdownContainer"] strong {
            color: #F8FAFC !important;
        }
        html.unit4b-night [class*="st-key-reset_"] button,
        html.unit4b-night [class*="st-key-reset_"] [data-testid="stBaseButton-secondary"] {
            background-color: #0F172A !important;
            color: #E2E8F0 !important;
            border: 1px solid #475569 !important;
        }
        html.unit4b-night [class*="st-key-reset_"] button p,
        html.unit4b-night [class*="st-key-reset_"] button span {
            color: #E2E8F0 !important;
        }
        html.unit4b-night .st-key-checklist_bento [data-testid="stHorizontalBlock"] {
            background: #1E293B !important;
            border: 1px solid #334155 !important;
            border-radius: 10px !important;
        }
        html.unit4b-night .st-key-checklist_bento [data-testid="stCheckbox"] label,
        html.unit4b-night .st-key-checklist_bento [data-testid="stCheckbox"] label p,
        html.unit4b-night .st-key-checklist_bento [data-testid="stCheckbox"] div[data-testid="stMarkdownContainer"] p {
            color: #F8FAFC !important;
        }
        /* Inline clinical keywords (:red[MTX], urine pH, etc.) — amber chips on dark rows */
        html.unit4b-night .st-key-checklist_bento [data-testid="stCheckbox"] span[style],
        html.unit4b-night .st-key-checklist_bento [data-testid="stMarkdownContainer"] span[style] {
            color: #FDE047 !important;
            background: rgba(250, 204, 21, 0.15) !important;
            padding: 1px 5px !important;
            border-radius: 4px !important;
            font-weight: 700 !important;
        }
        html.unit4b-night [class*="st-key-ehr_src_"] button,
        html.unit4b-night [class*="st-key-ehr_src_"] [data-testid="stPopoverButton"] {
            background-color: #064E3B !important;
            color: #6EE7B7 !important;
            border: 1px solid #10B981 !important;
        }
        html.unit4b-night [class*="st-key-ehr_src_"] button p,
        html.unit4b-night [class*="st-key-ehr_src_"] button span {
            color: #6EE7B7 !important;
        }
        html.unit4b-night .verify-pill-crit {
            background-color: rgba(159, 18, 57, 0.35) !important;
            color: #FECDD3 !important;
            border-color: #F43F5E !important;
        }
        html.unit4b-night .verify-pill-ok {
            background-color: rgba(6, 95, 70, 0.35) !important;
            color: #A7F3D0 !important;
            border-color: #10B981 !important;
        }

        /* Custom task composer */
        html.unit4b-night .st-key-checklist_bento [data-testid="stTextInput"] input,
        html.unit4b-night [data-testid="stTextInput"] input {
            background-color: #0F172A !important;
            color: #F8FAFC !important;
            border: 1px solid #475569 !important;
        }
        html.unit4b-night .st-key-checklist_bento [data-testid="stTextInput"] input::placeholder {
            color: #94A3B8 !important;
        }
        html.unit4b-night [class*="st-key-add_task_btn_"] button,
        html.unit4b-night [class*="st-key-add_task_btn_"] [data-testid="stBaseButton-secondary"] {
            background-color: #7C3AED !important;
            color: #FFFFFF !important;
            border: 1px solid #8B5CF6 !important;
            font-weight: 600 !important;
        }
        html.unit4b-night [class*="st-key-add_task_btn_"] button p,
        html.unit4b-night [class*="st-key-add_task_btn_"] button span {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }

        /* Scoped readable body text — NOT a blanket span washout */
        html.unit4b-night [data-testid="stCaptionContainer"],
        html.unit4b-night [data-testid="stCaptionContainer"] p,
        html.unit4b-night [data-testid="stCaptionContainer"] small,
        html.unit4b-night .stCaption,
        html.unit4b-night .stMarkdown h3,
        html.unit4b-night div[data-testid="stVerticalBlockBorderWrapper"] > div p,
        html.unit4b-night div[data-testid="stVerticalBlockBorderWrapper"] > div label {
            color: #E2E8F0 !important;
            font-weight: 500 !important;
            opacity: 1 !important;
        }
        </style>
        """,
        unsafe_allow_javascript=True,
    )


def inject_shift_view_active_styles(view_mode: str) -> None:
    """Force purple active Day/Night tab via nth-child CSS + inline JS (no :has)."""
    active_tab_idx = 1 if "Day" in str(view_mode) else 2
    inactive_tab_idx = 2 if active_tab_idx == 1 else 1
    active_label = DAY if active_tab_idx == 1 else NIGHT
    # Deterministic nth-of-type CSS from Python state (segmented + radio DOM)
    st.html(
        f"""
        <style>
        /* Disable overflow clipping / fade masks on Day-Night toggle */
        div[data-testid="stRadio"],
        div[data-testid="stRadio"] > div,
        div[data-testid="stRadio"] > div[role="radiogroup"],
        .st-key-shift_view,
        .st-key-shift_view > div,
        .st-key-shift_view [data-testid="stSegmentedControl"],
        .st-key-shift_view [data-testid="stSegmentedControl"] > div,
        .st-key-shift_view [data-baseweb="button-group"],
        .st-key-shift_view div[role="radiogroup"] {{
            overflow: visible !important;
            mask-image: none !important;
            -webkit-mask-image: none !important;
        }}
        div[data-testid="stRadio"]::before,
        div[data-testid="stRadio"]::after,
        div[data-testid="stRadio"] > div::before,
        div[data-testid="stRadio"] > div::after,
        div[data-testid="stRadio"] > div[role="radiogroup"]::before,
        div[data-testid="stRadio"] > div[role="radiogroup"]::after,
        .st-key-shift_view::before,
        .st-key-shift_view::after,
        .st-key-shift_view [data-testid="stSegmentedControl"]::before,
        .st-key-shift_view [data-testid="stSegmentedControl"]::after,
        .st-key-shift_view [data-testid="stSegmentedControl"] > div::before,
        .st-key-shift_view [data-testid="stSegmentedControl"] > div::after,
        .st-key-shift_view [data-baseweb="button-group"]::before,
        .st-key-shift_view [data-baseweb="button-group"]::after {{
            display: none !important;
            content: none !important;
            background: none !important;
        }}
        /* Outer pill track — fully enclose both Day/Night options */
        div[data-testid="stRadio"],
        div[data-testid="stRadio"] > div,
        .st-key-shift_view,
        .st-key-shift_view > div,
        .st-key-shift_view [data-testid="stSegmentedControl"],
        .st-key-shift_view [data-testid="stSegmentedControl"] > div {{
            width: auto !important;
            max-width: none !important;
            overflow: visible !important;
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"],
        .st-key-shift_view div[role="radiogroup"],
        .st-key-shift_view [data-testid="stSegmentedControl"],
        .st-key-shift_view [data-baseweb="button-group"] {{
            background-color: #EEF2F6 !important;
            padding: 5px 8px !important;
            border-radius: 999px !important;
            border: 1px solid #CBD5E1 !important;
            display: inline-flex !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            gap: 6px !important;
            width: max-content !important;
            min-width: max-content !important;
            max-width: none !important;
            box-sizing: border-box !important;
            overflow: visible !important;
            mask-image: none !important;
            -webkit-mask-image: none !important;
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"] > label,
        .st-key-shift_view div[role="radiogroup"] > label,
        .st-key-shift_view [data-baseweb="button-group"] > button,
        .st-key-shift_view [data-testid="stSegmentedControl"] button {{
            flex: 0 0 auto !important;
            width: max-content !important;
            margin: 0px !important;
            padding: 6px 16px !important;
            border-radius: 999px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-sizing: border-box !important;
            white-space: nowrap !important;
        }}
        /* Hide only the radio circle visually without breaking DOM attributes */
        div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child,
        .st-key-shift_view div[role="radiogroup"] > label > div:first-child {{
            width: 0px !important;
            height: 0px !important;
            overflow: hidden !important;
            opacity: 0 !important;
            margin: 0px !important;
            padding: 0px !important;
            position: absolute !important;
        }}
        /* ACTIVE / SELECTED TAB (Child #{active_tab_idx}) -> PURPLE */
        div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-of-type({active_tab_idx}),
        div[data-testid="stRadio"] > div[role="radiogroup"] > *:nth-child({active_tab_idx}),
        .st-key-shift_view [data-baseweb="button-group"] > *:nth-child({active_tab_idx}),
        .st-key-shift_view [data-testid="stSegmentedControl"] button:nth-of-type({active_tab_idx}),
        .st-key-shift_view div[role="radiogroup"] > label:nth-of-type({active_tab_idx}),
        .st-key-shift_view div[role="radiogroup"] > *:nth-child({active_tab_idx}) {{
            background-color: #F3E8FF !important;
            border: 1.5px solid #7C3AED !important;
            border-radius: 999px !important;
            padding: 6px 18px !important;
            box-shadow: 0 2px 6px rgba(124, 58, 237, 0.18) !important;
            cursor: pointer !important;
            transition: all 0.15s ease !important;
            color: #4C1D95 !important;
            font-weight: 700 !important;
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-of-type({active_tab_idx}) p,
        div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-of-type({active_tab_idx}) span,
        .st-key-shift_view [data-baseweb="button-group"] > *:nth-child({active_tab_idx}) p,
        .st-key-shift_view [data-baseweb="button-group"] > *:nth-child({active_tab_idx}) span,
        .st-key-shift_view [data-testid="stSegmentedControl"] button:nth-of-type({active_tab_idx}) p,
        .st-key-shift_view [data-testid="stSegmentedControl"] button:nth-of-type({active_tab_idx}) span,
        .st-key-shift_view div[role="radiogroup"] > label:nth-of-type({active_tab_idx}) p,
        .st-key-shift_view div[role="radiogroup"] > label:nth-of-type({active_tab_idx}) span {{
            color: #4C1D95 !important;
            font-weight: 700 !important;
        }}
        /* INACTIVE / UNSELECTED TAB (Child #{inactive_tab_idx}) -> RECESSED GREY */
        div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-of-type({inactive_tab_idx}),
        div[data-testid="stRadio"] > div[role="radiogroup"] > *:nth-child({inactive_tab_idx}),
        .st-key-shift_view [data-baseweb="button-group"] > *:nth-child({inactive_tab_idx}),
        .st-key-shift_view [data-testid="stSegmentedControl"] button:nth-of-type({inactive_tab_idx}),
        .st-key-shift_view div[role="radiogroup"] > label:nth-of-type({inactive_tab_idx}),
        .st-key-shift_view div[role="radiogroup"] > *:nth-child({inactive_tab_idx}) {{
            background-color: transparent !important;
            border: 1.5px solid transparent !important;
            border-radius: 999px !important;
            padding: 6px 18px !important;
            box-shadow: none !important;
            cursor: pointer !important;
            transition: all 0.15s ease !important;
            color: #64748B !important;
            font-weight: 500 !important;
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-of-type({inactive_tab_idx}) p,
        div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-of-type({inactive_tab_idx}) span,
        .st-key-shift_view [data-baseweb="button-group"] > *:nth-child({inactive_tab_idx}) p,
        .st-key-shift_view [data-baseweb="button-group"] > *:nth-child({inactive_tab_idx}) span,
        .st-key-shift_view [data-testid="stSegmentedControl"] button:nth-of-type({inactive_tab_idx}) p,
        .st-key-shift_view [data-testid="stSegmentedControl"] button:nth-of-type({inactive_tab_idx}) span,
        .st-key-shift_view div[role="radiogroup"] > label:nth-of-type({inactive_tab_idx}) p,
        .st-key-shift_view div[role="radiogroup"] > label:nth-of-type({inactive_tab_idx}) span {{
            color: #64748B !important;
            font-weight: 500 !important;
        }}
        </style>
        """
    )
    # Double guarantee: paint by matching the active label text in the live DOM
    active_js = json.dumps(active_label)
    st.html(
        f"""
        <div class="shift-toggle-style-host" aria-hidden="true"></div>
        <script>
        (function() {{
            const ACTIVE_LABEL = {active_js};
            const IS_NIGHT = ACTIVE_LABEL.includes('Night');
            function clearShiftOverflowMasks() {{
                const clipTargets = document.querySelectorAll(
                    'div[data-testid="stRadio"], div[data-testid="stRadio"] > div, ' +
                    'div[data-testid="stRadio"] > div[role="radiogroup"], ' +
                    '.st-key-shift_view, .st-key-shift_view > div, ' +
                    '.st-key-shift_view [data-testid="stSegmentedControl"], ' +
                    '.st-key-shift_view [data-testid="stSegmentedControl"] > div, ' +
                    '.st-key-shift_view [data-baseweb="button-group"], ' +
                    '.st-key-shift_view div[role="radiogroup"]'
                );
                clipTargets.forEach(el => {{
                    el.style.setProperty('overflow', 'visible', 'important');
                    el.style.setProperty('mask-image', 'none', 'important');
                    el.style.setProperty('-webkit-mask-image', 'none', 'important');
                    if (IS_NIGHT) {{
                        if (el.getAttribute('role') === 'radiogroup' ||
                            el.getAttribute('data-testid') === 'stSegmentedControl' ||
                            el.getAttribute('data-baseweb') === 'button-group') {{
                            el.style.setProperty('background-color', '#1E293B', 'important');
                            el.style.setProperty('border-color', '#334155', 'important');
                        }}
                    }}
                }});
            }}
            function paintShiftToggle() {{
                clearShiftOverflowMasks();
                const roots = Array.from(document.querySelectorAll(
                    '.st-key-shift_view, [data-testid="stSegmentedControl"], div[role="radiogroup"]'
                ));
                const nodes = [];
                roots.forEach(root => {{
                    root.querySelectorAll('button, label').forEach(el => nodes.push(el));
                }});
                const activeBg = IS_NIGHT ? '#3B0764' : '#F3E8FF';
                const activeBorder = IS_NIGHT ? '1.5px solid #A855F7' : '1.5px solid #7C3AED';
                const activeFg = IS_NIGHT ? '#F3E8FF' : '#4C1D95';
                const inactiveFg = IS_NIGHT ? '#94A3B8' : '#64748B';
                // Deduplicate
                const seen = new Set();
                nodes.forEach(el => {{
                    if (seen.has(el)) return;
                    seen.add(el);
                    const txt = (el.innerText || el.textContent || '').trim();
                    if (!txt.includes('Day Attending') && !txt.includes('Night Attending')) {{
                        return;
                    }}
                    const isActive = txt === ACTIVE_LABEL || (
                        ACTIVE_LABEL.includes('Day')
                            ? txt.includes('Day Attending')
                            : txt.includes('Night Attending')
                    );
                    if (isActive) {{
                        el.style.setProperty('background-color', activeBg, 'important');
                        el.style.setProperty('border', activeBorder, 'important');
                        el.style.setProperty('border-radius', '999px', 'important');
                        el.style.setProperty('box-shadow', '0 2px 6px rgba(168, 85, 247, 0.22)', 'important');
                        el.style.setProperty('color', activeFg, 'important');
                        el.style.setProperty('font-weight', '700', 'important');
                        el.querySelectorAll('p, span').forEach(child => {{
                            child.style.setProperty('color', activeFg, 'important');
                            child.style.setProperty('font-weight', '700', 'important');
                        }});
                    }} else {{
                        el.style.setProperty('background-color', 'transparent', 'important');
                        el.style.setProperty('border', '1.5px solid transparent', 'important');
                        el.style.setProperty('box-shadow', 'none', 'important');
                        el.style.setProperty('color', inactiveFg, 'important');
                        el.style.setProperty('font-weight', '500', 'important');
                        el.querySelectorAll('p, span').forEach(child => {{
                            child.style.setProperty('color', inactiveFg, 'important');
                            child.style.setProperty('font-weight', '500', 'important');
                        }});
                    }}
                }});
            }}
            paintShiftToggle();
            setTimeout(paintShiftToggle, 150);
            setTimeout(paintShiftToggle, 500);
        }})();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def render_command_bar() -> str:
    """Top Ambience command bar: title + live sync + Day/Night toggle."""
    left, mid, right = st.columns([1.15, 0.95, 1.2], vertical_alignment="center")
    with left:
        st.markdown("### Unit 4B attending handoff")
        st.caption("Pediatric ward · multi-archetype action engine")
    with mid:
        st.html(
            '<div class="amb-live-sync">'
            '<span class="amb-live-dot" aria-hidden="true"></span>'
            "⚡ Ambience Inpatient Chorus · Live EHR Sync"
            "</div>"
        )
    with right:
        shift = st.segmented_control(
            "Shift view",
            options=[DAY, NIGHT],
            default=DAY,
            key="shift_view",
            label_visibility="collapsed",
            width="content",
            required=True,
        )
    return shift or DAY


# ---------------------------------------------------------------------------
# Top command bar + master Bento layout
# ---------------------------------------------------------------------------
shift = render_command_bar()
inject_shift_view_active_styles(shift)
is_night = "Night" in str(shift)
inject_night_mode_styles(is_night)

CENSUS = sorted(PATIENTS, key=room_sort_key)
census_ids = [p["id"] for p in CENSUS]

if "selected_patient" not in st.session_state:
    st.session_state.selected_patient = census_ids[0]
elif st.session_state.selected_patient not in census_ids:
    st.session_state.selected_patient = census_ids[0]

if "custom_tasks" not in st.session_state:
    st.session_state.custom_tasks = {}

roster_col, detail_col = st.columns([0.24, 0.76], gap="medium")

with roster_col:
    render_census_rail(CENSUS)

active = patient_by_id(st.session_state.selected_patient, CENSUS)

with detail_col:
    render_patient_workspace(active, is_night=is_night)

n_crit = sum(1 for p in PATIENTS if p.get("critical"))
st.caption(
    f"{len(PATIENTS)} patients · {n_crit} critical archetypes · "
    f"Active: **{active['room']}** {active['name']} · "
    f"{'Night cross-cover' if is_night else 'Day synthesis'}"
)
