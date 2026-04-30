/* _track_side_nav.js
 * Shared left-rail sub-nav for every track page.
 *
 * Each page declares its identity on the empty <aside class="side-nav">
 * via:   data-side-nav-page="t1_task2"
 *
 * That string is the page-id key in the manifest below. The script then
 * paints the same cross-track navigation on every page, with:
 *   - the current track auto-expanded (<details open>)
 *   - the current item marked .active
 *
 * To add a new track or rename an item, edit only the MANIFEST. The HTML
 * across all pages does not change.
 *
 * Author: Cowork session for Prof. David Kirsh, COGS 160 SP, 2026-04-27.
 */
(function(){
  'use strict';

  /* ─────────────────────────────────────────────────────────────
   * Top-level (above all tracks) — Global Home, Syllabus, Course Setup.
   * These do NOT change per page.
   * ───────────────────────────────────────────────────────────── */
  var TOP_LINKS = [
    { label: 'Global Home', href: '../ka_home.html', icon: '⌂' },
    { label: '160 Syllabus', href: 'ka_schedule.html', icon: '☰' },
    { label: 'Course Setup', href: 'ka_student_setup.html', icon: '⚙' }
  ];

  /* ─────────────────────────────────────────────────────────────
   * Track manifest. Order = display order.
   * Each item.id matches the data-side-nav-page on the corresponding page.
   * "stub: true" marks a track without canonical pages yet (Track 4 today).
   * ───────────────────────────────────────────────────────────── */
  var TRACKS = [
    {
      id: 't1',
      label: 'Track 1: Image Tagger',
      stub: false,
      items: [
        { id: 't1_intro',       href: 't1_intro.html',       label: 'Track Intro' },
        { id: 't1_task1',       href: 't1_task1.html',       label: 'Task 1: Build Image Collection' },
        { id: 't1_task2',       href: 't1_task2.html',       label: 'Task 2: Build Latent Tag Detectors' },
        { id: 't1_task3',       href: 't1_task3.html',       label: 'Task 3: Annotate & Build Image Viewer' },
        { id: 't1_submissions', href: 't1_submissions.html', label: 'Submissions' }
      ]
    },
    {
      id: 't2',
      label: 'Track 2: Article Finder',
      stub: false,
      items: [
        { id: 't2_intro',       href: 't2_intro.html',       label: 'Track Intro' },
        { id: 't2_task1',       href: 't2_task1.html',       label: 'Task 1: Fix the Contribute Page' },
        { id: 't2_task2',       href: 't2_task2.html',       label: 'Task 2: Gap Targeting & Queries' },
        { id: 't2_task3',       href: 't2_task3.html',       label: 'Task 3: Search Execution & Triage' },
        { id: 't2_submissions', href: 't2_submissions.html', label: 'Submissions' }
      ]
    },
    {
      id: 't3',
      label: 'Track 3: VR Studio',
      stub: false,
      items: [
        { id: 't3_intro',       href: 't3_intro.html',       label: 'Track Intro' },
        { id: 't3_task1',       href: 't3_task1.html',       label: 'Task 1: Infinigen Setup & Manifests' },
        { id: 't3_task2',       href: 't3_task2.html',       label: 'Task 2: Render Pipeline & Gallery' },
        { id: 't3_task3',       href: 't3_task3.html',       label: 'Task 3: AI Front-End & Worship Flagship' },
        { id: 't3_submissions', href: 't3_submissions.html', label: 'Submissions' }
      ]
    },
    {
      id: 't4',
      label: 'Track 4: GUI / Interactivity',
      stub: false,
      items: [
        { id: 't4_intro',       href: 't4_intro.html',       label: 'Track Intro' },
        { id: 't4_task1',       href: 't4_task1.html',       label: 'Task 1: Build the Question Corpus' },
        { id: 't4_task2',       href: 't4_task2.html',       label: 'Task 2: Winnow & Fit Answer Shapes' },
        { id: 't4_task3',       href: 't4_task3.html',       label: 'Task 3: Prototype an Evidential Journey' },
        { id: 't4_submissions', href: 't4_submissions.html', label: 'Submissions' }
      ]
    }
  ];

  /* ─────────────────────────────────────────────────────────────
   * Helpers
   * ───────────────────────────────────────────────────────────── */
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){
    return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c];
  }); }

  function findTrackForPage(pageId){
    if (!pageId) return null;
    for (var i = 0; i < TRACKS.length; i++){
      var t = TRACKS[i];
      for (var j = 0; j < t.items.length; j++){
        if (t.items[j].id === pageId) return { track: t, item: t.items[j] };
      }
    }
    return null;
  }

  /* ─────────────────────────────────────────────────────────────
   * Renderer
   * ───────────────────────────────────────────────────────────── */
  function renderInto(aside){
    var pageId = aside.getAttribute('data-side-nav-page') || '';
    var ctx = findTrackForPage(pageId);
    var currentTrackId = ctx ? ctx.track.id : null;

    var parts = [];

    // Top-level links
    parts.push('<div class="side-nav-top-block">');
    TOP_LINKS.forEach(function(top){
      parts.push(
        '<a class="side-nav-top" href="' + esc(top.href) + '">' +
          '<span class="side-nav-top-icon" aria-hidden="true">' + esc(top.icon) + '</span>' +
          esc(top.label) +
        '</a>'
      );
    });
    parts.push('</div>');

    // Per-track twisties
    parts.push('<div class="side-nav-tracks">');
    parts.push('<div class="side-nav-tracks-label">Tracks</div>');
    TRACKS.forEach(function(track){
      var isCurrent = (track.id === currentTrackId);
      var detailsAttrs = isCurrent ? ' open' : '';
      var stubClass = track.stub ? ' side-nav-track-stub' : '';
      var stubBadge = track.stub ? ' <span class="side-nav-stub-badge">stub</span>' : '';

      var intro = track.items && track.items.length ? track.items[0] : null;
      var introHref = intro ? intro.href : '#';
      parts.push('<details class="side-nav-track' + stubClass + '"' + detailsAttrs + '>');
      parts.push('<summary><span class="side-nav-twistie" aria-hidden="true"></span>' +
                 '<a class="side-nav-track-link" href="' + esc(introHref) + '">' +
                 esc(track.label) + '</a>' + stubBadge + '</summary>');
      parts.push('<div class="side-nav-track-items">');
      track.items.forEach(function(item){
        var activeClass = (item.id === pageId) ? ' active' : '';
        var stubMark = item.stub ? ' <span class="side-nav-item-stub" title="not yet built">·stub</span>' : '';
        parts.push('<a class="side-nav-item' + activeClass + '" href="' + esc(item.href) + '"' +
                   (item.id === pageId ? ' aria-current="page"' : '') + '>' +
                   esc(item.label) + stubMark + '</a>');
      });
      parts.push('</div>');
      parts.push('</details>');
    });
    parts.push('</div>');

    aside.innerHTML = parts.join('');
  }

  /* ─────────────────────────────────────────────────────────────
   * Boot
   * ───────────────────────────────────────────────────────────── */
  function boot(){
    var asides = document.querySelectorAll('aside.side-nav[data-side-nav-page]');
    for (var i = 0; i < asides.length; i++){
      renderInto(asides[i]);
    }
  }
  if (document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
