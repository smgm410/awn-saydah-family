#!/usr/bin/env python3
"""check_site_vs_doc.py  -  pre-publish FLAGGER (not a judge).

Usage:  python3 -I tools/check_site_vs_doc.py <src/site.html> <doc_export.txt> [people_data.py]

This script only flags. It lists things written on the family website that it could not find
in the master research Doc export. A human must judge every flag: many are harmless (a spelling
variant, a date style, page furniture) and a few may be real mismatches. It never edits the site
or the Doc, and it cannot tell whether a site fact is right.

Checks:
  1. Full dates (20 January 1901, Jan 20 1901, 5-8 Mar 1913) not found as a date in the Doc.
  2. Four-digit years 1800-2026 not found in the Doc.
  3. Numbers of 3+ digits that look like certificate, petition, ED, sheet, lodge or street numbers.
  4. Street addresses (number + street name).
  5. Capitalised name tokens in the family tree, the descendants section and the people pages
     (tools/people_data.py, found next to this script or given as the 3rd argument).
  6. Site statements labelled with something other than Confirmed, Family or Probable.
  7. Links to a page or anchor that does not exist in the build.
Spelling variants are folded before comparing: Aoun/Awn/Owen/Aun; Saydah/Saida/Sayda/Smyda/
Sayyidah; Hadad/Haddad/Hodod/Hadel.
Exit code: 0 = nothing flagged, 1 = something flagged, 2 = could not run, 3 = PRIVACY FAIL (check 8; blocks publishing).
"""
import sys, os, re, html, ast, difflib
from collections import OrderedDict, defaultdict

# ---------------------------------------------------------------------------------------------
# PRIVACY BLOCKLIST (check 8, 'living-people surnames').  Site rule: "living relatives: first names only".
# LIVING_SURNAMES_BLOCKLIST comes from Doc bullet B11-53 (George M. Hakim death notices, The Record,
# 20 January 1996): the obituary index prints his living children as "Carol Giffen", "Michael Jimenez",
# "Gerald Jimenez" and "Joanne Jimenez". Their surnames (Giffen, Jimenez) differ from the family's own
# surnames, so they are blocked everywhere on the site. Deceased relatives' surnames (Saydah, Awn, Aoun,
# Hakim, Hadad ...) must NEVER be listed here.
LIVING_SURNAMES_BLOCKLIST = ['Giffen', 'Jimenez']
# Append any further living person's surname here (one place, no other edits needed).
EXTRA_LIVING_SURNAMES = []
# ---------------------------------------------------------------------------------------------

MONTHS = {'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3, 'april': 4, 'apr': 4,
          'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7, 'august': 8, 'aug': 8,
          'september': 9, 'sept': 9, 'sep': 9, 'october': 10, 'oct': 10, 'november': 11, 'nov': 11,
          'december': 12, 'dec': 12}
MON_RE = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sept?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?'
YEAR = r'(18\d\d|19\d\d|20[0-2]\d)'
DASH = r'\s*(?:–|—|-|to|and|&)\s*'
DATE_DMY = re.compile(r'\b(\d{1,2})(?:st|nd|rd|th)?(?:' + DASH + r'(\d{1,2})(?:st|nd|rd|th)?)?\s+(' + MON_RE + r')\s*,?\s+' + YEAR + r'\b')
DATE_MDY = re.compile(r'\b(' + MON_RE + r')\s+(\d{1,2})(?:st|nd|rd|th)?(?:' + DASH + r'(\d{1,2})(?:st|nd|rd|th)?)?\s*,?\s+' + YEAR + r'\b')
DATE_ISO = re.compile(r'\b(18\d\d|19\d\d|20[0-2]\d)-(\d\d)-(\d\d)\b')

VARIANTS = [('awn', r'aoun|awn|owen|aun'), ('saydah', r'saydah|saida|sayda|smyda|sayyidah'),
            ('hadad', r'hadad|haddad|hodod|hadel')]
