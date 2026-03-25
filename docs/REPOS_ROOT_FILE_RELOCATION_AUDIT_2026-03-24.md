# REPOS Root File Relocation Audit

Date: 2026-03-24
Scope:
- loose top-level files in `/Users/davidusa/REPOS`

## Governing rule

Do not move root-level files blindly.
Use this sequence:
1. identify likely owner repo
2. identify whether the file is canonical, duplicate, or archival
3. update references where needed
4. then move or archive

## High-priority root files

## Relocations already completed

Moved into `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1_recovery/docs/`:
- `ATLAS_COURSE_DESIGN_REVISED_2026-03-17.md`
- `ATLAS_COURSE_SCAFFOLDING_TASKS_2026-03-17.md`
- `ATLAS_THEORETICAL_FOUNDATIONS_EXPANDED_2026-03-17.md`
- `CONVERGENT_PIPELINE_PLAN.md`
- `CONSOLIDATED_ACTION_LIST_2026-02-28.md`
- `EXPERT_PANEL_MECHANISM_VS_EVIDENCE_2026-03-01.md`
- `Haack_Evidence_Inquiry_Extraction.md`
- `OVERSEER_EXECUTIVE_SUMMARY_2026-02-25.md`
- `SPRINT_PLAN_SUMMARY_2026-02-25.md`
- `SESSION_TRANSFER_DOC_2026-03-20.md`
- `PORTS_COORDINATION_CHECKLIST.md`
- `PORTS_REGISTRY.md`
- `CODEX_PROMPT_COURSE_SCAFFOLDING_2026-03-17.md`
- `PAPER_1_ATLAS_ARCHITECTURE_COMPLETE_DRAFT_2026-02-28.md`
- `DAVID_REVIEW_SET_20.md`

Moved into `/Users/davidusa/REPOS/Designing_Experiments/docs/`:
- `EXPERIMENT_WIZARD_INDEX.txt`
- `WIZARD_SUMMARY.txt`
- `QUICK_START.md`

Moved into `/Users/davidusa/REPOS/Knowledge_Atlas/docs/`:
- `GOOD_IDEAS.md`

Archived out of `/Users/davidusa/REPOS/` root into `/Users/davidusa/REPOS/Backups/root_file_archive_2026-03-24/`:
- `EXPERIMENT_WIZARD_README.md`
- `ENGINEERING_PANEL_AND_SPRINT_PLAN_2026-03-10.md`
- `LAYER_REVISION_PANEL_DELIBERATION_2026-03-10.md`

### 1. `MASTER_DOC_CMR_2026-02-25.md`

Current root path:
- `/Users/davidusa/REPOS/MASTER_DOC_CMR_2026-02-25.md`

Canonical git-backed location:
- `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1_recovery/docs/MASTER_DOC_CMR_2026-02-25.md`

Disposition:
- treat root copy as non-canonical duplicate
- do not keep two authoritative versions
- completed: root file reduced to a pointer stub; former full duplicate archived under `/Users/davidusa/REPOS/Backups/root_file_archive_2026-03-24/`

### 2. `ATLAS_COURSE_DESIGN_REVISED_2026-03-17.md`
### 3. `ATLAS_COURSE_SCAFFOLDING_TASKS_2026-03-17.md`

Likely owner repo:
- `Article_Eater_PostQuinean_v1_recovery/docs`

Reason:
- these are course design / scaffolding materials tightly coupled to the recovery-side class infrastructure and handoff docs

Disposition:
- completed: moved into `Article_Eater_PostQuinean_v1_recovery/docs/`

### 4. `ATLAS_THEORETICAL_FOUNDATIONS_EXPANDED_2026-03-17.md`
### 5. `EXPERT_PANEL_MECHANISM_VS_EVIDENCE_2026-03-01.md`
### 6. `Haack_Evidence_Inquiry_Extraction.md`
### 7. `NEURAL_EXPLANATIONS_ENVIRO_PSYCH_PAPER_2026-02-23.md`

Likely owner repo:
- `Article_Eater_PostQuinean_v1_recovery/docs`

Reason:
- these are theory / epistemic / extraction architecture materials

Disposition:
- completed:
  - moved: `ATLAS_THEORETICAL_FOUNDATIONS_EXPANDED_2026-03-17.md`
  - moved: `EXPERT_PANEL_MECHANISM_VS_EVIDENCE_2026-03-01.md`
  - moved: `Haack_Evidence_Inquiry_Extraction.md`
  - moved: `NEURAL_EXPLANATIONS_ENVIRO_PSYCH_PAPER_2026-02-23.md`

### 8. `CONVERGENT_PIPELINE_PLAN.md`
### 9. `CONSOLIDATED_ACTION_LIST_2026-02-28.md`
### 10. `ENGINEERING_PANEL_AND_SPRINT_PLAN_2026-03-10.md`
### 11. `SPRINT_PLAN_SUMMARY_2026-02-25.md`
### 12. `OVERSEER_EXECUTIVE_SUMMARY_2026-02-25.md`

Likely owner repo:
- `Article_Eater_PostQuinean_v1_recovery/docs`

Reason:
- these are pipeline / architecture / execution planning files

Disposition:
- partially completed:
  - moved: `CONVERGENT_PIPELINE_PLAN.md`
  - moved: `CONSOLIDATED_ACTION_LIST_2026-02-28.md`
  - moved: `OVERSEER_EXECUTIVE_SUMMARY_2026-02-25.md`
  - moved: `SPRINT_PLAN_SUMMARY_2026-02-25.md`
  - moved: `PAPER_1_ATLAS_ARCHITECTURE_COMPLETE_DRAFT_2026-02-28.md`
  - duplicate root copies of `ENGINEERING_PANEL_AND_SPRINT_PLAN_2026-03-10.md` and `LAYER_REVISION_PANEL_DELIBERATION_2026-03-10.md` have been archived out of the workspace root

### 13. `PORTS_REGISTRY.md`
### 14. `PORTS_COORDINATION_CHECKLIST.md`

Likely owner repo:
- undecided but should not remain loose at root

Best current target:
- `Article_Eater_PostQuinean_v1_recovery/docs` if they remain active system operations docs

Disposition:
- completed: moved into `Article_Eater_PostQuinean_v1_recovery/docs/`

### 15. `SESSION_TRANSFER_DOC_2026-03-20.md`

Likely owner repo:
- `Article_Eater_PostQuinean_v1_recovery/docs`

Reason:
- active coordination / handoff artifact tied to the recovery workspace

Disposition:
- completed: moved into `Article_Eater_PostQuinean_v1_recovery/docs/`

## Current final root-file policy

After the normalization pass, the only intentional files remaining directly at `/Users/davidusa/REPOS` root are:
- `CLAUDE.md`
- `MASTER_DOC_CMR_2026-02-25.md` (pointer stub only)
- `TOPIC_PROGRESS.md`

Loose non-repo workspace material has been grouped into:
- `Workspace_Docs/`
- `Workspace_Data/`
- `Workspace_Media/`
- `Workspace_Scripts/`
- `Backups/root_file_archive_2026-03-24/`

## Ongoing no-regret policy

1. do not create new loose docs at `/Users/davidusa/REPOS`
2. use repo-local `docs/` directories unless the file is a deliberate workspace-level exception
3. treat the AE recovery Master Doc path as canonical
