(function() {
  const MODE_LABELS = {
    student_explorer: 'STUDENT EXPLORER',
    researcher: 'RESEARCHER',
    contributor: 'CONTRIBUTOR',
    instructor: 'INSTRUCTOR',
    practitioner: 'PRACTITIONER',
    theory_mechanism_explorer: 'THEORY + MECHANISMS'
  };

  const MODE_NOTES = {
    student_explorer: 'Student mode foregrounds literature exploration and tractable entry points.',
    researcher: 'Researcher mode foregrounds evidence, gaps, and article discovery.',
    contributor: 'Contributor mode foregrounds intake, review, and progress-tracking workflows.',
    instructor: 'Instructor mode foregrounds course coordination, setup, and assignment oversight.',
    practitioner: 'Practitioner mode foregrounds readable evidence and applied topics.',
    theory_mechanism_explorer: 'Theory + mechanisms mode foregrounds theory guides, mechanisms, and explanatory questions.'
  };

  const NAV_ORDERS = {
    student_explorer: ['nav-shell-explore', 'nav-shell-evidence', 'nav-shell-gaps', 'nav-shell-articles', 'nav-shell-contribute', 'nav-shell-course'],
    researcher: ['nav-shell-evidence', 'nav-shell-gaps', 'nav-shell-articles', 'nav-shell-explore', 'nav-shell-contribute', 'nav-shell-course'],
    contributor: ['nav-shell-contribute', 'nav-shell-articles', 'nav-shell-evidence', 'nav-shell-explore', 'nav-shell-gaps', 'nav-shell-course'],
    instructor: ['nav-shell-course', 'nav-shell-contribute', 'nav-shell-explore', 'nav-shell-evidence', 'nav-shell-gaps', 'nav-shell-articles'],
    practitioner: ['nav-shell-explore', 'nav-shell-evidence', 'nav-shell-articles', 'nav-shell-gaps', 'nav-shell-contribute', 'nav-shell-course'],
    theory_mechanism_explorer: ['nav-shell-explore', 'nav-shell-evidence', 'nav-shell-gaps', 'nav-shell-articles', 'nav-shell-course', 'nav-shell-contribute']
  };

  function moveItem(navContainer, el) {
    if (!navContainer || !el) return;
    const node = el.tagName === 'LI' ? el : el.parentElement && el.parentElement.tagName === 'LI' ? el.parentElement : el;
    navContainer.appendChild(node);
  }

  function applyMode(mode, opts) {
    const navContainer = document.querySelector(opts.navContainerSelector);
    const order = NAV_ORDERS[mode] || NAV_ORDERS.student_explorer;
    order.forEach(function(id) {
      const link = document.getElementById(id);
      if (link) moveItem(navContainer, link);
    });

    if (opts.modePillId) {
      const pill = document.getElementById(opts.modePillId);
      if (pill) pill.textContent = MODE_LABELS[mode] || MODE_LABELS.student_explorer;
    }

    if (opts.modeNoteId) {
      const note = document.getElementById(opts.modeNoteId);
      if (note) note.textContent = MODE_NOTES[mode] || MODE_NOTES.student_explorer;
    }

    if (typeof opts.onModeApplied === 'function') {
      opts.onModeApplied(mode);
    }
  }

  function initShell(opts) {
    const options = opts || {};
    const defaultMode = options.defaultMode || 'student_explorer';
    window.KA_MODE_SWITCH.initModeControls({
      selectId: options.modeSelectId,
      pillContainerId: options.pillContainerId,
      defaultMode: defaultMode,
      onApply: function(mode) {
        applyMode(mode, options);
      }
    });
  }

  window.KA_SHELL = {
    initShell: initShell,
    MODE_LABELS: MODE_LABELS,
    MODE_NOTES: MODE_NOTES,
    NAV_ORDERS: NAV_ORDERS
  };
})();
