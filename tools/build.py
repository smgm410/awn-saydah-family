#!/usr/bin/env python3
"""Builds the multi-page site from src/site.html (the single content file).

Edit src/site.html (the story, captions, timeline) and run:  python3 tools/build.py
It writes index.html, part-one.html, part-two.html, part-three.html, descendants.html,
documents.html, people.html, journey.html, researchers.html, search.html,
site.css, site.js, search-index.json. Commit the generated files too (Netlify serves the repo as is).
"""
import re, json, html, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SRC = open('src/site.html', encoding='utf8').read()
UPDATED = '12 November 2026'

def esc(s): return html.escape(s, quote=True)
def plain(s):
    s = re.sub(r'<template.*?</template>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()

# ---------------------------------------------------------------- split the source
css = SRC[SRC.find('<style') + 7:SRC.find('</style>')]
hero_stats = re.search(r'<div class="stats">.*?</div></div>\s*</div></header>', SRC, re.S)
main = SRC[SRC.find('<main>') + 6:SRC.find('</main>')]
h2s = [(m.start(), m.group(1)) for m in re.finditer(r'<h2 id="([^"]+)"', main)]
def cut(start_id, end_id=None):
    s = dict((i, p) for p, i in h2s)[start_id]
    e = dict((i, p) for p, i in h2s)[end_id] if end_id else len(main)
    return main[s:e]
ID = {  # h2 ids in the source
    'glance': 'the-family-at-a-glance', 'one': 'part-one-the-aoun-awn-family-from-damour',
    'two': 'part-two-the-saydah-family-from-forzul-t', 'three': 'part-three-anthony-and-helen',
    'desc': 'the-descendants-of-anthony-and-helen', 'rec': 'records-cited-but-not-pictured',
    'dead': 'dead-ends-and-ruled-out-records', 'still': 'still-searching', 'src': 'sources', 'share': 'share'}
pre = main[:h2s[0][0]]                       # lead, note, how to read, etc.
glance = cut(ID['glance'], ID['one'])
part1 = cut(ID['one'], ID['two']); part2 = cut(ID['two'], ID['three']); part3 = cut(ID['three'], ID['desc'])
descs = cut(ID['desc'], ID['rec'])
researchers = cut(ID['rec'], ID['share'])
share = cut(ID['share'])
trailer = ''  # nothing after share

# the old chip tree is replaced
ti = glance.find('<h3 class="tl-h" id="family-tree">')
glance_timeline = glance[:ti]
old_tree = glance[ti:]
CHIPS = {}
for m in re.finditer(r'<a class="pn ?(me)?" href="([^"]+)"><b>(.*?)</b>(?:<span>(.*?)</span>)?</a>', old_tree):
    CHIPS[(m.group(3))] = dict(me=bool(m.group(1)), href=m.group(2), name=m.group(3), sub=m.group(4) or '')

# ---------------------------------------------------------------- page registry
PAGES = [  # file, nav label, title
    ('index.html', 'Home', None),
    ('part-one.html', 'Part One: Aoun (Awn)', 'Part One'),
    ('part-two.html', 'Part Two: Saydah', 'Part Two'),
    ('part-three.html', 'Part Three: Anthony and Helen', 'Part Three'),
    ('descendants.html', 'Descendants', 'Descendants'),
    ('documents.html', 'All documents', 'Documents'),
    ('people.html', 'People', 'People'),
    ('journey.html', 'Map', 'Map'),
    ('researchers.html', 'For researchers', 'For researchers'),
    ('search.html', 'Search', 'Search'),
]
NAVSHORT = {'index.html': 'Home', 'part-one.html': 'Part One', 'part-two.html': 'Part Two',
            'part-three.html': 'Part Three', 'descendants.html': 'Descendants', 'documents.html': 'Documents',
            'people.html': 'People', 'journey.html': 'Map', 'researchers.html': 'Researchers', 'search.html': 'Search'}

CONTENT = {}   # file -> html body of main
CONTENT['index.html'] = None  # built later
CONTENT['part-one.html'] = part1
CONTENT['part-two.html'] = part2
CONTENT['part-three.html'] = part3
CONTENT['descendants.html'] = descs
CONTENT['researchers.html'] = researchers

# which page owns which id (home owns glance, tree, share, start)
idpage = {}
def reg(file, body):
    for m in re.finditer(r'\sid="([^"]+)"', body):
        i = m.group(1)
        if i.startswith('item-'): continue
        idpage.setdefault(i, file)
for f in ('part-one.html', 'part-two.html', 'part-three.html', 'descendants.html', 'researchers.html'):
    reg(f, CONTENT[f])
reg('index.html', glance_timeline + share + pre)
for i in ('family-tree', 'start-here', 'whats-new', 'how-to-read', 'share', 'top'): idpage[i] = 'index.html'
idpage['the-family-at-a-glance'] = 'index.html'

def relink(body, cur):
    def f(m):
        i = m.group(1)
        if i == 'top': return m.group(0)
        pg = idpage.get(i)
        if pg and pg != cur: return 'href="%s#%s"' % (pg, i)
        return m.group(0)
    return re.sub(r'href="#([^"]*)"', f, body)

# ---------------------------------------------------------------- shared head / nav
def sitenav(cur):
    out = []
    for f, label, _ in PAGES:
        cls = ' aria-current="page"' if f == cur else ''
        out.append('<a href="%s"%s>%s</a>' % (f, cls, NAVSHORT[f]))
    out.append('<button type="button" class="bigtext" aria-pressed="false">Larger text</button>')
    return '<nav class="sitenav" aria-label="Site">' + ''.join(out) + '</nav>'

SEARCHFORM = ('<form class="sitesearch" action="search.html" method="get" role="search">'
              '<input type="search" name="q" placeholder="Search names, places, records" aria-label="Search the site" autocomplete="off">'
              '<button type="submit">Search</button></form>')

def hero(cur, title, sub):
    if cur == 'index.html':
        return ('<header class="hero"><div class="hero-in"><div class="kick">A family history</div>'
                '<h1>The Awn and Saydah Families: From Damour and Forzul to Brooklyn</h1>'
                '<p class="for">The story of our family, with the records behind it</p>' + SEARCHFORM + sitenav(cur) +
                '<div class="stats"><div><b>1869 to 2000</b><span>131 years of records</span></div>'
                '<div><b>2 villages</b><span>Damour and Forzul, Lebanon</span></div>'
                '<div><b>%d documents</b><span>shown beside the story</span></div></div></div></header>' % NDOCS)
    return ('<header class="hero slim"><div class="hero-in"><a class="kick" href="index.html">The Awn and Saydah families</a>'
            '<h1>%s</h1>%s' % (title, ('<p class="for">%s</p>' % sub if sub else '')) + SEARCHFORM + sitenav(cur) + '</div></header>')

def rail(cur, local):
    r = ['<button class="rail-x" id="railx" type="button" aria-label="Close contents">Close ✕</button>',
         '<a class="share-link" href="index.html#share">Share a memory or photo</a>',
         '<p class="rail-h">The site</p>']
    for f, label, _ in PAGES:
        r.append('<a class="l2%s" href="%s">%s</a>' % (' cur' if f == cur else '', f, esc(label)))
    if local:
        r.append('<p class="rail-h" style="margin-top:22px">On this page</p>')
        r.append(local)
    r.append('<a class="totop" href="#top" style="margin-top:18px">↑ Back to the top</a>')
    return '<nav class="rail" id="rail" aria-label="Contents">' + ''.join(r) + '</nav>'

def local_toc(body):
    out = []
    for m in re.finditer(r'<h([23])[^>]*?id="([^"]+)"[^>]*>(.*?)</h\1>', body, re.S):
        lv, i, t = m.group(1), m.group(2), m.group(3)
        t = re.sub(r'<span class="eyebrow">.*?</span>', '', t, flags=re.S)
        t = plain(t)
        out.append('<a class="l%s" href="#%s">%s</a>' % ('2' if lv == '2' else '3', i, esc(t)))
    return ''.join(out)

AR = re.compile(r'[\u0600-\u06FF\u0750-\u077F][\u0600-\u06FF\u0750-\u077F\s\u060C\u061B\u061F.\-]*[\u0600-\u06FF\u0750-\u077F]|[\u0600-\u06FF\u0750-\u077F]')
def arabic(h):
    parts = re.split(r'(<[^>]+>)', h)
    out = []; skip = False
    for p in parts:
        if p.startswith('<'):
            low = p.lower()
            if low.startswith(('<script', '<style')): skip = True
            elif low.startswith(('</script', '</style')): skip = False
            out.append(p)
        elif skip:
            out.append(p)
        else:
            out.append(AR.sub(lambda m: '<span lang="ar" dir="rtl">%s</span>' % m.group(0), p))
    return ''.join(out)

def doc(cur, title, desc, hero_title, hero_sub, body, local=None, extra_head='', extra_js=''):
    body = relink(body, cur)
    loc = local if local is not None else local_toc(body)
    loc = relink(loc, cur)
    return arabic('<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><meta name="description" content="%s">' % (esc(title), esc(desc)) + HEAD_EXTRA % (esc(title), esc(desc)) + FONTS +
            '<link rel="stylesheet" href="site.css">' + extra_head + '</head><body id="top"><a class="skip" href="#main">Skip to the story</a>' +
            hero(cur, hero_title, hero_sub) +
            '<div class="bar"><button id="menu" aria-expanded="false" aria-controls="rail">Menu</button>'
            '<a class="bar-title" href="index.html">Awn and Saydah family history</a><a href="search.html">Search</a></div>'
            '<div class="shell"><div class="scrim" id="scrim"></div>' + rail(cur, loc) + '<main id="main">' + body + '</main></div>'
            '<footer>Built from the family research files. Alien registration and Social Security numbers are hidden on the images. '
            'Last updated ' + UPDATED + '. <button type="button" class="bigtext" aria-pressed="false">Larger text</button></footer><button id="up" aria-label="Back to the top" type="button">↑</button>'
            '<div id="lb" role="dialog" aria-modal="true" aria-label="Document viewer"><div class="tb"><span class="ct"></span>'
            '<button class="pv">‹ Previous</button><button class="nx">Next ›</button><button class="x">Close</button></div><div class="box"></div></div>'
            '<script src="site.js"></script>' + extra_js + '</body></html>')

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,650&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Sans:wght@500;600&display=swap" rel="stylesheet">')

# ---------------------------------------------------------------- figures (for gallery and counts)
FIG_RE = re.compile(r'<figure class="doc" id="item-(\d+)">.*?</figure>', re.S)
NDOCS = len(set(re.findall(r'<figure class="doc" id="item-(\d+)"', main)))

def figs_with_context(file, body):
    """yield (num, figure_html, section_title) using nearest preceding h3/h2"""
    heads = [(m.start(), plain(re.sub(r'<span class="eyebrow">.*?</span>', '', m.group(2), flags=re.S)), m.group(1))
             for m in re.finditer(r'<h([23])[^>]*>(.*?)</h\1>', body, re.S)]
    for m in FIG_RE.finditer(body):
        t = ''
        for pos, txt, lv in heads:
            if pos < m.start(): t = txt
        yield int(m.group(1)), m.group(0), t

# ---------------------------------------------------------------- family tree
def chip(name, tag='a', extra=''):
    c = CHIPS[name]
    me = ' me' if c['me'] else ''
    return ('<a class="pn%s" href="%s"%s><b>%s</b>%s</a>' % (me, c['href'], extra, c['name'], ('<span>%s</span>' % c['sub']) if c['sub'] else ''))

def box(name, sub, href, cls='', style=''):
    return '<a class="pn %s" href="%s" style="%s"><b>%s</b>%s</a>' % (cls, href, style, name, ('<span>%s</span>' % sub) if sub else '')

def ped():
    A = 'a'; S = 's'
    cells = []
    def put(content, col, r1, r2, cls):
        cells.append('<div class="pc %s" style="grid-column:%d;grid-row:%d/%d">%s</div>' % (cls, col, r1, r2, content))
    def br(col, r1, r2, cls):
        cells.append('<div class="br %s" style="grid-column:%d;grid-row:%d/%d"></div>' % (cls, col, r1, r2))
    put(box('Boutros (Peter) Aoun', "Joseph's father", '#joseph-and-assin-aoun'), 1, 1, 2, A)
    put(box('Teresa', "Joseph's mother", '#joseph-and-assin-aoun'), 1, 2, 3, A)
    put(box('Joseph Segen', "Assin's father (Probable)", '#p-assin'), 1, 3, 4, A)
    put(box('Susanne', "Assin's mother (Probable)", '#p-assin'), 1, 4, 5, A)
    put(box('Wahbeh Saydah', "Antoon's father", '#anton-s-brothers-and-sisters'), 1, 5, 6, S)
    put(box('Noor', "Antoon's mother", '#anton-s-brothers-and-sisters'), 1, 6, 7, S)
    put(box('Hanna (John) Hadad', "Wassela's father · died 1913", '#p-hanna'), 1, 7, 8, S)
    put(box('Amina Shehadi', "Wassela's mother", '#p-wparents'), 1, 8, 9, S)
    for i, (r1, r2, c) in enumerate([(1, 3, A), (3, 5, A), (5, 7, S), (7, 9, S)]): br(2, r1, r2, c)
    put(box('Joseph (Youseuf) Aoun', '1869 – 1932', '#joseph-and-assin-aoun'), 3, 1, 3, A)
    put(box('Assin', 'died 1935', '#p-assin'), 3, 3, 5, A)
    put(box('Antoon (Anton) Saydah', '1880 or 1881 – 1949', '#anton-arrives-1898'), 3, 5, 7, S)
    put(box('Wassela Hadad', 'born 1886–93 · died about 1969', '#anton-and-wassela'), 3, 7, 9, S)
    br(4, 1, 5, A); br(4, 5, 9, S)
    put(box('Anthony J. Awn', '1914 – 1966 · Helen’s husband', '#anthony-a-citizen-and-a-shopkeeper', 'me'), 5, 1, 5, A)
    put(box('Helen Saydah', '1917 – 2000 · Anthony’s wife', '#helen', 'me'), 5, 5, 9, S)
    br(6, 1, 9, 'x')
    put('<a class="pn me kids" href="#five-children"><b>Their five children</b><span>Joseph, Jacqueline, Kathleen, Stephanie and Marie</span></a>', 7, 1, 9, 'kidsbox')
    lab = ('<div class="gl" style="grid-column:1;grid-row:1">Great-grandparents</div>')
    return '<div class="ped-wrap"><div class="ped">' + ''.join(cells) + '</div></div>'

def couple(a, b, wed):
    return '<div class="par">' + a + '<span class="wedl">%s</span>' % wed + b + '</div>'

def spine(chips):
    return '<ul class="spine">' + ''.join('<li>%s</li>' % c for c in chips) + '</ul>'

SPOUSES = [('Fred Gorayeb', 'born about 1889', 'fred-gorayeb', 'Husband of Mathilde'),
           ('Michael Koury', 'born 1906', 'michael-koury', 'Husband of Theresa'),
           ('Isabel Awn', '1916 – 2007', 'isabel', 'Wife of Elias'),
           ('Tirkman Saydah', 'died 1929', 'tirkman', 'Widow of Murad'),
           ('Eli Zrake', '1918 – 1958', 'eli-zrake', 'First husband of Evelyn'),
           ('Leonard F. Deschner', '1911 – 2003', 'leonard-deschner', 'Second husband of Evelyn'),
           ('George Michael Hakim', '1918 – 1996', 'george-hakim', 'Husband of Virginia')]

def branches():
    out = []
    out.append('<section class="branch a"><h4>Joseph and Assin’s nine children</h4>' + couple(box('Joseph (Youseuf) Aoun', '1869 – 1932', '#joseph-and-assin-aoun'), box('Assin', 'died 1935', '#p-assin'), 'married') +
               spine([chip(n) for n in ['Nassib (Nessil)', 'Mathilde (Matilda)', 'John', 'Theresa', 'George', 'Mitchell', 'Elias (Louis)', 'Anthony', 'Esther']]) + '</section>')
    out.append('<section class="branch s"><h4>Antoon and Wassela’s children</h4>' + couple(box('Antoon (Anton) Saydah', '1880 or 1881 – 1949', '#anton-arrives-1898'), box('Wassela Hadad', 'born 1886–93 · died about 1969', '#anton-and-wassela'), 'married 5 May 1912') +
               spine([chip(n) for n in ['Lily', 'Helen', 'Evelyn', 'Virginia']]) + '</section>')
    out.append('<section class="branch s"><h4>Antoon’s brothers and sisters</h4><p class="ft-par">Children of Wahbeh Saydah and Noor.</p>' +
               spine([chip(n) for n in ['Khaleel', 'Michael', 'Murad']] + [box('Antoon (Anton) Saydah', '1880 or 1881 – 1949', '#anton-arrives-1898')] + [chip(n) for n in ['Sa’da Kirkish', 'Nustas Kirkish']]) + '</section>')
    out.append('<section class="branch s"><h4>Wassela’s brothers</h4><p class="ft-par">Children of Hanna (John) Hadad and Amina Shehadi.</p>' +
               spine([chip(n) for n in ['Salim', 'Charles', 'Najib']]) + '</section>')
    out.append('<section class="branch a"><h4>Husbands and wives who joined the family</h4><p class="ft-par">Each name opens a short page.</p>' +
               spine([box(n, sub, 'person-%s.html' % sl) for n, sub, sl, note in SPOUSES]) + '</section>')
    return '<div class="branches">' + ''.join(out) + '</div>'

TREEMAP = {'Joseph (Youseuf) Aoun':'joseph-aoun','Assin':'assin','Nassib (Nessil)':'nassib','Mathilde (Matilda)':'mathilde','John':'john',
 'Theresa':'theresa','George':'george','Mitchell':'mitchell','Elias (Louis)':'elias','Esther':'esther','Anthony':'anthony','Anthony J. Awn':'anthony',
 'Helen':'helen','Helen Saydah':'helen','Antoon (Anton) Saydah':'antoon','Wassela Hadad':'wassela','Hanna (John) Hadad':'hanna-hadad',
 'Amina Shehadi':'amina','Lily':'lily','Evelyn':'evelyn','Virginia':'virginia','Khaleel':'khaleel','Michael':'michael-saydah','Murad':'murad',
 'Sa\u2019da Kirkish':'sada-kirkish','Nustas Kirkish':'nustas-kirkish'}
def _link_tree(h):
    def sub(m):
        slug = TREEMAP.get(m.group(3))
        if not slug: return m.group(0)
        return '%s href="person-%s.html"%s<b>%s</b>' % (m.group(1), slug, m.group(2), m.group(3))
    return re.sub(r'(<a class="pn[^"]*") href="[^"]+"([^>]*>)<b>(.*?)</b>', sub, h)

def tree_block():
    return _link_tree('<h3 class="tl-h" id="family-tree">Family tree</h3>'
            '<p class="tree-hint">Tap or click a name to open that person’s page, with dates, family and documents. Names without a page go to the story. Dates are the best we have; where records disagree, the story says so. '
            '<button type="button" class="btn sm alt" id="printtree">Print the tree</button></p>'
            '<div id="family-tree-wrap"><h4 class="ft-h">Four generations at a glance</h4><p class="swipe">Swipe sideways to see the whole chart.</p>' + ped() +
            '<h4 class="ft-h">Everyone we know of in each branch</h4>' + branches() + '</div>')

# ---------------------------------------------------------------- home
def build_home():
    start = ('<h2 id="start-here" class="plain">Start here</h2><p>New to the site? Pick the branch you want to follow, or look at the whole family at once.</p>'
             '<div class="cards">'
             '<a class="card a" href="part-one.html"><b>Anthony’s side</b><span>The Aouns (Awns) of Damour: Joseph and Assin and their nine children</span></a>'
             '<a class="card s" href="part-two.html"><b>Helen’s side</b><span>The Saydahs of Forzul and the Hadads of Zahle: Antoon and Wassela</span></a>'
             '<a class="card" href="part-three.html"><b>Anthony and Helen</b><span>Their wedding, their home and their five children</span></a>'
             '<a class="card" href="#family-tree"><b>The family tree</b><span>Four generations, with every branch we know of</span></a>'
             '<a class="card" href="documents.html"><b>All %d documents</b><span>Browse every record, grouped by the part of the story it belongs to</span></a>'
             '<a class="card" href="journey.html"><b>The journey map</b><span>Lebanon, Brooklyn and the places in between</span></a>'
             '</div>' % NDOCS)
    new = ('<h2 id="whats-new" class="plain">What’s new</h2><div class="new"><p class="new-d">Updated %s</p><ul>'
           '<li>18 more documents are shown in the story, so there are now %d: George’s funeral notice and grave, Anthony’s 1966 obituary, the 1913 shooting of Salim Hadad, Hanna Haddad’s death, the 1916 crash and its appeal, the 1941 wedding notices, and the death notices for Khaleel, Michael and Antoon.</li>'
           '<li>The site is now in several pages, with search, a branching family tree, a page of all documents, a people list and a journey map.</li>'
           '<li>“Records cited but not pictured” is grouped by family line, on the For researchers page.</li></ul></div>' % (UPDATED, NDOCS))
    how = pre
    # insert start/new after the note and rename howto heading id
    note_end = how.find('</aside>') + len('</aside>')
    how = how[:note_end] + start + new + how[note_end:]
    how = how.replace('<div class="howto"><p class="how-h">How to read it</p>', '<h2 id="how-to-read" class="plain">How to read it</h2><div class="howto">')
    how = how.replace('<li><p><b class="tag t-c">Confirmed</b>: a record shows it.</p></li>',
                      '<li><p><b class="tag t-c">Confirmed</b>: a record shows it. Example: Anthony died on 6 July 1966, shown in his obituary (document 137).</p></li>')
    how = how.replace('<li><p><b class="tag t-f">Family</b>: told to us, not yet found in a record.</p></li>',
                      '<li><p><b class="tag t-f">Family</b>: told to us, not yet found in a record. Example: the family name Aoun became Awn on arrival.</p></li>')
    how = how.replace('<li><p><b class="tag t-p">Probable</b>: it fits the records but is not proven.</p></li>',
                      '<li><p><b class="tag t-p">Probable</b>: it fits the records but is not proven. Example: that Nassib is the right spelling of Nessil.</p></li>')
    body = how + glance_timeline + tree_block() + (
        '<h3 class="tl-h" id="journey-link">Where it all happened</h3><p>See Lebanon, Brooklyn and the places in between on the <a href="journey.html">journey map</a>.</p>') + share
    return body

CONTENT['index.html'] = build_home()
reg('index.html', CONTENT['index.html'])

# ---------------------------------------------------------------- part pages: intro and pager
ORDER = ['index.html', 'part-one.html', 'part-two.html', 'part-three.html', 'descendants.html']
HEAD_EXTRA = ('<meta name="robots" content="noindex,nofollow">'
    '<link rel="icon" href="favicon.svg" type="image/svg+xml">'
    '<meta property="og:type" content="website"><meta property="og:site_name" content="Awn and Saydah Family History">'
    '<meta property="og:title" content="%s"><meta property="og:description" content="%s">'
    '<meta property="og:image" content="https://awnsaydah.com/og.png"><meta name="twitter:card" content="summary_large_image">')


def pager(cur):
    i = ORDER.index(cur); p = ORDER[i - 1] if i > 0 else None; n = ORDER[i + 1] if i + 1 < len(ORDER) else None
    lab = dict(zip(ORDER, ['Home', 'Part One: Aoun (Awn)', 'Part Two: Saydah', 'Part Three: Anthony and Helen', 'Descendants']))
    s = '<div class="pager">'
    if p: s += '<a class="prev" href="%s">← %s</a>' % (p, lab[p])
    if n: s += '<a class="next" href="%s">%s →</a>' % (n, lab[n])
    return s + '</div>'

INTRO = {
    'part-one.html': 'Joseph and Assin Aoun, their nine children and how the family reached Brooklyn.',
    'part-two.html': 'Antoon Saydah and Wassela Hadad, their daughters, and the Saydah and Hadad families.',
    'part-three.html': 'Anthony and Helen: the wedding, the shop, the home on 86th Street and their children.',
    'descendants.html': 'The children and grandchildren of Anthony and Helen.',
}

# ---------------------------------------------------------------- tree/people CSS etc are in EXTRA_CSS
EXTRA_CSS = open('tools/extra.css', encoding='utf8').read()
JS = open('tools/site.js', encoding='utf8').read()

# ---------------------------------------------------------------- documents page
def build_gallery():
    groups = []
    for f, label in (('part-one.html', 'Part One: the Aoun (Awn) family'), ('part-two.html', 'Part Two: the Saydah family'),
                     ('part-three.html', 'Part Three: Anthony and Helen')):
        body = CONTENT[f]
        secs = {}
        order = []
        for n, fig, t in figs_with_context(f, body):
            if t not in secs: secs[t] = []; order.append(t)
            secs[t].append((n, fig, f))
        groups.append((label, f, [(t, secs[t]) for t in order]))
    out = ['<p class="lead">Every document shown in the story, grouped by the part of the story it belongs to. Click a picture to see it large, with what it says. '
           'Records that cannot be pictured (index entries and the like) are listed on the <a href="researchers.html#records-cited-but-not-pictured">For researchers</a> page.</p>',
           '<div class="filters" role="group" aria-label="Filter documents"><button class="on" data-f="all">All</button><button data-f="p1">Aoun (Awn)</button>'
           '<button data-f="p2">Saydah</button><button data-f="p3">Anthony and Helen</button><button data-f="ar">Arabic pages</button></div>']
    total = 0
    for k, (label, f, secs) in enumerate(groups, 1):
        out.append('<h2 id="docs-%s" class="plain gal">%s</h2>' % (f[:-5], label))
        for t, items in secs:
            out.append('<h3 class="gal">%s</h3><aside class="docs gal-box"><div class="grid">' % esc(t))
            for n, fig, src in sorted(items):
                ar = ' ar' if 'native reader' in fig else ''
                fg = fig.replace('<figure class="doc" id="item-%d">' % n,
                                 '<figure class="doc g p%d%s" id="item-%d" data-story="%s#item-%d">' % (k, ar, n, src, n))
                out.append(fg); total += 1
            out.append('</div></aside>')
    return ''.join(out), total

# ---------------------------------------------------------------- people page
def build_people():
    def card(name, sub, href, note='', me=False):
        href = PERSONHREF.get(name, href)
        return '<a class="pn%s" href="%s"><b>%s</b>%s%s</a>' % (' me' if me else '', href, name, ('<span>%s</span>' % sub) if sub else '', ('<span class="rel">%s</span>' % note) if note else '')
    G = []
    def grp(title, cards, cls=''):
        G.append('<h3 class="gal">%s</h3><div class="people %s">%s</div>' % (title, cls, ''.join(cards)))
    c = lambda n, note: card(CHIPS[n]['name'], CHIPS[n]['sub'], CHIPS[n]['href'], note, CHIPS[n]['me'])
    grp('Anthony and Helen', [c('Anthony J. Awn', 'Married Helen Saydah, 29 December 1940'), c('Helen Saydah', 'Married Anthony Awn, 29 December 1940'),
                              card('Their five children', 'Joseph, Jacqueline, Kathleen, Stephanie and Marie', '#five-children', 'Children of Anthony and Helen')])
    grp('The Aoun (Awn) family of Damour',
        [card('Boutros (Peter) Aoun', '', '#joseph-and-assin-aoun', 'Father of Joseph'), card('Teresa', '', '#joseph-and-assin-aoun', 'Mother of Joseph'),
         c('Joseph (Youseuf) Aoun', 'Husband of Assin'), c('Assin', 'Wife of Joseph')] +
        [c(n, 'Child of Joseph and Assin') for n in ['Nassib (Nessil)', 'Mathilde (Matilda)', 'John', 'Theresa', 'George', 'Mitchell', 'Elias (Louis)', 'Anthony', 'Esther']], 'a')
    grp('The Saydah family of Forzul',
        [card('Wahbeh Saydah', '', '#anton-s-brothers-and-sisters', 'Father of Antoon and his brothers and sisters'), card('Noor', '', '#anton-s-brothers-and-sisters', 'Mother of Antoon'),
         c('Antoon (Anton) Saydah', 'Husband of Wassela')] +
        [c(n, 'Brother of Antoon') for n in ['Khaleel', 'Michael', 'Murad']] + [c(n, 'Sister of Antoon') for n in ['Sa’da Kirkish', 'Nustas Kirkish']], 's')
    grp('The Hadad family of Zahle',
        [card('Hanna (John) Hadad', 'died 1913', '#p-hanna', 'Father of Wassela'), card('Amina Shehadi', '', '#p-wparents', 'Mother of Wassela'),
         c('Wassela Hadad', 'Wife of Antoon')] + [c(n, 'Brother of Wassela') for n in ['Salim', 'Charles', 'Najib']], 's')
    grp('Antoon and Wassela’s children', [c(n, 'Child of Antoon and Wassela') for n in ['Lily', 'Helen', 'Evelyn', 'Virginia']], 's')
    grp('Spouses and in-laws', [card(n, sub, 'person-%s.html' % sl, note) for n, sub, sl, note in SPOUSES], 'a')
    return ('<p class="lead">Everyone who has a name in the family tree, with how they fit in. Names in bold lead to a short page for that person, with dates, family and documents. '
            'Living relatives are not listed.</p>' + ''.join(G)), G


# ---------------------------------------------------------------- person pages
sys.path.insert(0, 'tools')
import people_data
PEOPLE = people_data.PEOPLE
PBYSLUG = {p['slug']: p for p in PEOPLE}
PERSONHREF = {}
for _p in PEOPLE:
    for _n in _p['cards']: PERSONHREF[_n] = 'person-%s.html' % _p['slug']
TAGW = {'C': ('t-c', 'Confirmed'), 'F': ('t-f', 'Family'), 'P': ('t-p', 'Probable')}

def _items():
    info = {}
    for f in ('part-one.html', 'part-two.html', 'part-three.html'):
        for m in re.finditer(r'<figure class="doc" id="item-(\d+)">.*?aria-label="Open document \d+: (.*?)"><img[^>]*src="([^"]+)"', CONTENT[f], re.S):
            info[int(m.group(1))] = (html.unescape(m.group(2)), m.group(3))
    return info

def _section_items(hid):
    for f in ('part-one.html', 'part-two.html', 'part-three.html'):
        body = CONTENT[f]
        m = re.search(r'<h3 id="%s"' % re.escape(hid), body)
        if not m: continue
        n = re.search(r'<h[23] id=', body[m.end():])
        seg = body[m.start(): m.end() + (n.start() if n else len(body))]
        return [int(x) for x in re.findall(r'<figure class="doc" id="item-(\d+)"', seg)]
    return []

def build_person_pages():
    info = _items(); pages = {}; entries = []
    def link(m):
        s = m.group(1); q = PBYSLUG[s]
        return '<a href="person-%s.html">%s</a>' % (s, esc(q.get('short') or q['name']))
    for p in PEOPLE:
        rows = []
        for label, text, tag in p['rows']:
            t = re.sub(r'\{([a-z\-]+)\}', link, esc(text).replace('&#x27;', '’'))
            tg = ' <b class="tag %s">%s</b>' % TAGW[tag] if tag else ''
            rows.append('<div><dt>%s</dt><dd>%s%s</dd></div>' % (esc(label), t, tg))
        ids = []
        for d in p['docs']:
            ids += _section_items(d) if isinstance(d, str) else [d]
        seen = []; [seen.append(i) for i in ids if i not in seen and i in info]
        dg = ''.join('<a class="pdoc" href="documents.html#item-%d"><img loading="lazy" src="%s" alt=""><span><b>Document %d</b>%s</span></a>' % (i, info[i][1], i, esc(info[i][0])) for i in seen)
        pg, anchor = p['story']
        body = ('<p class="lead">%s</p>' % esc(p['brief']) +
                '<dl class="pfacts">%s</dl>' % ''.join(rows) +
                (('<p class="pspell"><b>Spellings in the records:</b> %s.</p>' % esc(p['spellings'])) if p['spellings'] else '') +
                '<p class="pgo"><a class="pbtn" href="%s#%s">Read the full story</a> <a class="pback" href="people.html">All the people</a></p>' % (pg, anchor) +
                (('<h3 class="gal">Documents about %s</h3><div class="pdocs">%s</div>' % (esc(p.get('short') or p['name']), dg)) if dg else '') +
                '<p class="pnote">Each fact carries its label: Confirmed (shown in a record), Family (told to us) or Probable (fits but unproven). Living relatives are not listed.</p>')
        f = 'person-%s.html' % p['slug']
        pages[f] = doc(f, '%s · Awn and Saydah Family History' % p['name'], p['brief'], p['name'], p['dates'], body, local='')
        txt = ' '.join([p['brief'], p['spellings']] + ['%s %s' % (a, re.sub(r'\{([a-z\-]+)\}', lambda m: PBYSLUG[m.group(1)]['name'], b)) for a, b, c in p['rows']])
        entries.append({'t': p['name'], 'u': f, 'x': txt[:2500], 'k': 'p'})
    return pages, entries

# ---------------------------------------------------------------- journey map page
def build_map():
    # Real geography (Natural Earth and US Census boundaries via world-atlas and us-atlas, public domain),
    # projected once by a script and stored in tools/map_paths.json; labels and points are placed on it.
    MP = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'map_paths.json')))
    def dot(x, y, cls, label, anchor='start', dx=12, dy=5, approx=False):
        tx = x + dx if anchor == 'start' else x - dx
        ring = ' approx' if approx else ''
        return ('<circle cx="%.1f" cy="%.1f" r="7" class="pt %s%s"/><text x="%.1f" y="%.1f" class="pl halo" text-anchor="%s">%s</text>'
                '<text x="%.1f" y="%.1f" class="pl" text-anchor="%s">%s</text>') % (x, y, cls, ring, tx, y + dy, anchor, label, tx, y + dy, anchor, label)
    def txt(x, y, label, cls='geo', anchor='start'):
        return '<text x="%.0f" y="%.0f" class="%s" text-anchor="%s">%s</text>' % (x, y, cls, anchor, label)
    L = MP['leb']; P = L['pts']; LB = L['lab']
    pts = [('Damour', 'The Aoun (Awn) family’s village', 'a'), ('Beirut', 'Port city', 'n'),
           ('Zahle', 'The Hadad family’s town (Wassela)', 's'), ('Forzul', 'The Saydah family’s village (position approximate)', 's')]
    svg1 = ['<svg class="mapsvg" viewBox="0 0 640 520" role="img" aria-label="Map of Lebanon with the coast, the border with Syria and Israel, and the villages Damour, Beirut, Zahle and approximately Forzul">',
            '<rect width="640" height="520" class="sea"/>', '<path d="%s" class="land"/>' % L['land'],
            '<path d="%s" class="lebfill"/>' % L['leb'], '<path d="%s" class="border"/>' % L['borders'],
            '<path d="%s" class="river"/>' % L['rivers'], '<path d="%s" class="coast"/>' % L['land'],
            txt(LB['sea'][0], LB['sea'][1], 'Mediterranean Sea'), txt(LB['leb'][0], LB['leb'][1], 'LEBANON', 'geo big', 'middle'), txt(LB['syria'][0], LB['syria'][1], 'SYRIA', 'geo big', 'middle')]
    for k, extra in (('Tripoli', 0), ('Sidon', 0), ('Baalbek', 0)):
        x, y = P[k]; svg1.append('<circle cx="%.1f" cy="%.1f" r="3.5" class="pt minor"/>' % (x, y) + txt(x + 8, y + 4, k, 'geo sm'))
    for n, d, c in pts:
        x, y = P[n]
        if n == 'Forzul':
            svg1.append(dot(x, y, c, 'Forzul (approx.)', 'start', 12, -12, True))
        elif n == 'Damour':
            svg1.append(dot(x, y, c, n, 'end', 12, 5))
        elif n == 'Beirut':
            svg1.append(dot(x, y, c, n, 'end', 12, 5))
        else:
            svg1.append(dot(x, y, c, n, 'start', 12, 18))
    svg1.append('</svg>')
    N = MP['ny']; NP = N['pts']; NL = N['lab']
    pts2 = [('Brooklyn', 'Where both families settled', 'b', 'start', 12, 5), ('Tuxedo Park', 'The 1916 crash', 'n', 'end', 12, 5),
            ('Tannersville', 'Summer 1945 in the mountains', 'n', 'end', 12, 5), ('Syracuse', 'Shehadi cousins; Hanna Hadad’s funeral', 's', 'start', 12, -10),
            ('Clifton Springs', 'Where Hanna Hadad spent his last months, 1913', 's', 'end', 12, 5)]
    svg2 = ['<svg class="mapsvg" viewBox="0 0 640 520" role="img" aria-label="Map of New York State with Lake Ontario, Lake Erie and Long Island, showing Brooklyn, Tuxedo Park, Tannersville, Syracuse and Clifton Springs">',
            '<rect width="640" height="520" class="sea"/>', '<path d="%s" class="land"/>' % N['land'], '<path d="%s" class="nyfill"/>' % N['ny'],
            '<path d="%s" class="lake"/>' % N['lakes'], '<path d="%s" class="river"/>' % N['rivers'],
            '<path d="%s" class="border"/>' % N['borders'],
            txt(NL['ont'][0], NL['ont'][1], 'Lake Ontario', 'geo', 'middle'), txt(NL['erie'][0], NL['erie'][1], 'Lake Erie', 'geo', 'middle'),
            txt(NL['atl'][0], NL['atl'][1], 'Atlantic Ocean', 'geo', 'end')]
    for n, d, c, anchor, dx, dy in pts2:
        x, y = NP[n]; svg2.append(dot(x, y, c, n, anchor, dx, dy))
    svg2.append('</svg>')
    lst1 = ''.join('<li><b>%s</b>: %s</li>' % (n, d) for n, d, c in pts)
    lst2 = ''.join('<li><b>%s</b>: %s</li>' % (n, d) for n, d, c, a, dx, dy in pts2)
    body = ('<p class="lead">The two families began in different parts of Lebanon and met again in Brooklyn. '
            'The coastlines, borders, lakes and rivers on these maps are real. The villages are placed from their coordinates, and Forzul’s position is only approximate.</p>'
            '<h2 id="map-lebanon" class="plain">Lebanon</h2>' + ''.join(svg1) + '<ul class="maplist">' + lst1 + '</ul>'
            '<h2 id="map-crossing" class="plain">The crossing</h2><p>Antoon Saydah came to New York in 1898 (the ship and the exact arrival date are still in question: see <a href="part-two.html#anton-arrives-1898">Antoon arrives, 1898</a>). '
            'Joseph and Assin’s family crossed in 1920 (<a href="part-one.html#the-crossing-1920">The crossing, 1920</a>). Anthony and Helen married in Brooklyn on 29 December 1940.</p>'
            '<h2 id="map-ny" class="plain">New York</h2>' + ''.join(svg2) + '<ul class="maplist">' + lst2 + '</ul>'
            '<p class="ft-par">Not on this map: Allendale, South Carolina, where the Brooklyn Eagle says Antoon died on 17 November 1949 (one Arabic paper says Columbia, South Carolina).</p>')
    return body

