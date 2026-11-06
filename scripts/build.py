# Gộp lưới ô + bản dịch -> site/data.js (dữ liệu wiki đã Việt hóa)
import json, glob, re, os, openpyxl

g = json.load(open('raw/grids.json', encoding='utf-8'))
TR = {}
for f in glob.glob('raw/tr/in_*.json'):
    src = json.load(open(f, encoding='utf-8'))
    out = json.load(open(f.replace('in_', 'out_'), encoding='utf-8'))
    TR.update({src[k]: out.get(k, src[k]) for k in src})

TR.update(json.load(open('raw/tr/manual.json', encoding='utf-8')))

def T(s):
    s = (s or '').strip() if isinstance(s, str) else ('' if s is None else str(s))
    return TR.get(s, s)

def cell(row, c):
    v = row.get(str(c))
    return v['t'] if v else ''

def img(row, c):
    v = row.get(str(c))
    return (v.get('img') or [''])[0].replace('site/', '') if v else ''

wb = openpyxl.load_workbook('raw/sheet.xlsx')
wbv = openpyxl.load_workbook('raw/sheet.xlsx', data_only=True)

def comments(sheet):
    """{row_index0: [comment...]} từ ghi chú ô (hover) của sheet."""
    out = {}
    for row in wb[sheet].iter_rows():
        for c in row:
            if c.comment: out.setdefault(c.row - 1, []).append(T(c.comment.text))
    return out

CLASSES = ['Warrior', 'Paladin', 'Archer', 'Hunter', 'Wizard', 'Priest']
heroes = {}  # name -> dict

ALIAS = {'Zoddd': 'Zodd'}  # ponytail: lỗi gõ trong sheet gốc

def hero(name, cls=None):
    name = ALIAS.get(name, name)
    h = heroes.setdefault(name, {'name': name})
    if cls and 'cls' not in h: h['cls'] = cls
    return h

# --- TL: hạng + nhận xét
cls = None
for i, r in enumerate(g['TL'][1:], 1):
    n = cell(r, 1)
    if not n: continue
    if n in CLASSES: cls = n; continue
    h = hero(n, cls)
    h['rank'] = cell(r, 3)
    h['note'] = T(cell(r, 4))
for i, notes in comments('TL').items():
    n = cell(g['TL'][i], 1)
    if n in heroes: heroes[n].setdefault('rankNote', []).extend(notes)

# --- SBW Options: build vũ khí + sigil
sbw_c = comments('SBW Options')
ws = wbv['SBW Options']
cls, last = None, None
for i, r in enumerate(g['SBW Options'][4:], 4):
    n = cell(r, 1)
    if not n: continue
    if n in CLASSES: cls = n; continue
    b = {
        'slot': [T(cell(r, 3)), T(cell(r, 4))],
        'crf': [cell(r, 5), cell(r, 6), cell(r, 7)],
        'set': T(ws.cell(i + 1, 10).value),
        'end': [cell(r, 12), cell(r, 13)], 'mid': [cell(r, 16), cell(r, 17)], 'early': [cell(r, 20), cell(r, 21)],
        'note': '\n'.join(x for x in [T(cell(r, 22))] + sbw_c.get(i, []) if x),
    }
    if n == '.': continue
    if n == '(ALT.)':
        if last: last.setdefault('builds', []).append({**b, 'alt': True})
        continue
    last = hero(n, cls)
    last.setdefault('builds', []).append(b)

# --- Skills: kỹ năng SP khuyến nghị
cls = None
for r in g['Skills'][1:]:
    n = cell(r, 1)
    if not n: continue
    if n in CLASSES:
        cls = n
        if cell(r, 4): heroes.setdefault('_classnote', {})[n] = T(cell(r, 4))
        continue
    sk = [cell(r, c) for c in (4, 6, 8) if cell(r, c)]
    h = hero(n, cls)
    h['skills'] = [s for s in sk if not s.startswith('Note')] or []
    notes = [T(s) for s in sk if s.startswith('Note')]
    if notes: h['skillNote'] = '\n'.join(notes)
classnote = heroes.pop('_classnote', {})

# --- Legacy Skin
for r in g['Legacy Skin'][2:]:
    n = cell(r, 1)
    if not n or n in CLASSES: continue
    sk = [{'name': cell(r, a), 'stat': cell(r, b)} for a, b in ((4, 5), (7, 8)) if cell(r, a)]
    if sk: hero(n)['skins'] = sk

