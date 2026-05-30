# Rule 04 — Security Checklist (release gate)

On completion, set `status.json → checklists.security.state`. A `failed`/`not-run` state blocks release.
For high-stakes changes, run this via a dedicated verification subagent. Consider the `security-review` skill.

## Secrets & config
- [ ] No secrets in code, logs, or client bundles. Secrets in env/secret manager only.
- [ ] `.env` and key material gitignored; secret scanning enabled in CI.
- [ ] Least-privilege keys; rotation plan documented.

## AuthN / AuthZ
- [ ] Every endpoint/resource enforces authorization server-side (never trust the client).
- [ ] Supabase RLS (or equivalent) enabled and tested for every table; default-deny.
- [ ] Session/token expiry, refresh, and revocation handled.
- [ ] Object-level access checks (no IDOR); tenant isolation verified for multi-tenant.

## Input & data
- [ ] All input validated/sanitized server-side; parameterized queries (no string-built SQL).
- [ ] Output encoding to prevent XSS; CSRF protection on state-changing requests.
- [ ] File uploads: type/size limits, virus/type sniffing, stored off-origin.
- [ ] PII inventory known; encrypted at rest + in transit; retention/deletion path exists.

## Platform / supply chain
- [ ] Dependencies scanned (Dependabot/audit); no known criticals shipped.
- [ ] Pinned/locked versions; provenance for critical deps.
- [ ] Security headers (CSP, HSTS, X-Content-Type-Options, frame-ancestors).
- [ ] Rate limiting / abuse protection on public + auth endpoints.

## Mobile / streaming
- [ ] No secrets in the app binary; certificate pinning where warranted.
- [ ] Keychain/Keystore for sensitive storage; jailbreak/root posture decided.
- [ ] DRM keys handled per platform requirements; license server access controlled.

## AI service
- [ ] Prompt-injection mitigations; untrusted content sandboxed from tool/agent authority.
- [ ] Output filtering for sensitive data leakage; no secrets reachable by the model.
- [ ] Per-user spend caps; logging excludes raw PII/prompts where required.

## Compliance
- [ ] Applicable regimes identified (GDPR/CCPA/App Store/Play/SOC2) — track via `operations:compliance-tracking`.
- [ ] Consent + privacy policy present for any data capture (incl. email capture loops).
