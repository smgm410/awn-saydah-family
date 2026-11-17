(function(){var on={};var chips=document.querySelectorAll('.chip');
function ok(r,f){if(f==='pic')return r.dataset.pic==='1';if(f==='open')return r.dataset.open==='1';return r.dataset.kind===f;}
function apply(){var act=Object.keys(on).filter(function(k){return on[k];});
var kinds=act.filter(function(k){return k==='index'||k==='arabic';});var others=act.filter(function(k){return k==='pic'||k==='open';});
var pf=document.getElementById('pfilter').value;var shown=0,filtering=act.length>0||!!pf;
document.querySelectorAll('.rec').forEach(function(r){var show=(!pf||(r.dataset.people||'').indexOf(' '+pf+' ')>-1)&&others.every(function(f){return ok(r,f);})&&(!kinds.length||kinds.some(function(f){return ok(r,f);}));r.classList.toggle('hide',!show);if(show)shown++;});
document.querySelectorAll('details.box').forEach(function(d){var n=d.querySelectorAll('.rec:not(.hide)').length;d.classList.toggle('empty',filtering&&n===0);if(filtering&&n>0)d.open=true;
d.querySelectorAll('section.disagree,.kid,.explainer,.tbd').forEach(function(e){e.classList.toggle('filt-hide',filtering);});});
var c=document.getElementById('filtercount');if(filtering){c.hidden=false;c.textContent='Showing '+shown+' of '+document.querySelectorAll('.rec').length+' cards. Boxes with no match are hidden. Turn a filter off to see everything.';}else{c.hidden=true;c.textContent='';}}
function clearFilters(){on={};document.getElementById('pfilter').value='';chips.forEach(function(b){b.setAttribute('aria-pressed','false');});apply();}
document.getElementById('pfilter').addEventListener('change',apply);
chips.forEach(function(b){b.addEventListener('click',function(){var f=b.dataset.f;on[f]=!on[f];b.setAttribute('aria-pressed',on[f]?'true':'false');apply();});});
function reveal(id){var t=document.getElementById(id);if(!t)return;if(t.closest('.hide,.filt-hide,.empty'))clearFilters();var d=t.closest('details');if(d)d.open=true;}
document.addEventListener('click',function(e){var a=e.target.closest('a[href^="#"]');if(!a||a.closest('.pics'))return;reveal(a.getAttribute('href').slice(1));});
window.addEventListener('hashchange',function(){reveal(location.hash.slice(1));var t=document.getElementById(location.hash.slice(1));if(t)t.scrollIntoView();});
if(location.hash)reveal(location.hash.slice(1));})();

(function(){var d=document.getElementById('dlb');document.addEventListener('click',function(e){var a=e.target.closest('.pics a');if(!a)return;e.preventDefault();d.querySelector('img').src=a.href;d.querySelector('.cp').textContent=a.dataset.cap||'';d.showModal();});
document.getElementById('dlbx').onclick=function(){d.close();};d.addEventListener('click',function(e){if(e.target===d)d.close();});})();