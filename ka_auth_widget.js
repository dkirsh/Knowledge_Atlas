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
  function getToken()   { return localStorage.getItem('ka_access_token'); }
  function getUser()    {
    try { return JSON.parse(localStorage.getItem('ka_current_user') || 'null'); } catch (_) { return null; }
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
    '.ka-aw-menu-item.logout { color:#c0392b; }'
  ].join('\n');
  document.head.appendChild(css);

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
