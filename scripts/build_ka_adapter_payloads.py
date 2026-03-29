#!/usr/bin/env python3
import json
import re
import sqlite3
import shutil
import sys
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime, timezone

CURRENT_YEAR = datetime.now().year
TITLE_REJECT_PATTERNS = [
    r'^contents lists available at', r'^science of the total environment\b', r'^landscape and urban planning\b',
    r'^frontiers in psychology\b', r'^ann\. n\.y\. acad\. sci\.', r'^march \d{4} \| volume',
    r'^article type:', r'^doi:', r'rights reserved', r'elsevier b\.v\.', r'copyediting, typesetting, pagination',
]
ABSTRACT_TRIM_MARKERS = [' Published by', ' 1. Introduction', '1. Introduction', ' Introduction ', ' * Corresponding author', ' Contents lists available at ScienceDirect ', ' Contents lists available at']


ROOT = Path('/Users/davidusa/REPOS')
AE = ROOT / 'Article_Eater_PostQuinean_v1_recovery'
OUT = ROOT / 'Knowledge_Atlas' / 'data' / 'ka_payloads'
OUT.mkdir(parents=True, exist_ok=True)
VISUALS_OUT = OUT / 'article_visuals'
VISUALS_OUT.mkdir(parents=True, exist_ok=True)
WORKFLOW_DB_PATH = ROOT / 'Knowledge_Atlas' / 'data' / 'ka_workflow.db'
REBUILD_DB_PATH = AE / 'data' / 'rebuild' / 'web_persistence_v5.db'

if str(AE) not in sys.path:
    sys.path.insert(0, str(AE))

FRONTS_PATH = AE / 'data' / 'rebuild' / 'research_fronts_v5.json'
CLAIMS_PATH = AE / 'data' / 'rebuild' / 'gold_claims_v7.jsonl'
REPAIRS_PATH = AE / 'data' / 'rebuild' / 'bibliographic_repairs.json'
AG_PDF_PACKAGE_REPAIRS_PATH = AE / 'data' / 'rebuild' / 'ag_pdf_package_repairs.json'
DEEP_STATS_DIR = AE / 'data' / 'verification_runs' / 'v6_deep_stats_adjudication'
ABSTRACT_ADJUDICATION_DIR = AE / 'data' / 'verification_runs' / 'v6_abstract_adjudication'
MAIN_CONCLUSION_DIR = AE / 'data' / 'verification_runs' / 'v6_main_conclusion_adjudication'
POPULATION_ADJUDICATION_DIR = AE / 'data' / 'verification_runs' / 'v6_population_count_adjudication'
RESULT_RELATION_DIR = AE / 'data' / 'verification_runs' / 'v6_result_relation_adjudication'
PAGE_IMAGE_SCAN_DIR = AE / 'data' / 'verification_runs' / 'page_image_first_section_scan'
STIMULUS_IMAGE_DIR = AE / 'data' / 'gold_standard' / 'stimulus_images'
FIELD_COVERAGE_BY_TYPE_PATH = AE / 'data' / 'verification_runs' / 'field_coverage_by_article_type' / 'field_coverage_by_article_type.json'
ARG_GRAPH_PATH = AE / 'data' / 'rebuild' / 'argumentation_graph_v5.json'
CLAIM_ARG_GRAPH_PATH = AE / 'data' / 'rebuild' / 'claim_argument_graph_v1.json'
ANNOTATIONS_PATH = AE / 'data' / 'rebuild' / 'annotations_regenerated.json'
INTERPRETATION_SUMMARY_PATH = AE / 'data' / 'interpretation_space' / 'phase4' / 'phase4_summary.json'
FRONTIER_QUESTIONS_PATH = AE / 'data' / 'interpretation_space' / 'phase4' / 'prioritized_frontier_questions.json'
VALIDATION_COMPLETENESS_PATH = AE / 'data' / 'interpretation_space' / 'phase4' / 'validation_completeness.json'
BOUNDARY_MAP_PATH = AE / 'data' / 'interpretation_space' / 'phase4' / 'boundary_map.json'
DEFAULT_TRACK_TARGETS = [
    ('Track 1 — Image Tagging', 5),
    ('Track 2 — Article Finding', 5),
    ('Track 3 — VR Production', 3),
    ('Track 4 — GUI Evaluation & Experiment Design', 3),
]

try:
    from src.services.article_type_policy import likely_warrant_types, primary_warrant_type
except Exception:
    def likely_warrant_types(article_type):
        return ["EMPIRICAL_ASSOCIATION"]

    def primary_warrant_type(article_type):
        return "EMPIRICAL_ASSOCIATION"

try:
    from src.services.bridge_warrants import CANONICAL_DISCOUNT_FACTORS

    BRIDGE_DISCOUNT_BY_VALUE = {
        bridge_type.value: discount
        for bridge_type, discount in CANONICAL_DISCOUNT_FACTORS.items()
    }
except Exception:
    BRIDGE_DISCOUNT_BY_VALUE = {
        "constitutive": 1.00,
        "mechanism": 0.80,
        "empirical_association": 0.80,
        "functional": 0.65,
        "capacity": 0.55,
        "analogical": 0.40,
        "theory_derived": 0.25,
    }

CANONICAL_BRIDGE_ORDER = [
    "constitutive",
    "mechanism",
    "empirical_association",
    "functional",
    "capacity",
    "analogical",
    "theory_derived",
]

RAW_EXTRACTION_TO_CANONICAL = {
    "pathway_or_interaction_text_to_mechanism_field": "mechanism",
    "manipulation_or_reliability_text_to_validation_field": "capacity",
    "theme_or_descriptor_text_to_qualitative_field": "capacity",
}

CONSTITUTIVE_MARKERS = (
    "constitutive",
    "component of",
    "part of",
    "consists of",
    "is a marker of",
    "marker of",
    "index of",
    "indexes",
    "indexed by",
    "signature of",
    "reliable indicator of",
)

CAPACITY_MARKERS = (
    "capacity to",
    "capable of",
    "ability to",
    "can support",
    "can produce",
    "has the capacity",
)

ANALOGICAL_MARKERS = (
    "analog",
    "analogy",
    "analogical",
    "resembles",
    "similar to",
    "like a",
)

THEORY_MARKERS = (
    "theory",
    "framework",
    "hypothesis",
    "predicts",
    "prediction",
    "suggests that",
    "argues that",
)

INSTRUMENT_PATTERNS = {
    'EEG': [' eeg ', 'electroencephal', 'alpha asymmetry', 'frontal theta', 'erp '],
    'EDA': [' eda ', 'electrodermal', 'skin conductance', 'scr ', 'scl '],
    'HRV': [' hrv ', 'heart rate variability', 'rmssd', 'heart rate'],
    'Cortisol': ['cortisol', 'salivary cortisol'],
    'Pupil': ['pupil', 'pupill'],
    'PVT': [' pvt ', 'psychomotor vigilance'],
    'NASA-TLX': ['nasa tlx', 'task load index', 'tlx '],
    'fNIRS': ['fnirs', 'functional near infrared'],
    'EMG': [' emg ', 'electromyography', 'corrugator'],
    'Self-report': ['self report', 'questionnaire', 'survey', 'rating scale', 'stai', 'panas'],
}


def slugify(text: str) -> str:
    return ''.join(ch.lower() if ch.isalnum() else '_' for ch in text).strip('_')[:80]


def humanize(text):
    if text in (None, ''):
        return ''
    if isinstance(text, (int, float)):
        return str(text)
    return str(text).replace('theory_', '').replace('_', ' ').replace('.', ' ').strip().title()


def canonical_warrant_display(value):
    token = str(value or '').strip().lower()
    if not token:
        return 'Unknown'
    label = humanize(token)
    return label.replace('Theory Derived', 'Theory-Derived')


def _primary_bridge_type(article_type):
    value = str(primary_warrant_type(article_type) or 'EMPIRICAL_ASSOCIATION').strip().lower()
    if value in BRIDGE_DISCOUNT_BY_VALUE:
        return value
    return 'empirical_association'


