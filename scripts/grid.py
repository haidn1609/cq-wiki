# Parse các tab htmlview của Google Sheets thành lưới ô {row: {col: {t, img}}} (giữ text hiển thị + ảnh)
import re, html, json, os, hashlib, urllib.request, glob
GIDS = {'Credits':'1706691344','CL Archive':'1717518592','Change Log':'2131363859','Glossary':'963486876',
 'Total War Guide':'1482434327','EP6 Challenge Guide':'1731727196','Tier List':'297127573','TL':'380597452',
 'SBW Options':'1174540630','Skills':'904073273','Legacy Skin':'432419334','DPS':'799339660','SP':'1430145850','Challenge Stat':'1111272512'}
import sys
RAW = sys.argv[1] if len(sys.argv) > 1 else 'raw'
import sys
RAW = sys.argv[1] if len(sys.argv) > 1 else 'raw'   # raw = sheet tier list, raw2 = sheet Guide to Almost Everything
if RAW != 'raw': GIDS = json.load(open(f'{RAW}/gids.json', encoding='utf-8'))
IMG = json.load(open('raw/imgmap.json')) if os.path.exists('raw/imgmap.json') else {}

def img(u):
    u = u.replace('&amp;', '&')
    if u not in IMG:
        p = f'site/img/{hashlib.md5(u.encode()).hexdigest()[:12]}.png'
        try:
            if not os.path.exists(p): urllib.request.urlretrieve(u, p)
            IMG[u] = p
        except Exception: IMG[u] = None  # ponytail: ảnh đã hỏng sẵn trên sheet gốc
    return IMG[u]

def cell_text(c):
    c = re.sub(r'<br\s*/?>', '\n', c)
    return html.unescape(re.sub(r'<[^>]+>', '', c)).strip()

COLS = {}
def parse_file(path, gid, grid):
    h = open(path, encoding='utf-8').read()
    body = h[h.find('<tbody>'):h.find('</tbody>')]
    cols = [int(x) for x in re.findall(rf'<th id="{gid}C(\d+)"', h)]
    COLS.setdefault(gid, set()).update(cols)
    pending = set()
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', body, re.S):
        m = re.search(rf'<th id="{gid}R(\d+)"', tr)
        if not m: continue
        r, row, ci = int(m[1]), {}, 0
        for attrs, inner in re.findall(r"<td([^>]*)>(.*?)</td>", tr, re.S):
            if "freezebar-cell" in attrs: continue
            while (r, ci) in pending: ci += 1
            cs = int((re.search(r'colspan="(\d+)"', attrs) or [0, 1])[1])
            rs = int((re.search(r'rowspan="(\d+)"', attrs) or [0, 1])[1])
            imgs = [p for p in (img(u) for u in re.findall(r'<img[^>]*src="([^"]*)"', inner)) if p]
            t = cell_text(inner)
            if ci < len(cols) and (t or imgs):
                row[cols[ci]] = {'t': t, **({'img': imgs} if imgs else {}), **({'cs': cs} if cs > 1 else {}), **({'rs': rs} if rs > 1 else {})}
            for dr in range(1, rs):
                for dc in range(cs): pending.add((r + dr, ci + dc))
            ci += cs
        if r not in grid or len(row) >= len(grid[r]): grid[r] = row

out = {}
for name, gid in GIDS.items():
    grid = {}
    for f in sorted(glob.glob(f'{RAW}/html/{gid}*.html')): parse_file(f, gid, grid)
    out[name] = [grid.get(i, {}) for i in range(max(grid) + 1)] if grid else []
    print(name, len(out[name]))
json.dump(out, open(f'{RAW}/grids.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(IMG, open('raw/imgmap.json', 'w'))
json.dump({n: sorted(COLS[g]) for n, g in GIDS.items()}, open(f'{RAW}/cols.json', 'w'))
