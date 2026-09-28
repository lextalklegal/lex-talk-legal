export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);

      // Legacy browser compatibility:
      // Old cached redirects may still send some visitors to the
      // previous workers.dev hostname. Send them back to the
      // canonical website without creating another permanent redirect.
      if (url.hostname === "lex-talk-legal.office-lextalklegal.workers.dev") {
        const canonical = new URL(request.url);
        canonical.protocol = "https:";
        canonical.hostname = "lextalk.legal";

        return new Response(null, {
          status: 302,
          headers: {
            "Location": canonical.toString(),
            "Cache-Control": "no-store"
          }
        });
      }

      if (/^\/admin(?:\/|$)/.test(url.pathname)) {
        return Response.redirect(new URL("/", request.url), 302);
      }

      if (/^\/advocates(?:\/|$)/.test(url.pathname)) {
        return Response.redirect(new URL("/team.html", request.url), 301);
      }

      return await env.ASSETS.fetch(request);

    } catch (_) {
      return new Response(
        "Lex Talk Legal — Temporary service error.",
        {
          status: 503,
          headers: {
            "content-type": "text/plain; charset=UTF-8"
          }
        }
      );
    }
  }
};
