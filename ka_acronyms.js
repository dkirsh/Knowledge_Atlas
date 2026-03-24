/**
 * ka_acronyms.js
 *
 * Standalone utility to auto-expand acronyms across Knowledge Atlas HTML pages.
 * Walks the DOM on page load and wraps first occurrences of acronyms with tooltips.
 *
 * Usage: Include <script src="ka_acronyms.js"></script> before </body> tag
 * Opt-out: Add <meta name="ka-no-acronyms" content="true"> to page head
 *
 * Last updated: 2026-03-23
 */

const KA_GLOSSARY = {
  'KA': 'Knowledge Atlas',
  'LKM': 'Large Knowledge Model',
  'CNFA': 'Cognitive Neuroscience of Functional Architecture',
  'EDA': 'Electrodermal Activity',
  'HR': 'Heart Rate',
  'HRV': 'Heart Rate Variability',
  'PVT': 'Psychomotor Vigilance Task',
  'EEG': 'Electroencephalography',
  'fNIRS': 'Functional Near-Infrared Spectroscopy',
  'fMRI': 'Functional Magnetic Resonance Imaging',
  'MRI': 'Magnetic Resonance Imaging',
  'WM': 'Working Memory',
  'VOI': 'Value of Information',
  'APA': 'Annotated Paper Abstract',
  'OSF': 'Open Science Framework',
  'RCT': 'Randomized Controlled Trial',
  'DOI': 'Digital Object Identifier',
  'ORCID': 'Open Researcher and Contributor Identifier',
  'IRB': 'Institutional Review Board',
  'SQL': 'Structured Query Language',
  'API': 'Application Programming Interface',
  'DB': 'Database',
  'JWT': 'JSON Web Token',
  'JSON': 'JavaScript Object Notation',
  'HTML': 'HyperText Markup Language',
  'CSS': 'Cascading Style Sheets',
  'UI': 'User Interface',
  'UX': 'User Experience',
  'VR': 'Virtual Reality',
  'NLP': 'Natural Language Processing',
  'ML': 'Machine Learning',
  'AI': 'Artificial Intelligence',
  'PANAS': 'Positive and Negative Affect Schedule',
  'SAM': 'Self-Assessment Manikin',
  'FACS': 'Facial Action Coding System',
  'NASA-TLX': 'NASA Task Load Index',
  'EMG': 'Electromyography',
  'ECG': 'Electrocardiography',
  'GSR': 'Galvanic Skin Response',
  'BVP': 'Blood Volume Pulse',
  'SpO2': 'Peripheral Oxygen Saturation',
  'CI': 'Confidence Interval',
  'SD': 'Standard Deviation',
  'RT': 'Response Time',
  'ipRGC': 'intrinsically Photosensitive Retinal Ganglion Cell',
  'UCSD': 'University of California San Diego',
  'UCLA': 'University of California Los Angeles',
  'NREL': 'National Renewable Energy Laboratory',
  'T1': 'Track 1',
  'T2': 'Track 2',
  'QA': 'Quality Assurance',
  'P0': 'Priority 0 (Critical)',
  'P1': 'Priority 1 (High)',
  'P2': 'Priority 2 (Medium)',
  'WCAG': 'Web Content Accessibility Guidelines',
  'CTA': 'Call to Action',
  'BN': 'Bayesian Network',
  'PI': 'Principal Investigator',
  'PubMed': 'Public Medicine database'
};

/**
 * Inject CSS for acronym expansions
 */
function injectAcronymCSS() {
  const style = document.createElement('style');
  style.textContent = `
    .ka-acr-expand {
      font-size: 0.76em;
      color: #8A7A68;
      font-style: normal;
      margin-left: 2px;
    }

    .ka-acr-expand::before {
      content: '[';
    }

    .ka-acr-expand::after {
      content: ']';
    }
  `;
  document.head.appendChild(style);
}

/**
 * Check if acronym expansion is disabled for this page
 */
function isExpansionDisabled() {
  const meta = document.querySelector('meta[name="ka-no-acronyms"]');
  return meta && meta.getAttribute('content') === 'true';
}

/**
 * Walk a node and its descendants, expanding acronyms in text nodes
 */
function expandAcronymsInNode(node, seen) {
  // Skip certain elements where we don't expand
  const skipTags = ['SCRIPT', 'STYLE', 'CODE', 'PRE', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6'];
  const skipIds = new Set(['nav', 'navigation', 'header'];

  if (node.nodeType === Node.ELEMENT_NODE) {
    // Skip if element matches exclusion criteria
    if (skipTags.includes(node.tagName)) {
      return;
    }

    if (node.id && skipIds.has(node.id.toLowerCase())) {
      return;
    }

    // Skip if already processed
    if (node.hasAttribute('data-ka-processed')) {
      return;
    }

    // Process child nodes
    const children = Array.from(node.childNodes);
    for (const child of children) {
      expandAcronymsInNode(child, seen);
    }
  } else if (node.nodeType === Node.TEXT_NODE) {
    const text = node.textContent;

    // Build regex to match any acronym in glossary (word boundary on left, optional punctuation on right)
    const acronyms = Object.keys(KA_GLOSSARY).sort((a, b) => b.length - a.length);

    let hasMatch = false;
    let fragment = document.createDocumentFragment();
    let lastIndex = 0;

    for (const acronym of acronyms) {
      // Create word-boundary regex: match acronym as whole word
      const regex = new RegExp(`\\b${acronym}\\b`, 'g');
      let match;

      while ((match = regex.exec(text)) !== null) {
        // Only expand if this is the first occurrence we've seen globally
        if (!seen.has(acronym)) {
          hasMatch = true;

          // Add text before match
          if (match.index > lastIndex) {
            fragment.appendChild(
              document.createTextNode(text.substring(lastIndex, match.index))
            );
          }

          // Add acronym + expansion span
          const acronymSpan = document.createElement('span');
          acronymSpan.classList.add('ka-acr-expanded');
          acronymSpan.textContent = acronym;
          fragment.appendChild(acronymSpan);

          const expansionSpan = document.createElement('span');
          expansionSpan.classList.add('ka-acr-expand');
          expansionSpan.textContent = KA_GLOSSARY[acronym];
          fragment.appendChild(expansionSpan);

          // Mark as seen
          seen.add(acronym);
          lastIndex = match.index + acronym.length;

          // Reset regex for next acronym scan
          regex.lastIndex = 0;
          break;
        }
      }
    }

    // If we made any substitutions, replace the node
    if (hasMatch) {
      if (lastIndex < text.length) {
        fragment.appendChild(document.createTextNode(text.substring(lastIndex)));
      }
      node.parentNode.replaceChild(fragment, node);
    }
  }
}

/**
 * Main expansion function
 */
function expandAcronyms() {
  // Check if expansion is disabled
  if (isExpansionDisabled()) {
    return;
  }

  // Inject CSS
  injectAcronymCSS();

  // Track which acronyms have been seen
  const seen = new Set();

  // Start walking from body
  if (document.body) {
    expandAcronymsInNode(document.body, seen);
  }

  // Mark as processed
  document.documentElement.setAttribute('data-ka-processed', 'true');
}

/**
 * Run on DOM ready
 */
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', expandAcronyms);
} else {
  expandAcronyms();
}
