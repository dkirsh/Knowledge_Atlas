# T2 Task 1 — Grade Report

**Student:** Kaden Leung
**Email:** kadenleung00@gmail.com
**Grader:** auto
**Date:** 2026-05-18 22:40 UTC

---

## Total: 15 / 100

## Rubric Scores

| Criterion | Score | Comment |
|-----------|-------|---------|
| Diagnosis: Boxology diagrams accurate, gap statement correct | 0/15 | (auto-only mode — not scored) |
| Spec quality: Contract is complete, specific, and testable | 0/15 | (auto-only mode — not scored) |
| Verification questions: Probing questions caught real problems | 0/15 | (auto-only mode — not scored) |
| Validation: At least 3/4 test papers produce correct results | 0/20 | (auto-only mode — not scored) |
| Diagnosis of failures: Correctly identified spec vs implementation bugs | 0/15 | (auto-only mode — not scored) |
| File manifest: Complete and matches actual changes | 0/5 | (auto-only mode — not scored) |
| Automated tests: Instructor-side tests pass (auto-scored) | 15/15 | Auto: 8/8 tests passed |

## Automated Test Results

| Test | Status | Weight | Details |
|------|--------|--------|---------|
| Classifier integration (round-trip) | ✅ | critical | Classifier is imported and .classify() is called |
| Duplicate detection logic | ✅ | important | Duplicate detection logic found in endpoint code |
| Contribute page modified | ✅ | critical | Contribute page has results section and API call |
| Corrupt PDF handling | ✅ | critical | PDF validation function found in endpoint code |
| DB field completeness | ✅ | important | All articles have status and created_at populated |
| Audit log presence | ✅ | minor | All articles have audit log entries |
| Storage path correctness | ✅ | critical | Storage paths are consistent with paper status |
| Accepted vs edge case distinguishability | ✅ | important | Found 2 distinct statuses: {'needs_review', 'staged_pending_review'} |
