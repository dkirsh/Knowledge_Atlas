# Track 2 Context — `ka_contribute_public.html`

---

# Plain English Overview — What Are These Three Programs?

This project has three separate pieces of code. Think of them like three rooms in a building that are supposed to be connected by doors — but right now the doors have not been installed. Each room is well-built; they just do not talk to each other yet.

---

## Key Terms (Jargon Glossary)

Before the three parts, here are the words that keep appearing and what they actually mean.

**localStorage** — Your browser has a small private notepad built into it. Websites can write notes there and read them back later, but only in that same browser on that same computer. Nobody else can see it. It is not a server, not a database, and not the internet.

**fetch() / POST request** — The way a webpage sends data to a server over the internet. When you click "buy" on Amazon, the page uses a fetch to send your order to Amazon's servers. Without a fetch call, data never leaves your browser.

**FormData** — A special package that a browser can build to send files (like PDFs) along with text fields in one network request. Without FormData, you can send text but not file contents.

**API endpoint** — A specific URL on a server that is set up to receive a certain kind of request and do something with it. For example, `POST /api/articles/submit` is an endpoint that expects to receive a paper submission. Think of it as a named slot in a mailroom drop box.

**multipart/form-data** — The format used when sending a mix of text fields and file uploads in one request. It is required any time you need to send actual file bytes (not just a filename) over the network.

**DOI** — Digital Object Identifier. A permanent ID for an academic paper, like `10.1016/j.jenvp.2014.02.003`. Every major paper has one. If you have a DOI, you can look up the title, authors, and abstract automatically from a public database.

**quarantine** — A holding folder on the server for newly uploaded PDFs that have not yet been approved. Nothing in quarantine is visible to the public or enters the main database. A reviewer has to approve it first.

