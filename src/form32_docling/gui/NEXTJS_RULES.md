# Next.js Rules for `src/form32_docling/gui`

This project uses:
- Next.js `16.1.6` (App Router)
- React `19`
- Static export (`output: 'export'`) with `trailingSlash: true`
- React Compiler (`reactCompiler: true`)

Follow these rules for all new code and refactors.

## 1. Routing and file conventions

- Keep all routes in `app/` using App Router conventions.
- Route UI files must be `page.js`; shared wrappers must be `layout.js`.
- API endpoints must use `route.js` under `app/api/...`.
- Do not place `route.js` in a folder that also contains `page.js`.
- Use `_private` folders for non-route modules inside `app/`.
- For Next 16+, use `proxy.ts` (not `middleware.ts`) if request interception is needed.

## 2. Server vs Client component boundaries

- Default to Server Components; add `'use client'` only when needed.
- Client components must not be `async`.
- Never pass non-serializable props from server to client:
  - No functions (except Server Actions),
  - No `Date` objects (pass ISO string),
  - No class instances, `Map`, or `Set`.
- Keep browser-only APIs (`window`, `document`, `localStorage`) inside Client Components only.

## 3. Data fetching and mutations

- Prefer direct server-side data fetching in Server Components for reads.
- Use Server Actions for UI-triggered mutations.
- Use Route Handlers for:
  - External integrations/webhooks,
  - Public or external-facing REST endpoints.
- Avoid fetch waterfalls:
  - Use `Promise.all` for parallel reads,
  - Use `Suspense` for streaming independent sections.

## 4. Async request APIs (Next 15+ / 16+)

- Treat these as async and await them:
  - `params`,
  - `searchParams`,
  - `cookies()`,
  - `headers()`.
- In non-async components, use `React.use()` where needed.

## 5. Error handling and not-found flows

- Add segment-level `error.js` for recoverable UI errors (`'use client'` required).
- Add `global-error.js` only for root-level failures (must include `<html>` and `<body>`).
- Add `not-found.js` where entity lookups can fail; call `notFound()` from route logic.
- Do not swallow navigation exceptions:
  - `redirect()`, `permanentRedirect()`, `notFound()`, `forbidden()`, `unauthorized()`
  - Keep them outside broad `try/catch`, or rethrow with `unstable_rethrow(error)`.

## 6. Static export constraints (critical for this app)

Because `next.config.mjs` sets `output: 'export'`:

- Do not rely on runtime Node server features for production pages.
- Ensure routes intended for export are statically renderable.
- Avoid server-only behavior that requires a live Next server at request time.
- If `next/image` is used, prefer one of:
  - `images.unoptimized: true` in config, or
  - Per-image `unoptimized` prop when appropriate.

If a feature requires dynamic server runtime, document it and revisit `output: 'export'`.

## 7. Metadata and SEO

- Define route metadata in Server Components only.
- Use static `metadata` for most routes; use `generateMetadata` only when content is dynamic.
- Keep route title patterns consistent from root layout.
- Add metadata files when needed:
  - `app/opengraph-image.(png|tsx)`,
  - `app/robots.(txt|ts)`,
  - `app/sitemap.(xml|ts)`.

## 8. Images, fonts, and assets

- Use `next/image` instead of raw `<img>` for app content images.
- Always provide sizing strategy:
  - `width` + `height`, or
  - `fill` + `sizes`.
- Use `priority` only for true above-the-fold/LCP images.
- Use `next/font` for font loading; do not use Google Fonts `<link>` tags.

## 9. Runtime selection

- Default to Node.js runtime (no explicit `runtime` needed).
- Use Edge runtime only with a clear latency requirement and compatible dependencies.

## 10. Bundling and dependency safety

- For browser-only packages, load via client boundaries or dynamic import with `ssr: false`.
- For problematic server packages, consider `serverExternalPackages` in `next.config.mjs`.
- Use `transpilePackages` for ESM/CJS compatibility issues as needed.
- Import CSS via JS/CSS modules; do not inject manual stylesheet `<link>` tags.

## 11. Existing project structure expectations

Current route set includes:
- `app/page.js`
- `app/workbench/page.js`

When adding features:
- Keep domain-specific UI under route folders in `app/`.
- Extract shared UI into non-route component folders (for example `app/_components/`).
- Keep API routes under `app/api/`.

## 12. Definition of done for Next.js changes

A PR touching the Next app is done when:
- `npm run lint` passes in `src/form32_docling/gui`,
- Build/export succeeds for affected routes,
- RSC boundaries are valid (`'use client'` only where required),
- Error and empty/not-found states are handled,
- New routes/components follow this file's conventions.
