(function(){
  try{
    const u=new URL(location.href);
    if(u.pathname==='/__legacy-bridge/'){
      const raw=u.searchParams.get('__to')||'/';
      const target=new URL(raw,u.origin);
      if(target.origin===u.origin){
        const clean=target.pathname+(target.search||'')+(target.hash||'');
        history.replaceState(null,'',clean||'/');
      }
    }
  }catch(_){}
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
  async function hydrateBuildTimestamp(){
    const els=[...document.querySelectorAll('.updated-line')];
    if(!els.length)return;
    try{
      const r=await fetch('/data/site_meta.json?ts='+Date.now(),{cache:'no-store'});
      if(!r.ok)return;
      const data=await r.json();
      const label=String(data.built_at_ist||'').trim();
      if(!label)return;
      els.forEach(el=>{el.textContent='Content last updated: '+label;if(data.built_at_epoch)el.dataset.builtEpoch=String(data.built_at_epoch);});
    }catch(_){}
  }
  hydrateBuildTimestamp();
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

/* Lex Talk Legal — GA4 interaction tracking */
(function(){
  function track(name,params){try{if(typeof window.gtag==='function')window.gtag('event',name,params||{});}catch(_){} }
  document.addEventListener('click',function(e){
    const a=e.target.closest('a'); if(!a)return;
    const href=a.getAttribute('href')||'';
    const text=(a.innerText||'').trim().slice(0,100);
    if(a.dataset.gaEvent){track(a.dataset.gaEvent,{campaign:a.dataset.gaCampaign||undefined,link_url:a.href,link_text:text});return;}
    if(/passthebar\.org/i.test(href)){track('sponsor_click',{campaign:'aibe100',link_url:a.href,link_text:text});return;}
    if(/youtube\.com/i.test(href)){track('youtube_click',{link_url:a.href,link_text:text});return;}
    if(/^mailto:/i.test(href)){track('contact_click',{method:'email',link_text:text});return;}
    try{if(/(^|\.)wa\.me$/i.test(new URL(href,location.href).hostname)){track('whatsapp_click',{link_url:a.href});return;}}catch(_){}
    if(a.target==='_blank'&&/^https?:/i.test(href)){track('external_link_click',{link_url:a.href,link_text:text});}
  });
})();
