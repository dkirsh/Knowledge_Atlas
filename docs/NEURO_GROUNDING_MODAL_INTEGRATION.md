# Neuroscientific Grounding Modal — Integration Guide

**Last Updated**: April 1, 2026
**Component**: `ka_neuro_grounding_modal.js`, `ka_neuro_grounding_modal.css`
**Demo Page**: `ka_neuro_grounding_demo.html`

---

## Overview

The Neuroscientific Grounding Modal is a reusable, self-contained component that displays mechanism chains, confidence levels, and grounding gaps for Knowledge Atlas claims. It renders as an overlay modal with smooth animations and full keyboard accessibility.

The component includes:
- **40 mechanisms** across 10 Tier 1 frameworks (CB, DP, DT, EC, IC, MS, MSI, NM, PP, SN)
- **Two modal variants**:
  - **Article Modal**: Deep dive showing all grounded claims with mechanism chains, CCI confidence bars, and identified gaps
  - **Topic Modal**: Lightweight view with aggregate grounding statistics and top 3 mechanisms

---

## Quick Start

### 1. Include on Your Page

Add these lines to any Knowledge Atlas page `<head>`:

```html
<link rel="stylesheet" href="ka_neuro_grounding_modal.css">
```

And before closing `</body>`:

```html
<script src="ka_neuro_grounding_modal.js"></script>
```

The modal will auto-initialize on page load.

### 2. Trigger from Article Cards

To add a trigger button to article cards, include:

```html
<button class="article-btn" onclick="window.NeuroGroundingModal.openForArticle('article-001')">
  🧠 Neuro Grounding
</button>
```

Replace `'article-001'` with your article ID. The modal will display all mechanistically grounded claims from that article.

### 3. Trigger from Topic Cards

For topic cards:

```html
<button class="topic-btn" onclick="window.NeuroGroundingModal.openForTopic('topic-circadian')">
  Explore Mechanisms
</button>
```

Replace `'topic-circadian'` with your topic ID.

---

## Data Structure

### Article Format

```javascript
{
  id: 'article-001',
  title: 'Light Exposure and Sleep: Neuroarchitecture Evidence',
  authors: 'Stevens et al.',
  year: 2024,
  claims: [
    {
      id: 'claim-001',
      text: 'Exposure to >10 melanopic lux suppresses melatonin',
      mechanismIds: ['CB-CIRCADIAN-ENTRAINMENT-001'],
      groundingGaps: ['Role of individual circadian phase sensitivity']
    }
  ]
}
```

### Topic Format

```javascript
{
  id: 'topic-circadian',
  name: 'Circadian & Sleep Alignment',
  frameworkId: 'CB',
  groundingStats: { total: 12, grounded: 8 },
  topMechanisms: ['CB-CIRCADIAN-ENTRAINMENT-001', 'CB-SLEEP-QUALITY-002']
}
```

---

## Adding Your Own Data

To add custom articles or topics, edit `ka_neuro_grounding_modal.js` and add entries to:

1. **For articles**: `this.articles` object (line ~200)
2. **For topics**: `this.topics` object (line ~280)

Follow the data structure examples above.

---

## Mechanism Properties

Each mechanism in the inventory includes:

| Property | Type | Example |
|----------|------|---------|
| `id` | string | `'PP-GIST-001'` |
| `framework` | string | `'PP'` (Predictive Processing) |
| `frameworkLabel` | string | `'Predictive Processing'` |
| `name` | string | `'Rapid Gist-Driven Affective Framing'` |
| `chain` | string | `'Low-freq statistics → V1/V2 → PFC → 130ms affective frame'` |
| `maturity` | string | `'How-Actually'` or `'How-Plausibly'` |
| `cci` | float | `0.75` (0–1 confidence scale) |
| `confidence` | float | `0.85` (empirical confidence) |
| `bridgeType` | string | `'Mechanism'`, `'Empirical Association'`, `'Functional'`, etc. |
| `description` | string | Plain English explanation |
| `evidence` | array | `['Bar (2007) Neuron', '...']` |

---

## Confidence Levels

The modal displays CCI confidence using both visual bars and text labels:

