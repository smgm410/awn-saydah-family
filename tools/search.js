(function(){
var q=document.getElementById('q'),out=document.getElementById('sres'),st=document.getElementById('sres-status'),data=null;
function norm(s){return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'')}
var GROUPS=[['aoun','awn','owen','aun','aou','aoon','owin'],['saydah','saidah','sayda','saida','smyda'],['hadad','haddad','hodod','hadel'],['antoon','anton','antoun'],['anthony','antoine','antony'],['elias','louis','luis'],['nassib','nessil','nessib'],['khaleel','khalil','kaleel'],['wassela','wassila','wassilah','wassilla','waseela','wassella'],['zahle','zahleh','zahlah'],['damour','damur','damoor'],['mathilde','matilda','matilde','mathilda'],['theresa','teresa','thirsie'],['george','georges'],['salim','salem','selim'],['najib','najeeb','nageeb','najeb'],['michael','michel','michal','micheal'],['kirkish','qirqish','kirkesh'],['shehadi','shahady','shehady','shahadi'],['john','jean','hanna'],['joseph','youseuf','yousef','youssef','yusuf'],['assin','aseen','essine','assine']];
function alts(k){for(var i=0;i<GROUPS.length;i++){if(GROUPS[i].indexOf(k)>-1)return GROUPS[i]}return [k]}
function has(text,list){for(var i=0;i<list.length;i++){var a=list[i],p=text.indexOf(a);while(p>-1){if(p===0||!/[a-z0-9]/.test(text.charAt(p-1)))return p;p=text.indexOf(a,p+1)}}return -1}
function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function run(term){
 out.innerHTML='';term=(term||'').trim();if(!term){st.textContent='';return}
 var toks=norm(term).split(/\s+/).filter(Boolean);var res=[];
 data.forEach(function(e){var t=norm(e.t),x=norm(e.x),score=0,ok=true;
  toks.forEach(function(k){var al=alts(k),inT=has(t,al)>-1,inX=has(x,al)>-1;if(!inT&&!inX){ok=false}else{score+=(inT?5:0)+(inX?1:0)}});
  if(ok)res.push({e:e,s:score})});
 res.sort(function(a,b){return b.s-a.s});
 var also=[];toks.forEach(function(k){var al=alts(k);if(al.length>1)also.push(al.join(', '))});var note=also.length?' Also searched the same name spelled: '+also.join('; ')+'.':'';st.textContent=res.length?res.length+' result'+(res.length>1?'s':'')+' for “'+term+'”.'+note:'Nothing found for “'+term+'”. Try another spelling (Aoun, Awn, Owen; Saydah, Saida; Hadad, Haddad) or a shorter word.';
 res.slice(0,60).forEach(function(r){var e=r.e,x=e.x,i=norm(x).indexOf(toks[0]),sn='';
  if(i>-1){var a=Math.max(0,i-70);sn=(a>0?'… ':'')+x.slice(a,i+150)+' …'}else{sn=x.slice(0,160)+' …'}
  var h=esc(sn);toks.forEach(function(k){alts(k).forEach(function(a){h=h.replace(new RegExp('(\\b'+a.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig'),'<mark>$1</mark>')})});
  var li=document.createElement('li');li.innerHTML='<span class="k">'+(e.k==='d'?'Document':'Story')+'</span><a href="'+e.u+'">'+esc(e.t)+'</a><p>'+h+'</p>';out.appendChild(li)})}
var params=new URLSearchParams(location.search),first=params.get('q')||'';
q.value=first;
fetch('search-index.json').then(function(r){return r.json()}).then(function(d){data=d;run(first);
 q.addEventListener('input',function(){run(q.value)})}).catch(function(){st.textContent='Search could not load. Please try again.'});
})();
