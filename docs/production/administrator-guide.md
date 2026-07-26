# Administrator Guide

How to manage PayVerify AI's single administrative account, projects, and data
retention for this MVP release.

## Authentication Model (Current Scope)

This release ships a **minimal, single-account** authentication layer — not a
multi-tenant user/role system. This is an intentional, documented scope
decision for the MVP:

- One configured admin/service account (`ADMIN_USERNAME` +
  `ADMIN_PASSWORD_HASH` environment variables), not a database-backed user
  table
- No role separation (e.g. "consultant" vs "admin") — **explicitly out of
  scope for this release**. Every valid bearer token grants the same access to
  every protected endpoint.
- Feature-flagged via `AUTH_ENABLED` (see
  [deployment-guide.md](deployment-guide.md) and
  [troubleshooting-guide.md](troubleshooting-guide.md#authentication-errors))

If your deployment requires per-consultant accounts, audit trails per user, or
granular permissions, this is the natural next increment — see
[services/ai_gateway.py](../../services/ai_gateway.py)-style extension: add a
`users` table, replace the single env-configured credential check in
`backend/app/auth.py::authenticate_admin` with a database lookup, and add a
`role` claim to the JWT payload.

## Managing the Admin Credential

**Generating a password hash:**
```bash
python scripts/hash_password.py
```
You will be prompted for a password (not echoed) and given a bcrypt hash to
store as `ADMIN_PASSWORD_HASH`. Never commit the plaintext password or store it
anywhere except your deployment platform's secret manager.

**Changing the password:** re-run the script with the new password, update
`ADMIN_PASSWORD_HASH`, and redeploy. All existing JWT tokens remain valid until
they expire (`JWT_EXPIRE_MINUTES`) since password changes don't invalidate
already-issued tokens — rotate `JWT_SECRET` too if you need immediate
invalidation (see [operations-guide.md](operations-guide.md#rotating-secrets)).

**Obtaining a token (for API clients / testing):**
```bash
curl -X POST https://<backend-url>/auth/token \
  -d "username=admin&password=<your-password>"
```
Response:
```json
{"access_token": "eyJhbGci...", "token_type": "bearer"}
```
Use it as `Authorization: Bearer <access_token>` on mutating requests
(`POST /api/projects`, uploads, `POST .../validate`, feedback).

## Managing Projects

Projects are created via `POST /api/projects` (or the frontend UI) and scope
all employees, registers, and variances. There is currently no UI/API to
delete a project — deletion must be done directly against the database if
needed (cascades to employees/registers/variances per the SQLAlchemy
relationship `cascade="all, delete-orphan"` in `backend/app/models.py`):

```sql
DELETE FROM projects WHERE id = <project_id>;
```

**Recommendation:** treat project deletion as a rare, deliberate operation —
back up the database (or export the project's variance data) before deleting.

## Data Retention

This MVP does not implement automatic data retention/expiry policies. All
uploaded registers, employee masters, variances, and feedback persist
indefinitely in Postgres until manually deleted. If your organization has a
data retention requirement (e.g. delete client payroll data after N days),
this must currently be implemented as an external scheduled job (e.g. a cron
task running a `DELETE ... WHERE created_at < NOW() - INTERVAL 'N days'`
query) — **not provided out of the box**.

## Audit Trail

Key mutating actions are recorded in the `audit_log` table (see
[docs/monitoring.md](../monitoring.md#audit-trail-audit_log-table) for schema
and example queries): register uploads, validation runs, and feedback
submissions. This is an immutable append-only log — there is no admin UI to
view it yet; query it directly via SQL.

## Known Limitations (Documented Scope Exclusions)

- No multi-user/role-based access control (see above)
- No project-level access restriction (any authenticated request can access
  any project)
- No self-service password reset flow (admin password is rotated by whoever
  controls the deployment's environment variables)
- No automated data retention/expiry
- No UI for browsing the audit trail (SQL only)

These are acceptable for the current MVP release per the Phase 3.7 acceptance
criteria (explicit documented limitations rather than silent gaps) and are
natural candidates for a future release.