def derive_canonical_bridge_type(obj):
    evidence_profile = obj.get('evidence_profile') or {}
    raw_warrant = str(evidence_profile.get('warrant_type') or obj.get('warrant_type') or '').strip().lower()
    article_type = obj.get('article_type')
    claim_role = str(obj.get('claim_role') or '').strip().lower()
    statement_text = ' '.join(
        str(part or '')
        for part in [
            obj.get('statement'),
            obj.get('claim_text'),
            obj.get('quote'),
        ]
    ).lower()
    theory_text = ' '.join(
        str(part or '')
        for part in [
            obj.get('theory_name'),
            ' '.join(obj.get('theory_names') or []),
        ]
    ).lower()

    if any(marker in statement_text for marker in ANALOGICAL_MARKERS):
        return 'analogical'
    if raw_warrant in RAW_EXTRACTION_TO_CANONICAL:
        return RAW_EXTRACTION_TO_CANONICAL[raw_warrant]
    if raw_warrant == 'indicator_pattern_plus_author_interpretation_to_construct_field':
        if any(marker in statement_text for marker in CONSTITUTIVE_MARKERS):
            return 'constitutive'
        if any(marker in statement_text for marker in CAPACITY_MARKERS):
            return 'capacity'
        return 'functional'
    if raw_warrant == 'multi_result_integration_to_synthesis_field':
        if any(marker in statement_text for marker in THEORY_MARKERS):
            return 'theory_derived'
        if any(marker in statement_text for marker in CAPACITY_MARKERS):
            return 'capacity'
        likely = [str(value or '').strip().lower() for value in likely_warrant_types(article_type)]
        for candidate in ('mechanism', 'functional', 'theory_derived', 'empirical_association'):
            if candidate in likely:
                return candidate
        return 'functional'
    if raw_warrant in {
        'measured_result_to_indicator_field',
        'condition_or_group_contrast_to_comparative_field',
    }:
        if any(marker in statement_text for marker in CONSTITUTIVE_MARKERS):
            return 'constitutive'
        return 'empirical_association'
    if claim_role == 'mechanism_claim':
        return 'mechanism'
    if claim_role == 'validation_claim':
        return 'capacity'
    if claim_role == 'synthesis_claim':
        return 'functional'
    if claim_role == 'construct_inference_claim':
        return 'functional'
    if any(marker in f"{statement_text} {theory_text}" for marker in THEORY_MARKERS) and _primary_bridge_type(article_type) == 'theory_derived':
        return 'theory_derived'
    return _primary_bridge_type(article_type)


def compose_warrant_chain(canonical_type, raw_warrant_type, result, claim_role):
    parts = []
    discount = BRIDGE_DISCOUNT_BY_VALUE.get(canonical_type)
    if discount is not None:
        parts.append(f"{canonical_warrant_display(canonical_type)} bridge (d={discount:.2f})")
    else:
        parts.append(f"{canonical_warrant_display(canonical_type)} bridge")
    if raw_warrant_type:
        parts.append(f"extraction warrant: {raw_warrant_type}")
    if claim_role:
        parts.append(f"claim role: {humanize(claim_role)}")
    test_statistic = str((result or {}).get('test_statistic') or '').strip()
    if test_statistic:
        parts.append(f"statistic: {test_statistic}")
    return ' · '.join(parts)


def compact_text(text, limit=220):
    value = ' '.join(str(text or '').split())
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + '…'


def clean_doi(value):
    text = str(value or '').strip()
    if not text or text.endswith('.json'):
        return ''
    return text


def publishable_title(text):
    value = ' '.join(str(text or '').split()).strip()
    if not value:
        return ''
    low = value.lower()
    if any(re.search(pattern, low) for pattern in TITLE_REJECT_PATTERNS):
        return ''
    if value.startswith('•'):
        return ''
    if len(value.split()) < 3:
        return ''
    return value


def sanitize_year(value):
    try:
        year = int(value)
    except Exception:
        return None
    if year < 1900 or year > CURRENT_YEAR + 1:
        return None
    return year


def sanitize_abstract(text):
    value = ' '.join(str(text or '').split()).strip()
    if not value:
        return ''
    for marker in ABSTRACT_TRIM_MARKERS:
        idx = value.find(marker)
        if idx > 200:
            value = value[:idx].rstrip()
            break
    return value


def normalize_authors(value):
    if value in (None, ''):
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = ' '.join(str(value).split()).strip()
    if not text:
        return []
    for sep in (';', ' and ', ' & '):
        if sep in text:
            return [part.strip(' ,') for part in text.split(sep) if part.strip(' ,')]
    if text.count(',') == 1:
        left, right = text.split(',', 1)
        if left.strip() and right.strip():
            return [left.strip(), right.strip()]
    return [text]


def format_apa_citation(authors, year, title, doi):
    title_value = publishable_title(title) or compact_text(title or '', 180)
    if not title_value:
        return ''
    author_list = normalize_authors(authors)
    author_text = ', '.join(author_list) if author_list else ''
    year_value = sanitize_year(year)
    parts = []
    if author_text:
        parts.append(author_text)
    if year_value:
        parts.append(f'({year_value}).')
    if title_value:
        parts.append(title_value.rstrip('.') + '.')
    doi_value = clean_doi(doi)
    if doi_value:
        parts.append(f'https://doi.org/{doi_value}')
    return ' '.join(parts).strip()


def title_status(title):
    value = str(title or '').strip()
    if not value:
        return 'missing'
    if not publishable_title(value):
        return 'blocked'
    if value.endswith((',', ':')) or len(value.split()) < 5:
        return 'provisional'
    return 'good'


def abstract_status(text):
    value = sanitize_abstract(text)
    if not value:
        return 'missing'
    if len(value) < 350:
        return 'provisional'
    return 'good'


def normalize_abstract_state(value):
    state = str(value or '').strip().lower()
    if state == 'accepted':
        return 'good'
    if state in {'good', 'provisional', 'missing'}:
        return state
    return 'missing'


def doi_status(value):
    return 'good' if clean_doi(value) else 'missing'


def subject_count_status(value):
    return 'good' if value not in (None, '', 0) else 'missing'


def normalize_adjudication_state(value):
    state = str(value or '').strip().lower()
    if state in {'accepted', 'provisional', 'review_required', 'missing'}:
        return state
    return 'missing'


def load_bibliographic_repairs():
    repairs = {}
    for path in (REPAIRS_PATH, AG_PDF_PACKAGE_REPAIRS_PATH):
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text())
        except Exception:
            continue
        for paper_id, row in (payload.get('papers', {}) or {}).items():
            merged = dict(repairs.get(paper_id, {}))
            for key, value in row.items():
                if value not in (None, '', [], {}):
                    merged[key] = value
            repairs[paper_id] = merged
    return repairs


def load_deep_stat_adjudications():
    payload = {}
    if not DEEP_STATS_DIR.exists():
        return payload
    for path in DEEP_STATS_DIR.glob('PDF-*.deep_stats_adjudication.json'):
        try:
            obj = json.loads(path.read_text())
        except Exception:
            continue
        paper_id = obj.get('paper_id') or path.name.split('.')[0]
        payload[paper_id] = obj.get('decisions') or {}
    return payload


def load_abstract_adjudications():
    payload = {}
    if not ABSTRACT_ADJUDICATION_DIR.exists():
        return payload
    for path in ABSTRACT_ADJUDICATION_DIR.glob('PDF-*.abstract_adjudication.json'):
        try:
            obj = json.loads(path.read_text())
        except Exception:
            continue
        paper_id = obj.get('paper_id') or path.name.split('.')[0]
        payload[paper_id] = obj
    return payload


def load_main_conclusion_adjudications():
    payload = {}
    if not MAIN_CONCLUSION_DIR.exists():
        return payload
    for path in MAIN_CONCLUSION_DIR.glob('PDF-*.main_conclusion_adjudication.json'):
        try:
            obj = json.loads(path.read_text())
        except Exception:
            continue
        paper_id = obj.get('paper_id') or path.name.split('.')[0]
        payload[paper_id] = obj.get('decision') or {}
    return payload


