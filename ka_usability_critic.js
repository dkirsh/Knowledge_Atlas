/**
 * ka_usability_critic.js  —  ATLAS Usability + Visualization Critique Agent
 * ---------------------------------------------------------------------------
 * Adds a small floating "Critique" button (bottom-left) visible to
 * all COGS160 Spring 2026 students. Clicking opens a structured
 * heuristic-based critique panel covering interface usability AND
 * data visualization design — the two overlapping concerns on ATLAS
 * search, review, HITL, and evidence-chain pages.
 *
 * The panel (five tabs):
 *   1. Auto-captures current page context (URL, title, headings, viz elements)
 *   2. Nielsen's 10 Heuristics (H1–H10) for general UI
 *   3. Shneiderman's 8 Golden Rules (R1–R8) for interaction design
 *   4. Visualization heuristics (V1–V17): Tufte, Cleveland, Cairo, Knaflic,
 *      and Shneiderman's Information-Seeking Mantra — for critiquing charts,
 *      evidence networks, coverage maps, and argument-structure displays
 *   5. Summary (copyable structured critique output)
 *   6. History (past saved sessions)
 *
 * TODO (future improvements — see TASKS.md):
 *   - Wire to a real LLM endpoint (POST /api/critique) so the system can
 *     generate an AI-written critique of the page using the student's notes
 *   - Add server-side aggregation endpoint so the instructor can review all
 *     submitted critiques across all students in one view
 *   - Integrate with ka_auth_server.py to tag critiques to specific students
 *   - Add screenshot capture (html2canvas or similar) to attach a page snapshot
 *   - Make severity icons draggable onto page elements (pin-point critique)
 *
 * Visibility: appears when localStorage has ka_cogs160_spring=1
 *   OR when the page has a ?cogs160=1 URL param
 *   OR when in any mode on ATLAS (the system is the course tool)
 *   Falls back to always visible on this domain for simplicity.
 *
 * Usage: <script src="ka_usability_critic.js"></script>
 * Then call: window.KA_CRITIC.init()
 */

