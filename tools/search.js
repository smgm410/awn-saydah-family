(function(){
var q=document.getElementById('q'),out=document.getElementById('sres'),st=document.getElementById('sres-status'),data=null;
function norm(s){return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'')}
function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function run(term){
 out.innerHTML='';term=(term||'').trim();if(!term){st.textContent='';return}
 var toks=norm(term).split(/\s+/).filter(Boolean);var res=[];
 data.forEach(function(e){var t=norm(e.t),x=norm(e.x),score=0,ok=true;
  toks.forEach(function(k){var inT=t.indexOf(k)>-1,inX=x.indexOf(k)>-1;if(!inT&&!inX){ok=false}else{score+=(inT?5:0)+(inX?1:0)}});
  if(ok)res.push({e:e,s:score})});
 res.sort(function(a,b){return b.s-a.s});
 st.textContent=res.length?res.length+' result'+(res.length>1?'s':'')+' for “'+term+'”':'Nothing found for “'+term+'”. Try another spelling (Aoun, Awn, Owen; Saydah, Saida; Hadad, Haddad) or a shorter word.';
 res.slice(0,60).forEach(function(r){var e=r.e,x=e.x,i=norm(x).indexOf(toks[0]),sn='';
  if(i>-1){var a=Math.max(0,i-70);sn=(a>0?'… ':'')+x.slice(a,i+150)+' …'}else{sn=x.slice(0,160)+' …'}
  var h=esc(sn);toks.forEach(function(k){h=h.replace(new RegExp('('+k.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig'),'<mark>$1</mark>')});
  var li=document.createElement('li');li.innerHTML='<span class="k">'+(e.k==='d'?'Document':'Story')+'</span><a href="'+e.u+'">'+esc(e.t)+'</a><p>'+h+'</p>';out.appendChild(li)})}
var params=new URLSearchParams(location.search),first=params.get('q')||'';
q.value=first;
fetch('search-index.json').then(function(r){return r.json()}).then(function(d){data=d;run(first);
 q.addEventListener('input',function(){run(q.value)})}).catch(function(){st.textContent='Search could not load. Please try again.'});
})();
