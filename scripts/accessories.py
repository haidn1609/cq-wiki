# Dòng chỉ số nhẫn (Manacar / Kurenai) + phụ kiện (khuyên tai, vòng cổ) từ BWiki -> raw2/acc.json (đã Việt hóa)
import json, re

P = json.load(open('raw2/bw_acc_pages.json', encoding='utf-8'))
ring_page, acc_page = P['戒指资料概览'], P['饰品属性']

STAT = [('（竞技场专用）', '(chỉ Arena) '), ('（剧情专用）', '(chỉ Story) '), ('物理伤害量', 'Sát thương vật lý'), ('魔法伤害量', 'Sát thương phép'),
        ('物理穿透', 'Apen'), ('魔法穿透', 'Rpen'), ('物理防御', 'Arm'), ('魔法防御', 'Res'), ('攻击力', 'Atk'), ('暴击伤害', 'CD'),
        ('暴击抵抗力', 'CR'), ('暴击率', 'CC'), ('伤害减少量', 'DR'), ('最大体力', 'HP'), ('攻击速度', 'AS'), ('回避率', 'Eva'),
        ('命中率', 'Acc'), ('吸血率', 'LS'), ('金币箱', 'Hộp vàng'), ('勇士团经验值获得量', 'EXP đoàn'), ('勇士经验值获得量', 'EXP hero')]
GROUP = {'攻击属性': 'Tấn công', '防御属性': 'Phòng thủ', '技能属性': 'Kỹ năng', '特殊属性': 'Đặc biệt'}

def st(s):
    for zh, vi in STAT: s = s.replace(zh, vi)
    s = s.replace('以体力', 'Hồi sinh 1 lần với ').replace('复活一次（复活后', ' HP (sau khi hồi sinh ').replace('秒无视所有伤害，无法重复使用复活效果）', 's miễn mọi sát thương, không dùng lại được)')
    return re.sub(r'\+\[', ' +[', s).replace('~', '–')

def rows(table):
    return [[c.strip() for c in r.split('||')] for r in re.findall(r'^\|(\[\[File:[^\n]*)$', table, re.M)]

def tables(section):
    return re.findall(r'\{\|class="wikitable sortable".*?\|\}', section, re.S)

mana, kure = ring_page.split('==红莲之力戒指==')[0], ring_page.split('==红莲之力戒指==')[1].split('==戒指与武器属性对照表==')[0]
icon = lambda c: (re.search(r'File:([^|\]]+)', c) or [0, ''])[1].strip()

def main_rows(t):
    return [{'icon': icon(r[0]), 'star': r[1].strip('★'), 'zh': r[2], 'stat': st(r[3])} for r in rows(t)]
def sub_rows(t):
    return [{'star': r[1].strip('★'), 'group': GROUP.get(r[2], r[2]), 'stat': st(r[3])} for r in rows(t)]

mt, kt = tables(mana), tables(kure)
data = {'ring': {'manacar': {'main': main_rows(mt[0]), 'sub': sub_rows(mt[1])},
                 'kurenai': {'main': main_rows(kt[0]), 'sub': sub_rows(kt[1])}}}

# Phụ kiện: "Tên--Mô tả {{饰品属性/等级|a//b//c//d//e}} ..." -> 5 cấp
LV = ['Thấp nhất', 'Thấp', 'Trung', 'Cao', 'Tối đa']
ACC = json.load(open('raw2/tr/acc_vi.json', encoding='utf-8'))  # tên + mẫu câu mô tả đã dịch tay
body = re.search(r'\{\{#arraymap:(.*?)\|；\|@data', acc_page, re.S).group(1)
acc = []
for item in [x.strip() for x in body.split('；') if x.strip()]:
    name, desc = item.split('--', 1)
    desc = re.sub(r'\{\{纠正\|(\d+)\|\d+\}\}', r'\1', desc)  # {{纠正|5|6}}: BWiki ghi chú sửa số, lấy số đầu
    vals = re.findall(r'\{\{饰品属性/等级\|([^}]*)\}\}', desc)
    vals = list(dict.fromkeys(vals))  # cùng 1 chuỗi giá trị lặp lại trong câu -> một placeholder
    levels = [[{'自身': 'bản thân', '我方': 'cả đội'}.get(x, x) for x in l] for l in zip(*[v.split('//') for v in vals])] if vals else []
    v = ACC[name]
    acc.append({'zh': name, 'name': v['name'], 'kind': v['kind'], 'desc': v['desc'],
                'levels': [list(l) for l in levels], 'fixedOnly': False})
data['acc'] = {'levels': LV, 'lines': acc,
               'note': ACC['_note']}
data['src'] = {'ring': 'https://wiki.biligame.com/cq/%E6%88%92%E6%8C%87%E8%B5%84%E6%96%99%E6%A6%82%E8%A7%88',
               'acc': 'https://wiki.biligame.com/cq/%E9%A5%B0%E5%93%81%E5%B1%9E%E6%80%A7'}
json.dump(data, open('raw2/acc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    assert st('物理穿透+[124~171]') == 'Apen +[124–171]'
    left = re.findall(r'[一-鿿]+', json.dumps({k: v for k, v in data.items() if k != 'src'}, ensure_ascii=False).replace('"zh": "', '"zh": "#'))
    print(len(data['ring']['manacar']['main']), len(data['ring']['manacar']['sub']), len(data['ring']['kurenai']['main']),
          len(data['ring']['kurenai']['sub']), len(acc), 'acc lines | còn chữ Hán ngoài trường zh/icon:',
          [x for x in left if x not in json.dumps([r['icon'] for k in ('manacar', 'kurenai') for r in data['ring'][k]['main']] + [a['zh'] for a in acc] + [r['zh'] for k in ('manacar', 'kurenai') for r in data['ring'][k]['main']], ensure_ascii=False)][:10])
