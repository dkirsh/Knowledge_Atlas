# Paper-Quality Migration Dry Run

Date: 2026-05-13

Scope: Codex repair for paper-quality build Commit 6.5 and Commit 7.

Artifacts:

- `contracts/schemas/paper_quality.sql`
- `scripts/migrations/2026_04_23_paper_quality.sql`
- `scripts/paper_quality_blackboard_init.py`
- `tests/test_paper_quality_blackboard_schema.py`

Dry-run method:

1. Apply `contracts/schemas/paper_quality.sql` to an empty temporary SQLite database.
2. Re-apply the same schema to prove idempotence.
3. Run `scripts/paper_quality_blackboard_init.py` against a synthetic 56-paper corpus with batch size 28.
4. Re-run the initializer against the same database to prove `INSERT OR IGNORE` idempotence.
5. Verify row counts: 168 jobs, 6 batches, 56 progress-view rows.

Result: see `pytest -q tests/test_paper_quality_blackboard_schema.py`.
