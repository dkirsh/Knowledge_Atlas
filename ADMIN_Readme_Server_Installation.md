# ADMIN Readme — Server Installation

This document explains how to install the Knowledge Atlas site on a server, using GitHub as the source of truth for the files.

It covers two deployment modes:

1. `KA-only site deployment`
   Use this if you want to serve the current Knowledge Atlas site and API exactly as it exists in the `Knowledge_Atlas` repo.

2. `Full ATLAS deployment with rebuild + payload refresh`
   Use this if you want the server to regenerate live KA payloads from the canonical Article Eater rebuild outputs when new papers are promoted.

The second mode is the real production path.

## 1. What Is Being Installed

The live server has three main parts.

- Static site files from the GitHub repo `https://github.com/dkirsh/Knowledge_Atlas.git`
- A FastAPI server in [`ka_auth_server.py`](/Users/davidusa/REPOS/Knowledge_Atlas/ka_auth_server.py) that serves both the API and the static files
- SQLite databases and payload JSON files under [`data/`](/Users/davidusa/REPOS/Knowledge_Atlas/data)

If you want live payload regeneration, there is a fourth part:

- The canonical rebuild repo `https://github.com/dkirsh/Article_Eater.git`, used by [`scripts/build_ka_adapter_payloads.py`](/Users/davidusa/REPOS/Knowledge_Atlas/scripts/build_ka_adapter_payloads.py)

## 2. Required Repositories

Clone these two repositories from GitHub:

- `Knowledge_Atlas`
- `Article_Eater`

Recommended server layout:

```text
/srv/atlas/
  Knowledge_Atlas/
  Article_Eater_PostQuinean_v1_recovery/
```

The payload builder now supports portable paths via environment variables, so you do not need to recreate the local `/Users/davidusa/REPOS` layout.

## 3. Server Prerequisites

Install:

- Ubuntu 22.04 or similar Linux distribution
- Python 3.10 or newer
- `git`
- `sqlite3`
- `nginx` if you want a public reverse proxy
- a persistent storage mount for uploaded PDFs

Recommended persistent storage mount:

```text
/mnt/ka_storage
```

The article intake module uses:

- `/mnt/ka_storage/quarantine`
- `/mnt/ka_storage/pdf_collection`
- `/mnt/ka_storage/rejected`

These are controlled by environment variables and can be moved if needed.

## 4. Clone From GitHub

```bash
sudo mkdir -p /srv/atlas
sudo chown "$USER":"$USER" /srv/atlas
cd /srv/atlas

git clone https://github.com/dkirsh/Knowledge_Atlas.git
git clone https://github.com/dkirsh/Article_Eater.git Article_Eater_PostQuinean_v1_recovery
```

## 5. Python Environment

```bash
cd /srv/atlas/Knowledge_Atlas
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install \
  fastapi \
  uvicorn \
  "python-jose[cryptography]" \
  "passlib[bcrypt]" \
  python-multipart \
  aiofiles \
  email-validator
```

The current KA server does not use a `requirements.txt`, so these packages must be installed explicitly.

## 6. Create Storage Directories

```bash
sudo mkdir -p /mnt/ka_storage/quarantine
sudo mkdir -p /mnt/ka_storage/pdf_collection
sudo mkdir -p /mnt/ka_storage/rejected
sudo chown -R "$USER":"$USER" /mnt/ka_storage
```

If you want a different root, set:

- `KA_STORAGE_ROOT`
- `KA_QUARANTINE_DIR`
- `KA_PDF_COLLECTION_DIR`
- `KA_REJECTED_DIR`

## 7. Database Inventory

There are two KA-side SQLite databases.

### 7.1 [`data/ka_auth.db`](/Users/davidusa/REPOS/Knowledge_Atlas/data/ka_auth.db)

This is the operational database for:

- users
- password reset tokens
- refresh tokens
- research questions
- article submissions
- submission batches
- audit log
- question claims

This database is created automatically on first server start.

Current tables:

- `users`
- `reset_tokens`
- `refresh_tokens`
- `research_questions`
- `articles`
- `submission_batches`
- `audit_log`
- `question_claims`

### 7.2 [`data/ka_workflow.db`](/Users/davidusa/REPOS/Knowledge_Atlas/data/ka_workflow.db)

This is a lighter workflow/demo-state database used by the payload builder.

Current tables:

- `registrations`
- `intake_submissions`
- `track_targets`

This is not the same thing as the auth database.

If you want the exact local demo state, copy this file from the source machine.

If you only need the site to run, the payload builder can recreate the tables it needs.

## 8. Article Eater Dependency

If you want live KA payload regeneration, the following Article Eater outputs must exist:

- `data/rebuild/web_persistence_v5.db`
- `data/rebuild/gold_claims_v7.jsonl`
- `data/rebuild/research_fronts_v7.json`
- `data/verification_runs/v7_gold_extraction_registry.db`

