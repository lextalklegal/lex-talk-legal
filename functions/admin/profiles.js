import { html, json, layout, adminEmail, esc, text } from "../_lib.js";

const app = `<main class="admin-page"><div class="utility-kicker">ADMIN CONSOLE</div><h1>Professional Profiles</h1><p class="lead">Review submissions, publish or suspend profiles, and add moderation notes. This console is intended to be protected by Cloudflare Access.</p><div id="adminNotice" class="notice">Loading profiles…</div><div class="admin-toolbar"><select id="status"><option value="pending">Pending</option><option value="under_review">Under Review</option><option value="approved">Published</option><option value="rejected">Rejected</option><option value="suspended">Suspended</option><option value="all">All</option></select><button class="admin-btn" id="refresh">Refresh</button></div><div id="list" class="admin-list"></div></main><script>
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const listEl=document.getElementById('list'), notice=document.getElementById('adminNotice'), statusEl=document.getElementById('status');
async function load(){notice.className='notice';notice.textContent='Loading…';listEl.innerHTML='';try{const r=await fetch('/api/admin/profiles?status='+encodeURIComponent(statusEl.value),{credentials:'same-origin',cache:'no-store'});const d=await r.json();if(!r.ok)throw new Error(d.error||'Request failed');notice.textContent='Admin access confirmed for '+esc(d.admin||'authorized user')+'.';(d.profiles||[]).forEach(render);}catch(e){notice.className='notice';notice.textContent=e.message;}}
function render(p){const el=document.createElement('article');el.className='admin-card';el.innerHTML='<div class="admin-card-head"><div><h2>'+esc(p.full_name)+'</h2><div class="lead">'+esc(p.state_bar_council)+' · Enrolment '+esc(p.enrolment_number)+' · '+esc(p.city)+', '+esc(p.state)+'</div></div><span class="admin-status">'+esc(p.status)+'</span></div><div class="profile-list" style="margin-top:13px"><div class="profile-item"><div class="profile-label">Qualification</div><div class="profile-value">'+esc(p.qualification)+'</div></div><div class="profile-item"><div class="profile-label">Year</div><div class="profile-value">'+esc(p.enrolment_year||'—')+'</div></div></div><p class="lead" style="margin-top:13px"><b>Bio:</b> '+esc(p.bio)+'</p><p class="lead"><b>Email:</b> '+esc(p.submitted_email)+'</p><textarea class="admin-note" placeholder="Review note (optional)">'+esc(p.review_notes||'')+'</textarea><div class="admin-actions"><button class="admin-btn" data-a="review">Mark Under Review</button><button class="admin-btn primary" data-a="approve">Approve & Publish</button><button class="admin-btn danger" data-a="reject">Reject</button><button class="admin-btn danger" data-a="suspend">Suspend</button><button class="admin-btn" data-a="note">Save Note</button></div>';
el.querySelectorAll('[data-a]').forEach(b=>b.addEventListener('click',()=>act(p.id,b.getAttribute('data-a'),el.querySelector('.admin-note').value)));listEl.appendChild(el)}
async function act(id,action,note){const r=await fetch('/api/admin/profiles',{method:'PATCH',credentials:'same-origin',headers:{'content-type':'application/json'},cache:'no-store',body:JSON.stringify({id,action,review_notes:note})});const d=await r.json();if(!r.ok){alert(d.error||'Action failed');return}load()}
document.getElementById('refresh').onclick=load;statusEl.onchange=load;load();
</script>`;

export async function onRequestGet(context){
  const admin = adminEmail(context.request, context.env);
  if(!admin) return html('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Admin Access Required</title></head><body style="font-family:Arial;padding:40px"><h1>Admin Access Required</h1><p>This area is protected. Sign in through the configured Cloudflare Access policy, then open <code>/admin/profiles</code>.</p></body></html>',401,{'WWW-Authenticate':'Cloudflare Access'});
  if(!context.env.DB) return html(layout('Professional Profile Admin','Lex Talk Legal admin console for professional profile moderation.',`<main class="admin-page"><div class="notice"><b>Database not configured.</b> Create the D1 database and bind it as <code>DB</code> before using profile moderation.</div></main>`,'https://lextalk.legal/admin/profiles'),503);
  return html(layout('Professional Profile Admin','Lex Talk Legal admin console for professional profile moderation.',app,'https://lextalk.legal/admin/profiles'));
}

export async function onRequestPatch(context){
  const admin = adminEmail(context.request, context.env);
  if(!admin) return json({error:'Unauthorized'},401,{'WWW-Authenticate':'Cloudflare Access'});
  if(!context.env.DB) return json({error:'Profile database is not configured.'},503);
  if(!['application/json','application/json; charset=utf-8'].includes((context.request.headers.get('content-type')||'').toLowerCase())) return json({error:'Content-Type must be application/json.'},415);

  let body;
  try { body = await context.request.json(); } catch { return json({error:'Invalid JSON body.'},400); }

  const id = text(body?.id,120);
  const action = text(body?.action,40).toLowerCase();
  const reviewNotes = text(body?.review_notes,2000);
  const allowed = new Set(['review','approve','reject','suspend','note']);
  if(!id || !allowed.has(action)) return json({error:'Invalid profile ID or moderation action.'},400);

  const existing = await context.env.DB.prepare('SELECT id, slug, status FROM profiles WHERE id=? LIMIT 1').bind(id).first();
  if(!existing) return json({error:'Profile not found.'},404);

  let status = existing.status;
  if(action==='review') status='under_review';
  if(action==='approve') status='approved';
  if(action==='reject') status='rejected';
  if(action==='suspend') status='suspended';

  const now = new Date().toISOString();
  if(action==='note') {
    await context.env.DB.prepare('UPDATE profiles SET review_notes=?, updated_at=? WHERE id=?').bind(reviewNotes || null, now, id).run();
  } else if(action==='approve') {
    await context.env.DB.prepare('UPDATE profiles SET status=?, review_notes=?, updated_at=?, published_at=COALESCE(published_at, ?) WHERE id=?').bind(status, reviewNotes || null, now, now, id).run();
  } else {
    await context.env.DB.prepare('UPDATE profiles SET status=?, review_notes=?, updated_at=? WHERE id=?').bind(status, reviewNotes || null, now, id).run();
  }

  const auditId = crypto.randomUUID();
  await context.env.DB.prepare('INSERT INTO audit_log (id, profile_id, actor_type, actor_email, action, details_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)')
    .bind(auditId, id, 'admin', admin, action, JSON.stringify({from_status: existing.status, to_status: status, note_added: !!reviewNotes}), now).run();

  return json({ok:true, id, status, action, admin});
}