# ---------------------------------------------------------------- search index
def build_search_index():
    entries = []
    for f in ('index.html', 'part-one.html', 'part-two.html', 'part-three.html', 'descendants.html', 'researchers.html'):
        body = CONTENT[f]
        heads = [(m.start(), m.end(), m.group(1), re.sub(r'<span class="eyebrow">.*?</span>', '', m.group(3), flags=re.S), m.group(2))
                 for m in re.finditer(r'<h([23])[^>]*?id="([^"]+)"[^>]*>(.*?)</h\1>', body, re.S)]
        # shift order of groups (level, id, title)
        hs = [(s, e, plain(t), i) for s, e, lv, t, i in [(a, b, c, d, e2) for a, b, c, d, e2 in heads]]
        # fix tuple order above: heads = (start,end,level,title,id)
        for k, (s, e, lv, t, i) in enumerate(heads):
            nxt = heads[k + 1][0] if k + 1 < len(heads) else len(body)
            text = plain(body[e:nxt])
            if not text: continue
            entries.append({'t': plain(t), 'u': '%s#%s' % (f, i), 'x': text[:6000], 'k': 's'})
    for f in ('part-one.html', 'part-two.html', 'part-three.html'):
        for n, fig, t in figs_with_context(f, CONTENT[f]):
            title = plain(re.search(r'<figcaption>.*?<b>(.*?)</b>', fig, re.S).group(1))
            cap = plain(re.search(r'<div class="cap">(.*?)</div>', fig, re.S).group(1)) if '<div class="cap">' in fig else ''
            cap = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html.unescape(re.search(r'<template class="full">(.*?)</template>', fig, re.S).group(1))))
            cap = cap.strip()
            entries.append({'t': 'Document %d: %s' % (n, title), 'u': 'documents.html#item-%d' % n, 'x': cap[:2500], 'k': 'd'})
    return entries

