# Contributing to BizLens

Thank you for helping improve BizLens.

## Before you contribute

Please keep the core principles in mind:

- calculations belong to deterministic code
- diagnoses must be evidence-backed
- confidence and limitations must be explicit
- AI should interpret verified context, not invent business facts
- every diagnosis rule needs tests

## Development workflow

1. Create a focused branch.
2. Make the smallest coherent change.
3. Add or update tests.
4. Run the local checks.
5. Open a pull request describing the problem, approach and validation.

## Diagnosis rules

A new diagnosis should document:

- diagnosis name and identifier
- business problem being detected
- exact trigger conditions
- calculation and thresholds
- required evidence
- confidence limitations
- impact interpretation
- recommended action
- positive test cases
- negative test cases

Avoid rules that depend on vague language-model judgments when the underlying signal can be calculated deterministically.

## Local checks

Backend:

```bash
pytest
```

Frontend:

```bash
cd apps/web
npm run lint
npm run build
```

## Pull requests

Keep pull requests focused. Include screenshots for meaningful UI changes and explain any change to diagnosis logic or AI behavior.
