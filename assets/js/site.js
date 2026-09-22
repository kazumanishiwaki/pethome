(() => {
  'use strict';
  const engine = window.PethomeCheck;
  const node = (tag, text, cls) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; };
  const safeUrl = value => { try { const u = new URL(value); return u.protocol === 'https:' ? u.href : null; } catch { return null; } };
  const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const scrollTo = target => target?.scrollIntoView({behavior:reducedMotion() ? 'auto' : 'smooth', block:'start'});
  let products = [], filter = 'all';
  const grid = document.querySelector('#product-grid');
  const count = document.querySelector('#product-count');
  const filterButtons = [...document.querySelectorAll('[data-filter]')];
  function renderProducts() {
    if (!grid) return;
    const rows = products.filter(p => filter === 'all' || p.category === filter);
    const cards = rows.map(p => {
      const card = node('article', undefined, 'product-card');
      card.append(node('span', p.type, 'product-type'), node('h3', `${p.maker} / ${p.name}`));
      const dl = node('dl');
      [['この部屋で見る理由',p.why || p.summary],['設置時の確認',p.install]].forEach(([title,text]) => dl.append(node('dt',title),node('dd',text)));
      card.append(dl);
      const href = safeUrl(p.url);
      if (href) { const link = node('a','公式確認先 ↗'); link.href = href; link.target = '_blank'; link.rel = 'noopener noreferrer'; card.append(link); }
      card.append(node('p', `確認日: ${p.checked_at}\n${p.relation}`, 'product-note'));
      return card;
    });
    grid.replaceChildren(...(cards.length ? cards : [node('p','この条件の参考商品はまだ掲載していません。')]));
    if (count) count.textContent = `参考候補 ${rows.length}件`;
  }
  filterButtons.forEach(button => button.addEventListener('click', () => {
    filter = button.dataset.filter || 'all';
    filterButtons.forEach(b => { const active = b === button; b.classList.toggle('is-active', active); b.setAttribute('aria-pressed', String(active)); });
    renderProducts();
  }));
  if (grid) fetch('data/products.json').then(r => { if (!r.ok) throw new Error('Could not load products'); return r.json(); }).then(data => {
    if (!Array.isArray(data)) throw new TypeError('Invalid product data');
    products = data.filter(p => p && typeof p.name === 'string' && typeof p.category === 'string'); renderProducts();
  }).catch(() => { grid.replaceChildren(node('p','参考商品を読み込めませんでした。ページを再読み込みしてください。')); });

  const form = document.querySelector('#self-check'), panel = document.querySelector('#check-result');
  const submit = document.querySelector('#check-submit'), error = document.querySelector('#check-error');
  let config = null, currentResult = null;
  const answers = () => Object.fromEntries(new FormData(form));
  function clearResult() { currentResult = null; if (panel) panel.hidden = true; }
  function updateProgress() {
    const answered = [...form.querySelectorAll('select')].filter(s => s.value).length;
    document.querySelector('#check-progress').textContent = `${answered} / 4`;
    document.querySelector('#check-help').textContent = answered === 4 ? '4つ選択しました。入口を表示できます。' : '4つすべて選ぶと、入口が表示されます。';
    clearResult();
  }
  function applyPrefill(params) {
    if (!config || !form) return;
    config.questions.forEach(q => { const value = params.get(q.key); if (value && Object.hasOwn(q.options,value)) form.elements.namedItem(q.key).value = value; });
    updateProgress();
  }
  function readPrefill() {
    const search = new URLSearchParams(window.location.search);
    const fragment = window.location.hash;
    const at = fragment.indexOf('?');
    const section = fragment.slice(1, at < 0 ? undefined : at);
    if (section === 'check' && at >= 0) new URLSearchParams(fragment.slice(at+1)).forEach((value,key) => search.set(key,value));
    const plan = search.get('plan');
    if (plan === 'cat-wall') { search.set('pet','cat'); search.set('focus','place'); }
    if (plan === 'cat-gate') { search.set('pet','cat'); search.set('focus','door'); }
    if (plan === 'dog-living') { search.set('pet','dog'); search.set('focus','place'); }
    applyPrefill(search);
    if (section === 'check') scrollTo(document.querySelector('#check'));
  }
  document.querySelectorAll('[data-prefill]').forEach(link => link.addEventListener('click', event => {
    if (!config) return; // Native URL remains usable until configuration is ready.
    event.preventDefault();
    applyPrefill(new URLSearchParams(link.dataset.prefill));
    // Do not put the user's current answers in URL history or storage.
    scrollTo(document.querySelector('#check'));
  }));
  window.addEventListener('hashchange', readPrefill);
  if (form && panel) {
    // Attach prevention before enabling submit. Without JS the button stays disabled.
    form.addEventListener('submit', event => {
      event.preventDefault();
      if (!config || !engine || !form.reportValidity()) return;
      try {
        const result = engine.result(config,answers()); currentResult = result;
        document.querySelector('#result-title').textContent = result.title;
        document.querySelector('#result-body').replaceChildren(...result.body.map(t => node('p',t)));
        document.querySelector('#result-checks').replaceChildren(...result.checks.map(t => node('li',t)));
        document.querySelector('#absence-result').hidden = !result.absenceChecks.length;
        document.querySelector('#absence-checks').replaceChildren(...result.absenceChecks.map(t => node('li',t)));
        document.querySelector('#absence-note').textContent = result.absenceNote;
        document.querySelector('#result-notice').replaceChildren(...result.common.map(t => node('p',t)));
        const links = result.links.filter(l => /^#[a-z][a-z0-9-]*$/.test(l.href) && document.querySelector(l.href)).map(l => { const a = node('a',l.label+' →'); a.href=l.href; return a; });
        document.querySelector('#result-plan-links').replaceChildren(...links);
        panel.dataset.result = result.id; panel.hidden = false; error.hidden = true;
        panel.focus({preventScroll:true}); scrollTo(panel);
      } catch { error.textContent = '入力内容を確認してください。4つの質問を選び直すこともできます。'; error.hidden = false; }
    });
    form.addEventListener('change', updateProgress);
    fetch('data/check-results.json').then(r => { if (!r.ok) throw new Error('Check data unavailable'); return r.json(); }).then(data => {
      if (!engine || !Array.isArray(data.questions) || data.questions.length !== 4 || Object.keys(data.results || {}).length !== 8) throw new TypeError('Invalid check configuration');
      config = data; submit.disabled = false; readPrefill();
    }).catch(() => { error.textContent = 'チェックを読み込めませんでした。ページを再読み込みするか、プラン例から入口を選んでください。'; error.hidden = false; });
  }
  document.querySelector('#save-brief')?.addEventListener('click', () => {
    if (!currentResult || !engine) return;
    const date = new Intl.DateTimeFormat('ja-JP',{year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
    const url = URL.createObjectURL(new Blob(['\ufeff'+engine.memo(currentResult,date)],{type:'text/plain;charset=utf-8'}));
    const a = document.createElement('a'); a.href=url; a.download='pethome-note.txt'; document.body.append(a); a.click(); a.remove();
    window.setTimeout(() => URL.revokeObjectURL(url),1000);
  });
  // No submissions, analytics, cookies, local/session storage or photo uploads.
})();