# --- DPS
dps_c = comments('DPS')
wsd = wbv['DPS']
dps = []
for i, r in enumerate(g['DPS'][2:], 2):
    n = cell(r, 1)
    if not n or n in ('.',): continue
    d = {'name': n, 'cls': cell(r, 3), 'icon': img(r, 4),
         'reg': cell(r, 6), 'regHit': cell(r, 7), 'champ': cell(r, 8), 'champHit': cell(r, 9),
         'inf': cell(r, 10), 'infHit': cell(r, 11), 'bpm': T(cell(r, 12)), 'cond': T(cell(r, 13)),
         'scale': [cell(r, 14), cell(r, 15), cell(r, 16)],
         'pen': T(wsd.cell(i + 1, 18).value), 'note': T(wsd.cell(i + 1, 19).value),
         'tips': dps_c.get(i, [])}
    dps.append(d)
    hero(n, d['cls'] or None).setdefault('dps', []).append(d)

# --- CL Archive: lịch sử thay đổi
archive = []
for r in g['CL Archive'][1:]:
    if not cell(r, 0) and not cell(r, 2): continue
    e = {'date': cell(r, 0), 'patch': cell(r, 1), 'hero': cell(r, 2), 'type': T(cell(r, 3)),
         'typeImg': img(r, 3), 'note': T(cell(r, 4))}
    archive.append(e)
    if e['hero'] in heroes: heroes[e['hero']].setdefault('log', []).append(len(archive) - 1)

# --- Tier List tổng
tiers, cur = [], None
for r in g['Tier List'][1:]:
    t = cell(r, 0)
    if t and (not tiers or tiers[-1]['tier'] != t): tiers.append({'tier': t, 'heroes': []})
    names = [v['t'] for k, v in sorted(r.items(), key=lambda x: int(x[0])) if int(k) >= 2 and v['t']]
    if names and tiers: tiers[-1]['heroes'] += names
for t in tiers:
    for n in t['heroes']: hero(n)['tier'] = t['tier']

# --- Glossary
glossary = [{'term': cell(r, 0), 'def': T(cell(r, 1))} for r in g['Glossary'][1:] if cell(r, 0)]

# --- Credits
cr = g['Credits']
announce = [T(cell(r, 3)) for r in cr[1:5] if cell(r, 3)]
grades = [{'g': cell(r, 0), 'pct': cell(r, 1), 'name': T(cell(r, 2)), 'desc': T(cell(r, 3))} for r in cr[6:12] if cell(r, 0)]
contrib = [{'name': cell(r, 1), 'desc': T(cell(r, 3))} for r in cr[14:] if cell(r, 1)]

# --- Sigil Set + tùy chọn trang bị (tab ẩn nhưng có dữ liệu thật)
sigilsets = []
for r in list(wbv['Sigil Set'].iter_rows(values_only=True))[1:]:
    if r[0]: sigilsets.append({'name': T(r[0]), 'end': [r[3], r[4]], 'mid': [r[7], r[8]], 'early': [r[11], r[12]], 'used': r[13]})
equip = []
for r in list(wbv['Equip'].iter_rows(values_only=True))[1:]:
    if not r[0]: continue
    stats = {h: v for h, v in zip(['HP', 'HAP', 'Arm', 'Res', 'CC', 'CD', 'Acc', 'Eva', 'APen', 'Rpen', 'AS', 'DR', 'LS', 'CR'], r[2:16]) if v not in (None, '')}
    equip.append({'opt': T(r[0]), 'type': T(r[1]), 'stats': stats, 'note': T(r[16])})

# --- Các tab hướng dẫn dạng lưới: dịch từng ô, giữ colspan/rowspan
cols = json.load(open('raw/cols.json'))
def grid(name, drop_empty=True):
    rows = []
    for r in g[name]:
        cells = [[int(c), T(v['t']), v.get('cs', 1), v.get('rs', 1), [x.replace('site/', '') for x in v.get('img', [])]]
                 for c, v in sorted(r.items(), key=lambda x: int(x[0]))]
        if drop_empty and not any(x[1] or x[4] for x in cells): rows.append(None); continue
        rows.append(cells)
    return {'cols': cols[name], 'rows': rows}

# --- Đợt 2: sheet "CQ Guide to Almost Everything" (raw2/grids.json) + đánh giá hero từ BWiki (raw2/bw_fields.json)
import sys
sys.path.insert(0, 'scripts')
from bw_clean import clean
for f in glob.glob('raw2/tr/in_*.json'):
    src = json.load(open(f, encoding='utf-8'))
    o = f.replace('in_', 'out_')
    if os.path.exists(o):
        out = json.load(open(o, encoding='utf-8'))
        TR.update({src[k]: out.get(k, src[k]) for k in src})
