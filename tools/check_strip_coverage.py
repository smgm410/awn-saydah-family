"""Strip-coverage check (added 17 Nov 2026 after boxes 13, 6 and 11 were shown with records missing).
For every converted section (div.lay in src/site.html) it takes every record bullet of that box in the
research Doc and asks: is there a picture card for it, or is it listed here with a reason?
Run:  python3 -I tools/check_strip_coverage.py DOC_EXPORT.txt
(DOC_EXPORT.txt = the decoded "Research boxes" export, as for check_site_vs_doc.py.)
A bullet is COVERED when (a) a card in its box's strip matches it (two or more shared dates, years or quoted
names; cards can also be tied by hand in tools/strip_coverage.tsv with status "card"), or
(b) tools/strip_coverage.tsv lists it with a reason: arabic, index, summary, private, other-box, living,
duplicate, docs-only, adds-nothing, not-ours; 'ask' = waiting for Sarah, listed but not failing.  Arabic pages and index lines are recognised from the bullet's opening words.
Anything else is UNACCOUNTED and the script exits 1: a section must not be shown to Sarah while that list is not empty.
Second report: Doc bullets that have no card on the Documents page (and no 'no-card' reason in the tsv)."""
import re,sys,os,html
BOX={1:'joseph-and-assin-aoun',2:'eight-children',3:'the-crossing-1920',4:'home-on-tompkins-place',5:'becoming-american',
6:'the-brothers-and-sisters-later-lives',7:'anton-arrives-1898',8:'anton-and-wassela',9:'wassela-s-family-the-hodods-hadad-and-th',
10:'the-tuxedo-park-accident-1917',11:'three-daughters',12:'anton-s-brothers-and-sisters',13:'khaleel-w-saydah',14:'michael-w-saydah',
15:'murad-saydah-and-tirkman',16:'the-kirkish-sisters',17:'the-end-of-anton-s-life',18:'anthony-a-citizen-and-a-shopkeeper',
19:'the-wedding',20:'a-home-on-86th-street',21:'helen',22:'five-children',23:'anthony-s-death',24:'the-family-jackie-married-into'}
ARABIC=re.compile(r"Al-Hoda|As-Sameer|Mira.at|Ash-Shams|As-Sayeh|Al-Kalemat|Jurab|Arabic|Hamrah|Al-Bayan",re.I)
INDEX=re.compile(r"index|Find a Grave|SSDI|burial search|search screen|WebSurrogate|NUMIDENT|Social Security|obituary index|Stories and Events",re.I)
SUMMARY=re.compile(r"^(open conflicts?|disagreements|nine children|sources named|naturalization papers held|esther in lebanon|jameel's birth|the date\.)",re.I)
def tok(t):
    t=html.unescape(re.sub('<[^>]+>',' ',t)).lower()
    out=set(re.findall(r'\b\d{1,2} (?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{4}\b',t))
    out|=set(re.findall(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{1,2},? \d{4}\b',t))
    out|=set(re.findall(r'\b1[89]\d\d\b',t))
    out|=set(re.findall(r'“([^”]{4,40})”',t))|set(re.findall(r'"([^"]{4,40})"',t))
    return out
def main(doc):
    full={}
    for l in open(doc,encoding='utf-8').read().split('\n'):
        m=re.match(r'^\s*[-*•]\s*\[(B\d\d-\d\d)\]\s*(.*)',l)
        if m and m.group(1) not in full: full[m.group(1)]=m.group(2)
    ex={};manual={}
    if os.path.exists('tools/strip_coverage.tsv'):
        for l in open('tools/strip_coverage.tsv',encoding='utf-8'):
            if l.startswith('#') or not l.strip(): continue
            p=l.rstrip('\n').split('\t')
            (manual if p[1]=='card' else ex)[p[0]]=p[1:]
    s=open('src/site.html',encoding='utf-8').read()
    hs=[(m.start(),m.group(1)) for m in re.finditer(r'<h3 id="([^"]+)">',s)]
    docs=open('documents.html',encoding='utf-8').read() if os.path.exists('documents.html') else ''
    cards=set(re.findall(r'data-id="(B\d\d-\d\d)"',docs))
    bad=0;conv=[];asks=[]
    for n,h in BOX.items():
        pos=[p for p,i in hs if i==h]
        if not pos: continue
        a=pos[0]; nb=[p for p,i in hs if p>a]; seg=s[a:(nb[0] if nb else len(s))]
        if '<div class="lay">' not in seg: continue
        conv.append(n); figs=re.findall(r'<figure class="[^"]*" id="([^"]+)">(.*?)</figure>',seg,re.S)
        ft=[(i,tok(t)) for i,t in figs]
        got=0;acc={};unacc=[]
        for k,v in full.items():
            if int(k[1:3])!=n: continue
            if k in manual or any(len(f&tok(v[:900]))>=2 for _,f in ft): acc[k]='card';continue
            if k in ex:
                acc[k]=ex[k][0]
                if ex[k][0]=='ask': asks.append((k,ex[k][1]))
                continue
            if ARABIC.search(v[:130]): acc[k]='arabic';continue
            if INDEX.search(v[:100]): acc[k]='index';continue
            if SUMMARY.search(v.strip()): acc[k]='summary';continue
            unacc.append((k,v[:90]))
        print('box %d: %d bullets, %d cards in the strip, %d unaccounted'%(n,len(acc)+len(unacc),len(figs),len(unacc)))
        for k,v in unacc: print('    UNACCOUNTED',k,v)
        bad+=len(unacc)
    nodoc=[k for k in full if int(k[1:3]) in conv and k not in cards and not (k in ex and ex[k][0]=='no-card')]
    print('\nDoc bullets in converted boxes with no card on the Documents page: %d'%len(nodoc))
    try:
        why=dict((l.split('\t')[0],l.rstrip('\n').split('\t')[1:]) for l in open('tools/no_card_reasons.tsv',encoding='utf8') if l.strip())
    except OSError: why={}
    noreason=[k for k in nodoc if k not in why]
    for k in nodoc: print('    NO DOCUMENTS CARD',k,'[%s]'%why.get(k,['NO REASON'])[0],full[k][:60])
    print('No-card bullets without a written reason: %d'%len(noreason)); bad+=len(noreason)
    print('\nOPEN DECISIONS for Sarah (status ask): %d'%len(asks))
    for k,v in asks: print('    ASK',k,v)
    print('\nUNACCOUNTED total:',bad); sys.exit(1 if bad else 0)
if __name__=='__main__': main(sys.argv[1])
