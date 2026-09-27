(function(){
const root=document.documentElement;
const themeBtn=document.getElementById("themeBtn");
const langBtn=document.getElementById("langBtn");

function setTheme(){
  const s=localStorage.getItem("lex-theme");
  if(s) root.dataset.theme=s;
  if(themeBtn) themeBtn.textContent=root.dataset.theme==="dark"?"☀ Light":"☾ Dark";
}
if(themeBtn) themeBtn.onclick=()=>{
  root.dataset.theme=root.dataset.theme==="dark"?"":"dark";
  localStorage.setItem("lex-theme",root.dataset.theme);
  themeBtn.textContent=root.dataset.theme==="dark"?"☀ Light":"☾ Dark";
};
setTheme();

function translateTo(lang){
  const select=document.querySelector(".goog-te-combo");
  if(!select) return false;
  select.value=lang;
  select.dispatchEvent(new Event("change"));
  return true;
}
window.lexApplyLanguage=function(){
  const lang=localStorage.getItem("lex-lang")||"en";
  if(langBtn) langBtn.textContent=lang==="hi"?"English":"हिन्दी";
  if(lang==="hi"){
    let tries=0;
    const go=()=>{ if(translateTo("hi")||tries++>24) return; setTimeout(go,250); };
    go();
  } else {
    translateTo("en");
  }
};
if(langBtn) langBtn.onclick=()=>{
  const next=(localStorage.getItem("lex-lang")||"en")==="hi"?"en":"hi";
  localStorage.setItem("lex-lang",next);
  langBtn.textContent=next==="hi"?"English":"हिन्दी";
  if(!translateTo(next)) window.lexApplyLanguage();
};

const saved=localStorage.getItem("lex-lang");
if(saved) root.lang=saved;
function c(){
  const d=new Date(),o={timeZone:"Asia/Kolkata"};
  const dl=document.getElementById("dateLabel"),tl=document.getElementById("timeLabel");
  if(dl) dl.textContent=d.toLocaleDateString("en-IN",{...o,weekday:"long",day:"2-digit",month:"long",year:"numeric"});
  if(tl) tl.textContent=d.toLocaleTimeString("en-IN",{...o,hour12:false})+" IST";
}
c();setInterval(c,1000);
})();