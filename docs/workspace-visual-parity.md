# BizLens V1 — approved visual identity and workspace parity gate

**Status:** Implementation in review, not a claim of pixel parity. This page
protects two preserved source references and the intentionally separate,
functional Next.js application.

## Source priority

1. **Original Figma Make** — authority for the landing identity,
   "See your business clearly.", and journey:
   https://www.figma.com/make/8G0aIwZnVF0vtl4sI8KdAI/High-Fidelity-BizLens-Experience
2. **Approved standalone visual prototype** — authority for dashboard polish,
   sidebar/navigation hierarchy, KPI cards, chart layout, contrast, evidence
   cards and responsive treatments. Original reference:
   `02_Approved_New_Visual_Reference_UNCHANGED/bizlens_design_v1_preview.html`
   in the separately archived `BizLens_Dual_Visual_References_V1.zip`.
3. **Verified business data** always outranks decorative examples. Synthetic
   reference amounts must not leak into live dashboard metrics.

Do **not** edit either of the reference sources while implementing UI changes.

## Why this PR exists

The application already provides the correct landing identity and an offline
CSV → analysis → report journey, but it used only sequential Next/Back
screens after analysis. This was **not visually faithful** to the approved
left-sidebar dashboard workspace.

This branch adds `WorkspaceShell` around the five *existing* analytical
screens — Overview, Diagnoses, What Changed, Ask BizLens and Report — without
rebuilding their deterministic financial functionality or modifying either
visual reference. It surfaces analysis state and currency limitations instead
of inventing a company name, historical date range or brand-new dataset.

The setup/question/upload path remains focused without a sidebar. Once
analysis is complete, the workspace remains visible while the user navigates
between analysis sections; "New diagnosis" returns to the setup flow and
"Landing" explicitly resets the client-side presentation.

Dashboard uses the approved identity palette:
Gold #FFD84D, Cyan #32D3DF, Iris #9275E9, Green #4ADE80 and Red #F87171.
Only **three** business charts are permitted: two within Overview and the
Observed Signals chart within What Changed. All numbers originate from the
analysis response, never the reference screenshot.

## Required before merge — visually verify, don't infer from CI

- [ ] Desktop at ~1440px: left rail remains visible, navigation and active
  section are clear, header/panel hierarchy matches approved references.
- [ ] Overview: read the executive takeaway before findings; KPI cards and
  two charts remain readable with genuine CSV data.
- [ ] Every sidebar destination works without losing the current analysis.
- [ ] Diagnosis evidence modal (Show Me Why) opens, closes via Escape, and
  returns focus accessibly; do not claim all seven stages without review.
- [ ] What Changed: third chart, period labels, numeric values and limitations.
- [ ] Ask BizLens and Report: answers/report retain current analysis and
  expose limitations instead of fabricated AI reasoning.
- [ ] Narrow viewport ~375px: sidebar becomes a compact horizontally
  scrollable navigation bar; no overlapped buttons or page-width overflow.
- [ ] Keyboard: tab navigation, visible focus and `aria-current="page"`.
- [ ] Browser printing: report does not include navigation chrome.
- [ ] Chrome auto-translation off during hydration verification;
  translation-induced React hydration mismatches are not silently
  attributed to business logic.

**CI checks only source health, build and HTTP correctness.** It cannot
approve aesthetic fidelity on its own. Request real browser screenshots
before converting this draft PR to ready/merging.
