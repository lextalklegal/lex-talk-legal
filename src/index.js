export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      const host = url.hostname.toLowerCase();

      // Legacy compatibility:
      // Some visitors may still have the old permanent redirect
      // cached from lextalk.legal -> workers.dev.
      // Send them to a cache-busting canonical URL.
      if (host === "lex-talk-legal.office-lextalklegal.workers.dev") {
        const target = new URL(request.url);
        target.protocol = "https:";
        target.hostname = "lextalk.legal";
        target.searchParams.set("__legacy", "1");

        return new Response(null, {
          status: 302,
          headers: {
            "Location": target.toString(),
            "Cache-Control": "no-store"
          }
        });
      }

      // Existing route redirects
      if (/^\/admin(?:\/|$)/.test(url.pathname)) {
        return Response.redirect(new URL("/", request.url), 302);
      }

      if (/^\/advocates(?:\/|$)/.test(url.pathname)) {
        return Response.redirect(new URL("/team.html", request.url), 301);
      }

      const response = await env.ASSETS.fetch(request);

      // One-time cleanup for visitors arriving through the legacy bridge.
      if (url.searchParams.get("__legacy") === "1") {
        const contentType = response.headers.get("content-type") || "";

        if (contentType.includes("text/html")) {
          const rewriter = new HTMLRewriter().on("body", {
            element(element) {
              element.append(
                `<script>
                  (() => {
                    const u = new URL(location.href);
                    u.searchParams.delete("__legacy");
                    history.replaceState(null, "", u.pathname + (u.search ? "?" + u.searchParams.toString() : "") + u.hash);
                  })();
                </script>`,
                { html: true }
              );
            }
          });

          const headers = new Headers(response.headers);
          headers.set("Cache-Control", "no-store");

          return rewriter.transform(
            new Response(response.body, {
              status: response.status,
              statusText: response.statusText,
              headers
            })
          );
        }
      }

      return response;

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
