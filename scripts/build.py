"""Validate the public HTML and build a portable static site. No dependencies."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from hashlib import sha256
import json,shutil,subprocess
from generate_review import generate
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dist'
summary=generate()
PAGES=['index.html','privacy.html','terms.html','commercial.html','ai-review.html','404.html']
EXTRA=['robots.txt','.nojekyll','ai-review.txt','ai-review.md','ai-review-states.json']
class Document(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.images=[]
 def handle_starttag(self,tag,attributes):
  a=dict(attributes)
  if 'id' in a:self.ids.append(a['id'])
  for k in ('href','src','action'):
   if a.get(k):self.links.append(a[k])
  for part in a.get('srcset','').split(','):
   if part.strip():self.links.append(part.strip().split()[0])
  if tag=='img':
   assert a.get('alt') and int(a.get('width','0'))>0 and int(a.get('height','0'))>0
   self.images.append(a)
docs={}
for name in PAGES:
 raw=(ROOT/name).read_text(encoding='utf-8')
 for obsolete in ('hello@example.com','mailto:','SMALL CHANGES','AI GENERATED','29,800'):
  assert obsolete not in raw,f'{name}: obsolete/private text'
 p=Document();p.feed(raw);assert len(p.ids)==len(set(p.ids)),f'Duplicate IDs: {name}';docs[name]=p
for name,p in docs.items():
 for value in p.links:
  u=urlsplit(value)
  if u.scheme or u.netloc:
   assert u.scheme=='https',f'Invalid link {value}';continue
  path=unquote(u.path) or name
  if path.startswith('/pethome/'):path=path[len('/pethome/'):]
  if path in ('','/'):path='index.html'
  f=(ROOT/path).resolve();assert f.is_relative_to(ROOT) and f.is_file(),f'{name}: missing {value}'
  frag=unquote(u.fragment.split('?',1)[0])
  if frag and path in docs:assert frag in docs[path].ids,f'{name}: broken anchor {value}'
required={'main','concept','why','plans','plan-cat-wall','plan-cat-gate','plan-dog','how','price','products','faq','check','availability','service','flow','top','partners','contact'}
assert required<=set(docs['index.html'].ids)
index=(ROOT/'index.html').read_text()
assert index.count('<select ')==4 and index.count('<details>')==8
assert len(docs['index.html'].images)==4
assert 'ai-review' not in index,'Internal review must not be linked from the public funnel'
for name in ('privacy.html','terms.html','commercial.html'):assert 'ai-review' not in (ROOT/name).read_text()
products=json.loads((ROOT/'data/products.json').read_text());assert len(products)==len({p['id'] for p in products})
for p in products:
 assert p['category'] in ('cat','dog','floor') and p['relationship']=='reference_only'
 assert urlsplit(p['url']).scheme=='https'
 for field in ('why','install','checked_at','relation'):assert p.get(field)
for image in json.loads((ROOT/'data/images.json').read_text()):
 path=(ROOT/image['path']).resolve();assert path.is_relative_to(ROOT/'assets/img')
 data=path.read_bytes();assert sha256(data).hexdigest()==image['sha256'] and len(data)==image['bytes']
 assert data[:4]==b'RIFF' and data[8:12]==b'WEBP'
for script in (ROOT/'assets/js').glob('*.js'):subprocess.run(['node','--check',str(script)],check=True)
shutil.rmtree(OUT,ignore_errors=True);OUT.mkdir()
for name in PAGES+EXTRA:shutil.copy2(ROOT/name,OUT/name)
for directory in ('assets','data'):shutil.copytree(ROOT/directory,OUT/directory)
(OUT/'build-info.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(f'Validated {len(PAGES)} pages; 4 questions, 8 result variants, {summary["states"]} input combinations.')