def load_population_adjudications():
    payload = {}
    if not POPULATION_ADJUDICATION_DIR.exists():
        return payload
    for path in POPULATION_ADJUDICATION_DIR.glob('PDF-*.population_count_adjudication.json'):
        try:
            obj = json.loads(path.read_text())
        except Exception:
            continue
        paper_id = obj.get('paper_id') or path.name.split('.')[0]
        payload[paper_id] = obj.get('decision') or {}
    return payload


def load_result_relation_adjudications():
    payload = {}
    if not RESULT_RELATION_DIR.exists():
        return payload
    for path in RESULT_RELATION_DIR.glob('PDF-*.result_relation_adjudication.json'):
        try:
            obj = json.loads(path.read_text())
        except Exception:
            continue
        paper_id = obj.get('paper_id') or path.name.split('.')[0]
        payload[paper_id] = obj.get('decisions') or {}
    return payload


def load_page_image_scans():
    payload = {}
    if not PAGE_IMAGE_SCAN_DIR.exists():
        return payload
    for path in PAGE_IMAGE_SCAN_DIR.glob('PDF-*/*.page_image_first_section_scan.json'):
        try:
            obj = json.loads(path.read_text())
        except Exception:
            continue
        paper_id = obj.get('paper_id') or path.name.split('.')[0]
        payload[paper_id] = obj
    return payload


def load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def parse_page_number(value):
    if value in (None, ''):
        return None
    if isinstance(value, int):
        return value
    match = re.search(r'page[_ ]?(\d+)', str(value), re.I)
    if match:
        try:
            return int(match.group(1))
        except Exception:
            return None
    return None


def top_pages(scan, key, limit):
    ranked = (scan or {}).get('ranked') or {}
    rows = ranked.get(key) or []
    return [int(row.get('page')) for row in rows[:limit] if row.get('page')]


def page_reason_map(scan, key, limit=6):
    ranked = (scan or {}).get('ranked') or {}
    rows = ranked.get(key) or []
    out = {}
    for row in rows[:limit]:
        page = row.get('page')
        if page:
            out[int(page)] = row.get('reasons') or []
    return out


def compact_reason_list(reasons, limit=2):
    values = []
    for reason in reasons[:limit]:
        values.append(compact_text(reason, 160))
    return '; '.join(values)


def copy_visual_asset(src_path, paper_id):
    src = Path(src_path)
    if not src.exists():
        return ''
    target_dir = VISUALS_OUT / paper_id
    target_dir.mkdir(parents=True, exist_ok=True)
    dst = target_dir / src.name
    if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
        shutil.copy2(src, dst)
    return f"data/ka_payloads/article_visuals/{paper_id}/{src.name}"


def build_visual_support_for_paper(paper_id, article_type, representative_claim):
    manifest_path = STIMULUS_IMAGE_DIR / paper_id / 'manifest.json'
    scan = load_page_image_scans.cache.get(paper_id) if hasattr(load_page_image_scans, 'cache') else None
    if not manifest_path.exists():
        return [], {}
    try:
        manifest = json.loads(manifest_path.read_text())
    except Exception:
        return [], {}

    figure_pages = set(top_pages(scan, 'figure_pages', 6))
    sample_pages = set(top_pages(scan, 'sample_pages', 4))
    methods_pages = set(top_pages(scan, 'methods_pages', 4))
    results_pages = set(top_pages(scan, 'results_pages', 4))
    table_pages = set(top_pages(scan, 'table_pages', 4))
    figure_reasons = page_reason_map(scan, 'figure_pages')
    sample_reasons = page_reason_map(scan, 'sample_pages')
    table_reasons = page_reason_map(scan, 'table_pages')
    results_reasons = page_reason_map(scan, 'results_pages')

    candidate_rows = []
    for row in manifest.get('embedded_images') or []:
        page = int(row.get('page') or 0)
        width = int(row.get('width') or 0)
        height = int(row.get('height') or 0)
        if width < 220 or height < 160:
            continue
        score = 1
        kind = 'supplemental_visual'
        reasons = []
        if page in figure_pages:
            score += 6
            kind = 'stimulus_or_result_figure'
            reasons.extend(figure_reasons.get(page) or [])
        if page in sample_pages or page in methods_pages:
            score += 5
            if kind == 'supplemental_visual':
                kind = 'experimental_context'
            reasons.extend(sample_reasons.get(page) or [])
        if page in table_pages or page in results_pages:
            score += 3
            if kind == 'supplemental_visual':
                kind = 'results_surface'
            reasons.extend(table_reasons.get(page) or [])
            reasons.extend(results_reasons.get(page) or [])
        candidate_rows.append({
            'page': page,
            'src_path': row.get('path'),
            'filename': row.get('filename'),
            'score': score,
            'kind': kind,
            'reasons': reasons,
            'render_type': 'embedded',
        })

    for row in manifest.get('rendered_pages') or []:
        page = int(row.get('page') or 0)
        score = 0
        reasons = []
        if page in table_pages:
            score += 8
            reasons.extend(table_reasons.get(page) or [])
        if page in results_pages:
            score += 6
            reasons.extend(results_reasons.get(page) or [])
        if page in figure_pages:
            score += 4
            reasons.extend(figure_reasons.get(page) or [])
        if page in sample_pages or page in methods_pages:
            score += 2
            reasons.extend(sample_reasons.get(page) or [])
        if score <= 0:
            continue
        candidate_rows.append({
            'page': page,
            'src_path': row.get('path'),
            'filename': row.get('filename'),
            'score': score,
            'kind': 'results_surface' if page in (table_pages | results_pages) else 'experimental_context',
            'reasons': reasons,
            'render_type': row.get('render_type') or 'full_page',
            'dpi': row.get('dpi'),
        })

    candidate_rows.sort(key=lambda row: (-row['score'], row['page'], row.get('filename') or ''))
    gallery = []
    seen_targets = set()
    for row in candidate_rows:
        rel_path = copy_visual_asset(row.get('src_path'), paper_id)
        if not rel_path or rel_path in seen_targets:
            continue
        seen_targets.add(rel_path)
        if row['kind'] == 'experimental_context':
            title = f"Experimental context, page {row['page']}"
        elif row['kind'] == 'results_surface':
            title = f"Result surface, page {row['page']}"
        else:
            title = f"Stimulus or figure, page {row['page']}"
        caption = compact_reason_list(row.get('reasons') or []) or f"Recovered visual support from page {row['page']}."
        gallery.append({
            'surface_kind': row['kind'],
            'page': row['page'],
            'image_url': rel_path,
            'atlas_title': title,
            'atlas_caption': caption,
            'render_type': row.get('render_type') or 'embedded',
            'dpi': row.get('dpi'),
        })
        if len(gallery) >= 8:
            break

    technical = {}
    for row in candidate_rows:
        if row['page'] in table_pages or row['page'] in results_pages:
            rel_path = copy_visual_asset(row.get('src_path'), paper_id)
            if not rel_path:
                continue
            technical = {
                'title': f"Technical results surface, page {row['page']}",
                'page': row['page'],
                'image_url': rel_path,
                'caption': compact_reason_list(row.get('reasons') or []) or f"Results-bearing page {row['page']}.",
                'summary': compact_text(
                    representative_claim.get('test_statistic')
                    or representative_claim.get('statement')
                    or representative_claim.get('claim')
                    or '',
                    360,
                ),
            }
            break

    if not technical and gallery:
        first = next((item for item in gallery if item.get('surface_kind') == 'results_surface'), gallery[0])
        technical = {
            'title': first.get('atlas_title') or 'Technical results surface',
            'page': first.get('page'),
            'image_url': first.get('image_url'),
            'caption': first.get('atlas_caption') or '',
            'summary': compact_text(
                representative_claim.get('test_statistic')
                or representative_claim.get('statement')
                or representative_claim.get('claim')
                or '',
                360,
            ),
        }

    return gallery, technical


