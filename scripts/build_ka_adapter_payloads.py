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
REGISTRY_DB_PATH = AE / 'data' / 'verification_runs' / 'v7_gold_extraction_registry.db'

if str(AE) not in sys.path:
    sys.path.insert(0, str(AE))

FRONTS_PATH = AE / 'data' / 'rebuild' / 'research_fronts_v5.json'
FRONTS_V7_PATH = AE / 'data' / 'rebuild' / 'research_fronts_v7.json'
CLAIMS_PATH = AE / 'data' / 'rebuild' / 'gold_claims_v7.jsonl'
TOPIC_ONTOLOGY_V1_PATH = AE / 'data' / 'rebuild' / 'topic_ontology_v1.json'
TOPIC_MEMBERSHIPS_V1_PATH = AE / 'data' / 'rebuild' / 'topic_memberships_v1.json'
IV_DV_CLASSIFICATIONS_PATH = AE / 'data' / 'exports' / 'ae_bundle' / 'supplementary' / 'iv_dv_classifications.json'
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
CLAIM_ARG_TARGETS_PATH = AE / 'data' / 'rebuild' / 'claim_argument_search_targets_v1.json'
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

IV_ROOT_LABELS = {
    'spatial': 'Spatial Form',
    'sensory': 'Sensory Conditions',
    'acoustic': 'Acoustic Conditions',
    'luminous': 'Lighting Conditions',
    'natural': 'Natural and Biophilic Conditions',
    'material': 'Material and Surface Conditions',
    'thermal': 'Thermal and Air Conditions',
    'config': 'Configuration and Wayfinding',
    'aesthetic': 'Aesthetic Conditions',
    'person_state': 'Participant State and Expertise',
    'social_spatial': 'Social-Spatial Conditions',
    'cultural': 'Cultural Framing',
    'olfactory': 'Olfactory Conditions',
    'temporal_env': 'Temporal Conditions',
    'unspecified': 'Unspecified Environment',
}

IV_ROOT_DESCRIPTIONS = {
    'spatial': 'Geometric, volumetric, and layout properties of space.',
    'sensory': 'Ambient sensory conditions other than explicit light-spectrum families.',
    'acoustic': 'Noise, soundscape, speech, reverberation, and other sound conditions.',
    'luminous': 'Illuminance, daylight, spectrum, and color-temperature manipulations.',
    'natural': 'Biophilic, vegetation, water, and nature-exposure conditions.',
    'material': 'Materials, finishes, and surface treatments.',
    'thermal': 'Temperature, ventilation, humidity, and thermal comfort conditions.',
    'config': 'Wayfinding, connectivity, privacy, and configurational structure.',
    'aesthetic': 'Order, complexity, visual style, and appearance.',
    'person_state': 'Participant expertise, prior state, and person-level moderation.',
    'social_spatial': 'Social occupancy, territory, and interpersonal spatial conditions.',
    'cultural': 'Cultural framing and interpretive context.',
    'olfactory': 'Smell, scent, and olfactory conditions.',
    'temporal_env': 'Temporal sequencing or time-of-exposure conditions.',
    'unspecified': 'Papers whose current export does not yet provide a stable IV assignment.',
}

DV_ROOT_LABELS = {
    'affect': 'Affect and Stress',
    'cog': 'Cognition and Performance',
    'behav': 'Behavior',
    'health': 'Health and Wellbeing',
    'physio': 'Physiology',
    'neural': 'Neural Activity',
    'performance': 'Performance',
    'person_state': 'Perceived State',
    'spatial': 'Spatial Experience',
    'natural': 'Nature-Related Response',
    'thermal': 'Thermal Response',
    'luminous': 'Lighting-Related Response',
    'acoustic': 'Acoustic Response',
    'social_spatial': 'Social-Spatial Response',
    'mechanism_or_pathway': 'Mechanism or Pathway',
    'study_validity_or_manipulation_check': 'Manipulation Check',
    'unspecified': 'Unspecified Outcome',
}

TAXONOMY_SEGMENT_RE = re.compile(r'[^a-z0-9_]+')
MEASUREMENT_LEAF_TOKENS = {
    'hr', 'hrv', 'heart_rate', 'cortisol', 'eda', 'eda_sc', 'eeg', 'fmri',
    'temperature', 'humidity', 'accuracy', 'reaction_time', 'task', 'self_report',
    'pulseox_physio', 'skin_temp', 'respiration', 'blood_pressure',
}
DV_FOCUS_TOKENS = {
    'stress', 'restorativeness', 'preference', 'wellbeing', 'comfort', 'memory',
    'attention', 'learning', 'navigation', 'wayfinding', 'productivity',
    'soundscape', 'cognitive_load', 'perceived_control', 'place_attachment',
    'health', 'awe', 'fascination', 'restoration', 'mood', 'arousal', 'pain',
}
LOW_INFO_DV_FOCI = {
    'unspecified.outcome',
    'study_validity_or_manipulation_check',
}
LOW_CONFIDENCE_DV_RAW_MARKERS = (
    'study validity or manipulation check',
    'self-report rating',
    'condition or group comparison',
    'between groups',
    'qualitative perception or theme',
)
IV_TEXT_HINTS = [
    ('spatial', ('building', 'buildings', 'architectural', 'architecture', 'urban', 'interior', 'workspace', 'workplace', 'office', 'home', 'restaurant', 'public space', 'spatial', 'space ')),
    ('material', ('material', 'materials', 'surface', 'surfaces', 'haptic', 'touch', 'tactile', 'rough', 'smooth')),
    ('sensory', ('multisensory', 'multi sensory', 'sensory')),
    ('acoustic.reverberation', ('reverberation', 'echo', 'sound absorption')),
    ('acoustic.soundscape', ('soundscape', 'background sound', 'spring water sound', 'birdsong', 'natural sounds')),
    ('acoustic.noise', ('noise', 'white noise', 'pink noise', 'office noise', 'traffic noise', 'speech noise')),
    ('sensory.acoustics', ('acoustic', 'auditory environment', 'sound propagation')),
    ('luminous.color_temp', ('color temperature', 'colour temperature', 'warm light', 'cool light')),
    ('luminous.daylight', ('daylight', 'sunlight', 'natural light', 'daylit')),
    ('sensory.lighting', ('lighting', 'illumination', 'light level', 'illuminance', 'luminance')),
    ('sensory.darkness', ('darkness', 'dim light', 'low light')),
    ('natural.biophilia', ('biophilic', 'biophilia', 'nature imagery', 'natural indoor', 'restorative environment', 'nature exposure')),
    ('natural.vegetation', ('plants', 'plant', 'greenery', 'forest', 'trees', 'bamboo')),
    ('natural.water', ('water', 'coastal', 'river', 'rainfall', 'fountain', 'spring water')),
    ('material.wood', ('wood', 'timber')),
    ('spatial.density', ('crowding', 'density', 'occupancy', 'occupant density')),
    ('spatial.openness', ('open-plan', 'open plan', 'openness', 'enclosure', 'enclosed space')),
    ('spatial.height', ('larger space', 'smaller space', 'ceiling height', 'room height')),
    ('spatial.layout', ('layout', 'floor design', 'floorplan', 'corridor', 'room configuration')),
    ('config.wayfinding', ('wayfinding', 'navigation', 'legibility', 'signage')),
    ('sensory.thermal', ('temperature', 'thermal', 'humidity')),
    ('thermal.ventilation', ('ventilation', 'air quality', 'co2', 'fresh air')),
    ('olfactory', ('odor', 'odour', 'smell', 'scent', 'olfactory')),
    ('aesthetic.order', ('symmetry', 'order', 'ordered')),
    ('aesthetic.complexity', ('visual complexity', 'complexity', 'ornamentation')),
]
DV_TEXT_HINTS = [
    ('affect.negative.stress', ('stress', 'anxiety', 'stai', 'stress scale', 'allostatic', 'arousal')),
    ('affect.restoration', ('restoration', 'restorative', 'recovery')),
    ('person_state.restorativeness', ('restorativeness', 'restorative quality')),
    ('affect.wellbeing', ('well-being', 'wellbeing', 'mental health')),
    ('affect.wellbeing', ('emotion', 'emotions', 'emotional')),
    ('cog.attention', ('attention', 'attentional', 'focus', 'alertness', 'vigilance')),
    ('person_state.cognitive_load', ('cognitive load', 'mental workload', 'workload', 'distractibility')),
    ('performance', ('performance', 'task performance', 'decision-making')),
    ('cog.performance', ('accuracy', 'reaction time', 'response time')),
    ('cog.memory', ('memory', 'recall', 'digit span')),
    ('cog.learning', ('learning', 'learning task')),
    ('cog.creativity.divergent', ('divergent thinking', 'creativity')),
    ('cog.creativity.remote_assoc', ('convergent thinking',)),
    ('cog.spatial.navigation', ('wayfinding', 'navigation')),
    ('affect.preference', ('preference', 'liking')),
    ('affect.satisfaction', ('satisfaction',)),
    ('affect.comfort', ('comfort', 'thermal comfort', 'visual comfort', 'acoustic comfort')),
    ('affect.soundscape', ('soundscape experience', 'emotional experience')),
    ('spatial_behavior.place_attachment', ('place attachment',)),
    ('neural', ('eeg', 'fmri', 'bold', 'ern', 'alpha', 'theta', 'oscillation', 'functional connectivity', 'brain entropy')),
    ('cog.physiology', ('electrodermal', 'eda', 'pulse oximeter', 'heart rate variability', 'hrv', 'heart rate')),
]
THEORETICAL_ARTICLE_TYPES = {'theoretical', 'review_article', 'book'}
THEORY_OVERLAY_MARKERS = (
    'overview', 'review', 'theory', 'framework', 'conceptual', 'approach',
    'introduction', 'seeking common ground', 'way of knowing', 'design',
)
SAFE_TOPIC_EXCLUSION_RE = re.compile(
    r'heisenberg|medical images|psychopathology|fukushima|u\(1\)|developable surface|habit-formation|not for distribution|metamaterials',
    re.I,
)

try:
    from src.services.environment_taxonomy import ENVIRONMENT_HIERARCHY, get_related
except Exception:
    ENVIRONMENT_HIERARCHY = {}

    def get_related(_env_id):
        return []

try:
    from src.services.dv_generalization import DVAccessLevel, get_dv_node
except Exception:
    DVAccessLevel = None

    def get_dv_node(_node_id):
        return None


def slugify(text: str) -> str:
    return ''.join(ch.lower() if ch.isalnum() else '_' for ch in text).strip('_')[:80]


