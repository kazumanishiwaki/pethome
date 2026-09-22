"""Validate the public preview and copy only deployable files. Standard library only."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
PAGES = ['index.html', 'privacy.html', 'terms.html', 'commercial.html']

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ('href', 'src', 'action'):
            if attrs.get(key):
                self.links.append(attrs[key])

docs = {}
for name in PAGES:
    text = (ROOT / name).read_text(encoding='utf-8')
    for forbidden in ('hello@example.com', 'mailto:', '29,800', 'P0'):
        assert forbidden not in text, f'{name}: unpublished placeholder {forbidden}'
    parser = Document()
    parser.feed(text)
    assert len(parser.ids) == len(set(parser.ids)), f'{name}: duplicate IDs'
    docs[name] = parser
for name, document in docs.items():
    for value in document.links:
        link = urlsplit(value)
        if link.scheme or link.netloc:
            assert link.scheme == 'https', f'Unexpected protocol: {value}'
            continue
        path = unquote(link.path) or name
        assert (ROOT / path).is_file(), f'{name}: missing {path}'
        if link.fragment and path in docs:
            assert unquote(link.fragment) in docs[path].ids, f'{name}: missing anchor {value}'
products = json.loads((ROOT / 'data/products.json').read_text(encoding='utf-8'))
assert len(products) == len({p['id'] for p in products})
for p in products:
    assert p['category'] in ('cat', 'dog', 'floor')
    assert urlsplit(p['url']).scheme == 'https'
    assert p['relationship'] == 'reference_only'
shutil.rmtree(OUT, ignore_errors=True)
OUT.mkdir()
for name in PAGES + ['robots.txt', '.nojekyll']:
    shutil.copy2(ROOT / name, OUT / name)
for directory in ('assets', 'data'):
    shutil.copytree(ROOT / directory, OUT / directory)
print(f'Validated {len(PAGES)} pages and {len(products)} product references. Build: {OUT}')
