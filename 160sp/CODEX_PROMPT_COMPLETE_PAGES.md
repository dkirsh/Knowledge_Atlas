# Codex Terminal Prompt: Complete and Deploy COGS 160 Pages

**Context**: You have SSH access to `xrlab.ucsd.edu`. The course pages live at `/var/www/html/ka/160sp/` (adjust if the actual webroot differs — find it with `find / -path "*/ka/160sp" -type d 2>/dev/null`). There are three HTML pages that are 85–90% complete and need finishing before they can go live. There is also a deploy instructions file (`DEPLOY_INSTRUCTIONS_COGS160_PAGES.md`) in the same directory that has more granular detail — read it first.

---

## Prompt to paste into Codex / Claude Code terminal:

```
You are completing and deploying three COGS 160 course pages on xrlab.ucsd.edu. SSH into the server and work directly on the files. Read DEPLOY_INSTRUCTIONS_COGS160_PAGES.md first for full context.

The site root for Knowledge Atlas is /var/www/html/ka/ (or wherever the ka/ directory lives — locate it). The pages being completed are in the 160sp/ subdirectory.

## FILES TO COMPLETE

### 1. demo_pdf_relevance_filter.html (PDF Relevance Filter Demo)

This is the most important page. It's an interactive demo of a 7-check pipeline that determines whether a submitted paper is relevant to a K-ATLAS research question.

TASKS:
a) **Question bank data**: The page fetches `../data/ka_payloads/question_bank.json` — verify this file exists on the server. If missing, generate it from ae.db:
   ```python
   import sqlite3, json
   db = sqlite3.connect('/path/to/ae.db')  # find ae.db on the server
   db.row_factory = sqlite3.Row
   questions = db.execute('''
       SELECT question_id, question_text, topic, subtopic, difficulty, description, search_hints
       FROM question_bank_student ORDER BY topic, question_id
   ''').fetchall()
   qlist = []
   for q in questions:
       d = dict(q)
       try: d['search_hints'] = json.loads(d['search_hints']) if d['search_hints'] else []
       except: d['search_hints'] = []
       qlist.append(d)
   with open('data/ka_payloads/question_bank.json', 'w') as f:
       json.dump({'questions': qlist, 'count': len(qlist)}, f, indent=2)
   ```

b) **Add topic keyword banks for the remaining 26 topics**. Currently only 8 topics have keyword banks in the TOPIC_KEYWORDS JavaScript object (Attention Restoration Theory, Stress Recovery Theory, Lighting, Acoustic Environment, Urban Green Space, Views of Nature, Color Psychology, Biophilia). The other 26 topics fall through to a generic fallback that extracts keywords from the question text.

   For each missing topic, add an entry to TOPIC_KEYWORDS with this structure:
   ```javascript
   'Topic Name': {
       env: ['environment-side keywords...'],
       outcome: ['outcome-side keywords...'],
       exclude_false: ['false-match terms to reject...']
   }
   ```

   The missing topics are: Neural Mechanisms, Research Methods, Healthcare Design, Educational Design, Workplace Design, Theory Comparison, Social Interaction, Specific Populations, Sensory Design, Residential Design, Place Attachment, Crowding and Privacy, Creativity and Cognition, Active Design, Materials and Form, Environmental Justice, Spatial Complexity, Fractal Patterns, Water Features, Thermal Comfort, Replication Crisis, Post-Occupancy Evaluation, Indoor Air Quality, Daylighting, Cultural Variation, ART vs SRT.

   Source keywords from:
   - The question_bank.json `search_hints` field for each topic
   - The `articles.json` file if it exists (look at `primary_topic` fields)
   - Your knowledge of environmental psychology / evidence-based design literature

   Each topic needs at minimum 5 env keywords, 5 outcome keywords, and 2-3 false-match exclusions. Be precise — these determine whether papers are accepted or rejected.

c) **Improve DV extraction**. The `extractQuestionDVs()` function matches against a fixed list of ~23 common DV terms. Add topic-specific DV lists alongside the keyword banks. For example, for Thermal Comfort the DVs should include "thermal sensation," "thermal comfort," "PMV," "PPD." For Crowding and Privacy, DVs should include "perceived crowding," "privacy," "personal space," "density."

d) **Add the standard K-ATLAS nav bar** at the top of the page. Copy the nav HTML from ka_student_setup.html — it looks like this:
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
   Also add at the bottom before </body>:
   ```html
   <script src="../ka_mode_switch.js"></script>
   <script src="../ka_site_shell.js"></script>
   ```
   Check that these JS files actually exist on the server before adding the script tags.

### 2. ex0_mechanism_pathway_tracer.html (Exercise 0: Mechanism Pathway Tracer)

TASKS:
a) **Data fetch path**: Verify `../data/ka_payloads/argumentation.json` is accessible on the server. This file should already exist (used by ka_argumentation.html).

b) **Add the standard K-ATLAS nav bar** — same as above.

c) **Graph layout improvement**: The current layout uses fixed left-to-right spacing. For paths longer than 4 nodes, nodes overflow the container. Fix by:
   - Making `hSpacing` responsive to path length: `hSpacing = Math.min(180, (containerWidth - 100) / pathLength)`
   - Adding `overflow-x: auto` to the SVG container for very long paths
   - Adjusting attack node positioning so multiple attacks on the same node don't overlap (use stacked Y offsets)

### 3. ka_technical_setup.html (Technical Setup Guide)

TASKS:
a) **GitHub repo URL**: Replace the placeholder `https://github.com/dkirsh/Knowledge_Atlas` with the actual repo URL. Search the server for a .git directory or ask — there should be 3 occurrences to update (Option A link, clone command, upstream remote command). If the real URL is not discoverable, leave a visible TODO comment.

