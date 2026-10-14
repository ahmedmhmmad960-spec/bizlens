# BizLens Visual Direction — Approved Demo Design Reference

**Status:** Approved visual direction by project owner, 2026-10-14.  
**Scope:** Design specification for engineering follow-up; not a claim that UI was implemented.

## Core aesthetic: Cinematic Minimal Intelligence

**Use ~70% of the previous funder-demo UI direction + ~30% of the newer dashboard reference.** This is design guidance, not a rigid pixel or code ratio.

### Preserve from the earlier demo
- Calm premium midnight/navy surfaces, readable information hierarchy, generous whitespace.
- One clearly dominant business-performance time-series visualization.
- Diagnosis/evidence as the focal point, not charts for their own sake.
- Restrained cyan/iris accents, purposeful semantic indicators and subtle motion.
- Clean executive summary, visible Show Me Why and next-decision affordances.

### Adapt from the newer reference
- Compact persistent side navigation for Overview, Findings, Show Me Why, Decision Twin, Business Memory, Ask BizLens, Base/USDC and Reports (with responsive mobile adaptation).
- Easily accessible global Ask BizLens search, navigation and current business context.
- Coherent brand, reusable cards, keyboard states, and precise design tokens.

### Explicit exclusions
- **No more than three primary charts on the executive home screen**. Decision Twin may have its own scenario graphs.
- Avoid decorative glow overload, gratuitous charts, densely packed KPI grids, animated backgrounds, and repetitive cards.
- Do not add Sudan-specific/geolocation imagery or merchant-status badges to the generic end-user product dashboard.
- Do not display unverified precision or invented financial evidence; synthetic demo data must be labeled.
- Do not copy generated mockups literally; visuals and numerical labels in generated images can be inconsistent.
- Preserve existing user flows/functionality. No redesign just to resemble Stripe, Linear or other platforms.

## Suggested design tokens (targets, subject to accessibility testing)

| Role | Token | Value | Use |
|---|---|---|---|
| Canvas | midnight | `#080F1D` | Main deep background |
| Surface | slate | `#17283C` | Layered cards and navigation |
| Primary accent | ice cyan | `#32D3DF` | Primary analytical focus / chart series |
| Secondary accent | iris | `#9275E9` | Comparison / alternative series |
| Reserved highlight | gold | `#F3CA65` | Rare priority/action focus |
| Risk | critical | `#F87171` | Negative outcomes/errors only |

Use accessible neutral text shades and contrast tokens after testing. Distinguish positive/negative with labels/icons as well as color. Do not encode chart meaning through hues alone.

## Information hierarchy (desktop funder demo)

1. Sidebar/nav + current dataset context.
2. Executive diagnosis headline and 3–4 concise metrics.
3. **Main chart**: Business Performance (single large time-series).
4. **Diagnosis spotlight**: the most important evidence-backed finding next to chart, Show Me Why entry.
5. **Driver chart**: compact explanation of quantifiable changes only where actual decomposition is valid.
6. **Base / USDC summary**: a third small, optional reconciled/missing chart (only after implementation); can be deferred.
7. Primary action: Compare Decisions → Decision Twin.
8. Secondary access: Business Memory / Report / Ask BizLens.

**Do not overload landing with every product feature.** Detailed evidence views, Decision Twin and Business Memory should have focused destinations.

## Interaction and motion

- Meaningful smooth transitions, 150–250 ms typically; no prolonged entrance animations.
- Chart hover/focus exposes exact values, time range and evidence link. Keyboard-accessible alternatives required.
- Use subtle hover/highlight/glow only to indicate interactive states.
- Respect `prefers-reduced-motion`; responsive from mobile to widescreen.
- Favor clear typography and readable chart tick labels over tiny decorative labels.

## Implementation notes discovered during code review

- Inspect the apparent missing global/component import of `apps/web/components/diagnosis-feed.css`; verify actual compiled styles and tests before changing.
- `apps/web/app/layout.tsx` loads Geist while `apps/web/app/globals.css` sets body to Arial; unify the font stack after visual verification.
- Current page architecture is a serial multi-screen flow; add durable navigation thoughtfully without removing existing analytic journey.
- Keep current functional metrics, evidence, replay, Ask BizLens, report and tests intact.
- Financial dataset schema and diagnosis correctness take precedence over chart animation.
- Implement in a separate reviewed code PR, then take real screenshots (desktop/mobile) and compare against this spec and accessibility checklist.

## Definition of design acceptance

- Dominant diagnosis and action readable immediately; chart should answer a specific question.
- Max 3 meaningful executive charts; no misleading axis scales or stacked ambiguity.
- Clear keyboard focus, accessible contrast, visible error/empty/loading/insufficient-evidence states.
- Mobile + desktop QA screenshots from *running code*, not generated concepts.
- Synthetic demo figures all reconcile with source fixtures and backend calculations.
- Existing core experience still functional; CI/automated tests pass before merge.

This document is the **approved design reference**, not a completed visual implementation.
