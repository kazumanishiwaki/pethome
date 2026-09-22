'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname,'..');
const config = JSON.parse(fs.readFileSync(path.join(root,'data/check-results.json'),'utf8'));
const engine = require(path.join(root,'assets/js/check-engine.js'));
const states=[];
for (const pet of Object.keys(config.questions[0].options))
 for (const home of Object.keys(config.questions[1].options))
  for (const absence of Object.keys(config.questions[2].options))
   for (const focus of Object.keys(config.questions[3].options)) {
    const answers={pet,home,absence,focus}; const result=engine.result(config,answers);
    assert.equal(result.checks.length>=3 && result.checks.length<=6,true);
    const long=['late-return','travel'].includes(absence);
    assert.equal(result.absenceChecks.length>0,long);
    if (pet==='dog' && long) assert.equal(result.id,'dog-absence-first');
    if (home==='rent'||home==='mansion') assert.equal(result.checks[0],config.modifiers.regulated);
    if (home==='unknown') assert.equal(result.checks[0],config.modifiers.unknown);
    if (!(pet==='dog'&&long) && focus==='product') assert.equal(result.id,'product-first');
    if (!(pet==='dog'&&long) && focus==='floor') assert.equal(result.id,'floor-mat');
    if (pet==='both'&&focus==='place') assert.equal(result.id,'both-split');
    const memo=engine.memo(result,'2026/09/22');
    for (const text of ['日付:','選択:','入口:','先に確認すること:','留守番で見ておくこと:','申し込みではありません']) assert.ok(memo.includes(text));
    states.push({answers,result_id:result.id,home_modifier:home,absence_block:long});
   }
assert.equal(states.length,192);
assert.equal(new Set(states.map(s=>s.result_id)).size,8);
assert.throws(()=>engine.result(config,{pet:'invalid'}));
process.stdout.write(JSON.stringify({schema_version:2,question_count:4,result_variants:8,tested_combinations:states.length,states},null,2)+'\n');
