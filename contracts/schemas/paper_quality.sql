-- ============================================================================
-- Paper-quality fingerprint schema
-- Date: 2026-04-23
-- Target: Knowledge Atlas lifecycle database, SQLite 3.x
--
-- Source authorities:
--   docs/PAPER_QUALITY_SYSTEM_DESIGN_2026-04-23.md
--   docs/PAPER_QUALITY_BLACKBOARD_DESIGN_2026-04-25.md
--   docs/PAPER_QUALITY_BUILD_PROMPT_FOR_CODEX_2026-04-23.md
--
-- Safety:
--   * Additive only.
--   * Idempotent: every table, index, trigger, and view uses IF NOT EXISTS or
--     DROP VIEW IF EXISTS before recreation.
--   * No existing table is altered or dropped.
-- ============================================================================

PRAGMA foreign_keys = ON;

-- 1. Per-paper fingerprint, one row per paper after auto-accept or adjudication.
CREATE TABLE IF NOT EXISTS paper_quality_fingerprints (
  paper_id                         TEXT PRIMARY KEY,
  extracted_at                     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  extractor_version                TEXT NOT NULL,
  human_adjudicated                INTEGER NOT NULL DEFAULT 0 CHECK (human_adjudicated IN (0, 1)),
  adjudicator_id                   TEXT,
  adjudicated_at                   TEXT,

  -- Sample cluster.
  n_total                          INTEGER,
  n_total_confidence               REAL CHECK (n_total_confidence IS NULL OR n_total_confidence BETWEEN 0 AND 1),
  sample_country                   TEXT, -- JSON array of ISO-3166 country codes.
  sample_setting                   TEXT CHECK (
    sample_setting IS NULL OR sample_setting IN (
      'research_university', 'community', 'online_panel', 'industrial',
      'clinical', 'mixed', 'other'
    )
  ),
  sample_weird                     INTEGER CHECK (sample_weird IS NULL OR sample_weird IN (0, 1)),
  age_distribution_json            TEXT,

  -- Design cluster.
  design_type                      TEXT CHECK (
    design_type IS NULL OR design_type IN (
      'lab_experiment', 'field_experiment', 'observational_cohort',
      'online', 'secondary_analysis', 'meta_analysis', 'theoretical'
    )
  ),
  preregistered                    INTEGER CHECK (preregistered IS NULL OR preregistered IN (0, 1)),
  preregistration_url              TEXT,
  preregistration_verified         INTEGER CHECK (
    preregistration_verified IS NULL OR preregistration_verified IN (0, 1)
  ),
  preregistration_verified_at      TEXT,
  replication_count                INTEGER CHECK (replication_count IS NULL OR replication_count >= 0),

  -- Statistical cluster.
  primary_effect_size              REAL,
  primary_ci_lower                 REAL,
  primary_ci_upper                 REAL,
  primary_metric                   TEXT CHECK (
    primary_metric IS NULL OR primary_metric IN ('d', 'r', 'or', 'hr', 'bayes_factor')
  ),
  statistical_power                REAL CHECK (statistical_power IS NULL OR statistical_power BETWEEN 0 AND 1),
  power_origin                     TEXT CHECK (
    power_origin IS NULL OR power_origin IN (
      'a_priori_reported', 'retrospective_computed', 'not_reported'
    )
  ),

  -- Measurement and openness cluster.
  primary_measure                  TEXT,
  primary_measure_psychometric_ref TEXT,
  open_data_url                    TEXT,
  open_data_verified               INTEGER CHECK (open_data_verified IS NULL OR open_data_verified IN (0, 1)),

  -- Human-review-only sidecars.
  construct_validity_flag          TEXT CHECK (
    construct_validity_flag IS NULL OR construct_validity_flag IN (
      'good', 'questionable', 'mixed', 'not_assessed'
    )
  ),
  construct_validity_notes         TEXT,
  conflict_of_interest_severity    TEXT CHECK (
    conflict_of_interest_severity IS NULL OR conflict_of_interest_severity IN (
      'none', 'minor', 'moderate', 'severe', 'unknown'
    )
  ),
  rhetorical_flags_json            TEXT NOT NULL DEFAULT '[]',
  field_norms_version              TEXT,

  -- Aggregate.
  overall_confidence               REAL CHECK (overall_confidence IS NULL OR overall_confidence BETWEEN 0 AND 1),
  notes_markdown                   TEXT,
  created_at                       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at                       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS paper_quality_fingerprints_extracted_idx
  ON paper_quality_fingerprints (extracted_at);
CREATE INDEX IF NOT EXISTS paper_quality_fingerprints_review_idx
  ON paper_quality_fingerprints (human_adjudicated, overall_confidence);
CREATE INDEX IF NOT EXISTS paper_quality_fingerprints_design_idx
  ON paper_quality_fingerprints (design_type);

CREATE TRIGGER IF NOT EXISTS paper_quality_fingerprints_touch_updated_at
AFTER UPDATE ON paper_quality_fingerprints
FOR EACH ROW
BEGIN
  UPDATE paper_quality_fingerprints
     SET updated_at = CURRENT_TIMESTAMP
   WHERE paper_id = OLD.paper_id;
END;

-- 2. Staging table for low-confidence, violating, or not-yet-adjudicated records.
CREATE TABLE IF NOT EXISTS fingerprint_staging (
  staging_id          INTEGER PRIMARY KEY AUTOINCREMENT,
  paper_id            TEXT NOT NULL,
  created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  extractor_version   TEXT NOT NULL,
  fingerprint_json    TEXT NOT NULL,
  routing_decision    TEXT NOT NULL CHECK (
    routing_decision IN ('auto_accept', 'adjudication_queue', 'reject', 'held_for_review')
  ),
  status              TEXT NOT NULL DEFAULT 'pending' CHECK (
    status IN ('pending', 'queued', 'held_for_review', 'adjudicated', 'rejected')
  ),
  rejection_reason    TEXT,
  source_excerpt      TEXT,
  confidence_summary  TEXT
);

CREATE INDEX IF NOT EXISTS fingerprint_staging_paper_idx
  ON fingerprint_staging (paper_id);
CREATE INDEX IF NOT EXISTS fingerprint_staging_status_idx
  ON fingerprint_staging (status, created_at);

CREATE TRIGGER IF NOT EXISTS fingerprint_staging_touch_updated_at
AFTER UPDATE ON fingerprint_staging
FOR EACH ROW
BEGIN
  UPDATE fingerprint_staging
     SET updated_at = CURRENT_TIMESTAMP
   WHERE staging_id = OLD.staging_id;
END;

-- 3. Sample-overlap graph for claim-level N aggregation.
CREATE TABLE IF NOT EXISTS sample_overlap_edges (
  paper_id_a    TEXT NOT NULL,
  paper_id_b    TEXT NOT NULL,
  overlap_kind  TEXT NOT NULL CHECK (
    overlap_kind IN ('shared_dataset', 'shared_authors', 'shared_subjects', 'meta_of_meta')
  ),
  confidence    REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  detected_by   TEXT NOT NULL CHECK (detected_by IN ('author_id', 'dataset_doi', 'manual', 'llm')),
  created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (paper_id_a, paper_id_b, overlap_kind)
);

CREATE INDEX IF NOT EXISTS sample_overlap_edges_b_idx
  ON sample_overlap_edges (paper_id_b);

-- 4. Immutable extraction-event audit trail.
CREATE TABLE IF NOT EXISTS fingerprint_extraction_events (
  event_id              INTEGER PRIMARY KEY AUTOINCREMENT,
  paper_id              TEXT NOT NULL,
  extracted_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  extractor_version     TEXT NOT NULL,
  extractor_family      TEXT CHECK (
    extractor_family IS NULL OR extractor_family IN ('claude', 'codex', 'gemini', 'human', 'other')
  ),
  subscription_session_id TEXT,
  conversation_id       TEXT,
  prompt_hash           TEXT,
  fingerprint_json      TEXT NOT NULL,
  routing_decision      TEXT NOT NULL CHECK (
    routing_decision IN ('auto_accept', 'adjudication_queue', 'reject', 'held_for_review')
  ),
  rejection_reason      TEXT
);

CREATE INDEX IF NOT EXISTS fingerprint_events_paper_idx
  ON fingerprint_extraction_events (paper_id, extracted_at);

-- 5. Admin adjudication queue.
CREATE TABLE IF NOT EXISTS quality_adjudication_queue (
  queue_id             INTEGER PRIMARY KEY AUTOINCREMENT,
  paper_id             TEXT NOT NULL,
  staging_id           INTEGER REFERENCES fingerprint_staging(staging_id),
  event_id             INTEGER REFERENCES fingerprint_extraction_events(event_id),
  field_name           TEXT,
  suggested_value_json TEXT,
  source_excerpt       TEXT,
  confidence_score     REAL CHECK (confidence_score IS NULL OR confidence_score BETWEEN 0 AND 1),
  queue_reason         TEXT NOT NULL,
  status               TEXT NOT NULL DEFAULT 'open' CHECK (
    status IN ('open', 'in_review', 'resolved', 'rejected')
  ),
  assigned_to          TEXT,
  adjudicated_value_json TEXT,
  adjudicator_id       TEXT,
  adjudicator_notes    TEXT,
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  resolved_at          TEXT
);

CREATE INDEX IF NOT EXISTS quality_adjudication_queue_status_idx
  ON quality_adjudication_queue (status, created_at);
CREATE INDEX IF NOT EXISTS quality_adjudication_queue_paper_idx
  ON quality_adjudication_queue (paper_id);

-- 6. Calibration history, append-only.
CREATE TABLE IF NOT EXISTS quality_calibration_history (
  calibration_id        INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id                TEXT NOT NULL,
  field_name            TEXT NOT NULL,
  model_family          TEXT NOT NULL CHECK (model_family IN ('claude', 'codex', 'gemini', 'human', 'other')),
  fixture_count         INTEGER NOT NULL CHECK (fixture_count >= 0),
  precision             REAL CHECK (precision IS NULL OR precision BETWEEN 0 AND 1),
  recall                REAL CHECK (recall IS NULL OR recall BETWEEN 0 AND 1),
  f1_score              REAL CHECK (f1_score IS NULL OR f1_score BETWEEN 0 AND 1),
  self_consistency_variance REAL CHECK (
    self_consistency_variance IS NULL OR self_consistency_variance >= 0
  ),
  conversation_count    INTEGER NOT NULL DEFAULT 0 CHECK (conversation_count >= 0),
  mean_tokens_per_call  REAL,
  wall_clock_seconds    REAL,
  report_path           TEXT,
  created_at            TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS quality_calibration_history_run_idx
  ON quality_calibration_history (run_id, field_name);

-- 7. Hard-rule violations are per-paper blockers, not build blockers.
CREATE TABLE IF NOT EXISTS hard_rule_violations (
  violation_id          INTEGER PRIMARY KEY AUTOINCREMENT,
  paper_id              TEXT NOT NULL,
  rule_id               TEXT NOT NULL CHECK (
    rule_id IN ('HARD_RULE_7', 'HARD_RULE_8', 'HARD_RULE_9')
  ),
  field_name            TEXT,
  violation_state       TEXT NOT NULL, -- JSON: prompt hash, conversations, responses, assertion.
  violation_timestamp   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  requires_dk_review    INTEGER NOT NULL DEFAULT 1 CHECK (requires_dk_review IN (0, 1)),
  staging_id            INTEGER REFERENCES fingerprint_staging(staging_id),
  resolved_at           TEXT,
  resolution_notes      TEXT
);

CREATE INDEX IF NOT EXISTS hard_rule_violations_review_idx
  ON hard_rule_violations (requires_dk_review, violation_timestamp);

-- 8. Interpretation-layer stub. No logic populates this in the paper-quality build.
CREATE TABLE IF NOT EXISTS paper_interpretation (
  paper_id                       TEXT PRIMARY KEY,
  interpretation_cue             TEXT,
  interpretation_layer_version   TEXT,
  fingerprint_id                 TEXT REFERENCES paper_quality_fingerprints(paper_id),
  created_at                     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at                     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS paper_interpretation_touch_updated_at
AFTER UPDATE ON paper_interpretation
FOR EACH ROW
BEGIN
  UPDATE paper_interpretation
     SET updated_at = CURRENT_TIMESTAMP
   WHERE paper_id = OLD.paper_id;
END;

-- 9. Blackboard batches: the unit of claiming.
CREATE TABLE IF NOT EXISTS paper_quality_batches (
  batch_id             TEXT PRIMARY KEY,
  pass_type            TEXT NOT NULL CHECK (
    pass_type IN ('extract_codex', 'extract_claude', 'verify_gemini')
  ),
  paper_ids            TEXT NOT NULL, -- JSON list of paper IDs.
  batch_size           INTEGER NOT NULL CHECK (batch_size BETWEEN 1 AND 30),
  status               TEXT NOT NULL DEFAULT 'pending' CHECK (
    status IN ('pending', 'in_progress', 'done', 'timeout_warning', 'reclaimable', 'failed')
  ),
  current_assignee     TEXT,
  claimed_at           TEXT,
  last_progress_at     TEXT,
  completed_at         TEXT,
  papers_done          INTEGER NOT NULL DEFAULT 0 CHECK (papers_done >= 0),
  papers_failed        INTEGER NOT NULL DEFAULT 0 CHECK (papers_failed >= 0),
  notification_events  TEXT NOT NULL DEFAULT '[]',
  reclamation_count    INTEGER NOT NULL DEFAULT 0 CHECK (reclamation_count >= 0)
);

CREATE INDEX IF NOT EXISTS paper_quality_batches_pending_idx
  ON paper_quality_batches (pass_type, status)
  WHERE status IN ('pending', 'reclaimable');

-- 10. Blackboard jobs: one row per (paper_id, pass_type).
CREATE TABLE IF NOT EXISTS paper_quality_jobs (
  job_id          TEXT PRIMARY KEY,
  paper_id        TEXT NOT NULL,
  pass_type       TEXT NOT NULL CHECK (
    pass_type IN ('extract_codex', 'extract_claude', 'verify_gemini')
  ),
  batch_id        TEXT REFERENCES paper_quality_batches(batch_id),
  status          TEXT NOT NULL DEFAULT 'pending' CHECK (
    status IN ('pending', 'in_progress', 'done', 'failed')
  ),
  claimed_at      TEXT,
  completed_at    TEXT,
  artifact_path   TEXT,
  attempt_count   INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
  UNIQUE (paper_id, pass_type)
);

CREATE INDEX IF NOT EXISTS paper_quality_jobs_paper_idx
  ON paper_quality_jobs (paper_id);
CREATE INDEX IF NOT EXISTS paper_quality_jobs_status_idx
  ON paper_quality_jobs (pass_type, status);

-- 11. Holding pen for DK review after ballistic extraction continues.
DROP VIEW IF EXISTS holding_pen;
CREATE VIEW holding_pen AS
SELECT
  h.violation_id AS item_id,
  h.paper_id,
  h.rule_id,
  h.field_name,
  h.violation_timestamp AS created_at,
  'hard_rule_violation' AS item_type,
  h.requires_dk_review,
  h.resolved_at,
  h.violation_state AS detail_json
FROM hard_rule_violations h
WHERE h.resolved_at IS NULL
UNION ALL
SELECT
  q.queue_id AS item_id,
  q.paper_id,
  NULL AS rule_id,
  q.field_name,
  q.created_at,
  'adjudication_queue' AS item_type,
  1 AS requires_dk_review,
  q.resolved_at,
  json_object(
    'queue_reason', q.queue_reason,
    'confidence_score', q.confidence_score,
    'suggested_value_json', q.suggested_value_json
  ) AS detail_json
FROM quality_adjudication_queue q
WHERE q.status IN ('open', 'in_review');

-- 12. Per-paper completion state across pass types.
DROP VIEW IF EXISTS paper_quality_progress;
CREATE VIEW paper_quality_progress AS
SELECT
  paper_id,
  MAX(CASE WHEN pass_type = 'extract_codex' AND status = 'done'
           THEN completed_at END) AS codex_done_at,
  MAX(CASE WHEN pass_type = 'extract_claude' AND status = 'done'
           THEN completed_at END) AS claude_done_at,
  MAX(CASE WHEN pass_type = 'verify_gemini' AND status = 'done'
           THEN completed_at END) AS gemini_done_at,
  MAX(CASE WHEN status = 'in_progress' THEN
           pass_type || ':' || COALESCE((
             SELECT current_assignee
               FROM paper_quality_batches b
              WHERE b.batch_id = paper_quality_jobs.batch_id), '?')
           END) AS active_workers,
  COUNT(*) AS pass_count,
  SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) AS pass_done_count
FROM paper_quality_jobs
GROUP BY paper_id;

-- 13. Claim-level view. It is intentionally conservative until the later
-- claim/warrant integration commit wires real claim IDs into the store.
DROP VIEW IF EXISTS claim_strengths_weaknesses;
CREATE VIEW claim_strengths_weaknesses AS
SELECT
  paper_id AS claim_id,
  1 AS n_supporting,
  0 AS n_defeating,
  COALESCE(n_total, 0) AS cumulative_n_unique,
  0 AS cumulative_n_overlap_flagged,
  NULL AS heterogeneity_i_squared,
  'n/a' AS heterogeneity_band,
  primary_effect_size AS weighted_effect_size,
  primary_metric AS weighted_effect_metric,
  NULL AS funnel_asymmetry_egger_p,
  CASE
    WHEN replication_count IS NULL THEN NULL
    WHEN replication_count > 0 THEN 1.0
    ELSE 0.0
  END AS replication_rate,
  1.0 AS lab_diversity_hhi,
  COALESCE(construct_validity_flag, 'not_assessed') AS construct_validity_dominant,
  CASE WHEN preregistered = 1 THEN 1.0 ELSE 0.0 END AS preregistration_share,
  'Single-paper paper-quality placeholder pending claim integration.' AS strengths_markdown,
  COALESCE(notes_markdown, '') AS weaknesses_markdown,
  CURRENT_TIMESTAMP AS generated_at,
  'paper_quality_schema_placeholder_v1' AS weighting_function_version
FROM paper_quality_fingerprints;

-- 14. Literature-body view. Topic linkage lands in a later commit; this gives
-- endpoint work a stable schema without inventing topic memberships.
DROP VIEW IF EXISTS literature_body_quality;
CREATE VIEW literature_body_quality AS
SELECT
  'all_papers' AS topic_id,
  COUNT(*) AS total_primary_paper_count,
  NULL AS five_year_growth_rate,
  AVG(CASE WHEN preregistered = 1 THEN 1.0 ELSE 0.0 END) AS preregistration_share,
  NULL AS replication_rate_estimate,
  NULL AS cross_citation_network_density,
  1.0 AS lab_diversity_hhi,
  CURRENT_TIMESTAMP AS generated_at
FROM paper_quality_fingerprints;
