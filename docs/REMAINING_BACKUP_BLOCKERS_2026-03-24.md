# Remaining Backup Blockers

Date: 2026-03-24

## Completed in this cleanup pass

- archived the accidental workspace-level git metadata from `/Users/davidusa/REPOS/.git` into `/Users/davidusa/REPOS/Backups/REPOS_root_git_backup_2026-03-24`
- restored independent repo behavior for:
  - `/Users/davidusa/REPOS/Knowledge_Atlas`
  - `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1_recovery`
  - `/Users/davidusa/REPOS/Designing_Experiments`
  - `/Users/davidusa/REPOS/Article_Finder_v3_2_3`
- pushed `Knowledge_Atlas/master` through commit `f7af13d`
- pushed `Article_Eater_PostQuinean_v1_recovery/codex/recovery-cc-migration-artifacts` through commit `31f0d2d87`
- moved a substantial set of loose root docs into canonical repo-local `docs/` directories
- embedded the Master Doc maintenance rule directly into the canonical Master Doc
- wrote the workspace registry and relocation audit

## Remaining blockers

There are no longer any repo-level GitHub backup blockers for the active repos.
The remaining issues are normalization decisions at the workspace root, not missing remotes.

### 1. `Designing_Experiments` remote provisioned
Path:
- `/Users/davidusa/REPOS/Designing_Experiments`

Current state:
- real git repo
- local commit history exists
- current local snapshot commit: `8f29cb2`
- remote configured: `https://github.com/dkirsh/Designing_Experiments.git`
- pushed branch: `master`

Consequence:
- no repo-level backup blocker remains

Required next action:
- none for backup; only normal future maintenance

### 2. `Article_Finder_v3_2_3` remote provisioned
Path:
- `/Users/davidusa/REPOS/Article_Finder_v3_2_3`

Current state:
- restored as a standalone local git repo after the root repo archive
- current local source snapshot commit: `f57d2b6`
- remote configured: `https://github.com/dkirsh/Article_Finder_v3_2_3.git`
- pushed branch: `main`

Consequence:
- no repo-level backup blocker remains

Required next action:
- none for backup; later work is data/storage policy rather than repo creation

### 3. `theory_guides` remote provisioned
Path:
- `/Users/davidusa/REPOS/theory_guides`

Current state:
- active content corpus
- initialized as git repo
- current local snapshot commit: `22ff7be`
- remote configured: `https://github.com/dkirsh/theory_guides.git`
- pushed branch: `main`

Consequence:
- no repo-level backup blocker remains

Required next action:
- only future integration decisions; backup is already covered

### 4. Workspace-root normalization is complete

Intentional root files:
- `/Users/davidusa/REPOS/CLAUDE.md`
- `/Users/davidusa/REPOS/MASTER_DOC_CMR_2026-02-25.md`
- `/Users/davidusa/REPOS/TOPIC_PROGRESS.md`

Supporting root subdirectories:
- `/Users/davidusa/REPOS/Workspace_Docs`
- `/Users/davidusa/REPOS/Workspace_Data`
- `/Users/davidusa/REPOS/Workspace_Media`
- `/Users/davidusa/REPOS/Workspace_Scripts`
- `/Users/davidusa/REPOS/Backups/root_file_archive_2026-03-24`

Consequence:
- no root-normalization blocker remains

Required next action:
- none; maintain the three-file root policy going forward

## Source-of-truth status after this pass

### Canonical and remotely backed up
- `Knowledge_Atlas`
- `Article_Eater_PostQuinean_v1_recovery`

### Canonical and now remotely backed up
- `Designing_Experiments`
- `Article_Finder_v3_2_3`
- `theory_guides`

## Bottom line

The active repos are now all backed up remotely.
The workspace root is normalized.
What remains is ordinary maintenance, not cleanup or repo-provisioning.
