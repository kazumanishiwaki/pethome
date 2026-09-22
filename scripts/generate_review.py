"""Generate a static, complete public-copy review page. No network or dependencies.

Only allowlisted public pages/data are read. Private plans/research are not inputs.
Self-check results are exported from the existing UI handler, not maintained twice.
"""
from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass, field
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://kazumanishiwaki.github.io/pethome/'
PAGE_NAMES = ('index.html', 'privacy.html', 'terms.html', 'commercial.html')
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

@dataclass
class Node:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

class Tree(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.root = Node('document')
        self.stack = [self.root]
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)
    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)
    def handle_data(self, data):
        self.stack[-1].children.append(data)

def nodes(node: Node):
    yield node
    for child in node.children:
        if isinstance(child, Node):
            yield from nodes(child)

def plain(node):
    if isinstance(node, str):
        return node
    if node.tag == 'br':
        return '\n'
    return ''.join(plain(child) for child in node.children)

def tidy(text: str) -> str:
    text = '\n'.join(re.sub(r'[ \t]+', ' ', line).strip() for line in text.splitlines())
    return re.sub(r'\n{3,}', '\n\n', text).strip()

def render(node, source: str) -> str:
    if isinstance(node, str):
        return re.sub(r'\s+', ' ', node)
    a, tag = node.attrs, node.tag
    if tag in {'script','style','head','nav','noscript'} or 'hidden' in a or a.get('aria-hidden') == 'true':
        return ''
    if set(a.get('class','').split()) & {'sr-only','skip-link','mobile-cta'}:
        return ''
    if a.get('id') in {'product-grid','product-count','check-result'}:
        return ''  # These are captured separately from data and the actual JS handler.
    text = ''.join(render(child, source) for child in node.children)
    if tag == 'br': return '\n'
    if tag == 'img': return '\n[画像の代替テキスト] ' + a.get('alt','') + '\n'
    if tag == 'option': return ('\n- ' + tidy(text)) if a.get('value') else ''
    if re.fullmatch(r'h[1-6]', tag): return '\n\n' + '#' * min(int(tag[1])+1, 6) + ' ' + tidy(text).replace('\n',' ') + '\n\n'
    if tag == 'summary': return '\n\n#### ' + tidy(text) + '\n'
    if tag == 'a':
        href = a.get('href','')
        if href and tidy(text):
            return ' [' + tidy(text) + '](' + urljoin(urljoin(BASE,source),href) + ') '
    if tag == 'button': return '\n[ボタン] ' + tidy(text) + '\n'
    if tag == 'li': return '\n- ' + tidy(text)
    if tag == 'dt': return tidy(text) + ': '
    if tag == 'dd': return tidy(text) + '\n'
    if tag in {'p','div','main','body','section','article','figure','figcaption','ul','ol','dl','fieldset','legend','footer','header','form'}:
        return '\n' + text + '\n'
    return text

