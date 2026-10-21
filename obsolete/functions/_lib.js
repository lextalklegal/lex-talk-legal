const SITE_ORIGIN = "https://lextalk.legal";

export function json(data, status = 200, extra = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...extra }
  });
}

export function html(body, status = 200, extra = {}) {
  return new Response(body, {
    status,
    headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", ...extra }
  });
}

export function esc(value = "") {
  return String(value).replace(/[&<>\"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
}

export function text(value, max = 1000) {
  return String(value ?? "").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim().slice(0, max);
}

export function list(value, maxItems = 12, itemMax = 80) {
  if (Array.isArray(value)) return value.map(x => text(x, itemMax)).filter(Boolean).slice(0, maxItems);
  return String(value ?? "").split(/[\n,]+/).map(x => text(x, itemMax)).filter(Boolean).slice(0, maxItems);
}

export function validEmail(value) {
  const e = text(value, 160).toLowerCase();
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(e) ? e : null;
}

export function safeUrl(value, allowedHosts = []) {
  const raw = text(value, 500);
  if (!raw) return null;
  try {
    const u = new URL(raw);
    if (u.protocol !== "https:") return null;
    if (allowedHosts.length && !allowedHosts.includes(u.hostname.toLowerCase())) return null;
    return u.href;
  } catch { return null; }
}

export function slugify(value) {
  return text(value, 120).toLowerCase().normalize("NFKD").replace(/[^a-z0-9\s-]/g, "").trim().replace(/\s+/g, "-").replace(/-+/g, "-").slice(0, 70) || "advocate";
}

export function initial(name) {
  const s = text(name, 120).replace(/^(adv\.?|advocate)\s+/i, "").trim();
  return (s[0] || "L").toUpperCase();
}

export function requestOriginAllowed(request, env = {}) {
  const origin = request.headers.get("Origin");
  if (!origin) return true;
  try {
    const requestOrigin = new URL(request.url).origin;
    if (origin === SITE_ORIGIN || origin === requestOrigin) return true;
    const extra = text(env.ALLOWED_ORIGINS, 2000).split(",").map(x => x.trim()).filter(Boolean);
    return extra.includes(origin);
  } catch { return false; }
}

export function adminEmail(request, env) {
  const email = text(request.headers.get("CF-Access-Authenticated-User-Email"), 160).toLowerCase();
  const allowed = text(env.ADMIN_EMAILS, 2000).split(",").map(x => x.trim().toLowerCase()).filter(Boolean);
  if (!email || !allowed.includes(email)) return null;
  return email;
}

export async function hashIp(ip, salt = "lex-talk-legal") {
  const data = new TextEncoder().encode(`${salt}|${ip}`);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(digest)].map(x => x.toString(16).padStart(2, "0")).join("");
}

export function layout(title, description, content, canonical = SITE_ORIGIN + "/") {
  const safeTitle = esc(title);
  const safeDescription = esc(description);
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="${safeDescription}"><link rel="canonical" href="${esc(canonical,500)}"><meta property="og:title" content="${safeTitle}"><meta property="og:description" content="${safeDescription}"><meta property="og:type" content="profile"><meta property="og:url" content="${esc(canonical,500)}"><meta name="twitter:card" content="summary"><title>${safeTitle} | Lex Talk Legal</title><link rel="stylesheet" href="/assets/site.css"></head><body><div class="top"></div><div class="utility"><div class="wrap"><div class="live-info"><span class="dot">●</span><span id="dateLabel">--</span><span>|</span><span id="timeLabel">--:--:-- IST</span><span>|</span><span>India</span></div><div class="controls"><button class="control" id="langBtn" type="button" aria-label="Switch language">हिन्दी</button><button class="control" id="themeBtn" type="button" aria-label="Switch theme">☾ Dark</button></div></div></div><header class="masthead"><a href="/" aria-label="Lex Talk Legal Home"><img src="/assets/LexTalkLegal_Logo-wo-bg.png" alt="Lex Talk Legal"></a></header><nav class="nav"><div class="wrap"><a href="/" data-i18n="latest">Latest</a><a href="/category/courts/" data-i18n="courts">Courts</a><a href="/category/law-policy/" data-i18n="lawPolicy">Law &amp; Policy</a><a href="/category/banking-law/" data-i18n="bankingLaw">Banking Law</a><a href="/category/drt-drat/" data-i18n="drtDrat">DRT / DRAT</a><a href="/category/legal-careers/" data-i18n="legalCareers">Legal Careers</a><a href="/category/dra/" data-i18n="dra">DRA</a><a class="active" href="/advocates/" data-i18n="legalProfessionals">Legal Professionals</a><a href="https://indiacode.gov.in/" target="_blank" rel="noopener" data-i18n="bareActs">Bare Acts</a><a href="/videos/" data-i18n="videos">Videos</a></div></nav>${content}<footer><div class="footergrid"><div><h3>Lex Talk Legal</h3><p>Law Simplified for Everyone.<br>Digital Legal News &amp; Legal Education Platform.</p></div><div><h3>Community</h3><ul><li><a href="/advocates/">Legal Professionals</a></li><li><a href="/advocates/apply.html">Create Free Profile</a></li><li><a href="/profile-guidelines.html">Profile Guidelines</a></li><li><a href="/videos/">Latest Videos</a></li></ul></div><div><h3>Connect</h3><ul><li><a href="https://www.youtube.com/@lextalklegal" target="_blank" rel="noopener">YouTube</a></li><li><a href="https://www.instagram.com/lex_talk_legal" target="_blank" rel="noopener">Instagram</a></li><li><a href="https://x.com/Lex_Talk_Legal" target="_blank" rel="noopener">X</a></li><li><a href="https://in.linkedin.com/company/lextalklegal" target="_blank" rel="noopener">LinkedIn</a></li></ul></div><div><h3>Legal</h3><ul><li><a href="/privacy-policy.html">Privacy</a></li><li><a href="/terms-of-use.html">Terms</a></li><li><a href="/disclaimer.html">Disclaimer</a></li><li><a href="/copyright-policy.html">Copyright / Takedown</a></li><li><a href="/corrections-grievance.html">Corrections &amp; Grievance</a></li></ul></div></div><div class="copy">© 2026 LEXBOTICS AI MEDIA LLP | Lex Talk Legal | For Educational &amp; Informational Use Only</div></footer><script src="/assets/site.js" defer></script></body></html>`;
}

export function profileData(row) {
  return {
    id: row.id, slug: row.slug, profile_type: row.profile_type, status: row.status,
    full_name: row.full_name, designation: row.designation, state_bar_council: row.state_bar_council,
    enrolment_number: row.enrolment_number, enrolment_year: row.enrolment_year, qualification: row.qualification,
    city: row.city, state: row.state, bio: row.bio,
    practice_areas: safeJsonArray(row.practice_areas_json), courts: safeJsonArray(row.courts_json),
    professional_website: row.professional_website, linkedin_url: row.linkedin_url, photo_url: row.photo_url,
    created_at: row.created_at, updated_at: row.updated_at, published_at: row.published_at,
    review_notes: row.review_notes ?? null, submitted_email: row.submitted_email ?? null,
    accuracy_confirmed: !!row.accuracy_confirmed, publication_consent: !!row.publication_consent, conduct_confirmed: !!row.conduct_confirmed
  };
}

export function safeJsonArray(value) { try { const x = JSON.parse(value || "[]"); return Array.isArray(x) ? x.map(v => text(v,80)).filter(Boolean) : []; } catch { return []; } }
