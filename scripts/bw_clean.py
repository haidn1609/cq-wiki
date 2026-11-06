# Làm sạch wikitext BWiki (trường của {{勇士测评}}) thành văn bản thuần, thay icon hero bằng tên EN
import json, re, html

N = json.load(open('raw2/names.json', encoding='utf-8'))
NICK, PAGE2EN = N['nick'], N['page2en']

def en(name):
    name = name.strip().replace(' icon', '')
    return NICK.get(name) or PAGE2EN.get(name)

def icon(m):
    parts = [p for p in re.split('[，,、]', m.group(1)) if p.strip()]
    out = [(e and f'[[{e}]]') or p.strip() for p, e in ((p, en(p)) for p in parts)]
    return '、'.join(out)

def clean(s):
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    s = re.sub(r'\{\{#(?:css|vardefine|arraydefine|info)[^{}]*(?:\{\{[^{}]*\}\}[^{}]*)*\}\}', '', s, flags=re.S)
    s = re.sub(r'<bstyle>.*?</bstyle>', '', s, flags=re.S)
    s = re.sub(r'\{\{等待加强[^{}]*\}\}', '', s)
    s = re.sub(r'\{\{图标2?\|([^|}]+)[^{}]*\}\}', icon, s)
    for _ in range(3):  # template lồng nhau
        s = re.sub(r'\{\{(?:字体样式|缩写|纠正)\|([^|{}]*)[^{}]*\}\}', r'\1', s)
    s = re.sub(r'\{\{#show:([^|}]+)[^{}]*\}\}', lambda m: f'[[{en(m.group(1)) or m.group(1)}]]', s)
    s = re.sub(r'\{\{[^{}]*\}\}', '', s)  # template còn lại (biểu thức tính...) bỏ
    s = re.sub(r'\[\[(?:文件|File):[^\]]*\]\]', '', s)
    s = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', s)
    s = re.sub(r'\[\[([^\]]+)\]\]', lambda m: f'[[{en(m.group(1)) or m.group(1)}]]' if '[' not in m.group(1) else m.group(0), s)
    s = re.sub(r'</t[dh]>\s*<t[dh][^>]*>', ' | ', s)
    s = re.sub(r'<br\s*/?>|</tr>|</p>|</div>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = s.replace("'''", '**').replace("''", '')
    s = re.sub(r'#(物伤|魔伤|真伤|中立伤害)', r' \1', s)
    s = html.unescape(s)
    s = re.sub(r'[ \t]+\n', '\n', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()

if __name__ == '__main__':
    assert clean("{{图标|虎神}} và {{字体样式|ABC|粗体=是}}<br>'''x'''") .startswith('[[')
    print(clean("{{图标|拉尼}}可以更换为{{图标|兔子}}。<br>'''撕开'''（消块）造成2×500%攻击#物伤"))
