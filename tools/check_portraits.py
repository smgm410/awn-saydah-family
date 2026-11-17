"""Portrait-crop check. For every converted section (div.lay) in src/site.html, list each approved
portrait crop (tools/portraits.py) for the people the section's jump line links to, and say whether
the crop's picture is in that section. Run: python3 -I tools/check_portraits.py"""
import re,sys,os
sys.path.insert(0,os.path.dirname(__file__))
import portraits
s=open('src/site.html',encoding='utf-8').read()
by={}
for d in portraits.P:
    for sl in d['slugs']: by.setdefault(sl,[]).append(d['file'])
parts=re.split(r'(?=<h3 id=")',s);bad=0
for part in parts:
    m=re.match(r'<h3 id="([^"]+)"',part)
    if not m or '<div class="lay">' not in part: continue
    jl=re.search(r'<p class="jump">(.*?)</p>',part,re.S)
    slugs=re.findall(r'person-([\w-]+)\.html',jl.group(1)) if jl else []
    for sl in slugs:
        for f in by.get(sl,[]):
            ok=f[:-4] in part
            if not ok: bad+=1
            print(('  ok     ' if ok else '  MISSING'),m.group(1),'|',sl,'|',f)
print('missing:',bad)