| CCI Range | Label | Color | Meaning |
|-----------|-------|-------|---------|
| 0.75–1.0 | **STRONG** | Green (#2A7868) | Well-established mechanism with strong empirical support |
| 0.60–0.74 | **WELL-SUPPORTED** | Amber (#E8872A) | Solid evidence, minor gaps or caveats |
| 0.40–0.59 | **PLAUSIBLE** | Tan (#D4A574) | Reasonable mechanisms, requires further validation |
| 0.0–0.39 | **SPECULATIVE** | Gray (#B8A89A) | Preliminary evidence or theoretical extrapolation |

---

## Bridge Types

The modal displays warrant types as colored pills:

| Type | Color | Meaning |
|------|-------|---------|
| **Mechanism** | Navy (#1C3D3A) | Direct causal pathway with known neural substrate |
| **Empirical Association** | Amber (#E8872A) | Correlated outcomes without full mechanistic explanation |
| **Functional** | Muted (#6A5E50) | System-level functional consequence |
| **Constitutive** | Navy (#1C3D3A) | Definitional or necessary component |
| **Analogical** | Tan (#D4A574) | Inferred by analogy with similar systems |

---

## Frameworks (Tier 1)

The 10 frameworks represented in the mechanism inventory:

| Code | Framework | Example Mechanisms |
|------|-----------|-------------------|
| **PP** | Predictive Processing | Gist-driven framing, prediction error, Goldilocks complexity |
| **SN** | Salience Network | Threat detection, DMN/CEN switching, stability |
| **DP** | Dopaminergic Prediction | Scene gist novelty, reward prediction error, exploration |
| **DT** | Default Mode Theory | Self-referential thought, sense of self in space |
| **NM** | Neuromodulatory Systems | Cholinergic attention, noradrenaline uncertainty |
| **IC** | Interoceptive/Autonomic Control | Allostatic load, affective valence, interoceptive precision |
| **CB** | Circadian/Biological Rhythms | ipRGC-SCN entrainment, sleep quality, allostatic load |
| **MS** | Memory & Spatial Cognition | Theta phase-locking, ripple consolidation, place cell remapping |
| **EC** | Embodied Cognition | Spatial externalism, affordance perception, social scaffolding |
| **MSI** | Multisensory Integration | Audiovisual binding, spatial recalibration, olfactory integration |

---

## Design Integration

### Styling with KA Design System

The modal uses the Knowledge Atlas design system colors and typography:

```css
--navy: #1C3D3A;      /* headings, primary UI */
--amber: #E8872A;     /* accents, highlights */
--cream: #F7F4EF;     /* backgrounds */
--green: #2A7868;     /* secondary, success states */
--text: #2D2010;      /* body text */
--muted: #6A5E50;     /* secondary text */
```

Fonts:
- **Headings**: Georgia serif
- **Body/UI**: System sans-serif (Arial, etc.)
- **Code/Chains**: Monospace (`SF Mono`, `Fira Code`, Consolas)

### Adding Neuro Grounding Trigger to Existing Cards

**Article cards** (e.g., in `ka_articles.html`):

```html
<div class="article-card">
  <!-- existing content -->
  <div style="display: flex; gap: 10px; margin-top: 12px;">
    <a href="article-detail.html" class="article-link">Read Full Article</a>
    <button class="article-neuro-btn" onclick="window.NeuroGroundingModal.openForArticle('article-001')">
      🧠 Mechanisms
    </button>
  </div>
</div>
```

Add minimal styling for the button:

```css
.article-neuro-btn {
  background: rgba(42, 120, 104, 0.1);
  color: #2A7868;
  border: 1px solid #2A7868;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.article-neuro-btn:hover {
  background: #2A7868;
  color: #fff;
}
```

---

## Keyboard & Accessibility

The modal is fully keyboard accessible:

| Key | Action |
|-----|--------|
| **Escape** | Close modal |
| **Tab** | Navigate between interactive elements (footer links, close button) |
| **Enter** | Activate buttons |

All color combinations meet WCAG 2.1 AA contrast ratios. The component respects `prefers-reduced-motion` preferences.

---

## API Reference

### Methods

```javascript
// Open article modal
window.NeuroGroundingModal.openForArticle(articleId, articleData)
// articleData optional; pulls from internal inventory if not provided

// Open topic modal
window.NeuroGroundingModal.openForTopic(topicId)

// Close modal
window.NeuroGroundingModal.close()
```

### Properties

```javascript
// Access the modal instance
const modal = window.NeuroGroundingModal;

// Read current state
modal.isOpen          // boolean
modal.currentMode     // 'article' or 'topic'
modal.currentData     // current article/topic object

// Access data
modal.mechanisms      // all mechanisms (ID → object map)
modal.articles        // all articles (ID → object map)
modal.topics          // all topics (ID → object map)
```

---

## Performance Notes

- **Lightweight**: Total JS + CSS ~35KB uncompressed, ~10KB gzipped
- **No dependencies**: Pure vanilla JavaScript, no libraries
- **Fast rendering**: All mechanism data is hardcoded; no API calls
- **Cached DOM**: Modal container created once on init, content replaced on open

---

## Demo & Testing

Visit `ka_neuro_grounding_demo.html` to:
- See both article and topic modal variants in action
- Test keyboard navigation and mobile responsiveness
- Review the complete mechanism inventory
- Understand integration patterns

---

## Future Enhancements

Potential extensions (not implemented in v1):

1. **Dynamic data loading**: Fetch article/topic data from API instead of hardcoding
2. **Search mechanism chains**: Filter by framework, maturity, or CCI range
3. **Citation export**: Copy mechanism chain citations in BibTeX/APA format
4. **Panel annotations**: Add expert reviewer notes and dissent flags
5. **Mechanism pathway visualization**: Interactive diagram showing chain relationships
6. **Mobile swipe gestures**: Swipe to close on touch devices
7. **Anchor sharing**: Deep links to specific claims/mechanisms

---

## Support & Issues

For bugs or integration questions, reference:
- Design spec: See `ka_neuro_perspective.html` for context
- Mechanism inventory: `Article_Eater_PostQuinean_v1_recovery/skills/neuroscience-expert/references/mechanism_inventory.md`
- KA design system: Check `ka_home.html` or `ka_neuro_perspective.html` for color/typography standards
