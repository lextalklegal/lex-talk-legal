(function(){
  const root=document.documentElement;
  const langBtn=document.getElementById('langBtn');
  const themeBtn=document.getElementById('themeBtn');

  function currentLang(){
    const m=document.cookie.match(/(?:^|;\s*)googtrans=([^;]+)/);
    if(m){ const v=decodeURIComponent(m[1]); if(v.endsWith('/hi')) return 'hi'; }
    return localStorage.getItem('lex-lang')==='hi' ? 'hi' : 'en';
  }

  function setButton(){
    const hi=currentLang()==='hi';
    root.lang=hi?'hi':'en';
    if(langBtn) langBtn.textContent=hi?'English':'हिन्दी';
  }

  function setGoogleCookie(lang){
    if(lang==='hi'){
      const value='/en/hi';
      document.cookie='googtrans='+value+';path=/';
    }else{
      document.cookie='googtrans=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
    }
    localStorage.setItem('lex-lang',lang);
  }

  if(langBtn){
    langBtn.addEventListener('click',function(){
      const next=currentLang()==='hi'?'en':'hi';
      setGoogleCookie(next);
      location.reload();
    });
  }

  const savedTheme=localStorage.getItem('lex-theme');
  if(savedTheme) root.dataset.theme=savedTheme;
  if(themeBtn){
    themeBtn.textContent=root.dataset.theme==='dark'?'☀ Light':'☾ Dark';
    themeBtn.addEventListener('click',function(){
      root.dataset.theme=root.dataset.theme==='dark'?'':'dark';
      localStorage.setItem('lex-theme',root.dataset.theme);
      themeBtn.textContent=root.dataset.theme==='dark'?'☀ Light':'☾ Dark';
    });
  }

  function clock(){
    const d=new Date();
    const o={timeZone:'Asia/Kolkata'};
    const dl=document.getElementById('dateLabel');
    const tl=document.getElementById('timeLabel');
    if(dl) dl.textContent=d.toLocaleDateString('en-IN',{...o,weekday:'long',day:'2-digit',month:'long',year:'numeric'});
    if(tl) tl.textContent=d.toLocaleTimeString('en-IN',{...o,hour12:false})+' IST';
  }
  clock(); setInterval(clock,1000); setButton();

  window.googleTranslateElementInit=function(){
    try{
      if(window.google && google.translate && google.translate.TranslateElement){
        new google.translate.TranslateElement({pageLanguage:'en',includedLanguages:'en,hi',autoDisplay:false},'google_translate_element');
        if(currentLang()==='hi'){
          setTimeout(function(){
            const select=document.querySelector('.goog-te-combo');
            if(select){ select.value='hi'; select.dispatchEvent(new Event('change')); }
          },500);
        }
      }
    }catch(e){}
  };

  const script=document.createElement('script');
  script.src='https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
  script.async=true;
  document.head.appendChild(script);
})();

// Courtroom VC confirmation / unavailable message
(function(){
  function ensureModal(){
    let bd=document.getElementById('vcModalBackdrop');
    if(bd) return bd;
    bd=document.createElement('div');
    bd.id='vcModalBackdrop'; bd.className='vc-modal-backdrop';
    bd.innerHTML='<div class="vc-modal" role="dialog" aria-modal="true" aria-labelledby="vcModalTitle">'
      +'<div class="vc-modal-head"><div><div class="vc-modal-kicker">PUBLIC COURT / VC LINK</div><h2 class="vc-modal-title" id="vcModalTitle">VC Link</h2></div><button class="vc-modal-close" type="button" aria-label="Close">×</button></div>'
      +'<div class="vc-modal-body"><p id="vcModalText"></p><div class="vc-modal-note" id="vcModalNote"></div></div>'
      +'<div class="vc-modal-actions"><button class="vc-modal-btn cancel" type="button">Cancel</button><button class="vc-modal-btn proceed" id="vcModalProceed" type="button">Proceed to VC</button></div>'
      +'</div>';
    document.body.appendChild(bd);
    function close(){bd.classList.remove('is-open');document.body.classList.remove('vc-modal-open');window.__lexVCUrl='';}
    bd.querySelector('.vc-modal-close').addEventListener('click',close);
    bd.querySelector('.cancel').addEventListener('click',close);
    bd.addEventListener('click',function(e){if(e.target===bd) close();});
    document.addEventListener('keydown',function(e){if(e.key==='Escape') close();});
    bd.querySelector('.proceed').addEventListener('click',function(){const u=window.__lexVCUrl;if(u){window.open(u,'_blank','noopener');close();}});
    return bd;
  }
  document.addEventListener('click',function(e){
    const btn=e.target.closest('.vc-link');
    if(!btn) return;
    e.preventDefault();
    const bd=ensureModal();
    const title=btn.getAttribute('data-vc-title')||'VC Link';
    const url=btn.getAttribute('data-vc-url')||'';
    bd.querySelector('#vcModalTitle').textContent=title;
    const txt=bd.querySelector('#vcModalText');
    const note=bd.querySelector('#vcModalNote');
    const proceed=bd.querySelector('#vcModalProceed');
    if(url){
      txt.textContent='You are about to open the public virtual-hearing destination for this court / courtroom in a new tab.';
      note.textContent='Please verify the court number, date and current VC details against the concerned court / tribunal cause list before joining.';
      proceed.style.display='inline-block';
      proceed.textContent='Proceed to VC';
    }else{
      txt.textContent='A direct public VC link is not available for this court in the latest automated sync.';
      note.textContent='Please refer to the current cause list or contact the concerned Court Registrar, Courtroom Master or Reader for the current hearing instructions.';
      proceed.style.display='none';
    }
    window.__lexVCUrl=url;
    bd.classList.add('is-open'); document.body.classList.add('vc-modal-open');
  });
})();
