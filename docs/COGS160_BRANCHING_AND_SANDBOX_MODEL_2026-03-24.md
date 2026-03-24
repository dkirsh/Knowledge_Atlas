# COGS160 Branching and Sandbox Model

Date: 2026-03-24
Repo: `/Users/davidusa/REPOS/Knowledge_Atlas`
Purpose: recommend the git and sandbox model for student coding with AI assistance

## Recommendation

CW's basic model is right.

Students should not work directly on `master`.
They should work on personal branches off a track-level staging branch.

## Recommended branch pattern

Use:
- `track/1-staging`
- `track/2-staging`
- `track/3-staging`
- `track/4-staging`

Then each student works from:
- `track/1-staging/<student-id>`
- `track/2-staging/<student-id>`
- `track/3-staging/<student-id>`
- `track/4-staging/<student-id>`

Example:
- `track/2-staging/jane-article-finder`

## Why this is the right model

It gives:
1. protected `master`
2. track-level review and integration
3. personal isolation for AI-assisted experiments
4. a realistic professional workflow

## Sandbox principle

Students should have:
- personal git branches
- student-safe DB copies where relevant
- explicit acceptance criteria

They should not have:
- direct write authority to production-like operational DBs
- unreviewed merges to `master`

## Repo reality

This model is best for repos where students are actually writing code.

For `Knowledge_Atlas`, that means:
- HTML / JS / UI work can follow the branch model directly

For `Article_Eater_PostQuinean_v1_recovery`, the stronger rule should be:
- very limited student write scope
- student-safe snapshots
- reviewed ingestion of accepted outputs

## Immediate next move

1. create the four `track/*-staging` branches in `Knowledge_Atlas`
2. document the checkout workflow on the new student setup page
3. define which repos each track is actually allowed to edit
