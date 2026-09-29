export async function onRequest(context) {
  const response = await context.next();
  const headers = new Headers(response.headers);
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  headers.set("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()");
  headers.set("X-Frame-Options", "SAMEORIGIN");
  headers.set("Content-Security-Policy", "default-src 'self'; img-src 'self' https: data:; style-src 'self' 'unsafe-inline'; script-src 'self' https://translate.google.com https://translate.googleapis.com; frame-src https://www.youtube-nocookie.com https://www.youtube.com; connect-src 'self' https://translate.googleapis.com; base-uri 'self'; form-action 'self'; object-src 'none'; frame-ancestors 'self';");
  return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
}
