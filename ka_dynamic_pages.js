(function(){
  'use strict';

  const CONFIG = {
    topics: {
      title:'Topics', active:'topics', type:'topic',
      kicker:'Browse-oriented entry point',
      lede:'Explore the Atlas by environmental condition, outcome, evidence status, and curiosity. This page is for users who do not yet know the right search term.',
      search:'Search topics, outcomes, theories, sensors...',
      narrative:['Interest tuner','Did You Know entry cards','Taxonomy lanes','Topic preview with papers and warrants']
    },
    theories: {
      title:'Theories', active:'theories', type:'theory',
      kicker:'Theory lattice and warrant',
      lede:'Inspect higher-level frameworks and named theories as a connected explanatory lattice, not merely a list of labels.',
      search:'Search theories, papers, topics...',
      narrative:['Why this counts as a theory','T1/T1.5 position','Representative papers','Challenges and open warrant']
    },
    mechanisms: {
      title:'Mechanisms', active:'mechanisms', type:'mechanism',
      kicker:'Causal pathway browser',
      lede:'Follow proposed chains from environmental input through mediator to cognitive, affective, physiological, or behavioral outcome.',
      search:'Search mechanisms, frameworks, temporal class...',
      narrative:['Input to mediator chain','Evidence coverage','Failure modes','Related theories and papers']
    },
    neural: {
      title:'Neural Underpinnings', active:'neural', type:'neural',
      kicker:'Plausible neural explanation',
      lede:'Separate plausible neural underpinnings from overclaim by showing framework, mechanism maturity, and readiness of each profile.',
      search:'Search neural mechanisms, framework, maturity...',
      narrative:['PNU overview','Pathway view','Confidence bands','Competing explanations']
    },
    papers: {
      title:'Papers', active:'articles', type:'paper',
      kicker:'Destination pages for papers',
      lede:'A paper is a destination: summary, figures, PNU, interpretation, possible objections, and links into theory and argumentation.',
      search:'Search paper title, DOI, topic, theory...',
      narrative:['Science-writer summary','Paper QA readiness','PNU and importance','Argument and challenges']
    },
    evidence: {
      title:'Evidence', active:'evidence', type:'evidence',
      kicker:'Warrants, claims, and uncertainty',
      lede:'Inspect why a claim is believed, what kind of warrant supports it, and what remains weak, indirect, or underspecified.',
      search:'Search findings, warrants, topics, sensors...',
      narrative:['Evidence strength','Direct versus indirect','Design relevance','Gaps and challenge prompts']
    },
    argumentation: {
      title:'Argumentation', active:'argumentation', type:'argument',
      kicker:'Challenge structure',
      lede:'Expose disagreement as structured argument: claims, grounds, warrant, backing, qualifiers, and rebuttals.',
      search:'Search clusters, theories, papers...',
      narrative:['Toulmin map','Challenge basis','Linked papers','Alternate breadcrumb paths']
    },
    search: {
      title:'Search Results', active:'search', type:'mixed',
      kicker:'Named query plus exploratory pivots',
      lede:'Search is for users who can name what they want; the result page still provides browse pivots for exploratory users.',
      search:'Search across papers, topics, theories, mechanisms...',
      narrative:['Structured result groups','Facet rail','Answer synthesis','Browse pivots']
    }
  };

  const $ = (sel, root=document) => root.querySelector(sel);
  const esc = value => String(value == null ? '' : value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const text = (value, fallback='Unknown') => String(value == null || value === '' ? fallback : value);
  const clamp = (arr, n=36) => arr.slice(0, n);

  async function loadPayloads() {
    const loader = window.KA_DATA_ADAPTER || window.KA_PAYLOADS;
    const load = (name, fallback) => loader ? loader.loadPayload(name, fallback) : Promise.resolve(fallback);
    const entries = await Promise.all([
      load('topic_hierarchy', {topics:[], summary:{}}),
      load('topic_crosswalk', {rows:[], summary:{}}),
      load('theories', {theories:[], summary:{}}),
      load('mechanisms', {mechanisms:[], summary:{}}),
      load('pnus', {frameworks:[], cross_framework:[], summary:{}}),
      load('articles', {articles:[]}),
      load('paper_pnus', {papers:[], summary:{}}),
      load('evidence', {evidence:[], summary:{}}),
      load('argumentation', {debate_clusters:[], summary:{}})
    ]);
    return {
      topicHierarchy: entries[0], crosswalk: entries[1], theories: entries[2],
      mechanisms: entries[3], pnus: entries[4], articles: entries[5],
      paperPnus: entries[6], evidence: entries[7], argumentation: entries[8]
    };
  }

  function summarize(value, n=180) {
    const s = text(value, '').replace(/\s+/g, ' ').trim();
    return s.length > n ? s.slice(0, n - 1).trim() + '...' : s;
  }

  function evidenceChip(v) {
    const s = String(v || '').toLowerCase();
    if (s.includes('strong') || s.includes('defended') || s.includes('actually')) return 'strong';
    if (s.includes('weak') || s.includes('stub') || s.includes('ungrounded')) return 'rose';
    if (s.includes('plaus') || s.includes('moderate') || s.includes('brief')) return 'amber';
    return 'blue';
  }

  function topicItems(data) {
    return (data.topicHierarchy.topics || []).map(t => ({
      type:'topic', id:t.id, title:t.label, group:t.iv_root_label || t.iv_root || 'Topic',
      score:+(t.paper_count || 0), body:`${text(t.iv_root_label)} to ${text(t.dv_focus_label || t.outcome_label)}. ${t.paper_count || 0} linked papers.`,
      chips:[t.evidence_status || 'defended', t.dv_focus_label || t.outcome_label, t.iv_root_label],
      raw:t
    })).sort((a,b)=>b.score-a.score);
  }

  function theoryItems(data) {
    return (data.theories.theories || []).map(t => ({
      type:'theory', id:t.id, title:t.name, group:'Theory',
      score:+(t.article_count || 0), body:`${t.article_count || 0} articles, ${t.topic_count || 0} topic links, ${t.debate_cluster_count || 0} debate clusters.`,
      chips:[`${t.article_count || 0} papers`, `${t.topic_count || 0} topics`, `${t.debate_cluster_count || 0} debates`],
      raw:t
    })).sort((a,b)=>b.score-a.score);
  }

  function mechanismItems(data) {
    return (data.mechanisms.mechanisms || []).map(m => ({
      type:'mechanism', id:m.id, title:m.name, group:m.framework_name || m.framework_id || 'Mechanism',
      score:+(m.word_count || 0), body:`${text(m.framework_name || m.framework_id)}. ${text(m.temporal, 'Temporal class not set')}.`,
      chips:[m.maturity, m.temporal, `${m.word_count || 0}w`],
      raw:m
    })).sort((a,b)=>b.score-a.score);
  }

  function neuralItems(data) {
    const fromFrameworks = [];
    (data.pnus.frameworks || []).forEach(fw => (fw.mechanisms || []).forEach(m => fromFrameworks.push({...m, framework_name:fw.name, framework_id:fw.id})));
    const source = fromFrameworks.length ? fromFrameworks : (data.mechanisms.mechanisms || []);
    return source.map(m => ({
      type:'neural', id:m.id, title:m.name, group:m.framework_name || m.framework_id || 'PNU',
      score:+(m.word_count || 0), body:`${text(m.framework_name || m.framework_id)}. ${text(m.maturity)}. ${text(m.temporal, 'Temporal class not set')}.`,
      chips:[m.framework_id, m.maturity, `${m.word_count || 0}w`],
      raw:m
    })).sort((a,b)=>b.score-a.score);
  }

  function paperItems(data) {
    const source = (data.paperPnus.papers || []).length ? data.paperPnus.papers : (data.articles.articles || []);
    return source.map(p => ({
      type:'paper', id:p.paper_id, title:p.title, group:p.primary_topic || p.article_type || 'Paper',
      score:+(p.year || 0), body:summarize(p.science_summary?.core_finding || p.abstract || p.apa_citation, 210),
      chips:[p.paper_id, p.year, p.article_type || p.primary_topic],
      raw:p
    })).sort((a,b)=>(b.raw.year||0)-(a.raw.year||0));
  }

  function evidenceItems(data) {
    return (data.evidence.evidence || []).map(e => ({
      type:'evidence', id:e.id, title:e.finding || e.claim, group:e.primary_topic || e.warrant || 'Evidence',
      score:+(e.credence || 0), body:summarize(e.warrant_chain || e.abstract || e.claim, 210),
      chips:[e.warrant, e.warrant_status, e.paper_id],
      raw:e
    })).sort((a,b)=>b.score-a.score);
  }

  function argumentItems(data) {
    return (data.argumentation.debate_clusters || []).map(c => ({
      type:'argument', id:c.cluster_id, title:`Debate cluster ${c.cluster_id}`, group:'Argumentation',
      score:+(c.paper_count || 0), body:`${c.paper_count || 0} papers and ${c.theory_count || 0} theories. ${((c.theories || []).slice(0,3)).join(', ')}`,
      chips:[`${c.paper_count || 0} papers`, `${c.theory_count || 0} theories`],
      raw:c
    })).sort((a,b)=>b.score-a.score);
  }

  function allItems(data, mode) {
    if (mode === 'topics') return topicItems(data);
    if (mode === 'theories') return theoryItems(data);
    if (mode === 'mechanisms') return mechanismItems(data);
    if (mode === 'neural') return neuralItems(data);
    if (mode === 'papers') return paperItems(data);
    if (mode === 'evidence') return evidenceItems(data);
    if (mode === 'argumentation') return argumentItems(data);
    return [
      ...clamp(paperItems(data), 30),
      ...clamp(topicItems(data), 25),
      ...clamp(theoryItems(data), 25),
      ...clamp(mechanismItems(data), 25),
      ...clamp(evidenceItems(data), 25)
    ];
  }

  function buildShell(root, cfg) {
    root.innerHTML = `
      <section class="ka-dyn-hero">
        <div>
          <div class="ka-dyn-kicker">${esc(cfg.kicker)}</div>
          <h1>${esc(cfg.title)}</h1>
          <p>${esc(cfg.lede)}</p>
        </div>
        <div class="ka-dyn-query">
          <input id="kaDynSearch" type="search" placeholder="${esc(cfg.search)}">
          <select id="kaDynLens">
            <option value="browse">Browsing for something interesting</option>
            <option value="researcher">Researcher checking warrant</option>
            <option value="student">Student learning the field</option>
            <option value="practitioner">Practitioner looking for design relevance</option>
          </select>
          <label class="ka-dyn-slider"><span>Evidence</span><input id="kaDynEvidence" type="range" min="0" max="100" value="45"><b id="kaDynEvidenceValue">45</b></label>
          <label class="ka-dyn-slider"><span>Novelty</span><input id="kaDynNovelty" type="range" min="0" max="100" value="55"><b id="kaDynNoveltyValue">55</b></label>
        </div>
      </section>
      <section class="ka-dyn-metrics" id="kaDynMetrics"></section>
      <section class="ka-dyn-layout">
        <aside class="ka-dyn-panel">
          <h2>Journey Controls</h2>
          <p class="ka-dyn-small">The same page can serve a browser, a named-search user, or a theory-first user. These controls show that distinction.</p>
          <div class="ka-dyn-taxonomy" id="kaDynTaxonomy"></div>
          <div class="ka-dyn-detail-block">
            <h4>Narrative spine</h4>
            <div class="ka-dyn-list">${cfg.narrative.map(x=>`<div>${esc(x)}</div>`).join('')}</div>
          </div>
        </aside>
        <main>
          <div id="kaDynDidYouKnow"></div>
          <div class="ka-dyn-cardgrid" id="kaDynCards"></div>
        </main>
        <aside class="ka-dyn-panel ka-dyn-detail" id="kaDynDetail"></aside>
      </section>`;
  }

  function metricsFor(mode, data, items) {
    const base = {
      topics:['Topics', data.topicHierarchy.topics?.length || items.length, 'IV/DV topic lattice'],
      theories:['Theories', data.theories.theories?.length || items.length, 'article and debate linked'],
      mechanisms:['Mechanisms', data.mechanisms.mechanisms?.length || items.length, 'causal pathway profiles'],
      neural:['PNU profiles', data.pnus.summary?.total || items.length, 'framework-routed neural stories'],
      papers:['Papers', data.paperPnus.summary?.article_count || data.articles.articles?.length || items.length, 'summary + PNU destinations'],
      evidence:['Claims', data.evidence.evidence?.length || items.length, 'warrant-bearing claims'],
      argumentation:['Clusters', data.argumentation.summary?.cluster_count || items.length, 'structured disagreement'],
      search:['Indexed items', items.length, 'mixed result surface']
    }[mode];
    return [
      base,
      ['Visible now', Math.min(items.length, 36), 'filtered cards'],
      ['Payloads', 7, 'live JSON sources'],
      ['Mode', mode === 'search' ? 'Mixed' : 'Focused', 'page-specific narrative']
    ];
  }

  function renderMetrics(mode, data, items) {
    $('#kaDynMetrics').innerHTML = metricsFor(mode, data, items).map(m => `
      <div class="ka-dyn-metric"><div class="label">${esc(m[0])}</div><div class="value">${esc(m[1])}</div><div class="sub">${esc(m[2])}</div></div>
    `).join('');
  }

  function renderTaxonomy(items, selectedGroup) {
    const groups = [...new Set(items.map(i => i.group).filter(Boolean))].slice(0, 10);
    $('#kaDynTaxonomy').innerHTML = [`<button data-group="" class="${selectedGroup?'':'active'}">All lanes</button>`]
      .concat(groups.map(g => `<button data-group="${esc(g)}" class="${g===selectedGroup?'active':''}">${esc(g)}</button>`)).join('');
  }

  function itemHay(item) {
    return [item.type,item.id,item.title,item.group,item.body,(item.chips||[]).join(' ')].join(' ').toLowerCase();
  }

  function renderCards(items, selected, onSelect) {
    const cardRoot = $('#kaDynCards');
    if (!items.length) {
      cardRoot.innerHTML = '<div class="ka-dyn-empty">No matching items. Lower the evidence or novelty slider, or broaden the search.</div>';
      return;
    }
    cardRoot.innerHTML = clamp(items, 36).map((item, idx) => `
      <article class="ka-dyn-card ${selected && selected.id === item.id && selected.type === item.type ? 'active' : ''}" data-idx="${idx}">
        <div class="type">${esc(item.type)} · ${esc(item.group)}</div>
        <h3>${esc(item.title)}</h3>
        <p>${esc(item.body)}</p>
        <div class="ka-dyn-chiprow">${(item.chips||[]).filter(Boolean).slice(0,3).map(c=>`<span class="ka-dyn-chip ${evidenceChip(c)}">${esc(c)}</span>`).join('')}</div>
        <div class="meta">${esc(item.id)} · score ${Math.round((item.score || 0) * 100) / 100}</div>
      </article>`).join('');
    [...cardRoot.querySelectorAll('.ka-dyn-card')].forEach(card => card.addEventListener('click', () => onSelect(items[+card.dataset.idx])));
  }

  function didYouKnow(items, lens) {
    const picked = items.find(i => i.type === 'evidence') || items[0];
    if (!picked) return '';
    const question = lens === 'practitioner'
      ? 'What would change in a design decision if this claim is true?'
      : lens === 'student'
        ? 'What is the simplest route into this idea?'
        : lens === 'researcher'
          ? 'What would count as a serious challenge to this warrant?'
          : 'Why might this be more interesting than the obvious search result?';
    return `<div class="ka-dyn-dyk"><b>Did you know?</b> ${esc(picked.title)} can be entered as a ${esc(picked.type)} rather than as a keyword search. <br>${esc(question)}</div>`;
  }

  function renderDetail(item, cfg) {
    if (!item) {
      $('#kaDynDetail').innerHTML = `<div class="ka-dyn-detail-title">${esc(cfg.title)}</div><p class="ka-dyn-small">Select a card to inspect warrant, linked papers, and next navigation moves.</p>`;
      return;
    }
    const r = item.raw || {};
    const papers = r.paper_preview || r.representative_papers || (r.papers || []).map(p=>({paper_id:p,title:p})) || [];
    const theories = r.theories || r.shared_theories || [];
    const links = [
      ['Search this', `ka_search.html?q=${encodeURIComponent(item.title)}`],
      ['Open articles', 'ka_articles.html'],
      ['Open topics', 'ka_topics.html'],
      ['Open argumentation', 'ka_argumentation.html']
    ];
    $('#kaDynDetail').innerHTML = `
      <div class="ka-dyn-detail-title">${esc(item.title)}</div>
      <div class="ka-dyn-chiprow">${(item.chips||[]).filter(Boolean).slice(0,5).map(c=>`<span class="ka-dyn-chip ${evidenceChip(c)}">${esc(c)}</span>`).join('')}</div>
      <div class="ka-dyn-detail-block"><h4>Why this page should say something</h4><p class="ka-dyn-small">${esc(item.body)}</p></div>
      <div class="ka-dyn-detail-block"><h4>Warrant / place in Atlas</h4><p class="ka-dyn-small">${esc(warrantText(item))}</p></div>
      <div class="ka-dyn-detail-block"><h4>Representative papers</h4><div class="ka-dyn-list">${papers.slice(0,5).map(p=>`<a href="ka_article.html?paper=${esc(p.paper_id || p)}">${esc(p.title || p.paper_id || p)}</a>`).join('') || '<div>No paper list in payload for this item yet.</div>'}</div></div>
      <div class="ka-dyn-detail-block"><h4>Related theories / lenses</h4><div class="ka-dyn-chiprow">${theories.slice(0,6).map(t=>`<span class="ka-dyn-chip blue">${esc(t)}</span>`).join('') || '<span class="ka-dyn-chip">Not linked yet</span>'}</div></div>
      <div class="ka-dyn-detail-block"><h4>Next moves</h4><div class="ka-dyn-list">${links.map(l=>`<a href="${l[1]}">${l[0]}</a>`).join('')}</div></div>
      <p class="ka-dyn-note">Breadcrumb can differ by journey. A search user, a topic browser, and a theory-first user may arrive at the same paper or mechanism page.</p>`;
  }

  function warrantText(item) {
    if (item.type === 'topic') return 'Topic warrant comes from IV/DV membership, linked paper count, theories, sensors, and defended versus working corpus status.';
    if (item.type === 'theory') return 'Theory warrant should explain why this is a framework, named theory, or lower-level explanatory claim, and show its place in the lattice.';
    if (item.type === 'mechanism') return 'Mechanism warrant asks whether the causal chain is directly observed, bridged through adjacent evidence, or only plausible.';
    if (item.type === 'neural') return 'PNU warrant separates a plausible neural explanation from direct neural evidence and marks profile readiness.';
    if (item.type === 'paper') return 'Paper warrant should expose summary, interpretation, PNU, objection paths, and papers that challenge or presuppose it.';
    if (item.type === 'evidence') return 'Evidence warrant is the bridge from extracted claim to belief: extraction type, article family, discount, and open qualifier.';
    if (item.type === 'argument') return 'Argument warrant is structural: what claim is supported, what can attack it, and what backing is missing.';
    return 'Mixed search results should disclose result type, evidence status, and the best next browsing pivot.';
  }

  function update(state) {
    const q = $('#kaDynSearch').value.trim().toLowerCase();
    const evidence = +$('#kaDynEvidence').value;
    const novelty = +$('#kaDynNovelty').value;
    $('#kaDynEvidenceValue').textContent = evidence;
    $('#kaDynNoveltyValue').textContent = novelty;
    let filtered = state.items.filter(i => !q || itemHay(i).includes(q));
    if (state.group) filtered = filtered.filter(i => i.group === state.group);
    if (evidence > 70) filtered = filtered.filter(i => (i.score || 0) >= 1 || evidenceChip((i.chips||[]).join(' ')) === 'strong');
    if (novelty > 70) filtered = filtered.slice().reverse();
    $('#kaDynDidYouKnow').innerHTML = didYouKnow(filtered, $('#kaDynLens').value);
    renderMetrics(state.mode, state.data, filtered);
    const selectItem = item => {
      state.selected = item;
      renderCards(filtered, state.selected, selectItem);
      renderDetail(item, state.cfg);
    };
    renderCards(filtered, state.selected, selectItem);
    renderDetail(state.selected && filtered.includes(state.selected) ? state.selected : filtered[0], state.cfg);
  }

  async function init() {
    const root = $('#kaDynamicRoot');
    if (!root) return;
    const mode = document.body.dataset.kaDynamicPage || 'topics';
    const cfg = CONFIG[mode] || CONFIG.topics;
    const data = await loadPayloads();
    const state = {mode, cfg, data, items: allItems(data, mode), selected:null, group:''};
    buildShell(root, cfg);
    renderTaxonomy(state.items, state.group);
    $('#kaDynTaxonomy').addEventListener('click', e => {
      const b = e.target.closest('button[data-group]');
      if (!b) return;
      state.group = b.dataset.group;
      renderTaxonomy(state.items, state.group);
      update(state);
    });
    ['kaDynSearch','kaDynEvidence','kaDynNovelty','kaDynLens'].forEach(id => $('#' + id).addEventListener('input', () => update(state)));
    update(state);
  }

  document.addEventListener('DOMContentLoaded', init);
})();
