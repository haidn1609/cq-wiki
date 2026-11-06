# Dữ liệu chi tiết sigil + set từ BWiki -> raw2/sigils.json (đã Việt hóa)
import json, re

P = json.load(open('raw2/bw_sigil_pages.json', encoding='utf-8'))      # trang sigil (tên ZH)
S = json.load(open('raw2/bw_set_pages.json', encoding='utf-8'))        # trang set (tên ZH)
ZH = json.load(open('raw/sigil_zh.json', encoding='utf-8'))            # EN -> ZH
SRC = json.load(open('raw2/tr/sigil_in.json', encoding='utf-8'))
MAN = json.load(open('raw2/tr/sigil_out_manual.json', encoding='utf-8'))
TR = {SRC[k]: v for k, v in MAN.items()}
EN = {v: k for k, v in ZH.items()}                                     # ZH -> EN

STAT = [('物理穿透', 'Apen'), ('魔法穿透', 'Rpen'), ('物理防御', 'Arm'), ('魔法防御', 'Res'), ('攻击力', 'Atk'),
        ('暴击伤害量', 'CD'), ('暴击伤害', 'CD'), ('暴击抵抗', 'CR'), ('暴击率', 'CC'), ('暴击', 'CC'),
        ('伤害减少量', 'DR'), ('被害减少量', 'DR'), ('承伤降低', 'DR'), ('最大体力', 'HP'), ('体力上限', 'HP'),
        ('体力', 'HP'), ('命中率', 'Acc'), ('命中', 'Acc'), ('回避率', 'Eva'), ('回避', 'Eva'), ('吸血率', 'LS')]

def stats(s):
    """'物理穿透+1750,暴击率+11%' -> 'Apen +1750, CC +11%' (dòng có mô tả dài thì dùng bản dịch tay)."""
    s = (s or '').strip()
    if s in TR: return TR[s]
    for zh, en in STAT: s = s.replace(zh, en + ' ')
    s = re.sub(r'\s*\+\s*', ' +', s)
    return re.sub(r'\s*[,，]\s*', ', ', s).strip()

def t(s):
    s = (s or '').strip()
    return TR.get(s, s)

def field(w, k):
    return (re.search(rf'^\|{k}=(.*)$', w, re.M) or [0, ''])[1].strip()

sets = {}
for zh, w in S.items():
    a, b = field(w, '符文1'), field(w, '符文2')
    sets[zh] = {'name': t(zh), 'star': field(w, '星级'), 'grade': t(field(w, '品级')),
                'pieces': [EN.get(a, a), EN.get(b, b)], 'bonus': stats(field(w, '属性')), 'full': stats(field(w, '整套属性'))}

out = {}
for en, zh in ZH.items():
    f = P.get(zh)
    if not f: continue
    st = f.get('套装', '').strip()
    out[en] = {'zh': zh, 'desc': t(f.get('介绍')), 'type': t(f.get('类型')), 'grade': t(f.get('品级')), 'star': f.get('星级', '').strip(),
               'stats': stats(f.get('属性')), 'drop': [t(x) for x in [f.get('来源', '').strip()] if x],
               'set': sets.get(st), 'price': f.get('售价', '').strip(),
               'src': 'https://wiki.biligame.com/cq/' + __import__('urllib.parse').parse.quote(zh)}
json.dump(out, open('raw2/sigils.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    assert stats('物理穿透+1750,暴击率+11%') == 'Apen +1750, CC +11%', stats('物理穿透+1750,暴击率+11%')
    left = [(k, v) for k, v in out.items() for x in (v['desc'], v['stats'], *v['drop'], (v['set'] or {}).get('full', ''), (v['set'] or {}).get('name', '')) if re.search('[一-鿿]', x)]
    print(len(out), 'sigils | còn chữ Hán:', left[:5])
