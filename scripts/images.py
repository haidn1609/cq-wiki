# Tải ảnh hero (icon + chân dung) từ BWiki, nén WebP -> site/img/hero/, ghi raw/img_hero.json
import json, os, re, time, urllib.parse, urllib.request, io
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

H = json.load(open('raw/hero_zh.json', encoding='utf-8'))          # tên EN -> [trang BWiki]
INFO = json.load(open('raw/fandom/bw_heroimg.json', encoding='utf-8'))  # 'File:X icon.png' -> imageinfo
UA = {'User-Agent': 'Mozilla/5.0 cq-wiki-vi'}
slug = lambda s: re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def fetch(url):
    for i in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception:
            time.sleep(3 * (i + 1))
    return None

def thumb(key, w):
    """URL thumbnail chuẩn MediaWiki: /images/cq/thumb/<a>/<ab>/<file>/<w>px-<name>"""
    base, tail = INFO[key]['url'].split('/images/cq/')
    name = key.split(':', 1)[1].replace(' ', '_')
    return f'{base}/images/cq/thumb/{tail}/{w}px-{urllib.parse.quote(name)}' if INFO[key]['width'] > w else INFO[key]['url']

def save(data, path, maxw):
    im = Image.open(io.BytesIO(data)).convert('RGBA')
    if im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    im.save(path, 'WEBP', quality=82, method=6)

def job(name):
    page = H[name][0]
    out = {'zh': page, 'src': 'https://wiki.biligame.com/cq/' + urllib.parse.quote(page)}
    for kind, key, w in (('icon', f'文件:{page} icon.png', 72), ('art', f'文件:{page}立绘.png', 300)):
        if key not in INFO: continue
        p = f'site/img/hero/{slug(name)}-{kind}.webp'
        if not os.path.exists(p):
            b = fetch(thumb(key, w)) or fetch(INFO[key]['url'])
            if not b: continue
            try: save(b, p, w)
            except Exception as e:
                print('skip', name, kind, e); continue
        out[kind] = p.replace('site/', '')
    return name, out

os.makedirs('site/img/hero', exist_ok=True)
with ThreadPoolExecutor(6) as ex:
    res = dict(ex.map(job, sorted(H)))
json.dump(res, open('raw/img_hero.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(res), 'icon', sum('icon' in v for v in res.values()), 'art', sum('art' in v for v in res.values()))
