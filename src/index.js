import { onRequestPost as submitProfile } from "../functions/api/profile-submit.js";
import { onRequestGet as listProfiles } from "../functions/api/profiles.js";
import { onRequestGet as advocateDirectory } from "../functions/advocates/index.js";
import { onRequestGet as advocateProfile } from "../functions/advocates/[slug].js";
import { onRequestGet as adminProfilesGet, onRequestPatch as adminProfilesPatch } from "../functions/admin/profiles.js";

function ctx(request, env, context, params = {}) {
  return { request, env, ctx: context, params };
}

async function adminContext(request, env, context) {
  // Defense-in-depth: profile administration must be behind Cloudflare Access.
  // Do not trust a client-supplied CF-Access-Authenticated-User-Email header.
  if (!context?.access || typeof context.access.getIdentity !== 'function') return null;
  let identity;
  try { identity = await context.access.getIdentity(); } catch { return null; }
  const email = String(identity?.email || '').trim().toLowerCase();
  const allowed = String(env.ADMIN_EMAILS || '').split(',').map(v => v.trim().toLowerCase()).filter(Boolean);
  if (!email || !allowed.includes(email)) return null;
  const headers = new Headers(request.headers);
  headers.set('CF-Access-Authenticated-User-Email', email);
  return new Request(request, { headers });
}

function secure(response, request, path) {
  const h = new Headers(response.headers);
  h.set("X-Content-Type-Options", "nosniff");
  h.set("Referrer-Policy", "strict-origin-when-cross-origin");
  h.set("Permissions-Policy", "geolocation=(), microphone=(), camera=(), payment=()");
  h.set("X-Frame-Options", "SAMEORIGIN");
  h.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
  if (path.startsWith("/api/") || path.startsWith("/admin/")) {
    h.set("Cache-Control", "no-store");
    h.set("X-Robots-Tag", "noindex, nofollow");
  }
  if (path === "/advocates/apply.html") h.set("X-Robots-Tag", "noindex, nofollow");
  return new Response(response.body, { status: response.status, statusText: response.statusText, headers: h });
}

function redirect(request, path) {
  const target = path === "/advocates" ? "/advocates/" : `${path}/`;
  return Response.redirect(new URL(target, request.url).toString(), 301);
}

export default {
  async fetch(request, env, context) {
    const url = new URL(request.url);
    const raw = url.pathname;
    const path = raw.replace(/\/+$/, "") || "/";

    try {
      // Canonical trailing-slash redirects for the main directory routes.
      if (request.method === "GET" && ["/courtrooms", "/case-status", "/videos", "/advocates"].includes(path) && raw === path) {
        return redirect(request, path);
      }

      if (path === "/api/profile-submit" && request.method === "POST") return secure(await submitProfile(ctx(request, env, context)), request, raw);
      if (path === "/api/profiles" && request.method === "GET") return secure(await listProfiles(ctx(request, env, context)), request, raw);
      if (path === "/api/admin/profiles" && (request.method === "GET" || request.method === "PATCH")) {
        const trustedRequest = await adminContext(request, env, context);
        if (!trustedRequest) return secure(new Response("Admin authentication required.", { status: 401, headers: { "content-type": "text/plain; charset=utf-8", "www-authenticate": "Cloudflare Access" } }), request, raw);
        const response = request.method === "GET"
          ? await adminProfilesGet(ctx(trustedRequest, env, context))
          : await adminProfilesPatch(ctx(trustedRequest, env, context));
        return secure(response, request, raw);
      }

      if (path === "/advocates" && request.method === "GET") return secure(await advocateDirectory(ctx(request, env, context)), request, raw);
      if (path === "/admin/profiles" && request.method === "GET") {
        const trustedRequest = await adminContext(request, env, context);
        if (!trustedRequest) return secure(new Response("Admin authentication required.", { status: 401, headers: { "content-type": "text/plain; charset=utf-8", "www-authenticate": "Cloudflare Access" } }), request, raw);
        return secure(await adminProfilesGet(ctx(trustedRequest, env, context)), request, raw);
      }

      if (raw.startsWith("/advocates/")) {
        const rest = decodeURIComponent(raw.slice("/advocates/".length));
        if (!rest || rest === "apply.html" || rest.endsWith("/apply.html")) return secure(await env.ASSETS.fetch(request), request, raw);
        return secure(await advocateProfile(ctx(request, env, context, { slug: rest.replace(/\/$/, "") })), request, raw);
      }

      // /admin/index.html may remain a harmless landing page; /admin/profiles is Access-protected by its handler.
      const asset = await env.ASSETS.fetch(request);
      return secure(asset, request, raw);
    } catch (e) {
      return new Response("Internal Server Error", { status: 500, headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "no-store", "X-Content-Type-Options": "nosniff" } });
    }
  }
};
