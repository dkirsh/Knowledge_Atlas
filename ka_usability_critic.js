/**
 * ka_usability_critic.js  —  ATLAS Usability Critique Agent
 * -----------------------------------------------------------
 * Adds a small floating "Critique" button (bottom-left) visible to
 * all COGS160 Spring 2026 students. Clicking opens a structured
 * heuristic-based critique panel.
 *
 * The panel:
 *   1. Auto-captures current page context (URL, title, headings)
 *   2. Walks through Nielsen's 10 Heuristics + Shneiderman's 8 Golden Rules
 *   3. Lets students rate each dimension (Pass / Issue / Fail) + free-text note
 *   4. Optionally generates a formatted critique summary (copyable)
 *   5. Saves results to localStorage; links to ka_article_propose.html for logging
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
      capturedAt: new Date().toISOString()
    };
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
      '</div>' +
      '<div class="ka-critic-tabs">' +
        '<button class="ka-critic-tab active" data-tab="heuristics">Nielsen H1–H10</button>' +
        '<button class="ka-critic-tab" data-tab="shneiderman">Shneiderman R1–R8</button>' +
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
      renderHeuristicTab(content, NIELSEN, 'Nielsen\'s 10 Heuristics', 'H');
    } else if (tabName === 'shneiderman') {
      renderHeuristicTab(content, SHNEIDERMAN, 'Shneiderman\'s 8 Golden Rules', 'R');
    } else if (tabName === 'summary') {
      renderSummaryTab(content);
    } else if (tabName === 'history') {
      renderHistoryTab(content);
    }
  }

  function renderHeuristicTab(container, heuristics, sectionLabel, prefix) {
    const saved = currentSession ? (currentSession.ratings || {}) : {};
    const notes = currentSession ? (currentSession.notes || {}) : {};

    container.innerHTML =
      '<div class="ka-h-section-label">' + sectionLabel + '</div>' +
      heuristics.map(function (h) {
        const currentRating = saved[h.id] || '';
        const currentNote = notes[h.id] || '';
        const ratingBtns = RATINGS.map(function (r) {
          const isSelected = currentRating === r.val;
          return '<button class="ka-rating-btn' + (isSelected ? ' selected' : '') + '"' +
            ' data-hid="' + h.id + '" data-val="' + r.val + '"' +
            ' style="' + (isSelected ? '--sel-color:' + r.color + ';--sel-bg:' + r.bg : '') + '">' +
            r.label + '</button>';
        }).join('');
        return '<div class="ka-h-row">' +
          '<div class="ka-h-row-hdr">' +
            '<div class="ka-h-code">' + h.code + '</div>' +
            '<div class="ka-h-label">' + escHtml(h.label) + '</div>' +
          '</div>' +
          '<div class="ka-h-desc">' + escHtml(h.desc) + '</div>' +
          '<div class="ka-h-rating-row">' + ratingBtns + '</div>' +
          '<textarea class="ka-h-note" data-hid="' + h.id + '" placeholder="Note any specific issue…" rows="2">' +
            escHtml(currentNote) + '</textarea>' +
        '</div>';
      }).join('');

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
    const all = NIELSEN.concat(SHNEIDERMAN);
    let pass = 0, minor = 0, major = 0, na = 0;
    all.forEach(function (h) {
      const r = ratings[h.id];
      if (r === 'pass') pass++;
      else if (r === 'minor') minor++;
      else if (r === 'major') major++;
      else if (r === 'na') na++;
    });

    // Build summary text
    const ctx = currentSession.context;
    const issues = all.filter(function (h) {
      return ratings[h.id] === 'minor' || ratings[h.id] === 'major';
    });

    let summaryText = 'USABILITY CRITIQUE — ' + (ctx ? ctx.h1 || ctx.title : 'Unknown page') + '\n';
    summaryText += 'URL: ' + (ctx ? ctx.url : '') + '\n';
    summaryText += 'Critiqued: ' + new Date().toLocaleString() + '\n\n';
    summaryText += 'SCORES: Pass=' + pass + ' Minor=' + minor + ' Major=' + major + ' N/A=' + na + '\n\n';
    if (issues.length > 0) {
      summaryText += 'ISSUES FOUND (' + issues.length + '):\n';
      issues.forEach(function (h) {
        const sev = ratings[h.id] === 'major' ? '[MAJOR]' : '[MINOR]';
        const note = notes[h.id] || '(no note)';
        summaryText += '  ' + sev + ' ' + h.code + ' ' + h.label + '\n    ' + note + '\n';
      });
    } else {
      summaryText += 'No issues flagged.\n';
    }

    container.innerHTML =
      '<div id="ka-critic-summary-tab">' +
        '<div class="ka-summary-stats">' +
          '<div class="ka-stat-chip" style="border-color:#a7f3d0"><div class="ka-stat-num" style="color:#059669">' + pass + '</div><div class="ka-stat-label">Pass</div></div>' +
          '<div class="ka-stat-chip" style="border-color:#fcd34d"><div class="ka-stat-num" style="color:#d97706">' + minor + '</div><div class="ka-stat-label">Minor Issues</div></div>' +
          '<div class="ka-stat-chip" style="border-color:#fca5a5"><div class="ka-stat-num" style="color:#dc2626">' + major + '</div><div class="ka-stat-label">Major Fails</div></div>' +
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
        const all = NIELSEN.concat(SHNEIDERMAN);
        let pass = 0, minor = 0, major = 0;
        all.forEach(function (h) {
          const r = ratings[h.id];
          if (r === 'pass') pass++; else if (r === 'minor') minor++; else if (r === 'major') major++;
        });
        const title = s.context ? (s.context.h1 || s.context.title || 'Unnamed') : 'Unnamed';
        const date = s.savedAt ? new Date(s.savedAt).toLocaleString() : 'Unknown date';
        return '<div class="ka-hist-item" data-sid="' + s.id + '">' +
          '<div class="ka-hist-title">' + escHtml(title.slice(0, 60)) + '</div>' +
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
        if (s) { currentSession = s; renderTab('heuristics'); document.querySelectorAll('.ka-critic-tab')[0].classList.add('active'); }
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