# ---------------------------------------------------------------- write everything
def main_():
    global NDOCS
    gal_body, gal_total = build_gallery()
    assert gal_total == NDOCS, (gal_total, NDOCS)
    people_body, _ = build_people()
    person_pages, person_entries = build_person_pages()
    map_body = build_map()
    out = {}
    out['index.html'] = doc('index.html', 'Awn and Saydah Family History', 'The Awn and Saydah families, from Damour and Forzul in Lebanon to Brooklyn.', None, None, CONTENT['index.html'],
                            local=''.join('<a class="l2" href="#%s">%s</a>' % x for x in [('start-here', 'Start here'), ('whats-new', 'What’s new'), ('how-to-read', 'How to read it'),
                                                                                       ('the-family-at-a-glance', 'At a glance'), ('family-tree', 'Family tree'), ('share', 'Share something')]),
                            extra_js=SHAREJS)
    for f, label, title in PAGES[1:5]:
        body = CONTENT[f]
        intro = '<p class="lead">%s</p>' % INTRO[f]
        out[f] = doc(f, '%s · Awn and Saydah Family History' % label, INTRO[f], re.sub(r'<[^>]+>', '', re.search(r'<h2[^>]*>(.*?)</h2>', body, re.S).group(1).replace('<span class="eyebrow">', '').replace('</span>', ': ')).strip(': '),
                     None, intro + body + pager(f))
    out['documents.html'] = doc('documents.html', 'All documents · Awn and Saydah Family History', 'Every document in the family history, grouped by story.', 'All documents', '%d records, each beside the part of the story it belongs to' % NDOCS, gal_body)
    out['people.html'] = doc('people.html', 'People · Awn and Saydah Family History', 'The people in the family tree.', 'People', 'Who is who in the tree', people_body)
    out['journey.html'] = doc('journey.html', 'Map · Awn and Saydah Family History', 'Where the family lived.', 'The journey map', 'Lebanon, Brooklyn and the places in between', map_body)
    res_intro = ('<p class="lead">This page is for researchers and for relatives who want to check our work: the records we cite but could not picture, the dead ends, and what we are still searching for.</p>')
    out['researchers.html'] = doc('researchers.html', 'For researchers · Awn and Saydah Family History', 'Sources, dead ends and open questions.', 'For researchers', 'Sources, dead ends and what we are still searching for', res_intro + CONTENT['researchers.html'])
    srch = ('<p class="lead">Search the story and the document captions.</p><form class="sitesearch big" action="search.html" method="get" role="search"><input type="search" name="q" id="q" placeholder="Try: Hadad, Maloof, Damour, 1913" aria-label="Search the site" autocomplete="off"><button type="submit">Search</button></form>'
            '<p id="sres-status" class="hint" role="status"></p><ol id="sres" class="sres"></ol><noscript><p>Search needs JavaScript. Use the Contents links instead.</p></noscript>')
    out['search.html'] = doc('search.html', 'Search · Awn and Saydah Family History', 'Search the family history.', 'Search', 'Names, places, dates and records', srch,
                             local='', extra_js='<script src="search.js"></script>')
    out.update(person_pages)
    for f, t in out.items(): open(f, 'w', encoding='utf8').write(t)
    open('site.css', 'w', encoding='utf8').write(css.strip() + '\n' + EXTRA_CSS)
    open('site.js', 'w', encoding='utf8').write(JS)
    open('search.js', 'w', encoding='utf8').write(open('tools/search.js', encoding='utf8').read())
    idx = build_search_index() + person_entries
    json.dump(idx, open('search-index.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    print('pages', len(out), 'docs', NDOCS, 'search entries', len(idx))

SHAREJS = '<script>' + re.search(r'<script>\s*\(function\(\)\{var f=document.getElementById\(\'shareform\'\).*?</script>', SRC, re.S).group(0)[len('<script>'):]

main_()