g2 = json.load(open('raw2/grids.json', encoding='utf-8'))
cols2 = json.load(open('raw2/cols.json'))
def grid2(name):
    key = '2:' + name  # tránh trùng tên tab với sheet 1 (vd. Credits)
    g[key], cols[key] = g2[name], cols2[name]
    return grid(key)

F2 = json.load(open('raw2/bw_fields.json', encoding='utf-8'))
N2 = json.load(open('raw2/names.json', encoding='utf-8'))
SK2 = json.load(open('raw2/skill_zh2en.json', encoding='utf-8'))
HZ = json.load(open('raw/hero_zh.json', encoding='utf-8'))
CLS_ZH = {'剑士': 'Warrior', '骑士': 'Paladin', '弓手': 'Archer', '猎人': 'Hunter', '法师': 'Wizard', '祭司': 'Priest'}
ASK = json.load(open('raw/fandom/bw_ask.json', encoding='utf-8'))
def tidy(s):
    """Dọn mảnh wikitext tiếng Trung còn sót sau khi dịch (link ảnh, link trang ZH, tham số template)."""
    s = re.sub(r'link=[^|\s]*\|\d+px', '', s)
    s = re.sub(r'\d+px\|link=(\S*)', r'\1', s)
    s = re.sub(r'\|[^|\n]*\{\{#replace:[^\n]*', '', s)
    s = re.sub(r'\{\{#css:[^}]*\}*', '', s)
    s = re.sub(r'\{\{#expr:[^}]*\}\}', '?', s)  # ponytail: biểu thức tính chỉ số trên BWiki không chạy offline -> '?'
    s = re.sub(r'\{\{[^{}]*\}\}', '', s)
    s = re.sub(r'^\s*\}\}|\}\}\s*$|__NOEDITSECTION__', '', s, flags=re.M)
    s = re.sub(r'\[\[(?:file|文件):[^\]\n]*\]?\]?', '', s, flags=re.I)
    s = re.sub(r'\[\[([^\]\n]*[一-鿿][^\]\n#]*)(?:#[^\]\n]*)?\]?\]?', lambda m: m.group(1).split('/')[-1], s)
    s = re.sub(r'(?:字号|颜色|粗体)=[^\s*]*\**', '', s)
    s = re.sub(r'\|技能推荐\d理由=.*', '', s)
    return s.strip()
TC = lambda s: tidy(T(clean(s or '')))
num_ = lambda s: (re.match(r'\s*([\d.]+(?:#[\d.]+)*)', s or '') or [None, ''])[1].replace('#', '/')
SCORES = [('竞技', 'Arena'), ('EP5', 'Challenge EP5'), ('EP6', 'Challenge EP6'), ('讨伐F4', 'Raid F4'), ('全力战', 'Total War (Hard/Nightmare/Inferno)')]
for en, pages in HZ.items():
    f = F2.get(pages[0])
    if not f: continue
    h = hero(en, CLS_ZH.get((ASK.get(pages[0], {}).get('printouts', {}).get('职业') or [{}])[0].get('fulltext')))
    sc = [{'k': k, 'v': num_(f.get(z + '评分')), 'why': TC(f.get(z + '评分理由'))} for z, k in SCORES if num_(f.get(z + '评分'))]
    builds = []
    for line in f.get('词条符文推荐', '').split(';'):
        p = [x.strip() for x in clean(line).split(',')]
        if len(p) >= 5:
            note, label = (','.join(p[4:-1]), p[-1]) if len(p) > 5 else (p[4], '')
            builds.append({'slot': [T(p[0]), T(p[1])], 'ring': T(p[2]), 'set': T(p[3]), 'note': tidy(T(note)), 'label': T(label)})
    sk = []
    for i in range(1, 6):
        z = f.get(f'技能推荐{i}', '').strip()
        if z: sk.append({'name': SK2.get(z.split('|')[0], tidy(T(z))), 'why': TC(f.get(f'技能推荐{i}理由'))})
    h['bw'] = {k: v for k, v in {
        'review': TC(f.get('勇士评价')), 'kit': TC(f.get('技能说明')), 'scores': sc, 'builds': builds, 'skills': sk,
        'ring': TC(f.get('戒指词条推荐')), 'acc': TC(f.get('饰品词条推荐')), 'team': TC(f.get('推荐阵容搭配')),
        'sbw': TC(f.get('专武评价')), 'block': TC(f.get('消块机制')), 'inherit': TC(f.get('吃书推荐')),
        'tags': [T(t.strip()) for t in re.split('[,，]', f.get('标签', '')) if t.strip() and '{' not in t],
        'zh': pages[0], 'src': 'https://wiki.biligame.com/cq/' + __import__('urllib.parse').parse.quote(pages[0]),
    }.items() if v}

