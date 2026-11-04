---
name: crm-preview
description: Launch the Django CRM locally on a throwaway database with Keycloak mocked, to look at a CRM template or view change in a browser. Use when a change touches crm/ (templates, views, static) and the result must be reviewed visually, or when asked for a local preview of the CRM.
---

# CRM preview (throwaway DB, no Keycloak)

The CRM views use `@keycloak_required` and Keycloak is not configured locally. `scripts/serve.py` mocks the token validation in its own process only, so nothing in the repo is modified. Data goes into a separate database (`crm_preview` by default), never `preprod_nalo4`. To run several previews side by side (one worktree or ticket each), pick another name, for example `DB=crm_preview_<ticket>`, and another `PORT`.

Prerequisites: local PostgreSQL (user `preprod`, password `1234`, see `conf/settings.py`) and `uv sync` done. Run everything from `services/backend` of the worktree to preview.

## Steps

```bash
S=~/.claude/skills/crm-preview/scripts
DB=crm_preview   # database name, change it to keep several previews apart

# 1. Throwaway DB migrated with the branch code
PGPASSWORD=1234 psql -h localhost -U preprod -d postgres -c "drop database if exists $DB" -c "create database $DB"
DATABASE_NAME=$DB uv run python manage.py migrate

# 2. Base data: one client with a contract (profile 1) and a staff account. Run once, alone.
DATABASE_NAME=$DB uv run python $S/seed.py

# 3. Optional topic data: your own seed_<topic>.py, see "Another page or ticket" below.

# 4. Server on http://127.0.0.1:8765 (PORT=xxxx to change it; run in the background if needed)
DATABASE_NAME=$DB uv run python $S/serve.py
```

## Open a page

1. Open any URL of the server, for example `http://127.0.0.1:8765/static/crm/assets/global/plugins/bootstrap/css/bootstrap.min.css`.
2. In the browser console: `document.cookie = "access_token=x; path=/"`.
3. Go to the page, for example the client sheet `http://127.0.0.1:8765/crm/user/1?tab=alerts`.

With curl: `curl -b "access_token=x" http://127.0.0.1:8765/crm/user/1`.

When a browser tool is available (chrome-devtools), set the cookie with `evaluate_script`, navigate, scroll to the element and take a screenshot to look at the result. Look at it before saying the design is fine.

## Pitfalls

- `IntegrityError ... james.bond+test1@nalo.fr`: two seeds ran at the same time, or the DB is already seeded. Redo step 1.
- `Failed to synchronize user ... realms/None/...` logs come from the Keycloak sync and are harmless.
- `ValueError: multiple authentication backends`: the `backend=` argument is missing in `login` (already set in `serve.py`).
- `serve.py` does not auto-reload. Restart it after a change in Python code. Template changes show on reload.
- Never run `create_complete_user` against a shared database, it creates test users.

## Stop and clean up

```bash
pkill -f crm-preview/scripts/serve.py
dropdb -h localhost -U preprod "${DB:-crm_preview}"
```

## Another page or ticket

Only the seed changes. Add a `scripts/seed_<topic>.py` that creates the objects to display, starting from the base data:

```python
profile = Profile.objects.get(pk=1)
contract = Contract.objects.filter(user=profile.user).first()
```

Reuse the header of `seed.py` (path, settings, `DATABASE_NAME`, `django.setup()`). Create the objects with the model fields or the project factories, then open the page that lists them. Do not commit a seed that depends on a field not yet merged in `develop`.