These are read by [`scripts/build_ka_adapter_payloads.py`](/Users/davidusa/REPOS/Knowledge_Atlas/scripts/build_ka_adapter_payloads.py).

Without them, the KA site can still serve whatever payload JSON is already committed in `Knowledge_Atlas/data/ka_payloads`, but it cannot regenerate from the live canonical corpus.

## 9. Build KA Payloads

Run this from the KA repo:

```bash
cd /srv/atlas/Knowledge_Atlas
source .venv/bin/activate

export KA_REPO_PATH=/srv/atlas/Knowledge_Atlas
export KA_AE_REPO_PATH=/srv/atlas/Article_Eater_PostQuinean_v1_recovery
export KA_REPOS_ROOT=/srv/atlas

python3 scripts/build_ka_adapter_payloads.py
```

This writes JSON payloads under:

```text
/srv/atlas/Knowledge_Atlas/data/ka_payloads/
```

Important payloads include:

- `articles.json`
- `evidence.json`
- `topics.json`
- `topic_hierarchy.json`
- `topic_memberships.json`
- `topic_ontology.json`
- `research_fronts.json`
- `workflow.json`

## 10. Configure the API Base

The KA pages read [`ka_config.js`](/Users/davidusa/REPOS/Knowledge_Atlas/ka_config.js).

For same-origin deployment, keep:

```javascript
window.__KA_CONFIG__ = {
  apiBase: '',
  siteName: 'Knowledge Atlas',
  courseCode: 'COGS 160',
  quarter: 'Spring 2026',
};
```

This is the recommended production setting if the API and HTML are served from the same host and port through the same reverse proxy.

## 11. First Server Start

```bash
cd /srv/atlas/Knowledge_Atlas
source .venv/bin/activate

export KA_STORAGE_ROOT=/mnt/ka_storage
export KA_SECRET_KEY="$(openssl rand -hex 32)"

python3 ka_auth_server.py
```

By default it starts on:

```text
http://127.0.0.1:8765
```

This first start will:

- create `data/ka_auth.db`
- create `data/ka_auth_secret.txt` if `KA_SECRET_KEY` is not supplied
- seed the instructor account if none exists
- initialize article-submission tables

### Important first-login warning

The server seeds this instructor account:

- email: `dkirsh@ucsd.edu`
- password: `atlas2026`

Change it immediately after first start.

The current password-reset flow prints reset links to the server console. That is acceptable for private development, but you should treat it as an administrative convenience, not a polished public recovery system.

## 12. Recommended Production Run: systemd

Create:

```text
/etc/systemd/system/knowledge-atlas.service
```

Use:

```ini
[Unit]
Description=Knowledge Atlas
After=network.target

[Service]
Type=simple
User=atlas
Group=atlas
WorkingDirectory=/srv/atlas/Knowledge_Atlas
Environment=KA_STORAGE_ROOT=/mnt/ka_storage
Environment=KA_SECRET_KEY=REPLACE_WITH_LONG_RANDOM_SECRET
Environment=KA_REPO_PATH=/srv/atlas/Knowledge_Atlas
Environment=KA_AE_REPO_PATH=/srv/atlas/Article_Eater_PostQuinean_v1_recovery
Environment=KA_REPOS_ROOT=/srv/atlas
ExecStart=/srv/atlas/Knowledge_Atlas/.venv/bin/uvicorn ka_auth_server:app --host 127.0.0.1 --port 8765
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable knowledge-atlas
sudo systemctl start knowledge-atlas
sudo systemctl status knowledge-atlas
```

## 13. Recommended Public Serving: nginx

Create a site file such as:

```text
/etc/nginx/sites-available/knowledge-atlas
```

Example:

```nginx
server {
    listen 80;
    server_name atlas.example.edu;

    client_max_body_size 150M;

    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then:

```bash
sudo ln -s /etc/nginx/sites-available/knowledge-atlas /etc/nginx/sites-enabled/knowledge-atlas
sudo nginx -t
sudo systemctl reload nginx
```

Add TLS with your normal certificate process after the plain HTTP proxy works.

## 14. Full Rebuild + Payload Refresh Procedure

When new PDFs have been validated and promoted, rebuild the canonical corpus first, then regenerate the KA payloads.

### 14.1 Canonical rebuild

```bash
cd /srv/atlas/Article_Eater_PostQuinean_v1_recovery
bash scripts/rebuild_all.sh
```

This replaces the live rebuild outputs, including:

- `data/rebuild/web_persistence_v5.db`
- `data/rebuild/gold_claims_v7.jsonl`
- `data/rebuild/research_fronts_v7.json`

### 14.2 Refresh KA payloads

```bash
cd /srv/atlas/Knowledge_Atlas
source .venv/bin/activate

export KA_REPO_PATH=/srv/atlas/Knowledge_Atlas
export KA_AE_REPO_PATH=/srv/atlas/Article_Eater_PostQuinean_v1_recovery
export KA_REPOS_ROOT=/srv/atlas

