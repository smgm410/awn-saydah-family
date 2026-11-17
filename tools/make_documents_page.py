#!/usr/bin/env python3
"""One-off converter (17 Nov 2026): turns the approved Documents-page draft into src/documents_page.html and tools/docs_page.css.
Usage: python3 -I tools/make_documents_page.py <draft.html> <orbmap.json> <imgmap.json>
Arabic newspaper pages are text only (Sarah, 17 Nov 2026), except the George Aoun portrait crop."""
import re, sys, os, json, html, difflib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
draft = open(sys.argv[1], encoding='utf8').read()
orb = {int(k): v for k, v in json.load(open(sys.argv[2])).items()}
imgm = {int(k): v for k, v in json.load(open(sys.argv[3])).items()}
site = open('src/site.html', encoding='utf8').read()

# ---- body
b0 = draft.index('<h1>Documents page</h1>'); b1 = draft.index('<script>', b0)
body = draft[b0:b1]
body = body.replace('<h1>Documents page</h1>', '').replace('<h2 class="plain">All documents, organized by box</h2>', '')
def tofile(m):
    p = m.group(2); b = os.path.splitext(os.path.basename(p))[0] + '.jpg'
    return '%s="img/%s"' % (m.group(1), b)
body = re.sub(r'(src|href)="(\.\./[^"]+\.(?:jpg|png))"', tofile, body)
# thumbnails inside the picture strips
body = re.sub(r'<img ([^>]*?)src="img/([^"]+)\.jpg"', lambda m: '<img %ssrc="img/%s-t.jpg"' % (m.group(1), m.group(2)), body)
# ---- Arabic pages: text only, except the portrait crop
def strip_arabic(m):
    card = m.group(0)
    if 'data-kind="arabic"' not in card: return card
    keep = re.findall(r'<a [^>]*href="img/portrait_[^"]+"[^>]*>.*?</a>', card, re.S)
    card = re.sub(r'<div class="pics">.*?</div>', '<div class="pics">' + ''.join(keep) + '</div>' if keep else '', card, flags=re.S)
    card = card.replace('data-pic="1"', 'data-pic="%d"' % (1 if keep else 0))
    return card
body = re.sub(r'<article class="rec".*?</article>', strip_arabic, body, flags=re.S)

# ---- old item numbers -> cards
cards = {m.group(1): m.group(0) for m in re.finditer(r'<article class="rec"[^>]*?id="([^"]+)".*?</article>', body, re.S)}
def card_for_img(name):
    base = os.path.splitext(name)[0]
    for cid, c in cards.items():
        if 'img/%s.jpg' % base in c: return cid
old = {}
for m in re.finditer(r'<figure class="doc" id="item-(\d+)">(.*?)</figure>', site, re.S):
    n = int(m.group(1)); fg = m.group(2)
    t = html.unescape(re.search(r'aria-label="Open document \d+: (.*?)"', fg).group(1))
    imgs = [i for i in re.findall(r'(?:src|data-src)="(img/[^"]+)"', fg) if not i.endswith('-t.jpg')]
    cap = re.search(r'<div class="cap">(.*?)</div>', fg, re.S).group(1)
    alt = html.unescape(re.search(r'alt="([^"]*)"', fg).group(1))
    arabic = n in (135, 139, 141, 146, 147, 148, 149, 150, 151, 152, 159)
    old[n] = dict(title=t, imgs=imgs, cap=cap, alt=alt, ar=arabic)
anchor = {}   # card id -> [item numbers]
extras = []
report = []
for n, o in sorted(old.items()):
    cid = None
    if n in imgm: cid = card_for_img(imgm[n][1])
    elif n in orb and orb[n][0] >= 25: cid = card_for_img(orb[n][1])
    OVR = {135: 'B02-09', 139: 'B09-24', 141: 'B09-28', 146: 'B19-05', 147: 'B19-04', 148: 'B13-25', 149: 'B13-10', 150: 'B14-08', 151: 'B17-06', 152: 'B17-06', 159: 'B15-18'}
    if o['ar'] and n in OVR: cid = OVR[n]; report.append('ARABIC item %d -> %s' % (n, cid))
    elif cid is None and o['ar']:
        norm = lambda s: re.sub(r'[^a-z0-9]+', ' ', s.lower())
        best = max(cards, key=lambda c: difflib.SequenceMatcher(None, norm(o['title']), norm(re.search(r'<h4>(.*?)</h4>', cards[c], re.S).group(1))).ratio())
        cid = best; report.append('ARABIC item %d -> %s (%s)' % (n, best, re.search(r'<h4>(.*?)</h4>', cards[best], re.S).group(1)[:60]))
    if cid: anchor.setdefault(cid, []).append(n)
    else: extras.append(n)
for cid, ns in anchor.items():
    new = re.sub(r'(<article class="rec"[^>]*?id="%s"[^>]*>)' % re.escape(cid), lambda m: m.group(1) + ''.join('<span id="item-%d"></span>' % n for n in ns), cards[cid], count=1)
    body = body.replace(cards[cid], new, 1)
# ---- extras section: pictures shown in the story that have no card above
ex = ['<details class="box" id="box-story" open><summary>Pictures from the story <span class="meta">%d items</span></summary>' % len(extras),
      '<p class="explainer">These pictures are shown in the story and are not yet matched to a card in a box above. Each keeps its document number.</p><div class="recs">']
for n in extras:
    o = old[n]
    pics = ''.join('<a data-cap="%s" href="%s"><img alt="%s" loading="lazy" src="%s"/></a>' % (html.escape(o['title'], quote=True), i, html.escape(o['alt'], quote=True), i[:-4] + '-t.jpg') for i in o['imgs'])
    ex.append('<article class="rec" data-hold="0" data-id="item-%d" data-kind="record" data-open="0" data-pic="1" id="item-%d"><div class="tx"><h4>Document %d: %s</h4><div class="capt">%s</div><div class="pics">%s</div></div></article>'
              % (n, n, n, html.escape(o['title']), o['cap'], pics))
ex.append('</div></details>')
last = body.rindex('</details>') + len('</details>')
body = body[:last] + ''.join(ex) + body[last:]
open('src/documents_page.html', 'w', encoding='utf8').write(body.strip() + '\n')
# ---- css, scoped
css = draft[draft.index('<style>') + 7:draft.index('</style>')]
out = []
def scope(sel):
    parts = []
    for s in sel.split(','):
        s = s.strip()
        if s.startswith(':root') or s.startswith('body'): parts.append('#docs-page' + s[4:] if s.startswith('body') else s)
        elif s.startswith('main'): parts.append('#docs-page' + s[4:])
        else: parts.append('#docs-page ' + s)
    return ','.join(parts)
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
def rule(m):
    sel, bodyr = m.group(1), m.group(2)
    if sel.strip().startswith('@'): return m.group(0)
    return scope(sel) + '{' + bodyr + '}'
css2 = re.sub(r'([^{}@][^{}]*)\{([^{}]*)\}', rule, css)
css2 = css2.replace('dialog.lb', '#docs-page dialog.lb')
open('tools/docs_page.css', 'w', encoding='utf8').write(css2)
print('cards', len(cards), 'with anchors', len(anchor), 'extras', len(extras)); print('\n'.join(report))
