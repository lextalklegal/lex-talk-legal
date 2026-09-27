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
