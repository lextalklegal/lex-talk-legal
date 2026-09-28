export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      const host = url.hostname.toLowerCase();

      // Legacy compatibility bridge for browsers that still have an old
      // permanent redirect cached to the former workers.dev hostname.
      if (host === "lex-talk-legal.office-lextalklegal.workers.dev") {
        const target = new URL("https://lextalk.legal/__legacy-bridge/");
        target.searchParams.set("__to", url.pathname + url.search);
        return new Response(null, {
          status: 302,
          headers: {
            "Location": target.toString(),
            "Cache-Control": "no-store",
            "X-Robots-Tag": "noindex, nofollow, noarchive"
          }
        });
      }

      // Serve the original path through the canonical host. site.js silently
      // cleans the bridge URL from the browser address bar after the page loads.
      if (host === "lextalk.legal" && url.pathname === "/__legacy-bridge/") {
        let targetPath = url.searchParams.get("__to") || "/";
        try {
          const target = new URL(targetPath, "https://lextalk.legal");
          if (target.origin !== "https://lextalk.legal") targetPath = "/";
          else targetPath = target.pathname + target.search;
        } catch (_) {
          targetPath = "/";
        }
        const assetUrl = new URL(targetPath, "https://lextalk.legal");
        const assetRequest = new Request(assetUrl.toString(), request);
        const response = await env.ASSETS.fetch(assetRequest);
        const headers = new Headers(response.headers);
        headers.set("Cache-Control", "no-store");
        return new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers
        });
      }

      if (/^\/admin(?:\/|$)/.test(url.pathname)) {
        return Response.redirect(new URL('/', request.url), 302);
      }
      if (/^\/advocates(?:\/|$)/.test(url.pathname)) {
        return Response.redirect(new URL('/team.html', request.url), 301);
      }
      return await env.ASSETS.fetch(request);
    } catch (_) {
      return new Response("Lex Talk Legal — Temporary service error.", {
        status: 503,
        headers: {"content-type":"text/plain; charset=UTF-8"}
      });
    }
  }
};
