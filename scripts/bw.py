# Client nhỏ cho API BWiki (wiki.biligame.com/cq) có giãn cách + retry khi bị rate-limit
import json, time, urllib.request, urllib.parse
def api(**q):
    q = {'format': 'json', **q}
    url = 'https://wiki.biligame.com/cq/api.php?' + urllib.parse.urlencode(q)
    for i in range(6):
        try:
            time.sleep(3.0)
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 cq-wiki-vi'}), timeout=120))
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503, 567): raise
            time.sleep(60 * (i + 1))
    raise RuntimeError('rate limited: ' + url)
