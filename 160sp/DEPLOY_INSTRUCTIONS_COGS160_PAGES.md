# Deployment Instructions: COGS 160 Demo Pages

**Created**: 2026-04-06
**Author**: CW (Claude Code, Cowork session)
**For**: Any AI worker (Codex, Claude Code, AG) deploying these pages to xrlab.ucsd.edu

---

## Files to Deploy

Three new pages were created in `160sp/` and need to be completed and deployed to the live server at `xrlab.ucsd.edu/ka/160sp/`.

| File | Purpose | Status |
|------|---------|--------|
| `ka_technical_setup.html` | Student environment setup guide (AI tools, Git, context files) | 90% complete |
| `demo_pdf_relevance_filter.html` | Live demo: PDF relevance filter with 7-step method walkthrough | 85% complete |
| `ex0_mechanism_pathway_tracer.html` | Exercise 0: D3.js mechanism pathway visualization | 85% complete |

One new data file was also created:

| File | Purpose | Status |
|------|---------|--------|
| `data/ka_payloads/question_bank.json` | 130 K-ATLAS questions exported from ae.db `question_bank_student` table | Complete |

---

## What Needs Fixing on the Server

### 1. `demo_pdf_relevance_filter.html`

**Question bank dropdown does not populate without the JSON file.**

The page fetches questions from:
```javascript
const resp = await fetch('../data/ka_payloads/question_bank.json');
```

This file (`question_bank.json`) was exported from `ae.db` and placed in `data/ka_payloads/`. Verify it exists on the server at:
```
xrlab.ucsd.edu/ka/data/ka_payloads/question_bank.json
```

If it is missing, regenerate it:
```python
import sqlite3, json

db = sqlite3.connect('path/to/ae.db')
db.row_factory = sqlite3.Row
questions = db.execute('''
    SELECT question_id, question_text, topic, subtopic, difficulty, description, search_hints
    FROM question_bank_student ORDER BY topic, question_id
''').fetchall()

qlist = []
for q in questions:
    d = dict(q)
    try:
        d['search_hints'] = json.loads(d['search_hints']) if d['search_hints'] else []
    except:
        d['search_hints'] = []
    qlist.append(d)

with open('data/ka_payloads/question_bank.json', 'w') as f:
    json.dump({'questions': qlist, 'count': len(qlist)}, f, indent=2)
```

**Topic keyword coverage is incomplete.**

The `TOPIC_KEYWORDS` object in the JavaScript only covers 8 of 34 topics:
- Attention Restoration Theory
- Stress Recovery Theory
- Lighting
- Acoustic Environment
- Urban Green Space
- Views of Nature
- Color Psychology
- Biophilia

The remaining 26 topics (Neural Mechanisms, Research Methods, Healthcare Design, Educational Design, Workplace Design, Theory Comparison, Social Interaction, Specific Populations, Sensory Design, Residential Design, Place Attachment, Crowding and Privacy, Creativity and Cognition, Active Design, Materials and Form, Environmental Justice, Spatial Complexity, Fractal Patterns, Water Features, Thermal Comfort, Replication Crisis, Post-Occupancy Evaluation, Indoor Air Quality, Daylighting, Cultural Variation, ART vs SRT) fall through to the fallback that extracts keywords from the question text. This works but is imprecise.

**TODO**: Add keyword banks for at least the top 10 remaining topics. Each needs:
```javascript
'Topic Name': {
    env: ['environment-side keywords...'],
    outcome: ['outcome-side keywords...'],
    exclude_false: ['false-match terms to reject...']
}
```

Source the keywords from:
- The question bank's `search_hints` field (good starting point)
- The `articles.json` `primary_topic` field (shows the IV→DV structure)
- The existing corpus: what environment/outcome terms appear in papers assigned to each topic

**DV extraction is heuristic.**

The `extractQuestionDVs()` function matches against a fixed list of 23 common DV terms. For questions about less common outcomes (e.g., "social cohesion", "wayfinding", "thermal sensation"), it will miss them. Consider:
- Parsing the question text more aggressively (extract nouns after "affect", "influence", "improve", "reduce")
- Adding topic-specific DV lists alongside the keyword banks

**Nav links.**

The page currently has no site navigation bar. Add the standard K-ATLAS nav from `ka_student_setup.html` or `week2_exercises.html` so students can navigate back to the course pages. The nav HTML and JS includes are:
```html
<nav>
  <a href="../ka_home.html" class="nav-brand">Knowledge Atlas</a>
  <div class="nav-center">
    <a href="../ka_topics.html" class="nav-link">Explore</a>
    <a href="../ka_evidence.html" class="nav-link">Evidence</a>
    <a href="../ka_gaps.html" class="nav-link">Gaps</a>
    <a href="../ka_article_search.html" class="nav-link">Articles</a>
    <a href="../ka_contribute.html" class="nav-link">Contribute</a>
    <a href="ka_student_setup.html" class="nav-link active">Course</a>
  </div>
</nav>
```

And at the bottom:
```html
<script src="../ka_mode_switch.js"></script>
<script src="../ka_site_shell.js"></script>
```

### 2. `ex0_mechanism_pathway_tracer.html`

**Data fetch path.**

The page fetches:
```javascript
const resp = await fetch('../data/ka_payloads/argumentation.json');
```