def generate() -> dict:
    sources = list(PAGE_NAMES) + ['data/products.json', 'data/images.json', 'assets/js/site.js']
    digest = sha256()
    for name in sources:
        digest.update(name.encode() + b'\0' + (ROOT/name).read_bytes() + b'\0')
    fingerprint = digest.hexdigest()
    docs = {name:Tree((ROOT/name).read_text(encoding='utf-8')).root for name in PAGE_NAMES}
    form = next(n for n in nodes(docs['index.html']) if n.attrs.get('id') == 'self-check')
    definitions = {n.attrs['name']:[{'value':o.attrs['value'],'label':tidy(plain(o))} for o in nodes(n) if o.tag == 'option' and o.attrs.get('value')] for n in nodes(form) if n.tag == 'select'}
    exported = subprocess.run(['node', str(ROOT/'scripts/export_review_states.cjs')], input=json.dumps(definitions), encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15, check=True)
    states = json.loads(exported.stdout)
    expected = 1
    for options in definitions.values(): expected *= len(options)
    if len(states) != expected: raise ValueError('Self-check state export incomplete')
    sections = [
        '# pethome｜AIレビュー用 公開コンテンツ全文',
        '公開サイト: ' + BASE,
        '内容フィンガープリント: ' + fingerprint,
        'この文書は同じビルドの公開HTML・商品データ・セルフチェックから自動集約しています。JSを実行しなくても全文を読めます。本文を変えると次回ビルドでこの文書も更新されます。',
        '## レビューの前提と範囲',
        'サイト上の将来計画と、現在利用できる機能を区別してレビューしてください。掲載画像はAI生成の空間イメージであり、施工実績・特定商品の再現・安全性の根拠ではありません。公開中の本文と機能だけを集約し、内部の採算試算、顧客情報、未公開の調査資料は含めません。',
        '確認したい観点: 顧客が対価を払う理由／既製品・軽施工という範囲との整合性／猫と犬それぞれの訴求／料金・受付状況の誤認／施工責任と安全表現／画像とサービス範囲のずれ／CTAと実装済み機能の一致。',
        '---\n\n## 1. トップページの公開本文',
        '出典: ' + BASE
    ]
    index = docs['index.html']
    title = next(n for n in nodes(index) if n.tag == 'title')
    description = next(n.attrs['content'] for n in nodes(index) if n.tag == 'meta' and n.attrs.get('name') == 'description')
    sections += ['ページタイトル: ' + tidy(plain(title)), '検索用説明文: ' + description]
    for node in nodes(index):
        if 'preview-notice' in node.attrs.get('class','').split():
            sections.append('\n'.join(tidy(plain(c)) for c in node.children if isinstance(c, Node)))
            break
    main = next(n for n in nodes(index) if n.tag == 'main')
    sections.append(tidy(render(main,'index.html')))
    sections += ['---\n\n## 2. 参考商品の全文（動的表示部分）', '出典: ' + urljoin(BASE,'data/products.json')]
    for product in json.loads((ROOT/'data/products.json').read_text(encoding='utf-8')):
        sections += ['### ' + product['maker'] + ' / ' + product['name'], '\n'.join([
            '区分: '+product['type'], product['summary'], '設置時の確認: '+product['install'],
            '公式確認先: '+product['url'], '元データの確認日: '+product['checked_at'], '関係: 参考情報のみ（提携・販売代理店契約を示すものではありません）'])]
    sections += ['---\n\n## 3. セルフチェックの全結果文言',
                 f'出典: assets/js/site.js の実際の処理。全{len(states)}通りを実行して同じ結果本文をまとめています。各選択の完全な結果と保存メモは '+urljoin(BASE,'ai-review-states.json')+' にも収録しています。']
    groups = OrderedDict()
    for state in states:
        groups.setdefault((state['title'],state['body'],state['link']), []).append(state)
    for (heading, body, link), variants in groups.items():
        pairs = list(dict.fromkeys(v['labels']['pet']+' × '+v['labels']['goal'] for v in variants))
        sections += ['### '+heading, '表示条件: '+' / '.join(pairs), body, '誘導先: '+urljoin(BASE,'index.html'+link), '確認事項（該当条件の文言を付加）:']
        checks = list(dict.fromkeys(check for v in variants for check in v['checks']))
        for check in checks:
            matching = [v for v in variants if check in v['checks']]
            homes = set(v['labels']['home'] for v in matching)
            pets = set(v['labels']['pet'] for v in matching)
            if len(matching) == len(variants): condition = 'この結果の全選択'
            elif len(homes) == 1: condition = '住まい: '+next(iter(homes))
            elif len(pets) == 1: condition = 'ペット: '+next(iter(pets))
            else: condition = '該当する選択。詳細は全分岐JSONを参照'
            sections.append('- ['+condition+'] '+check)
    sections += ['### 検討メモの保存', '保存ファイル名: pethome-note.txt',
                 '冒頭: '+states[0]['memo'].splitlines()[0],
                 '内容: 表示された結果タイトル、本文、その選択条件に該当する確認事項を順に収録。',
                 '末尾: '+states[0]['memo'].splitlines()[-1]]
    sections.append('---\n\n## 4. 補足ページの全文')
    for name in PAGE_NAMES[1:]:
        sections.append('出典: '+urljoin(BASE,name))
        page_main = next(n for n in nodes(docs[name]) if n.tag == 'main')
        sections.append(tidy(render(page_main,name)))
    sections += ['---\n\n## 5. 画像ファイルと表示上の位置づけ',
                 '3枚とも本プロジェクトで生成したAI画像です。写真のような質感でも実在の施工写真ではありません。画像内容と特定のメーカー製品の品番・価格・施工条件を結びつけて解釈しないでください。']
    labels = {'cat-wall':'トップと猫の壁面・窓辺プラン','cat-entrance':'猫の玄関・出入口プラン','dog-living':'犬のくつろぎ・動線プラン'}
    for image in json.loads((ROOT/'data/images.json').read_text(encoding='utf-8')):
        if '-small.' in image['path']: continue
        key = Path(image['path']).stem
        sections.append(labels[key]+': '+urljoin(BASE,image['path'])+'\n形式・サイズ: WebP / '+str(image['width'])+' × '+str(image['height'])+'\n位置づけ: AI生成の空間イメージ。施工実績・設置仕様・安全性の証拠ではありません。')
    sections += ['---\n\n## 6. この集約ページについて',
                 'HTML: '+urljoin(BASE,'ai-review.html')+'\nTXT: '+urljoin(BASE,'ai-review.txt')+'\nMarkdown: '+urljoin(BASE,'ai-review.md'),
                 '公開情報を集めたページです。noindexはアクセス制限ではありません。生成元の公開コンテンツを修正し、ビルドで再生成してください。']
    text = '\n\n'.join(sections).strip()+'\n'
    for ext in ('txt','md'):
        (ROOT/f'ai-review.{ext}').write_text(text,encoding='utf-8')
    (ROOT/'ai-review-states.json').write_text(json.dumps(states,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    template = '''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,follow"><title>AIレビュー用コンテンツ全文｜pethome</title><meta name="description" content="pethomeの公開本文・商品情報・FAQ・セルフチェック結果・補足ページを自動集約したAIレビュー用のテキストページです。"><link rel="stylesheet" href="assets/css/ai-review.css"><script defer src="assets/js/review-page.js"></script></head>
<body><header><div class="review-wrap"><a href="index.html">← pethome サービスサイト</a><p class="eyebrow">PUBLIC CONTENT / REVIEW EDITION</p><h1>AIレビュー用コンテンツ全文</h1><p class="intro">サービス本文、プラン、料金方針、商品候補、FAQ、セルフチェックの結果文言、補足ページを一か所に集約しています。本文はJavaScriptなしで読めます。更新時は同じソースから自動再生成します。</p><p class="intro">全文をコピーするか、TXT / MarkdownのURLをレビューしたいAIに渡してください。内部資料や個人情報は含めていません。</p><div class="review-actions"><button type="button" id="copy-content">全文をコピー</button><a href="ai-review.txt" download>TXTを保存</a><a href="ai-review.md" download>Markdownを保存</a><a href="ai-review-states.json">セルフチェック全分岐</a></div><p id="copy-status" role="status" aria-live="polite"></p><p class="fingerprint">CONTENT SNAPSHOT: __FINGERPRINT__ / セルフチェック __COUNT__ 通り</p></div></header><main class="review-wrap"><pre id="review-text" tabindex="0">__CONTENT__</pre></main><footer><div class="review-wrap">このページは公開資料です。内容の修正は元のHTML・商品データ・セルフチェック処理に反映してください。<br><a href="index.html">サービスサイトへ戻る</a></div></footer></body></html>
'''
    html = template.replace('__FINGERPRINT__',fingerprint[:16]).replace('__COUNT__',str(len(states))).replace('__CONTENT__',escape(text))
    (ROOT/'ai-review.html').write_text(html,encoding='utf-8')
    return {'fingerprint':fingerprint,'states':len(states),'result_variants':len(groups),'characters':len(text)}

if __name__ == '__main__':
    print(json.dumps(generate(),ensure_ascii=False))
