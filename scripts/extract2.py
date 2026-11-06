# Gom chuỗi cần dịch từ (1) sheet "Guide to Almost Everything" (EN) và (2) trang hero BWiki (ZH)
# -> raw2/tr/in_XX.json, mỗi batch ~ 20k ký tự
import json, re, os, sys
sys.path.insert(0, 'scripts')
from bw_clean import clean

keep = set(json.load(open('raw/keep.json', encoding='utf-8')))
g = json.load(open('raw2/grids.json', encoding='utf-8'))
F = json.load(open('raw2/bw_fields.json', encoding='utf-8'))
N = json.load(open('raw2/names.json', encoding='utf-8'))
old = {}
for f in os.listdir('raw/tr'):
    if f.startswith('in_'):
        old.update({v: 1 for v in json.load(open('raw/tr/' + f, encoding='utf-8')).values()})

texts = []
def add(t):
    t = (t or '').strip()
    if t and t not in old and t not in keep and re.search(r'[A-Za-z]{2}|[一-鿿]', t) \
            and not re.fullmatch(r'[A-Z][a-z]*\+*|[A-Z]{2,4}\+*|C\d+H?|#REF!|#N/A|[\d.,%/ +-]+', t):
        texts.append(t)

SKIP = {'Data', 'World Map'}
for name, rows in g.items():
    if name in SKIP: continue
    for r in rows:
        for c, v in r.items():
            if name == 'General Glossary' and c == '0': continue
            add(v['t'])

# BWiki: các trường văn bản (điểm số là số, không dịch)
TEXT_FIELDS = ['勇士评价', '技能说明', '竞技评分理由', 'EP5评分理由', 'EP6评分理由', '讨伐F4评分理由', '全力战评分理由',
               '技能推荐1理由', '技能推荐2理由', '技能推荐3理由', '技能推荐4理由', '技能推荐5理由',
               '戒指词条推荐', '饰品词条推荐', '推荐阵容搭配', '专武评价', '消块机制', '吃书推荐']
for p, f in F.items():
    if p not in N['page2en']: continue
    for k in TEXT_FIELDS:
        add(clean(f.get(k, '')))
    for line in f.get('词条符文推荐', '').split(';'):  # "slot1,slot2,ring,set,note,label"
        parts = [x.strip() for x in clean(line).split(',')]
        if len(parts) >= 5:
            add(','.join(parts[4:-1]) if len(parts) > 5 else parts[4]); add(parts[-1] if len(parts) > 5 else '')
            for x in parts[:4]: add(x)
    for t in re.split('[,，]', f.get('标签', '')): add(t)
    for i in range(1, 6): add(f.get(f'技能推荐{i}', ''))

uniq = list(dict.fromkeys(texts))
os.makedirs('raw2/tr', exist_ok=True)
batches, cur, size = [], {}, 0
for i, t in enumerate(uniq):
    cur[str(i)] = t; size += len(t)
    if size > 20000: batches.append(cur); cur, size = {}, 0
if cur: batches.append(cur)
for i, b in enumerate(batches):
    json.dump(b, open(f'raw2/tr/in_{i:02d}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(uniq), sum(map(len, uniq)), 'chars', len(batches), 'batches',
      'zh:', sum(1 for t in uniq if re.search(r'[一-鿿]', t)))