def humanize(text):
    if text in (None, ''):
        return ''
    if isinstance(text, (int, float)):
        return str(text)
    return str(text).replace('theory_', '').replace('_', ' ').replace('.', ' ').strip().title()


def clean_topic_candidate(value):
    text = ' '.join(str(value or '').split()).strip()
    if not text:
        return ''
    lowered = text.lower()
    if lowered in {'unknown', 'claim'}:
        return ''
    if len(text) > 96:
        return ''
    if text.count(' ') > 10 and not any(marker in lowered for marker in ['theory', 'framework', 'model']):
        return ''
    if text.startswith('theory_') or '_' in text:
        text = text.replace('theory_', '').replace('_', ' ')
    return text.strip()


def canonical_warrant_display(value):
    token = str(value or '').strip().lower()
    if not token:
        return 'Unknown'
    label = humanize(token)
    return label.replace('Theory Derived', 'Theory-Derived')


def split_csvish(text):
    return [part.strip() for part in str(text or '').split(',') if part.strip()]


def normalize_taxonomy_id(value):
    raw = str(value or '').strip()
    if not raw:
        return ''
    lowered = raw.lower()
    if lowered in {'n/a', 'na', 'none', 'unknown', 'null'}:
        return ''
    parts = []
    for segment in raw.split('.'):
        token = TAXONOMY_SEGMENT_RE.sub('_', segment.lower()).strip('_')
        if not token or len(token) > 32:
            return ''
        parts.append(token)
    if not parts or len(parts) > 5:
        return ''
    return '.'.join(parts)


def iv_root_label(root_id):
    return IV_ROOT_LABELS.get(root_id, humanize(root_id or 'Unspecified'))


def iv_root_description(root_id):
    if root_id in IV_ROOT_DESCRIPTIONS:
        return IV_ROOT_DESCRIPTIONS[root_id]
    if root_id in ENVIRONMENT_HIERARCHY:
        return ENVIRONMENT_HIERARCHY.get(root_id, {}).get('_description') or ''
    return ''


def dv_root_label(root_id):
    return DV_ROOT_LABELS.get(root_id, humanize(root_id or 'Unspecified'))


def iv_node_label(node_id):
    node = str(node_id or '').strip()
    if not node:
        return 'Unspecified Environment'
    if node == 'unspecified.environment':
        return 'Unspecified Environment'
    parts = node.split('.')
    if len(parts) == 1:
        return iv_root_label(parts[0])
    return humanize(parts[-1])


def dv_focus_label(node_id):
    node = str(node_id or '').strip()
    if not node:
        return 'Unspecified Outcome'
    if node == 'unspecified.outcome':
        return 'Unspecified Outcome'
    dv_node = get_dv_node(node)
    if dv_node and getattr(dv_node, 'label', None):
        return dv_node.label
    return humanize(node.split('.')[-1])


def canonical_iv_node(raw_value):
    node_id = normalize_taxonomy_id(raw_value)
    if not node_id:
        return 'unspecified.environment'
    return node_id


def canonical_iv_root(node_id):
    value = str(node_id or 'unspecified.environment').strip()
    if not value:
        return 'unspecified'
    return value.split('.')[0]


def canonical_dv_node(raw_value):
    node_id = normalize_taxonomy_id(raw_value)
    if not node_id:
        return 'unspecified.outcome'
    return node_id


def canonical_dv_focus(raw_value):
    node_id = canonical_dv_node(raw_value)
    if node_id == 'unspecified.outcome':
        return node_id

    dv_node = get_dv_node(node_id)
    if dv_node and DVAccessLevel is not None:
        access_level = getattr(dv_node, 'access_level', None)
        parent_id = getattr(dv_node, 'parent_id', None)
        if access_level != DVAccessLevel.UNSPECIFIED and parent_id:
            return parent_id
        return node_id

    parts = node_id.split('.')
    for index, segment in enumerate(parts):
        if segment in DV_FOCUS_TOKENS:
            return '.'.join(parts[:index + 1])
    if parts[-1] in MEASUREMENT_LEAF_TOKENS and len(parts) > 1:
        return '.'.join(parts[:-1])
    if len(parts) >= 4:
        return '.'.join(parts[:3])
    return node_id


def canonical_dv_root(node_id):
    value = str(node_id or 'unspecified.outcome').strip()
    if not value:
        return 'unspecified'
    return value.split('.')[0]


def topic_display_label(iv_node, dv_focus):
    return f"{iv_node_label(iv_node)} -> {dv_focus_label(dv_focus)}"


def topic_iv_focus(node_id):
    node = canonical_iv_node(node_id)
    if node == 'unspecified.environment':
        return node
    parts = node.split('.')
    if len(parts) >= 2:
        return '.'.join(parts[:2])
    return node


def topic_text_blob(article):
    return ' '.join(
        str(part or '')
        for part in [
            article.get('title'),
            article.get('abstract'),
            article.get('main_conclusion'),
            article.get('primary_topic'),
            ' '.join(article.get('theories') or []),
            ' '.join(article.get('constructs') or []),
            ' '.join(article.get('instruments') or []),
            article.get('sensor_summary'),
        ]
    ).lower()


def infer_nodes_from_text(text, patterns, weight=1.0):
    out = Counter()
    haystack = str(text or '').lower()
    if not haystack:
        return out
    for node_id, hints in patterns:
        for hint in hints:
            if hint in haystack:
                out[node_id] += weight
    return out


def row_iv_scores(row, article):
    scores = Counter()
    node_id = topic_iv_focus(row.get('iv_node_id'))
    if node_id != 'unspecified.environment':
        scores[node_id] += 1.25 + (0.1 * node_id.count('.'))
    scores.update(infer_nodes_from_text(row.get('iv_raw') or '', IV_TEXT_HINTS, 1.6))
    if not scores:
        scores.update(infer_nodes_from_text(article.get('title') or '', IV_TEXT_HINTS, 0.9))
    return scores


def row_dv_scores(row, article):
    scores = Counter()
    raw_value = str(row.get('dv_raw') or '').lower()
    focus = canonical_dv_focus(row.get('dv_node_id'))
    if focus not in LOW_INFO_DV_FOCI and not any(marker in raw_value for marker in LOW_CONFIDENCE_DV_RAW_MARKERS):
        scores[focus] += 1.2 + (0.1 * focus.count('.'))
    scores.update(infer_nodes_from_text(raw_value, DV_TEXT_HINTS, 1.6))
    if not scores:
        scores.update(infer_nodes_from_text(article.get('title') or '', DV_TEXT_HINTS, 0.9))
    return scores


def article_iv_scores(article):
    scores = Counter()
    scores.update(infer_nodes_from_text(article.get('title') or '', IV_TEXT_HINTS, 1.0))
    scores.update(infer_nodes_from_text(article.get('abstract') or '', IV_TEXT_HINTS, 0.6))
    scores.update(infer_nodes_from_text(article.get('main_conclusion') or '', IV_TEXT_HINTS, 0.5))
    return Counter({topic_iv_focus(node): score for node, score in scores.items() if topic_iv_focus(node) != 'unspecified.environment'})


def article_dv_scores(article):
    scores = Counter()
    scores.update(infer_nodes_from_text(article.get('title') or '', DV_TEXT_HINTS, 1.0))
    scores.update(infer_nodes_from_text(article.get('abstract') or '', DV_TEXT_HINTS, 0.6))
    scores.update(infer_nodes_from_text(article.get('main_conclusion') or '', DV_TEXT_HINTS, 0.5))
    sensor_text = str(article.get('sensor_summary') or '').lower()
    if 'eeg' in sensor_text or 'fmri' in sensor_text:
        scores['neural'] += 0.8
    if any(token in sensor_text for token in ('heart rate', 'hrv', 'electrodermal', 'eda', 'cortisol')):
        scores['affect.negative.stress'] += 0.6
    return Counter({node: score for node, score in scores.items() if node not in LOW_INFO_DV_FOCI})


def choose_topic_pairs_for_article(article, rows_for_paper):
    iv_scores = Counter()
    dv_scores = Counter()
    pair_scores = Counter()

    for row in rows_for_paper:
        iv_row = row_iv_scores(row, article)
        dv_row = row_dv_scores(row, article)
        iv_scores.update(iv_row)
        dv_scores.update(dv_row)
        if iv_row and dv_row:
            best_iv, best_iv_score = iv_row.most_common(1)[0]
            best_dv, best_dv_score = dv_row.most_common(1)[0]
            if best_iv != 'unspecified.environment' and best_dv not in LOW_INFO_DV_FOCI:
                pair_scores[(best_iv, best_dv)] += min(best_iv_score, best_dv_score)

    iv_scores.update(article_iv_scores(article))
    dv_scores.update(article_dv_scores(article))

    overlay_text = topic_text_blob(article)
    if not any(node not in LOW_INFO_DV_FOCI for node in dv_scores):
        if any(marker in overlay_text for marker in THEORY_OVERLAY_MARKERS):
            dv_scores['mechanism_or_pathway'] += 1.1

    if not pair_scores:
        best_ivs = [node for node, _ in iv_scores.most_common(2) if node != 'unspecified.environment']
        best_dvs = [node for node, _ in dv_scores.most_common(3) if node not in LOW_INFO_DV_FOCI]
        for iv_node in best_ivs[:2]:
            for dv_node in best_dvs[:2]:
                pair_scores[(iv_node, dv_node)] += 0.75 + 0.1 * iv_scores[iv_node] + 0.1 * dv_scores[dv_node]

    ranked_pairs = []
    for (iv_node, dv_node), pair_score in pair_scores.items():
        if iv_node == 'unspecified.environment' or dv_node in LOW_INFO_DV_FOCI:
            continue
        quality = pair_score + (0.15 * iv_scores.get(iv_node, 0)) + (0.15 * dv_scores.get(dv_node, 0))
        ranked_pairs.append((iv_node, dv_node, quality))

    ranked_pairs.sort(key=lambda row: (-row[2], row[0], row[1]))

    memberships = []
    if ranked_pairs:
        top_score = ranked_pairs[0][2]
        for iv_node, dv_node, score in ranked_pairs:
            if len(memberships) >= 3:
                break
            if score < max(0.9, top_score * 0.55):
                continue
            memberships.append((iv_node, dv_node, score))

    visible = bool(memberships)
    missing_iv = not any(node != 'unspecified.environment' for node in iv_scores)
    missing_dv = not any(node not in LOW_INFO_DV_FOCI for node in dv_scores)
    if not visible:
        missing_iv = True if not iv_scores else missing_iv
        missing_dv = True if not dv_scores else missing_dv

    return {
        'memberships': memberships,
        'iv_scores': iv_scores,
        'dv_scores': dv_scores,
        'missing_iv': missing_iv,
        'missing_dv': missing_dv,
    }


