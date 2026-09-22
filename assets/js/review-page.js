(() => {
  'use strict';
  const text = document.querySelector('#review-text');
  const button = document.querySelector('#copy-content');
  const status = document.querySelector('#copy-status');
  if (!text || !button || !status) return;
  button.addEventListener('click', async () => {
    try {
      if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(text.textContent);
      status.textContent = '全文をコピーしました。AIレビューに貼り付けて使えます。';
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(text);
      selection.removeAllRanges(); selection.addRange(range);
      status.textContent = '全文を選択しました。⌘C / Ctrl+C でコピーするか、TXTを保存してください。';
    }
  });
})();
