(function() {
  const PAYLOAD_PATHS = {
    topics: 'data/ka_payloads/topics.json',
    topic_hierarchy: 'data/ka_payloads/topic_hierarchy.json',
    topic_ontology: 'data/ka_payloads/topic_ontology.json',
    topic_memberships: 'data/ka_payloads/topic_memberships.json',
    research_fronts: 'data/ka_payloads/research_fronts.json',
    gaps: 'data/ka_payloads/gaps.json',
    evidence: 'data/ka_payloads/evidence.json',
    articles: 'data/ka_payloads/articles.json',
    dashboard: 'data/ka_payloads/dashboard.json',
    json_status: 'data/ka_payloads/json_status.json',
    argumentation: 'data/ka_payloads/argumentation.json',
    annotations: 'data/ka_payloads/annotations.json',
    interpretation: 'data/ka_payloads/interpretation.json',
    layers: 'data/ka_payloads/layers.json'
  };

  async function loadJson(path) {
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) {
      throw new Error('Failed to load ' + path + ' (' + response.status + ')');
    }
    return response.json();
  }

  async function loadWithFallback(path, fallback) {
    try {
      return await loadJson(path);
    } catch (err) {
      return fallback;
    }
  }

  async function loadFirstAvailable(paths, fallback) {
    const candidates = Array.isArray(paths) ? paths : [paths];
    for (const path of candidates) {
      try {
        const payload = await loadJson(path);
        if (payload && typeof payload === 'object') {
          payload.__loaded_from = path;
        }
        return payload;
      } catch (err) {
        // Try the next candidate.
      }
    }
    return fallback;
  }

  async function loadPayload(name, fallback) {
    const path = PAYLOAD_PATHS[name];
    if (!path) {
      throw new Error('Unknown Knowledge Atlas payload: ' + name);
    }
    return loadWithFallback(path, fallback || {});
  }

  window.KA_DATA_ADAPTER = {
    loadJson,
    loadWithFallback,
    loadFirstAvailable,
    loadPayload,
    PATHS: PAYLOAD_PATHS
  };

  window.KA_PAYLOADS = {
    loadJson,
    loadWithFallback,
    loadFirstAvailable,
    loadPayload,
    PATHS: PAYLOAD_PATHS
  };
})();
