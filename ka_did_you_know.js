(function () {
  const DYK_URL = 'data/ka_payloads/did_you_know.json';

  function escapeHtml(value) {
    return String(value || '').replace(/[&<>"']/g, ch => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[ch]));
  }

  async function loadDidYouKnowCards() {
    const response = await fetch(DYK_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error(`DYK payload fetch failed: ${response.status}`);
    const payload = await response.json();
    return Array.isArray(payload.cards) ? payload.cards : [];
  }

  function cardHtml(card) {
    const topic = (card.topic_labels && card.topic_labels[0]) || card.primary_topic || 'Knowledge Atlas';
    const strength = card.evidence_strength || 'source-backed';
    const href = (card.links && (card.links.articles || card.links.topics)) || 'ka_articles.html';
    return `
      <article class="dyk-card" data-dyk-id="${escapeHtml(card.id)}">
        <div class="kicker">${escapeHtml(strength.toUpperCase())} · ${escapeHtml(topic)}</div>
        <h3>${escapeHtml(card.title)}</h3>
        <p>${escapeHtml(card.body || card.hook)}</p>
        <a class="dyk-more" href="${escapeHtml(href)}">Trace the evidence →</a>
      </article>
    `;
  }

  function applyCardsToGrid(grid, cards, limit) {
    if (!grid || !cards.length) return;
    grid.innerHTML = cards.slice(0, limit).map(cardHtml).join('');
  }

  async function hydrateHomeGrid(selector, limit) {
    const grid = document.querySelector(selector);
    if (!grid) return;
    try {
      const cards = await loadDidYouKnowCards();
      applyCardsToGrid(grid, cards, limit);
    } catch (err) {
      console.warn(err);
    }
  }

  async function hydrateStudentCard() {
    const title = document.getElementById('dykTitle');
    const body = document.getElementById('dykBody');
    const cta = document.getElementById('dykCta');
    if (!title || !body) return;
    try {
      const cards = await loadDidYouKnowCards();
      if (!cards.length) return;
      const index = Math.floor(Math.random() * Math.min(cards.length, 20));
      const card = cards[index];
      title.textContent = card.title || title.textContent;
      body.textContent = card.body || card.hook || body.textContent;
      if (cta && card.links) cta.href = card.links.articles || card.links.topics || cta.href;
    } catch (err) {
      console.warn(err);
    }
  }

  window.KADidYouKnow = {
    loadDidYouKnowCards,
    hydrateHomeGrid,
    hydrateStudentCard,
  };
})();
