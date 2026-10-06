/**
 * The Shelf — Cloudflare Worker
 *
 * This site is fully static (public/), so the worker's only job is to
 * hand every request to the ASSETS binding declared in wrangler.toml.
 * Kept as a worker (rather than plain Pages) so this project matches
 * the same deploy shape as the other apps on this account.
 */

export default {
  async fetch(request, env) {
    if (env.ASSETS) {
      return env.ASSETS.fetch(request);
    }
    return new Response("Not found", { status: 404 });
  },
};
