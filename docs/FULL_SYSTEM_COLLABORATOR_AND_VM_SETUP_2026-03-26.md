# Full-System Collaborator and VM Setup

Date: 2026-03-26
Owner machine root: `/Users/davidusa/REPOS`

## Purpose

This document is the practical handoff for bringing a collaborator onto the active Knowledge Atlas / Article Eater / Article Finder system and for reproducing that system on a second machine or VM.

The important distinction is:

- the **code repos** come from GitHub
- the **meaningful runtime state** still depends on machine-local data and config that are **not** in Git

A collaborator who only clones `Knowledge_Atlas` will be able to inspect the site code, but will **not** be able to reproduce the rebuild pipeline or the current payload-backed system behavior.

## Repos that matter

The active system currently spans these repos:

1. `dkirsh/Knowledge_Atlas`
2. `dkirsh/Article_Eater`
3. `dkirsh/Article_Finder_v3_2_3`
4. `dkirsh/Designing_Experiments`

## Active branches and commits

Current working tips on the owner machine:

- `Knowledge_Atlas`
  - branch: `master`
  - commit: `d07e976`
- `Article_Eater_PostQuinean_v1_recovery`
  - branch: `codex/recovery-cc-migration-artifacts`
  - commit: `f2b7bfa06`
- `Article_Finder_v3_2_3`
  - branch: `main`
  - commit: `ce555c7`
- `Designing_Experiments`
  - branch: `master`
  - commit: `8f29cb2`

If the collaborator wants the same current system state, they should start from those branches.

## Access requirement

The collaborator should have GitHub access to all four repos above.

Giving access to `Knowledge_Atlas` alone is not enough because:

- `Knowledge_Atlas` depends on payloads generated from `Article_Eater`
- Track-2 / intake / discovery workflows depend on `Article_Finder_v3_2_3`
- some course/studio pages still reference `Designing_Experiments`

## Recommended machine specs

### For a collaborator laptop

Minimum practical setup:

- 16 GB RAM
- 50+ GB free SSD space
- Python 3.12
- git
- sqlite
- enough disk for runtime bundles and cloned repos

### For a VM / server

Recommended:

- Ubuntu 24.04 LTS
- 8 vCPU
- 16–32 GB RAM
- 150+ GB SSD
- Python 3.12
- git
- sqlite3
- unzip / zip / build-essential

If the VM is intended to run ongoing rebuilds and hold large PDF / Mathpix / verification state, prefer 32 GB RAM and 200+ GB SSD.

## macOS setup

```bash
xcode-select --install
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.12 git gh sqlite
brew install --cask visual-studio-code
```

Optional:

```bash
brew install node
```

`node` is not required for the current rebuild path, but is useful for some older validators in `Article_Eater`.

## Ubuntu / VM setup

```bash
sudo apt update
sudo apt install -y software-properties-common build-essential git gh sqlite3 zip unzip curl ca-certificates
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
```

Verify:

```bash
python3.12 --version
git --version
sqlite3 --version
```

## Clone commands

```bash
mkdir -p ~/REPOS
cd ~/REPOS

git clone https://github.com/dkirsh/Knowledge_Atlas.git
git clone https://github.com/dkirsh/Article_Eater.git Article_Eater_PostQuinean_v1_recovery
git clone https://github.com/dkirsh/Article_Finder_v3_2_3.git
git clone https://github.com/dkirsh/Designing_Experiments.git
```

## Branch checkout

```bash
cd ~/REPOS/Knowledge_Atlas
git checkout master
git pull

cd ~/REPOS/Article_Eater_PostQuinean_v1_recovery
git checkout codex/recovery-cc-migration-artifacts
git pull

cd ~/REPOS/Article_Finder_v3_2_3
git checkout main
git pull

cd ~/REPOS/Designing_Experiments
git checkout master
git pull
```

## Personal branch model

For full-system collaboration, use personal branches per repo, not the course `track/*` branch model.

Recommended:

```bash
cd ~/REPOS/Knowledge_Atlas
git checkout -b <username>/ka-work

cd ~/REPOS/Article_Eater_PostQuinean_v1_recovery
git checkout -b <username>/ae-work

cd ~/REPOS/Article_Finder_v3_2_3
git checkout -b <username>/af-work

cd ~/REPOS/Designing_Experiments
git checkout -b <username>/de-work
```

