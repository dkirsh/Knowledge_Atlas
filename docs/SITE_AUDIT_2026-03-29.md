# Knowledge Atlas Site Audit — 2026-03-29

*Comprehensive read-only audit of all 30 HTML pages. Every page inspected for stubs, dead links, placeholder content, inactive elements, and backend dependencies.*

---

## Executive Summary

**30 pages audited.** 22 are production-ready or nearly so. 8 have significant stub content. Of the issues found, **14 are fixable without a running backend** and **19 require backend integration**.

| Category | Count |
|----------|-------|
| Production-ready pages | 22 |
| Pages with stub/incomplete sections | 8 |
| Issues fixable without backend | 14 |
| Issues requiring backend | 19 |
| Total dead `href="#"` links across site | ~25 |
| Pages with `localhost:8765` dependency | 5 |

---

## Tier 1: Production-Ready (No Blocking Issues)

These pages work now. Ship them.

| Page | Lines | Assessment |
|------|-------|------------|
| ka_home.html | 900+ | Public landing; 5 hash-anchor stubs (#theory, #about) — minor |
| ka_user_home.html | 850+ | Auth home; graceful demo fallback |
| ka_workflow_hub.html | 700+ | Step player; fully self-contained, no dead links |
| ka_topics.html | 723 | 100% functional; filtering, sorting, cards |
| ka_gaps.html | 1336 | 100% functional; bookmarking, hypothesis links |
| ka_sensors.html | 1299 | 100% functional; instrument catalogue |
| ka_evidence.html | 1807 | 98%; one dead "Clear filters" link |
| ka_question_maker.html | 734 | 100%; 3-column builder, integrated from 4 pages |
| ka_sitemap.html | 1132 | 100%; master navigation index |
| ka_schedule.html | 682 | 100%; 10-week course schedule |
| ka_student_setup.html | 941 | 100%; setup guide |
| ka_tag_assignment.html | 826 | 100%; bundle claiming |
| ka_article_finder_assignment.html | 723 | 100%; Track 2 workflow |
| ka_gui_assignment.html | 1035 | 100%; Track 4 workflow |
| ka_vr_assignment.html | 1076 | 100%; Track 3 workflow |
| ka_thursday_tasks.html | 535 | 100%; discovery session |
| ka_ai_methodology.html | 1140 | 100%; 8 methods documented |
| ka_login.html | ~500 | Auth form; demo fallback |
| ka_register.html | ~500 | Multi-track registration |
| ka_warrants.html | 1633 | NEW — sensitivity simulator |
| ka_annotations.html | 1324 | REBUILT — full inspector with admin add |
| ka_argumentation.html | 1710 | REBUILT — Critique/Support CTAs |
| ka_interpretation.html | 1310 | REBUILT — VOI terrain map |

---

## Tier 2: Fixable Without Backend (Do Now)

| # | Page | Issue | Fix |
|---|------|-------|-----|
| 1 | ka_home.html | `href="#theory"` and `href="#about"` (5 instances) — no target sections exist | Link #theory → ka_topics.html; link #about → ka_ai_methodology.html |
| 2 | ka_evidence.html line 910 | `href="#"` on "Clear all filters" — page reloads on click | Change to `<button>` with onclick handler |
| 3 | ka_articles.html line 1252 | DOI link `href="#"` should be external | Change to `href="https://doi.org/10.1080/00140130802283516"` |
| 4 | ka_demo_v04.html line 450 | Wordmark `href="#"` | Link to ka_home.html |
| 5 | ka_demo_v04.html lines 1029-1146 | 6 dead citation reference links | Either link to DOI or remove href |
| 6 | ka_demo_v04.html lines 536-541 | 5 non-functional tab links | Disable tabs with "Coming soon" tooltip or hide |
| 7 | ka_demo_v04.html lines 516-521 | 6 dead user menu items | Hide non-functional items |
| 8 | ka_approve.html line 992 | Hardcoded "TBD" in capacity text | Use template pattern from line 1273 |
| 9 | ka_forgot_password.html line 69 | Dev helper link `href="#"` | Bind to dynamic URL (JS exists at line 114) |
| 10 | ka_dashboard.html lines 939-940 | Dead track overview/assignment links | Link to actual track assignment pages |
| 11 | ka_home.html | Warrants inspector missing from "Operational Layers" pillar section | DONE — fixed in this session |
| 12 | ka_dashboard.html | Warrants inspector missing from sidebar nav | DONE — fixed in this session |
| 13 | ka_sitemap.html | Warrants inspector missing from layer cards | DONE — fixed in this session |
| 14 | ka_schedule.html line 386 | Misleading comment "WEEKS 4-7 as collapsed placeholders" (they're actually present) | Update comment |

---

## Tier 3: Requires Backend (Prioritized)

| Priority | Page | Issue | Backend Needed |
|----------|------|-------|----------------|
| **P1** | ka_dashboard.html | All 11 student progress counters show "0" | `GET /api/student/progress` from auth server (port 8765) |
| **P1** | ka_demo_v04.html | Science Summary modals open with placeholder content | `GET /api/qa/summary/{belief_id}` |
| **P1** | ka_article_search.html | All 3 search mode buttons disabled | `POST /api/search/{mode}` |
| **P2** | ka_articles.html | "Reject" buttons (6 instances) have no handler | `POST /api/articles/reject/{paper_id}` |
| **P2** | ka_articles.html | Submit Evaluation / Save Draft / Flag buttons unwired | `POST /api/articles/evaluate` |
| **P2** | ka_hypothesis_builder.html | Form submission and state persistence missing | `POST /api/hypothesis/save` |
| **P2** | ka_tagger.html | Tagset vocabulary section disabled | `GET /api/tagset/vocabulary` |
| **P2** | ka_article_propose.html | "Stage for nightly review" button disabled | `POST /api/articles/stage` |
| **P3** | ka_approve.html | Search handler for applicant lookup | `GET /api/approve/search` |
| **P3** | ka_demo_v04.html | User menu items (Profile, Settings, etc.) | Full user account system |
| **P3** | 5 pages | `localhost:8765` hardcoded | Environment-based config |

---

## Tier 4: User Story Pathways (Missing)

No page currently asks a question that naturally routes a researcher or experiment designer to the inspector pages. The following pathways should exist:

| User Story | Entry Point | Destination | CTA Text |
|------------|-------------|-------------|----------|
| "What's the most contested claim in my research area?" | ka_topics.html (topic card) | ka_argumentation.html | "See debate structure →" |
| "Where's the biggest gap my experiment could fill?" | ka_gaps.html (gap card) | ka_interpretation.html | "See frontier questions →" |
| "How strong is this evidence — what type of warrant?" | ka_evidence.html (evidence row) | ka_warrants.html | "Inspect warrant strength →" |
| "Has anyone challenged this finding?" | ka_evidence.html (evidence row) | ka_argumentation.html | "See critiques →" |
| "What annotations flag this belief?" | ka_gaps.html or ka_evidence.html | ka_annotations.html | "See flags and notes →" |
| "What would change if we had mechanism evidence?" | ka_warrants.html (sensitivity) | ka_interpretation.html | "See frontier impact →" |
