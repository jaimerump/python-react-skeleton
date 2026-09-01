# ui

React + TypeScript + Vite frontend. Feature-folder architecture with **TanStack Query
as the single source of server state**, a typed two-tier API layer, React Context for
true app-state only, shadcn-style primitives (Radix + Tailwind + CVA), and Sonner toasts.
Tested with Vitest + React Testing Library and Playwright (Page Object Model).

See the full blueprint in `../.context/attachments/.../reusable-frontend-architecture.md`.

## Layout

```
src/
├── app/          # shell: main.tsx, App.tsx (provider tree), routes, AppLayout, providers/
├── features/     # one self-contained slice per domain (api + queries + components + pages)
│   └── health/   # example slice — exercises the whole stack against /ready
├── shared/       # cross-cutting: api/ (fetch wrapper), query/, auth/, ui/, theme/, flags/, hooks/, lib/
└── test/         # setup.ts + test-utils.tsx (createWrapper)
e2e/              # Playwright POM (pages/, fixtures/)
```

**Boundary rule** (enforced by ESLint): a feature imports only `shared/` and its own
slice, and another feature only via that feature's public `index.ts`. `shared/` never
imports `features/` or `app/`.

**Path alias:** `@` → `src`.

## Getting started

```bash
npm install
cp .env.example .env.local        # defaults proxy /api -> http://localhost:8000
npm run dev                       # Vite dev server at http://localhost:5173
```

The dev server proxies `/api/*` to the backend (stripping the `/api` prefix), so run the
backend too (`uv run uvicorn app.api.main:app --reload` from the repo root). The home page
reads the backend's `/ready` and shows its status.

## Scripts

```bash
npm run lint         # ESLint (incl. architecture boundary rules)
npm run typecheck    # tsc, no emit
npm test             # Vitest (unit/component)
npm run build        # type-check + production build
npm run e2e          # Playwright (needs: npx playwright install chromium)
```

## Adding a feature slice

Create `src/features/<domain>/` with `api.ts` (typed fns over `fetchApi`),
`queries.ts` / `mutations.ts` (over `shared/query/queryKeys`), `types.ts`,
`components/`, `pages/`, and an `index.ts` barrel exposing only the public surface.
Add the domain's keys to `shared/query/queryKeys.ts`.

## Swappable seams

Auth (`shared/auth`), feature flags (`shared/flags`), error reporting
(`shared/lib/logger.ts`), and toasts are stubs/seams — swap the implementation without
touching call sites. Auth currently reports an unauthenticated user because the backend
has no auth vendor wired in yet.