b) **Track 5 (QA/Trust)**: The page mentions Track 5 in an accordion in Section 8 but there is no `ka_track5_qa.html`. Either:
   - Create a minimal placeholder page for Track 5 that links to Exercises A and C, OR
   - Update the Track 5 accordion to say "See Exercises A and C on the Week 2 page" with a link to week2_exercises.html

c) **Context file index**: Section 4 links to `context/index.html`. Verify this file exists on the server at 160sp/context/index.html.

d) **AI tool free-tier info**: The page says "The free tier gives you a limited number of messages per day." Replace with something more specific or at minimum: "Check the tool's website for current free-tier limits, which change frequently."

## LINKING INTO THE SITE

After completing the three pages:

a) **Add to week2_exercises.html**: Add a demo card for the PDF Relevance Filter BEFORE the Exercise 0 card:
   ```html
   <div class="exercise-card">
     <div class="exercise-header demo">
       <div class="exercise-tag">Live Demo · Prof Kirsh</div>
       <div class="exercise-name">The Demo Task: PDF Relevance Filter</div>
       <div class="exercise-meta">Quality Control · ~40 min live · 7-Step Method</div>
     </div>
     <div class="exercise-body">
       <a href="demo_pdf_relevance_filter.html" class="context-link">Open interactive demo</a>
       <p>Prof Kirsh demonstrates the 7-step method by building a PDF relevance
       filter — the quality gate that determines whether a submitted paper
       provides evidence relevant to a K-ATLAS question.</p>
     </div>
   </div>
   ```

b) **Add to ka_student_setup.html**: Add a callout linking to the technical setup guide:
   ```html
   <div class="callout callout-info">
     <strong>Need help setting up your tools?</strong>
     See the <a href="ka_technical_setup.html">Technical Setup Guide</a>
     for step-by-step instructions on AI tools, Git, and your development environment.
   </div>
   ```

## TESTING CHECKLIST

After all changes, verify each of these manually in a browser:

- [ ] demo_pdf_relevance_filter.html loads and the question dropdown populates (should show 130 questions)
- [ ] Select SQ-001, click "Direct hit" example, run filter → ACCEPT with all 7 checks passing
- [ ] Select SQ-001, click "Off-topic" → REJECT at Check 1
- [ ] Select SQ-001, click "Adjacent but wrong DV" → MANUAL REVIEW, tier INDIRECT
- [ ] Select SQ-001, click "False keyword match" → REJECT at Check 2
- [ ] ex0_mechanism_pathway_tracer.html loads; type "noise" → "stress" → Trace shows a multi-step path
- [ ] Type "unicorns" → "happiness" → shows "No mechanism chain found"
- [ ] ka_technical_setup.html loads, all accordion sections expand/collapse, tab switching works
- [ ] Nav links work on all three pages
- [ ] All three pages display correctly on mobile (test at 375px width)
- [ ] Context file links from ka_technical_setup.html Section 4 resolve correctly
- [ ] week2_exercises.html shows the new demo card
- [ ] ka_student_setup.html shows the new callout linking to technical setup

## IMPORTANT NOTES

- Do NOT change any existing CSS class names or IDs — other pages depend on them
- Do NOT modify files outside the 160sp/ directory and data/ka_payloads/ unless you are certain
- Preserve the existing visual style (navy/teal/amber/cream palette, Georgia headings, etc.)
- If ae.db cannot be found, check common locations: /var/www/html/ka/data/, /home/*/ka/data/, or ask
- Back up any file before editing: `cp filename.html filename.html.bak`
```
