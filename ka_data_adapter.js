(function() {
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

  window.KA_PAYLOADS = {
    loadJson,
    loadWithFallback
  };
})();
