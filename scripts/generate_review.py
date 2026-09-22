"""Generate HTML/TXT/Markdown from current public pages and check data only."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urljoin
from hashlib import sha256
import json, re, subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='https://kazumanishiwaki.github.io/pethome/'
PAGES=('index.html','privacy.html','terms.html','commercial.html')
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
@dataclass
class Node:
 tag:str
 attrs:dict=field(default_factory=dict)
 children:list=field(default_factory=list)
class Tree(HTMLParser):
 def __init__(self,text):
  super().__init__(convert_charrefs=True);self.root=Node('document');self.stack=[self.root];self.feed(text)
 def handle_starttag(self,tag,attrs):
  n=Node(tag,dict(attrs));self.stack[-1].children.append(n)
  if tag not in VOID:self.stack.append(n)
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==tag:del self.stack[i:];return
 def handle_startendtag(self,tag,attrs):
  self.handle_starttag(tag,attrs)
  if tag not in VOID:self.handle_endtag(tag)
 def handle_data(self,data):self.stack[-1].children.append(data)
def tidy(t):
 return re.sub(r'\n{3,}','\n\n','\n'.join(re.sub(r'[ \t]+',' ',x).strip() for x in t.splitlines())).strip()
def render(n,source):
 if isinstance(n,str):return re.sub(r'\s+',' ',n)
 a,t=n.attrs,n.tag
 if t in {'script','style','head','nav','noscript'} or 'hidden' in a or a.get('aria-hidden')=='true':return ''
 if set(a.get('class','').split())&{'sr-only','skip-link','mobile-cta','anchor-alias'}:return ''
 if a.get('id') in {'product-grid','product-count','check-result'}:return ''
 text=''.join(render(c,source) for c in n.children)
 if t=='br':return '\n'
 if t=='img':return '\n画像: '+a.get('alt','')+'\n'
 if re.fullmatch(r'h[1-6]',t):return '\n\n'+'#'*min(int(t[1])+1,6)+' '+tidy(text).replace('\n',' ')+'\n\n'
 if t=='summary':return '\n\n#### '+tidy(text)+'\n'
 if t=='option':return '\n- '+tidy(text) if a.get('value') else ''
 if t=='li':return '\n- '+tidy(text)
 if t=='dt':return '\n'+tidy(text)+': '
 if t=='dd':return tidy(text)+'\n'
 if t=='button':return '\n[ボタン] '+tidy(text)+'\n'
 if t=='a' and a.get('href') and tidy(text):return ' ['+tidy(text)+']('+urljoin(urljoin(BASE,source),a['href'])+') '
 if t in {'p','div','section','article','main','body','header','footer','figure','figcaption','aside','ul','ol','dl','form','label'}:return '\n'+text+'\n'
 return text

def generate():
 cfg=json.loads((ROOT/'data/check-results.json').read_text())
 products=json.loads((ROOT/'data/products.json').read_text())
 exported=json.loads(subprocess.check_output(['node',str(ROOT/'scripts/export_review_states.cjs')],text=True))
 public_inputs=list(PAGES)+['data/check-results.json','data/products.json','data/images.json','assets/js/check-engine.js','assets/js/site.js','assets/css/site.css']
 digest=sha256()
 for path in public_inputs:digest.update(path.encode());digest.update((ROOT/path).read_bytes())
 fingerprint=digest.hexdigest()
 pieces=['# pethome｜公開コンテンツ・AIレビュー用テキスト',
 '基準日: 2026-09-22\n公開サイト: '+BASE,
 'このページは内部レビューのための集約です。一般向けナビには掲載していません。URLを知っている人は閲覧できます。アクセス制限はありません。非公開の事業資料・ターゲット情報・料金仮説は含めていません。',
 '## 現在の提供状況\nサービス準備中。相談・写真受付・決済は行いません。4問のセルフチェックは端末内で処理します。',
 '## レビュー時の確認観点\n公開コピーと実際の機能の整合、8種類の結果、留守番への注意、費用の未確定表示、生成画像の注記、申込み導線がないことを確認してください。']
 for name in PAGES:
  raw=(ROOT/name).read_text()
  title=re.search(r'<title>(.*?)</title>',raw,re.S).group(1)
  pieces.append('## ページ: '+title+'\n元ページ: '+urljoin(BASE,name)+'\n\n'+tidy(render(Tree(raw).root,name)))
 pieces.append('## 参考商品データ')
 for p in products:
  pieces.append('\n'.join(['### '+p['maker']+' / '+p['name'],'区分: '+p['type'],'この部屋で見る理由: '+p['why'],'設置時の確認: '+p['install'],'公式確認先: '+p['url'],'確認日: '+p['checked_at'],'関係: '+p['relation']]))
 pieces.append('## セルフチェックのルーティング\n犬かつ遅い帰宅・外泊の場合は、目的にかかわらず担い手を先に表示します。それ以外は、商品指定→マット→玄関→猫犬のゾーン分け→猫の窓辺／犬の一角の順です。住まいは確認事項、留守の時間は留守番メモを修飾します。')
 for key,r in cfg['results'].items():
  pieces.append('\n'.join(['### '+r['title'],'内部キー: '+key,*r['body'],'\n先に確認すること:',*['- '+c for c in r['checks']],'\nプランの留守番メモ: '+r.get('memo',''),'\n関連プラン:',*['- '+l['label']+' '+BASE+l['href'] for l in r['links']]]))
 pieces.append('## 共通修飾子\n'+'\n'.join(cfg['modifiers'].values())+'\n\n留守番で見ておくこと（遅い帰宅・外泊の場合）:\n'+'\n'.join('- '+c for c in cfg['absence_checks'])+'\n'+cfg['absence_note']+'\n\n'+'\n'.join(cfg['common']))
 pieces.append('## 画像と現実の区別\n掲載画像は生成された雰囲気イメージです。施工実績・特定商品の再現ではありません。ヒーローには生成した夜の室内イメージを使用しています。文字と操作部は画像ではなくHTMLです。')
 pieces.append('## 同期情報\nフィンガープリント: '+fingerprint+'\n4問・8種類の結果。全192入力組み合わせを検証。')
 text=tidy('\n\n'.join(pieces))+'\n'
 for ext in ('txt','md'):(ROOT/f'ai-review.{ext}').write_text(text,encoding='utf-8')
 (ROOT/'ai-review-states.json').write_text(json.dumps(exported,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 page='''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>公開コンテンツ全文｜pethome 内部レビュー用</title><link rel="stylesheet" href="assets/css/ai-review.css"><script defer src="assets/js/review-page.js"></script></head><body><header><div class="review-wrap"><a href="index.html">← サイトへ</a><p class="eyebrow">内部レビュー用・自動生成</p><h1>pethome コンテンツ全文</h1><p class="intro">最新のHTML本文・参考商品・4問のセルフチェック・8種類の結果・補足ページを集約しています。一般向けナビには載せていませんが、アクセス制限のある非公開ページではありません。</p><div class="review-actions"><button id="copy-content" type="button">全文をコピー</button><a href="ai-review.txt" download>TXT保存</a><a href="ai-review.md" download>Markdown保存</a></div><p id="copy-status" role="status"></p><p class="fingerprint">同期ID: __HASH__</p></div></header><main class="review-wrap"><pre id="review-text">__TEXT__</pre></main><footer><div class="review-wrap">公開データのみを集約。4問・8種類の結果。サービス準備中。</div></footer></body></html>'''
 (ROOT/'ai-review.html').write_text(page.replace('__HASH__',fingerprint).replace('__TEXT__',escape(text)),encoding='utf-8')
 return {'fingerprint':fingerprint,'states':exported['tested_combinations'],'questions':4,'result_variants':8,'characters':len(text),'version':cfg['version']}
if __name__=='__main__':print(json.dumps(generate(),ensure_ascii=False))
