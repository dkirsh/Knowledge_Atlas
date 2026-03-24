/**
 * ka_demo_wiring.js
 * Knowledge Atlas — Demo Navigation Wiring
 *
 * Provides:
 *  1. A "Coming Soon" modal that appears whenever a button or link would
 *     require a live backend. Each element can carry data attributes that
 *     describe what *would* happen in a live system.
 *
 *  2. Demo login routing — navigates to ka_dashboard.html on any login
 *     form submission (demo mode: any non-empty email).
 *
 *  3. Auto-wires common patterns across all pages so navigation feels
 *     continuous to a first-time reviewer.
 *
 * Usage: include <script src="ka_demo_wiring.js"></script> at the END of
 * each page, after all other scripts.
 *
 * To mark an element as "coming soon", add:
 *   data-coming-soon="true"
 *   data-cs-title="Save Hypothesis"            (optional — header text)
 *   data-cs-live="POST /api/hypotheses"        (what happens live)
 *   data-cs-source="hypotheses table, student_id FK"  (where data lives)
 *   data-cs-phase="Phase 3 — User Management"  (critical path phase)
 *
 * Or call: window.KA.showComingSoon({ title, live, source, phase })
 */

(function () {
  'use strict';

  /* ─── CSS ─────────────────────────────────────────────────────────────── */
  const CSS = `
    #ka-cs-overlay {
      display: none; position: fixed; inset: 0; z-index: 999990;
      background: rgba(0,0,0,0.52); backdrop-filter: blur(2px);
      align-items: center; justify-content: center;
    }
    #ka-cs-overlay.open { display: flex; }
    #ka-cs-modal {
      background: #fff; border-radius: 12px; width: 480px; max-width: 94vw;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      animation: csIn 0.18s ease; overflow: hidden;
    }
    @keyframes csIn {
      from { transform: translateY(14px); opacity: 0; }
      to   { transform: translateY(0);    opacity: 1; }
    }
    #ka-cs-header {
      background: linear-gradient(135deg, #2A5C58 0%, #1C3D3A 100%);
      padding: 16px 20px 13px;
      display: flex; align-items: center; gap: 10px;
    }
    #ka-cs-icon { font-size: 1.4rem; flex-shrink: 0; }
    #ka-cs-header-text { flex: 1; }
    #ka-cs-super {
      font-size: 0.64rem; font-weight: 700; letter-spacing: 0.14em;
      text-transform: uppercase; color: #7AACA0; margin-bottom: 3px;
    }
    #ka-cs-title {
      font-family: Georgia, serif; font-size: 0.98rem; color: #fff; font-weight: 600;
    }
    #ka-cs-close {
      background: rgba(255,255,255,0.14); border: none; color: #fff;
      width: 26px; height: 26px; border-radius: 50%; font-size: 0.95rem;
      cursor: pointer; flex-shrink: 0;
    }
    #ka-cs-close:hover { background: rgba(255,255,255,0.28); }
    #ka-cs-body { padding: 18px 20px 6px; }
    .cs-row {
      display: flex; gap: 12px; align-items: flex-start;
      padding: 9px 0; border-bottom: 1px solid #EEE9E3;
    }
    .cs-row:last-child { border-bottom: none; }
    .cs-row-label {
      font-size: 0.66rem; font-weight: 700; letter-spacing: 0.1em;
      text-transform: uppercase; color: #B0A090; min-width: 80px; padding-top: 1px;
    }
    .cs-row-val {
      font-family: Georgia, serif; font-size: 0.87rem; color: #2D2D2D;
      line-height: 1.55; flex: 1;
    }
    .cs-phase-pill {
      display: inline-block; padding: 2px 9px; border-radius: 20px;
      font-family: Arial, sans-serif; font-size: 0.73rem; font-weight: 700;
      background: #E0F2EE; color: #1C3D3A; border: 1px solid #B8DDD5;
    }
    #ka-cs-footer {
      padding: 12px 20px 16px; display: flex; justify-content: flex-end;
    }
    #ka-cs-dismiss {
      background: #1C3D3A; color: #fff; border: none;
      padding: 8px 22px; border-radius: 6px;
      font-size: 0.84rem; font-weight: 700; cursor: pointer;
    }
    #ka-cs-dismiss:hover { background: #2A7868; }

    /* ─── DEMO LOGIN BANNER ─── */
    #ka-demo-banner {
      display: none; position: fixed; top: 60px; left: 50%;
      transform: translateX(-50%); z-index: 999989;
      background: #1C3D3A; color: #fff;
      padding: 10px 20px; border-radius: 8px;
      font-family: Arial, sans-serif; font-size: 0.84rem;
      box-shadow: 0 4px 18px rgba(0,0,0,0.25);
      animation: bannerIn 0.2s ease;
    }
    @keyframes bannerIn {
      from { transform: translateX(-50%) translateY(-8px); opacity: 0; }
      to   { transform: translateX(-50%) translateY(0);     opacity: 1; }
    }
    #ka-demo-banner strong { color: #F5A623; }
  `;

  /* ─── Inject styles ────────────────────────────────────────────────────── */
  function injectStyles () {
    const el = document.createElement('style');
    el.id = 'ka-demo-wiring-css';
    if (!document.getElementById('ka-demo-wiring-css')) {
      el.textContent = CSS;
      document.head.appendChild(el);
    }
  }

  /* ─── Build modal DOM ──────────────────────────────────────────────────── */
  function buildModal () {
    if (document.getElementById('ka-cs-overlay')) return;

    const overlay = document.createElement('div');
    overlay.id = 'ka-cs-overlay';
    overlay.innerHTML = `
      <div id="ka-cs-modal" onclick="event.stopPropagation()">
        <div id="ka-cs-header">
          <span id="ka-cs-icon">🔌</span>
          <div id="ka-cs-header-text">
            <div id="ka-cs-super">Demo Mode — Backend not yet connected</div>
            <div id="ka-cs-title">Coming Soon</div>
          </div>
          <button id="ka-cs-close">✕</button>
        </div>
        <div id="ka-cs-body">
          <div class="cs-row" id="cs-row-live">
            <span class="cs-row-label">In live system</span>
            <span class="cs-row-val" id="cs-live-text">—</span>
          </div>
          <div class="cs-row" id="cs-row-source">
            <span class="cs-row-label">Data source</span>
            <span class="cs-row-val" id="cs-source-text">—</span>
          </div>
          <div class="cs-row" id="cs-row-phase">
            <span class="cs-row-label">Requires</span>
            <span class="cs-row-val" id="cs-phase-text"><span class="cs-phase-pill">—</span></span>
          </div>
        </div>
        <div id="ka-cs-footer">
          <button id="ka-cs-dismiss">Got it</button>
        </div>
      </div>`;
    overlay.addEventListener('click', closeCS);
    document.body.appendChild(overlay);

    document.getElementById('ka-cs-close').addEventListener('click', closeCS);
    document.getElementById('ka-cs-dismiss').addEventListener('click', closeCS);
  }

  function buildBanner () {
    if (document.getElementById('ka-demo-banner')) return;
    const b = document.createElement('div');
    b.id = 'ka-demo-banner';
    document.body.appendChild(b);
  }

  /* ─── Modal control ────────────────────────────────────────────────────── */
  function openCS (opts) {
    const overlay = document.getElementById('ka-cs-overlay');
    if (!overlay) return;
    document.getElementById('ka-cs-title').textContent   = opts.title  || 'Coming Soon';
    document.getElementById('cs-live-text').textContent      = opts.live   || 'This action would connect to the backend API.';
    document.getElementById('cs-source-text').textContent  = opts.source || 'Requires database and API to be implemented.';
    document.getElementById('cs-phase-text').innerHTML     = `<span class="cs-phase-pill">${opts.phase || '—'}</span>`;
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeCS () {
    const overlay = document.getElementById('ka-cs-overlay');
    if (overlay) overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  /* ─── Demo toast banner ─────────────────────────────────────────────────── */
  function showBanner (html) {
    const b = document.getElementById('ka-demo-banner');
    if (!b) return;
    b.innerHTML = html;
    b.style.display = 'block';
    clearTimeout(b._t);
    b._t = setTimeout(() => { b.style.display = 'none'; }, 3500);
  }

  /* ─── Auto-wire data-coming-soon elements ───────────────────────────────── */
  function wireComingSoon () {
    document.querySelectorAll('[data-coming-soon]').forEach(el => {
      el.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        openCS({
          title:  el.dataset.csTitle  || el.textContent.trim().slice(0, 60),
          live:   el.dataset.csLive   || 'This action requires a live backend.',
          source: el.dataset.csSource || 'Backend database and API.',
          phase:  el.dataset.csPhase  || '—'
        });
      });
    });
  }

  /* ─── Page-specific wiring ──────────────────────────────────────────────── */

  // ── LOGIN PAGE ──
  function wireLogin () {
    const form = document.getElementById('loginForm');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const email = (document.getElementById('email') || {}).value || '';
      if (!email) {
        showBanner('Please enter an email address to sign in (demo mode).');
        return;
      }
      localStorage.setItem('ka_logged_in', '1');
      sessionStorage.setItem('ka_logged_in', '1');
      // Pick landing based on email hints
      let dest = 'ka_dashboard.html';
      if (email.includes('admin') || email.includes('approve')) dest = 'ka_approve.html';
      else if (email.includes('instructor') || email.includes('prof')) dest = 'ka_approve.html';
      else if (email.includes('researcher') || email.includes('research')) dest = 'ka_demo_v04.html';
      showBanner(`<strong>Demo login</strong> — signing in as ${email} → redirecting…`);
      setTimeout(() => { window.location.href = dest; }, 900);
    });
  }

  // ── REGISTER PAGE ──
  function wireRegister () {
    const form = document.getElementById('registerForm') ||
                 document.querySelector('form');
    if (!form || window.location.href.includes('ka_login')) return;
    if (!window.location.href.includes('ka_register')) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      openCS({
        title:  'Submit Registration',
        live:   'Creates a pending user record in the users table (status=pending) and sends a confirmation email. The instructor sees this application in ka_approve.html.',
        source: 'POST /auth/register → users table (status=pending)',
        phase:  'Phase 1 — Foundation Infrastructure'
      });
    });
  }

  // ── HOME PAGE ──
  function wireHome () {
    if (!window.location.href.includes('ka_home')) return;
    // Wire CTA buttons to real destinations
    document.querySelectorAll('.btn-enter, .btn-login, [href="#login"], [href="#sign-in"]').forEach(el => {
      el.href = 'ka_login.html';
    });
    document.querySelectorAll('[href="#register"], .btn-register, .btn-contributor').forEach(el => {
      el.href = 'ka_register.html';
    });
    document.querySelectorAll('[href="#demo"], .btn-demo, .btn-try').forEach(el => {
      el.href = 'ka_demo_v04.html';
    });
    // Footer placeholder links
    document.querySelectorAll('a[href="#"]').forEach(el => {
      const text = el.textContent.trim().toLowerCase();
      if (text.includes('doc')) {
        el.setAttribute('data-coming-soon', 'true');
        el.dataset.csTitle = 'Documentation';
        el.dataset.csLive = 'Full documentation site covering the KA epistemic framework, API reference, and contributor guides.';
        el.dataset.csSource = 'Static docs site (not yet built)';
        el.dataset.csPhase = 'Phase 5 — Polish';
      } else if (text.includes('contact')) {
        el.setAttribute('data-coming-soon', 'true');
        el.dataset.csTitle = 'Contact';
        el.dataset.csLive = 'Contact form routing to the project team at UCSD Cognitive Science.';
        el.dataset.csSource = 'Static form (not yet built)';
        el.dataset.csPhase = 'Phase 5 — Polish';
      }
    });
    wireComingSoon();
  }

  // ── TOP NAV DELEGATION (event delegation handles dynamically-rendered nav) ──
  function wireNavDelegate () {
    // Mapping: normalised link text → real href OR Coming Soon config object.
    // Normalisation: lower-case, strip leading emoji+space, strip trailing ▾.
    var NAV_MAP = {
      // ── ASK section ──
      'ask a question':      'ka_demo_v04.html',
      'compare answers':     { title: 'Compare Answers',
        live:   'Runs two queries in parallel and renders results side-by-side: evidence strength, credence scores, warrant chains, and conflicting findings. Useful for comparing two constructs or two framings of the same hypothesis.',
        source: 'POST /api/v1/query (×2, parallel) → merge → GET /api/v1/compare/{id}',
        phase:  'Phase 2 — Core Tool Backends' },
      'session history':     { title: 'Session History',
        live:   'Shows every query you have run this session and in prior sessions, each with its answer snapshot. You can replay any query, diff two runs of the same query as the evidence base grows, or export a session as a formatted research brief.',
        source: 'user_sessions + query_logs tables → GET /api/v1/users/{id}/sessions',
        phase:  'Phase 3 — User Management' },

      // ── TOOLS section (sidebar) ──
      'question guide':      { title: 'Question Guide',
        live:   'An interactive checklist that teaches well-framed research questions: construct specificity, operationalisable IVs and DVs, measurability via CNFA instruments, and a live evidence-density check that warns if fewer than 3 independent studies address the topic.',
        source: 'Client-side guide + POST /api/v1/scope/check?q={query} for evidence density',
        phase:  'Phase 2 — Core Tool Backends' },
      'scope check':         { title: 'Scope Check',
        live:   'Analyses your current query before submission: estimates how many papers directly address it, identifies the nearest well-studied adjacent constructs, and flags if the evidence base is too thin (< 3 studies) to support a high-confidence answer.',
        source: 'query_engine.py → scope_estimator.py → GET /api/v1/scope/check?q={query}',
        phase:  'Phase 2 — Core Tool Backends' },
      'answer settings':     { title: 'Answer Settings',
        live:   'Controls for answer presentation: credence display mode (numeric / bar / verbal), citation style (APA / inline / DOI only), persona filter (student / researcher / practitioner phrasing), evidence verbosity (summary / detailed / full provenance), and toggle for conflicting-findings section.',
        source: 'user_preferences table → GET / PATCH /api/v1/users/{id}/preferences',
        phase:  'Phase 3 — User Management' },

      // ── EVIDENCE nav ──
      'evidence table':      'ka_evidence.html',
      'by study type':       { title: 'Browse by Study Type',
        live:   'Filters the evidence table to show only RCTs, narrative reviews, field studies, etc. Uses the method_conditioned_class field from the gold_claims corpus to categorise each study.',
        source: 'GET /api/v1/evidence?method_type={type} → gold_claims_v5.jsonl method_conditioned_class',
        phase:  'Phase 2 — Core Tool Backends' },
      'chronological':       { title: 'Chronological Evidence View',
        live:   'Shows all evidence nodes ordered by publication year, so you can trace how the evidence on a topic has developed over time and identify recency effects.',
        source: 'GET /api/v1/evidence?sort=year_asc → articles table → year field',
        phase:  'Phase 2 — Core Tool Backends' },
      'curated sets':        { title: 'Curated Evidence Sets',
        live:   'Instructor-assembled collections of evidence nodes around a theme (e.g., "Best evidence on light and alertness for COGS 160 Week 4"). Students can subscribe to a set and receive updates when new relevant evidence is added.',
        source: 'curated_sets table → GET /api/v1/curated-sets',
        phase:  'Phase 4 — Course Integration' },
      'effect sizes':        { title: 'Effect Size Explorer',
        live:   'A sortable table of all reported effect sizes in the corpus: Cohen\'s d, r, η², with study metadata. Enables quick identification of the strongest and most reliable findings for a construct.',
        source: 'GET /api/v1/evidence?has_effect_size=true → gold_claims causal_tier + direction fields',
        phase:  'Phase 2 — Core Tool Backends' },
      'meta-analysis':       { title: 'Meta-Analysis View',
        live:   'For constructs with ≥ 5 independent studies, displays a forest plot (synthesised effect size ± CI) computed from the gold_claims corpus using a random-effects model. Flags publication bias via funnel plot asymmetry.',
        source: 'GET /api/v1/meta-analysis/{construct_id} → finding_clusters → Python meta module',
        phase:  'Phase 2–3 — requires clustering + sufficient data' },
      'contradictions':      { title: 'Contradictions & Conflicts',
        live:   'Lists claim pairs in the corpus where two studies address the same construct and IV/DV combination but report opposite directions. Displays the abstract_methods_conflict_flag from gold_claims and the rebutting warrant chain.',
        source: 'conflict_pairs view → gold_claims abstract_methods_conflict_flag + direction fields',
        phase:  'Phase 2 — Core Tool Backends' },
      'export':              { title: 'Export Evidence',
        live:   'Exports your current filtered evidence set as CSV, BibTeX, or a structured JSON bundle compatible with Zotero and the KA Phase 0 ae_bundle schema.',
        source: 'GET /api/v1/evidence/export?format={csv|bibtex|json} → streaming response',
        phase:  'Phase 3 — User Management' },

      // ── KNOWLEDGE nav ──
      'belief network':      { title: 'Belief Network Explorer',
        live:   'An interactive graph showing how constructs in the corpus are connected via warrant chains. Node size encodes credence; edge colour encodes warrant type (constitutive / probabilistic / rebuttal). Powered by the Bayesian Network layer in BN_graphical.',
        source: 'BN_graphical repo → GET /api/v1/knowledge/belief-network?root={construct_id}',
        phase:  'Phase 2–3 — BN_graphical integration required' },
      'relations':           { title: 'Construct Relations',
        live:   'A tabular view of all pairwise relationships in the knowledge graph: construct A → construct B, relationship type (inhibits / amplifies / mediates / moderates), evidence count, and mean credence.',
        source: 'construct_relations table → GET /api/v1/knowledge/relations',
        phase:  'Phase 2 — Core Tool Backends' },
      'entity index':        { title: 'Entity Index',
        live:   'An alphabetically-browsable index of all named constructs, instruments, mechanisms, and theoretical frameworks in the corpus — essentially a structured glossary backed by the gold_claims tagging.',
        source: 'constructs + instruments tables → GET /api/v1/knowledge/entities',
        phase:  'Phase 2 — Core Tool Backends' },
      'tier 2 mechanisms':   { title: 'Tier 2 Mechanisms',
        live:   'Displays the mechanism_chain field from gold_claims: the intermediate biological, cognitive, or physical steps proposed to connect an IV to a DV. Groups mechanisms by construct and shows which steps have direct vs. inferred evidence.',
        source: 'GET /api/v1/knowledge/mechanisms?construct_id={id} → mechanism_chain field',
        phase:  'Phase 2 — Core Tool Backends' },
      'neuroscience layer':  { title: 'Neuroscience Layer',
        live:   'A sub-graph filtered to claims where theory_links includes a neuroscience framework (circadian, ipRGC, dopaminergic, etc.). Intended for researchers examining the mechanistic underpinnings of CNFA constructs.',
        source: 'GET /api/v1/knowledge/belief-network?theory_layer=neuroscience → theory_links field',
        phase:  'Phase 2 — Core Tool Backends' },
      'warrants':            { title: 'Warrant Browser',
        live:   'Lists all warrant types used in the corpus (constitutive, probabilistic, analogical, rebuttal) with the claims that instantiate each, showing the grounds → claim backing structure from the Toulmin model.',
        source: 'GET /api/v1/knowledge/warrants → warrant_type field in gold_claims',
        phase:  'Phase 2 — Core Tool Backends' },

      // ── RESEARCH GAPS nav ──
      'gap explorer':        'ka_gaps.html',
      'experiment maker':    'ka_hypothesis_builder.html',
      'topic browser':       'ka_topics.html',
      'voi rankings':        { title: 'Value of Information Rankings',
        live:   'Lists all identified research gaps ranked by their computed VOI score: the expected reduction in uncertainty if a well-powered study were conducted. Score components: current credence variance, construct centrality in the belief network, and estimated study feasibility.',
        source: 'GET /api/v1/gaps?sort=voi_desc → gaps table → voi_score field',
        phase:  'Phase 2 — Core Tool Backends' },

      // ── DESIGN STUDY nav ──
      'pre-registration':    'ka_hypothesis_builder.html',
      'sensor selection':    'ka_sensors.html',
      'protocol template':   { title: 'Protocol Template Generator',
        live:   'Generates a pre-filled experimental protocol document from your hypothesis brief: IV manipulation, DV measurement instruments (pulled from the Signal/Measuring Instrument Catalogue), participant criteria, and APA-formatted pre-registration text ready for OSF submission.',
        source: 'GET /api/v1/protocols/generate?hypothesis_id={id} → hypothesis + instruments tables',
        phase:  'Phase 3 — User Management + Phase 2 instrument data' },

      // ── CONTRIBUTOR nav ──
      'my overview':         'ka_dashboard.html',
      'open queue':          'ka_tagger.html',
      'tag bundles':         'ka_tag_assignment.html',
      'run search':          'ka_article_search.html',
      'question maker':      'ka_question_maker.html',
      'propose article':     'ka_article_propose.html',
      'article finder':      'ka_article_finder_assignment.html',
      'gui assignment':      'ka_gui_assignment.html',
      'new capture':         'ka_datacapture.html',

      // ── PROFILE DROPDOWN ──
      'my profile':          { title: 'My Profile',
        live:   'View and edit your display name, institutional affiliation, persona preference, and notification settings. Profile data is stored in the users table.',
        source: 'GET / PATCH /api/v1/users/{id}',
        phase:  'Phase 3 — User Management' },
      'saved evidence':      { title: 'Saved Evidence',
        live:   'A personal collection of evidence nodes, science summaries, and study references you have bookmarked. Stored in the user_bookmarks table; accessible across sessions.',
        source: 'GET /api/v1/users/{id}/bookmarks → user_bookmarks table',
        phase:  'Phase 3 — User Management' },
      'my queries':          { title: 'My Queries',
        live:   'All queries you have submitted to Knowledge Atlas, with answer snapshots, timestamps, and a diff view showing how the answer has changed as new evidence was added.',
        source: 'GET /api/v1/users/{id}/queries → query_logs table',
        phase:  'Phase 3 — User Management' },
      'notifications':       { title: 'Notifications',
        live:   'Alerts for: new evidence added to constructs you follow, replication failures affecting claims in your saved evidence, and instructor feedback on your submitted work.',
        source: 'GET /api/v1/users/{id}/notifications → notifications table',
        phase:  'Phase 3 — User Management' },
      'settings':            { title: 'Account Settings',
        live:   'Password, email, two-factor authentication, data export, and account deletion. In the live system this is the standard account management panel.',
        source: 'PATCH /api/v1/users/{id} → users table',
        phase:  'Phase 3 — User Management' },
      'sign out':            { title: 'Sign Out',
        live:   'Ends your session by invalidating the session token in the database and clearing the local auth cookie. In this demo, clears localStorage and redirects to the home page.',
        source: 'POST /auth/logout → sessions table invalidation',
        phase:  'Phase 1 — Foundation Infrastructure' }
    };

    function normalise (text) {
      // Strip leading emoji and whitespace, trailing ▾ or ▸, lower-case
      return text.trim()
                 .replace(/^[^\w\s]+\s*/, '')   // leading emoji/symbols
                 .replace(/\s*[▾▸✓]\s*$/, '')   // trailing caret/checkmark
                 .toLowerCase()
                 .trim();
    }

    // Delegate on the nav-items container (survives re-render on mode switch)
    var navBar = document.getElementById('nav-items');
    if (navBar) {
      navBar.addEventListener('click', function (e) {
        var a = e.target.closest('a');
        if (!a) return;
        var key = normalise(a.textContent);
        var cfg = NAV_MAP[key];
        if (cfg === undefined) return; // not in map, ignore
        e.preventDefault();
        if (typeof cfg === 'string') {
          window.location.href = cfg;
        } else {
          openCS(cfg);
        }
      });
    }

    // Profile dropdown (outside nav-items)
    var profileDrop = document.querySelector('.profile-dropdown');
    if (profileDrop) {
      profileDrop.addEventListener('click', function (e) {
        var a = e.target.closest('a');
        if (!a) return;
        var key = normalise(a.textContent);
        var cfg = NAV_MAP[key];
        if (cfg === undefined) return;
        e.preventDefault();
        if (typeof cfg === 'string') {
          window.location.href = cfg;
        } else if (key === 'sign out') {
          // Demo sign-out: clear flag and go home
          localStorage.removeItem('ka_logged_in');
          sessionStorage.removeItem('ka_logged_in');
          window.location.href = 'ka_home.html';
        } else {
          openCS(cfg);
        }
      });
    }
  }

  // ── ASK PAGE (ka_demo_v04) ──
  function wireAsk () {
    if (!window.location.href.includes('ka_demo') &&
        !window.location.href.includes('ka_ask')) return;

    // 1. Sidebar tool links (static <a href="#"> elements)
    var SIDEBAR_CS = {
      'compare answers': {
        title: 'Compare Answers',
        live:   'Runs two queries in parallel and presents results side-by-side: evidence strength, credence scores, warrant chains, and conflicting findings.',
        source: 'POST /api/v1/query (×2) → GET /api/v1/compare/{id}',
        phase:  'Phase 2 — Core Tool Backends'
      },
      'session history': {
        title: 'Session History',
        live:   'Shows every query you have run this session and in prior sessions, each with its answer snapshot. You can replay any query or export a session as a formatted research brief.',
        source: 'user_sessions + query_logs tables → GET /api/v1/users/{id}/sessions',
        phase:  'Phase 3 — User Management'
      },
      'question guide': {
        title: 'Question Guide',
        live:   'An interactive checklist for framing well-formed research questions: construct specificity, operationalisable IVs/DVs, measurability via CNFA instruments, and a live evidence-density check.',
        source: 'Client-side guide + POST /api/v1/scope/check?q={query}',
        phase:  'Phase 2 — Core Tool Backends'
      },
      'scope check': {
        title: 'Scope Check',
        live:   'Analyses your current query before submission: how many papers directly address it, the nearest well-studied adjacent constructs, and a warning if evidence is too thin for a confident answer.',
        source: 'query_engine.py → scope_estimator.py → GET /api/v1/scope/check?q={query}',
        phase:  'Phase 2 — Core Tool Backends'
      },
      'answer settings': {
        title: 'Answer Settings',
        live:   'Controls: credence display mode (numeric / bar / verbal), citation style (APA / inline / DOI only), persona filter, evidence verbosity (summary / full provenance), and toggle for conflicting-findings section.',
        source: 'user_preferences table → GET / PATCH /api/v1/users/{id}/preferences',
        phase:  'Phase 3 — User Management'
      }
    };

    document.querySelectorAll('.sidenav a[href="#"]').forEach(function (el) {
      var raw = el.textContent.trim().replace(/^[^\w\s]+\s*/, '').toLowerCase().trim();
      var cfg = SIDEBAR_CS[raw];
      if (cfg) {
        el.addEventListener('click', function (e) {
          e.preventDefault();
          openCS(cfg);
        });
      }
    });

    // 2. Related Topics panel cards
    document.querySelectorAll('.panel-card').forEach(function (el) {
      if (el.dataset.wired) return;
      el.dataset.wired = '1';
      el.style.cursor = 'pointer';
      el.addEventListener('click', function () {
        var construct = el.querySelector('.pc-title') ? el.querySelector('.pc-title').textContent : el.textContent.trim();
        var isGap = el.classList.contains('gap-card');
        if (isGap) {
          openCS({
            title:  'Research Gap: ' + construct,
            live:   'Opens the gap detail page for "' + construct + '": all studies that have attempted to address this gap, VOI score breakdown (credence variance × construct centrality × feasibility), and the Experiment Maker template pre-filled for a study targeting this gap.',
            source: 'gaps table → GET /api/v1/gaps/{id} → ka_gaps.html detail view',
            phase:  'Phase 2 — Core Tool Backends'
          });
        } else {
          openCS({
            title:  'Topic: ' + construct,
            live:   'Navigates to the topic detail page for "' + construct + '": all finding_cluster nodes tagged to this construct sorted by credence, the Belief Network subgraph, warrant chains, and related gaps. In this demo, this would be a dedicated ka_topics/{slug}.html page.',
            source: 'query_engine.py → ae.query_response.v1 → finding_clusters for this construct',
            phase:  'Phase 0 FastAPI stub → Phase 2 data seeding'
          });
        }
      });
    });

    // 3. Follow-up question chips
    document.querySelectorAll('.followup-chip, .chip-followup, [data-followup]').forEach(function (el) {
      el.addEventListener('click', function (e) {
        e.stopPropagation();
        openCS({
          title:  el.textContent.trim(),
          live:   'Re-queries the engine with response_mode="detail" and the same construct context. Returns a deeper disclosure layer: method summaries, strongest papers, conflict flags, or mechanism proposals depending on which follow-on was selected.',
          source: 'query_engine.py / cross_layer_query.py → response_mode: detail / deep_dive',
          phase:  'Phase 0 FastAPI service stub'
        });
      });
    });

    // 4. Wire the top nav via delegation (survives mode-switch re-render)
    wireNavDelegate();
  }

  // ── EVIDENCE BROWSER ──
  function wireEvidence () {
    if (!window.location.href.includes('ka_evidence')) return;
    // "Add to Hypothesis Brief" button
    document.querySelectorAll('.btn-add-brief, [data-add-brief], .add-brief').forEach(el => {
      el.setAttribute('data-coming-soon', 'true');
      el.dataset.csTitle  = 'Add Evidence to Hypothesis Brief';
      el.dataset.csLive   = 'Saves a reference to this evidence node in the student\'s current hypothesis draft. In the live system this writes to the hypothesis_evidence_refs junction table.';
      el.dataset.csSource = 'POST /api/hypotheses/:id/evidence — requires hypotheses table (Phase 3)';
      el.dataset.csPhase  = 'Phase 3 — User Management';
    });
    wireComingSoon();
  }

  // ── ARTICLE SEARCH ──
  function wireArticleSearch () {
    if (!window.location.href.includes('ka_article_search')) return;
    // Sort dropdown stub
    document.querySelectorAll('.results-sort select').forEach(el => {
      el.addEventListener('change', function () {
        showBanner('Sort order: <strong>re-query with sort=' + el.value + '</strong> would call GET /api/articles?sort=' + el.value + ' in the live system.');
      });
    });
  }

  // ── DASHBOARD ──
  function wireDashboard () {
    if (!window.location.href.includes('ka_dashboard')) return;
    // Mark any "View all" or stat links as coming soon
    document.querySelectorAll('a[href="#"], button[data-action]').forEach(el => {
      const text = el.textContent.trim().toLowerCase();
      if (text.includes('view all') || text.includes('view more')) {
        el.setAttribute('data-coming-soon', 'true');
        el.dataset.csTitle  = 'View Full History';
        el.dataset.csLive   = 'Fetches the complete activity log for this student from the course_assignments table, paginated.';
        el.dataset.csSource = 'GET /api/students/:id/activity — requires course_assignments table (Phase 3)';
        el.dataset.csPhase  = 'Phase 3 — User Management';
      }
    });
    wireComingSoon();
  }

  // ── HYPOTHESIS BUILDER ──
  function wireHypothesisBuilder () {
    if (!window.location.href.includes('ka_hypothesis')) return;
    // Auto-save / save button
    document.querySelectorAll('[id*="save"], [class*="save"], [data-action="save"]').forEach(el => {
      el.setAttribute('data-coming-soon', 'true');
      el.dataset.csTitle  = 'Save Hypothesis';
      el.dataset.csLive   = 'Writes the current hypothesis state to the hypotheses table with student_id and status=draft. Accessible to the instructor via the review queue.';
      el.dataset.csSource = 'POST /api/hypotheses — requires hypotheses table (Phase 3)';
      el.dataset.csPhase  = 'Phase 3 — User Management';
    });
    wireComingSoon();
  }

  // ── APPROVE PAGE ──
  function wireApprove () {
    if (!window.location.href.includes('ka_approve')) return;
    // Buttons are already wired with proper modals — nothing extra needed
  }

  // ── GAPS PAGE ──
  function wireGaps () {
    if (!window.location.href.includes('ka_gaps')) return;
    // Any "detect more gaps" or refresh button
    document.querySelectorAll('[data-action="detect"], [class*="refresh"]').forEach(el => {
      el.setAttribute('data-coming-soon', 'true');
      el.dataset.csTitle  = 'Detect Research Gaps';
      el.dataset.csLive   = 'Runs the gap detection algorithm over the evidence node corpus — identifies finding_clusters with credence below threshold, untested predictions, conflicting finding pairs, and missing measurement coverage.';
      el.dataset.csSource = 'finding_clustering.py + gap detection service — requires Phase 2 data seeding';
      el.dataset.csPhase  = 'Phase 2 — Data Seeding + Phase 4 — Core Backends';
    });
    wireComingSoon();
  }

  /* ─── Keyboard ────────────────────────────────────────────────────────── */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeCS();
  });

  /* ─── Expose global API ─────────────────────────────────────────────────── */
  window.KA = window.KA || {};
  window.KA.showComingSoon = openCS;
  window.KA.closeComingSoon = closeCS;
  window.KA.showBanner = showBanner;

  /* ─── Initialise ────────────────────────────────────────────────────────── */
  function init () {
    injectStyles();
    buildModal();
    buildBanner();

    wireLogin();
    wireRegister();
    wireHome();
    wireAsk();           // also calls wireNavDelegate() for the dynamic #nav-items nav
    wireNavDelegate();   // called again here so it fires on any page with #nav-items
    wireEvidence();
    wireArticleSearch();
    wireDashboard();
    wireHypothesisBuilder();
    wireApprove();
    wireGaps();

    // Final pass: wire anything still carrying data-coming-soon
    wireComingSoon();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
