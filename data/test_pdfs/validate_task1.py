#!/usr/bin/env python3
"""Task 1 Phase 4 validation — runs all 4 test cases and checks storage."""
import sys, json, sqlite3, os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ATLAS_SHARED_SRC = REPO_ROOT.parent / "atlas_shared" / "src"
sys.path.insert(0, str(ATLAS_SHARED_SRC))

from atlas_shared.article_types import HeuristicArticleTypeClassifier
from atlas_shared.relevance import (
    QuestionArticleRelevanceFilter, ArticleCandidate, QuestionConstitution
)

CONSTITUTIONS_PATH = ATLAS_SHARED_SRC / "atlas_shared" / "data" / "question_constitutions_starter.json"

def load_constitutions():
    data = json.loads(CONSTITUTIONS_PATH.read_text())
    return [QuestionConstitution.from_panel_spec(q) for q in data["questions"]]

def extract_pdf_text(data: bytes) -> str:
    try:
        import pdfplumber, io
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages[:3])
    except Exception:
        pass
    return data[:6000].decode("latin-1", errors="ignore")

def run_classifier(title: str, abstract: str) -> dict:
    type_decision = HeuristicArticleTypeClassifier().classify(abstract=abstract, title=title)
    constitutions = load_constitutions()
    rf = QuestionArticleRelevanceFilter()
    candidate = ArticleCandidate(paper_id="test-tmp", title=title, abstract=abstract)

    best = None
    for c in constitutions:
        a = rf.assess(c, candidate)
        if a.verdict == "accept":
            best = (a, c); break
        if a.verdict == "edge_case":
            if best is None or best[0].confidence < a.confidence:
                best = (a, c)

    if best is None:
        all_a = [(rf.assess(c, candidate), c) for c in constitutions]
        best = max(all_a, key=lambda x: x[0].confidence)

    a, c = best
    return {
        "article_type": type_decision.value,
        "article_type_confidence": round(type_decision.confidence, 3),
        "verdict": a.verdict,
        "topic_confidence": round(a.confidence, 3),
        "topic": c.topic,
        "question_id": c.question_id,
        "environment_hits": list(a.environment_hits),
        "outcome_hits": list(a.outcome_hits),
        "reasons": list(a.reasons),
    }

def make_pdf(text: str) -> bytes:
    body = text.encode("latin-1", errors="replace")
    stream = b"BT /F1 12 Tf 50 750 Td (" + body[:200].replace(b"(", b"").replace(b")", b"") + b") Tj ET"
    obj3 = b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"
    obj1 = b"<< /Type /Catalog /Pages 2 0 R >>"
    obj2 = b"<< /Type /Pages /Kids [4 0 R] /Count 1 >>"
    obj4 = b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 3 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>"
    parts = [obj1, obj2, obj3, obj4]
    body_parts = []; offsets = []; offset = len(b"%PDF-1.4\n")
    for i, p in enumerate(parts):
        obj_bytes = str(i+1).encode() + b" 0 obj\n" + p + b"\nendobj\n"
        offsets.append(offset); body_parts.append(obj_bytes); offset += len(obj_bytes)
    xref_offset = offset
    xref = b"xref\n0 5\n0000000000 65535 f \n"
    for o in offsets:
        xref += str(o).zfill(10).encode() + b" 00000 n \n"
    trailer = b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n" + str(xref_offset).encode() + b"\n%%EOF"
    return b"%PDF-1.4\n" + b"".join(body_parts) + xref + trailer

HERE = Path(__file__).parent

TESTS = [
    {
        "name": "Test 1 — On-topic empirical (nature + attention)",
        "pdf_text": "Effects of natural environment and green space exposure on directed attention. Randomized experiment N=80 participants. Results p<0.01. Attention task. Methods: ANOVA between-subjects. Nature, vegetation, biophilic design.",
        "expected_verdict": ("accept", "edge_case"),
        "expected_type": "empirical_research",
        "should_store": True,
    },
    {
        "name": "Test 2 — Off-topic (ML paper)",
        "pdf_text": "Deep learning for image classification using convolutional neural networks. ImageNet. Batch normalization gradient descent. No participants no environment.",
        "expected_verdict": ("reject",),
        "expected_type": None,
        "should_store": False,
    },
    {
        "name": "Test 3 — Edge case (nature + no attention outcome, theoretical)",
        "pdf_text": "Biophilic design and natural environment in workplace architecture: a theoretical review. We argue that green space and vegetation in office buildings promotes wellbeing. Conceptual framework, no empirical measurement, no participants, no attention task.",
        "expected_verdict": ("edge_case",),
        "expected_type": "theoretical",
        "should_store": True,
    },
    {
        "name": "Test 4 — Citation only (no PDF)",
        "citation": "Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. Journal of Environmental Psychology, 15(3), 169–182.",
        "expected_verdict": ("accept", "edge_case", "reject"),
        "expected_type": None,
        "should_store": None,  # varies
    },
]

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

print("=" * 70)
print("TASK 1 VALIDATION MATRIX")
print("=" * 70)

all_pass = True
for t in TESTS:
    print(f"\n{t['name']}")
    if "citation" in t:
        # Citation-only: parse title
        import re
        title_match = re.match(r'^(.+?)\s*\(\d{4}\)\.\s*(.+)', t["citation"])
        title = title_match.group(2).split(".")[0].strip() if title_match else t["citation"][:100]
        result = run_classifier(title, "")
        print(f"  Parsed title: {title}")
    else:
        content = make_pdf(t["pdf_text"])
        text = extract_pdf_text(content)
        words = text.split()
        title = " ".join(words[:10])
        result = run_classifier(title, text[:3000])

    verdict = result["verdict"]
    atype   = result["article_type"]
    aconf   = result["article_type_confidence"]
    tconf   = result["topic_confidence"]
    topic   = result["topic"]
    store   = verdict in ("accept", "edge_case")

    verdict_ok = verdict in t["expected_verdict"]
    type_ok    = t["expected_type"] is None or atype == t["expected_type"]
    store_ok   = t["should_store"] is None or store == t["should_store"]

    row_pass = verdict_ok and type_ok and store_ok
    if not row_pass:
        all_pass = False

    print(f"  verdict:      {verdict:12s}  expected: {t['expected_verdict']}  -> {PASS if verdict_ok else FAIL}")
    print(f"  article_type: {atype:20s}  conf: {aconf*100:.0f}%")
    print(f"  topic:        {topic or 'none':30s}  conf: {tconf*100:.0f}%")
    print(f"  store?:       {str(store):5s}  expected: {t['should_store']}  -> {PASS if store_ok else FAIL}")
    print(f"  env_hits:     {result['environment_hits']}")
    print(f"  out_hits:     {result['outcome_hits']}")

print("\n" + "=" * 70)
print(f"OVERALL: {'ALL PASS' if all_pass else 'SOME FAILURES — see above'}")
print("=" * 70)
