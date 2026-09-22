/* Pure routing shared by the browser, review export and acceptance tests. */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PethomeCheck = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const LONG_ABSENCE = new Set(['late-return', 'travel']);
  function route(pet, focus, absence) {
    // Acceptance rule: the care-first route precedes ALL dog installation goals.
    if (pet === 'dog' && LONG_ABSENCE.has(absence)) return 'dog-absence-first';
    if (focus === 'product') return 'product-first';
    if (focus === 'floor') return 'floor-mat';
    if (focus === 'door') return pet === 'dog' ? 'dog-door' : 'cat-door';
    if (pet === 'both') return 'both-split';
    return pet === 'dog' ? 'dog-corner' : 'cat-window';
  }
  function valid(config, answers) {
    return config.questions.every(q => typeof answers[q.key] === 'string' && Object.hasOwn(q.options, answers[q.key]));
  }
  function result(config, answers) {
    if (!valid(config, answers)) throw new TypeError('Four valid answers required');
    const id = route(answers.pet, answers.focus, answers.absence);
    const base = config.results[id];
    if (!base) throw new TypeError('Missing result definition');
    const checks = [...base.checks];
    if (['rent', 'mansion'].includes(answers.home)) checks.unshift(config.modifiers.regulated);
    else if (answers.home === 'unknown') checks.unshift(config.modifiers.unknown);
    if (answers.pet === 'both' && id !== 'both-split') checks.push(config.modifiers.mixed);
    const absenceChecks = LONG_ABSENCE.has(answers.absence) ? [...config.absence_checks] : [];
    if (absenceChecks.length && base.memo) absenceChecks.unshift(base.memo);
    if (absenceChecks.length && answers.pet === 'both' && id !== 'both-split') {
      absenceChecks.push('犬の散歩や世話の担い手・預け先を先に確認します。');
    }
    return {id, title:base.title, body:[...base.body], checks, links:base.links.map(l => ({...l})),
      absenceChecks, absenceNote:absenceChecks.length ? config.absence_note : '', common:[...config.common],
      selected:config.questions.map(q => ({label:q.label, value:q.options[answers[q.key]]}))};
  }
  function memo(data, date) {
    const selected = data.selected.map(item => `・${item.label}: ${item.value}`);
    return [
      'pethome｜検討メモ（施工可否の診断・見積ではありません）',
      `日付: ${date}`, '', '選択:', ...selected, '', `入口: ${data.title}`, ...data.body, '',
      '先に確認すること:', ...data.checks.map(t => '・' + t), '', '留守番で見ておくこと:',
      ...(data.absenceChecks.length ? data.absenceChecks.map(t => '・' + t) : ['選んだプランの留守番メモも確認してください。']),
      ...(data.absenceNote ? [data.absenceNote] : []), '', ...data.common, '',
      '注意: このメモは申し込みではありません。サービスは準備中です。'
    ].join('\n');
  }
  return Object.freeze({route, valid, result, memo});
});
