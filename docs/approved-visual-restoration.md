# Approved BizLens V1 visual restoration — comparison and acceptance

This visual change **implements the two previously approved references**; it
does not create a third design and does not modify either reference archive.

## Source of truth

1. **Original Figma Make**: [High-Fidelity BizLens Experience](https://www.figma.com/make/8G0aIwZnVF0vtl4sI8KdAI/High-Fidelity-BizLens-Experience) — visual identity and onboarding journey.
2. **Approved new visual prototype**, dated October 17, 2026, preserved
   unchanged in the Library archive `BizLens_Dual_Visual_References_V1.zip`,
   especially its `bizlens_landing_preview.png`,
   `bizlens_overview_preview.png`, and
   `bizlens_mobile_overview_preview.png` — quality bar for workspace.
3. **Unified visual reference** `BizLens_Unified_Visual_Reference_V1.md` —
   black/gold brand, midnight dashboard, five KPIs, spotlight, sidebar,
   exactly three meaningful charts, and evidence-first content.

The approved visual prototype uses illustrative figures that **must not be
copied as live analytics**. This implementation continues to show only
the backend's actual CSV metrics, findings, and chart series.

## Verified implementation gap before this PR

- Current `app/page.tsx` used mutually exclusive full-page screens; it
  had **no persistent workspace sidebar** or direct section navigation.
- Overview had four KPI cards rather than the five shown in the approved
  workspace; AOV was computed but not displayed in its primary KPI row.
- Overview's executive summary appeared after the charts and lacked the
  original visual hierarchy of a prominent observation plus spotlight.
- The landing's `Try Demo` action only scrolled to the illustrative card
  and did **not** start analysis of the demo dataset.
- Base CSS used near-black surfaces for analytics; the approved workspace
  instead calls for distinguishable midnight blue analytical surfaces.

## Changes in this PR

- Keep one loaded analysis object for Overview, Diagnoses, What Changed,
  Ask BizLens and Report. Add persistent desktop sidebar and accessible
  mobile navigation, with real buttons for existing screens.
- Landing's yellow primary action **Try Interactive Demo** reads the
  published synthetic fixture, analyzes it using the existing real
  `/api/analyze` route, then opens Overview. No model/API paid calls
  are added. Loading/errors are visible, and the dataset is explicitly
  marked illustrative.
- Reintroduce 5 KPI cards: revenue, gross profit, overall margin,
  orders, AOV. Mark older CSV row-count order estimates honestly.
- Move one factual headline and a linked takeaway into the top
  overview area. Revenue-up/profit-down wording is conditional on the
  actual two-period numeric comparison. No fabricated claim.
- Keep the previously validated pair of calendar-quarter charts and
  the separate Observed Signals visualization unchanged in data.
- Reinstate approved color semantics: black/gold brand, midnight
  workspace, cyan revenue, iris profit, gold margin, reserved
  green/red for directional observations.

## Release gate: not a visual PASS until actual browser review

CI must pass Python/Ruff, Next.js lint/build and live HTTP smoke for the
**exact review head**. The smoke additionally checks the landing text and
one-click demo entry action are present, but this is not a graphical
click test.

Before declaring design parity, compare the new branch *visually* with
the supplied archive PNGs at ~1440px desktop and ~390px mobile and confirm:

- [ ] Logo gold diamond, headline size, whitespace, CTAs and example-card
  spacing resemble the approved landing.
- [ ] Sidebar stays present for all five sections on desktop; tab
  switching does not lose the analysis id, question context or results.
- [ ] Mobile menu is usable by keyboard and touch, dismisses correctly
  and never obscures navigation permanently.
- [ ] Spotlight is visible before five KPI cards; values derive from the
  live imported dataset; no USD symbol when currency is unspecified.
- [ ] Quarterly charts, three finding previews, evidence drawer,
  What Changed, Ask and Report remain functional after navigation.
- [ ] No horizontal viewport overflow, collapsed text or unusable
  focus indicators at 390px.
- [ ] Invalid CSV and failed demo service result in visible errors.

**Do not merge merely because tests pass.** Confirm screenshot fidelity
and mobile usability with the user's live preview, then finish corrections
on the PR branch before merging. The user Codespace dirty worktree and
the two approved visual-reference source archives must remain untouched.
