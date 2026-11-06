# Gom các chuỗi tiếng Anh cần Việt hóa -> raw/tr/in_XX.json (chia batch)
import json, re, os, openpyxl
g = json.load(open('raw/grids.json', encoding='utf-8'))
wb = openpyxl.load_workbook('raw/sheet.xlsx')

def col(name, c, start=0): return [r[str(c)]['t'] for r in g[name][start:] if str(c) in r]

# Tên riêng giữ nguyên: nhân vật, sigil, skin, skill
heroes = set(col('TL', 1) + col('SBW Options', 1) + col('DPS', 1) + col('Skills', 1) + col('Legacy Skin', 1))
for r in g['Tier List']:
    heroes |= {v['t'] for k, v in r.items() if int(k) >= 3}
keep = set(heroes)
for c in (12, 13, 16, 17, 20, 21): keep |= set(col('SBW Options', c))
for c in (4, 7): keep |= set(col('Legacy Skin', c))
for c in (4, 6, 8): keep |= {t for t in col('Skills', c) if not t.startswith(('Note', 'Priest'))}
keep |= {'Palm Sweep', 'Palm Barrage', 'Ying Yang Barrage', 'Tides of the Far Shore', 'Palm Laser', 'Hellfire', 'Yellow Emperor'}

texts = []
def add(t):
    t = t.strip()
    if t and re.search('[A-Za-z]{2}', t) and t not in keep and not re.fullmatch(r'[A-Z][a-z]*\+*|[A-Z]{2,4}\+*|C\d+H?|C\d+-\d|Raid\d|FoRS|#REF!|#N/A', t):
        texts.append(t)

for name, rows in g.items():
    if name in ('SP',): continue
    for r in rows:
        for c, v in r.items():
            if name == 'Glossary' and c == '0': continue  # thuật ngữ viết tắt giữ nguyên
            add(v['t'])
# comment ô + cột ẩn + 2 tab ẩn hữu ích
for n in ('SBW Options', 'DPS', 'Challenge Stat', 'TL'):
    for row in wb[n].iter_rows():
        for c in row:
            if c.comment: add(c.comment.text)
wbv = openpyxl.load_workbook('raw/sheet.xlsx', data_only=True)
for r in wbv['DPS'].iter_rows(min_row=3, values_only=True):
    if r[18]: add(str(r[18]))
for n in ('Sigil Set', 'Equip'):
    for r in wbv[n].iter_rows(values_only=True):
        for v in r:
            if isinstance(v, str) and '☆' not in v and v not in keep: add(v)

uniq = list(dict.fromkeys(texts))
os.makedirs('raw/tr', exist_ok=True)
json.dump(sorted(keep), open('raw/keep.json', 'w', encoding='utf-8'), ensure_ascii=False)
batches, cur, size = [], {}, 0
for i, t in enumerate(uniq):
    cur[str(i)] = t; size += len(t)
    if size > 22000: batches.append(cur); cur, size = {}, 0
if cur: batches.append(cur)
for i, b in enumerate(batches):
    json.dump(b, open(f'raw/tr/in_{i:02d}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(uniq), sum(map(len, uniq)), 'chars', len(batches), 'batches')
