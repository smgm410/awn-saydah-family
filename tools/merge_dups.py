"""One-off: merge old story items into the Documents-page card that is the same record.
Each old item keeps its document number as an anchor (<span id="item-N">) on the card, its pictures are added to the card,
and its printed source line is kept under the card text. Pairs were checked by comparing dates and pictures (17 Nov 2026)."""
import re, sys
P = 'src/documents_page.html'
PAIRS = {128: 'nyt-2001-evelyn-deschner-notice', 77: 'caravan-1954-eli-evelyn-married', 94: 'census-1900-negaunee',
         26: 'helen-census-1920-1930', 89: 'helen-census-1920-1930', 5: 'census-1940-both-single', 27: 'census-1940-both-single',
         25: 'deed-index-1916-ellen-irwin', 38: 'eagle-1932-hamilton-graduates', 45: 'sympathy-note-1969', 46: 'syramar-1975-helen-awn',
         48: 'pilsudski-cruise-1937', 64: 'mitchell-deed-index-1947', 65: 'panam-manifest-1947-john', 87: 'census-1940-zrake-brooklyn',
         93: 'merhige-1940-census', 111: 'deed-index-1947-anthony', 124: 'specialty-shop-goods-ads', 145: 'eagle-1919-01-11-reargument'}
D = open(P, encoding='utf-8').read()
for n, cid in PAIRS.items():
    m = re.search(r'<article class="rec"[^>]*id="item-%d"[^>]*>.*?</article>' % n, D, re.S)
    assert m, n
    art = m.group(0)
    pics = re.search(r'<div class="pics">(.*?)</div>', art, re.S)
    src = re.search(r'<em>(Source:.*?)</em>', art, re.S)
    D = D.replace(art, '', 1)
    c = re.search(r'(<article class="rec"[^>]*id="%s"[^>]*>)(.*?)(</article>)' % re.escape(cid), D, re.S)
    assert c, cid
    head, body, tail = c.group(1), c.group(2), c.group(3)
    head = re.sub(r'data-pic="\d"', 'data-pic="1"', head)
    body = body.replace('<div class="tx">', '<div class="tx"><span id="item-%d"></span>' % n, 1)
    if pics:
        if '<div class="pics">' in body:
            body = body.replace('</div></div>', '', 0)
            k = body.rindex('</div></div>') if body.rstrip().endswith('</div></div>') else None
            body = re.sub(r'(<div class="pics">.*?)(</div>)(</div>\s*)$', lambda mm: mm.group(1) + pics.group(1) + mm.group(2) + mm.group(3), body, count=1, flags=re.S)
        else:
            body = re.sub(r'</div>\s*$', '<div class="pics">%s</div></div>' % pics.group(1), body, count=1)
    if src and 'Source' not in body:
        body = re.sub(r'(<p class="kind">.*?</p>)', r'\1<p class="srcline"><em>%s</em></p>' % src.group(1).replace('\\', '\\\\'), body, count=1, flags=re.S) if '<p class="kind">' in body else body
    D = D.replace(c.group(0), head + body + tail, 1)
n_left = len(re.findall(r'<article class="rec"[^>]*id="item-\d+"', D[D.index('id="box-story"'):]))
D = re.sub(r'(<summary>Pictures from the story <span class="meta">)\d+ items', r'\g<1>%d items' % n_left, D)
open(P, 'w', encoding='utf-8').write(D)
print('merged', len(PAIRS), 'left in closing box', n_left)
