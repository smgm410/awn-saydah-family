(function(){
var figs=[].slice.call(document.querySelectorAll('figure.doc')),lb=document.getElementById('lb'),box=lb.querySelector('.box'),ct=lb.querySelector('.ct'),cur=-1,last=null;
function vis(){return figs.filter(function(f){return f.offsetParent!==null||f.classList.contains('g')===false})}
function open(i,list){list=list||figs;cur=(i+list.length)%list.length;var f=list[cur],t=f.querySelector('template');box.innerHTML=t.innerHTML;
[].forEach.call(box.querySelectorAll('img[data-src]'),function(im){im.src=im.dataset.src;im.title='Click to zoom';im.addEventListener('click',function(){im.classList.toggle('zoom');hint(im)})});
var pc=box.querySelector('.pics');if(pc&&pc.querySelector('img')){var h=document.createElement('div');h.className='zh';h.textContent='Click the picture to zoom in or out';pc.insertBefore(h,pc.firstChild)}
var cap=box.querySelector('.cap'),st=f.getAttribute('data-story');if(cap&&st){var p=document.createElement('p');p.innerHTML='<a href="'+st+'" style="color:#e0bd83">See it in the story →</a>';cap.appendChild(p)}
ct.textContent=f.querySelector('.num').textContent+' ('+(cur+1)+' of '+list.length+' on this page)';lb.classList.add('on');box.scrollTop=0;[].forEach.call(box.children,function(c){c.scrollTop=0});document.body.style.overflow='hidden';lb.querySelector('.x').focus();lb._list=list}
function hint(im){var h=lb.querySelector('.zh');if(h)h.textContent=im.classList.contains('zoom')?'Zoomed in. Scroll to move around. Click to zoom out.':'Click the picture to zoom in or out'}
function close(){lb.classList.remove('on');box.innerHTML='';document.body.style.overflow='';if(last)last.focus()}
function visList(){return figs.filter(function(f){return f.offsetParent!==null})}
figs.forEach(function(f){var b=f.querySelector('.thumb');b.addEventListener('click',function(){last=b;var l=visList();open(l.indexOf(f),l)})});
lb.querySelector('.x').onclick=close;lb.querySelector('.pv').onclick=function(){open(cur-1,lb._list)};lb.querySelector('.nx').onclick=function(){open(cur+1,lb._list)};
document.addEventListener('keydown',function(e){if(!lb.classList.contains('on'))return;if(e.key==='Escape')close();if(e.key==='ArrowLeft')open(cur-1,lb._list);if(e.key==='ArrowRight')open(cur+1,lb._list)});
/* gallery filters */
var fb=document.querySelectorAll('.filters button');
[].forEach.call(fb,function(b){b.addEventListener('click',function(){[].forEach.call(fb,function(x){x.classList.remove('on')});b.classList.add('on');var f=b.dataset.f;
 [].forEach.call(document.querySelectorAll('figure.doc.g'),function(g){var show=f==='all'||(f==='ar'&&g.classList.contains('ar'))||g.classList.contains(f==='p1'?'p1':f==='p2'?'p2':f==='p3'?'p3':'zz');g.classList.toggle('hide',!show)});
 [].forEach.call(document.querySelectorAll('aside.gal-box'),function(a){var any=a.querySelector('figure.doc.g:not(.hide)');a.classList.toggle('hide',!any);var h=a.previousElementSibling;if(h&&h.tagName==='H3')h.classList.toggle('hide',!any)});
 [].forEach.call(document.querySelectorAll('h2.gal'),function(h){var n=h.nextElementSibling,any=false;while(n&&n.tagName!=='H2'){if(n.tagName==='ASIDE'&&!n.classList.contains('hide'))any=true;n=n.nextElementSibling}h.classList.toggle('hide',!any)})})});
/* rail */
var rail=document.getElementById('rail'),menu=document.getElementById('menu'),scrim=document.getElementById('scrim');
function setMenu(o){rail.classList.toggle('open',o);scrim.classList.toggle('open',o);menu.setAttribute('aria-expanded',o)}
menu.onclick=function(){setMenu(!rail.classList.contains('open'))};
scrim.onclick=function(){setMenu(false)};document.getElementById('railx').onclick=function(){setMenu(false)};
document.addEventListener('keydown',function(e){if(e.key==='Escape')setMenu(false)});
window.addEventListener('resize',function(){if(window.innerWidth>900)setMenu(false)});
rail.addEventListener('click',function(e){if(e.target.tagName==='A')setMenu(false)});
var links={};[].forEach.call(rail.querySelectorAll('a[href^="#"]'),function(a){links[a.getAttribute('href').slice(1)]=a});
var heads=[].slice.call(document.querySelectorAll('main h2[id],main h3[id]')).filter(function(h){return links[h.id]});
function spy(){var c=null;heads.forEach(function(h){if(h.getBoundingClientRect().top<120)c=h});
 [].forEach.call(rail.querySelectorAll('a.on'),function(a){a.classList.remove('on')});if(c){var a=links[c.id];a.classList.add('on');
 if(window.innerWidth>900){var r=a.getBoundingClientRect(),rr=rail.getBoundingClientRect();if(r.top<rr.top+40||r.bottom>rr.bottom-40)rail.scrollTop+=r.top-rr.top-rr.height/3}}}
var up=document.getElementById('up');up.onclick=function(){window.scrollTo({top:0,behavior:'smooth'})};
/* print the tree */
var pt=document.getElementById('printtree');if(pt)pt.onclick=function(){document.documentElement.classList.add('print-tree');window.print()};
window.addEventListener('afterprint',function(){document.documentElement.classList.remove('print-tree')});
/* landing: keep a #hash from another page; otherwise start at the top */
if('scrollRestoration' in history)history.scrollRestoration='manual';
function top0(){window.scrollTo(0,0);document.documentElement.scrollTop=0;document.body.scrollTop=0}
function land(){var id=decodeURIComponent((location.hash||'').slice(1));if(!id){top0();return}
 var m=/^item-(\d+)$/.exec(id),t=document.getElementById(id);
 if(m&&t&&t.classList.contains('g')){var l=visList();last=t.querySelector('.thumb');open(l.indexOf(t),l);t.scrollIntoView();return}
 if(t){t.scrollIntoView();t.style.animation='none';void t.offsetWidth;t.style.animation=''}}
window.addEventListener('load',function(){land();setTimeout(function(){if(!location.hash)top0();else{var t=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(t&&!lb.classList.contains('on'))t.scrollIntoView()}},150)});
window.addEventListener('pageshow',function(e){if(!location.hash)top0()});
window.addEventListener('hashchange',land);
var tk=false;window.addEventListener('scroll',function(){if(!tk){tk=true;requestAnimationFrame(function(){spy();up.classList.toggle('on',window.scrollY>900);tk=false})}},{passive:true});spy();
})();

(function(){var bs=[].slice.call(document.querySelectorAll('.bigtext'));function set(on){document.documentElement.classList.toggle('big',on);bs.forEach(function(b){b.setAttribute('aria-pressed',on);b.textContent=on?'Normal text':'Larger text'})}var on=false;try{on=localStorage.getItem('bigtext')==='1'}catch(e){}set(on);bs.forEach(function(b){b.addEventListener('click',function(){on=!on;set(on);try{localStorage.setItem('bigtext',on?'1':'0')}catch(e){}})})})();
