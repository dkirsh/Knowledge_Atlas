/**
 * ka_page_function.js
 * Knowledge Atlas — Page Function Spec Overlay
 *
 * Injects a discreet "Page function spec" button at the bottom-left of every
 * KA page. Visible only when the user is logged in (checked via localStorage
 * flag 'ka_logged_in' = '1' set by ka_login.html). Clicking opens a structured
 * side-panel overlay showing the page's audience, purpose, workflow position,
 * and what it is / is not for — for use by GUI track evaluators.
 *
 * Usage: include <script src="ka_page_function.js"></script> in every page,
 * with window.KA_PAGE_FUNCTION defined before the script tag (or after — the
 * script waits for DOMContentLoaded).
 *
 * window.KA_PAGE_FUNCTION = {
 *   pageId:       'ka_sensors',           // matches filename sans extension
 *   title:        'Signal / Measuring Instrument Catalogue',
 *   audience:     'Students (operationalization stage); researchers selecting instruments',
 *   purpose:      'One-paragraph description ...',
 *   workflowPos:  'Between Hypothesis (stage 3) and Operationalize (stage 4) in the 6-stage model',
 *   notFor:       'Article search, evidence browsing, credence assessment',
 *   phase:        'Phase 2 — Data Seeding',   // critical-path phase to make this live
 *   evalQuestions: [
 *     'Does the tier badge (PRIMARY / AUXILIARY) communicate construct relevance clearly?',
 *     ...
 *   ]
 * };
 */

