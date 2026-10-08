# Security Policy

## Reporting a vulnerability

Please do not open a public issue for a suspected security vulnerability.

Use the repository's private security reporting channel when available. If private reporting is not available, contact the maintainers before disclosing sensitive details publicly.

When reporting a vulnerability, include:

- affected component or endpoint
- reproduction steps
- expected and actual behavior
- potential impact
- any relevant logs or proof of concept that does not contain real credentials or customer data

## Secrets and business data

Never commit:

- API keys
- passwords
- access tokens
- production credentials
- private customer data
- real business datasets without explicit authorization

Use environment variables for local secrets and the provided example environment files as templates.

## Supported versions

The `main` branch is the actively maintained development line while BizLens is in pre-1.0 development.
