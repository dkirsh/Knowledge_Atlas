# Workspace Registry

Date: 2026-03-24
Scope:
- `/Users/davidusa/REPOS` multi-repo workspace

## Purpose

This file records the canonical owner for each active repo and major workspace artifact so agents do not keep creating new source-of-truth confusion.

## Canonical repos

### 1. Knowledge_Atlas
Path:
- `/Users/davidusa/REPOS/Knowledge_Atlas`

Role:
- canonical GUI / site / navigation / interaction repo
- home for Atlas-facing pages, contributor pages, class-facing site integration, and GUI design standards

Git status:
- real git repo
- remote configured
- `master` pushed
- staging branches pushed: `track/1-staging` through `track/4-staging`

Owns:
- KA HTML/JS/CSS pages
- GUI architecture docs
- mode-switch behavior
- intake UX contracts
- repo/workspace stabilization docs

### 2. Article_Eater_PostQuinean_v1_recovery
Path:
- `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1_recovery`

Role:
- canonical extraction / rebuild / theory / summary / JSON / Master Doc repo

Git status:
- real git repo
- remote configured
- branch `codex/recovery-cc-migration-artifacts` active

Owns:
- canonical Master Doc
- theory/rebuild semantics
- gold-claim pipeline
- summaries and science-writer outputs
- recovery-side course infrastructure docs where tightly coupled to the rebuild system

### 3. Designing_Experiments
Path:
- `/Users/davidusa/REPOS/Designing_Experiments`

Role:
- course docs, experiment-design assets, research-front materials, and legacy/embedded frontend assets

Git status:
- real git repo
- remote configured: `https://github.com/dkirsh/Designing_Experiments.git`

Owns:
- experiment-design docs
- wizard/reference docs
- course packs and teaching materials that are not canonical KA pages

### 4. Article_Finder_v3_2_3
Path:
- `/Users/davidusa/REPOS/Article_Finder_v3_2_3`

Role:
- article intake / citation parsing / PDF cataloging / literature search engine

Git status:
- now re-initialized as a standalone local repo after the accidental root repo was archived
- remote configured: `https://github.com/dkirsh/Article_Finder_v3_2_3.git`

Owns:
- AF ingestion and search code
- DOI/citation/PDF normalization logic
- AF-local secrets templates and local settings

## Non-repo workspace areas

### `theory_guides`
Path:
- `/Users/davidusa/REPOS/theory_guides`

Role:
- standalone theory-guide corpus
- now backed up as its own git repo:
  - `https://github.com/dkirsh/theory_guides.git`
- should still be treated as content to integrate, not as a primary operational repo

### `Backups`
Path:
- `/Users/davidusa/REPOS/Backups`

Role:
- archive storage for workspace-level safety actions
- currently includes the archived accidental root git metadata:
  - `/Users/davidusa/REPOS/Backups/REPOS_root_git_backup_2026-03-24`

## Canonical document rules

### Master Doc
Canonical location:
- `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1_recovery/docs/MASTER_DOC_CMR_2026-02-25.md`

Secondary assembled surface:
- `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1_recovery/docs/MASTER_DOC_CMR_ASSEMBLED.md`

Non-canonical duplicate still present:
- `/Users/davidusa/REPOS/MASTER_DOC_CMR_2026-02-25.md`

Rule:
- do not treat the root copy as authoritative
- the root file is now only a pointer stub redirecting readers to the canonical AE recovery docs path
- future updates belong in the canonical AE recovery docs path

### Root-level loose files
Rule:
- no new design/spec/docs files should be created at `/Users/davidusa/REPOS` root
- repo-local `docs/` directories are the default home
- operational exceptions at root should be rare and justified

## Current operational exceptions at `/Users/davidusa/REPOS` root

These are now the only intentional root-level files:
- `CLAUDE.md`
- `MASTER_DOC_CMR_2026-02-25.md` (pointer stub only; canonical content archived out of root)
- `TOPIC_PROGRESS.md` (intentional workspace-level operational log)

## Root-level organization buckets

Non-repo workspace material has been grouped into:
- `/Users/davidusa/REPOS/Workspace_Docs`
- `/Users/davidusa/REPOS/Workspace_Data`
- `/Users/davidusa/REPOS/Workspace_Media`
- `/Users/davidusa/REPOS/Workspace_Scripts`
- `/Users/davidusa/REPOS/Backups/root_file_archive_2026-03-24`

## Source-of-truth summary

If an agent needs to know where to work first:
1. GUI / site / nav / contributor flows -> `Knowledge_Atlas`
2. JSON / theory / extraction / Master Doc / summaries -> `Article_Eater_PostQuinean_v1_recovery`
3. course docs / experiment builder materials -> `Designing_Experiments`
4. intake / citation / PDF / literature-search engine -> `Article_Finder_v3_2_3`

## Enforcement rule

Before creating a new major doc or code artifact, decide:
1. which repo owns the subject matter
2. whether the file is canonical or auxiliary
3. whether the Master Doc needs an update or brief

If those answers are unclear, stop and resolve ownership before creating another loose root file.