(function () {
  'use strict';

  const CSS = `
    #ka-fn-btn {
      position: fixed; bottom: 16px; left: 20px; z-index: 9990;
      display: none; /* shown only when logged in */
      background: rgba(28,61,58,0.88); color: #A8C8BF;
      font-family: Arial, sans-serif; font-size: 0.67rem; font-weight: 700;
      letter-spacing: 0.1em; text-transform: uppercase;
      padding: 4px 11px; border-radius: 10px; cursor: pointer;
      border: none; transition: background 0.15s, color 0.15s;
      user-select: none;
    }
    #ka-fn-btn:hover { background: #1C3D3A; color: #F5A623; }

    #ka-fn-overlay {
      display: none; position: fixed; inset: 0; z-index: 99990;
      background: rgba(0,0,0,0.45); backdrop-filter: blur(2px);
    }
    #ka-fn-panel {
      position: fixed; right: 0; top: 0; bottom: 0;
      width: 440px; max-width: 95vw; background: #fff;
      box-shadow: -8px 0 32px rgba(0,0,0,0.22);
      display: flex; flex-direction: column;
      font-family: Arial, sans-serif;
      animation: kaFnSlide 0.22s ease;
    }
    @keyframes kaFnSlide {
      from { transform: translateX(40px); opacity: 0; }
      to   { transform: translateX(0);    opacity: 1; }
    }
    #ka-fn-header {
      background: linear-gradient(135deg, #1C3D3A 0%, #163230 100%);
      padding: 18px 20px 14px;
      display: flex; align-items: flex-start; gap: 10px;
    }
    #ka-fn-header-text { flex: 1; }
    #ka-fn-super {
      font-size: 0.65rem; font-weight: 700; letter-spacing: 0.14em;
      text-transform: uppercase; color: #7AACA0; margin-bottom: 4px;
    }
    #ka-fn-title {
      font-family: Georgia, serif; font-size: 1rem; color: #fff;
      line-height: 1.35; font-weight: 600;
    }
    #ka-fn-close {
      background: rgba(255,255,255,0.14); border: none; color: #fff;
      width: 28px; height: 28px; border-radius: 50%; font-size: 1rem;
      cursor: pointer; flex-shrink: 0;
    }
    #ka-fn-close:hover { background: rgba(255,255,255,0.28); }
    #ka-fn-body {
      overflow-y: auto; flex: 1; padding: 0;
    }
    .fn-section {
      padding: 14px 20px; border-bottom: 1px solid #EEE9E3;
    }
    .fn-section:last-child { border-bottom: none; }
    .fn-label {
      font-size: 0.65rem; font-weight: 700; letter-spacing: 0.11em;
      text-transform: uppercase; color: #B0A090; margin-bottom: 7px;
    }
    .fn-text {
      font-family: Georgia, serif; font-size: 0.87rem; color: #2D2D2D;
      line-height: 1.65;
    }
    .fn-phase-pill {
      display: inline-block; padding: 4px 11px; border-radius: 20px;
      font-size: 0.76rem; font-weight: 700; background: #E0F2EE;
      color: #1C3D3A; border: 1px solid #B8DDD5;
    }
    .fn-not-for {
      background: #FFF8F0; border-left: 3px solid #E8872A;
      padding: 9px 12px; border-radius: 0 5px 5px 0;
      font-size: 0.84rem; color: #5A3010; line-height: 1.5;
    }
    .fn-eval-list { list-style: none; padding: 0; margin: 0; }
    .fn-eval-list li {
      padding: 7px 0 7px 22px; position: relative;
      font-size: 0.84rem; color: #2D2D2D; line-height: 1.5;
      border-bottom: 1px dashed #EEE9E3;
    }
    .fn-eval-list li:last-child { border-bottom: none; }
    .fn-eval-list li::before {
      content: "?"; position: absolute; left: 0;
      font-size: 0.75rem; font-weight: 700; color: #E8872A;
      background: #FFF0CC; border-radius: 50%;
      width: 16px; height: 16px; display: flex; align-items: center;
      justify-content: center; top: 8px;
    }
    #ka-fn-footer {
      padding: 12px 20px; background: #F7F4EF;
      border-top: 1px solid #E0DAD3;
      font-size: 0.74rem; color: #9A8A78; font-style: italic;
      text-align: center; line-height: 1.5;
    }
  `;

  function injectStyles() {
    const el = document.createElement('style');
    el.textContent = CSS;
    document.head.appendChild(el);
  }

  function isLoggedIn() {
    return localStorage.getItem('ka_logged_in') === '1' ||
           sessionStorage.getItem('ka_logged_in') === '1' ||
           // fallback for demo: show if URL has ?fnspec=1
           new URLSearchParams(window.location.search).get('fnspec') === '1';
  }

  function buildPanel(spec) {
    // Overlay backdrop
    const overlay = document.createElement('div');
    overlay.id = 'ka-fn-overlay';
    overlay.addEventListener('click', closePanel);

    const panel = document.createElement('div');
    panel.id = 'ka-fn-panel';
    panel.addEventListener('click', e => e.stopPropagation());

    panel.innerHTML = `
      <div id="ka-fn-header">
        <div id="ka-fn-header-text">
          <div id="ka-fn-super">Page Function Specification</div>
          <div id="ka-fn-title">${spec.title || 'Untitled page'}</div>
        </div>
        <button id="ka-fn-close" onclick="document.getElementById('ka-fn-overlay').style.display='none'; document.body.style.overflow='';">✕</button>
      </div>

      <div id="ka-fn-body">
        <div class="fn-section">
          <div class="fn-label">Primary Audience</div>
          <div class="fn-text">${spec.audience || '—'}</div>
        </div>

        <div class="fn-section">
          <div class="fn-label">Page Purpose</div>
          <div class="fn-text">${spec.purpose || '—'}</div>
        </div>

        <div class="fn-section">
          <div class="fn-label">Position in Student Workflow</div>
          <div class="fn-text">${spec.workflowPos || '—'}</div>
        </div>

        <div class="fn-section">
          <div class="fn-label">This page is NOT for</div>
          <div class="fn-not-for">${spec.notFor || '—'}</div>
        </div>

        <div class="fn-section">
          <div class="fn-label">Critical Path Phase to Make Live</div>
          <span class="fn-phase-pill">${spec.phase || '—'}</span>
        </div>

        ${spec.evalQuestions && spec.evalQuestions.length ? `
        <div class="fn-section">
          <div class="fn-label">GUI Track Evaluation Questions</div>
          <ul class="fn-eval-list">
            ${spec.evalQuestions.map(q => `<li>${q}</li>`).join('')}
          </ul>
        </div>` : ''}
      </div>

      <div id="ka-fn-footer">
        GUI Track evaluation tool · KA v0.4 · Visible to logged-in users only
      </div>
    `;

    overlay.appendChild(panel);
    document.body.appendChild(overlay);
  }

  function openPanel() {
    const overlay = document.getElementById('ka-fn-overlay');
    if (overlay) {
      overlay.style.display = 'block';
      document.body.style.overflow = 'hidden';
    }
  }

  function closePanel() {
    const overlay = document.getElementById('ka-fn-overlay');
    if (overlay) overlay.style.display = 'none';
    document.body.style.overflow = '';
  }

  function buildButton() {
    const btn = document.createElement('button');
    btn.id = 'ka-fn-btn';
    btn.textContent = '⊙ Page function spec';
    btn.title = 'View the function specification for this page (GUI track evaluators only)';
    btn.addEventListener('click', openPanel);
    document.body.appendChild(btn);
    return btn;
  }

  document.addEventListener('DOMContentLoaded', function () {
    const spec = window.KA_PAGE_FUNCTION;
    if (!spec) return; // page hasn't defined a spec — skip silently

    injectStyles();

    const btn = buildButton();
    if (isLoggedIn()) {
      btn.style.display = 'block';
    }

    buildPanel(spec);

    // Also listen for login state changes within the session
    window.addEventListener('storage', function (e) {
      if (e.key === 'ka_logged_in') {
        btn.style.display = e.newValue === '1' ? 'block' : 'none';
      }
    });

    // Keyboard shortcut: Shift+F (for Function spec) — only when logged in
    document.addEventListener('keydown', function (e) {
      if (e.shiftKey && e.key === 'F' && isLoggedIn()) {
        const overlay = document.getElementById('ka-fn-overlay');
        if (overlay.style.display === 'block') { closePanel(); } else { openPanel(); }
      }
      if (e.key === 'Escape') { closePanel(); }
    });
  });

})();