python3 scripts/build_ka_adapter_payloads.py
sudo systemctl restart knowledge-atlas
```

## 15. If You Need Exact Local State

If you want the server to look exactly like the current local demonstration state, copy these items from the source machine after the GitHub clone:

- `Knowledge_Atlas/data/ka_auth.db`
- `Knowledge_Atlas/data/ka_workflow.db`
- `Knowledge_Atlas/data/ka_payloads/`
- `Article_Eater_PostQuinean_v1_recovery/data/rebuild/`
- `Article_Eater_PostQuinean_v1_recovery/data/verification_runs/v7_gold_extraction_registry.db`

If you do not copy them, the server can still run, but it will reflect a fresh operational state unless you regenerate everything.

## 16. Smoke Test Checklist

After deployment, test these:

```bash
curl http://127.0.0.1:8765/health
curl -I http://127.0.0.1:8765/ka_home.html
curl -I http://127.0.0.1:8765/ka_user_home.html
curl -I http://127.0.0.1:8765/ka_topic_hierarchy.html
curl -I http://127.0.0.1:8765/160sp/ka_schedule.html
curl -I http://127.0.0.1:8765/docs
```

Then open in a browser:

- `/ka_home.html`
- `/ka_user_home.html`
- `/ka_workflow_hub.html?wf=student-probe`
- `/ka_topic_hierarchy.html`
- `/ka_topics.html`
- `/ka_evidence.html`
- `/ka_article_search.html`
- `/160sp/ka_schedule.html`

## 17. Backup Instructions

Back up these locations:

- `/srv/atlas/Knowledge_Atlas/data/ka_auth.db`
- `/srv/atlas/Knowledge_Atlas/data/ka_workflow.db`
- `/srv/atlas/Knowledge_Atlas/data/ka_payloads/`
- `/mnt/ka_storage/quarantine/`
- `/mnt/ka_storage/pdf_collection/`
- `/mnt/ka_storage/rejected/`
- `/srv/atlas/Article_Eater_PostQuinean_v1_recovery/data/rebuild/`

SQLite backup example:

```bash
sqlite3 /srv/atlas/Knowledge_Atlas/data/ka_auth.db ".backup '/srv/atlas/backups/ka_auth_$(date +%F).db'"
sqlite3 /srv/atlas/Knowledge_Atlas/data/ka_workflow.db ".backup '/srv/atlas/backups/ka_workflow_$(date +%F).db'"
```

## 18. Common Failure Modes

### Builder cannot find Article Eater outputs

Cause:

- `KA_AE_REPO_PATH` not set
- wrong sibling repo path
- canonical rebuild not run

Fix:

- confirm `/srv/atlas/Article_Eater_PostQuinean_v1_recovery/data/rebuild/web_persistence_v5.db` exists
- export `KA_AE_REPO_PATH`
- rerun the canonical rebuild first

### Pages load but payloads are stale

Cause:

- site was deployed from GitHub but payload regeneration was not run after rebuild

Fix:

- rerun `python3 scripts/build_ka_adapter_payloads.py`

### API works but uploads fail

Cause:

- `KA_STORAGE_ROOT` missing
- write permissions wrong
- nginx `client_max_body_size` too small

Fix:

- fix directory ownership
- confirm `quarantine`, `pdf_collection`, `rejected` exist
- increase reverse-proxy upload limit

### Auth works but the UI points to the wrong API host

Cause:

- `ka_config.js` has the wrong `apiBase`

Fix:

- for same-origin deployment, set `apiBase: ''`

## 19. Minimal Command Sequence

If you want the shortest version:

```bash
cd /srv/atlas
git clone https://github.com/dkirsh/Knowledge_Atlas.git
git clone https://github.com/dkirsh/Article_Eater.git Article_Eater_PostQuinean_v1_recovery

cd /srv/atlas/Knowledge_Atlas
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn "python-jose[cryptography]" "passlib[bcrypt]" python-multipart aiofiles email-validator

mkdir -p /mnt/ka_storage/quarantine /mnt/ka_storage/pdf_collection /mnt/ka_storage/rejected

export KA_STORAGE_ROOT=/mnt/ka_storage
export KA_SECRET_KEY="$(openssl rand -hex 32)"
export KA_REPO_PATH=/srv/atlas/Knowledge_Atlas
export KA_AE_REPO_PATH=/srv/atlas/Article_Eater_PostQuinean_v1_recovery
export KA_REPOS_ROOT=/srv/atlas

cd /srv/atlas/Article_Eater_PostQuinean_v1_recovery
bash scripts/rebuild_all.sh

cd /srv/atlas/Knowledge_Atlas
python3 scripts/build_ka_adapter_payloads.py
python3 ka_auth_server.py
```

That is enough to get the site up, but for anything serious you should run it under `systemd` and `nginx`.
