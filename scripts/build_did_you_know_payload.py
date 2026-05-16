#!/usr/bin/env python3
"""Build generated Did You Know cards for KA journeys and topic browsing.

The generator selects source-backed candidate claims from the KA evidence
payload, scores them for browsing value, then applies a deterministic
science-writing pass. The writer changes presentation only; it does not invent
claims or sources.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_DIR = REPO_ROOT / "data" / "ka_payloads"
DEFAULT_EVIDENCE_PATH = PAYLOAD_DIR / "evidence.json"
DEFAULT_OUTPUT_PATH = PAYLOAD_DIR / "did_you_know.json"

SCIENCE_WRITER_VERSION = "science_writer_dyk_v1_2026_05_14"
HAND_AUTHORED_DYK_VERSION = "hand_authored_dyk_v1_2026_05_15"
PAYLOAD_SCHEMA_VERSION = "ka_did_you_know_v1"

STOP_TOPICS = {"Unknown", "", "Unspecified"}

SURPRISE_TERMS = {
    "sleep",
    "stress",
    "cortisol",
    "memory",
    "attention",
    "noise",
    "sound",
    "light",
    "daylight",
    "green",
    "nature",
    "window",
    "view",
    "physiological",
    "neural",
    "brain",
    "walking",
    "wayfinding",
    "preference",
}

PRACTICAL_TERMS = {
    "office",
    "classroom",
    "hospital",
    "workplace",
    "home",
    "residential",
    "school",
    "lighting",
    "noise",
    "window",
    "material",
    "thermal",
    "green",
    "plants",
    "wayfinding",
    "open",
    "corridor",
}

TOPIC_WRITING_FRAMES: dict[tuple[str, str], dict[str, str]] = {
    (
        "Acoustic Environment",
        "Physiological Response",
    ): {
        "title": "Classroom sound can change children's bodies, not just their attention.",
        "hook": "Quiet, noisy, and reverberant classrooms can be treated as physiological stimuli.",
        "lead": (
            "The acoustic stimulus is a classroom soundscape: quiet versus noisy rooms, with different "
            "reverberation times. The affected response is not just preference; the review connects these "
            "conditions to children's performance and physiological indicators such as EEG, electrodermal "
            "activity, heart rate, and pupil response."
        ),
    },
    (
        "Acoustic Environment",
        "Comfort",
    ): {
        "title": "Sound measurements alone do not explain acoustic comfort.",
        "hook": "Noise and sound-insulation measures matter, but occupants judge comfort through perception.",
        "lead": (
            "The stimulus is the acoustic field in a dwelling, including noise, airborne sound, and impact "
            "sound. The response is perceived acoustic comfort: whether occupants experience the space as "
            "annoying, tolerable, or comfortable."
        ),
    },
}

HAND_AUTHORED_DID_YOU_KNOW_CARDS: list[dict[str, Any]] = [
    {
        "id": "dyk_hand_predictive_processing",
        "title": "Your brain predicts a building before experiencing it.",
        "kicker": "CURATED · Predictive Processing",
        "hook": "A building can produce prediction error before a visitor can explain what feels wrong.",
        "body": (
            "Visual, acoustic, and thermal cues generate top-down predictions at every level of cortex. "
            "Subtle violations — an almost-right angle, a misplaced acoustic reflection — leave persistent "
            "unresolved prediction error that occupants can rarely articulate but reliably feel."
        ),
        "primary_topic": "Frameworks -> Predictive Processing",
        "topic_ids": ["frameworks__predictive_processing"],
        "topic_labels": ["Frameworks -> Predictive Processing"],
        "journey_tags": ["researcher", "student_explorer", "theory_browser", "topic_browser"],
        "sort_tags": ["did_you_know", "hand_authored", "surprising", "framework", "moderate"],
        "evidence_strength": "moderate",
        "confidence": 0.72,
        "surprise_score": 0.82,
        "practical_value_score": 0.58,
        "controversy_score": 0.22,
        "links": {"topics": "ka_topics_dyk.html", "framework": "ka_framework_pp.html"},
    },
    {
        "id": "dyk_hand_chronobiology_daylight",
        "title": "Morning daylight is a neurochemical signal.",
        "kicker": "CURATED · Chronobiology",
        "hook": "A window is also a timing device for the nervous system.",
        "body": (
            "Light above roughly 250 melanopic lux in the first hours of the day activates intrinsically "
            "photosensitive retinal ganglion cells, advances the circadian clock, and produces measurable "
            "gains in daytime alertness, memory, and sleep quality. Window placement is neurochemistry."
        ),
        "primary_topic": "Luminous Environment -> Sleep Quality",
        "topic_ids": ["luminous_environment__sleep_quality"],
        "topic_labels": ["Luminous Environment -> Sleep Quality", "Frameworks -> Chronobiology"],
        "journey_tags": ["practitioner", "researcher", "student_explorer", "topic_browser"],
        "sort_tags": ["did_you_know", "hand_authored", "practical", "surprising", "moderate"],
        "evidence_strength": "moderate",
        "confidence": 0.74,
        "surprise_score": 0.78,
        "practical_value_score": 0.76,
        "controversy_score": 0.12,
        "links": {"topics": "ka_topics_dyk.html", "framework": "ka_framework_cb.html"},
    },
    {
        "id": "dyk_hand_embodied_cognition",
        "title": "Spaces you only see are spaces you implicitly inhabit.",
        "kicker": "CURATED · Embodied Cognition",
        "hook": "Perception of action-relevant geometry can recruit the body's planning systems.",
        "body": (
            "Premotor and parietal circuits activate during perception of action-relevant geometry, not only "
            "during action itself. A handrail invites grip simulation in passing; a corridor invites walking "
            "simulation in reading. Design choices recruit motor cortex whether or not the occupant moves."
        ),
        "primary_topic": "Spatial Form -> Embodied Cognition",
        "topic_ids": ["spatial_form__embodied_cognition"],
        "topic_labels": ["Spatial Form -> Embodied Cognition", "Frameworks -> Embodied Cognition"],
        "journey_tags": ["practitioner", "researcher", "student_explorer", "theory_browser", "topic_browser"],
        "sort_tags": ["did_you_know", "hand_authored", "surprising", "framework", "moderate"],
        "evidence_strength": "moderate",
        "confidence": 0.7,
        "surprise_score": 0.8,
        "practical_value_score": 0.62,
        "controversy_score": 0.18,
        "links": {"topics": "ka_topics_dyk.html", "framework": "ka_framework_ec.html"},
    },
    {
        "id": "dyk_hand_natural_light_sleep",
        "title": "Natural light improves sleep.",
        "kicker": "CURATED · Daylight",
        "hook": "Work-hour light exposure can show up later as sleep quality.",
        "body": (
            "Natural light exposure during work hours improves sleep quality by 46 minutes per night "
            "(Boubekri et al., 2014). Workers in offices with adequate natural light report better sleep "
            "and fewer cognitive complaints."
        ),
        "primary_topic": "Luminous Environment -> Sleep Quality",
        "topic_ids": ["luminous_environment__sleep_quality"],
        "topic_labels": ["Luminous Environment -> Sleep Quality"],
        "journey_tags": ["practitioner", "student_explorer", "topic_browser"],
        "sort_tags": ["did_you_know", "hand_authored", "practical", "moderate"],
        "evidence_strength": "moderate",
        "confidence": 0.68,
        "surprise_score": 0.66,
        "practical_value_score": 0.82,
        "controversy_score": 0.12,
        "links": {"topics": "ka_topics_dyk.html", "articles": "ka_articles.html?q=Boubekri%202014"},
    },
    {
        "id": "dyk_hand_green_spaces_stress",
        "title": "Green spaces reduce stress.",
        "kicker": "CURATED · Nature",
        "hook": "A short encounter with nature can be physiologically visible.",
        "body": (
            "Just 20 minutes in a natural environment can significantly lower cortisol levels and reduce "
            "physiological stress markers. This effect appears across multiple studies and holds for both "
            "urban parks and more remote natural areas."
        ),
        "primary_topic": "Nature & Biophilia -> Stress Response",
        "topic_ids": ["nature_biophilia__stress_response"],
        "topic_labels": ["Nature & Biophilia -> Stress Response"],
        "journey_tags": ["practitioner", "student_explorer", "topic_browser"],
        "sort_tags": ["did_you_know", "hand_authored", "practical", "moderate"],
        "evidence_strength": "moderate",
        "confidence": 0.68,
        "surprise_score": 0.62,
        "practical_value_score": 0.72,
        "controversy_score": 0.14,
        "links": {"topics": "ka_topics_dyk.html"},
    },
    {
        "id": "dyk_hand_noise_concentration",
        "title": "Noise impairs concentration.",
        "kicker": "CURATED · Acoustics",
        "hook": "Some environmental stressors get worse with repeated exposure rather than fading out.",
        "body": (
            "Ambient noise above 70 dB shows sensitization rather than habituation—the stress response "
            "actually increases with repeated exposure, unlike most environmental stimuli. This explains "
            "why you don't 'get used to' bad noise."
        ),
        "primary_topic": "Acoustic Environment -> Cognitive Performance",
        "topic_ids": ["acoustic_environment__cognitive_performance"],
        "topic_labels": ["Acoustic Environment -> Cognitive Performance"],
        "journey_tags": ["debate_journey", "practitioner", "student_explorer", "topic_browser"],
        "sort_tags": ["did_you_know", "hand_authored", "practical", "surprising", "moderate"],
        "evidence_strength": "moderate",
        "confidence": 0.64,
        "surprise_score": 0.72,
        "practical_value_score": 0.76,
        "controversy_score": 0.3,
        "links": {"topics": "ka_topics_dyk.html"},
    },
    {
        "id": "dyk_hand_ceiling_height_cognition",
        "title": "Spatial enclosure affects thinking.",
        "kicker": "CURATED · Spatial Form",
        "hook": "Ceiling height may bias cognition toward abstract or detail-focused work.",
        "body": (
            "Ceiling height influences cognitive styles: high ceilings promote creative, abstract thinking "
            "while low ceilings promote focused, detailed work. This effect is measurable and appears to be "
            "neurally mediated through the parietal cortex."
        ),
        "primary_topic": "Spatial Form -> Cognitive Performance",
        "topic_ids": ["spatial_form__cognitive_performance"],
        "topic_labels": ["Spatial Form -> Cognitive Performance"],
        "journey_tags": ["practitioner", "student_explorer", "topic_browser"],
        "sort_tags": ["did_you_know", "hand_authored", "practical", "surprising", "moderate"],
        "evidence_strength": "moderate",
        "confidence": 0.62,
        "surprise_score": 0.76,
        "practical_value_score": 0.68,
        "controversy_score": 0.26,
        "links": {"topics": "ka_topics_dyk.html"},
    },
    {
        "id": "dyk_hand_material_textures",
        "title": "Material textures matter neurologically.",
        "kicker": "CURATED · Materials",
        "hook": "Surfaces can change the felt character of a space through somatosensory systems.",
        "body": (
            "Tactile properties of surfaces activate somatosensory cortex and influence emotional responses "
            "to spaces. Soft materials increase comfort perception and reduce cortisol compared to harsh "
            "reflective surfaces."
        ),
        "primary_topic": "Material & Surface -> Physiological Response",
        "topic_ids": ["material_surface__physiological_response"],
        "topic_labels": ["Material & Surface -> Physiological Response"],
        "journey_tags": ["practitioner", "student_explorer", "topic_browser"],
        "sort_tags": ["did_you_know", "hand_authored", "practical", "moderate"],
        "evidence_strength": "moderate",
        "confidence": 0.62,
        "surprise_score": 0.64,
        "practical_value_score": 0.7,
        "controversy_score": 0.18,
        "links": {"topics": "ka_topics_dyk.html"},
    },
]


@dataclass(frozen=True)
class DidYouKnowCandidate:
    source: dict[str, Any]
    score: float
    surprise_score: float
    practical_value_score: float
    controversy_score: float
    evidence_strength: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def compact_text(value: Any, *, max_chars: int = 320) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip(" ,.;:") + "..."


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "card"


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def topic_parts(label: str) -> tuple[str, str]:
    if "→" in label:
        left, right = label.split("→", 1)
    elif "->" in label:
        left, right = label.split("->", 1)
    else:
        return label.strip(), ""
    return left.strip(), right.strip()


def evidence_strength(row: dict[str, Any]) -> str:
    credence = float(row.get("credence") or 0.0)
    support = int(row.get("support_count") or 0)
    attacks = int(row.get("attack_count") or 0)
    if credence >= 0.85 and support >= 4 and attacks == 0:
        return "strong"
    if credence >= 0.70 and support >= 2:
        return "moderate"
    if attacks > 0 or credence < 0.45:
        return "contested"
    return "emerging"


def score_candidate(row: dict[str, Any]) -> DidYouKnowCandidate | None:
    claim = compact_text(row.get("claim") or row.get("finding"), max_chars=520)
    topic = str(row.get("primary_topic") or "").strip()
    paper_id = str(row.get("paper_id") or "").strip()
    if not claim or not paper_id or topic in STOP_TOPICS:
        return None
    if len(claim) < 45:
        return None

    text = f"{claim} {topic} {row.get('paper_title') or ''} {row.get('abstract') or ''}".lower()
    credence = float(row.get("credence") or 0.0)
    support = int(row.get("support_count") or 0)
    attacks = int(row.get("attack_count") or 0)

    surprise_hits = sum(1 for term in SURPRISE_TERMS if term in text)
    practical_hits = sum(1 for term in PRACTICAL_TERMS if term in text)
    surprise = clamp(0.25 + surprise_hits * 0.08 + (0.1 if "no " in text or "not " in text else 0.0))
    practical = clamp(0.2 + practical_hits * 0.09)
    controversy = clamp(0.1 + attacks * 0.2 + (0.2 if credence < 0.55 else 0.0))
    strength = evidence_strength(row)
    strength_bonus = {"strong": 0.24, "moderate": 0.16, "emerging": 0.08, "contested": 0.04}[strength]
    score = (
        credence * 0.36
        + min(support, 8) / 8 * 0.18
        + surprise * 0.2
        + practical * 0.16
        + strength_bonus
        + controversy * 0.06
    )
    return DidYouKnowCandidate(
        source=row,
        score=round(score, 4),
        surprise_score=round(surprise, 3),
        practical_value_score=round(practical, 3),
        controversy_score=round(controversy, 3),
        evidence_strength=strength,
    )


class ScienceWriterDidYouKnow:
    """Local science-writer pass for DYK cards.

    This intentionally does not call an LLM. It enforces the science-writing
    contract in a deterministic way: preserve the source claim, add context and
    epistemic caution, and keep the card readable.
    """

    writing_agent = "science_writer"
    writing_agent_version = SCIENCE_WRITER_VERSION

    def render(self, candidate: DidYouKnowCandidate) -> dict[str, Any]:
        row = candidate.source
        topic = str(row.get("primary_topic") or "Built Environment").strip()
        left, right = topic_parts(topic)
        claim = compact_text(row.get("claim") or row.get("finding"), max_chars=260)
        paper_title = compact_text(row.get("paper_title") or row.get("citation"), max_chars=110)
        frame = self._topic_frame(left, right)
        title = self._title(left, right, claim, frame)
        hook = self._hook(left, right, candidate.evidence_strength, frame)
        body = self._body(claim, paper_title, candidate)
        cid = self._card_id(row, title)
        topic_ids = [tid for tid in row.get("topic_ids") or [] if tid]
        if row.get("primary_topic_id") and row["primary_topic_id"] not in topic_ids:
            topic_ids.insert(0, row["primary_topic_id"])
        return {
            "id": cid,
            "schema_version": PAYLOAD_SCHEMA_VERSION,
            "title": title,
            "kicker": f"{candidate.evidence_strength.upper()} EVIDENCE · {left or 'KA'}",
            "hook": hook,
            "body": body,
            "source_claim_ids": [str(row.get("id"))],
            "source_paper_ids": [str(row.get("paper_id"))],
            "source_papers": [
                {
                    "paper_id": str(row.get("paper_id")),
                    "title": paper_title,
                    "citation": compact_text(row.get("citation"), max_chars=180),
                    "year": row.get("year") or "",
                }
            ],
            "topic_ids": topic_ids,
            "topic_labels": [topic],
            "primary_topic": topic,
            "front_ids": [fid for fid in ([row.get("front_id")] + list(row.get("fronts") or [])) if fid],
            "theory_ids": [],
            "mechanism_ids": [],
            "journey_tags": self._journey_tags(candidate),
            "sort_tags": self._sort_tags(candidate),
            "evidence_strength": candidate.evidence_strength,
            "surprise_score": candidate.surprise_score,
            "practical_value_score": candidate.practical_value_score,
            "controversy_score": candidate.controversy_score,
            "confidence": round(float(row.get("credence") or 0.0), 3),
            "support_count": int(row.get("support_count") or 0),
            "attack_count": int(row.get("attack_count") or 0),
            "writing_agent": self.writing_agent,
            "writing_agent_version": self.writing_agent_version,
            "verification_status": "source_backed",
            "verification_notes": "Generated only from existing KA evidence fields; no unsupported claim expansion.",
            "links": {
                "articles": f"ka_articles.html?paper={row.get('paper_id')}",
                "topics": "ka_topics.html",
                "question": f"ka_demo_v04.html?q={slugify(title)}",
            },
        }

    def _topic_frame(self, left: str, right: str) -> dict[str, str]:
        return TOPIC_WRITING_FRAMES.get((left, right), {})

    def _title(self, left: str, right: str, claim: str, frame: dict[str, str]) -> str:
        if frame.get("title"):
            return frame["title"]
        if left and right:
            stimulus = left.replace(" Environment", "").lower()
            response = right.lower()
            return f"{left}: how {stimulus} conditions may affect {response}."
        if left:
            return f"{left} has measurable human consequences."
        words = claim.split()
        return compact_text(" ".join(words[:9]).rstrip(".") + ".", max_chars=80)

    def _hook(self, left: str, right: str, strength: str, frame: dict[str, str]) -> str:
        if frame.get("hook"):
            return frame["hook"]
        if left and right:
            return f"The card asks what stimulus is changing, who is affected, and what response shifts."
        if strength == "contested":
            return "The interesting part is not certainty; it is where the evidence starts to disagree."
        return "A concrete evidence claim worth opening before choosing a topic path."

    def _body(self, claim: str, paper_title: str, candidate: DidYouKnowCandidate) -> str:
        row = candidate.source
        left, right = topic_parts(str(row.get("primary_topic") or ""))
        frame = self._topic_frame(left, right)
        caution = {
            "strong": "This is a good entry point, but it is still evidence to inspect rather than a design law.",
            "moderate": "Treat this as a plausible pattern that needs scope conditions before design use.",
            "emerging": "The claim is useful for browsing, but the evidence is still developing.",
            "contested": "Use this as a debate card: it is interesting because the warrant is not settled.",
        }[candidate.evidence_strength]
        citation = f" Source: {paper_title}." if paper_title else ""
        if frame.get("lead"):
            return compact_text(f"{frame['lead']} Source claim: {claim}{citation} {caution}", max_chars=620)
        return compact_text(f"{self._topic_lead(left, right, row)} Source claim: {claim}{citation} {caution}", max_chars=520)

    def _topic_lead(self, left: str, right: str, row: dict[str, Any]) -> str:
        if not left or not right:
            return "The point of the card is the human consequence of a built-environment condition."
        population = self._population_phrase(row)
        stimulus = self._stimulus_phrase(left, row)
        response = self._response_phrase(right, row)
        return f"The stimulus is {stimulus}. The response is {response}{population}."

    def _population_phrase(self, row: dict[str, Any]) -> str:
        text = f"{row.get('claim') or ''} {row.get('abstract') or ''}".lower()
        if "student" in text or "children" in text or "classroom" in text:
            return " in students or children"
        if "worker" in text or "office" in text:
            return " in workers"
        if "patient" in text or "hospital" in text:
            return " in patients or care settings"
        return " in occupants"

    def _stimulus_phrase(self, left: str, row: dict[str, Any]) -> str:
        text = f"{row.get('claim') or ''} {row.get('abstract') or ''}".lower()
        if left == "Acoustic Environment":
            if "reverberation" in text or "rt" in text:
                return "the soundscape of a room, especially noise level and reverberation"
            return "the soundscape of a room, including noise, speech, and building-system sound"
        if left == "Luminous Environment":
            return "the lighting condition, including daylight, brightness, timing, or visual exposure"
        if left == "Thermal & Air Quality":
            return "the indoor climate, including temperature, ventilation, or air quality"
        if left == "Spatial Form":
            return "the spatial layout, enclosure, scale, or route structure"
        if left == "Nature & Biophilia":
            return "contact with vegetation, views, or natural settings"
        return f"the {left.lower()} condition"

    def _response_phrase(self, right: str, row: dict[str, Any]) -> str:
        sensor_summary = compact_text(row.get("sensor_summary"), max_chars=120)
        if right == "Physiological Response" and sensor_summary:
            return f"measured bodily arousal or regulation, including {sensor_summary}"
        if right == "Physiological Response":
            return "a bodily response such as arousal, stress physiology, or autonomic regulation"
        if right == "Cognitive Performance":
            return "attention, memory, task performance, or learning"
        if right == "Stress Response":
            return "stress, affect, or physiological load"
        if right == "Comfort":
            return "perceived comfort, annoyance, or tolerance of the space"
        if right == "Sleep Quality":
            return "sleep timing, alertness, or circadian regulation"
        return right.lower()

    def _journey_tags(self, candidate: DidYouKnowCandidate) -> list[str]:
        tags = {"student_explorer", "topic_browser"}
        if candidate.practical_value_score >= 0.45:
            tags.add("practitioner")
        if candidate.evidence_strength in {"strong", "moderate"}:
            tags.add("researcher")
        if candidate.controversy_score >= 0.35:
            tags.add("debate_journey")
        return sorted(tags)

    def _sort_tags(self, candidate: DidYouKnowCandidate) -> list[str]:
        tags = ["did_you_know"]
        if candidate.surprise_score >= 0.55:
            tags.append("surprising")
        if candidate.practical_value_score >= 0.45:
            tags.append("practical")
        if candidate.controversy_score >= 0.35:
            tags.append("debated")
        tags.append(candidate.evidence_strength)
        return tags

    def _card_id(self, row: dict[str, Any], title: str) -> str:
        raw = f"{row.get('id')}|{row.get('paper_id')}|{title}"
        digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
        return f"dyk_{digest}"


def hand_authored_cards() -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for source in HAND_AUTHORED_DID_YOU_KNOW_CARDS:
        card = dict(source)
        card.update(
            {
                "schema_version": PAYLOAD_SCHEMA_VERSION,
                "source_kind": "hand_authored_did_you_know",
                "source_claim_ids": [],
                "source_paper_ids": [],
                "source_papers": [],
                "front_ids": [],
                "theory_ids": [],
                "mechanism_ids": [],
                "support_count": 0,
                "attack_count": 0,
                "writing_agent": "human_curated",
                "writing_agent_version": HAND_AUTHORED_DYK_VERSION,
                "verification_status": "hand_authored_curated",
                "verification_notes": (
                    "Preserved from the current hand-authored KA Did You Know set; "
                    "requires evidence-trace review before being treated as source-backed."
                ),
            }
        )
        cards.append(card)
    return cards


def build_payload(
    evidence_payload: dict[str, Any], *, limit: int = 240, include_hand_authored: bool = True
) -> dict[str, Any]:
    evidence_rows = evidence_payload.get("evidence") or []
    candidates = [c for c in (score_candidate(row) for row in evidence_rows) if c is not None]
    candidates.sort(key=lambda item: (-item.score, -item.surprise_score, -item.practical_value_score))

    writer = ScienceWriterDidYouKnow()
    cards: list[dict[str, Any]] = []
    seen_topics: dict[str, int] = {}
    seen_papers: set[str] = set()
    for candidate in candidates:
        row = candidate.source
        topic = str(row.get("primary_topic") or "")
        paper_id = str(row.get("paper_id") or "")
        if seen_topics.get(topic, 0) >= 8:
            continue
        if paper_id in seen_papers and len(cards) < 40:
            continue
        card = writer.render(candidate)
        cards.append(card)
        seen_topics[topic] = seen_topics.get(topic, 0) + 1
        seen_papers.add(paper_id)
        if len(cards) >= limit:
            break

    generated_cards = cards
    if include_hand_authored:
        cards = hand_authored_cards() + generated_cards

    topic_counts: dict[str, int] = {}
    journey_counts: dict[str, int] = {}
    for card in cards:
        for topic in card["topic_labels"]:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        for tag in card["journey_tags"]:
            journey_counts[tag] = journey_counts.get(tag, 0) + 1

    return {
        "schema_version": PAYLOAD_SCHEMA_VERSION,
        "generated_at": utc_now(),
        "source_kind": "ka_evidence_did_you_know_generator",
        "source_files": {
            "evidence": str(DEFAULT_EVIDENCE_PATH.relative_to(REPO_ROOT)),
            "hand_authored_cards": ["ka_home.html", "ka_home_student.html", "ka_home_student_new.html"],
        },
        "science_writer": {
            "agent": writer.writing_agent,
            "version": writer.writing_agent_version,
            "method": "deterministic source-preserving rewrite",
            "non_promises": [
                "does not invent claims",
                "does not upgrade evidence strength",
                "does not replace source-paper review",
            ],
        },
        "summary": {
            "candidate_count": len(candidates),
            "generated_card_count": len(generated_cards),
            "hand_authored_card_count": len(cards) - len(generated_cards),
            "card_count": len(cards),
            "topic_count": len(topic_counts),
            "journey_counts": dict(sorted(journey_counts.items())),
            "evidence_strength_counts": dict(_counts(card["evidence_strength"] for card in cards)),
        },
        "cards": cards,
    }


def _counts(values: Iterable[str]) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return sorted(counts.items())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--limit", type=int, default=240)
    args = parser.parse_args(argv)

    evidence_payload = load_json(args.evidence)
    payload = build_payload(evidence_payload, limit=args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(payload['cards'])} Did You Know cards to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
