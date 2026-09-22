(() => {
  'use strict';
  const grid = document.querySelector('#product-grid');
  const count = document.querySelector('#product-count');
  const filters = [...document.querySelectorAll('[data-filter]')];
  let products = [];
  let activeFilter = 'all';
  const make = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const safeUrl = (value) => {
    try { const url = new URL(value); return url.protocol === 'https:' ? url.href : null; }
    catch { return null; }
  };
  const render = () => {
    if (!grid) return;
    const rows = products.filter(p => activeFilter === 'all' || p.category === activeFilter);
    const fragment = document.createDocumentFragment();
    rows.forEach(p => {
      const card = make('article', undefined, 'product-card');
      card.append(make('span', p.type, 'product-type'), make('h3', p.name), make('p', p.maker, 'maker'), make('p', p.summary), make('div', p.install, 'product-meta'));
      const href = safeUrl(p.url);
      if (href) { const link = make('a', 'メーカー公式で仕様を確認 ↗'); link.href = href; link.target = '_blank'; link.rel = 'noopener noreferrer'; card.append(link); }
      fragment.append(card);
    });
    if (!rows.length) fragment.append(make('p', 'この条件の参考商品はまだ掲載していません。'));
    grid.replaceChildren(fragment);
    if (count) count.textContent = `参考商品 ${rows.length}件`;
  };
  filters.forEach(button => button.addEventListener('click', () => {
    activeFilter = button.dataset.filter || 'all';
    filters.forEach(b => { const selected = b === button; b.classList.toggle('is-active', selected); b.setAttribute('aria-pressed', String(selected)); });
    render();
  }));
  if (grid) fetch('data/products.json').then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }).then(data => {
    if (!Array.isArray(data)) throw new Error('Invalid product data');
    products = data.filter(p => p && typeof p.name === 'string' && typeof p.category === 'string');
    render();
  }).catch(() => { grid.replaceChildren(make('p', '参考商品を読み込めませんでした。時間をおいてページを再読み込みしてください。')); if (count) count.textContent = ''; });

  const form = document.querySelector('#self-check');
  const result = document.querySelector('#check-result');
  let memo = '';
  if (form && result) {
    form.addEventListener('submit', event => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const data = new FormData(form);
      const pet = data.get('pet'), home = data.get('home'), goal = data.get('goal');
      if (!['cat','dog','both'].includes(pet) || !['owned','condo','rental','unknown'].includes(home) || !['space','gate','install','floor'].includes(goal)) return;
      let title, body, anchor;
      const checks = [];
      if (goal === 'install') {
        title = '商品が決まっているなら、取付条件の整理から。';
        body = '空間全体のプランを必須にせず、品番・取付場所・必要作業を先に確認する入口です。自立式を置くだけで足りる場合は、施工が不要なこともあります。'; anchor = '#price';
        checks.push('品番・取扱説明書・付属部品、購入済みかどうかを整理する。');
      } else if (goal === 'floor') {
        title = '張り替える前に、置き敷きでできることを。';
        body = 'よく通る場所と休む場所を整理し、既存床に合うマットを検討する入口です。歩行の安全や、滑りの完全な防止を保証する結果ではありません。'; anchor = '#plan-dog';
        checks.push('床材・ワックス・床暖房との相性、扉との干渉、洗い方を確認する。');
      } else if (goal === 'gate') {
        title = pet === 'dog' ? 'ゲート一つと、周辺の動線から。' : '猫用ゲートと、出入口まわりから。';
        body = '開口幅だけでなく、固定先の状態と扉の動き、通り抜けや飛び越えの可能性を確かめる入口です。設置すれば脱走を完全に防げるという意味ではありません。'; anchor = pet === 'dog' ? '#plan-dog' : '#plan-cat-gate';
        checks.push('対象動物・体格・開口寸法・設置場所の条件を、メーカー説明書と照合する。');
        checks.push('階段上など転落につながる場所は、専用の設置条件を施工店・メーカーに確認する。');
      } else if (pet === 'dog') {
        title = 'リビングの一角に、犬のくつろぐ場所を。';
        body = '既製サークルやベッド、ゲート、マットを別々に増やすのではなく、人の通り道も含めて一つのゾーンとして整理する入口です。'; anchor = '#plan-dog';
        checks.push('寝る場所・食事・トイレ・人の通り道と、掃除するスペースを確認する。');
      } else {
        title = pet === 'both' ? '猫の壁面と犬の居場所を、分けて考える。' : '壁一面と、今ある家具のつながりから。';
        body = '既製ステップやウォークを候補に、窓・家具・扉との関係を整理する入口です。高い場所を一律に増やさず、普段の動きに合う配置を検討します。'; anchor = '#plan-cat-wall';
        checks.push('壁を正面から見た寸法、周囲の家具、ペットの年齢・体格・動き方を整理する。');
      }
      if (pet === 'both') checks.push('猫と犬それぞれの居場所と、相手を避けられる配置を別々に検討する。');
      if (home === 'rental') checks.push('賃貸では固定や穴あけ前に貸主・管理会社へ確認。突っ張り式やマットも無傷・原状回復を保証しない。');
      if (home === 'condo') checks.push('マンションの管理規約・工事申請・施工対象部分の条件を先に確認する。');
      if (home === 'unknown') checks.push('住まいの条件が分かるまでは商品を発注せず、確認できる図面や管理窓口を整理する。');
      checks.push('壁面固定の可否・下地・固定方法は写真だけでは判断しない。購入前に施工店の現地確認を受ける。');
      document.querySelector('#result-title').textContent = title;
      document.querySelector('#result-body').textContent = body;
      document.querySelector('#result-checks').replaceChildren(...checks.map(text => make('li', text)));
      document.querySelector('#result-link').href = anchor;
      memo = ['pethome｜検討メモ（施工可否の診断・見積ではありません）', '', title, body, '', ...checks.map(t => '・' + t), '', 'このメモは端末内で作成。個別相談・予約・発注は成立していません。'].join('\n');
      result.hidden = false;
      result.focus({preventScroll:true});
      result.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block:'nearest'});
    });
  }
  document.querySelector('#save-brief')?.addEventListener('click', () => {
    if (!memo) return;
    const url = URL.createObjectURL(new Blob(['\ufeff' + memo], {type:'text/plain;charset=utf-8'}));
    const link = document.createElement('a'); link.href = url; link.download = 'pethome-note.txt'; document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  // This preview intentionally has no analytics, storage, photo upload, or contact transmission.
})();