**deduplication** — Checking whether the paper being submitted is one that has already been submitted. The system does this by comparing SHA-256 hashes (a fingerprint of the file's bytes), DOIs, and titles.

**SHA-256 hash** — A mathematical fingerprint of a file. If two PDFs have the same SHA-256 hash, they are byte-for-byte identical. If even one character differs, the hashes are completely different. Used here to catch duplicate uploads.

**constitution bank** — The Atlas's master list of research topics (daylight, noise, ceiling height, etc.), each described with a set of keywords and inclusion/exclusion terms. The classifier checks each paper against every topic in this list.

**confidence score** — A number between 0 and 1 that the classifier outputs alongside its verdict. 0.95 means "very sure." 0.35 means "guessing." Below 0.72, the system flags the paper for human review instead of routing it automatically.

**next_action** — The classifier's output recommendation: what should happen to this paper next? Options include "ready to extract," "needs more evidence," or "send to a human reviewer."

**FastAPI / APIRouter** — FastAPI is the Python framework the KA server is built on (similar to how WordPress is a framework for websites). APIRouter is a FastAPI tool for grouping related endpoints together in one file.

---

## Part 1 — The Web Form (`ka_contribute_public.html`)

**What it is:** A webpage with a form on it. Anyone can go to this page, drop a PDF of a research paper, type in a citation, and click "Send suggestion." It is the public-facing front door of the contribution system.

**What it's supposed to do:** Take the PDF and any text you typed, send it across the internet to the Knowledge Atlas server, and give you a submission ID so you can track whether your paper was accepted.

**What it actually does right now:** Nothing useful. When you click "Send suggestion," the JavaScript code reads the filename of your PDF (just the name, like `boubekri_2014.pdf`, not the actual contents), packs it into a small object along with your typed text, and saves that object to `localStorage` — your browser's private notepad. The PDF bytes are never read. No network request is made. The thank-you modal pops up after half a second no matter what, even if localStorage itself throws an error. Close the tab and everything vanishes. No one at Knowledge Atlas ever sees anything.

**Analogy:** It is like a suggestion box where the slot looks real but leads directly into a trash can hidden inside the wall. You put your note in, it disappears, and the box says "Thank you!" regardless.

**Where the code lives:** The entire form logic is in a single `<script>` block at the bottom of the HTML file — two functions, `handleFiles()` and `submitSuggestion()`, about 40 lines total.

---

## Part 2 — The Classifier (`classifier_system.py`)

**What it is:** A Python program that reads information about a research paper and makes two decisions: (1) what *type* of paper is it (empirical experiment, review article, theoretical, meta-analysis, etc.), and (2) what *topic* does it belong to in the Atlas (daylight and cognition, ceiling height and creativity, noise and stress, thermal comfort, etc.).

**What it's supposed to do:** Every paper that gets submitted needs to be sorted and labeled before it can be added to the Atlas. The classifier is the automated sorting machine that does this work so reviewers don't have to read every paper from scratch.

**How it decides article type:**
- It is handed a paper's title, abstract, keywords, and optionally the full PDF.
- It reads through all that text looking for signal words. Phrases like "systematic review" or "meta-analysis" strongly suggest a review paper. Words like "participants," "randomized," "experiment," and "results" together suggest an empirical study. Phrases like "theoretical framework" or "we propose" suggest a theoretical paper.
- Each match raises the confidence score. The first label to cross a high enough threshold wins.

**How it decides topic:**
- It runs two systems in parallel. First, it checks the paper against every topic in the "constitution bank" — the Atlas's master list of research topics. Each topic has keywords and inclusion/exclusion terms; the paper's full text is scanned for matches and scored. The highest-scoring topic becomes the primary topic.
- Second, if the caller passes in an "active overlay" (a custom short list of topics to check against), those get phrase-matched too and returned as a ranked list.

**What it outputs:** An `AdaptiveClassificationResult` — a structured object containing the article type, its confidence score, the best-matching topic, a summary of which topics it matched, and a `next_action` recommendation telling the pipeline what to do next.

**What it cannot do on its own:** It cannot receive files from the internet. It has no web server, no URL, no way for a browser to talk to it directly. It is purely a Python function — it needs a server (Part 3) to receive the submission first and then hand the paper to it.

**Analogy:** A highly trained librarian sitting in a back room with no phone and no door to the street. You walk papers to them, they read, classify, and shelve. Nobody is currently walking papers to them.

---

## Part 3 — The Backend Server (`ka_article_endpoints.py`)

**What it is:** A Python web server module (using FastAPI) that sits between the web form and the classifier. It defines real, reachable URLs (endpoints) that the form can POST data to, and it orchestrates everything that needs to happen when a paper arrives.

**What it does step by step when a PDF arrives:**
1. Reads the uploaded file bytes and checks the "magic bytes" — the first 5 characters of every real PDF are `%PDF-`. If they are not there, the file is rejected immediately regardless of what its name says.
2. Computes a SHA-256 hash (fingerprint) of the file and checks the database — if this exact file has been submitted before, it is flagged as a duplicate and stopped.
3. Checks the DOI (if extractable) and the title (fuzzy match) against existing papers for a second layer of duplicate detection.
4. Saves the PDF to the quarantine folder with a new name (`KA-ART-000042.pdf`) — the original filename is never used for storage.
5. Parses the citation text you typed (if any) using a regex-based APA parser to extract title, authors, year, and DOI.
6. Calls the classifier (`AdaptiveClassifierSubsystem.classify()`) with everything it has so far. If the `atlas_shared` package is not installed, it automatically falls back to a simpler built-in classifier.
7. Writes the submission record to a SQLite database with full provenance — who submitted, when, what the classifier decided, current status.
8. Writes an entry to the audit log so every state change is permanently recorded.
9. Returns a JSON response with a `submission_id` (like `KA-IN-000042`) and a per-paper `article_id` (like `KA-ART-000042`) that the submitter can use to check status later.

**What it already has built and working:** The database schema (four tables: articles, submission_batches, audit_log, question_claims), the storage folder structure (quarantine / pdf_collection / rejected), PDF magic-byte validation, size enforcement (100 MB cap), SHA-256 deduplication, APA citation parsing, DOI extraction, the classifier call with fallback, and all seven endpoints including the instructor review workflow that promotes a paper from quarantine into the extraction pipeline.

**What it is missing:** It is not yet registered in the main auth server (`ka_auth_server.py`). The `configure()` function that wires up the shared database connection and user authentication has not been called. So the endpoints exist in the code but the server does not know to serve them yet.

**Analogy:** A fully staffed and equipped mailroom — receiving desk, security scanner, filing system, sorting machine, shelving. The building is built. The mailroom is ready. The front door of the building (the web form) just does not send mail to it yet.

---

## Why Nothing Works End-to-End Right Now

There are exactly two missing connections:

**Connection A (most important):** The web form does not send data to the server. `submitSuggestion()` writes to `localStorage` instead of calling `fetch()`. Fixing this is roughly 10 lines of JavaScript: build a `FormData` object with the PDF bytes and text fields attached, then POST it to `window.__KA_CONFIG__.apiBase + "/api/articles/submit"`.

**Connection B (also needed):** The server module (`ka_article_endpoints.py`) is not plugged into the main server (`ka_auth_server.py`). The router needs to be imported and the `configure()` function needs to be called with the shared database and user dependencies. Without this, the endpoint URL does not exist even though the code is written.

Fix both of those and the full pipeline is live: **Form → Server → Classifier → Database → Reviewer queue → pdf_collection → Extraction pipeline.**

---

## Boxology Diagram

```
╔══════════════════════════════════════════════════════════════════╗
║   CURRENT BEHAVIOUR  (ka_contribute_public.html)                ║
╚══════════════════════════════════════════════════════════════════╝

  ┌──────────────────────────────────────────────────────────────┐
  │                           USER                               │
  │   drops PDF · types citation · types why · types email       │
  └──────────────────────────────────────────────────────────────┘
       │ PDF file
       ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  handleFiles()                                               │
  │                                                              │
  │  Stores the File object in memory and shows filename on      │
  │  screen. File bytes are NEVER read or touched.               │
  └────────────────────────┬─────────────────────────────────────┘
                           │ filename string only
                           │ (citation / why / email pass through too)
                           ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  submitSuggestion()                                          │
  │                                                              │
  │  payload = {                                                 │
  │    filename:     "paper.pdf"   ← name only, bytes discarded  │
  │    citation:     <text field>                                │
  │    why:          <text field>                                │
  │    email:        <text field>                                │
  │    submitted_at: <ISO timestamp>                             │
  │  }                                                           │
  └──────────────────┬───────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
  ┌────────────────────┐  ┌─────────────────────────────────────┐
  │  localStorage      │  │  setTimeout(500 ms)                 │
  │                    │  │                                     │
  │  ⚠ DEAD END        │  │  ⚠ ALWAYS fires — even if the       │
  │                    │  │    localStorage write threw         │
  │  Payload saved to  │  │    an error                         │
  │  this browser only │  │                                     │
  │  No reviewer sees  │  │  Opens the thank-you modal          │
  │  it. Gone on tab   │  │  unconditionally                    │
  │  close.            │  └─────────────────────────────────────┘
  └────────────────────┘

  ─── Net result ────────────────────────────────────────────────
  PDF bytes       → discarded
  Network request → never made
  Reviewer queue  → never reached
  Submission      → lost when tab closes
  ───────────────────────────────────────────────────────────────


╔══════════════════════════════════════════════════════════════════╗
║   WHAT IS MISSING  (the unbuilt connections)                    ║
╚══════════════════════════════════════════════════════════════════╝

  ┌──────────────────────────────────────────────────────────────┐
  │  submitSuggestion()  needs these additions:                  │
  └────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  ✗  Step 1 — Build FormData with actual file bytes           │
  │                                                              │
  │     const fd = new FormData()                                │
  │     fd.append("files",    chosenFile)  ← real PDF bytes      │
  │     fd.append("citations", citation)                         │
  │     fd.append("notes",    why)                               │
  │     fd.append("email",    email)                             │
  └────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  ✗  Step 2 — Send over the network                           │
  │                                                              │
  │     fetch(window.__KA_CONFIG__.apiBase                       │
  │           + "/api/articles/submit",                          │
  │           { method: "POST", body: fd })                      │
  └────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  ✗  Step 3 — Handle the response properly                    │
  │                                                              │
  │     200 OK    → show thank-you + article_id receipt          │
  │     4xx error → show what went wrong (duplicate, bad PDF)    │
  │     5xx/fail  → offer retry; do NOT open the thank-you modal │
  └────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  ka_article_endpoints.py — ALREADY BUILT, just not wired in  │
  │                                                              │
  │  POST /api/articles/submit                                   │
  │  ├─ validates magic bytes  (%PDF-)                           │
  │  ├─ deduplicates  (SHA-256 hash + DOI + title)               │
  │  ├─ saves PDF to quarantine/ folder                          │
  │  ├─ parses citation text  (APA / DOI / plain title)          │
  │  ├─ calls classifier → article type + topic                  │
  │  ├─ writes to SQLite database                                │
  │  └─ returns { submission_id, article_id, status }            │
  └──────────────────────────────────────────────────────────────┘

  ─── Also missing (smaller items) ─────────────────────────────
  ✗  Client-side file-size check before upload
  ✗  Way to remove or swap the chosen file before submitting
  ✗  Multi-file drop  (currently silently picks only files[0])
  ✗  Keyboard trap and Esc-to-close on the modal
  ───────────────────────────────────────────────────────────────
```

## Current State

`ka_contribute_public.html` is a **UI-only stub** of the public paper-suggestion flow. It renders the full intended interface — drag-and-drop PDF zone, citation/DOI textarea, "why this matters" field, optional email, and a "Send suggestion" button — and it gives the user every visual cue of a successful submission, including a "✓ filename — ready to send" confirmation and a thank-you modal.

What it *actually* does on submit: reads the four text fields, captures only the PDF's **filename string** (never the bytes), stamps an ISO timestamp, and appends that JSON object to `localStorage["ka.public_suggestions"]` in the user's own browser. After a hard-coded 500 ms `setTimeout` it unconditionally opens the thank-you modal.

What it does **not** do: there is no `fetch()`, no `FormData`, no use of `window.__KA_CONFIG__.apiBase` (despite `ka_config.js` being loaded), no PDF byte transmission, no backend endpoint, no validation beyond "is at least one of file-or-citation present," no error path (the modal opens even if storage throws), no dedupe check, no extraction of title/authors/abstract (despite the UI hint promising it), no submission ID, and no sink that any reviewer — DK or a COGS 160 Article Finder student — can read. The "What happens next" card describes a pipeline that is not wired up; the submission terminates in the submitter's own browser.

---

# Classifier System — `classifier_system.py`

## How Article Type Is Decided

**Class:** `AdaptiveClassifierSubsystem`
**Method:** `classify()` → delegates to `self.filter.classify_article_type(article)` (line 700)
**Underlying classifier:** `HeuristicArticleTypeClassifier` (default, from `.article_types`)
**Returns:** `ArticleTypeDecision` with a confidence score

**Data it looks at** — an `ArticleCandidate` built by `evidence.to_article_candidate()`, which packages:
- title, abstract, year
- keywords + topic_hints (merged)
- preliminary_article_type (any tag the upstream pipeline already set)
- body_text = full `_article_text()` blob: title + abstract + keywords + zotero tags +
  first-page text + surface-snapshot excerpts (raw / intro / methods / conclusion) +
  IV / DV / measurement / instrument / sensor terms + topic hints

## How Topic Is Decided

Two parallel systems run inside every `classify()` call:

**A. Stable topics — constitution bank**
- Method: `_assess_questions()` → `_build_stable_topic_routing()`
- For each `QuestionConstitution` loaded from `load_topic_constitution_bank()`, the
  `QuestionArticleRelevanceFilter.assess()` returns a `RelevanceAssessment`
  (verdict: accept / edge_case / reject, plus confidence).
- Assessments are grouped by `constitution.topic`, turned into `TopicBundleCandidate`s,
  scored by summed `_assessment_weight`, and the highest-scoring topic becomes `primary_topic`.
- Data: same `ArticleCandidate.body_text` blob.

**B. Active overlay topics — keyword/phrase matching**
- Class: `HeuristicTopicOverlayMatcher`
- Method: `match()` — caller passes in `active_topic_overlay` records at call time.
- For each overlay record, regex-searches lowercased `evidence.text_for_classification`
  for `label + keywords + inclusion_terms`.
- Score = `0.24 + 0.12 × hits + 0.08 (if label matched) − 0.12 × exclusion_hits`, capped at 0.96, threshold 0.2.
- Returns top-N `TopicOverlayMatch` objects.

## Boxology — Inside `classify()`

```
╔══════════════════════════════════════════════════════════════════╗
║   INSIDE classify()  (AdaptiveClassifierSubsystem)              ║
╚══════════════════════════════════════════════════════════════════╝

  INPUT
  ├─ evidence_like        paper metadata (plain dict or object)
  └─ active_topic_overlay optional short list of topics to check
                           │
                           ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  STEP 1 — Normalise input                                    │
  │                                                              │
  │  If a plain dict arrived, convert it to a typed              │
  │  ClassificationEvidence object so every downstream step      │
  │  gets the same field names and types.                        │
  └────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  STEP 2 — Assess how much information we have                │
  │                                                              │
  │  bibliographic_only  →  title / authors / year only          │
  │  metadata_text       →  also has abstract or keywords        │
  │  pdf_surface_light   →  also has first-page or PDF scan      │
  │  extraction_aware    →  also has IVs, DVs, measurements      │
  │                                                              │
  │  The stage controls how hard the classifier works next.      │
  └────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  STEP 3 — Extract PDF surface text  (only if needed)         │
  │                                                              │
  │  Skipped if:  stage is already pdf_surface or better,        │
  │               OR no pdf_path exists on disk.                 │
  │                                                              │
  │  Tool chain:  pdftotext (shell) → pypdf → PyPDF2  fallback   │
  │                                                              │
  │  Produces PDFSurfaceSnapshot:                                │
  │    raw text · section headings · intro excerpt               │
  │    methods excerpt · conclusion excerpt                      │
  └────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  STEP 4 — Pack all available text into one blob              │
  │                                                              │
  │  Combines:  title · abstract · keywords · zotero tags        │
  │    · first-page text · PDF excerpts (intro / methods /       │
  │    conclusion) · IVs · DVs · measurement terms               │
  │    · instrument terms · sensor terms · topic hints           │
  │                                                              │
  │  All three classifiers below read this same blob.            │
  └────────────────────────┬─────────────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
  ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
  │  A. ARTICLE TYPE  │ │  B. STABLE TOPIC  │ │  C. TOPIC OVERLAY │
  │                   │ │                   │ │                   │
  │  Scans blob for   │ │  Scores blob vs   │ │  Scores blob vs   │
  │  signal phrases:  │ │  every topic in   │ │  caller-supplied  │
  │                   │ │  constitution     │ │  topic list.      │
  │  "meta-analysis"  │ │  bank.            │ │                   │
  │  "systematic      │ │                   │ │  Score formula:   │
  │   review"         │ │  Each topic gets  │ │  0.24  base       │
  │  "participants"   │ │  a score by how   │ │  +0.12 per hit    │
  │  "randomized"     │ │  many keywords    │ │  +0.08 if label   │
  │  "we propose"     │ │  match.           │ │   matched exactly │
  │                   │ │                   │ │  -0.12/exclusion  │
  │  → article_type   │ │  Top score wins   │ │  Cap: 0.96        │
  │    + confidence   │ │  → primary_topic  │ │                   │
  │                   │ │  → candidates[]   │ │  → ranked list    │
  └────────┬──────────┘ └────────┬──────────┘ └────────┬──────────┘
           │                    │                      │
           └────────────────────┴──────────────────────┘
                                │
                                ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  STEP 5 — Compute overall_confidence                         │
  │                                                              │
  │  = max( article_type confidence,                             │
  │         best stable-topic confidence,                        │
  │         best overlay match score )                           │
  │                                                              │
  │  Score < 0.72  →  paper flagged for human review             │
  └────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  STEP 6 — Choose next_action                                 │
  │                                                              │
  │  need_abstract_or_keywords  →  go get more metadata first    │
  │  extract_pdf_surface        →  go read the PDF               │
  │  ready_for_intake_decision  →  enough info to decide now     │
  │  ready_for_downstream_      →  send to extraction pipeline   │
  │    extraction                                                │
  │  ready_for_topic_routing    →  assign to a topic bundle      │
  │  review_borderline_case     →  escalate to human reviewer    │
  └────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  OUTPUT — AdaptiveClassificationResult                       │
  │                                                              │
  │  article_type          what kind of paper  (empirical, etc.) │
  │  stable_topic_routing  which Atlas topic it belongs to       │
  │  active_topic_matches  overlay scores, ranked                │
  │  overall_confidence    0.0–1.0 certainty score               │
  │  next_action           what the pipeline does next           │
  │  stage_history         log of evidence gathered this run     │
  │  surface_snapshot      PDF text extracted (if any)           │
  └──────────────────────────────────────────────────────────────┘
```

---

# Integration Gap Statement

The contribute page (`ka_contribute_public.html`) currently captures a PDF drop, a citation string, a "why it matters" note, and an optional email, then writes only the filename string — never the bytes — to the submitter's own `localStorage` and unconditionally shows a thank-you modal; no data ever leaves the browser. The classifier (`AdaptiveClassifierSubsystem` in `classifier_system.py`) can accept that same evidence as a structured `ClassificationEvidence` mapping, extract a lightweight PDF surface via `LocalPDFSurfaceExtractor`, determine article type via `HeuristicArticleTypeClassifier`, route the paper to a primary topic via the constitution bank, and return a `next_action` that tells the pipeline what to do next. The existing backend (`ka_article_endpoints.py`) already implements `POST /api/articles/submit` with multipart file handling, SHA-256 deduplication, magic-byte PDF validation, APA citation parsing, quarantine storage, the full `articles` / `audit_log` database schema, and a classifier call that tries `atlas_shared.AdaptiveClassifierSubsystem` and falls back gracefully to a local heuristic. To finish the integration, we need exactly three things: (1) replace the `localStorage` write in `submitSuggestion()` with a `fetch()` POST to `window.__KA_CONFIG__.apiBase + "/api/articles/submit"` that attaches the PDF bytes via `FormData`; (2) surface the returned `article_id` in the thank-you modal so submitters have a receipt token; and (3) ensure `ka_auth_server.py` includes the `ka_article_endpoints` router and calls `configure()` so the dependency injection is live — at which point the two programs are fully connected with no new infrastructure required.

---

# Addendum (2026-05-17): Corrections after re-reading the code

While drafting the Phase-2 contract I re-read `ka_auth_server.py` and `ka_article_endpoints.py` line by line and found two claims in the body of this Phase-1 document that no longer match the code on this checkout. Adding them here as an addendum rather than rewriting the body, so the original analysis is preserved.

**Correction 1 — the router is already wired in `ka_auth_server.py`.** The Integration Gap Statement above says the third remaining step is to "ensure `ka_auth_server.py` includes the `ka_article_endpoints` router and calls `configure()`." On this checkout that step is *already complete*: see `ka_auth_server.py` lines 976–988, which import `ka_article_endpoints`, call `ka_article_endpoints.configure(get_db=…, get_current_user=…, …)`, and run `app.include_router(ka_article_endpoints.router)`. The `/api/articles/submit` route exists and is reachable; the gap is upstream of that, in the form.

**Correction 2 — the classifier is NOT actually called from `/api/articles/submit`.** The Integration Gap Statement says the backend "already implements … a classifier call that tries `atlas_shared.AdaptiveClassifierSubsystem` and falls back gracefully to a local heuristic." On this checkout that is half-true. The classifier IS imported at the module level (`ka_article_endpoints.py:154`) and the fallback chain (`atlas_shared` → local heuristic) is wired. There is also a helper `_classify_article_payload(...)` defined at line 1648 and called by *other* endpoints (`/api/student/classify-one`, etc.) at lines 1847, 2024, 2153. But inside the `submit_articles` handler (lines 648–919), the flow goes validation → SHA-256 dedup → quarantine write → `INSERT INTO articles` with `status='staged_pending_review'`, and **never calls `_classify_article_payload` or `.classify()`**. So the classifier integration is not "already implemented" inside `/submit`; adding that call is part of the Phase-2 PR's scope. The Classifier Integration Contract (Phase 2) lists this gap as condition 2 of §1, with invariant I-13 and structural check `STRUCT-classifier-call-site` verifying that the call lands inside `async def submit_articles`.

**What this changes about the three "remaining things" in the body above:** items (1) and (2) are still accurate. Item (3) is already done, and a new item (3′) — call the classifier inside `submit_articles` — replaces it as the actual remaining backend work.
