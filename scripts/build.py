"""Build the public preview and AI review exports. Python/Node standard libraries only."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from hashlib import sha256
import json
import shutil
import subprocess
from generate_review import generate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'dist'
summary = generate()
PAGES = ['index.html','privacy.html','terms.html','commercial.html','ai-review.html']
EXTRA = ['robots.txt','.nojekyll','ai-review.txt','ai-review.md','ai-review-states.json']

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links = [], []
    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        if 'id' in a: self.ids.append(a['id'])
        for key in ('href','src','action'):
            if a.get(key): self.links.append(a[key])
        for part in a.get('srcset','').split(','):
            if part.strip(): self.links.append(part.strip().split()[0])
        if tag == 'img':
            assert a.get('alt'), 'An image needs descriptive alt text'
            assert int(a.get('width',0)) > 0 and int(a.get('height',0)) > 0, 'Image dimensions missing'

docs = {}
for name in PAGES:
    text = (ROOT/name).read_text(encoding='utf-8')
    for forbidden in ('hello@example.com','mailto:','29,800','P0'):
        assert forbidden not in text, f'{name}: unpublished placeholder {forbidden}'
    parser = Document(); parser.feed(text)
    assert len(parser.ids) == len(set(parser.ids)), f'{name}: duplicate IDs'
    docs[name] = parser
for name, document in docs.items():
    for value in document.links:
        link = urlsplit(value)
        if link.scheme or link.netloc:
            assert link.scheme == 'https', f'Unexpected protocol: {value}'
            continue
        relative = unquote(link.path) or name
        target = (ROOT/relative).resolve()
        assert target.is_relative_to(ROOT) and target.is_file(), f'{name}: missing/invalid {relative}'
        if link.fragment and relative in docs:
            assert unquote(link.fragment) in docs[relative].ids, f'{name}: missing anchor {value}'
products = json.loads((ROOT/'data/products.json').read_text(encoding='utf-8'))
assert len(products) == len({p['id'] for p in products})
for p in products:
    assert p['category'] in ('cat','dog','floor') and p['relationship'] == 'reference_only'
    assert urlsplit(p['url']).scheme == 'https'
for image in json.loads((ROOT/'data/images.json').read_text(encoding='utf-8')):
    target = (ROOT/image['path']).resolve()
    assert target.is_relative_to(ROOT/'assets/img'), 'Unexpected image path'
    data = target.read_bytes()
    assert sha256(data).hexdigest() == image['sha256'], f'Image integrity mismatch: {target}'
    assert len(data) == image['bytes'] and data[:4] == b'RIFF' and data[8:12] == b'WEBP'
for script in (ROOT/'assets/js').glob('*.js'):
    subprocess.run(['node','--check',str(script)],check=True)
shutil.rmtree(OUT,ignore_errors=True); OUT.mkdir()
for name in PAGES+EXTRA: shutil.copy2(ROOT/name,OUT/name)
for directory in ('assets','data'): shutil.copytree(ROOT/directory,OUT/directory)
(OUT/'build-info.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Validated {len(PAGES)} pages, {len(products)} product references and {summary["states"]} self-check states. Build: {OUT}')
