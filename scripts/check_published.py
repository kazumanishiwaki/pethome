"""Verify deployed bytes against the local, validated dist (no answer transmission)."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import URLError
from hashlib import sha256
import sys,time
root=Path(__file__).resolve().parents[1]/'dist'
base=(sys.argv[1] if len(sys.argv)>1 else 'https://kazumanishiwaki.github.io/pethome/').rstrip('/')+'/'
paths=['index.html','privacy.html','terms.html','commercial.html','ai-review.html','ai-review.txt','ai-review.md','build-info.json','data/check-results.json','assets/js/check-engine.js','assets/js/site.js','assets/css/site.css','assets/img/hero-night.webp','assets/img/hero-night-small.webp','assets/img/cat-window.webp','assets/img/cat-entrance.webp','assets/img/dog-living.webp']
for attempt in range(1,10):
 errors=[]
 for path in paths:
  try:
   local=(root/path).read_bytes()
   query='?v='+sha256(local).hexdigest()[:16]
   request=Request(base+path+query,headers={'User-Agent':'pethome-deployment-check','Cache-Control':'no-cache'})
   with urlopen(request,timeout=25) as response:
    assert response.status==200
    remote=response.read()
   if sha256(remote).digest()!=sha256(local).digest():errors.append(path+': not updated')
  except (URLError,TimeoutError,AssertionError) as exc:errors.append(path+': '+str(exc))
 if not errors:
  print('Public delivery verified: '+base);print('\n'.join(paths));break
 print(f'Attempt {attempt}: '+', '.join(errors))
 if attempt==9:raise SystemExit('Published content did not match this build')
 time.sleep(10)
