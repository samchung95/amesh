# ADR-023: React SPA shell and accessible primitives

- Status: Accepted
- Date: 2026-08-22
- Scope: EPIC-404

## Context

ADR-007 selected React and TypeScript. The repository now has a stable authenticated `/api/v1` slice
but no executable frontend. EPIC-404 requires deep links, server state, a global command palette,
internationalization, accessibility evidence and a production artifact served with the API. Building
routing, cache synchronization, focus-trapped dialogs or localization infrastructure locally would
reimplement mature general-purpose behavior.

## Decision

1. Build a client-rendered React 19 TypeScript application with Vite 8. Server-side rendering is not
   required for this authenticated control plane.
2. Use React Router 7 in declarative mode for URL ownership, history and deep links, and TanStack Query
   5 for remote server state. Keep ephemeral shell state in React and URL search parameters rather than
   adding a general client-state library.
3. Use i18next plus react-i18next for message lookup and locale switching. Use the browser `Intl` APIs
   for dates, numbers and IANA time zones.
4. Use `cmdk` for the accessible searchable command palette and Lucide for a consistent icon set.
   AMESH owns all visual styling through `DESIGN.md` tokens; no themed component kit or utility CSS
   framework is introduced.
5. Bundle IBM Plex Sans and IBM Plex Mono through Fontsource so the production UI makes no font CDN
   request and remains usable offline.
6. Use Vitest, Testing Library and user-event for component behavior. Use Playwright with axe-core for
   real-browser navigation, keyboard, responsive and automated WCAG checks. Automated checks do not
   replace the documented manual keyboard and screen-reader pass.
7. Commit exact npm versions and `package-lock.json`. `uv` remains authoritative for Python packages;
   npm owns only the isolated `frontend/` JavaScript workspace.
8. Build the SPA in a Node stage and copy only `frontend/dist` into the existing Python runtime image.
   FastAPI serves the immutable assets and falls back to `index.html` for non-API deep links.
9. Product telemetry has no runtime client or outbound endpoint by default. A future telemetry adapter
   requires an explicit deployment setting, visible consent text and a new reviewed decision.

## Alternatives considered

- Next.js or React Router framework mode: useful for public SSR and server actions, but adds a second
  application server and deployment boundary without benefit for the authenticated control plane.
- Hand-written routing, request caching, dialogs and translations: fewer dependencies on paper, but
  recreates history, focus management, async lifecycle and locale edge cases that are not AMESH domain
  logic.
- A themed component system or Tailwind: faster generic composition, but conflicts with the accepted
  product-specific instrument aesthetic and adds a second token abstraction. Revisit only if the
  component count makes plain tokenized CSS measurably difficult to maintain.

## Consequences

- The first application loads as static assets and calls the same public APIs used by automation.
- Strategic server state and routing libraries remain visible at route/hooks boundaries; AMESH domain
  types and permissions stay in local modules.
- The frontend build requires Node 22 in development and the image build stage, while the production
  image remains Python-only and non-root.

## Sources

- [Vite React TypeScript setup](https://vite.dev/guide/)
- [React Router modes](https://reactrouter.com/start/modes)
- [TanStack Query installation and browser support](https://tanstack.com/query/latest/docs/framework/react/installation)
- [react-i18next quick start](https://react.i18next.com/guides/quick-start)
- [Radix accessibility behavior used by cmdk](https://www.radix-ui.com/primitives/docs/overview/accessibility)
- [Playwright accessibility testing](https://playwright.dev/docs/accessibility-testing)
