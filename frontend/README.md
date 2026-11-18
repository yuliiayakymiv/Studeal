# Frontend

React 19 + Vite + Tailwind + shadcn/ui. Sign-in with Amazon Cognito through `react-oidc-context`. How to run everything together: see the main [README](../README.md).

## Commands

```sh
cp .env.example .env.local   # first time only
npm install
npm run dev                  # http://localhost:5173, /api is forwarded to the backend on :8000
npm run build                # production build into dist/
npm run lint                 # oxlint
```

## Pages

| Path | Page | Sign-in |
|---|---|---|
| `/` | Home: what Studeal is, sign-in button | — |
| `/catalog` | Deals: category filter, UCU filter, search, save | required |
| `/deals/:id` | One deal, save / unsave | required |
| `/events` | Events: category filter, UCU filter | required |
| `/saved` | Saved deals | required |

## Configuration (`.env.local`, not committed)

| Variable | Meaning |
|---|---|
| `VITE_DEV_NO_AUTH` | `true` = skip sign-in in `npm run dev` (never applies to `npm run build`) |
| `VITE_COGNITO_ISSUER` | `https://cognito-idp.<region>.amazonaws.com/<user pool id>` |
| `VITE_COGNITO_CLIENT_ID` | Cognito app client id |
| `VITE_COGNITO_DOMAIN` | Cognito Hosted UI domain (used for sign-out) |

Vite builds these values into the app, so they must be set when running `npm run build`.

## Structure

```
src/
  pages/         Home, Catalog, DealPage, Events, Saved
  components/    Header, DealCard, ui/ (shadcn components)
  lib/           api.js (API calls), auth.js (Cognito), devAuth.jsx (local mode),
                 categories.js, themes.js
```