## Python environments

### Article Eater

```bash
cd ~/REPOS/Article_Eater_PostQuinean_v1_recovery
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Optional dev extras:

```bash
pip install -r requirements-dev.txt
```

### Article Finder

```bash
cd ~/REPOS/Article_Finder_v3_2_3
python3.12 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -e .
pip install -r requirements.txt
```

### Knowledge Atlas

Knowledge Atlas is currently mostly static HTML / JS plus Python payload builders.

If a separate venv is desired:

```bash
cd ~/REPOS/Knowledge_Atlas
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

In practice, the AE venv can usually run the KA payload-builder scripts as long as the repos sit side by side under `~/REPOS`.

## Critical non-git runtime state

A second machine cannot reproduce the current system from Git alone.

### Required machine-local assets

These are the most important machine-local assets:

#### From `Article_Eater_PostQuinean_v1_recovery`

- `config/pdf_preprocessor_bakeoff.env`
- `data/pdf_cache/`
- `data/extraction_pipeline/`
- `data/rebuild/`
- `data/verification_runs/`
- `data/extraction_pipeline.db`
- `data/article_eater.db`
- `data/environment_images.db`

#### From `Article_Finder_v3_2_3`

- `config/settings.local.yaml`
- `data/article_finder.db`
- `data/bibliographer_state.json`
- `data/ae_jobs/`
- `data/job_bundles/`

### Optional but valuable local assets

These are useful if the collaborator will also do acquisition / corpus maintenance work in Article Finder:

- `Article_Finder_v3_2_3/data/pdfs/`
- any top-level PDF files already present inside `Article_Finder_v3_2_3/data/`

## Handoff archives created on the owner machine

Two archive layers are recommended:

### 1. Runtime bundle (required)

Purpose:

- enough machine-local state to reproduce the current rebuild / payload / verification environment
- smaller and more practical than shipping every Article Finder PDF immediately

### 2. Full Article Finder corpus bundle (optional)

Purpose:

- adds the larger local PDF / AF corpus state for discovery and acquisition work
- useful for a fuller mirror or server deployment

## Security note

The runtime bundle includes local config and API-related settings.

Do **not** commit these files to GitHub.
Transfer them directly and securely.

## First smoke tests after setup

### Article Finder

```bash
cd ~/REPOS/Article_Finder_v3_2_3
source venv/bin/activate
python cli/main.py stats
```

### Article Eater

```bash
cd ~/REPOS/Article_Eater_PostQuinean_v1_recovery
source .venv/bin/activate
python3 -m py_compile src/services/deep_stat_candidate_aggregator.py
python3 scripts/build_deep_stat_adjudication_batch.py
```

### Knowledge Atlas payload rebuild

```bash
cd ~/REPOS/Knowledge_Atlas
python3 scripts/build_ka_adapter_payloads.py
```

### View the site locally

```bash
cd ~/REPOS/Knowledge_Atlas
python3 -m http.server 8080
```

Open:

- `http://localhost:8080/ka_home.html`

## VM operational notes

If the VM is intended to act as a server-like rebuild machine:

1. keep the same repo layout under `~/REPOS` or `/srv/REPOS`
2. install the Python environments exactly as above
3. unpack the runtime bundle so the relative repo paths match the code assumptions
4. verify:
   - AF CLI works
   - AE rebuild scripts can read their local DBs and data dirs
   - KA payload builder runs from the rebuilt outputs
5. only after that start thinking about daemonization, cron, or service wrappers

The first goal is reproducibility, not deployment sophistication.

## Recommended order of operations for a new machine

1. install system packages
2. clone repos
3. check out the active branches
4. create virtual environments
5. unpack the runtime bundle into the repo roots
6. run the smoke tests
7. open the site locally
8. only then try Mathpix, rebuilds, or AF discovery workflows

## Bottom line

A collaborator needs:

- the four code repos
- the correct active branches
- the Python environments
- the local runtime bundles

Without the local runtime bundles, they will have the shell of the system but not the current working rebuild state.