(function () {
  'use strict';

  /* ── Heuristic definitions ─────────────────────────────────────────── */

  const NIELSEN = [
    { id: 'n1', code: 'H1', label: 'Visibility of system status',
      desc: 'The user should always know what is happening. Does the page show loading states, current location, and action confirmations?' },
    { id: 'n2', code: 'H2', label: 'Match between system and real world',
      desc: 'Does the language match what users know? Are concepts explained in the user\'s terms, not the system\'s internal model?' },
    { id: 'n3', code: 'H3', label: 'User control and freedom',
      desc: 'Can the user undo, cancel, or escape from unwanted states? Are "emergency exits" clearly marked?' },
    { id: 'n4', code: 'H4', label: 'Consistency and standards',
      desc: 'Do elements look and behave consistently across the page and site? Are platform conventions followed?' },
    { id: 'n5', code: 'H5', label: 'Error prevention',
      desc: 'Does the design prevent errors before they happen? Are dangerous actions confirmed?' },
    { id: 'n6', code: 'H6', label: 'Recognition rather than recall',
      desc: 'Are options visible? Does the user need to remember information from elsewhere to complete a task?' },
    { id: 'n7', code: 'H7', label: 'Flexibility and efficiency',
      desc: 'Are there shortcuts for expert users? Do novice paths remain clean while expert paths are available?' },
    { id: 'n8', code: 'H8', label: 'Aesthetic and minimalist design',
      desc: 'Is every element earning its place? Does any non-functional element compete with the user\'s task?' },
    { id: 'n9', code: 'H9', label: 'Error recovery',
      desc: 'When errors occur, are messages plain-language, specific, and constructive? Does the system help the user recover?' },
    { id: 'n10', code: 'H10', label: 'Help and documentation',
      desc: 'Is help available when needed? Is it task-focused and searchable?' }
  ];

  const SHNEIDERMAN = [
    { id: 's1', code: 'R1', label: 'Consistency',
      desc: 'Same terminology, same layout, same behavior for similar tasks throughout.' },
    { id: 's2', code: 'R2', label: 'Shortcuts for expert users',
      desc: 'Accelerators that novices don\'t notice but experts appreciate.' },
    { id: 's3', code: 'R3', label: 'Informative feedback',
      desc: 'Every action produces visible, comprehensible feedback.' },
    { id: 's4', code: 'R4', label: 'Closure',
      desc: 'Task sequences have a clear end state. The user knows when they are finished.' },
    { id: 's5', code: 'R5', label: 'Error prevention and handling',
      desc: 'Errors are rare; when they occur, recovery is easy and non-punitive.' },
    { id: 's6', code: 'R6', label: 'Reversal of actions',
      desc: 'The user can undo actions and retract submissions without penalty.' },
    { id: 's7', code: 'R7', label: 'Internal locus of control',
      desc: 'The user feels in charge. The system responds to the user, not the reverse.' },
    { id: 's8', code: 'R8', label: 'Reduce short-term memory load',
      desc: 'No need to remember information across pages or across parts of the same screen.' }
  ];

  /* ── Visualization heuristics ─────────────────────────────────────── */
  /*  Drawn from Tufte (1983, 2001), Cleveland (1985, 1993),            */
  /*  Cairo (2012, 2016), Knaflic (2015), and Shneiderman (1996).       */
  /*  Grouped by scholar; use renderGroupedHeuristicTab() to render.    */

  const VIZ_HEURISTICS = [
    /* — Tufte: Data-Ink and Graphical Integrity ——————————————————— */
    { id: 'v1', code: 'V1', label: 'Data-ink maximization',
      group: 'Tufte — Data-Ink & Integrity',
      codeColor: '#5b4200', codeBg: '#fde68a',
      desc: 'The proportion of ink (or pixels) devoted to actual data should be as high as possible. Eliminate redundant gridlines, unnecessary tick marks, decorative borders, and any element that encodes no information. Ask: what happens if I remove this? If nothing is lost, remove it.' },
    { id: 'v2', code: 'V2', label: 'Graphical integrity / Lie Factor',
      group: 'Tufte — Data-Ink & Integrity',
      codeColor: '#5b4200', codeBg: '#fde68a',
      desc: 'The visual effect must be proportional to the numerical quantity. Lie Factor = (size of effect in graphic) / (size of effect in data). A factor > 1.05 or < 0.95 is a distortion. Check: are y-axes truncated without justification? Does a 10% difference appear as a 300% visual difference?' },
    { id: 'v3', code: 'V3', label: 'Chartjunk elimination',
      group: 'Tufte — Data-Ink & Integrity',
      codeColor: '#5b4200', codeBg: '#fde68a',
      desc: 'Chartjunk = moiré vibrations (striped fill), heavy grids, self-promotional "ducks" (icons used as data markers), and 3-D effects on 2-D data. Does this visualization contain any element that adds visual noise without adding information? Rate "Major Fail" if 3-D is used to display simple proportions.' },
    { id: 'v4', code: 'V4', label: 'Small multiples for comparison',
      group: 'Tufte — Data-Ink & Integrity',
      codeColor: '#5b4200', codeBg: '#fde68a',
      desc: 'When comparing across conditions, domains, or time periods, small multiples (the same chart form repeated at small scale, side by side) are more legible than overlapping lines or superimposed colors. Does this visualization have overlapping series that would be clearer as a small-multiples panel?' },

    /* — Cleveland: Graphical Perception Hierarchy ————————————————— */
    { id: 'v5', code: 'V5', label: 'Perceptual encoding hierarchy',
      group: 'Cleveland — Graphical Perception',
      codeColor: '#1a4731', codeBg: '#bbf7d0',
      desc: 'Accuracy of quantitative judgment runs: Position (most accurate) > Length > Angle > Area > Color hue (least accurate). Is the most important comparison encoded at the highest-accuracy level available? If the key finding is a difference in magnitude, encode it as position (dot plot), not as angle (pie) or area (bubble).' },
    { id: 'v6', code: 'V6', label: 'Pattern discrimination without color',
      group: 'Cleveland — Graphical Perception',
      codeColor: '#1a4731', codeBg: '#bbf7d0',
      desc: 'Overlapping series should be distinguishable by line type, symbol shape, or position — not by color alone (accessibility). Can every category be identified if the image is printed in grayscale? Cleveland recommends at least three line-type levels (solid, dashed, dotted) before adding color as a redundant encoding.' },
    { id: 'v7', code: 'V7', label: 'Scale, baseline, and reference lines',
      group: 'Cleveland — Graphical Perception',
      codeColor: '#1a4731', codeBg: '#bbf7d0',
      desc: 'When showing magnitudes (not rates or indices), the y-axis should include zero so the viewer can judge absolute differences. Are there meaningful reference values (grand mean, theoretical threshold, previous-year benchmark) that would help the viewer calibrate? Label reference lines explicitly.' },

    /* — Cairo: Truthfulness, Function, Beauty, Insightfulness ——————— */
    { id: 'v8', code: 'V8', label: 'Truthfulness — show uncertainty',
      group: 'Cairo — Truthfulness & Purpose',
      codeColor: '#1e3a6e', codeBg: '#bfdbfe',
      desc: 'Every estimate has uncertainty; hiding it is dishonest. Are confidence intervals, error bars, credible intervals, or at minimum a sample-size annotation present wherever the underlying values are estimates? On ATLAS evidence-quality and confidence-score displays, missing uncertainty ranges are a Major Fail.' },
    { id: 'v9', code: 'V9', label: 'Functionality — every element earns its place',
      group: 'Cairo — Truthfulness & Purpose',
      codeColor: '#1e3a6e', codeBg: '#bfdbfe',
      desc: 'Beauty must serve communication, not decorate it. Does each visual element (icon, border, color, texture) communicate something? If a decorative choice were replaced by a functional one, would the display improve? Gradients, drop shadows, and rounded rectangles are not wrong, but they must not compete with data.' },
    { id: 'v10', code: 'V10', label: 'Insightfulness — more than a table',
      group: 'Cairo — Truthfulness & Purpose',
      codeColor: '#1e3a6e', codeBg: '#bfdbfe',
      desc: 'A visualization should reveal something a plain table does not. Does this display expose patterns (clusters, outliers, trends, gaps) that would be invisible in a sorted list? If a well-formatted table would do the job equally well, the chart form is not earning its added cognitive cost.' },
    { id: 'v11', code: 'V11', label: 'Enlightenment — appropriate form for claim',
      group: 'Cairo — Truthfulness & Purpose',
      codeColor: '#1e3a6e', codeBg: '#bfdbfe',
      desc: 'Exploratory (find a pattern) and explanatory (show an already-known pattern clearly) visualizations need different designs. An exploratory tool should let users filter and drill; an explanatory display should guide the eye to one key finding. Does the form match the communicative purpose of this page?' },

    /* — Knaflic: Cognitive Design and Preattentive Attributes ———————— */
    { id: 'v12', code: 'V12', label: 'Preattentive attributes — one focal signal',
      group: 'Knaflic — Cognitive Design',
      codeColor: '#5b1a6e', codeBg: '#e9d5ff',
      desc: 'Preattentive attributes (color saturation, size, motion, orientation) are processed before focused attention — they guide the eye involuntarily. There should be exactly one dominant preattentive signal per display, pointing to the most important datum. Multiple competing "accent" colors cancel each other. Is there a single clear focal element?' },
    { id: 'v13', code: 'V13', label: 'Declutter — ruthless signal-to-noise',
      group: 'Knaflic — Cognitive Design',
      codeColor: '#5b1a6e', codeBg: '#e9d5ff',
      desc: 'Default chart-tool output (Excel, Tableau, Matplotlib) is almost always over-decorated: heavy gridlines, box borders, redundant legends, tick marks on every integer. Remove every non-data element that can be removed without a viewer noticing data loss. Start with gridlines (go light gray), then borders, then tick marks, then legends (replace with direct labels).' },
    { id: 'v14', code: 'V14', label: 'Direct labeling over legends',
      group: 'Knaflic — Cognitive Design',
      codeColor: '#5b1a6e', codeBg: '#e9d5ff',
      desc: 'A legend forces the viewer to look away from the data, find the key, match color to category, then return to the data — at minimum four eye movements per data point. Direct labels (text alongside the series, bar, or point) eliminate this cost. Does this visualization use a legend where direct labels would work?' },
    { id: 'v15', code: 'V15', label: 'Contextual text — title states the finding',
      group: 'Knaflic — Cognitive Design',
      codeColor: '#5b1a6e', codeBg: '#e9d5ff',
      desc: 'Assertion-evidence structure: the title should state what the viewer should conclude (e.g., "Confidence scores cluster below 0.5 for neuroarchitecture articles"), not just label the content (e.g., "Confidence score distribution"). Are axis labels unambiguous about units? Is the scale legible without a tooltip? Is the data source credited?' },

    /* — Shneiderman Information-Seeking Mantra ————————————————————— */
    { id: 'v16', code: 'V16', label: 'Overview → zoom/filter → details on demand',
      group: 'Shneiderman — Info-Seeking Mantra',
      codeColor: '#7c1d1d', codeBg: '#fecaca',
      desc: 'Effective information visualization follows a three-stage workflow: (1) Overview — the user can see the full dataset at a glance; (2) Zoom and filter — the user can narrow to a subset of interest without leaving the view; (3) Details on demand — the user can retrieve details about a specific item by clicking or hovering. Does this ATLAS page support all three stages? Where does it break down?' },
    { id: 'v17', code: 'V17', label: 'Persistent context during exploration',
      group: 'Shneiderman — Info-Seeking Mantra',
      codeColor: '#7c1d1d', codeBg: '#fecaca',
      desc: 'The viewer should always know where they are in the data space. When a filter is applied, the remaining view should still show where the filtered data sits relative to the whole (e.g., a mini-map, a count badge, a greyed-out background showing filtered-out items). Does zooming in destroy the overview context? Does the user lose their place?' }
  ];

  /* ── Page context capture ─────────────────────────────────────────── */

  function capturePageContext() {
    const h1s = Array.from(document.querySelectorAll('h1')).map(function (h) { return h.textContent.trim(); }).join(' / ');
    const h2s = Array.from(document.querySelectorAll('h2')).slice(0, 4).map(function (h) { return h.textContent.trim(); });
    const errorEls = document.querySelectorAll('[class*="error"],[class*="Error"],[aria-invalid="true"]');
    return {
      url: window.location.href,
      title: document.title,
      h1: h1s || document.title,
      sections: h2s,
      hasErrors: errorEls.length > 0,
      vizElements: detectVizElements(),
      capturedAt: new Date().toISOString()
    };
  }

  /* ── Visualization element detection ─────────────────────────────── */
  /*  Scans the live DOM for chart/viz elements to prompt students      */
  /*  to use the Viz tab when relevant displays are present.            */

  function detectVizElements() {
    const found = [];
    if (document.querySelectorAll('canvas').length > 0)
      found.push('canvas (' + document.querySelectorAll('canvas').length + ')');
    if (document.querySelectorAll('svg').length > 0)
      found.push('SVG (' + document.querySelectorAll('svg').length + ')');
    // Common charting library class patterns
    const chartClasses = [
      '[class*="chart"]', '[class*="Chart"]', '[class*="graph"]', '[class*="Graph"]',
      '[class*="plot"]', '[class*="Plot"]', '[class*="viz"]', '[class*="Viz"]',
      '[class*="network"]', '[class*="Network"]', '[class*="treemap"]',
      '[data-chart]', '[data-highcharts-chart]', '.recharts-wrapper',
      '.apexcharts-canvas', '.d3-chart', '.evidence-chain', '.bn-graph'
    ];
    chartClasses.forEach(function (sel) {
      try {
        const els = document.querySelectorAll(sel);
        if (els.length > 0) found.push(sel.replace(/[\[\].*]/g, '') + ' (' + els.length + ')');
      } catch (e) {}
    });
    return found;
  }

  /* ── Storage ──────────────────────────────────────────────────────── */

  const STORAGE_KEY = 'ka_critic_sessions';

  function loadSessions() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }
    catch (e) { return []; }
  }

  function saveSession(session) {
    const sessions = loadSessions();
    const idx = sessions.findIndex(function (s) { return s.id === session.id; });
    if (idx >= 0) { sessions[idx] = session; }
    else { sessions.unshift(session); }
    // Keep last 50 sessions
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions.slice(0, 50))); }
    catch (e) {}
  }

  /* ── Rating helpers ───────────────────────────────────────────────── */

  const RATINGS = [
    { val: 'pass',  label: 'Pass', color: '#059669', bg: '#d1fae5' },
    { val: 'minor', label: 'Minor Issue', color: '#d97706', bg: '#fef3c7' },
    { val: 'major', label: 'Major Fail', color: '#dc2626', bg: '#fee2e2' },
    { val: 'na',    label: 'N/A', color: '#6b7280', bg: '#f3f4f6' }
  ];

  /* ── Build Widget DOM ─────────────────────────────────────────────── */

  let widgetEl = null;
  let panelOpen = false;
  let currentSession = null;

  function buildWidget() {
    const el = document.createElement('div');
    el.id = 'ka-critic-widget';

    const style = document.createElement('style');
    style.textContent = `
      #ka-critic-widget {
        position: fixed;
        bottom: 24px;
        left: 16px;
        z-index: 8500;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 13px;
      }
      #ka-critic-btn {
        width: 36px; height: 36px;
        border-radius: 50%;
        background: #6b3fa0;
        color: #fff;
        border: none;
        cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        font-size: .9rem;
        box-shadow: 0 2px 8px rgba(107,63,160,.4);
        transition: transform .15s, box-shadow .15s;
        position: relative;
        title: 'Usability Critique (COGS160)';
      }
      #ka-critic-btn:hover {
        transform: scale(1.12);
        box-shadow: 0 4px 14px rgba(107,63,160,.55);
      }
      #ka-critic-btn-label {
        position: absolute;
        left: 42px;
        top: 50%; transform: translateY(-50%);
        background: #6b3fa0;
        color: #fff;
        border-radius: 5px;
        padding: 3px 10px;
        font-size: .72rem;
        font-weight: 700;
        white-space: nowrap;
        pointer-events: none;
        display: none;
        box-shadow: 0 2px 6px rgba(0,0,0,.2);
      }
      #ka-critic-btn:hover #ka-critic-btn-label { display: block; }

      #ka-critic-panel {
        position: fixed;
        left: 0; bottom: 0; top: 0;
        width: 440px;
        max-width: 100vw;
        background: #fff;
        border-right: 1.5px solid #e5e7eb;
        box-shadow: 4px 0 30px rgba(0,0,0,.15);
        display: flex;
        flex-direction: column;
        z-index: 8500;
        transition: transform .25s ease;
        transform: translateX(-100%);
      }
      #ka-critic-panel.open { transform: translateX(0); }

      #ka-critic-panel-hdr {
        background: #6b3fa0;
        color: #fff;
        padding: 14px 16px;
        flex-shrink: 0;
        display: flex; align-items: center; gap: 10px;
      }
      #ka-critic-panel-title { font-weight: 800; font-size: 1rem; flex: 1; }
      #ka-critic-panel-close {
        background: rgba(255,255,255,.15); border: none;
        color: #fff; border-radius: 6px; padding: 4px 10px;
        cursor: pointer; font-size: .8rem;
        transition: background .15s;
      }
      #ka-critic-panel-close:hover { background: rgba(255,255,255,.28); }

      /* Tab bar */
      .ka-critic-tabs {
        display: flex;
        border-bottom: 1.5px solid #e5e7eb;
        flex-shrink: 0;
        background: #faf5ff;
      }
      .ka-critic-tab {
        flex: 1; padding: 9px 6px;
        border: none; background: none;
        font-size: .78rem; font-weight: 600;
        color: #9ca3af; cursor: pointer;
        border-bottom: 2px solid transparent;
        transition: color .15s, border-color .15s;
      }
      .ka-critic-tab.active { color: #6b3fa0; border-bottom-color: #6b3fa0; }

      /* Scrollable content area */
      #ka-critic-content { flex: 1; overflow-y: auto; padding: 0; }

      /* Context strip */
      #ka-critic-context {
        background: #faf5ff;
        border-bottom: 1px solid #e8d5fc;
        padding: 10px 14px;
        flex-shrink: 0;
      }
      #ka-critic-context-url {
        font-size: .72rem; color: #6b7280;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
      }
      #ka-critic-context-title { font-size: .84rem; font-weight: 700; color: #182B49; }

      /* Heuristic rows */
      .ka-h-section-label {
        padding: 12px 14px 6px;
        font-size: .7rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1px;
        color: #9ca3af;
        background: #fafafa;
        border-bottom: 1px solid #f0f0f0;
      }
      .ka-h-row {
        border-bottom: 1px solid #f3f4f6;
        padding: 10px 14px;
      }
      .ka-h-row-hdr {
        display: flex; align-items: flex-start; gap: 8px; margin-bottom: 6px;
      }
      .ka-h-code {
        font-size: .7rem; font-weight: 700; color: #fff;
        background: #6b3fa0;
        border-radius: 4px; padding: 1px 6px;
        flex-shrink: 0; margin-top: 2px;
      }
      .ka-h-label { font-size: .88rem; font-weight: 700; color: #182B49; }
      .ka-h-desc { font-size: .8rem; color: #6b7280; line-height: 1.4; margin-bottom: 8px; }
      .ka-h-rating-row { display: flex; gap: 4px; margin-bottom: 6px; flex-wrap: wrap; }
      .ka-rating-btn {
        border: 1.5px solid #d1d5db;
        border-radius: 5px;
        padding: 3px 8px;
        font-size: .72rem; font-weight: 700;
        cursor: pointer; background: none;
        color: #6b7280;
        transition: all .12s;
      }
      .ka-rating-btn.selected { border-color: var(--sel-color); background: var(--sel-bg); color: var(--sel-color); }
      .ka-h-note {
        width: 100%; border: 1.5px solid #d1d5db;
        border-radius: 5px; padding: 5px 8px;
        font-size: .8rem; font-family: inherit;
        resize: none; min-height: 36px;
        color: #374151; outline: none;
      }
      .ka-h-note:focus { border-color: #6b3fa0; }

      /* Summary tab */
      #ka-critic-summary-tab { padding: 16px 14px; }
      .ka-summary-stats {
        display: grid; grid-template-columns: repeat(3, 1fr);
        gap: 8px; margin-bottom: 16px;
      }
      .ka-stat-chip {
        text-align: center; border-radius: 8px;
        padding: 10px 8px; border: 1.5px solid #e5e7eb;
      }
      .ka-stat-num { font-size: 1.4rem; font-weight: 800; }
      .ka-stat-label { font-size: .72rem; color: #6b7280; }
      .ka-summary-text {
        background: #f8f8f8; border: 1px solid #e5e7eb;
        border-radius: 6px; padding: 12px;
        font-size: .82rem; line-height: 1.6;
        color: #374151; white-space: pre-wrap;
        font-family: 'Courier New', monospace;
        max-height: 280px; overflow-y: auto;
        margin-bottom: 12px;
      }
      .ka-action-row { display: flex; gap: 8px; flex-wrap: wrap; }
      .ka-action-btn {
        flex: 1; border-radius: 7px; padding: 9px 12px;
        font-size: .82rem; font-weight: 700;
        cursor: pointer; border: none;
        transition: opacity .15s;
      }
      .ka-action-btn:hover { opacity: .85; }
      .ka-copy-btn { background: #6b3fa0; color: #fff; }
      .ka-save-btn { background: #e5e7eb; color: #374151; }
      .ka-reset-btn { background: #fee2e2; color: #991b1b; }

      /* Past sessions */
      #ka-critic-history-tab { padding: 0; }
      .ka-hist-item {
        padding: 10px 14px;
        border-bottom: 1px solid #f3f4f6;
        cursor: pointer;
      }
      .ka-hist-item:hover { background: #faf5ff; }
      .ka-hist-title { font-size: .85rem; font-weight: 700; color: #182B49; }
      .ka-hist-meta { font-size: .74rem; color: #9ca3af; }
      .ka-hist-pills { display: flex; gap: 4px; margin-top: 4px; }
      .ka-hist-pill { font-size: .68rem; font-weight: 700; border-radius: 4px; padding: 1px 6px; }

      #ka-critic-overlay {
        position: fixed; inset: 0;
        background: rgba(0,0,0,.3);
        z-index: 8400;
        display: none;
      }
    `;
    document.head.appendChild(style);

    // Overlay
    const overlay = document.createElement('div');
    overlay.id = 'ka-critic-overlay';
    overlay.addEventListener('click', closePanel);
    document.body.appendChild(overlay);

    // Panel
    const panel = document.createElement('div');
    panel.id = 'ka-critic-panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', 'Usability Critique Panel');
    document.body.appendChild(panel);

    // Button
    el.innerHTML = `<button id="ka-critic-btn" aria-label="Open usability critique panel">🔎<span id="ka-critic-btn-label">Critique page</span></button>`;
    document.body.appendChild(el);
    widgetEl = el;

    el.querySelector('#ka-critic-btn').addEventListener('click', togglePanel);
    buildPanel(panel);
  }

  function buildPanel(panel) {
    const ctx = capturePageContext();
    currentSession = createSession(ctx);

    panel.innerHTML =
      '<div id="ka-critic-panel-hdr">' +
        '<div id="ka-critic-panel-title">🔎 Usability Critique</div>' +
        '<button id="ka-critic-panel-close">Close ✕</button>' +
      '</div>' +
      '<div id="ka-critic-context">' +
        '<div id="ka-critic-context-url">' + escHtml(ctx.url) + '</div>' +
        '<div id="ka-critic-context-title">' + escHtml(ctx.h1 || ctx.title) + '</div>' +
        (ctx.vizElements && ctx.vizElements.length > 0
          ? '<div style="margin-top:5px;font-size:.72rem;color:#92400e;background:#fef3c7;border-radius:4px;padding:3px 7px;display:inline-block">📊 Viz elements: ' + escHtml(ctx.vizElements.join(', ')) + ' — use the Viz tab</div>'
          : '') +
      '</div>' +
      '<div class="ka-critic-tabs">' +
        '<button class="ka-critic-tab active" data-tab="heuristics">Nielsen H1–10</button>' +
        '<button class="ka-critic-tab" data-tab="shneiderman">Shneider R1–8</button>' +
        '<button class="ka-critic-tab" data-tab="viz" style="position:relative">' +
          'Viz V1–17' +
          (ctx.vizElements && ctx.vizElements.length > 0
            ? ' <span style="position:absolute;top:4px;right:4px;width:7px;height:7px;background:#f59e0b;border-radius:50%;display:inline-block" title="Viz elements detected on this page"></span>'
            : '') +
        '</button>' +
        '<button class="ka-critic-tab" data-tab="summary">Summary</button>' +
        '<button class="ka-critic-tab" data-tab="history">History</button>' +
      '</div>' +
      '<div id="ka-critic-content"></div>';

    panel.querySelector('#ka-critic-panel-close').addEventListener('click', closePanel);

    const tabs = panel.querySelectorAll('.ka-critic-tab');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        tabs.forEach(function (t) { t.classList.remove('active'); });
        tab.classList.add('active');
        renderTab(tab.dataset.tab);
      });
    });

    renderTab('heuristics');
  }

  /* ── Tab Rendering ────────────────────────────────────────────────── */

  function renderTab(tabName) {
    const content = document.getElementById('ka-critic-content');
    if (!content) return;
    if (tabName === 'heuristics') {
      renderHeuristicTab(content, NIELSEN, 'Nielsen\'s 10 Heuristics', false);
    } else if (tabName === 'shneiderman') {
      renderHeuristicTab(content, SHNEIDERMAN, 'Shneiderman\'s 8 Golden Rules', false);
    } else if (tabName === 'viz') {
      renderHeuristicTab(content, VIZ_HEURISTICS, 'Visualization Design Heuristics (V1–V17)', true);
    } else if (tabName === 'summary') {
      renderSummaryTab(content);
    } else if (tabName === 'history') {
      renderHistoryTab(content);
    }
  }

  function renderHeuristicTab(container, heuristics, sectionLabel, useGroups) {
    const saved = currentSession ? (currentSession.ratings || {}) : {};
    const notes = currentSession ? (currentSession.notes || {}) : {};

    let lastGroup = null;
    const rows = heuristics.map(function (h) {
      const currentRating = saved[h.id] || '';
      const currentNote = notes[h.id] || '';
      const ratingBtns = RATINGS.map(function (r) {
        const isSelected = currentRating === r.val;
        return '<button class="ka-rating-btn' + (isSelected ? ' selected' : '') + '"' +
          ' data-hid="' + h.id + '" data-val="' + r.val + '"' +
          ' style="' + (isSelected ? '--sel-color:' + r.color + ';--sel-bg:' + r.bg : '') + '">' +
          r.label + '</button>';
      }).join('');

      // Code badge styling — per-heuristic color for viz, default purple for others
      const codeStyle = (h.codeBg && h.codeColor)
        ? 'background:' + h.codeBg + ';color:' + h.codeColor
        : 'background:#6b3fa0;color:#fff';

      // Group header (viz tab only)
      let groupHeader = '';
      if (useGroups && h.group && h.group !== lastGroup) {
        lastGroup = h.group;
        groupHeader = '<div class="ka-h-section-label" style="background:#f5f3ff;border-top:1.5px solid #e8d5fc;margin-top:4px">' +
          escHtml(h.group) + '</div>';
      }

      return groupHeader + '<div class="ka-h-row">' +
        '<div class="ka-h-row-hdr">' +
          '<div class="ka-h-code" style="' + codeStyle + '">' + h.code + '</div>' +
          '<div class="ka-h-label">' + escHtml(h.label) + '</div>' +
        '</div>' +
        '<div class="ka-h-desc">' + escHtml(h.desc) + '</div>' +
        '<div class="ka-h-rating-row">' + ratingBtns + '</div>' +
        '<textarea class="ka-h-note" data-hid="' + h.id + '" placeholder="Note what you observe…" rows="2">' +
          escHtml(currentNote) + '</textarea>' +
      '</div>';
    }).join('');

    container.innerHTML =
      '<div class="ka-h-section-label">' + sectionLabel + '</div>' + rows;

    // Rating button listeners
    container.querySelectorAll('.ka-rating-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const hid = btn.dataset.hid;
        const val = btn.dataset.val;
        // Update session
        currentSession.ratings[hid] = val;
        saveCurrentSession();
        // Re-style buttons in this row
        const row = btn.closest('.ka-h-rating-row');
        row.querySelectorAll('.ka-rating-btn').forEach(function (b) {
          const r = RATINGS.find(function (rx) { return rx.val === b.dataset.val; });
          b.classList.toggle('selected', b.dataset.val === val);
          b.style = b.dataset.val === val ? '--sel-color:' + r.color + ';--sel-bg:' + r.bg : '';
        });
      });
    });

    // Note listeners
    container.querySelectorAll('.ka-h-note').forEach(function (ta) {
      ta.addEventListener('input', function () {
        currentSession.notes[ta.dataset.hid] = ta.value;
        saveCurrentSession();
      });
    });
  }

  function renderSummaryTab(container) {
    if (!currentSession) { container.innerHTML = '<div style="padding:20px;color:#999">No session active.</div>'; return; }

    const ratings = currentSession.ratings || {};
    const notes = currentSession.notes || {};

    function tally(heuristicSet) {
      let pass = 0, minor = 0, major = 0, na = 0, unrated = 0;
      heuristicSet.forEach(function (h) {
        const r = ratings[h.id];
        if (r === 'pass') pass++;
        else if (r === 'minor') minor++;
        else if (r === 'major') major++;
        else if (r === 'na') na++;
        else unrated++;
      });
      return { pass: pass, minor: minor, major: major, na: na, unrated: unrated };
    }

    const nTally = tally(NIELSEN);
    const sTally = tally(SHNEIDERMAN);
    const vTally = tally(VIZ_HEURISTICS);
    const totPass  = nTally.pass  + sTally.pass  + vTally.pass;
    const totMinor = nTally.minor + sTally.minor + vTally.minor;
    const totMajor = nTally.major + sTally.major + vTally.major;
    const totNa    = nTally.na    + sTally.na    + vTally.na;

    // Build summary text
    const ctx = currentSession.context;
    const all = NIELSEN.concat(SHNEIDERMAN).concat(VIZ_HEURISTICS);
    const issues = all.filter(function (h) {
      return ratings[h.id] === 'minor' || ratings[h.id] === 'major';
    });

    let summaryText = 'USABILITY + VIZ CRITIQUE — ' + (ctx ? ctx.h1 || ctx.title : 'Unknown page') + '\n';
    summaryText += 'URL: ' + (ctx ? ctx.url : '') + '\n';
    summaryText += 'Critiqued: ' + new Date().toLocaleString() + '\n';
    if (ctx && ctx.vizElements && ctx.vizElements.length > 0) {
      summaryText += 'Viz elements detected: ' + ctx.vizElements.join(', ') + '\n';
    }
    summaryText += '\n';
    summaryText += 'SECTION SCORES:\n';
    summaryText += '  Nielsen H1–H10:          Pass=' + nTally.pass + ' Minor=' + nTally.minor + ' Major=' + nTally.major + ' N/A=' + nTally.na + '\n';
    summaryText += '  Shneiderman R1–R8:       Pass=' + sTally.pass + ' Minor=' + sTally.minor + ' Major=' + sTally.major + ' N/A=' + sTally.na + '\n';
    summaryText += '  Visualization V1–V17:    Pass=' + vTally.pass + ' Minor=' + vTally.minor + ' Major=' + vTally.major + ' N/A=' + vTally.na + '\n';
    summaryText += '  TOTAL (35 dimensions):   Pass=' + totPass + ' Minor=' + totMinor + ' Major=' + totMajor + ' N/A=' + totNa + '\n\n';

    if (issues.length > 0) {
      summaryText += 'ISSUES FOUND (' + issues.length + '):\n';
      issues.forEach(function (h) {
        const sev = ratings[h.id] === 'major' ? '[MAJOR]' : '[MINOR]';
        const note = notes[h.id] || '(no note)';
        summaryText += '  ' + sev + ' ' + h.code + ' ' + h.label + '\n    ' + note + '\n';
      });
    } else {
      summaryText += 'No issues flagged yet. Complete ratings on all three tabs.\n';
    }

    container.innerHTML =
      '<div id="ka-critic-summary-tab">' +
        '<div style="font-size:.78rem;font-weight:700;color:#6b3fa0;margin-bottom:6px">Overall (35 dimensions)</div>' +
        '<div class="ka-summary-stats">' +
          '<div class="ka-stat-chip" style="border-color:#a7f3d0"><div class="ka-stat-num" style="color:#059669">' + totPass + '</div><div class="ka-stat-label">Pass</div></div>' +
          '<div class="ka-stat-chip" style="border-color:#fcd34d"><div class="ka-stat-num" style="color:#d97706">' + totMinor + '</div><div class="ka-stat-label">Minor Issues</div></div>' +
          '<div class="ka-stat-chip" style="border-color:#fca5a5"><div class="ka-stat-num" style="color:#dc2626">' + totMajor + '</div><div class="ka-stat-label">Major Fails</div></div>' +
        '</div>' +
        '<div style="font-size:.76rem;color:#6b7280;margin-bottom:6px">By section</div>' +
        '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-bottom:14px">' +
          buildSectionMini('Nielsen H1–10', nTally, '#6b3fa0') +
          buildSectionMini('Shneiderman R1–8', sTally, '#0e7490') +
          buildSectionMini('Viz V1–17', vTally, '#d97706') +
        '</div>' +
        '<div class="ka-summary-text" id="ka-summary-output">' + escHtml(summaryText) + '</div>' +
        '<div style="font-size:.76rem;color:#9ca3af;margin-bottom:10px">Sessions saved locally. Future version will POST to instructor dashboard.</div>' +
        '<div class="ka-action-row">' +
          '<button class="ka-action-btn ka-copy-btn" id="ka-copy-btn">⎘ Copy critique</button>' +
          '<button class="ka-action-btn ka-save-btn" id="ka-save-btn">💾 Save session</button>' +
          '<button class="ka-action-btn ka-reset-btn" id="ka-reset-btn">✕ New critique</button>' +
        '</div>' +
      '</div>';

    container.querySelector('#ka-copy-btn').addEventListener('click', function () {
      navigator.clipboard.writeText(summaryText).then(function () {
        container.querySelector('#ka-copy-btn').textContent = 'Copied ✓';
        setTimeout(function () { container.querySelector('#ka-copy-btn').textContent = '⎘ Copy critique'; }, 2000);
      });
    });

    container.querySelector('#ka-save-btn').addEventListener('click', function () {
      saveCurrentSession();
      container.querySelector('#ka-save-btn').textContent = 'Saved ✓';
      setTimeout(function () { container.querySelector('#ka-save-btn').textContent = '💾 Save session'; }, 2000);
    });

    container.querySelector('#ka-reset-btn').addEventListener('click', function () {
      if (confirm('Start a new critique? Current session is saved to History.')) {
        saveCurrentSession();
        currentSession = createSession(capturePageContext());
        renderTab('heuristics');
        document.querySelectorAll('.ka-critic-tab').forEach(function (t) { t.classList.remove('active'); });
        document.querySelectorAll('.ka-critic-tab')[0].classList.add('active');
      }
    });
  }

  function buildSectionMini(label, tally, color) {
    return '<div style="border:1px solid #e5e7eb;border-radius:6px;padding:7px;text-align:center">' +
      '<div style="font-size:.68rem;font-weight:700;color:' + color + ';margin-bottom:4px">' + escHtml(label) + '</div>' +
      '<div style="display:flex;justify-content:center;gap:4px;flex-wrap:wrap">' +
        (tally.pass > 0 ? '<span style="font-size:.68rem;background:#d1fae5;color:#065f46;border-radius:3px;padding:1px 5px">' + tally.pass + ' ✓</span>' : '') +
        (tally.minor > 0 ? '<span style="font-size:.68rem;background:#fef3c7;color:#92400e;border-radius:3px;padding:1px 5px">' + tally.minor + ' !</span>' : '') +
        (tally.major > 0 ? '<span style="font-size:.68rem;background:#fee2e2;color:#991b1b;border-radius:3px;padding:1px 5px">' + tally.major + ' ✕</span>' : '') +
        (tally.unrated > 0 ? '<span style="font-size:.68rem;background:#f3f4f6;color:#6b7280;border-radius:3px;padding:1px 5px">' + tally.unrated + ' —</span>' : '') +
      '</div>' +
    '</div>';
  }

  function renderHistoryTab(container) {
    const sessions = loadSessions();
    if (sessions.length === 0) {
      container.innerHTML = '<div style="padding:24px;text-align:center;color:#9ca3af;font-size:.88rem">No saved critiques yet.<br>Complete a session and click "Save session."</div>';
      return;
    }
    container.innerHTML =
      '<div id="ka-critic-history-tab">' +
      sessions.map(function (s) {
        const ratings = s.ratings || {};
        const all = NIELSEN.concat(SHNEIDERMAN).concat(VIZ_HEURISTICS);
        let pass = 0, minor = 0, major = 0;
        all.forEach(function (h) {
          const r = ratings[h.id];
          if (r === 'pass') pass++; else if (r === 'minor') minor++; else if (r === 'major') major++;
        });
        const title = s.context ? (s.context.h1 || s.context.title || 'Unnamed') : 'Unnamed';
        const date = s.savedAt ? new Date(s.savedAt).toLocaleString() : 'Unknown date';
        const hasViz = s.context && s.context.vizElements && s.context.vizElements.length > 0;
        return '<div class="ka-hist-item" data-sid="' + s.id + '">' +
          '<div class="ka-hist-title">' + escHtml(title.slice(0, 60)) + (hasViz ? ' <span style="font-size:.68rem;background:#fef3c7;color:#92400e;border-radius:3px;padding:1px 5px">📊 viz</span>' : '') + '</div>' +
          '<div class="ka-hist-meta">' + date + '</div>' +
          '<div class="ka-hist-pills">' +
            (pass > 0 ? '<span class="ka-hist-pill" style="background:#d1fae5;color:#065f46">' + pass + ' pass</span>' : '') +
            (minor > 0 ? '<span class="ka-hist-pill" style="background:#fef3c7;color:#92400e">' + minor + ' minor</span>' : '') +
            (major > 0 ? '<span class="ka-hist-pill" style="background:#fee2e2;color:#991b1b">' + major + ' major</span>' : '') +
          '</div>' +
        '</div>';
      }).join('') +
      '</div>';

    container.querySelectorAll('.ka-hist-item').forEach(function (item) {
      item.addEventListener('click', function () {
        const sid = item.dataset.sid;
        const s = sessions.find(function (x) { return x.id === sid; });
        if (s) {
        currentSession = s;
        const tabs = document.querySelectorAll('.ka-critic-tab');
        tabs.forEach(function (t) { t.classList.remove('active'); });
        tabs[0].classList.add('active');
        renderTab('heuristics');
      }
      });
    });
  }

  /* ── Session helpers ──────────────────────────────────────────────── */

  function createSession(ctx) {
    return {
      id: 'sess_' + Date.now(),
      context: ctx,
      ratings: {},
      notes: {},
      savedAt: new Date().toISOString()
    };
  }

  function saveCurrentSession() {
    if (!currentSession) return;
    currentSession.savedAt = new Date().toISOString();
    saveSession(currentSession);
  }

  /* ── Panel toggle ─────────────────────────────────────────────────── */

  function togglePanel() {
    panelOpen ? closePanel() : openPanel();
  }

  function openPanel() {
    panelOpen = true;
    // Refresh context if URL changed
    const newCtx = capturePageContext();
    if (!currentSession || currentSession.context.url !== newCtx.url) {
      if (currentSession && Object.keys(currentSession.ratings).length > 0) saveCurrentSession();
      currentSession = createSession(newCtx);
    }
    const panel = document.getElementById('ka-critic-panel');
    const overlay = document.getElementById('ka-critic-overlay');
    if (panel) { panel.classList.add('open'); buildPanel(panel); }
    if (overlay) overlay.style.display = 'block';
  }

  function closePanel() {
    panelOpen = false;
    saveCurrentSession();
    const panel = document.getElementById('ka-critic-panel');
    const overlay = document.getElementById('ka-critic-overlay');
    if (panel) panel.classList.remove('open');
    if (overlay) overlay.style.display = 'none';
  }

  /* ── Utilities ────────────────────────────────────────────────────── */

  function escHtml(s) {
    return (s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  /* ── Init ─────────────────────────────────────────────────────────── */

  function init() {
    if (widgetEl) return;
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', buildWidget);
    } else {
      buildWidget();
    }
  }

  /* ── Public API ───────────────────────────────────────────────────── */

  window.KA_CRITIC = {
    init:       init,
    open:       openPanel,
    close:      closePanel,
    getSessions: loadSessions
  };

})();
