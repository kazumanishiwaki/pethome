"""Smoke-test deployed public files from a network-enabled CI runner."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from hashlib import sha256
import json
import sys
import time
from generate_review import generate

ROOT = Path(__file__).resolve().parents[1]

class ReviewText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = False
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag == 'pre' and dict(attrs).get('id') == 'review-text':
            self.active = True
    def handle_endtag(self, tag):
        if tag == 'pre':
            self.active = False
    def handle_data(self, data):
        if self.active:
            self.parts.append(data)


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 scripts/check_published.py HTTPS_SITE_URL')
    base = sys.argv[1].rstrip('/') + '/'
    if urlsplit(base).scheme != 'https':
        raise SystemExit('Only an HTTPS deployment URL is accepted')
    summary = generate()
    expected = (ROOT/'ai-review.txt').read_text(encoding='utf-8')
    fingerprint = summary['fingerprint']
    images = json.loads((ROOT/'data/images.json').read_text(encoding='utf-8'))

    def get(path):
        url = urljoin(base,path) + '?v=' + fingerprint[:16]
        request = Request(url,headers={'User-Agent':'pethome-public-check/1.0','Cache-Control':'no-cache'})
        with urlopen(request, timeout=20) as response:
            if response.status != 200:
                raise RuntimeError(f'{path}: HTTP {response.status}')
            data = response.read(2000001)
            if len(data) > 2000000:
                raise RuntimeError(f'{path}: unexpected size')
            return data

    for attempt in range(1,7):
        try:
            info = json.loads(get('build-info.json'))
            assert info['fingerprint'] == fingerprint, 'CDN is still serving a different snapshot'
            for name in ('index.html','privacy.html','terms.html','commercial.html','ai-review.html'):
                assert get(name) == (ROOT/name).read_bytes(), f'{name}: stale or unexpected page'
            parser = ReviewText()
            parser.feed(get('ai-review.html').decode('utf-8'))
            assert ''.join(parser.parts) == expected, 'Review HTML does not contain full text'
            for ext in ('txt','md'):
                assert get('ai-review.'+ext).decode('utf-8') == expected, 'Review export mismatch'
            states = json.loads(get('ai-review-states.json'))
            assert len(states) == summary['states'] == 48, 'Self-check state count mismatch'
            for image in images:
                assert sha256(get(image['path'])).hexdigest() == image['sha256'], 'Image mismatch: '+image['path']
            for folder in ('assets/css','assets/js','data'):
                for path in (ROOT/folder).iterdir():
                    if path.is_file():
                        assert get(path.relative_to(ROOT).as_posix()) == path.read_bytes(), 'Asset mismatch: '+path.name
            print(json.dumps({'public_url':base,'html_pages':5,'images':len(images),'self_check_states':len(states),'review_characters':len(expected),'fingerprint':fingerprint,'result':'passed'},ensure_ascii=False))
            return
        except (AssertionError, OSError, ValueError, RuntimeError) as error:
            if attempt == 6:
                raise
            print(f'Public check attempt {attempt}: {error}; waiting for propagation.',flush=True)
            time.sleep(5)

if __name__ == '__main__':
    main()
