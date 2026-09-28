export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      if (/^\/admin(?:\/|$)/.test(url.pathname)) return Response.redirect(new URL('/', request.url), 302);
      if (/^\/advocates(?:\/|$)/.test(url.pathname)) return Response.redirect(new URL('/team.html', request.url), 301);
      return await env.ASSETS.fetch(request);
    } catch (_) {
      return new Response("Lex Talk Legal — Temporary service error.", {status: 503, headers: {"content-type":"text/plain; charset=UTF-8"}});
    }
  }
};