STOP = set('''the a an and or of in on at to for from by with as is are was were be been it its this that these those
their there then than but not no yes he she his her him they them we our us you your who whom whose which what when where
why how all any each every both few more most other some such only own same so too very can will just if into over after
before about above below up down out off again further once here also tap click dates date best have has had see per
one two three four five six seven eight nine ten first second third part box record records still searching sources share
mr mrs miss dr st street avenue ave sts home page pages
january february march april may june july august september october november december
monday tuesday wednesday thursday friday saturday sunday confirmed family probable
brooklyn new york'''.split())
WEAK_LABELS = ['Possible', 'Uncertain', 'Unknown', 'Unverified', 'Unconfirmed', 'Likely', 'Rumored', 'Tentative',
               'Speculative', 'Disputed']
STREET_WORDS = r'(?:Street|St|Avenue|Ave|Place|Pl|Road|Rd|Boulevard|Blvd|Court|Ct|Lane|Drive|Dr|Terrace|Ter|Broadway|Parkway|Pkwy|Alley)'
ADDR = re.compile(r"\b(\d{1,5})\s+((?:[A-Z0-9][\w.'’-]*\s+){0,3}?" + STREET_WORDS + r")\b\.?")
NUM_CTX_BEFORE = re.compile(r'(?:certificate|cert\.?|petition|declaration|no\.?|number|#|ED|E\.D\.|enumeration district|sheet|'
                            r'page|p\.|pp\.|lodge|image|frame|line|volume|vol\.?|book|file|serial|license|permit|index|page)\s*(?:of\s+)?$', re.I)
ID_BEFORE = re.compile(r'(?:images?|memorial|ark|group|microfilm|collection|masthead)\s*(?:#|no\.?)?\s*(?:[\d,]+\s*(?:and|,|to)\s*)*$|\bimages?\s+[\d, and]+\s+of\s*$', re.I)
NUM_CTX_AFTER = re.compile(r'^\s*(?:,|\s)?\s*(?:ED|sheet|page|lodge)\b', re.I)


def norm_text(s):
    s = html.unescape(s).replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = s.replace('–', '-').replace('—', '-').replace(' ', ' ')
    s = s.lower()
    for canon, pat in VARIANTS:
        s = re.sub(r'\b(?:' + pat + r')(?=\b|s\b)', canon, s)
    return s


def strip_tags(s, keep_templates=True):
    s = re.sub(r'<(script|style)\b.*?</\1>', ' ', s, flags=re.S)
    if not keep_templates:
        s = re.sub(r'<template.*?</template>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


def dates_in(text):
    """Return list of (y, m, d, raw) found in text; day ranges expand to every day named."""
    out = []
    for m in DATE_DMY.finditer(text):
        mon = MONTHS[m.group(3).rstrip('.').lower()]
        for d in (m.group(1), m.group(2)):
            if d: out.append((int(m.group(4)), mon, int(d), m.group(0)))
    for m in DATE_MDY.finditer(text):
        mon = MONTHS[m.group(1).rstrip('.').lower()]
        for d in (m.group(2), m.group(3)):
            if d: out.append((int(m.group(4)), mon, int(d), m.group(0)))
    for m in DATE_ISO.finditer(text):
        out.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(0)))
    return out


def clip(text, a, b, w=70):
    return text[max(0, a - w):min(len(text), b + w)].strip()


