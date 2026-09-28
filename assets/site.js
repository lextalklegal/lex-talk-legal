(function(){
  const root=document.documentElement;
  const langBtn=document.getElementById('langBtn');
  const themeBtn=document.getElementById('themeBtn');
  if(localStorage.getItem('lex-lang-version')!=='v5'){
    localStorage.setItem('lex-lang','en');
    localStorage.setItem('lex-lang-version','v5');
  }
  const T={
    en:{latest:'Latest',courts:'Courts',lawPolicy:'Law & Policy',bankingLaw:'Banking Law',drtDrat:'DRT / DRAT',legalCareers:'Legal Careers',dra:'DRA',legalProfessionals:'Legal Professionals',bareActs:'Bare Acts',courtrooms:'Courtrooms',caseStatus:'Case Status',videos:'Videos',hindi:'हिन्दी',english:'English',dark:'☾ Dark',light:'☀ Light',breaking:'BREAKING',tick:'Legal news • Courts • Judgments • Law & Policy • DRT/DRAT • Legal Careers • Legal Explainers',legalUtility:'LEGAL UTILITY',legalKnowledge:'LEGAL KNOWLEDGE',legalCommunity:'LEGAL COMMUNITY',quickLinks:'Quick Links',utilities:'Legal Utilities',latestVideos:'Latest Videos',communityTitle:'Build Your Free Professional Profile',communityText:'Lex Talk Legal is developing an informational legal-professional community where advocates can maintain a free public professional profile, share knowledge and connect with the wider legal community. Profiles are reviewed before publication.',communityFree:'Profile creation is free',communityReview:'Submitted information is reviewed',communitySearch:'Published profiles can be discoverable',noPaidRanking:'NO PAID RANKING',communitySide:'Informational profiles. No star ratings, paid ranking, guaranteed results or “best lawyer” claims.',exploreProfiles:'Explore Profiles ↗',readStory:'Read Story ↗',watchYouTube:'Watch on YouTube',privacy:'Privacy',terms:'Terms',disclaimer:'Disclaimer',editorial:'Editorial Policy',copyright:'Copyright / Takedown',corrections:'Corrections & Grievance',aiPolicy:'AI Content Policy',advertise:'Advertise With Us'},
    hi:{latest:'ताज़ा',courts:'न्यायालय',lawPolicy:'कानून और नीति',bankingLaw:'बैंकिंग कानून',drtDrat:'DRT / DRAT',legalCareers:'कानूनी करियर',dra:'DRA',legalProfessionals:'कानूनी पेशेवर',bareActs:'Bare Acts',courtrooms:'कोर्टरूम',caseStatus:'केस स्टेटस',videos:'वीडियो',hindi:'हिन्दी',english:'English',dark:'☾ डार्क',light:'☀ लाइट',breaking:'ब्रेकिंग',tick:'कानूनी समाचार • न्यायालय • फैसले • कानून और नीति • DRT/DRAT • कानूनी करियर • कानूनी जानकारी',legalUtility:'कानूनी उपयोगिता',legalKnowledge:'कानूनी जानकारी',legalCommunity:'कानूनी समुदाय',quickLinks:'त्वरित लिंक',utilities:'कानूनी उपयोगिताएँ',latestVideos:'ताज़ा वीडियो',communityTitle:'अपनी निःशुल्क प्रोफेशनल प्रोफाइल बनाएं',communityText:'Lex Talk Legal एक सूचनात्मक कानूनी-पेशेवर समुदाय विकसित कर रहा है, जहाँ अधिवक्ता निःशुल्क सार्वजनिक प्रोफेशनल प्रोफाइल रख सकते हैं, ज्ञान साझा कर सकते हैं और व्यापक कानूनी समुदाय से जुड़ सकते हैं। प्रोफाइल प्रकाशन से पहले समीक्षा की जाती है।',communityFree:'प्रोफाइल बनाना निःशुल्क है',communityReview:'जमा की गई जानकारी की समीक्षा होती है',communitySearch:'प्रकाशित प्रोफाइल खोज इंजनों द्वारा खोजी जा सकती हैं',noPaidRanking:'पेड रैंकिंग नहीं',communitySide:'सूचनात्मक प्रोफाइल। कोई स्टार रेटिंग, पेड रैंकिंग, परिणाम की गारंटी या “बेस्ट लॉयर” जैसे दावे नहीं।',exploreProfiles:'प्रोफाइल देखें ↗',readStory:'स्टोरी पढ़ें ↗',watchYouTube:'YouTube पर देखें',privacy:'गोपनीयता',terms:'उपयोग की शर्तें',disclaimer:'डिस्क्लेमर',editorial:'एडिटोरियल नीति',copyright:'कॉपीराइट / टेकडाउन',corrections:'सुधार और शिकायत',aiPolicy:'AI कंटेंट नीति',advertise:'हमारे साथ विज्ञापन करें'}
  };
  function lang(){return localStorage.getItem('lex-lang')==='hi'?'hi':'en';}
  function applyLanguage(l){
    l=l==='hi'?'hi':'en'; root.lang=l; localStorage.setItem('lex-lang',l);
    document.querySelectorAll('[data-i18n]').forEach(el=>{const k=el.getAttribute('data-i18n');if(T[l][k]!==undefined)el.textContent=T[l][k];});
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>{const k=el.getAttribute('data-i18n-placeholder');if(T[l][k]!==undefined)el.setAttribute('placeholder',T[l][k]);});
    if(langBtn)langBtn.textContent=l==='hi'?T.en.english:T.en.hindi;
    if(themeBtn)themeBtn.textContent=root.dataset.theme==='dark'?T[l].light:T[l].dark;
    window.dispatchEvent(new CustomEvent('lex-language-change',{detail:{lang:l}}));
  }
  if(langBtn)langBtn.addEventListener('click',()=>applyLanguage(lang()==='hi'?'en':'hi'));
  const savedTheme=localStorage.getItem('lex-theme');if(savedTheme)root.dataset.theme=savedTheme;
  if(themeBtn)themeBtn.addEventListener('click',()=>{root.dataset.theme=root.dataset.theme==='dark'?'':'dark';localStorage.setItem('lex-theme',root.dataset.theme);applyLanguage(lang());});
  function clock(){const d=new Date(),o={timeZone:'Asia/Kolkata'},l=lang();const dl=document.getElementById('dateLabel'),tl=document.getElementById('timeLabel');if(dl)dl.textContent=d.toLocaleDateString(l==='hi'?'hi-IN':'en-IN',{...o,weekday:'long',day:'2-digit',month:'long',year:'numeric'});if(tl)tl.textContent=d.toLocaleTimeString('en-IN',{...o,hour12:false})+' IST';}
  clock();setInterval(clock,1000);applyLanguage(lang());
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

// Homepage headline slider and floating quick links
(function(){
  const slider=document.getElementById('heroSlider');
  if(slider){
    const slides=[...slider.querySelectorAll('.hero-slide')];
    const dots=[...slider.querySelectorAll('.hero-dots button')];
    let idx=slides.findIndex(x=>x.classList.contains('active')); if(idx<0) idx=0;
    let timer;
    function show(n){
      if(!slides.length) return;
      idx=(n+slides.length)%slides.length;
      slides.forEach((s,i)=>s.classList.toggle('active',i===idx));
      dots.forEach((d,i)=>d.classList.toggle('active',i===idx));
    }
    function restart(){clearInterval(timer); if(slides.length>1) timer=setInterval(()=>show(idx+1),6500);}
    dots.forEach((d,i)=>d.addEventListener('click',()=>{show(i);restart();}));
    const prev=slider.querySelector('.hero-arrow.prev'), next=slider.querySelector('.hero-arrow.next');
    if(prev) prev.addEventListener('click',()=>{show(idx-1);restart();});
    if(next) next.addEventListener('click',()=>{show(idx+1);restart();});
    slider.addEventListener('mouseenter',()=>clearInterval(timer));
    slider.addEventListener('mouseleave',restart);
    show(idx); restart();
  }

  const float=document.getElementById('floatingQuick');
  if(float){
    const toggle=float.querySelector('.floating-toggle');
    function close(){float.classList.remove('open'); if(toggle) toggle.setAttribute('aria-expanded','false');}
    if(toggle) toggle.addEventListener('click',e=>{e.stopPropagation(); const open=!float.classList.contains('open'); float.classList.toggle('open',open); toggle.setAttribute('aria-expanded',open?'true':'false');});
    document.addEventListener('click',e=>{if(!float.contains(e.target)) close();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape') close();});
  }

  document.querySelectorAll('.auction-widget').forEach(box=>{
    const themes=['Residential Property','Commercial Property','Industrial Asset','Plot / Land','Vehicle Auction','Bank-Owned Asset'];
    const theme=box.querySelector('.auction-theme');
    if(theme) theme.textContent=themes[Math.floor(Math.random()*themes.length)];
  });

  const observer=('IntersectionObserver' in window)?new IntersectionObserver(entries=>{
    entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-visible');observer.unobserve(entry.target);}});
  },{threshold:.12}):null;
  if(observer) document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));
})();