def ensure_workflow_db():
    WORKFLOW_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(WORKFLOW_DB_PATH)
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS registrations (
            user_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            role TEXT,
            institution TEXT,
            department TEXT,
            user_type TEXT,
            nav_preference TEXT,
            track_choice1 TEXT,
            track_choice2 TEXT,
            status TEXT,
            approved_track TEXT,
            rejection_reason TEXT,
            timestamp TEXT,
            approved_at TEXT,
            rejected_at TEXT
        );

        CREATE TABLE IF NOT EXISTS intake_submissions (
            submission_id TEXT PRIMARY KEY,
            user_id TEXT,
            identity_type TEXT,
            track TEXT,
            status TEXT,
            kind TEXT,
            title TEXT,
            citation TEXT,
            authors TEXT,
            abstract TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS track_targets (
            track_label TEXT PRIMARY KEY,
            target INTEGER NOT NULL
        );
        """
    )

    cur.execute("SELECT COUNT(*) FROM registrations")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            """
            INSERT INTO registrations (
                user_id, first_name, last_name, email, role, institution, department,
                user_type, nav_preference, track_choice1, track_choice2, status,
                approved_track, rejection_reason, timestamp, approved_at, rejected_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ('student_alex_chen', 'Alex', 'Chen', 'alex.chen@example.edu', 'undergrad', 'UC San Diego', 'Cognitive Science', 'student_explorer', 'explore_literature', 'Track 2 — Article Finding', 'Track 4 — GUI Evaluation & Experiment Design', 'approved', 'Track 2 — Article Finding', '', '2026-03-20T09:00:00Z', '2026-03-21T18:00:00Z', ''),
                ('student_jordan_miles', 'Jordan', 'Miles', 'jordan.miles@example.edu', 'undergrad', 'UC San Diego', 'Design Lab', 'contributor', 'contribute', 'Track 1 — Image Tagging', 'Track 2 — Article Finding', 'approved', 'Track 1 — Image Tagging', '', '2026-03-20T11:00:00Z', '2026-03-21T18:10:00Z', ''),
                ('student_taylor_reed', 'Taylor', 'Reed', 'taylor.reed@example.edu', 'graduate', 'UC San Diego', 'VR Lab', 'contributor', 'contribute', 'Track 3 — VR Production', 'Track 4 — GUI Evaluation & Experiment Design', 'approved', 'Track 3 — VR Production', '', '2026-03-20T12:00:00Z', '2026-03-21T18:20:00Z', ''),
                ('student_morgan_liu', 'Morgan', 'Liu', 'morgan.liu@example.edu', 'undergrad', 'UC San Diego', 'Human Factors', 'student_explorer', 'explore_literature', 'Track 4 — GUI Evaluation & Experiment Design', 'Track 2 — Article Finding', 'pending', '', '', '2026-03-24T08:30:00Z', '', ''),
                ('student_priya_nair', 'Priya', 'Nair', 'priya.nair@example.edu', 'undergrad', 'UC San Diego', 'Psychology', 'student_explorer', 'explore_literature', 'Track 2 — Article Finding', 'Track 1 — Image Tagging', 'pending', '', '', '2026-03-24T10:15:00Z', '', ''),
                ('student_sam_ortiz', 'Sam', 'Ortiz', 'sam.ortiz@example.edu', 'undergrad', 'UC San Diego', 'Cognitive Science', 'contributor', 'contribute', 'Track 1 — Image Tagging', 'Track 4 — GUI Evaluation & Experiment Design', 'rejected', '', 'Track capacity currently full', '2026-03-23T14:05:00Z', '', '2026-03-24T17:30:00Z'),
            ],
        )

    cur.execute("SELECT COUNT(*) FROM intake_submissions")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            """
            INSERT INTO intake_submissions (
                submission_id, user_id, identity_type, track, status, kind, title,
                citation, authors, abstract, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ('KA-PROP-0042', 'student_alex_chen', 'student', 'Track 2 — Article Finding', 'approved', 'citation', 'Impact of windows and daylight exposure on overall health and sleep quality of office workers', 'Boubekri et al. (2014). Impact of windows and daylight exposure on overall health and sleep quality of office workers. Journal of Clinical Sleep Medicine.', 'Boubekri, Cheung, Reid, Wang, Zee', 'Office workers with more daylight exposure slept longer and reported better quality of life indicators than workers in windowless offices.', '2026-03-22T09:10:00Z'),
                ('KA-PROP-0043', 'student_alex_chen', 'student', 'Track 2 — Article Finding', 'pending', 'pdf', 'Appearance wood products and psychological well-being', 'Rice et al. (2006). Appearance wood products and psychological well-being. Wood and Fiber Science.', 'Rice, Kozak, Meitner, Cohen', 'Exploratory study of whether wood interiors shape emotional responses and perceived well-being.', '2026-03-24T11:30:00Z'),
                ('KA-PROP-0044', 'student_jordan_miles', 'student', 'Track 1 — Image Tagging', 'approved', 'pdf', 'High-rise window views and stress recovery', '', 'Metadata pending', '', '2026-03-24T12:45:00Z'),
                ('KA-PROP-0045', 'student_taylor_reed', 'student', 'Track 3 — VR Production', 'pending', 'citation', 'Green-water and green views from high-rise windows', 'Author metadata staged from window-view corpus.', 'Metadata pending', '', '2026-03-24T13:20:00Z'),
            ],
        )

    cur.execute("SELECT COUNT(*) FROM track_targets")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO track_targets (track_label, target) VALUES (?, ?)", DEFAULT_TRACK_TARGETS)
    conn.commit()
    conn.close()


def build_workflow_payload():
    ensure_workflow_db()
    conn = sqlite3.connect(WORKFLOW_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    registrations = [dict(row) for row in cur.execute("SELECT * FROM registrations ORDER BY timestamp DESC, user_id")]
    submissions = [dict(row) for row in cur.execute("SELECT * FROM intake_submissions ORDER BY created_at DESC, submission_id DESC")]
    track_targets = [dict(row) for row in cur.execute("SELECT * FROM track_targets ORDER BY track_label")]
    conn.close()

    registrations_payload = [
        {
            'id': row['user_id'],
            'firstName': row['first_name'],
            'lastName': row['last_name'],
            'email': row['email'],
            'role': row['role'],
            'institution': row['institution'],
            'department': row['department'],
            'userType': row['user_type'],
            'navPreference': row['nav_preference'],
            'trackChoice1': row['track_choice1'],
            'trackChoice2': row['track_choice2'],
            'status': row['status'],
            'approvedTrack': row['approved_track'],
            'rejectionReason': row['rejection_reason'],
            'timestamp': row['timestamp'],
            'approvedAt': row['approved_at'],
            'rejectedAt': row['rejected_at'],
        }
        for row in registrations
    ]
    submissions_payload = [
        {
            'submissionId': row['submission_id'],
            'userId': row['user_id'],
            'identityType': row['identity_type'],
            'track': row['track'],
            'status': row['status'],
            'kind': row['kind'],
            'title': row['title'],
            'citation': row['citation'],
            'authors': row['authors'],
            'abstract': row['abstract'],
            'createdAt': row['created_at'],
        }
        for row in submissions
    ]
    current_user = next((row for row in registrations_payload if row['id'] == 'student_alex_chen'), registrations_payload[0] if registrations_payload else None)
    return {
        'current_user': current_user,
        'registrations': registrations_payload,
        'intake_submissions': submissions_payload,
        'track_targets': track_targets,
        'summary': {
            'registration_count': len(registrations_payload),
            'pending_count': sum(1 for row in registrations_payload if row.get('status') == 'pending'),
            'approved_count': sum(1 for row in registrations_payload if row.get('status') == 'approved'),
            'rejected_count': sum(1 for row in registrations_payload if row.get('status') == 'rejected'),
            'submission_count': len(submissions_payload),
            'pending_submission_count': sum(1 for row in submissions_payload if row.get('status') == 'pending'),
        },
        'db_path': str(WORKFLOW_DB_PATH),
        'generated_at': datetime.now(timezone.utc).isoformat(),
    }


def load_rebuild_belief_lookup():
    lookup = {}
    if not REBUILD_DB_PATH.exists():
        return lookup
    conn = sqlite3.connect(REBUILD_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    for row in cur.execute("SELECT belief_id, credence_value, omega_json FROM beliefs"):
        omega_json = {}
        try:
            omega_json = json.loads(row['omega_json'] or '{}')
        except Exception:
            omega_json = {}
        belief_id = str(row['belief_id'] or '').strip()
        if not belief_id:
            continue
        lookup[belief_id] = {
            'credence_value': float(row['credence_value'] or 0.5),
            'omega_json': omega_json,
        }
    conn.close()
    return lookup


def summarize_methodology(method_profile, article_type):
    if not isinstance(method_profile, dict):
        return humanize(article_type) or 'Current rebuild article record.'
    bits = []
    if method_profile.get('study_design'):
        bits.append(humanize(method_profile['study_design']))
    if method_profile.get('method_families'):
        bits.append('Methods: ' + ', '.join(humanize(x) for x in method_profile['method_families'][:3]))
    if method_profile.get('measure_families'):
        bits.append('Measures: ' + ', '.join(humanize(x) for x in method_profile['measure_families'][:3]))
    return '; '.join(bits) if bits else (humanize(article_type) or 'Current rebuild article record.')


def detect_instruments(obj):
    haystack = ' '.join([
        str(obj.get('statement') or ''),
        str(obj.get('iv') or ''),
        str(obj.get('dv') or ''),
        str(obj.get('abstract_clean_text') or ''),
        str((obj.get('structured_result_row') or {}).get('comparison') or ''),
        str((obj.get('structured_result_row') or {}).get('outcome') or ''),
    ])
    lowered = f" {haystack.lower()} "
    found = []
    for label, patterns in INSTRUMENT_PATTERNS.items():
        if any(pat in lowered for pat in patterns):
            found.append(label)
    return found


def classify_front(front):
    label = (front.get('label') or '').lower()
    theories = ' '.join(front.get('shared_theories') or []).lower()
    constructs = ' '.join(front.get('shared_constructs') or []).lower()
    blob = ' '.join([label, theories, constructs])
    if any(x in blob for x in ['neuro', 'brain', 'cognitive_map', 'attention', 'memory', 'locus', 'circadian']):
        return 'Neuroscience'
    if any(x in blob for x in ['stress', 'arousal', 'fatigue', 'well_being', 'sleep', 'circadian', 'thermal']):
        return 'Physiological'
    if any(x in blob for x in ['theory', 'replication', 'method', 'measurement']):
        return 'Methodology'
    if any(x in blob for x in ['wayfinding', 'cog', 'creativity', 'executive', 'attention']):
        return 'Cognitive'
    return 'Environmental'


def load_fronts():
    obj = json.loads(FRONTS_PATH.read_text())
    fronts = obj.get('fronts', [])
    topic_payload = []
    gap_payload = []
    for front in fronts:
        label = front.get('label') or front.get('front_id') or 'Unlabeled front'
        cat = classify_front(front)
        size = int(front.get('size') or len(front.get('papers') or []))
        voi = round(float(front.get('mean_omega') or 0.0), 2)
        desc_bits = []
        theories = front.get('shared_theories') or []
        constructs = front.get('shared_constructs') or []
        if theories:
            desc_bits.append('Theories: ' + ', '.join(t.replace('theory_', '').replace('_', ' ') for t in theories[:3]))
        if constructs:
            desc_bits.append('Constructs: ' + ', '.join(c.replace('_', ' ') for c in constructs[:4]))
        desc_bits.append(f"Maturity: {front.get('maturity', 'unknown')}.")
        desc = ' '.join(desc_bits) if desc_bits else 'Research front from the current rebuild.'
        topic_payload.append({
            'id': front.get('front_id') or slugify(label),
            'cat': cat,
            'n': size,
            'voi': voi,
            'name': label,
            'desc': desc,
            'maturity': front.get('maturity', 'unknown'),
            'shared_theories': theories,
            'shared_constructs': constructs,
            'contradictions': int(front.get('n_contradictions') or 0),
            'replications': int(front.get('n_replications') or 0),
        })
        if size <= 8 or front.get('maturity') != 'established' or int(front.get('n_contradictions') or 0) > 0:
            if voi >= 0.7:
                voi_label = 'high'
            elif voi >= 0.45:
                voi_label = 'medium'
            else:
                voi_label = 'low'
            gap_type = 'untested' if size <= 8 else 'conflict' if int(front.get('n_contradictions') or 0) > 0 else 'credence'
            gap_payload.append({
                'id': front.get('front_id') or slugify(label),
                'type': gap_type,
                'title': label,
                'description': desc,
                'construct': slugify((constructs[0] if constructs else cat).replace('.', ' ')),
                'context': 'multiple',
                'voi': voi_label,
                'credence': voi,
                'whyMatters': f"This front remains strategically important because its current maturity is {front.get('maturity', 'unknown')} with corpus size {size}.",
                'hypothesisBuild': f"ka_hypothesis_builder.html?front={front.get('front_id')}",
                'evidenceLink': f"ka_evidence.html?front={front.get('front_id')}"
            })
    topic_payload.sort(key=lambda x: (-x['voi'], -x['n'], x['name']))
    gap_payload.sort(key=lambda x: ({'high':0,'medium':1,'low':2}[x['voi']], x['title']))
    return topic_payload, gap_payload


def parse_claims():
    evidence = []
    paper_claims = defaultdict(list)
    paper_meta = {}
    belief_lookup = load_rebuild_belief_lookup()
    repairs = load_bibliographic_repairs()
    deep_stats = load_deep_stat_adjudications()
    abstract_adjudications = load_abstract_adjudications()
    main_conclusions = load_main_conclusion_adjudications()
    population_adjudications = load_population_adjudications()
    result_relations = load_result_relation_adjudications()
    page_image_scans = load_page_image_scans()
    load_page_image_scans.cache = page_image_scans
    with CLAIMS_PATH.open() as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            pid = obj.get('paper_id')
            belief_id = str(obj.get('id') or obj.get('finding_id') or '').strip()
            belief_state = belief_lookup.get(belief_id, {})
            statement = obj.get('statement') or obj.get('claim') or ''
            result = obj.get('structured_result_row') or {}
            theories = []
            ptf = obj.get('paper_theory_frame') or {}
            theories.extend(ptf.get('canonical_theories') or [])
            theories.extend(obj.get('theory_names') or [])
            repair = repairs.get(pid, {})
            if pid and pid not in paper_meta:
                abstract_payload = abstract_adjudications.get(pid) or {}
                abstract_decision = abstract_payload.get('decision') or {}
                abstract_choice = sanitize_abstract(abstract_decision.get('chosen_text') or '')
                fallback_abstract = sanitize_abstract(repair.get('abstract') or obj.get('abstract_clean_text')) or ''
                abstract_value = abstract_choice or fallback_abstract
                abstract_state = (
                    normalize_abstract_state(abstract_payload.get('status') or abstract_status(abstract_choice))
                    if abstract_choice
                    else normalize_abstract_state(abstract_status(abstract_value))
                )
                stat_decisions = deep_stats.get(pid, {})
                sample_decision = stat_decisions.get('sample_n') or {}
                p_value_decision = stat_decisions.get('p_value') or {}
                effect_decision = stat_decisions.get('effect_size') or {}
                population_decision = population_adjudications.get(pid) or {}
                raw_subject_total = obj.get('subject_count_total')
                population_value = population_decision.get('chosen_value')
                population_state = normalize_adjudication_state(population_decision.get('status')) if population_decision else 'missing'
                relation_decisions = result_relations.get(pid) or {}
                construct_pair_decision = relation_decisions.get('construct_pair') or {}
                direction_decision = relation_decisions.get('direction') or {}
                if population_value in (None, '', 0) and raw_subject_total not in (None, '', 0):
                    population_value = raw_subject_total
                    population_state = subject_count_status(raw_subject_total)
                paper_meta[pid] = {
                    'paper_id': pid,
                    'title': publishable_title(repair.get('title')) or publishable_title(obj.get('paper_title')) or publishable_title(obj.get('title')) or '',
                    'doi': clean_doi(repair.get('doi') or obj.get('doi')),
                    'year': sanitize_year(repair.get('year') or obj.get('year')),
                    'abstract': abstract_value,
                    'abstract_status': abstract_state,
                    'abstract_source': abstract_decision.get('chosen_source') or repair.get('source') or '',
                    'repair_source': repair.get('source') or '',
                    'abstract_surface_path': repair.get('abstract_surface_path') or '',
                    'theories': theories,
                    'subject_count_total': population_value,
                    'subject_count_total_status': population_state,
                    'construct_pair': construct_pair_decision.get('chosen_value'),
                    'construct_pair_status': construct_pair_decision.get('status') or 'missing',
                    'direction': direction_decision.get('chosen_value'),
                    'direction_status': direction_decision.get('status') or 'missing',
                    'sample_n': sample_decision.get('chosen_value', obj.get('sample_n')),
                    'sample_n_status': sample_decision.get('status') or subject_count_status(obj.get('sample_n')),
                    'p_value': p_value_decision.get('chosen_value'),
                    'p_value_status': p_value_decision.get('status') or 'missing',
                    'effect_size': effect_decision.get('chosen_value'),
                    'effect_size_status': effect_decision.get('status') or 'missing',
                    'article_type': obj.get('article_type') or '',
                    'authors': normalize_authors(repair.get('authors')),
                    'venue': repair.get('venue') or '',
                    'apa_citation': repair.get('apa_citation') or '',
                    'main_conclusion': (main_conclusions.get(pid) or {}).get('chosen_text') or '',
                    'main_conclusion_status': (main_conclusions.get(pid) or {}).get('status') or 'missing',
                }
            if pid:
                paper_claims[pid].append(obj)
            if len(evidence) < 200:
                result_sentence = result.get('result_sentence') or ''
                fallback_finding = result_sentence or ' -> '.join(
                    x for x in [result.get('comparison'), result.get('outcome')] if x
                )
                outcome_tags = obj.get('outcome_tags') or []
                construct_label = ''
                if outcome_tags:
                    construct_label = humanize(outcome_tags[0].get('canonical'))
                if not construct_label:
                    construct_label = compact_text(result.get('outcome') or obj.get('dv') or 'Unknown', 80)
                raw_warrant_type = (
                    (obj.get('evidence_profile') or {}).get('warrant_type')
                    or obj.get('warrant_type')
                    or ''
                )
                canonical_warrant_type = (
                    ((belief_state.get('omega_json') or {}).get('bridge_type'))
                    or derive_canonical_bridge_type(obj)
                )
                warrant_label = canonical_warrant_display(canonical_warrant_type)
                methodology_summary = summarize_methodology(obj.get('method_profile_excerpt'), obj.get('article_type'))
                evidence.append({
                    'id': len(evidence) + 1,
                    'finding': compact_text(statement or fallback_finding or pid, 220),
                    'construct': construct_label,
                    'signal': humanize(obj.get('evidence_strength_class') or obj.get('claim_type') or 'Claim'),
                    'studyType': humanize(obj.get('article_type') or 'Unknown'),
                    'warrant': warrant_label,
                    'warrant_class': canonical_warrant_type,
                    'warrant_discount': BRIDGE_DISCOUNT_BY_VALUE.get(canonical_warrant_type),
                    'extraction_warrant_type': raw_warrant_type,
                    'article_type_warrant_family': _primary_bridge_type(obj.get('article_type')),
                    'claim_role': obj.get('claim_role') or '',
                    'credence': round(float(belief_state.get('credence_value', obj.get('severity') or 0.5)), 2),
                    'year': sanitize_year(repair.get('year') or obj.get('year')) or '',
                    'citation': pid,
                    'abstract': compact_text(paper_meta[pid]['abstract'] or 'Abstract not yet recovered from the current rebuild.', 500),
                    'claim': compact_text(statement or fallback_finding or pid, 260),
                    'methodology': methodology_summary,
                    'warrant_chain': compose_warrant_chain(
                        canonical_warrant_type,
                        raw_warrant_type,
                        result,
                        obj.get('claim_role'),
                    ),
                    'paper_id': pid,
                    'front_id': obj.get('topic_label') or obj.get('finding_id') or '',
                })
    articles = []
    for pid, claims in paper_claims.items():
        meta = paper_meta.get(pid, {'paper_id': pid, 'title': pid, 'doi': '', 'abstract': '', 'theories': []})
        theory_counter = Counter()
        construct_counter = Counter()
        measure_counter = Counter()
        for c in claims:
            for t in (c.get('theory_names') or []):
                theory_counter[t] += 1
            ptf = c.get('paper_theory_frame') or {}
            for t in (ptf.get('canonical_theories') or []):
                theory_counter[t] += 1
            for tag in (c.get('outcome_tags') or []):
                construct_counter[tag.get('canonical') or ''] += 1
            for tag in (c.get('env_tags') or []):
                construct_counter[tag.get('canonical') or ''] += 1
            method_profile = c.get('method_profile_excerpt') or {}
            for m in (method_profile.get('measure_families') or []):
                measure_counter[m] += 1
            for label in detect_instruments(c):
                measure_counter[label] += 1
        top_theories = [t.replace('theory_', '').replace('_', ' ') for t, _ in theory_counter.most_common(4)]
        top_constructs = [humanize(t) for t, _ in construct_counter.most_common(4) if t]
        top_measures = [humanize(t) for t, _ in measure_counter.most_common(3) if t]
        representative = claims[0] if claims else {}
        representative_result = representative.get('structured_result_row') or {}
        visual_support_gallery, technical_results_table = build_visual_support_for_paper(
            pid,
            meta.get('article_type') or representative.get('article_type') or '',
            representative,
        )
        title = publishable_title(meta.get('title')) or publishable_title(representative.get('paper_title')) or publishable_title(representative.get('title'))
        if not title:
            title = compact_text(
                representative_result.get('comparison')
                or representative_result.get('outcome')
                or representative.get('dv')
                or representative.get('iv')
                or pid,
                120,
            )
        articles.append({
            'paper_id': pid,
            'title': title,
            'doi': clean_doi(meta.get('doi')),
            'year': sanitize_year(meta.get('year')),
            'apa_citation': meta.get('apa_citation') or format_apa_citation(meta.get('authors'), meta.get('year'), title, meta.get('doi')),
            'abstract': sanitize_abstract(meta.get('abstract')) or 'Abstract not yet recovered from the current rebuild.',
            'claim_count': len(claims),
            'sample_n': meta.get('sample_n'),
            'p_value': meta.get('p_value'),
            'effect_size': meta.get('effect_size'),
            'subject_count_total': meta.get('subject_count_total'),
            'construct_pair': meta.get('construct_pair'),
            'direction': meta.get('direction'),
            'theories': top_theories,
            'constructs': top_constructs,
            'instruments': top_measures,
            'article_type': meta.get('article_type') or '',
            'authors': normalize_authors(meta.get('authors')),
            'venue': meta.get('venue') or '',
                'main_conclusion': meta.get('main_conclusion') or '',
                'repair_source': meta.get('repair_source') or '',
            'abstract_source': meta.get('abstract_source') or '',
            'abstract_surface_path': meta.get('abstract_surface_path') or '',
            'visual_support_gallery': visual_support_gallery,
            'technical_results_table': technical_results_table,
                'json_status': {
                'title': title_status(title),
                'doi': doi_status(meta.get('doi')),
                'abstract': meta.get('abstract_status') or abstract_status(meta.get('abstract')),
                    'sample_n': meta.get('sample_n_status') or 'missing',
                    'p_value': meta.get('p_value_status') or 'missing',
                    'effect_size': meta.get('effect_size_status') or 'missing',
                    'main_conclusion': meta.get('main_conclusion_status') or 'missing',
                    'subject_count_total': meta.get('subject_count_total_status') or subject_count_status(meta.get('subject_count_total')),
                    'construct_pair': meta.get('construct_pair_status') or 'missing',
                    'direction': meta.get('direction_status') or 'missing',
                    'repair_source': meta.get('repair_source') or 'rebuild',
                },
            })
    articles.sort(key=lambda x: (-x['claim_count'], x['paper_id']))
    return evidence, articles[:250]


def build_json_status(articles):
    summary = {
        'papers_total': len(articles),
        'title_good': 0,
        'title_provisional': 0,
        'title_missing_or_blocked': 0,
        'abstract_good': 0,
        'abstract_provisional': 0,
        'abstract_missing': 0,
        'doi_good': 0,
        'doi_missing': 0,
        'sample_n_accepted': 0,
        'sample_n_provisional': 0,
        'sample_n_review_required': 0,
        'sample_n_missing': 0,
        'p_value_accepted': 0,
        'p_value_provisional': 0,
        'p_value_review_required': 0,
        'p_value_missing': 0,
        'effect_size_accepted': 0,
        'effect_size_provisional': 0,
        'effect_size_review_required': 0,
        'effect_size_missing': 0,
        'main_conclusion_accepted': 0,
        'main_conclusion_provisional': 0,
        'main_conclusion_missing': 0,
        'subject_count_total_accepted': 0,
        'subject_count_total_provisional': 0,
        'subject_count_total_review_required': 0,
        'subject_count_total_missing': 0,
        'subject_count_good': 0,
        'subject_count_missing': 0,
        'construct_pair_good': 0,
        'construct_pair_missing': 0,
        'direction_good': 0,
        'direction_missing': 0,
    }
    rows = []
    for article in articles:
        status = article.get('json_status') or {}
        title_state = status.get('title') or 'missing'
        abstract_state = status.get('abstract') or 'missing'
        doi_state = status.get('doi') or 'missing'
        sample_state = status.get('sample_n') or 'missing'
        p_state = status.get('p_value') or 'missing'
        effect_state = status.get('effect_size') or 'missing'
        conclusion_state = status.get('main_conclusion') or 'missing'
        subject_state = status.get('subject_count_total') or 'missing'
        construct_pair_state = status.get('construct_pair') or 'missing'
        direction_state = status.get('direction') or 'missing'
        if title_state == 'good':
            summary['title_good'] += 1
        elif title_state == 'provisional':
            summary['title_provisional'] += 1
        else:
            summary['title_missing_or_blocked'] += 1
        if abstract_state == 'good':
            summary['abstract_good'] += 1
        elif abstract_state == 'provisional':
            summary['abstract_provisional'] += 1
        else:
            summary['abstract_missing'] += 1
        if doi_state == 'good':
            summary['doi_good'] += 1
        else:
            summary['doi_missing'] += 1
        summary[f"sample_n_{sample_state if sample_state in {'accepted', 'provisional', 'review_required'} else 'missing'}"] += 1
        summary[f"p_value_{p_state if p_state in {'accepted', 'provisional', 'review_required'} else 'missing'}"] += 1
        summary[f"effect_size_{effect_state if effect_state in {'accepted', 'provisional', 'review_required'} else 'missing'}"] += 1
        summary[f"main_conclusion_{conclusion_state if conclusion_state in {'accepted', 'provisional'} else 'missing'}"] += 1
        if subject_state == 'good':
            normalized_subject_state = 'provisional'
        elif subject_state in {'accepted', 'provisional', 'review_required'}:
            normalized_subject_state = subject_state
        else:
            normalized_subject_state = 'missing'
        summary[f"subject_count_total_{normalized_subject_state}"] += 1
        if subject_state in {'good', 'accepted', 'provisional'}:
            summary['subject_count_good'] += 1
        else:
            summary['subject_count_missing'] += 1
        summary[f"construct_pair_{'good' if construct_pair_state in {'accepted', 'provisional', 'good'} else 'missing'}"] += 1
        summary[f"direction_{'good' if direction_state in {'accepted', 'provisional', 'good'} else 'missing'}"] += 1
        rows.append({
            'paper_id': article.get('paper_id'),
            'title': article.get('title'),
            'claim_count': article.get('claim_count'),
            'json_status': status,
        })
    return {'summary': summary, 'papers': rows}


def build_dashboard(articles, evidence):
    payload = {
        'student_name': 'Alex Chen',
        'track': 'Track 2',
        'week_label': 'Week 4 of 10',
        'next_due_days': 3,
        'progress': {
            'apa_submissions': {'done': 7, 'target': 20, 'href': 'ka_article_propose.html'},
            'pdfs_uploaded': {'done': 3, 'target': 10, 'href': 'ka_article_propose.html'},
            'images_tagged': {'done': 24, 'target': 50, 'href': 'ka_tagger.html'},
            'articles_evaluated': {'done': min(6, len(evidence)), 'target': 15, 'href': 'ka_evidence.html'},
        },
        'recent_activity': [
            {'type': f"Evidence rows loaded: {len(evidence)}", 'date': 'Current rebuild', 'badge': 'SYNCED'},
            {'type': f"Article payload size: {len(articles)} papers", 'date': 'Current rebuild', 'badge': 'READY'},
        ],
        'leaderboard': [
            {'rank': 1, 'name': 'Jordan M.', 'count': 18},
            {'rank': 2, 'name': 'Taylor R.', 'count': 15},
            {'rank': 3, 'name': 'You (Alex Chen)', 'count': 12},
        ]
    }
    coverage = load_json(FIELD_COVERAGE_BY_TYPE_PATH, {})
    if coverage:
        payload['field_coverage_by_article_type'] = coverage
    return payload


def build_argumentation_payload():
    paper_graph = load_json(ARG_GRAPH_PATH, {})
    claim_graph = load_json(CLAIM_ARG_GRAPH_PATH, {})

    paper_nodes_raw = paper_graph.get('nodes') or {}
    if isinstance(paper_nodes_raw, dict):
        paper_nodes = list(paper_nodes_raw.values())
    else:
        paper_nodes = list(paper_nodes_raw)

    claim_nodes_raw = claim_graph.get('nodes') or {}
    if isinstance(claim_nodes_raw, dict):
        claim_nodes = list(claim_nodes_raw.values())
    else:
        claim_nodes = list(claim_nodes_raw)

    clusters = []
    for cluster in paper_graph.get('debate_clusters') or []:
        theories = cluster.get('theories') or []
        papers = cluster.get('papers') or []
        clusters.append({
            'cluster_id': cluster.get('cluster_id'),
            'paper_count': len(papers),
            'theory_count': len(theories),
            'papers': papers[:12],
            'theories': theories[:10],
        })
    clusters.sort(key=lambda item: (-item['paper_count'], item['cluster_id'] or ''))

    paper_nodes.sort(
        key=lambda node: (
            -(node.get('contradiction_count') or 0),
            -(node.get('claim_count') or 0),
            str(node.get('paper_id') or node.get('belief_id') or ''),
        )
    )
    claim_nodes.sort(
        key=lambda node: (
            -(node.get('incoming_attack_count') or 0),
            -(node.get('incoming_support_count') or 0),
            -(node.get('contradiction_count') or 0),
            str(node.get('belief_id') or ''),
        )
    )

    metadata = paper_graph.get('metadata') or {}
    coverage = paper_graph.get('coverage_report') or {}
    claim_metadata = claim_graph.get('metadata') or {}
    return {
        'summary': {
            'paper_node_count': metadata.get('node_count', len(paper_nodes)),
            'paper_edge_count': metadata.get('edge_count', len(paper_graph.get('edges') or [])),
            'claim_node_count': claim_metadata.get('node_count', len(claim_nodes)),
            'claim_edge_count': claim_metadata.get('edge_count', len(claim_graph.get('edges') or [])),
            'cluster_count': metadata.get('cluster_count', len(clusters)),
            'total_claims': coverage.get('total_claims', 0),
            'stance_coverage_rate': coverage.get('stance_coverage_rate', 0),
            'unique_theories': coverage.get('unique_theories', 0),
            'critical_question_payload_present': bool(claim_metadata.get('critical_question_payload_present')),
        },
        'coverage_report': coverage,
        'debate_clusters': clusters[:12],
        'paper_nodes': [
            {
                'paper_id': node.get('paper_id') or node.get('belief_id'),
                'content_preview': compact_text(node.get('content_preview') or node.get('content') or '', 180),
                'contradiction_count': node.get('contradiction_count') or 0,
                'node_qualifier': node.get('node_qualifier') or node.get('qualifier') or '',
            }
            for node in paper_nodes[:24]
        ],
        'claim_nodes': [
            {
                'belief_id': node.get('belief_id'),
                'paper_id': node.get('paper_id'),
                'content_preview': compact_text(node.get('content_preview') or node.get('content') or '', 180),
                'incoming_support_count': node.get('incoming_support_count') or 0,
                'incoming_attack_count': node.get('incoming_attack_count') or 0,
                'qualifier': node.get('qualifier') or node.get('node_qualifier') or '',
            }
            for node in claim_nodes[:24]
        ],
        'source_files': {
            'paper_graph': str(ARG_GRAPH_PATH.relative_to(ROOT)),
            'claim_graph': str(CLAIM_ARG_GRAPH_PATH.relative_to(ROOT)),
        },
    }


def build_annotations_payload():
    annotations = load_json(ANNOTATIONS_PATH, {})
    by_type = annotations.get('by_type') or {}
    annotation_rows = annotations.get('annotations') or []
    type_rows = [
        {'type': key, 'count': value}
        for key, value in sorted(by_type.items(), key=lambda item: (-item[1], item[0]))
    ]
    return {
        'summary': {
            'total_beliefs': annotations.get('total_beliefs', 0),
            'total_annotations': annotations.get('total_annotations', len(annotation_rows)),
            'artifact_role': annotations.get('artifact_role') or '',
            'canonical_source': annotations.get('canonical_source') or '',
            'description': annotations.get('description') or '',
        },
        'by_type': type_rows,
        'annotations': [
            {
                'id': row.get('id'),
                'type': row.get('type'),
                'target_type': row.get('target_type'),
                'target_id': row.get('target_id'),
                'content': compact_text(row.get('content') or '', 220),
                'confidence': row.get('confidence'),
                'status': row.get('status') or '',
            }
            for row in annotation_rows[:40]
        ],
        'source_file': str(ANNOTATIONS_PATH.relative_to(ROOT)),
    }


def build_interpretation_payload():
    phase4_summary = load_json(INTERPRETATION_SUMMARY_PATH, {})
    frontier = load_json(FRONTIER_QUESTIONS_PATH, {})
    validation = load_json(VALIDATION_COMPLETENESS_PATH, {})
    boundary = load_json(BOUNDARY_MAP_PATH, {})

    questions = []
    for row in frontier.get('questions') or []:
        questions.append({
            'frontier_id': row.get('frontier_id'),
            'belief_id': row.get('belief_id'),
            'framework_name': row.get('resolved_framework_name') or row.get('resolved_framework_id') or row.get('belief_id'),
            'voi_score': row.get('voi_score'),
            'voi_bucket': row.get('voi_bucket'),
            'zone': row.get('zone'),
            'question_set': (row.get('questions') or [])[:3],
            'matching_paper_count': len(row.get('matching_paper_ids') or []),
        })
    questions.sort(key=lambda row: (-(row.get('voi_score') or 0), row.get('framework_name') or ''))

    beliefs = []
    for row in validation.get('beliefs') or []:
        beliefs.append({
            'belief_id': row.get('belief_id'),
            'validation_completeness': row.get('validation_completeness'),
            'replication_status': row.get('replication_status'),
            'supporting_evidence_count': row.get('supporting_evidence_count'),
            'challenging_evidence_count': row.get('challenging_evidence_count'),
            'scope_specified': row.get('scope_specified'),
        })
    beliefs.sort(
        key=lambda row: (
            -(row.get('challenging_evidence_count') or 0),
            row.get('validation_completeness') or 0,
            row.get('belief_id') or '',
        )
    )

    zone_counts = (boundary.get('zone_classification') or {})
    transitions = boundary.get('transition_dynamics') or {}
    return {
        'summary': {
            'analysis_complete': bool(phase4_summary.get('analysis_complete')),
            'average_completeness': (validation.get('average_completeness')),
            'phase3_baseline': validation.get('phase3_baseline'),
            'high_voi_count': frontier.get('high_voi_count', 0),
            'medium_voi_count': frontier.get('medium_voi_count', 0),
            'low_voi_count': frontier.get('low_voi_count', 0),
            'active_boundary_count': zone_counts.get('active_boundary_count', 0),
            'identified_periphery_count': zone_counts.get('identified_periphery_count', 0),
        },
        'phase4_summary': phase4_summary,
        'frontier_questions': questions[:20],
        'validation_beliefs': beliefs[:20],
        'boundary_map': {
            'zone_classification': zone_counts,
            'beliefs_by_zone': boundary.get('beliefs_by_zone') or {},
            'transition_dynamics': transitions,
        },
        'source_files': {
            'phase4_summary': str(INTERPRETATION_SUMMARY_PATH.relative_to(ROOT)),
            'frontier_questions': str(FRONTIER_QUESTIONS_PATH.relative_to(ROOT)),
            'validation_completeness': str(VALIDATION_COMPLETENESS_PATH.relative_to(ROOT)),
            'boundary_map': str(BOUNDARY_MAP_PATH.relative_to(ROOT)),
        },
    }


def build_layers_summary(argumentation, annotations, interpretation):
    return {
        'layers': [
            {
                'id': 'argumentation',
                'title': 'Argumentation Layer',
                'href': 'ka_argumentation.html',
                'brief': 'docs/ARGUMENTATION_LAYER_ONE_PAGER_2026-03-26.md',
                'primary_metric': argumentation.get('summary', {}).get('claim_edge_count', 0),
                'primary_label': 'claim-level support edges',
            },
            {
                'id': 'annotations',
                'title': 'Annotation Layer',
                'href': 'ka_annotations.html',
                'brief': 'docs/ANNOTATION_LAYER_ONE_PAGER_2026-03-26.md',
                'primary_metric': annotations.get('summary', {}).get('total_annotations', 0),
                'primary_label': 'active annotations',
            },
            {
                'id': 'interpretation',
                'title': 'Interpretation Layer',
                'href': 'ka_interpretation.html',
                'brief': 'docs/INTERPRETATION_LAYER_ONE_PAGER_2026-03-26.md',
                'primary_metric': interpretation.get('summary', {}).get('high_voi_count', 0),
                'primary_label': 'high-VOI frontier questions',
            },
        ]
    }


def main():
    generated_at = datetime.now(timezone.utc).isoformat()
    workflow = build_workflow_payload()
    topics, gaps = load_fronts()
    evidence, articles = parse_claims()
    dashboard = build_dashboard(articles, evidence)
    json_status = build_json_status(articles)
    argumentation = build_argumentation_payload()
    annotations = build_annotations_payload()
    interpretation = build_interpretation_payload()
    layers = build_layers_summary(argumentation, annotations, interpretation)
    (OUT / 'topics.json').write_text(json.dumps({'topics': topics}, indent=2))
    (OUT / 'gaps.json').write_text(json.dumps({'gaps': gaps}, indent=2))
    (OUT / 'evidence.json').write_text(
        json.dumps(
            {
                'generated_at': generated_at,
                'source_claims': str(CLAIMS_PATH.relative_to(ROOT)),
                'warrant_taxonomy': {
                    'display_field': 'warrant',
                    'display_class_field': 'warrant_class',
                    'raw_extraction_field': 'extraction_warrant_type',
                    'discounts': BRIDGE_DISCOUNT_BY_VALUE,
                    'order': CANONICAL_BRIDGE_ORDER,
                },
                'evidence': evidence,
            },
            indent=2,
        )
    )
    (OUT / 'articles.json').write_text(json.dumps({'articles': articles}, indent=2))
    (OUT / 'dashboard.json').write_text(json.dumps({'dashboard': dashboard}, indent=2))
    (OUT / 'json_status.json').write_text(json.dumps(json_status, indent=2))
    (OUT / 'argumentation.json').write_text(json.dumps(argumentation, indent=2))
    (OUT / 'annotations.json').write_text(json.dumps(annotations, indent=2))
    (OUT / 'interpretation.json').write_text(json.dumps(interpretation, indent=2))
    (OUT / 'layers.json').write_text(json.dumps(layers, indent=2))
    (OUT / 'workflow.json').write_text(json.dumps(workflow, indent=2))
    (OUT / 'workflow.js').write_text(
        "window.KA_WORKFLOW_PAYLOAD = " + json.dumps(workflow, indent=2) + ";\n",
        encoding='utf-8',
    )
    print('Wrote payloads to', OUT)

if __name__ == '__main__':
    main()