# Bảng "Có cần hero này?" (Picking Heroes / Promo-Legend / Seasonal) gắn vào hero
for tab, hc, need, purpose, note in (('Picking Heroes', 1, 3, 4, 5), ('Useful Promo/Legend Heroes', 1, 3, 4, 5), ('Seasonal Schedule', 1, 4, 5, 6)):
    for r in g2[tab][1:]:
        n = cell(r, hc)
        if n in heroes and cell(r, need):
            heroes[n]['guide'] = {'tab': tab, 'need': T(cell(r, need)), 'purpose': T(cell(r, purpose)), 'note': T(cell(r, note))}

# Hạng tự xếp cho hero chưa có trong tier list EN (dựa trên điểm BWiki, căn theo ngưỡng hạng EN hiện có)
for n, v in json.load(open('raw2/my_ranks.json', encoding='utf-8')).items():
    if n in heroes and not heroes[n].get('rank'):
        heroes[n].update(rank=v['rank'], note=v['note'], rankAuto=True)

# Hero dùng từng set sigil (đếm lại từ build, kể cả build ALT.) – thay cột Usage của sheet vốn lệch 7 set
for s in sigilsets:
    s['heroes'] = [{'name': h['name'], 'alt': bool(b.get('alt'))}
                   for h in sorted(heroes.values(), key=lambda h: h['name'].lower()) for b in h.get('builds', []) if b['set'] == s['name']]
    s['used'] = len({x['name'] for x in s['heroes']})
SIG = json.load(open('raw2/sigils.json', encoding='utf-8')) if os.path.exists('raw2/sigils.json') else {}

# --- Ảnh (nguồn: BWiki biligame + CQ Fandom), sinh bởi scripts/images.py & các bước tải ảnh
def load(p):
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
IH, IK, IG, IS = load('raw/img_hero.json'), load('raw/img_skill.json'), load('raw/img_sigil.json'), load('raw/img_skin.json')
for h in heroes.values():
    if h['name'] in IH: h['img'] = IH[h['name']]
    for s in h.get('skins', []):
        if s['name'] in IS: s['img'] = IS[s['name']]['img']
images = {'skill': {k: v['img'] for k, v in IK.items()}, 'sigil': {k: v['img'] for k, v in IG.items()},
          'src': {'skill': {k: v['src'] for k, v in IK.items()}, 'sigil': {k: v['src'] for k, v in IG.items()},
                  'skin': {k: v['src'] for k, v in IS.items()}}}

data = {
    'heroes': sorted(heroes.values(), key=lambda h: h['name'].lower()),
    'images': images,
    'classes': CLASSES, 'classNote': classnote, 'tiers': tiers, 'dps': dps, 'archive': archive,
    'glossary': glossary, 'announce': announce, 'grades': grades, 'contrib': contrib,
    'sigilsets': sigilsets, 'equip': equip, 'sigils': SIG,
    'grids': {**{k: grid(k) for k in ('Total War Guide', 'EP6 Challenge Guide', 'Challenge Stat', 'Change Log')},
              **{k: grid2(k) for k in ('General Glossary', 'SP Skills Glossary', 'Picking Heroes', 'Useful Promo/Legend Heroes',
                                       'Seasonal Schedule', 'Resources', 'CQ Maths 101', 'Ring Guide', 'Goddesses',
                                       'Daily Surprise Gift Schedule', 'World Map', 'Story Mode Secrets', 'Active Coupons', 'Credits')}},
    'ui': {k: T(k) for k in ('Hero Balance', 'DPS Change', 'New Hero', 'Tier Change', 'Announcement')},
}
open('site/data.js', 'w', encoding='utf-8').write('window.CQ=' + json.dumps(data, ensure_ascii=False) + ';')
miss = [s for s in TR if TR[s] == s]
print(len(data['heroes']), 'heroes |', len(dps), 'dps |', len(archive), 'log |', len(TR), 'tr strings')
