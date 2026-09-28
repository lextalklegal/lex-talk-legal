/* Legacy URL cleanup: silently restore the canonical address after the workers.dev compatibility bridge. */
(function(){
  const u=new URL(window.location.href);
  if(u.pathname==='/__legacy-bridge/'){
    let target='/';
    try{
      const raw=u.searchParams.get('__to')||'/';
      const t=new URL(raw,window.location.origin);
      if(t.origin===window.location.origin){
        target=t.pathname+t.search+t.hash;
      }
    }catch(_){}
    try{window.history.replaceState(null,'',target)}catch(_){}
  }
})();
/* Lex Talk Legal — shared publication controls */
(function(){
  const root=document.documentElement;
  const menuBtn=document.getElementById('menuTrigger');
  const menu=document.getElementById('megaMenu');
  const themeBtn=document.getElementById('themeBtn');
  function closeMenu(){
    if(!menu||!menuBtn)return;
    menu.hidden=true;menuBtn.setAttribute('aria-expanded','false');
  }
  if(menuBtn&&menu){
    menuBtn.addEventListener('click',e=>{e.stopPropagation();const open=menu.hidden;menu.hidden=!open;menuBtn.setAttribute('aria-expanded',open?'true':'false');});
    document.addEventListener('click',e=>{if(!menu.contains(e.target)&&e.target!==menuBtn)closeMenu();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape')closeMenu();});
    menu.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
  }
  function applyTheme(mode){
    root.dataset.theme=mode;
    try{localStorage.setItem('lexThemeV9',mode)}catch(_){ }
    if(themeBtn){
      themeBtn.textContent=mode==='dark'?'☼ Light':'☾ Dark';
      themeBtn.setAttribute('aria-label',mode==='dark'?'Switch to light mode':'Switch to dark mode');
    }
  }
  let stored=null;
  try{stored=localStorage.getItem('lexThemeV9')}catch(_){ }
  applyTheme(stored==='dark'?'dark':'light');
  themeBtn?.addEventListener('click',()=>applyTheme(root.dataset.theme==='dark'?'light':'dark'));
  function clock(){
    const d=new Date(),o={timeZone:'Asia/Kolkata'},dl=document.getElementById('dateLabel'),tl=document.getElementById('timeLabel');
    if(dl)dl.textContent=d.toLocaleDateString('en-IN',{...o,weekday:'long',day:'2-digit',month:'long',year:'numeric'});
    if(tl)tl.textContent=d.toLocaleTimeString('en-IN',{...o,hour12:false})+' IST';
  }
  clock();setInterval(clock,1000);
  function relativeUpdate(){
    const el=document.querySelector('[data-built-epoch]');if(!el)return;
    const epoch=Number(el.getAttribute('data-built-epoch'));if(!Number.isFinite(epoch))return;
    const now=Date.now(), mins=Math.max(0,Math.floor((now-epoch*1000)/60000));
    const label=mins<1?'just now':mins<60?mins+' min ago':Math.floor(mins/60)+' hr '+(mins%60)+' min ago';
    const exact=el.textContent||'';
    if(!el.dataset.exact)el.dataset.exact=exact;
    el.textContent='Content last updated: '+label;
    el.title=el.dataset.exact;
  }
  relativeUpdate();setInterval(relativeUpdate,60000);
})();
(function(){
  function ensureModal(){
    let bd=document.getElementById('vcModalBackdrop');if(bd)return bd;
    bd=document.createElement('div');bd.id='vcModalBackdrop';bd.className='vc-modal-backdrop';
    bd.innerHTML='<div class="vc-modal" role="dialog" aria-modal="true" aria-labelledby="vcModalTitle"><div class="vc-modal-head"><div><div class="vc-modal-kicker">PUBLIC COURT / VC LINK</div><h2 class="vc-modal-title" id="vcModalTitle">VC Link</h2></div><button class="vc-modal-close" type="button" aria-label="Close">×</button></div><div class="vc-modal-body"><p id="vcModalText"></p><div class="vc-modal-note" id="vcModalNote"></div></div><div class="vc-modal-actions"><button class="vc-modal-btn cancel" type="button">Cancel</button><button class="vc-modal-btn proceed" id="vcModalProceed" type="button">Proceed</button></div></div>';
    document.body.appendChild(bd);
    function close(){bd.classList.remove('is-open');document.body.classList.remove('vc-modal-open');window.__lexVCUrl='';}
    bd.querySelector('.vc-modal-close').onclick=close;bd.querySelector('.cancel').onclick=close;bd.addEventListener('click',e=>{if(e.target===bd)close()});document.addEventListener('keydown',e=>{if(e.key==='Escape')close()});
    bd.querySelector('.proceed').onclick=()=>{if(window.__lexVCUrl)window.open(window.__lexVCUrl,'_blank','noopener');close()};return bd;
  }
  document.addEventListener('click',e=>{
    const btn=e.target.closest('.vc-link');if(!btn||!btn.dataset.vcUrl)return;e.preventDefault();
    const bd=ensureModal();bd.querySelector('#vcModalTitle').textContent=btn.dataset.vcTitle||'VC Link';bd.querySelector('#vcModalText').textContent='You are about to open a public virtual-hearing destination in a new tab.';bd.querySelector('#vcModalNote').textContent='Verify the court number, date and current VC details against the concerned court or tribunal cause list before joining.';window.__lexVCUrl=btn.dataset.vcUrl;bd.classList.add('is-open');document.body.classList.add('vc-modal-open');
  });
})();
