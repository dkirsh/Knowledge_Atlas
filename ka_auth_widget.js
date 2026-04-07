/**
 * ka_auth_widget.js
 * Persistent login / profile / logout widget for every KA page.
 *
 * Include this script on any page:
 *   <script src="ka_auth_widget.js"></script>
 *   (use "../ka_auth_widget.js" from 160sp/ subdirectory pages)
 *
 * It reads auth state from localStorage and injects a small widget
 * into the page's existing navbar — no markup changes needed.
 */
(function () {
  'use strict';

  // ── Auth helpers ─────────────────────────────────────────────────
  function getToken()   { return localStorage.getItem('ka_access_token') || localStorage.getItem('katlas_token'); }
  function getUser()    {
    try {
      var user = JSON.parse(localStorage.getItem('ka_current_user') || 'null');
      if (user) return user;
    } catch (_) {}
    var legacyUser = localStorage.getItem('katlas_user');
    return legacyUser ? { email: legacyUser } : null;
  }
  function isLoggedIn() { return !!(getToken() && getUser()); }

  function logout() {
    localStorage.removeItem('katlas_token');
    localStorage.removeItem('katlas_user');
    localStorage.removeItem('ka_access_token');
    localStorage.removeItem('ka_refresh_token');
    localStorage.removeItem('ka_current_user');
    localStorage.removeItem('ka_logged_in');
    window.location.reload();
  }

  function initials(user) {
    if (!user) return '?';
    var f = (user.first_name || user.firstName || '').trim();
    var l = (user.last_name  || user.lastName  || '').trim();
    return ((f[0] || '') + (l[0] || '')).toUpperCase() || '?';
  }

  function displayName(user) {
    if (!user) return '';
    var parts = [user.first_name || user.firstName, user.last_name || user.lastName].filter(Boolean);
    return parts.join(' ').trim() || user.email || '';
  }

  // ── Resolve paths (handles pages in subdirectories) ──────────────
  var scripts = document.getElementsByTagName('script');
  var basePath = '';
  for (var i = 0; i < scripts.length; i++) {
    var src = scripts[i].getAttribute('src') || '';
    if (src.indexOf('ka_auth_widget') !== -1) {
      basePath = src.replace(/ka_auth_widget\.js.*$/, '');
      break;
    }
  }

  // ── Inject styles ────────────────────────────────────────────────
  var css = document.createElement('style');
  css.textContent = [
    '.ka-aw { display:flex; align-items:center; gap:10px; margin-left:auto; font-family:Arial,sans-serif; font-size:0.82rem; }',
    '.ka-aw-avatar { width:30px; height:30px; border-radius:50%; background:#E8872A; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.72rem; letter-spacing:0.04em; cursor:pointer; position:relative; }',
    '.ka-aw-name { color:rgba(255,255,255,.85); max-width:120px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }',
    '.ka-aw-btn { background:none; border:1px solid rgba(255,255,255,.25); color:rgba(255,255,255,.8); padding:4px 12px; border-radius:5px; font-size:0.78rem; cursor:pointer; text-decoration:none; transition:background .15s,color .15s; }',
    '.ka-aw-btn:hover { background:rgba(255,255,255,.12); color:#fff; }',
    '.ka-aw-btn-accent { background:#E8872A; border-color:#E8872A; color:#fff; font-weight:600; }',
    '.ka-aw-btn-accent:hover { background:#C05A1F; border-color:#C05A1F; }',
    '.ka-aw-logout { background:none; border:none; color:rgba(255,255,255,.5); font-size:0.76rem; cursor:pointer; padding:4px 6px; }',
    '.ka-aw-logout:hover { color:#fff; }',
    '.ka-aw-menu { display:none; position:absolute; top:36px; right:0; background:#fff; border-radius:10px; box-shadow:0 4px 20px rgba(0,0,0,.15); min-width:200px; z-index:9999; padding:8px 0; }',
    '.ka-aw-menu.open { display:block; }',
    '.ka-aw-menu-header { padding:12px 16px; border-bottom:1px solid #EDE8E0; }',
    '.ka-aw-menu-name { font-weight:700; color:#1C3D3A; font-size:0.88rem; }',
    '.ka-aw-menu-email { color:#7A6E62; font-size:0.78rem; margin-top:2px; }',
    '.ka-aw-menu-item { display:block; width:100%; text-align:left; padding:10px 16px; background:none; border:none; font-size:0.84rem; color:#4A3E32; cursor:pointer; text-decoration:none; }',
    '.ka-aw-menu-item:hover { background:#F7F4EF; }',
    '.ka-aw-menu-sep { border-top:1px solid #EDE8E0; margin:4px 0; }',
    '.ka-aw-menu-item.logout { color:#c0392b; }',
    '.ka-160sp-nav-fallback { background:#1C3D3A; display:flex; align-items:center; gap:18px; padding:0 28px; min-height:52px; position:sticky; top:0; z-index:500; border-bottom:2px solid #E8872A; }',
    '.ka-160sp-nav-fallback .ka-nav-home { color:#A8C8BF; font-size:0.78rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; text-decoration:none; }',
    '.ka-160sp-breadcrumb-fallback { background:#EDE8E0; padding:8px 28px; font-size:0.78rem; color:#6A5E50; display:flex; align-items:center; gap:6px; flex-wrap:wrap; }',
    '.ka-160sp-breadcrumb-fallback a { color:#1C3D3A; text-decoration:none; font-weight:600; }',
    '.ka-week-links { margin-left:auto; display:flex; align-items:center; gap:8px; flex-wrap:wrap; font-size:0.76rem; }',
    '.ka-week-links-label { font-weight:800; color:#1C3D3A; white-space:nowrap; }',
    '.ka-week-link { color:#2A7868; text-decoration:none; font-weight:650; white-space:nowrap; }',
    '.ka-week-link:hover { color:#1C3D3A; text-decoration:underline; }',
    '.ka-160sp-nav-center { display:flex; align-items:center; gap:14px; flex:1; }',
    '.ka-160sp-nav-center .nav-link { color:#7AACA0; font-size:0.8rem; text-decoration:none; padding:6px 10px; border-radius:6px; }',
    '.ka-160sp-nav-center .nav-link:hover { color:#fff; background:rgba(255,255,255,0.08); }'
  ].join('\n');
  document.head.appendChild(css);

  // ── COGS 160 header helpers ─────────────────────────────────────
  var CANONICAL_160SP_NAV = [
    { id: 'nav-shell-explore', label: 'Explore', href: '../ka_topics.html' },
    { id: 'nav-shell-evidence', label: 'Evidence', href: '../ka_evidence.html' },
    { id: 'nav-shell-gaps', label: 'Gaps', href: '../ka_gaps.html' },
    { id: 'nav-shell-articles', label: 'Articles', href: '../ka_article_search.html' },
    { id: 'nav-shell-contribute', label: 'Contribute', href: '../ka_contribute.html' },
    { id: 'nav-shell-course', label: 'Course', href: 'ka_student_setup.html' },
    { id: 'nav-shell-syllabus', label: '160 Syllabus', href: 'ka_schedule.html' }
  ];

  var WEEK_LINKS = {
    1: [
      { label: 'Week 1 Agenda', href: 'week1_agenda.html' },
      { label: 'Register', href: '../ka_register.html' },
      { label: 'Topics', href: '../ka_topics.html' },
      { label: 'Question Maker', href: '../ka_question_maker.html' },
      { label: 'Submit Articles', href: '../ka_article_propose.html' }
    ],
    2: [
      { label: 'Week 2 Agenda', href: 'week2_agenda.html' },
      { label: 'Programming Exercises', href: 'week2_exercises.html' },
      { label: 'Demo: PDF Relevance Filter', href: 'demo_pdf_relevance_filter.html' },
      { label: 'Live Demo', href: 'week2_agenda.html' },
      { label: 'Technical Setup', href: 'ka_technical_setup.html' }
    ],
    3: [
      { label: 'Week 3 Agenda', href: 'week3_agenda.html' },
      { label: 'Student Setup', href: 'ka_student_setup.html' },
      { label: 'Tracks', href: 'ka_tracks.html' }
    ],
    4: [
      { label: 'Week 4 Agenda', href: 'week4_agenda.html' },
      { label: 'T1 Workbook', href: 'ka_tag_assignment.html' },
      { label: 'T2 Workbook', href: 'ka_article_finder_assignment.html' },
      { label: 'T3 Workbook', href: 'ka_vr_assignment.html' },
      { label: 'T4 Workbook', href: 'ka_gui_assignment.html' }
    ],
    5: [{ label: 'Week 5 Agenda', href: 'week5_agenda.html' }],
    6: [{ label: 'Week 6 Agenda', href: 'week6_agenda.html' }],
    7: [{ label: 'Week 7 Agenda', href: 'week7_agenda.html' }],
    8: [
      { label: 'Week 8 Agenda', href: 'week8_agenda.html' },
      { label: 'Phase 3 Assignment', href: '../Designing_Experiments/docs/student_tracks/phase3_wk08.html' }
    ],
    9: [{ label: 'Phase 3 Week 9', href: '../Designing_Experiments/docs/student_tracks/phase3_wk09.html' }],
    10: [{ label: 'Phase 3 Week 10', href: '../Designing_Experiments/docs/student_tracks/phase3_wk10.html' }]
  };

  var PAGE_WEEK_OVERRIDES = {
    'week1_agenda.html': 1,
    'week2_agenda.html': 2,
    'week2_exercises.html': 2,
    'atlas_system_architecture.html': 2,
    'demo_pdf_relevance_filter.html': 2,
    'ex0_mechanism_pathway_tracer.html': 2,
    'ka_technical_setup.html': 2,
    'week3_agenda.html': 3,
    'week4_agenda.html': 4,
    'ka_tag_assignment.html': 4,
    'ka_article_finder_assignment.html': 4,
    'ka_vr_assignment.html': 4,
    'ka_gui_assignment.html': 4,
    'week5_agenda.html': 5,
    'week6_agenda.html': 6,
    'week7_agenda.html': 7,
    'week8_agenda.html': 8
  };

  function is160spPage() {
    return /\/160sp\//.test(window.location.pathname);
  }

  function currentCourseWeek() {
    var weekOneMonday = new Date(2026, 2, 30); // First Monday of Spring 2026 Week 1.
    var today = new Date();
    var todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    var days = Math.floor((todayStart - weekOneMonday) / 86400000);
    return Math.max(1, Math.min(10, Math.floor(days / 7) + 1));
  }

  function pageWeek() {
    var file = window.location.pathname.split('/').pop() || '';
    var m = file.match(/^week(\d+)_agenda\.html$/);
    if (m) return Math.max(1, Math.min(10, parseInt(m[1], 10)));
    return PAGE_WEEK_OVERRIDES[file] || currentCourseWeek();
  }

  function makeNavLink(item) {
    var a = document.createElement('a');
    a.id = item.id;
    a.href = item.href;
    a.className = 'nav-link';
    a.textContent = item.label;
    return a;
  }

  function ensure160spNav() {
    if (!is160spPage()) return;
    var nav = document.querySelector('nav.top-nav, nav.ka-nav, nav');
    if (!nav) {
      nav = document.createElement('nav');
      nav.className = 'top-nav';
      document.body.insertBefore(nav, document.body.firstChild);
    }

    var navCenter = nav.querySelector('.nav-center');
    if (!navCenter) {
      navCenter = document.createElement('div');
      navCenter.className = 'nav-center ka-160sp-nav-center';
      var right = nav.querySelector('.nav-right');
      nav.insertBefore(navCenter, right || null);
      Array.prototype.slice.call(nav.children).forEach(function(el) {
        if (el.tagName === 'A' && el.classList.contains('nav-link')) el.parentNode.removeChild(el);
        if (el.classList.contains('nav-sep')) el.parentNode.removeChild(el);
      });
    } else {
      navCenter.classList.add('ka-160sp-nav-center');
    }

    Array.prototype.slice.call(navCenter.children).forEach(function(child) {
      navCenter.removeChild(child);
    });
    CANONICAL_160SP_NAV.forEach(function(item) {
      navCenter.appendChild(makeNavLink(item));
    });
  }

  function looksLikeBreadcrumb(el) {
    if (!el || el.querySelector('.ka-week-links')) return false;
    var text = (el.textContent || '').toLowerCase();
    return text.indexOf('home') !== -1 && (text.indexOf('cogs 160') !== -1 || text.indexOf('schedule') !== -1 || text.indexOf('dashboard') !== -1 || text.indexOf('start') !== -1);
  }

  function findBreadcrumb() {
    var direct = document.querySelector('.ka-breadcrumb, .breadcrumb-bar');
    if (direct) return direct;
    var candidates = Array.prototype.slice.call(document.querySelectorAll('body > div, body > header + div'));
    var found = candidates.find(looksLikeBreadcrumb);
    if (found) return found;

    var nav = document.querySelector('nav.top-nav, nav.ka-nav, nav');
    var breadcrumb = document.createElement('div');
    breadcrumb.className = 'ka-160sp-breadcrumb-fallback';
    breadcrumb.innerHTML = '<a href="../ka_home.html">Home</a><span>/</span><a href="ka_student_setup.html">COGS 160 Start</a><span>/</span><span>Course Page</span>';
    if (nav && nav.parentNode) nav.parentNode.insertBefore(breadcrumb, nav.nextSibling);
    else document.body.insertBefore(breadcrumb, document.body.firstChild);
    return breadcrumb;
  }

  function add160spWeekLinks() {
    if (!is160spPage()) return;
    var breadcrumb = findBreadcrumb();
    if (!breadcrumb) return;
    breadcrumb.style.display = 'flex';
    breadcrumb.style.alignItems = 'center';
    breadcrumb.style.gap = breadcrumb.style.gap || '6px';
    breadcrumb.style.flexWrap = 'wrap';

    var week = pageWeek();
    var links = WEEK_LINKS[week] || WEEK_LINKS[currentCourseWeek()] || [];
    var strip = document.createElement('div');
    strip.className = 'ka-week-links';
    strip.setAttribute('aria-label', 'Course week links');

    var label = document.createElement('span');
    label.className = 'ka-week-links-label';
    label.textContent = 'Week ' + week + ':';
    strip.appendChild(label);

    links.forEach(function(item) {
      var a = document.createElement('a');
      a.className = 'ka-week-link';
      a.href = item.href;
      a.textContent = item.label;
      strip.appendChild(a);
    });
    breadcrumb.appendChild(strip);
  }

  // ── Build widget ─────────────────────────────────────────────────
  function buildWidget() {
    var w = document.createElement('div');
    w.className = 'ka-aw';

    if (isLoggedIn()) {
      var user = getUser();

      // Avatar with dropdown
      var avatarWrap = document.createElement('div');
      avatarWrap.style.position = 'relative';

      var avatar = document.createElement('div');
      avatar.className = 'ka-aw-avatar';
      avatar.textContent = initials(user);
      avatar.title = displayName(user);

      var menu = document.createElement('div');
      menu.className = 'ka-aw-menu';
      menu.innerHTML =
        '<div class="ka-aw-menu-header">' +
          '<div class="ka-aw-menu-name">' + displayName(user) + '</div>' +
          '<div class="ka-aw-menu-email">' + (user.email || '') + '</div>' +
        '</div>' +
        '<a class="ka-aw-menu-item" href="' + basePath + '160sp/collect-articles-upload.html" style="font-weight:700;color:#E8872A;">Assignment 0</a>' +
        '<a class="ka-aw-menu-item" href="' + basePath + 'ka_user_home.html">My Workspace</a>' +
        '<a class="ka-aw-menu-item" href="' + basePath + '160sp/ka_student_setup.html">Student Setup</a>' +
        '<div class="ka-aw-menu-sep"></div>' +
        '<button class="ka-aw-menu-item logout" id="ka-aw-logout-btn">Log out</button>';

      avatarWrap.appendChild(avatar);
      avatarWrap.appendChild(menu);
      w.appendChild(avatarWrap);

      var name = document.createElement('span');
      name.className = 'ka-aw-name';
      name.textContent = displayName(user);
      w.appendChild(name);

      // Toggle menu on avatar click
      avatar.addEventListener('click', function (e) {
        e.stopPropagation();
        menu.classList.toggle('open');
      });
      document.addEventListener('click', function () { menu.classList.remove('open'); });

      // Logout handler (deferred so the button exists in DOM)
      setTimeout(function () {
        var btn = document.getElementById('ka-aw-logout-btn');
        if (btn) btn.addEventListener('click', logout);
      }, 0);

    } else {
      // Logged out: show Log In + Register
      var login = document.createElement('a');
      login.className = 'ka-aw-btn';
      login.href = basePath + 'ka_login.html';
      login.textContent = 'Log In';
      w.appendChild(login);

      var reg = document.createElement('a');
      reg.className = 'ka-aw-btn ka-aw-btn-accent';
      reg.href = basePath + 'ka_register.html';
      reg.textContent = 'Register';
      w.appendChild(reg);
    }

    return w;
  }

  // ── Inject into page nav ─────────────────────────────────────────
  function inject() {
    ensure160spNav();
    add160spWeekLinks();

    var widget = buildWidget();

    // Strategy 1: page already has a dedicated auth area we should replace
    // (ka_home.html has .btn-login + .btn-register-nav inside .nav-public)
    var existingLogin = document.querySelector('.btn-login');
    var existingReg   = document.querySelector('.btn-register-nav');
    if (existingLogin && existingReg) {
      existingLogin.parentNode.insertBefore(widget, existingLogin);
      existingLogin.style.display = 'none';
      existingReg.style.display   = 'none';
      return;
    }

    // Strategy 2: top-bar pattern (ka_user_home, ka_workflow_hub)
    var topBarUser = document.getElementById('top-bar-user-area');
    if (topBarUser) {
      // Hide original auth elements, replace with widget
      topBarUser.style.display = 'none';
      topBarUser.parentNode.appendChild(widget);
      return;
    }

    // Strategy 3: upload page (.topbar-user) — only if parent is visible
    var topbarUser = document.querySelector('.topbar-user');
    if (topbarUser) {
      var tbParent = topbarUser.parentNode;
      var parentVisible = tbParent && getComputedStyle(tbParent).display !== 'none';
      if (parentVisible) {
        topbarUser.style.display = 'none';
        tbParent.appendChild(widget);
        return;
      }
    }

    // Strategy 4: nav-right section (ka_topics, ka_contribute, ka_student_setup, ka_register)
    var navRight = document.querySelector('.nav-right');
    if (navRight) {
      // Hide any existing login/register links to avoid duplicates
      navRight.querySelectorAll('a.nav-link').forEach(function (a) {
        if (/log\s*in/i.test(a.textContent)) a.style.display = 'none';
      });
      navRight.appendChild(widget);
      return;
    }

    // Strategy 5: bare <nav> — append to the first nav element
    var nav = document.querySelector('nav') || document.querySelector('.topnav') || document.querySelector('.top-bar');
    if (nav) {
      widget.style.marginLeft = 'auto';
      nav.appendChild(widget);
    }
  }

  // Run after DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
