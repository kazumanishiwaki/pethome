(() => {
  const productGrid = document.querySelector('#product-grid');
  const filterButtons = [...document.querySelectorAll('[data-filter]')];
  let products = [];

  const escapeHtml = (value = '') => String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  const renderProducts = (filter = 'all') => {
    if (!productGrid) return;
    const rows = filter === 'all'
      ? products
      : products.filter((item) => item.category === filter);

    productGrid.innerHTML = rows.map((item) => `
      <article class="product-card">
        <span class="product-type">${escapeHtml(item.type)} / ${escapeHtml(item.priority)}</span>
        <h3>${escapeHtml(item.name)}</h3>
        <p class="maker">${escapeHtml(item.maker)}</p>
        <p>${escapeHtml(item.summary)}</p>
        <div class="product-meta">
          <span>${escapeHtml(item.install)}</span>
          <span class="product-price">${escapeHtml(item.price)}</span>
        </div>
        <a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">メーカー・販売元で確認 ↗</a>
      </article>
    `).join('');
  };

  fetch('data/products.json')
    .then((response) => {
      if (!response.ok) throw new Error('product data unavailable');
      return response.json();
    })
    .then((data) => {
      products = Array.isArray(data) ? data : [];
      renderProducts();
    })
    .catch(() => {
      if (productGrid) {
        productGrid.innerHTML = '<p>商品データを読み込めませんでした。</p>';
      }
    });

  filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
      filterButtons.forEach((item) => item.classList.remove('is-active'));
      button.classList.add('is-active');
      renderProducts(button.dataset.filter || 'all');
    });
  });

  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (event) => {
      const id = link.getAttribute('href');
      if (!id || id === '#') return;
      const target = document.querySelector(id);
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  const form = document.querySelector('.mvp-form');
  if (form) {
    form.addEventListener('submit', (event) => {
      const action = form.getAttribute('action') || '';
      if (action.includes('hello@example.com')) {
        event.preventDefault();
        window.alert('MVP受付フォームは準備中です。公開前にTallyまたはFormspreeへ接続します。');
      }
    });
  }

  const params = new URLSearchParams(window.location.search);
  ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'].forEach((key) => {
    const value = params.get(key);
    if (value) sessionStorage.setItem(key, value);
  });
})();
