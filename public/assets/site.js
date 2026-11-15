// Bold Shift Advisory redesign: tiny progressive enhancements (no framework).
(() => {
  // Mobile menu
  const btn = document.querySelector('.menu-btn');
  const nav = document.getElementById('nav');
  if (btn && nav) {
    const set = (open) => {
      btn.setAttribute('aria-expanded', String(open));
      btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      nav.classList.toggle('open', open);
    };
    btn.addEventListener('click', () => set(btn.getAttribute('aria-expanded') !== 'true'));
    document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape') set(false); });
    nav.addEventListener('click', (ev) => { if (ev.target.closest('a')) set(false); });
    matchMedia('(min-width: 961px)').addEventListener('change', () => set(false));
  }

  // Tabs (WAI-ARIA pattern, arrow keys + Home/End)
  document.querySelectorAll('[role=tablist]').forEach((list) => {
    const tabs = [...list.querySelectorAll('[role=tab]')];
    const select = (tab, focus) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
      });
      if (focus) tab.focus();
    };
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => select(t));
      t.addEventListener('keydown', (ev) => {
        const k = ev.key;
        let n = null;
        if (k === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
        if (k === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (k === 'Home') n = tabs[0];
        if (k === 'End') n = tabs[tabs.length - 1];
        if (n) { ev.preventDefault(); select(n, true); }
      });
    });
  });

  // Reveal on scroll
  const els = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    els.forEach((el) => io.observe(el));
  } else {
    els.forEach((el) => el.classList.add('in'));
  }

  // Contact form -> compose an email (static site, no backend)
  const form = document.getElementById('enquiry');
  if (form) {
    form.addEventListener('submit', (ev) => {
      ev.preventDefault();
      const d = new FormData(form);
      const subject = `${d.get('topic')} - ${d.get('name')}`;
      const lines = [d.get('message'), '', `Name: ${d.get('name')}`, `Email: ${d.get('email')}`];
      if (d.get('org')) lines.push(`Organization: ${d.get('org')}`);
      const to = form.getAttribute('action').replace('mailto:', '');
      location.href = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join('\n'))}`;
    });
  }
})();