# ------------------------------------------------------------------ site sectioning
def split_div(src, start_marker):
    i = src.find(start_marker)
    if i < 0: return None
    depth = 0
    for m in re.finditer(r'<(/?)div\b[^>]*>', src[i:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return i, i + m.end()
    return None


def sections_of(src):
    """Return OrderedDict name -> text (tags stripped, templates kept). Tree split out on its own."""
    mi, mj = src.find('<main>'), src.find('</main>')
    main = src[mi + 6:mj] if mi >= 0 and mj > mi else src
    secs = OrderedDict()
    span = split_div(main, '<div class="ftree">')
    if span:
        secs['Family tree'] = strip_tags(main[span[0]:span[1]])
        main = main[:span[0]] + ' ' + main[span[1]:]
    toks = [(m.start(), m.group(1), m.group(2), strip_tags(m.group(3), True)) for m in
            re.finditer(r'<(h[23])\b([^>]*)>(.*?)</\1>', main, re.S)]
    heads = []
    for pos, tag, attrs, txt in toks:
        heads.append((pos, tag, txt))
    cur_h2, cur_h3 = 'Lead / how to read', ''
    last = 0
    pieces = []
    for pos, tag, txt in heads:
        pieces.append((cur_h2, cur_h3, main[last:pos]))
        if tag == 'h2': cur_h2, cur_h3 = txt[:70], ''
        else: cur_h3 = txt[:70]
        last = pos
    pieces.append((cur_h2, cur_h3, main[last:]))
    for h2, h3, body in pieces:
        t = strip_tags(body)
        if not t: continue
        key = h2 + (' > ' + h3 if h3 else '')
        secs[key] = (secs.get(key, '') + ' ' + t).strip()
    return secs, main


def people_sections(path):
    """Each person in people_data.py -> text built only from string constants (no code is run)."""
    if not path or not os.path.exists(path): return OrderedDict()
    tree = ast.parse(open(path, encoding='utf8').read())
    out = OrderedDict()
    skip_kw = {'slug', 'story', 'docs', 'line', 'cards'}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'dict':
            kws = {k.arg: k.value for k in node.keywords if k.arg}
            if 'slug' not in kws or 'name' not in kws: continue
            strs = []
            for k, v in kws.items():
                if k in skip_kw: continue
                for sub in ast.walk(v):
                    if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                        strs.append(sub.value)
            slug = kws['slug'].value if isinstance(kws['slug'], ast.Constant) else '?'
            txt = re.sub(r'\{[a-z\-]+\}', ' ', ' '.join(strs))
            out['Person page: ' + slug] = txt
    return out


# ------------------------------------------------------------------ doc index
class DocIndex:
    def __init__(self, text):
        self.raw = text
        self.n = norm_text(text)
        self.dates = set()
        self.date_list = []
        for y, m, d, raw in dates_in(text):
            self.dates.add((y, m, d)); self.date_list.append((y, m, d, raw))
        self.years = set(re.findall(r'\b(1[89]\d\d|20[0-2]\d)\b', self.n))
        self.numbers = set(x.replace(',', '') for x in re.findall(r'\b\d[\d,]*\d\b|\b\d\b', self.n))
        words = re.findall(r"[a-z][a-z'\-]*", self.n)
        self.words = set(words)
        self.words |= set(w.strip("'-") for w in words) | set(w[:-2] for w in words if w.endswith("'s"))
        self.addr = set()
        for m in re.finditer(r'\b(\d{1,5})\s+((?:[a-z0-9][\w.\'-]*\s+){0,3}?(?:street|st|avenue|ave|place|pl|road|rd|boulevard|blvd|court|ct|lane|drive|dr|terrace|ter|broadway|parkway|pkwy|alley))\b', self.n):
            self.addr.add(self._addr_key(m.group(1), m.group(2)))
        self.addr_text = re.sub(r'[.,]', '', self.n)

    @staticmethod
    def _addr_key(num, name):
        name = re.sub(r'[.,]', '', name.lower())
        name = re.sub(r'\b(street|st)$', 'st', name)
        name = re.sub(r'\b(avenue|ave)$', 'ave', name)
        name = re.sub(r'\b(place|pl)$', 'pl', name)
        name = re.sub(r'\b(road|rd)$', 'rd', name)
        name = re.sub(r'(\d+)(st|nd|rd|th)\b', r'\1', name)
        return num + ' ' + re.sub(r'\s+', ' ', name)


def near_dates(doc, y, m, d):
    hits = []
    for (yy, mm, dd, raw) in doc.date_list:
        same = (yy == y) + (mm == m) + (dd == d)
        if same == 2 and raw not in hits: hits.append(raw)
    return hits[:4]


# ------------------------------------------------------------------ the checks
def run(site_path, doc_path, people_path):
    src = open(site_path, encoding='utf8').read()
    doc = DocIndex(open(doc_path, encoding='utf8').read())
    secs, main = sections_of(src)
    secs_people = people_sections(people_path)
    flags = defaultdict(lambda: defaultdict(list))   # class -> section -> [lines]
    nflag = defaultdict(int)

    def add(cls, sec, line):
        key = line
        if key in flags[cls][sec]: return
        flags[cls][sec].append(line); nflag[cls] += 1

    all_secs = list(secs.items()) + list(secs_people.items())
    for sec, text in all_secs:
        nt = norm_text(text)
        # 1 full dates
        for y, m, d, raw in dates_in(text):
            if (y, m, d) not in doc.dates:
                mm = [k for k, v in MONTHS.items() if v == m and len(k) > 3 and k != 'sept'][:1]
                alt = near_dates(doc, y, m, d)
                hint = ('  [Doc has similar: ' + '; '.join(alt) + ']') if alt else ''
                at = text.find(raw)
                add('date', sec, '"%s" (%02d-%02d-%d) ...%s...%s' % (raw, d, m, y, clip(text, at, at + len(raw), 45), hint))
        # 2 years
        date_spans = [(m.start(), m.end()) for m in DATE_DMY.finditer(text)] + [(m.start(), m.end()) for m in DATE_MDY.finditer(text)]
        for m in re.finditer(r'(?<![\d,.$/#-])(1[89]\d\d|20[0-2]\d)(?![\d,])', text):
            y = m.group(1)
            if y not in doc.years:
                add('year', sec, '%s ...%s...' % (y, clip(text, m.start(), m.end(), 50)))
        # 3 numbers
        for m in re.finditer(r'(?<![\d,.$/-])(\d{3,}(?:,\d{3})*)(?![\d,]*\d?[%])', text):
            raw = m.group(1); n = raw.replace(',', '')
            if re.fullmatch(r'1[89]\d\d|20[0-2]\d', n): continue
            before = text[max(0, m.start() - 30):m.start()]
            after = text[m.end():m.end() + 25]
            ctx = bool(NUM_CTX_BEFORE.search(before) or NUM_CTX_AFTER.match(after) or
                       re.match(r'\s*(?:[A-Z][a-z]+\s+){0,2}' + STREET_WORDS + r'\b', after) or
                       re.match(r"\s*(?:st|nd|rd|th)\b", after))
            if len(n) >= 4 or ctx:
                if n not in doc.numbers:
                    isid = bool(ID_BEFORE.search(text[max(0, m.start() - 40):m.start()])) or text[m.end():m.end() + 1] in '_-' or text[m.start() - 1:m.start()] in '_-'
                    cls = 'idnum' if (isid and not re.search(r'(?:no\.?|petition|certificate|declaration|ED|sheet|lodge)\s*$', before, re.I)) else 'number'
                    add(cls, sec, '%s%s ...%s...' % (raw, '' if ctx else ' (bare)', clip(text, m.start(), m.end(), 50)))
        # 4 addresses
        for m in ADDR.finditer(text):
            if m.group(2).split()[0] in ('The', 'A', 'An', 'In', 'On'): continue
            key = DocIndex._addr_key(m.group(1), m.group(2))
            if key not in doc.addr:
                loose = re.sub(r'[.,]', '', norm_text(m.group(0)))
                if loose not in doc.addr_text:
                    add('address', sec, '"%s" ...%s...' % (m.group(0).strip(), clip(text, m.start(), m.end(), 45)))
    # 5 names: tree, descendants and people pages
    name_secs = [(s, t) for s, t in all_secs if s == 'Family tree' or s.startswith('Person page') or
                 'descendants' in s.lower()]
    for sec, text in name_secs:
        seen = set()
        for m in re.finditer(r"(?<![\w’'-])([A-Z][A-Za-z’'\-]{2,})", text):
            tok = m.group(1)
            t = norm_text(tok).strip("'-")
            if t.endswith("'s"): t = t[:-2]
            if t in STOP or t in seen: continue
            seen.add(t)
            if t in doc.words: continue
            close = difflib.get_close_matches(t, doc.words, n=3, cutoff=0.8)
            hint = '  [Doc has similar: %s]' % ', '.join(close) if close else ''
            add('name', sec, '%s ...%s...%s' % (tok, clip(text, m.start(), m.end(), 40), hint))
    # 6 labels
    for m in re.finditer(r'<(b|strong|span|em)\b([^>]*class="[^"]*\b(?:tag|label|badge)\b[^"]*"[^>]*)>(.*?)</\1>', src, re.S):
        txt = strip_tags(m.group(3))
        if txt not in ('Confirmed', 'Family', 'Probable'):
            add('label', 'tag element', '"%s" in <%s %s> ...%s...' % (txt, m.group(1), m.group(2).strip()[:40], clip(strip_tags(src[m.start() - 200:m.end() + 100]), 0, 0, 100)))
    plain_main = strip_tags(main)
    for w in WEAK_LABELS:
        for m in re.finditer(r'<(?:b|strong)\b[^>]*>\s*' + w + r'\b', src):
            add('label', 'bold weak label', '"%s" ...%s...' % (w, strip_tags(src[m.start():m.start() + 200])[:110]))
        for m in re.finditer(r'\((?:' + w + r')\)|\b(?:Label|Labelled|Labeled):\s*' + w + r'\b', plain_main):
            add('label', 'bracketed weak label', '"%s" ...%s...' % (m.group(0), clip(plain_main, m.start(), m.end(), 60)))
    # 7 links
    base = os.path.dirname(os.path.dirname(os.path.abspath(site_path)))
    ids = set(re.findall(r'\sid="([^"]+)"', src))
    built = {f for f in os.listdir(base) if f.endswith('.html')} if os.path.isdir(base) else set()
    slugs = set(re.findall(r"slug='([^']+)'", open(people_path, encoding='utf8').read())) if people_path and os.path.exists(people_path) else set()
    built |= {'person-%s.html' % s for s in slugs}
    for m in re.finditer(r'href="([^"]+)"', main):
        h = m.group(1)
        if h.startswith(('http://', 'https://', 'mailto:', 'tel:')): continue
        page, _, frag = h.partition('#')
        ctx = clip(strip_tags(main[m.start() - 150:m.end() + 150]), 0, 0, 0) if False else ''
        if page and page not in built:
            add('link', 'source site.html', 'page not in build: %s' % h)
        elif not page and frag and frag not in ids and frag != 'top':
            add('link', 'source site.html', 'anchor not found in site.html: #%s' % frag)
    # links in generated pages, if present (built output is read only here)
    gen_ids = {}
    for f in sorted(built):
        p = os.path.join(base, f)
        if os.path.exists(p): gen_ids[f] = set(re.findall(r'\sid="([^"]+)"', open(p, encoding='utf8').read()))
    for f, _ in sorted(gen_ids.items()):
        txt = open(os.path.join(base, f), encoding='utf8').read()
        for m in re.finditer(r'href="([^"]+)"', txt):
            h = m.group(1)
            if h.startswith(('http://', 'https://', 'mailto:', 'tel:', 'data:')): continue
            page, _, frag = h.partition('#')
            tgt = page or f
            if tgt.endswith('.html') and tgt not in built:
                add('link', 'built page ' + f, 'page not in build: %s' % h)
            elif tgt in gen_ids and frag and frag not in gen_ids[tgt]:
                add('link', 'built page ' + f, 'anchor missing: %s' % h)
            elif page and not page.endswith('.html') and not os.path.exists(os.path.join(base, page)):
                add('link', 'built page ' + f, 'file not found: %s' % h)
    return flags, nflag


def living_surname_check(site_path, people_path):
    """Check 8. Returns list of (file, surname, context). Raw text is scanned (tags, comments, attributes
    included), so a hidden mention in markup or a built page is caught too."""
    names = sorted({n.strip() for n in list(LIVING_SURNAMES_BLOCKLIST) + list(EXTRA_LIVING_SURNAMES) if n.strip()})
    if not names: return []
    pat = re.compile(r"(?<![\w])(" + '|'.join(re.escape(n) for n in names) + r")(?![\w])", re.I)
    files = [site_path]
    if people_path and os.path.exists(people_path): files.append(people_path)
    base = os.path.dirname(os.path.dirname(os.path.abspath(site_path)))
    if os.path.isdir(base):
        files += [os.path.join(base, f) for f in sorted(os.listdir(base)) if f.endswith('.html')]
    seen, hits = set(), []
    for f in files:
        rp = os.path.realpath(f)
        if rp in seen or not os.path.exists(f): continue
        seen.add(rp)
        t = open(f, encoding='utf8', errors='replace').read()
        for m in pat.finditer(t):
            hits.append((os.path.basename(f), m.group(1), re.sub(r'\s+', ' ', t[max(0, m.start() - 40):m.end() + 40])))
    return hits


TITLES = OrderedDict([('date', '1. FULL DATES not found as a date in the Doc'),
                      ('year', '2. YEARS (1800-2026) not found anywhere in the Doc'),
                      ('number', '3. NUMBERS (3+ digits: certificate / petition / ED / sheet / lodge / street) not found in the Doc'),
                      ('idnum', '3b. ID-STYLE NUMBERS (image, memorial, ark, record, newspaper image ids) not found in the Doc'),
                      ('address', '4. STREET ADDRESSES not found in the Doc'),
                      ('name', '5. NAME TOKENS (family tree, descendants, people pages) not found in the Doc'),
                      ('label', '6. LABELS other than Confirmed / Family / Probable'),
                      ('link', '7. LINKS to a page or anchor that does not exist in the build')])


def main_():
    a = [x for x in sys.argv[1:]]
    if len(a) < 2:
        print(__doc__); return 2
    site, doc = a[0], a[1]
    people = a[2] if len(a) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'people_data.py')
    for p in (site, doc):
        if not os.path.exists(p):
            print('File not found:', p); return 2
    flags, n = run(site, doc, people)
    out = []
    out.append('SITE vs DOC FLAGGER  -  a flagger for a human to judge, not a judge.')
    out.append('It lists what the site says that it could not find in the Doc export. A flag is NOT an error:')
    out.append('spelling variants, date styles and page furniture are common. Nothing is edited.')
    out.append('Site source: %s' % site); out.append('Doc export : %s' % doc)
    out.append('People data: %s' % (people if os.path.exists(people) else '(not found, people pages not scanned)'))
    out.append('')
    total = sum(n.values())
    for k, title in TITLES.items():
        out.append('%s  [%d flagged]' % (title, n.get(k, 0)))
        for sec, lines in flags[k].items():
            out.append('  -- %s (%d)' % (sec, len(lines)))
            for l in lines: out.append('       * ' + l)
        out.append('')
    out.append('TOTAL FLAGGED: %d  (%s)' % (total, ', '.join('%s %d' % (k, n.get(k, 0)) for k in TITLES)))
    living = living_surname_check(site, people)
    out.append('8. LIVING-PEOPLE SURNAMES (privacy; blocks publishing)  [%d found]' % len(living))
    for fn, sn, ctx in living:
        out.append('       * BLOCKED: "%s" in %s ...%s...' % (sn, fn, ctx))
    out.append('')
    if living:
        out.append('PRIVACY CHECK FAILED: a living person\'s surname is on the site. Do NOT publish. Remove it (first names only).')
    print('\n'.join(out))
    if living: return 3
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main_())
