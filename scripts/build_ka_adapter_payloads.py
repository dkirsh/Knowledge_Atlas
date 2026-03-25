#!/usr/bin/env python3
import json
import re
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime

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

FRONTS_PATH = AE / 'data' / 'rebuild' / 'research_fronts_v5.json'
CLAIMS_PATH = AE / 'data' / 'rebuild' / 'gold_claims.jsonl'
REPAIRS_PATH = AE / 'data' / 'rebuild' / 'bibliographic_repairs.json'

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


def doi_status(value):
    return 'good' if clean_doi(value) else 'missing'


def subject_count_status(value):
    return 'good' if value not in (None, '', 0) else 'missing'


def load_bibliographic_repairs():
    if not REPAIRS_PATH.exists():
        return {}
    try:
        payload = json.loads(REPAIRS_PATH.read_text())
        return payload.get('papers', {})
    except Exception:
        return {}


def warrant_bucket(value):
    if isinstance(value, (int, float)):
        if value >= 0.67:
            return 'High'
        if value >= 0.4:
            return 'Medium'
        return 'Low'
    return humanize(value) or 'Unknown'


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
    repairs = load_bibliographic_repairs()
    with CLAIMS_PATH.open() as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            pid = obj.get('paper_id')
            statement = obj.get('statement') or obj.get('claim') or ''
            result = obj.get('structured_result_row') or {}
            theories = []
            ptf = obj.get('paper_theory_frame') or {}
            theories.extend(ptf.get('canonical_theories') or [])
            theories.extend(obj.get('theory_names') or [])
            repair = repairs.get(pid, {})
            if pid and pid not in paper_meta:
                paper_meta[pid] = {
                    'paper_id': pid,
                    'title': publishable_title(repair.get('title')) or publishable_title(obj.get('paper_title')) or publishable_title(obj.get('title')) or '',
                    'doi': clean_doi(repair.get('doi') or obj.get('doi')),
                    'year': sanitize_year(repair.get('year') or obj.get('year')),
                    'abstract': sanitize_abstract(repair.get('abstract') or obj.get('abstract_clean_text')) or '',
                    'repair_source': repair.get('source') or '',
                    'abstract_surface_path': repair.get('abstract_surface_path') or '',
                    'theories': theories,
                    'subject_count_total': obj.get('subject_count_total'),
                    'sample_n': obj.get('sample_n'),
                    'article_type': obj.get('article_type') or '',
                    'authors': repair.get('authors') or [],
                    'venue': repair.get('venue') or '',
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
                warrant_value = obj.get('mechanism_warrant')
                if warrant_value in (None, ''):
                    warrant_value = obj.get('evidence_strength_class')
                warrant_label = warrant_bucket(warrant_value)
                methodology_summary = summarize_methodology(obj.get('method_profile_excerpt'), obj.get('article_type'))
                evidence.append({
                    'id': len(evidence) + 1,
                    'finding': compact_text(statement or fallback_finding or pid, 220),
                    'construct': construct_label,
                    'signal': humanize(obj.get('evidence_strength_class') or obj.get('claim_type') or 'Claim'),
                    'studyType': humanize(obj.get('article_type') or 'Unknown'),
                    'warrant': warrant_label,
                    'credence': round(float(obj.get('severity') or 0.5), 2),
                    'year': sanitize_year(repair.get('year') or obj.get('year')) or '',
                    'citation': pid,
                    'abstract': compact_text(sanitize_abstract(repair.get('abstract') or obj.get('abstract_clean_text')) or 'Abstract not yet recovered from the current rebuild.', 500),
                    'claim': compact_text(statement or fallback_finding or pid, 260),
                    'methodology': methodology_summary,
                    'warrant_chain': result.get('test_statistic') or '',
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
            'abstract': sanitize_abstract(meta.get('abstract')) or 'Abstract not yet recovered from the current rebuild.',
            'claim_count': len(claims),
            'sample_n': meta.get('sample_n'),
            'subject_count_total': meta.get('subject_count_total'),
            'theories': top_theories,
            'constructs': top_constructs,
            'instruments': top_measures,
            'article_type': meta.get('article_type') or '',
            'authors': meta.get('authors') or [],
            'venue': meta.get('venue') or '',
            'repair_source': meta.get('repair_source') or '',
            'abstract_surface_path': meta.get('abstract_surface_path') or '',
            'json_status': {
                'title': title_status(title),
                'doi': doi_status(meta.get('doi')),
                'abstract': abstract_status(meta.get('abstract')),
                'subject_count_total': subject_count_status(meta.get('subject_count_total')),
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
        'subject_count_good': 0,
        'subject_count_missing': 0,
    }
    rows = []
    for article in articles:
        status = article.get('json_status') or {}
        title_state = status.get('title') or 'missing'
        abstract_state = status.get('abstract') or 'missing'
        doi_state = status.get('doi') or 'missing'
        subject_state = status.get('subject_count_total') or 'missing'
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
        if subject_state == 'good':
            summary['subject_count_good'] += 1
        else:
            summary['subject_count_missing'] += 1
        rows.append({
            'paper_id': article.get('paper_id'),
            'title': article.get('title'),
            'claim_count': article.get('claim_count'),
            'json_status': status,
        })
    return {'summary': summary, 'papers': rows}


def build_dashboard(articles, evidence):
    return {
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


def main():
    topics, gaps = load_fronts()
    evidence, articles = parse_claims()
    dashboard = build_dashboard(articles, evidence)
    json_status = build_json_status(articles)
    (OUT / 'topics.json').write_text(json.dumps({'topics': topics}, indent=2))
    (OUT / 'gaps.json').write_text(json.dumps({'gaps': gaps}, indent=2))
    (OUT / 'evidence.json').write_text(json.dumps({'evidence': evidence}, indent=2))
    (OUT / 'articles.json').write_text(json.dumps({'articles': articles}, indent=2))
    (OUT / 'dashboard.json').write_text(json.dumps({'dashboard': dashboard}, indent=2))
    (OUT / 'json_status.json').write_text(json.dumps(json_status, indent=2))
    print('Wrote payloads to', OUT)

if __name__ == '__main__':
    main()
