# AMESH web control room

The React/TypeScript control room is the graphical entry point for the current AMESH API. It provides
permission-aware navigation, flow and execution lists, execution task-run detail, tenant/namespace
context, saved execution views, global resource search, notifications, locale/time-zone controls and
retryable offline states. Routes reserved for later UI epics remain visibly labelled and inactive.

## Run it

The container build compiles and serves the UI and API on one origin:

```powershell
docker compose up --build api postgres minio
```

Open `http://localhost:8000`, then use `development-token` and tenant `default` for the development
configuration. The token is retained only in session storage; locale, time zone, context and saved
views use local storage.

For frontend development, start the API from the repository root and Vite in a second terminal:

```powershell
uv run --extra runtime python -m amesh.server
cd frontend
npm ci
npm run dev
```

Vite proxies `/api`, `/health` and `/ready` to `http://127.0.0.1:8000`.

## Verification

```powershell
npm run lint
npm run test
npm run build
npx playwright install chromium
npm run test:e2e
```

The browser suite covers connection, API-backed navigation, direct/reloaded deep links, the keyboard
command menu, server-authoritative denied routes, Simplified Chinese switching, locale formatting,
retry recovery, same-origin/offline privacy, a 768 px compact tablet layout and WCAG 2.2 AA axe rules.

## Browser support policy

- Chrome and Edge: current and previous stable desktop versions.
- Firefox: current and previous stable desktop versions.
- Safari: current stable macOS and iPadOS versions.
- Minimum layout widths: 768 px tablet and 1280 px desktop; the 390 px drawer is maintained as a
  convenience layout but is not yet a GA-qualified mobile workflow.
- Internet Explorer and browsers without ES2022 modules, `Intl` time zones or CSS custom properties
  are unsupported.

Chromium desktop and 768 px tablet checks run automatically. Firefox, Edge, Safari and iPadOS remain
part of the pre-GA manual release matrix; this epic does not claim that future editor or large-run
debugging workflows are already qualified.

## Accessibility and privacy record

On 2026-08-22 the shell passed its keyboard/semantic audit: the skip link is the first tab stop and
moves focus to `main`; navigation, complementary, main, dialog, listbox, table, form, status and alert
semantics expose stable accessible names; compact tablet links retain names when labels are visually
hidden; `Ctrl+K`, filtering and `Enter` operate the command menu; focus rings and 44 px controls remain
visible; and execution state is represented by icon, text and color. Axe reported no critical or
serious findings for the supported dashboard workflow.

Chromium accessibility-tree assertions cover English and Simplified Chinese. NVDA/VoiceOver release
matrix acceptance remains part of the shared GA accessibility requirement owned with EPIC-405 and
EPIC-407.

No analytics SDK, update check, font CDN or other outbound request is included. Product telemetry is
off by default and the server reports the explicit `PRODUCT_TELEMETRY_ENABLED` deployment policy in
the UI session response. The browser network acceptance test observes only the application origin.