def should_exclude_from_topic_view(article, missing_iv, missing_dv):
    if not (missing_iv and missing_dv):
        return False
    title = str(article.get('title') or '')
    if SAFE_TOPIC_EXCLUSION_RE.search(title):
        return True
    article_type = str(article.get('article_type') or '').strip().lower()
    if article_type == 'not_applicable' and int(article.get('claim_count') or 0) <= 1:
        return True
    return False


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
    label = (front.get('label') or front.get('title') or front.get('name') or '').lower()
    theories = ' '.join(front.get('shared_theories') or front.get('theories') or []).lower()
    constructs = ' '.join(
        front.get('shared_constructs')
        or front.get('topic_ids')
        or front.get('dominant_iv_families')
        or front.get('dominant_dv_families')
        or []
    ).lower()
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


def load_front_records():
    payload = load_json(FRONTS_V7_PATH if FRONTS_V7_PATH.exists() else FRONTS_PATH, {})
    if isinstance(payload, list):
        return payload
    return payload.get('fronts') or payload.get('research_fronts') or payload.get('items') or []


def load_paper_belief_score_lookup():
    lookup = {}
    if not REBUILD_DB_PATH.exists():
        return lookup
    conn = sqlite3.connect(REBUILD_DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            paper_id,
            AVG(credence_value) AS mean_credence,
            AVG(CAST(json_extract(omega_json, '$.omega') AS REAL)) AS mean_omega,
            COUNT(*) AS belief_count
        FROM beliefs
        WHERE paper_id IS NOT NULL AND TRIM(paper_id) != ''
        GROUP BY paper_id
        """
    )
    for paper_id, mean_credence, mean_omega, belief_count in cur.fetchall():
        key = str(paper_id or '').strip()
        if not key:
            continue
        lookup[key] = {
            'mean_credence': float(mean_credence or 0.0),
            'mean_omega': float(mean_omega or 0.0),
            'belief_count': int(belief_count or 0),
        }
    conn.close()
    return lookup


PAPER_BELIEF_SCORE_LOOKUP = load_paper_belief_score_lookup()


def summarize_front(front):
    label = front.get('label') or front.get('title') or front.get('name') or front.get('front_id') or 'Unlabeled front'
    cat = classify_front(front)
    paper_rows = front.get('papers') or front.get('paper_ids') or []
    size = int(front.get('size') or len(paper_rows))
    papers = [str(paper_id).strip() for paper_id in paper_rows if str(paper_id).strip()]
    mean_credence = float(front.get('mean_credence') or 0.0)
    mean_omega = float(front.get('mean_omega') or front.get('mean_warrant') or 0.0)
    if papers and (mean_credence <= 0.0 or mean_omega <= 0.0):
        credence_values = []
        omega_values = []
        for paper_id in papers:
            score_row = PAPER_BELIEF_SCORE_LOOKUP.get(paper_id)
            if not score_row:
                continue
            if score_row.get('mean_credence'):
                credence_values.append(float(score_row['mean_credence']))
            if score_row.get('mean_omega'):
                omega_values.append(float(score_row['mean_omega']))
        if credence_values and mean_credence <= 0.0:
            mean_credence = sum(credence_values) / len(credence_values)
        if omega_values and mean_omega <= 0.0:
            mean_omega = sum(omega_values) / len(omega_values)
    voi = round(float(mean_omega or mean_credence or 0.0), 3)
    shared_theories = [
        token.replace('theory_', '').replace('_', ' ')
        for token in (front.get('shared_theories') or front.get('theories') or [])
        if str(token).strip()
    ]
    shared_constructs = [
        token.replace('.', ' ').replace('_', ' ')
        for token in (
            front.get('shared_constructs')
            or front.get('topic_ids')
            or front.get('dominant_iv_families')
            or front.get('dominant_dv_families')
            or []
        )
        if str(token).strip()
    ]
    desc_bits = []
    if shared_theories:
        desc_bits.append('Theories: ' + ', '.join(shared_theories[:3]))
    if shared_constructs:
        desc_bits.append('Constructs: ' + ', '.join(shared_constructs[:4]))
    desc_bits.append(f"Maturity: {front.get('maturity', front.get('maturity_label', 'unknown'))}.")
    desc = ' '.join(desc_bits) if desc_bits else 'Research front from the current rebuild.'
    return {
        'id': front.get('front_id') or slugify(label),
        'cat': cat,
        'n': size,
        'voi': voi,
        'name': label,
        'desc': desc,
        'maturity': front.get('maturity', front.get('maturity_label', 'unknown')),
        'mean_credence': round(mean_credence, 3),
        'mean_omega': round(mean_omega, 3),
        'shared_theories': shared_theories,
        'shared_constructs': shared_constructs,
        'contradictions': int(front.get('n_contradictions') or front.get('contradiction_count') or 0),
        'replications': int(front.get('n_replications') or front.get('replication_count') or 0),
        'paper_ids': papers,
    }


def load_fronts():
    fronts = load_front_records()
    topic_payload = []
    gap_payload = []
    unique_papers = set()
    for front in fronts:
        topic = summarize_front(front)
        label = topic['name']
        size = topic['n']
        voi = round(float(topic.get('voi') or 0.0), 2)
        unique_papers.update(topic.get('paper_ids') or [])
        topic_payload.append(topic)
        if size <= 8 or front.get('maturity') != 'established' or int(front.get('n_contradictions') or 0) > 0:
            if voi >= 0.7:
                voi_label = 'high'
            elif voi >= 0.45:
                voi_label = 'medium'
            else:
                voi_label = 'low'
            gap_type = 'untested' if size <= 8 else 'conflict' if int(front.get('n_contradictions') or 0) > 0 else 'credence'
            gap_payload.append({
                'id': topic['id'],
                'type': gap_type,
                'title': label,
                'description': topic['desc'],
                'construct': slugify(((topic.get('shared_constructs') or [topic['cat']])[0]).replace('.', ' ')),
                'context': 'multiple',
                'voi': voi_label,
                'credence': voi,
                'whyMatters': f"This front remains strategically important because its current maturity is {front.get('maturity', 'unknown')} with corpus size {size}.",
                'hypothesisBuild': f"ka_hypothesis_builder.html?front={front.get('front_id')}",
                'evidenceLink': f"ka_evidence.html?front={front.get('front_id')}"
            })
    topic_payload.sort(key=lambda x: (-x['voi'], -x['n'], x['name']))
    gap_payload.sort(key=lambda x: ({'high':0,'medium':1,'low':2}[x['voi']], x['title']))
    return topic_payload, gap_payload, {
        'front_count': len(topic_payload),
        'unique_paper_count': len(unique_papers),
        'front_source': 'research_fronts_v7' if FRONTS_V7_PATH.exists() else 'research_fronts_v5',
    }


def build_front_membership(fronts):
    paper_to_fronts = defaultdict(list)
    for front in fronts:
        summary = summarize_front(front)
        article_front = {
            'id': summary['id'],
            'name': summary['name'],
            'cat': summary['cat'],
            'voi': summary['voi'],
            'n': summary['n'],
            'maturity': summary['maturity'],
            'mean_credence': summary.get('mean_credence') or 0.0,
            'mean_omega': summary.get('mean_omega') or 0.0,
            'contradictions': summary['contradictions'],
            'replications': summary['replications'],
            'shared_theories': list(summary.get('shared_theories') or [])[:6],
            'shared_constructs': list(summary.get('shared_constructs') or [])[:6],
        }
        for paper_id in summary.get('paper_ids') or []:
            paper_to_fronts[paper_id].append(article_front)
    for fronts_for_paper in paper_to_fronts.values():
        fronts_for_paper.sort(key=lambda row: (-(row.get('voi') or 0), -(row.get('n') or 0), row.get('name') or ''))
    return dict(paper_to_fronts)


def load_registry_lookup():
    lookup = {}
    if not REGISTRY_DB_PATH.exists():
        return lookup
    conn = sqlite3.connect(REGISTRY_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    for row in cur.execute(
        """
        SELECT
            paper_id,
            has_figures,
            has_tables,
            has_stimuli,
            has_experimental_context_images,
            has_sensor_data,
            sensor_summary,
            crop_needed,
            crop_status,
            package_root,
            package_json_path,
            pdf_path,
            ocr_path,
            mathpix_path,
            pageimages_200_path
        FROM gold_papers
        WHERE accepted_for_rebuild = 1
        """
    ):
        paper_id = str(row['paper_id'] or '').strip()
        if not paper_id:
            continue
        lookup[paper_id] = {
            'has_sensor_data': bool(row['has_sensor_data']),
            'sensor_summary': compact_text(row['sensor_summary'] or '', 220),
            'asset_profile': {
                'has_figures': bool(row['has_figures']),
                'has_tables': bool(row['has_tables']),
                'has_stimuli': bool(row['has_stimuli']),
                'has_experimental_context_images': bool(row['has_experimental_context_images']),
                'crop_needed': bool(row['crop_needed']),
                'crop_status': row['crop_status'] or '',
            },
            'source_bundle': {
                'package_root': row['package_root'] or '',
                'package_json_path': row['package_json_path'] or '',
                'pdf_path': row['pdf_path'] or '',
                'ocr_path': row['ocr_path'] or '',
                'mathpix_path': row['mathpix_path'] or '',
                'pageimages_200_path': row['pageimages_200_path'] or '',
            },
        }
    conn.close()
    return lookup


def _argumentation_paper_summary():
    return {
        'claim_count': 0,
        'direct_support_edges': 0,
        'direct_attack_edges': 0,
        'incoming_support_total': 0,
        'incoming_attack_total': 0,
        'contested_claim_count': 0,
        'defeated_claim_count': 0,
        'dominant_stance': '',
        'theories': [],
        'top_attack_schemes': [],
        'search_target_count': 0,
        'top_search_targets': [],
    }


def load_argumentation_indexes():
    paper_graph = load_json(ARG_GRAPH_PATH, {})
    claim_graph = load_json(CLAIM_ARG_GRAPH_PATH, {})
    targets_payload = load_json(CLAIM_ARG_TARGETS_PATH, {})

    paper_nodes_raw = paper_graph.get('nodes') or {}
    paper_nodes = list(paper_nodes_raw.values()) if isinstance(paper_nodes_raw, dict) else list(paper_nodes_raw)
    claim_nodes_raw = claim_graph.get('nodes') or {}
    claim_nodes = list(claim_nodes_raw.values()) if isinstance(claim_nodes_raw, dict) else list(claim_nodes_raw)

    paper_index = {}
    belief_index = {}
    claim_node_by_id = {}
    paper_targets = defaultdict(list)
    belief_targets = {}
    belief_attacks = defaultdict(list)
    belief_supports = defaultdict(list)
    attack_scheme_counts = Counter()

    for node in paper_nodes:
        paper_id = str(node.get('paper_id') or node.get('belief_id') or '').strip()
        if not paper_id:
            continue
        paper_index[paper_id] = {
            **_argumentation_paper_summary(),
            'claim_count': int(node.get('claim_count') or 0),
            'dominant_stance': node.get('dominant_stance') or '',
            'theories': list(node.get('theories') or [])[:8],
        }

    for node in claim_nodes:
        belief_id = str(node.get('belief_id') or '').strip()
        paper_id = str(node.get('paper_id') or '').strip()
        if not belief_id or not paper_id:
            continue
        claim_node_by_id[belief_id] = node
        summary = paper_index.setdefault(paper_id, _argumentation_paper_summary())
        support_count = int(node.get('incoming_support_count') or 0)
        attack_count = int(node.get('incoming_attack_count') or 0)
        summary['incoming_support_total'] += support_count
        summary['incoming_attack_total'] += attack_count
        if attack_count > 0:
            summary['contested_claim_count'] += 1
        if str(node.get('warrant_status') or '').upper() == 'DEFEATED':
            summary['defeated_claim_count'] += 1
        belief_index[belief_id] = {
            'belief_id': belief_id,
            'paper_id': paper_id,
            'content_preview': compact_text(node.get('content_preview') or node.get('content') or '', 220),
            'incoming_support_count': support_count,
            'incoming_attack_count': attack_count,
            'qualifier': node.get('qualifier') or node.get('node_qualifier') or '',
            'warrant_status': node.get('warrant_status') or '',
            'defeat_type': node.get('defeat_type') or '',
            'claim_type': node.get('claim_type') or '',
            'article_family': node.get('article_family') or '',
            'direction_of_effect': node.get('direction_of_effect') or '',
        }

    for target in targets_payload.get('targets') or []:
        belief_id = str(target.get('belief_id') or '').strip()
        paper_id = str(target.get('paper_id') or '').strip()
        if not belief_id or not paper_id:
            continue
        target_row = {
            'belief_id': belief_id,
            'paper_id': paper_id,
            'warrant_status': target.get('warrant_status') or '',
            'target_kind': target.get('target_kind') or '',
            'priority_score': float(target.get('priority_score') or 0.0),
            'review_urgency': target.get('review_urgency') or '',
            'conflict_count': int(target.get('conflict_count') or 0),
            'support_count': int(target.get('support_count') or 0),
            'defeat_types': list(target.get('defeat_types') or []),
            'attack_scheme_hints': list(target.get('attack_scheme_hints') or []),
            'resolution_question': compact_text(target.get('resolution_question') or '', 240),
            'search_query': compact_text(target.get('search_query') or '', 240),
            'reason': compact_text(target.get('reason') or '', 180),
        }
        belief_targets[belief_id] = target_row
        paper_targets[paper_id].append(target_row)

    attack_examples = []
    for edge in claim_graph.get('edges') or []:
        target_id = str(edge.get('target') or '').strip()
        source_id = str(edge.get('source') or '').strip()
        relation = str(edge.get('relation') or '').strip().lower()
        target_node = claim_node_by_id.get(target_id, {})
        source_node = claim_node_by_id.get(source_id, {})
        target_paper_id = str(target_node.get('paper_id') or '').strip()
        if target_paper_id:
            paper_index.setdefault(target_paper_id, _argumentation_paper_summary())
            if relation == 'attack':
                paper_index[target_paper_id]['direct_attack_edges'] += 1
            elif relation == 'support':
                paper_index[target_paper_id]['direct_support_edges'] += 1
        example = {
            'source': source_id,
            'target': target_id,
            'source_paper_id': str(source_node.get('paper_id') or '').strip(),
            'target_paper_id': target_paper_id,
            'source_preview': compact_text(source_node.get('content_preview') or source_node.get('content') or '', 160),
            'target_preview': compact_text(target_node.get('content_preview') or target_node.get('content') or '', 160),
            'scheme_hint': edge.get('scheme_hint') or '',
            'qualifier': edge.get('qualifier') or '',
            'defeat_type': edge.get('defeat_type') or '',
            'strength': round(float(edge.get('strength') or 0.0), 3),
            'critical_question_hints': list(edge.get('critical_question_hints') or [])[:3],
        }
        if relation == 'attack':
            attack_scheme_counts[example['scheme_hint'] or 'unspecified_attack'] += 1
            attack_examples.append(example)
            belief_attacks[target_id].append(example)
        elif relation == 'support':
            belief_supports[target_id].append(example)

    for paper_id, targets in paper_targets.items():
        targets.sort(key=lambda row: (-(row.get('priority_score') or 0), row.get('belief_id') or ''))
        scheme_counter = Counter()
        for row in targets:
            for hint in row.get('attack_scheme_hints') or []:
                scheme_counter[hint] += 1
        summary = paper_index.setdefault(paper_id, _argumentation_paper_summary())
        summary['search_target_count'] = len(targets)
        summary['top_search_targets'] = targets[:3]
        summary['top_attack_schemes'] = [name for name, _ in scheme_counter.most_common(3)]

    attack_examples.sort(key=lambda row: (-row['strength'], row['target']))
    return {
        'paper_graph': paper_graph,
        'claim_graph': claim_graph,
        'paper_nodes': paper_nodes,
        'claim_nodes': claim_nodes,
        'paper_index': paper_index,
        'belief_index': belief_index,
        'belief_targets': belief_targets,
        'paper_targets': dict(paper_targets),
        'belief_attacks': dict(belief_attacks),
        'belief_supports': dict(belief_supports),
        'attack_scheme_counts': attack_scheme_counts,
        'attack_examples': attack_examples,
    }


def build_related_papers(articles):
    for article in articles:
        primary_front = (article.get('primary_front') or {}).get('id')
        front_ids = {front.get('id') for front in (article.get('fronts') or []) if front.get('id')}
        theories = {str(value).lower() for value in (article.get('theories') or []) if str(value).strip()}
        constructs = {str(value).lower() for value in (article.get('constructs') or []) if str(value).strip()}
        instruments = {str(value).lower() for value in (article.get('instruments') or []) if str(value).strip()}
        candidates = []
        for other in articles:
            if other.get('paper_id') == article.get('paper_id'):
                continue
            score = 0
            reasons = []
            other_primary_front = (other.get('primary_front') or {}).get('id')
            other_front_ids = {front.get('id') for front in (other.get('fronts') or []) if front.get('id')}
            shared_fronts = front_ids & other_front_ids
            if primary_front and other_primary_front and primary_front == other_primary_front:
                score += 4
                reasons.append((article.get('primary_front') or {}).get('name') or 'shared front')
            elif shared_fronts:
                score += 2 * len(shared_fronts)
                reasons.append('shared research front')
            shared_theories = theories & {str(value).lower() for value in (other.get('theories') or []) if str(value).strip()}
            if shared_theories:
                score += min(2, len(shared_theories))
                reasons.append('shared theory')
            shared_constructs = constructs & {str(value).lower() for value in (other.get('constructs') or []) if str(value).strip()}
            if shared_constructs:
                score += min(2, len(shared_constructs))
                reasons.append('shared construct')
            shared_instruments = instruments & {str(value).lower() for value in (other.get('instruments') or []) if str(value).strip()}
            if shared_instruments:
                score += 1
                reasons.append('shared instrument')
            if article.get('has_sensor_data') and other.get('has_sensor_data'):
                score += 1
                reasons.append('sensor-rich method family')
            if score <= 0:
                continue
            candidates.append({
                'paper_id': other.get('paper_id'),
                'title': other.get('title'),
                'score': score,
                'reason': ', '.join(dict.fromkeys(reasons)),
                'primary_front': (other.get('primary_front') or {}).get('name') or '',
            })
        candidates.sort(key=lambda row: (-row['score'], row['paper_id']))
        article['related_papers'] = candidates[:4]
    return articles


def parse_claims():
    evidence = []
    paper_claims = defaultdict(list)
    paper_meta = {}
    belief_lookup = load_rebuild_belief_lookup()
    front_membership = build_front_membership(load_front_records())
    registry_lookup = load_registry_lookup()
    argumentation = load_argumentation_indexes()
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
            paper_fronts = front_membership.get(pid) or []
            primary_front = paper_fronts[0] if paper_fronts else {}
            registry_row = registry_lookup.get(pid, {})
            belief_arg = argumentation['belief_index'].get(belief_id, {})
            target_row = argumentation['belief_targets'].get(belief_id, {})
            primary_topic = (
                primary_front.get('name')
                or clean_topic_candidate(construct_label)
                or clean_topic_candidate((paper_meta[pid].get('theories') or [''])[0])
                or humanize(obj.get('article_type') or 'Paper')
            )
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
                'citation': (
                    paper_meta[pid].get('apa_citation')
                    or format_apa_citation(paper_meta[pid].get('authors'), paper_meta[pid].get('year'), paper_meta[pid].get('title'), paper_meta[pid].get('doi'))
                    or pid
                ),
                'paper_title': paper_meta[pid].get('title') or pid,
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
                'front_id': primary_front.get('id') or '',
                'primary_front': primary_front.get('name') or '',
                'primary_topic': primary_topic,
                'fronts': [front.get('name') for front in paper_fronts[:3]],
                'has_sensor_data': bool(registry_row.get('has_sensor_data')),
                'sensor_summary': registry_row.get('sensor_summary') or '',
                'support_count': int(belief_arg.get('incoming_support_count') or 0),
                'attack_count': int(belief_arg.get('incoming_attack_count') or 0),
                'qualifier': belief_arg.get('qualifier') or '',
                'warrant_status': belief_arg.get('warrant_status') or '',
                'defeat_type': belief_arg.get('defeat_type') or '',
                'resolution_question': target_row.get('resolution_question') or '',
                'review_urgency': target_row.get('review_urgency') or '',
                'search_query': target_row.get('search_query') or '',
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
        top_theories = [
            clean_topic_candidate(t)
            for t, _ in theory_counter.most_common(6)
            if clean_topic_candidate(t)
        ][:4]
        top_constructs = [humanize(t) for t, _ in construct_counter.most_common(4) if t]
        top_measures = [humanize(t) for t, _ in measure_counter.most_common(3) if t]
        representative = claims[0] if claims else {}
        representative_result = representative.get('structured_result_row') or {}
        paper_fronts = front_membership.get(pid) or []
        primary_front = paper_fronts[0] if paper_fronts else {}
        registry_row = registry_lookup.get(pid, {})
        paper_arg = dict(argumentation['paper_index'].get(pid, _argumentation_paper_summary()))
        paper_arg['claim_count'] = len(claims)
        paper_arg['theories'] = [
            value.replace('theory_', '').replace('_', ' ')
            for value in (paper_arg.get('theories') or [])
            if str(value).strip()
        ][:6]
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
        primary_topic = primary_front.get('name') or (top_constructs[0] if top_constructs else (top_theories[0] if top_theories else humanize(meta.get('article_type') or 'Paper')))
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
            'fronts': paper_fronts[:4],
            'primary_front': primary_front,
            'primary_topic': primary_topic,
            'has_sensor_data': bool(registry_row.get('has_sensor_data')),
            'sensor_summary': registry_row.get('sensor_summary') or '',
            'asset_profile': registry_row.get('asset_profile') or {},
            'source_bundle': registry_row.get('source_bundle') or {},
            'argumentation_summary': paper_arg,
            'search_targets': list(paper_arg.get('top_search_targets') or []),
            'related_papers': [],
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
    articles = build_related_papers(articles)
    return evidence, articles


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


def load_iv_dv_classifications():
    payload = load_json(IV_DV_CLASSIFICATIONS_PATH, [])
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return payload.get('classifications') or payload.get('rows') or payload.get('items') or []
    return []


def _first_list(payload, *keys):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return list(value.values())
    return []


def _normalize_str_list(values):
    output = []
    seen = set()
    for value in values or []:
        if isinstance(value, dict):
            text = (
                value.get('name')
                or value.get('label')
                or value.get('title')
                or value.get('id')
                or ''
            )
        else:
            text = value
        text = compact_text(text or '', 160)
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(text)
    return output


def _normalize_cross_relations(values):
    rows = []
    for value in values or []:
        if not isinstance(value, dict):
            continue
        target_id = str(
            value.get('target_id')
            or value.get('topic_id')
            or value.get('id')
            or ''
        ).strip()
        target_label = (
            value.get('target_label')
            or value.get('label')
            or value.get('name')
            or target_id
        )
        if not target_id:
            continue
        rows.append(
            {
                'target_id': target_id,
                'target_label': compact_text(target_label or target_id, 120),
                'kind': value.get('kind') or value.get('relation_kind') or '',
                'label': compact_text(value.get('label') or value.get('reason') or '', 140),
                'score': round(float(value.get('score') or value.get('weight') or 0.0), 3),
                'paper_count': int(value.get('paper_count') or 0),
                'shared_theories': _normalize_str_list(value.get('shared_theories') or []),
                'shared_sensors': _normalize_str_list(value.get('shared_sensors') or []),
            }
        )
    return rows


def _load_canonical_topic_artifacts():
    if not (TOPIC_ONTOLOGY_V1_PATH.exists() and TOPIC_MEMBERSHIPS_V1_PATH.exists()):
        return None, None
    return load_json(TOPIC_ONTOLOGY_V1_PATH, {}), load_json(TOPIC_MEMBERSHIPS_V1_PATH, {})


def _extract_topic_nodes(ontology_payload):
    rows = _first_list(ontology_payload, 'topic_nodes', 'topics', 'nodes', 'items')
    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        topic_id = str(row.get('id') or row.get('topic_id') or row.get('node_id') or '').strip()
        if not topic_id:
            continue
        iv_root = str(
            row.get('iv_root')
            or row.get('iv_root_id')
            or row.get('iv_family')
            or row.get('dominant_iv_family')
            or 'unspecified'
        ).strip() or 'unspecified'
        iv_node = str(
            row.get('iv_node')
            or row.get('iv_branch')
            or row.get('iv_branch_id')
            or row.get('dominant_iv_branch')
            or iv_root
        ).strip() or iv_root
        dv_root = str(
            row.get('dv_root')
            or row.get('dv_root_id')
            or row.get('dv_family')
            or row.get('dominant_dv_family')
            or 'unspecified'
        ).strip() or 'unspecified'
        dv_focus = str(
            row.get('dv_focus')
            or row.get('dv_node')
            or row.get('dv_branch')
            or row.get('dv_branch_id')
            or row.get('dominant_dv_focus')
            or 'unspecified.outcome'
        ).strip() or 'unspecified.outcome'
        normalized.append(
            {
                'id': topic_id,
                'label': compact_text(
                    row.get('label') or row.get('name') or row.get('title') or topic_id,
                    140,
                ),
                'iv_root': iv_root,
                'iv_root_label': row.get('iv_root_label') or row.get('iv_family_label') or iv_root_label(iv_root),
                'iv_root_description': row.get('iv_root_description') or row.get('iv_family_description') or iv_root_description(iv_root),
                'iv_node': iv_node,
                'iv_label': row.get('iv_label') or row.get('iv_branch_label') or iv_node_label(iv_node),
                'dv_root': dv_root,
                'dv_root_label': row.get('dv_root_label') or row.get('dv_family_label') or dv_root_label(dv_root),
                'dv_focus': dv_focus,
                'dv_focus_label': row.get('dv_focus_label') or row.get('dv_label') or dv_focus_label(dv_focus),
                'theories': _normalize_str_list(row.get('theories') or row.get('shared_theories') or []),
                'sensors': _normalize_str_list(row.get('sensors') or row.get('shared_sensors') or []),
                'fronts': _normalize_str_list(row.get('fronts') or row.get('research_fronts') or []),
                'cross_relations': _normalize_cross_relations(row.get('cross_relations') or row.get('relations') or []),
                'raw': row,
            }
        )
    return normalized


def _extract_membership_rows(membership_payload):
    rows = _first_list(membership_payload, 'memberships', 'paper_topic_memberships', 'items')
    if rows:
        flattened = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            topic_ids = row.get('topic_ids')
            if isinstance(topic_ids, list):
                primary_topic_id = str(row.get('primary_topic_id') or '').strip()
                secondary_topic_ids = [str(value).strip() for value in (row.get('secondary_topic_ids') or []) if str(value).strip()]
                for topic_id in topic_ids:
                    topic_id = str(topic_id or '').strip()
                    if not topic_id:
                        continue
                    flattened.append(
                        {
                            'paper_id': row.get('paper_id'),
                            'topic_id': topic_id,
                            'primary': topic_id == primary_topic_id or (not primary_topic_id and topic_id not in secondary_topic_ids),
                            'confidence': row.get('confidence') or row.get('score') or 0.0,
                            'visible': str(row.get('visibility') or '').lower() != 'hidden',
                            'hidden_from_view': str(row.get('visibility') or '').lower() == 'hidden',
                            'repair_reason': row.get('hide_reason') or row.get('repair_reason') or '',
                            'missing_iv': not bool(row.get('iv_roots')),
                            'missing_dv': not bool(row.get('dv_focuses')),
                        }
                    )
                if not topic_ids or str(row.get('visibility') or '').lower() == 'hidden':
                    flattened.append(
                        {
                            'paper_id': row.get('paper_id'),
                            'visible': False,
                            'hidden_from_view': True,
                            'repair_reason': row.get('hide_reason') or row.get('repair_reason') or 'hidden in canonical topic memberships',
                            'missing_iv': not bool(row.get('iv_roots')),
                            'missing_dv': not bool(row.get('dv_focuses')),
                        }
                    )
            else:
                flattened.append(row)
        return flattened
    papers = _first_list(membership_payload, 'papers', 'paper_memberships')
    flattened = []
    for paper in papers:
        if not isinstance(paper, dict):
            continue
        paper_id = str(paper.get('paper_id') or paper.get('id') or '').strip()
        for membership in paper.get('memberships') or []:
            if not isinstance(membership, dict):
                continue
            row = dict(membership)
            row.setdefault('paper_id', paper_id)
            flattened.append(row)
        if paper.get('hidden_from_view') or paper.get('visible') is False:
            flattened.append(
                {
                    'paper_id': paper_id,
                    'visible': False,
                    'repair_reason': paper.get('repair_reason') or paper.get('hidden_reason') or 'hidden in canonical topic memberships',
                    'title': paper.get('title') or '',
                    'year': paper.get('year'),
                }
            )
    return flattened


def _extract_hidden_membership_rows(membership_payload):
    rows = _first_list(membership_payload, 'hidden_papers', 'hidden', 'repair_queue')
    if not rows and isinstance(membership_payload, list):
        rows = [row for row in membership_payload if isinstance(row, dict) and str(row.get('visibility') or '').lower() == 'hidden']
    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        paper_id = str(row.get('paper_id') or row.get('id') or '').strip()
        if not paper_id:
            continue
        normalized.append(
            {
                'paper_id': paper_id,
                'title': row.get('title') or '',
                'year': row.get('year'),
                'repair_reason': row.get('repair_reason') or row.get('hide_reason') or row.get('hidden_reason') or 'hidden in canonical topic memberships',
                'missing_iv': bool(row.get('missing_iv')) or not bool(row.get('iv_roots')),
                'missing_dv': bool(row.get('missing_dv')) or not bool(row.get('dv_focuses')),
            }
        )
    return normalized


def build_topic_hierarchy_from_canonical(articles, topic_summary, ontology_payload, membership_payload):
    topic_nodes = _extract_topic_nodes(ontology_payload)
    if not topic_nodes:
        return None

    article_lookup = {article.get('paper_id'): article for article in articles}
    topic_lookup = {
        node['id']: {
            **node,
            'paper_ids': set(),
            'paper_preview': [],
            'theory_counter': Counter(node.get('theories') or []),
            'sensor_counter': Counter(node.get('sensors') or []),
            'front_counter': Counter(node.get('fronts') or []),
        }
        for node in topic_nodes
    }

    visible_memberships = defaultdict(list)
    hidden_memberships = {row['paper_id']: row for row in _extract_hidden_membership_rows(membership_payload)}
    for row in _extract_membership_rows(membership_payload):
        if not isinstance(row, dict):
            continue
        paper_id = str(row.get('paper_id') or '').strip()
        topic_id = str(row.get('topic_id') or row.get('topic') or row.get('id') or '').strip()
        visible = row.get('visible')
        hidden = bool(row.get('hidden_from_view'))
        if not paper_id:
            continue
        if not topic_id or visible is False or hidden:
            hidden_memberships.setdefault(
                paper_id,
                {
                    'paper_id': paper_id,
                    'title': row.get('title') or '',
                    'year': row.get('year'),
                    'repair_reason': row.get('repair_reason') or row.get('hide_reason') or row.get('hidden_reason') or 'hidden in canonical topic memberships',
                    'missing_iv': bool(row.get('missing_iv')),
                    'missing_dv': bool(row.get('missing_dv')),
                },
            )
            continue
        visible_memberships[paper_id].append(
            {
                'topic_id': topic_id,
                'primary': bool(row.get('primary') or row.get('membership_kind') == 'primary' or row.get('rank') in (0, 1)),
                'confidence': round(float(row.get('confidence') or row.get('score') or 0.0), 3),
            }
        )

    fallback_iv_count = 0
    fallback_dv_count = 0
    repair_queue = []
    exclusion_queue = []

    for article in articles:
        paper_id = article.get('paper_id')
        memberships = visible_memberships.get(paper_id) or []
        if not memberships:
            hidden = hidden_memberships.get(paper_id, {})
            missing_iv = bool(hidden.get('missing_iv'))
            missing_dv = bool(hidden.get('missing_dv'))
            if missing_iv:
                fallback_iv_count += 1
            if missing_dv:
                fallback_dv_count += 1
            if should_exclude_from_topic_view(article, missing_iv, missing_dv):
                exclusion_queue.append(
                    {
                        'paper_id': paper_id,
                        'title': article.get('title') or paper_id,
                        'year': article.get('year'),
                        'claim_count': int(article.get('claim_count') or 0),
                        'article_type': article.get('article_type') or '',
                        'exclusion_reason': hidden.get('repair_reason') or 'safe non-topic or contamination candidate',
                    }
                )
            else:
                repair_queue.append(
                    {
                        'paper_id': paper_id,
                        'title': article.get('title') or paper_id,
                        'year': article.get('year'),
                        'claim_count': int(article.get('claim_count') or 0),
                        'primary_front': (article.get('primary_front') or {}).get('name') or '',
                        'primary_topic': article.get('primary_topic') or '',
                        'sensor_summary': article.get('sensor_summary') or '',
                        'theories': list(article.get('theories') or [])[:4],
                        'missing_iv': missing_iv,
                        'missing_dv': missing_dv,
                        'repair_reason': hidden.get('repair_reason') or 'no visible canonical topic membership',
                    }
                )
            continue

        memberships.sort(key=lambda row: (not row['primary'], -row['confidence'], row['topic_id']))
        for membership in memberships:
            topic = topic_lookup.get(membership['topic_id'])
            if not topic:
                repair_queue.append(
                    {
                        'paper_id': paper_id,
                        'title': article.get('title') or paper_id,
                        'year': article.get('year'),
                        'claim_count': int(article.get('claim_count') or 0),
                        'primary_front': (article.get('primary_front') or {}).get('name') or '',
                        'primary_topic': article.get('primary_topic') or '',
                        'sensor_summary': article.get('sensor_summary') or '',
                        'theories': list(article.get('theories') or [])[:4],
                        'missing_iv': False,
                        'missing_dv': False,
                        'repair_reason': f"membership references missing topic node {membership['topic_id']}",
                    }
                )
                continue
            topic['paper_ids'].add(paper_id)
            topic['paper_preview'].append(
                {
                    'paper_id': paper_id,
                    'title': article.get('title') or paper_id,
                    'year': article.get('year'),
                    'claim_count': int(article.get('claim_count') or 0),
                    'primary_front': (article.get('primary_front') or {}).get('name') or '',
                    'sensor_summary': article.get('sensor_summary') or '',
                    'has_sensor_data': bool(article.get('has_sensor_data')),
                    'membership_score': membership['confidence'],
                    'membership_kind': 'primary' if membership['primary'] else 'secondary',
                }
            )
            for theory in article.get('theories') or []:
                label = clean_topic_candidate(theory)
                if label:
                    topic['theory_counter'][label] += 1
            for sensor in split_csvish(article.get('sensor_summary') or ''):
                topic['sensor_counter'][sensor] += 1
            for front in article.get('fronts') or []:
                name = str(front.get('name') or '').strip()
                if name:
                    topic['front_counter'][name] += 1

    topic_list = []
    root_groups = {}
    for topic in topic_lookup.values():
        if not topic['paper_ids']:
            continue
        item = {
            'id': topic['id'],
            'label': topic['label'],
            'iv_root': topic['iv_root'],
            'iv_root_label': topic['iv_root_label'],
            'iv_root_description': topic['iv_root_description'],
            'iv_node': topic['iv_node'],
            'iv_label': topic['iv_label'],
            'dv_root': topic['dv_root'],
            'dv_root_label': topic['dv_root_label'],
            'dv_focus': topic['dv_focus'],
            'dv_focus_label': topic['dv_focus_label'],
            'paper_count': len(topic['paper_ids']),
            'paper_ids': sorted(topic['paper_ids']),
            'paper_preview': sorted(topic['paper_preview'], key=lambda row: (row.get('membership_kind') != 'primary', -(row.get('claim_count') or 0), row.get('paper_id') or ''))[:14],
            'theories': [name for name, _ in topic['theory_counter'].most_common(6)],
            'sensors': [name for name, _ in topic['sensor_counter'].most_common(6)],
            'fronts': [name for name, _ in topic['front_counter'].most_common(4)],
            'hidden_from_view': False,
            'cross_relations': topic.get('cross_relations') or [],
        }
        topic_list.append(item)
        root = root_groups.setdefault(
            item['iv_root'],
            {
                'id': item['iv_root'],
                'label': item['iv_root_label'],
                'description': item['iv_root_description'],
                'visible_paper_ids': set(),
                'children': {},
            },
        )
        root['visible_paper_ids'].update(item['paper_ids'])
        child = root['children'].setdefault(
            item['iv_node'],
            {
                'id': item['iv_node'],
                'label': item['iv_label'],
                'visible_paper_ids': set(),
                'topics': [],
            },
        )
        child['visible_paper_ids'].update(item['paper_ids'])
        child['topics'].append(
            {
                'id': item['id'],
                'label': item['label'],
                'paper_count': item['paper_count'],
                'dv_focus': item['dv_focus'],
                'dv_focus_label': item['dv_focus_label'],
            }
        )

    topic_list.sort(key=lambda row: (row['iv_root'] == 'unspecified', row['dv_focus'] == 'unspecified.outcome', -row['paper_count'], row['label']))
    for topic in topic_list:
        if topic['cross_relations']:
            continue
        related_nodes = set(get_related(topic['iv_node']) or [])
        theory_set = set(topic['theories'])
        sensor_set = set(topic['sensors'])
        candidates = []
        for other in topic_list:
            if other['id'] == topic['id']:
                continue
            score = 0
            reasons = []
            shared_theories = theory_set & set(other['theories'])
            shared_sensors = sensor_set & set(other['sensors'])
            if other['dv_focus'] == topic['dv_focus'] and other['iv_node'] != topic['iv_node']:
                score += 4
                reasons.append(f"measures {topic['dv_focus_label'].lower()} too")
            if other['iv_root'] == topic['iv_root'] and other['iv_node'] != topic['iv_node']:
                score += 2
                reasons.append(f"same {topic['iv_root_label'].lower()} family")
            if other['iv_node'] in related_nodes:
                score += 2
                reasons.append('adjacent environment branch')
            if shared_theories:
                score += 1
                reasons.append('shared theory')
            if shared_sensors:
                score += 1
                reasons.append('shared sensors')
            if score <= 0:
                continue
            candidates.append(
                {
                    'target_id': other['id'],
                    'target_label': other['label'],
                    'kind': 'same_dv_focus' if other['dv_focus'] == topic['dv_focus'] else 'same_iv_root',
                    'label': '; '.join(reasons[:2]),
                    'score': score,
                    'paper_count': other['paper_count'],
                    'shared_theories': sorted(shared_theories)[:2],
                    'shared_sensors': sorted(shared_sensors)[:2],
                }
            )
        candidates.sort(key=lambda row: (-row['score'], -row['paper_count'], row['target_label']))
        topic['cross_relations'] = candidates[:8]

    root_payload = []
    for root in root_groups.values():
        children = []
        for child in root['children'].values():
            child['topics'].sort(key=lambda row: (row['dv_focus'] == 'unspecified.outcome', -row['paper_count'], row['label']))
            child['paper_count'] = len(child['visible_paper_ids'])
            del child['visible_paper_ids']
            if child['topics']:
                children.append(child)
        children.sort(key=lambda row: (row['id'] == 'unspecified.environment', -row['paper_count'], row['label']))
        if not children:
            continue
        root_payload.append(
            {
                'id': root['id'],
                'label': root['label'],
                'description': root['description'],
                'paper_count': len(root['visible_paper_ids']),
                'child_count': len(children),
                'children': children,
            }
        )
    root_payload.sort(key=lambda row: (row['id'] == 'unspecified', -row['paper_count'], row['label']))

    return {
        'summary': {
            'article_count': len(articles),
            'visible_article_count': len(articles) - len(repair_queue) - len(exclusion_queue),
            'hidden_article_count': len(repair_queue),
            'excluded_article_count': len(exclusion_queue),
            'front_covered_paper_count': int(topic_summary.get('front_covered_paper_count', 0)),
            'root_count': len(root_payload),
            'topic_count': len(topic_list),
            'hidden_topic_count': 0,
            'cross_relation_count': sum(len(topic['cross_relations']) for topic in topic_list),
            'fallback_iv_paper_count': fallback_iv_count,
            'fallback_dv_paper_count': fallback_dv_count,
            'source_kind': 'canonical_topic_artifacts',
            'front_source': topic_summary.get('front_source') or 'research_fronts_v7',
        },
        'notes': [
            'This viewer uses the current topic export as its base map.',
            'Research fronts are narrower overlays on that map rather than the map itself.',
            'Hidden papers are carried forward with explicit repair reasons rather than silently dropped.',
            'Cross-relations may be supplied by the canonical ontology or computed locally when absent.',
        ],
        'roots': root_payload,
        'topics': topic_list,
        'repair_queue': sorted(repair_queue, key=lambda row: (not row['missing_dv'], not row['missing_iv'], -(row['claim_count'] or 0), row['paper_id'])),
        'exclusion_queue': sorted(exclusion_queue, key=lambda row: (-(row['claim_count'] or 0), row['paper_id'])),
        'source_files': {
            'topic_ontology': str(TOPIC_ONTOLOGY_V1_PATH.relative_to(ROOT)),
            'topic_memberships': str(TOPIC_MEMBERSHIPS_V1_PATH.relative_to(ROOT)),
            'articles': str((OUT / 'articles.json').relative_to(ROOT)),
        },
    }


def build_topic_hierarchy_payload(articles, topic_summary):
    ontology_payload, membership_payload = _load_canonical_topic_artifacts()
    canonical_payload = None
    if ontology_payload and membership_payload:
        canonical_payload = build_topic_hierarchy_from_canonical(
            articles,
            topic_summary,
            ontology_payload,
            membership_payload,
        )

    rows = load_iv_dv_classifications()
    article_lookup = {article.get('paper_id'): article for article in articles}
    rows_by_paper = defaultdict(list)
    for row in rows:
        paper_id = str(row.get('paper_id') or '').strip()
        if paper_id:
            rows_by_paper[paper_id].append(row)

    topic_groups = {}
    root_groups = {}
    repair_queue = []
    exclusion_queue = []
    fallback_iv_count = 0
    fallback_dv_count = 0

    for article in articles:
        paper_id = article.get('paper_id')
        assignment = choose_topic_pairs_for_article(article, rows_by_paper.get(paper_id) or [])
        memberships = assignment['memberships']
        missing_iv = assignment['missing_iv']
        missing_dv = assignment['missing_dv']
        hidden_from_view = not memberships
        if missing_iv:
            fallback_iv_count += 1
        if missing_dv:
            fallback_dv_count += 1
        if hidden_from_view:
            if should_exclude_from_topic_view(article, missing_iv, missing_dv):
                exclusion_queue.append(
                    {
                        'paper_id': paper_id,
                        'title': article.get('title') or paper_id,
                        'year': article.get('year'),
                        'claim_count': int(article.get('claim_count') or 0),
                        'article_type': article.get('article_type') or '',
                        'exclusion_reason': 'safe non-topic or contamination candidate',
                    }
                )
                continue
            repair_queue.append(
                {
                    'paper_id': paper_id,
                    'title': article.get('title') or paper_id,
                    'year': article.get('year'),
                    'claim_count': int(article.get('claim_count') or 0),
                    'primary_front': (article.get('primary_front') or {}).get('name') or '',
                    'primary_topic': article.get('primary_topic') or '',
                    'sensor_summary': article.get('sensor_summary') or '',
                    'theories': list(article.get('theories') or [])[:4],
                    'missing_iv': missing_iv,
                    'missing_dv': missing_dv,
                    'repair_reason': (
                        'missing dominant IV and DV'
                        if missing_iv and missing_dv
                        else 'missing dominant IV'
                        if missing_iv
                        else 'missing dominant DV'
                    ),
                }
            )
        if hidden_from_view:
            continue

        for primary_iv, primary_dv, membership_score in memberships:
            iv_root = canonical_iv_root(primary_iv)
            dv_root = canonical_dv_root(primary_dv)
            topic_id = slugify(f"{primary_iv}__{primary_dv}")
            topic = topic_groups.setdefault(
                topic_id,
                {
                    'id': topic_id,
                    'label': topic_display_label(primary_iv, primary_dv),
                    'iv_root': iv_root,
                    'iv_root_label': iv_root_label(iv_root),
                    'iv_root_description': iv_root_description(iv_root),
                    'iv_node': primary_iv,
                    'iv_label': iv_node_label(primary_iv),
                    'dv_root': dv_root,
                    'dv_root_label': dv_root_label(dv_root),
                    'dv_focus': primary_dv,
                    'dv_focus_label': dv_focus_label(primary_dv),
                    'hidden_from_view': False,
                    'paper_ids': set(),
                    'paper_preview': [],
                    'theory_counter': Counter(),
                    'sensor_counter': Counter(),
                    'front_counter': Counter(),
                },
            )
            topic['paper_ids'].add(paper_id)
            topic['paper_preview'].append(
                {
                    'paper_id': paper_id,
                    'title': article.get('title') or paper_id,
                    'year': article.get('year'),
                    'claim_count': int(article.get('claim_count') or 0),
                    'primary_front': (article.get('primary_front') or {}).get('name') or '',
                    'sensor_summary': article.get('sensor_summary') or '',
                    'has_sensor_data': bool(article.get('has_sensor_data')),
                    'membership_score': round(float(membership_score), 3),
                }
            )
            for theory in article.get('theories') or []:
                label = clean_topic_candidate(theory)
                if label:
                    topic['theory_counter'][label] += 1
            for sensor in split_csvish(article.get('sensor_summary') or ''):
                topic['sensor_counter'][sensor] += 1
            for front in article.get('fronts') or []:
                name = str(front.get('name') or '').strip()
                if name:
                    topic['front_counter'][name] += 1

            root = root_groups.setdefault(
                iv_root,
                {
                    'id': iv_root,
                    'label': iv_root_label(iv_root),
                    'description': iv_root_description(iv_root),
                    'paper_ids': set(),
                    'visible_paper_ids': set(),
                    'children': {},
                },
            )
            root['paper_ids'].add(paper_id)
            root['visible_paper_ids'].add(paper_id)
            child = root['children'].setdefault(
                primary_iv,
                {
                    'id': primary_iv,
                    'label': iv_node_label(primary_iv),
                    'paper_ids': set(),
                    'visible_paper_ids': set(),
                    'topics': [],
                },
            )
            child['paper_ids'].add(paper_id)
            child['visible_paper_ids'].add(paper_id)
            child['topics'].append(topic_id)

    topic_list = []
    topic_lookup = {}
    for topic in topic_groups.values():
        paper_ids = sorted(topic['paper_ids'])
        paper_preview = sorted(
            topic['paper_preview'],
            key=lambda row: (-(row.get('claim_count') or 0), row.get('paper_id') or ''),
        )[:14]
        item = {
            'id': topic['id'],
            'label': topic['label'],
            'iv_root': topic['iv_root'],
            'iv_root_label': topic['iv_root_label'],
            'iv_root_description': topic['iv_root_description'],
            'iv_node': topic['iv_node'],
            'iv_label': topic['iv_label'],
            'dv_root': topic['dv_root'],
            'dv_root_label': topic['dv_root_label'],
            'dv_focus': topic['dv_focus'],
            'dv_focus_label': topic['dv_focus_label'],
            'paper_count': len(paper_ids),
            'paper_ids': paper_ids,
            'paper_preview': paper_preview,
            'theories': [name for name, _ in topic['theory_counter'].most_common(6)],
            'sensors': [name for name, _ in topic['sensor_counter'].most_common(6)],
            'fronts': [name for name, _ in topic['front_counter'].most_common(4)],
            'hidden_from_view': topic['hidden_from_view'],
            'cross_relations': [],
        }
        topic_lookup[item['id']] = item
        topic_list.append(item)

    def topic_sort_key(row):
        return (
            row['iv_root'] == 'unspecified',
            row['dv_focus'] == 'unspecified.outcome',
            -row['paper_count'],
            row['label'],
        )

    for root in root_groups.values():
        for child in root['children'].values():
            unique_topic_ids = sorted(set(child['topics']))
            child['topics'] = [
                {
                    'id': topic_id,
                    'label': topic_lookup[topic_id]['label'],
                    'paper_count': topic_lookup[topic_id]['paper_count'],
                    'dv_focus': topic_lookup[topic_id]['dv_focus'],
                    'dv_focus_label': topic_lookup[topic_id]['dv_focus_label'],
                }
                for topic_id in unique_topic_ids
                if not topic_lookup[topic_id]['hidden_from_view']
            ]
            child['topics'].sort(
                key=lambda row: (
                    row['id'].startswith('unspecified_environment'),
                    row['dv_focus'] == 'unspecified.outcome',
                    -row['paper_count'],
                    row['label'],
                )
            )
            child['paper_count'] = len(child['visible_paper_ids'])
            del child['paper_ids']
            del child['visible_paper_ids']

    topic_list.sort(key=topic_sort_key)
    visible_topic_list = [topic for topic in topic_list if not topic['hidden_from_view']]

    for topic in visible_topic_list:
        related_nodes = set(get_related(topic['iv_node']) or [])
        theory_set = set(topic['theories'])
        sensor_set = set(topic['sensors'])
        candidates = []
        for other in visible_topic_list:
            if other['id'] == topic['id']:
                continue
            score = 0
            reasons = []
            shared_theories = theory_set & set(other['theories'])
            shared_sensors = sensor_set & set(other['sensors'])

            if other['dv_focus'] == topic['dv_focus'] and other['iv_node'] != topic['iv_node']:
                score += 4
                reasons.append(f"measures {topic['dv_focus_label'].lower()} too")
            if other['iv_root'] == topic['iv_root'] and other['iv_node'] != topic['iv_node']:
                score += 2
                reasons.append(f"same {topic['iv_root_label'].lower()} family")
            if other['iv_node'] in related_nodes:
                score += 2
                reasons.append('adjacent environment branch')
            if shared_theories:
                score += 1
                reasons.append('shared theory')
            if shared_sensors:
                score += 1
                reasons.append('shared sensors')
            if score <= 0:
                continue

            relation_kind = 'same_dv_focus' if other['dv_focus'] == topic['dv_focus'] else 'same_iv_root'
            candidates.append(
                {
                    'target_id': other['id'],
                    'target_label': other['label'],
                    'kind': relation_kind,
                    'label': '; '.join(reasons[:2]),
                    'score': score,
                    'paper_count': other['paper_count'],
                    'shared_theories': sorted(shared_theories)[:2],
                    'shared_sensors': sorted(shared_sensors)[:2],
                }
            )
        candidates.sort(key=lambda row: (-row['score'], -row['paper_count'], row['target_label']))
        topic['cross_relations'] = candidates[:8]

    root_payload = []
    for root in root_groups.values():
        children = [child for child in root['children'].values() if child.get('topics')]
        children.sort(
            key=lambda row: (
                row['id'] == 'unspecified.environment',
                -row['paper_count'],
                row['label'],
            )
        )
        if not children:
            continue
        root_payload.append(
            {
                'id': root['id'],
                'label': root['label'],
                'description': root['description'],
                'paper_count': len(root['visible_paper_ids']),
                'child_count': len(children),
                'children': children,
            }
        )
    root_payload.sort(
        key=lambda row: (
            row['id'] == 'unspecified',
            -row['paper_count'],
            row['label'],
        )
    )

    heuristic_payload = {
        'summary': {
            'article_count': len(articles),
            'visible_article_count': len(articles) - len(repair_queue) - len(exclusion_queue),
            'hidden_article_count': len(repair_queue),
            'excluded_article_count': len(exclusion_queue),
            'front_covered_paper_count': int(topic_summary.get('front_covered_paper_count', 0)),
            'root_count': len(root_payload),
            'topic_count': len(visible_topic_list),
            'hidden_topic_count': len(topic_list) - len(visible_topic_list),
            'cross_relation_count': sum(len(topic['cross_relations']) for topic in visible_topic_list),
            'fallback_iv_paper_count': fallback_iv_count,
            'fallback_dv_paper_count': fallback_dv_count,
            'source_kind': 'heuristic_topic_hierarchy',
            'front_source': topic_summary.get('front_source') or 'research_fronts_v5',
        },
        'notes': [
            'Each paper is assigned to a stable working topic from IV and DV evidence so the broader map remains usable while coverage improves.',
            'Research fronts are included as supporting metadata, not as the sole topic authority.',
            'Cross-relations highlight papers that measure the same high-level outcome or sit nearby in the IV hierarchy.',
            'Topics with unresolved dominant IV or DV assignments are hidden from the viewer and moved into a repair queue.',
            'Obvious non-topic contaminants are separated into an exclusion queue rather than left in the repair queue.',
        ],
        'roots': root_payload,
        'topics': visible_topic_list,
        'repair_queue': sorted(repair_queue, key=lambda row: (not row['missing_dv'], not row['missing_iv'], -(row['claim_count'] or 0), row['paper_id'])),
        'exclusion_queue': sorted(exclusion_queue, key=lambda row: (-(row['claim_count'] or 0), row['paper_id'])),
        'source_files': {
            'iv_dv_classifications': str(IV_DV_CLASSIFICATIONS_PATH.relative_to(ROOT)),
            'articles': str((OUT / 'articles.json').relative_to(ROOT)),
            'topics': str((OUT / 'topics.json').relative_to(ROOT)),
        },
    }
    if canonical_payload:
        heuristic_payload['notes'].insert(
            0,
            f"Canonical topic artifacts are available and provide the defended map, but they currently surface only {canonical_payload.get('summary', {}).get('visible_article_count', 0)} of {len(articles)} papers. The broader working map remains useful for exploratory coverage.",
        )
        heuristic_payload['source_files']['topic_ontology'] = str(TOPIC_ONTOLOGY_V1_PATH.relative_to(ROOT))
        heuristic_payload['source_files']['topic_memberships'] = str(TOPIC_MEMBERSHIPS_V1_PATH.relative_to(ROOT))
        defended_visible = int(canonical_payload.get('summary', {}).get('visible_article_count', 0))
        working_visible = int(heuristic_payload.get('summary', {}).get('visible_article_count', 0))
        hidden_until_reviewed = int(heuristic_payload.get('summary', {}).get('hidden_article_count', 0))
        excluded_count = int(heuristic_payload.get('summary', {}).get('excluded_article_count', 0))
        return {
            'summary': {
                'article_count': len(articles),
                'defended_article_count': defended_visible,
                'working_article_count': working_visible,
                'hidden_article_count': hidden_until_reviewed,
                'excluded_article_count': excluded_count,
                'front_covered_paper_count': int(topic_summary.get('front_covered_paper_count', 0)),
                'source_kind': 'progressive_topic_hierarchy',
                'front_source': topic_summary.get('front_source') or 'research_fronts_v7',
                'default_view': 'defended',
            },
            'notes': [
                'This map now uses progressive disclosure rather than a single confidence policy.',
                f"The defended map shows {defended_visible} papers whose topic placement is strong enough to defend publicly.",
                f"The working map expands that to {working_visible} papers by including provisional placements that are still under review.",
                f"{hidden_until_reviewed} papers remain hidden until reviewed, and {excluded_count} were separated as safe exclusions.",
                'Research fronts remain overlays on top of the topic map rather than the main taxonomy.',
            ],
            'default_view': 'defended',
            'available_views': ['defended', 'working'],
            'progressive_disclosure': {
                'defended_article_count': defended_visible,
                'working_article_count': working_visible,
                'working_expansion_count': max(working_visible - defended_visible, 0),
                'hidden_until_reviewed_count': hidden_until_reviewed,
                'excluded_article_count': excluded_count,
            },
            'views': {
                'defended': canonical_payload,
                'working': heuristic_payload,
            },
            'roots': canonical_payload.get('roots') or [],
            'topics': canonical_payload.get('topics') or [],
            'repair_queue': heuristic_payload.get('repair_queue') or [],
            'exclusion_queue': heuristic_payload.get('exclusion_queue') or [],
            'source_files': {
                'topic_ontology': str(TOPIC_ONTOLOGY_V1_PATH.relative_to(ROOT)),
                'topic_memberships': str(TOPIC_MEMBERSHIPS_V1_PATH.relative_to(ROOT)),
                'iv_dv_classifications': str(IV_DV_CLASSIFICATIONS_PATH.relative_to(ROOT)),
                'articles': str((OUT / 'articles.json').relative_to(ROOT)),
                'topics': str((OUT / 'topics.json').relative_to(ROOT)),
            },
        }
    return heuristic_payload


def _write_optional_payload_copy(source_path, output_name):
    source = Path(source_path)
    if not source.exists():
        return False
    (OUT / output_name).write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
    return True


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
    index = load_argumentation_indexes()
    paper_graph = index['paper_graph']
    claim_graph = index['claim_graph']
    paper_nodes = list(index['paper_nodes'])
    claim_nodes = list(index['claim_nodes'])
    belief_targets = index['belief_targets']
    belief_attacks = index['belief_attacks']
    belief_supports = index['belief_supports']

    clusters = []
    for cluster in paper_graph.get('debate_clusters') or []:
        theories = cluster.get('theories') or []
        papers = cluster.get('papers') or []
        clusters.append({
            'cluster_id': cluster.get('cluster_id'),
            'paper_count': len(papers),
            'theory_count': len(theories),
            'papers': papers[:16],
            'theories': theories[:12],
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
            'support_edge_count': claim_metadata.get('support_edge_count', 0),
            'attack_edge_count': claim_metadata.get('attack_edge_count', 0),
            'search_target_count': claim_metadata.get('target_count', 0),
        },
        'coverage_report': coverage,
        'debate_clusters': clusters,
        'paper_nodes': [
            {
                'paper_id': node.get('paper_id') or node.get('belief_id'),
                'content_preview': compact_text(node.get('content_preview') or node.get('content') or '', 180),
                'contradiction_count': node.get('contradiction_count') or 0,
                'node_qualifier': node.get('node_qualifier') or node.get('qualifier') or '',
                'claim_count': node.get('claim_count') or 0,
                'dominant_stance': node.get('dominant_stance') or '',
                'theories': list(node.get('theories') or [])[:8],
                'search_target_count': int((index['paper_index'].get(node.get('paper_id')) or {}).get('search_target_count') or 0),
            }
            for node in paper_nodes
        ],
        'claim_nodes': [
            {
                'belief_id': node.get('belief_id'),
                'paper_id': node.get('paper_id'),
                'content_preview': compact_text(node.get('content_preview') or node.get('content') or '', 180),
                'incoming_support_count': node.get('incoming_support_count') or 0,
                'incoming_attack_count': node.get('incoming_attack_count') or 0,
                'qualifier': node.get('qualifier') or node.get('node_qualifier') or '',
                'warrant_status': node.get('warrant_status') or '',
                'defeat_type': node.get('defeat_type') or '',
                'resolution_question': (belief_targets.get(node.get('belief_id')) or {}).get('resolution_question') or '',
                'review_urgency': (belief_targets.get(node.get('belief_id')) or {}).get('review_urgency') or '',
                'attack_scheme_hints': (belief_targets.get(node.get('belief_id')) or {}).get('attack_scheme_hints') or [],
                'top_attacks': (belief_attacks.get(node.get('belief_id')) or [])[:3],
                'top_supports': (belief_supports.get(node.get('belief_id')) or [])[:3],
            }
            for node in claim_nodes
        ],
        'search_targets': sorted(
            [row for row in belief_targets.values()],
            key=lambda row: (-(row.get('priority_score') or 0), row.get('belief_id') or ''),
        ),
        'attack_scheme_counts': [
            {'scheme': name, 'count': count}
            for name, count in sorted(index['attack_scheme_counts'].items(), key=lambda item: (-item[1], item[0]))
        ],
        'attack_examples': index['attack_examples'][:36],
        'source_files': {
            'paper_graph': str(ARG_GRAPH_PATH.relative_to(ROOT)),
            'claim_graph': str(CLAIM_ARG_GRAPH_PATH.relative_to(ROOT)),
            'search_targets': str(CLAIM_ARG_TARGETS_PATH.relative_to(ROOT)),
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
            for row in annotation_rows
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
    topics, gaps, topic_summary = load_fronts()
    evidence, articles = parse_claims()
    topic_summary['front_covered_paper_count'] = topic_summary.get('unique_paper_count', 0)
    topic_summary['article_count'] = len(articles)
    topic_hierarchy = build_topic_hierarchy_payload(articles, topic_summary)
    dashboard = build_dashboard(articles, evidence)
    json_status = build_json_status(articles)
    argumentation = build_argumentation_payload()
    annotations = build_annotations_payload()
    interpretation = build_interpretation_payload()
    layers = build_layers_summary(argumentation, annotations, interpretation)
    (OUT / 'topics.json').write_text(json.dumps({'topics': topics, 'summary': topic_summary}, indent=2))
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
    (OUT / 'topic_hierarchy.json').write_text(json.dumps(topic_hierarchy, indent=2))
    (OUT / 'topic_repair_queue.json').write_text(json.dumps({'repair_queue': topic_hierarchy.get('repair_queue') or []}, indent=2))
    (OUT / 'topic_exclusion_queue.json').write_text(json.dumps({'exclusion_queue': topic_hierarchy.get('exclusion_queue') or []}, indent=2))
    _write_optional_payload_copy(TOPIC_ONTOLOGY_V1_PATH, 'topic_ontology.json')
    _write_optional_payload_copy(TOPIC_MEMBERSHIPS_V1_PATH, 'topic_memberships.json')
    _write_optional_payload_copy(FRONTS_V7_PATH, 'research_fronts.json')
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