Verify `argumentation.json` is accessible at `xrlab.ucsd.edu/ka/data/ka_payloads/argumentation.json`. This file should already exist (it's used by ka_argumentation.html).

**Nav bar missing.** Same fix as above — add the standard K-ATLAS nav.

**Graph layout could be improved.** The current layout is simple left-to-right with fixed spacing. For paths longer than 4 nodes, nodes can overflow the container width. Consider:
- Making `hSpacing` responsive to path length
- Adding horizontal scrolling for very long paths
- Using a D3 force layout instead of manual positioning for complex graphs

**Attack node positioning.** Attack nodes are placed at fixed Y offsets above/below the path. When multiple attacks target the same node, they can overlap. A force-directed layout for attack nodes would fix this.

### 3. `ka_technical_setup.html`

**GitHub repo URL is a placeholder.**

The page links to:
```
https://github.com/dkirsh/Knowledge_Atlas
```

Replace with the actual GitHub organization/repo URL once the repo is public. If using a different GitHub username or org, update all occurrences (there are 3: Option A link, clone command, upstream remote command).

**Track 5 is missing from the track grid.**

The existing site has Tracks 1-4 in the `ka_student_setup.html` grid, but Week 2 exercises also assign Teams to Track 5 (QA/Trust). The `ka_technical_setup.html` Section 8 mentions Track 5 in an accordion but there is no `ka_track5_qa.html` page yet. Either create one or link Track 5 students to the relevant exercises (A and C).

**Context file index link.**

Section 4 links to `context/index.html`. Verify this file exists on the server. It was present in the local repo.

**AI tool free-tier limits.**

The page says "The free tier gives you a limited number of messages per day." This is vague. Check current limits for Claude free tier and ChatGPT free tier and add specific numbers if possible, or at minimum say "check the tool's website for current limits."

---

## Linking These Pages into the Site

### Add to week2_exercises.html

The PDF Relevance Filter demo should be linked from the exercises page. Add a new exercise card BEFORE Exercise 0, or replace Exercise 0 with it as the primary demo:

```html
<!-- Before the Exercise 0 card -->
<div class="exercise-card">
  <div class="exercise-header demo">
    <div class="exercise-tag">Live Demo · Prof Kirsh</div>
    <div class="exercise-name">The Demo Task: PDF Relevance Filter</div>
    <div class="exercise-meta">Quality Control · ~40 min live · 7-Step Method</div>
  </div>
  <div class="exercise-body">
    <a href="demo_pdf_relevance_filter.html" class="context-link">
      🔗 Open interactive demo
    </a>
    <p>Prof Kirsh demonstrates the 7-step method by building a PDF relevance
    filter — the quality gate that determines whether a submitted paper
    provides evidence relevant to a K-ATLAS question.</p>
  </div>
</div>
```

### Add to ka_student_setup.html

Add a link to `ka_technical_setup.html` in the existing setup page. Currently `ka_student_setup.html` has 3 sections (Reading, Assignment, Track). Add a callout or button between sections:

```html
<div class="callout callout-info">
  <strong>Need help setting up your tools?</strong>
  See the <a href="ka_technical_setup.html">Technical Setup Guide</a>
  for step-by-step instructions on AI tools, Git, and your development environment.
</div>
```

### Update the nav "Setup" link

The nav currently points `Course` to `ka_student_setup.html`. Consider whether `ka_technical_setup.html` should be a sub-page (linked from setup) or a sibling (in the nav dropdown). The current design has it as a sub-page with breadcrumb navigation back to the orientation page.

---

## Data Dependencies Summary

| Page | Fetches | From |
|------|---------|------|
| `demo_pdf_relevance_filter.html` | `question_bank.json` | `../data/ka_payloads/question_bank.json` |
| `ex0_mechanism_pathway_tracer.html` | `argumentation.json` | `../data/ka_payloads/argumentation.json` |
| `ka_technical_setup.html` | Nothing | Static page, no data fetches |

Both JSON files must be accessible from the `160sp/` directory via relative paths. On the server, this means they should be at:
```
xrlab.ucsd.edu/ka/data/ka_payloads/question_bank.json
xrlab.ucsd.edu/ka/data/ka_payloads/argumentation.json
```

---

## Testing Checklist

After deploying, verify:

- [ ] `ka_technical_setup.html` loads with all sections, accordions work, tab switching works
- [ ] `demo_pdf_relevance_filter.html` loads and the question dropdown populates with 130 questions
- [ ] Selecting SQ-001 and clicking "Direct hit" example → run filter → shows ACCEPT with all 7 checks passing
- [ ] Selecting SQ-001 and clicking "Off-topic" → shows REJECT at Check 1
- [ ] Selecting SQ-001 and clicking "Adjacent but wrong DV" → shows MANUAL REVIEW with INDIRECT tier
- [ ] Selecting SQ-001 and clicking "False keyword match" → shows REJECT at Check 2
- [ ] `ex0_mechanism_pathway_tracer.html` loads and typing "noise" → "stress" → Trace shows a multi-step path
- [ ] Typing "unicorns" → "happiness" → shows "No mechanism chain found"
- [ ] All three pages display correctly on mobile (responsive layout)
- [ ] Nav links work (if nav bar has been added)
- [ ] Context file links from `ka_technical_setup.html` Section 4 table resolve correctly
