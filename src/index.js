export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      if (/^\/admin(?:\/|$)/.test(url.pathname)) return Response.redirect(new URL('/', request.url), 302);
      if (/^\/advocates(?:\/|$)/.test(url.pathname)) return Response.redirect(new URL('/team.html', request.url), 301);

      if (url.pathname === "/creator-studio/grap" || url.pathname === "/creator-studio/grap/") {
        if (request.method !== "GET") return new Response("Method not allowed.", {status:405, headers:{"allow":"GET","cache-control":"no-store"}});
        return new Response(CREATOR_STUDIO_HTML, {status:200, headers:PRIVATE_HTML_HEADERS});
      }
      if (url.pathname === "/api/private/grap-script") {
        if (request.method !== "POST") return new Response("Method not allowed.", {status:405, headers:{"allow":"POST","cache-control":"no-store"}});
        const origin = request.headers.get("Origin");
        if (!origin || new URL(origin).origin !== url.origin) return new Response("Forbidden.", {status:403, headers:PRIVATE_JSON_HEADERS});
        if (!(request.headers.get("Content-Type") || "").toLowerCase().includes("application/json")) return new Response("Unsupported media type.", {status:415, headers:PRIVATE_JSON_HEADERS});
        const contentLength = Number(request.headers.get("Content-Length") || "0");
        if (contentLength > 1024) return new Response("Request too large.", {status:413, headers:PRIVATE_JSON_HEADERS});
        let payload;
        try { payload = await request.json(); } catch (_) { return new Response("Bad request.", {status:400, headers:PRIVATE_JSON_HEADERS}); }
        if (!env.CREATOR_ACCESS_CODE || !env.GRAP_CREATOR_SCRIPT_HTML) return new Response("Creator studio is not configured.", {status:503, headers:PRIVATE_JSON_HEADERS});
        const submitted = payload && typeof payload.code === "string" ? payload.code : "";
        if (!constantTimeTextEqual(submitted, env.CREATOR_ACCESS_CODE)) return new Response("Access denied.", {status:401, headers:PRIVATE_JSON_HEADERS});
        return Response.json({html:env.GRAP_CREATOR_SCRIPT_HTML}, {status:200, headers:PRIVATE_JSON_HEADERS});
      }
      return await env.ASSETS.fetch(request);
    } catch (_) {
      return new Response("Lex Talk Legal — Temporary service error.", {status:503, headers:PRIVATE_JSON_HEADERS});
    }
  }
};
const PRIVATE_HTML_HEADERS = {
  "content-type":"text/html; charset=UTF-8","cache-control":"private, no-store, no-cache, must-revalidate","pragma":"no-cache",
  "x-content-type-options":"nosniff","x-frame-options":"DENY","x-robots-tag":"noindex, nofollow, noarchive","referrer-policy":"no-referrer",
  "content-security-policy":"default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
};
const PRIVATE_JSON_HEADERS = {
  "content-type":"application/json; charset=UTF-8","cache-control":"private, no-store, no-cache, must-revalidate","pragma":"no-cache",
  "x-content-type-options":"nosniff","x-robots-tag":"noindex, nofollow, noarchive","referrer-policy":"no-referrer"
};
function constantTimeTextEqual(a,b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  const left = new TextEncoder().encode(a), right = new TextEncoder().encode(b);
  if (left.length !== right.length) return false;
  let diff = 0; for (let i=0;i<left.length;i++) diff |= left[i] ^ right[i];
  return diff === 0;
}
const CREATOR_STUDIO_HTML = "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n<meta name=\"robots\" content=\"noindex,nofollow,noarchive\"><title>Private Video Creator Studio | Lex Talk Legal</title>\n<style>\n:root{color-scheme:dark;--bg:#09111f;--panel:#111e30;--line:#2d415c;--white:#f4f7fb;--muted:#aab8ca;--red:#ff5664;--gold:#f5c76b}\n*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 80% 0%,#18263a,transparent 42%),var(--bg);color:var(--white);font:15px/1.65 Arial,sans-serif}main{max-width:1080px;margin:0 auto;padding:36px 20px 64px}\n.eyebrow{color:var(--red);font-size:11px;font-weight:800;letter-spacing:1.8px;text-transform:uppercase}h1{font:700 clamp(30px,5vw,44px)/1.12 Georgia,serif;margin:9px 0 12px}h2{font:700 26px/1.2 Georgia,serif}p{color:var(--muted)}\n.panel{margin-top:24px;padding:24px;border:1px solid var(--line);border-radius:15px;background:rgba(17,30,48,.9)}label{display:block;font-size:13px;font-weight:700;margin-bottom:7px}\ninput{width:100%;max-width:440px;display:block;padding:13px 14px;border-radius:8px;border:1px solid #526680;background:#07101d;color:var(--white);font:16px Arial}button{margin-top:12px;padding:12px 16px;border:0;border-radius:8px;background:var(--gold);color:#111827;font-weight:800;cursor:pointer}\nbutton:focus-visible,input:focus-visible,a:focus-visible{outline:3px solid var(--red);outline-offset:3px}#status{min-height:24px;font-size:13px}.help-link{display:inline-block;margin-top:12px;color:#ff8992;text-underline-offset:3px}.small{font-size:12px}\n.narration{margin-top:24px}.narration-intro{font-size:14px}.script-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.script-card{border:1px solid var(--line);background:#0c1828;border-radius:10px;padding:16px}\n.script-card .time{font-size:11px;font-weight:800;letter-spacing:.5px;color:var(--red);text-transform:uppercase}.script-card h3{font-size:16px;margin:8px 0}.script-card p{font-size:14px;color:#d5dfeb;margin:0}\n.source-note{margin-top:18px;padding:15px 17px;background:#0d1a29;border-left:3px solid var(--red);font-size:12px;color:var(--muted)}.source-note a{color:#ff8992;text-underline-offset:3px}\n@media(max-width:700px){main{padding:24px 14px 40px}.panel{padding:18px}.script-grid{grid-template-columns:1fr}}\n</style></head><body><main>\n<div class=\"eyebrow\">Lex Talk Legal · Private workspace</div><h1>Video Creator Studio</h1>\n<p>This page contains creator-only Hinglish voiceover cues and recording notes. The access code is checked by the site Worker; it is not embedded in this page.</p>\n<div id=\"loginPanel\" class=\"panel\"><form id=\"unlockForm\"><label for=\"creatorCode\">Creator access code</label>\n<input id=\"creatorCode\" name=\"creatorCode\" type=\"password\" autocomplete=\"current-password\" required maxlength=\"128\" aria-describedby=\"status\">\n<button id=\"unlockButton\" type=\"submit\">Unlock private notes</button><p id=\"status\" role=\"status\" aria-live=\"polite\"></p></form>\n<p class=\"small\">Notes are fetched only after successful verification and are not saved by this page. Use a trusted device and close the tab when finished.</p>\n<a class=\"help-link\" href=\"/video-tools/delhi-grap-stage-i-explainer.html\">Open the public animated GRAP explainer ↗</a></div>\n<div id=\"notesPanel\" class=\"panel\" hidden><div style=\"display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap\">\n<div><div class=\"eyebrow\">Private creator notes</div><h2>Hinglish voiceover &amp; source cues</h2></div><button id=\"lockButton\" type=\"button\">Lock &amp; clear notes</button></div>\n<div id=\"notesContent\"></div><p class=\"small\">Attribute claims to their sources and re-check the latest CAQM direction before recording time-sensitive restrictions.</p>\n<a class=\"help-link\" href=\"/video-tools/delhi-grap-stage-i-explainer.html\" target=\"_blank\" rel=\"noopener noreferrer\">Open the animation in another tab ↗</a></div>\n</main><script>\n(function(){var form=document.getElementById('unlockForm'),input=document.getElementById('creatorCode'),status=document.getElementById('status'),button=document.getElementById('unlockButton'),login=document.getElementById('loginPanel'),notes=document.getElementById('notesPanel'),content=document.getElementById('notesContent');\nform.addEventListener('submit',async function(event){event.preventDefault();var code=input.value;input.value='';status.textContent='Checking access…';button.disabled=true;\ntry{var response=await fetch('/api/private/grap-script',{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'content-type':'application/json'},body:JSON.stringify({code:code})});var data=await response.json();if(!response.ok||!data||typeof data.html!=='string')throw new Error('invalid');content.innerHTML=data.html;login.hidden=true;notes.hidden=false;status.textContent='';window.scrollTo({top:0,behavior:'auto'});}\ncatch(_){status.textContent='Code incorrect, or private notes are temporarily unavailable. Please try again.';input.focus();}\nfinally{button.disabled=false;}});\ndocument.getElementById('lockButton').addEventListener('click',function(){content.replaceChildren();notes.hidden=true;login.hidden=false;input.value='';status.textContent='Private notes cleared from this page.';input.focus();});})();\n</script></body></html>";
