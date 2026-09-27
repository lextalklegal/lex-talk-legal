
(function(){
  function pad(n){return String(n).padStart(2,'0')}
  function updateClock(){
    const now=new Date();
    const opts={timeZone:'Asia/Kolkata',year:'numeric',month:'short',day:'2-digit'};
    const date=now.toLocaleDateString('en-IN',opts);
    const time=now.toLocaleTimeString('en-IN',{timeZone:'Asia/Kolkata',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:true});
    document.querySelectorAll('[data-ist-date]').forEach(e=>e.textContent=date);
    document.querySelectorAll('[data-ist-time]').forEach(e=>e.textContent=time+' IST');
  }
  updateClock(); setInterval(updateClock,1000);

  const saved=localStorage.getItem('ltl-theme');
  if(saved==='dark') document.body.classList.add('dark');
  document.querySelectorAll('[data-theme-toggle]').forEach(btn=>{
    btn.addEventListener('click',()=>{
      document.body.classList.toggle('dark');
      localStorage.setItem('ltl-theme',document.body.classList.contains('dark')?'dark':'light');
    });
  });

  document.querySelectorAll('[data-lang-toggle]').forEach(btn=>{
    btn.addEventListener('click',()=>{
      const lang=document.documentElement.lang==='hi'?'en':'hi';
      document.documentElement.lang=lang;
      document.querySelectorAll('[data-lang-toggle]').forEach(b=>b.textContent=lang==='hi'?'EN':'हिन्दी');
    });
  });
})();
