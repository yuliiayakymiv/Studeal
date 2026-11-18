# Frontend

React 19 + Vite + Tailwind + shadcn/ui. Sign-in with Amazon Cognito through `react-oidc-context` (as in spry). How to run everything together: see the main [README](../README.md).

## Run

```sh
cp .env.example .env.local   # first time only
npm install
npm run dev                  # http://localhost:5173, /api goes to the backend on :8000
npm run build                # production build into dist/
npm run lint                 # oxlint
```

## Pages

| Path | Page | Sign-in |
|---|---|---|
| `/` | Home: what Studeal is, sign-in button | — |
| `/catalog` | Deals: category filter, UCU filter, search | required |
| `/deals/:id` | One deal, save / unsave | required |
| `/events` | Events: category filter, UCU filter | required |
| `/saved` | Saved deals | required |

Data comes from the backend API (`src/lib/api.js`); every request sends the Cognito access token.

## Configuration (`.env.local`)

| Variable | Meaning |
|---|---|
| `VITE_DEV_NO_AUTH` | `true` = skip sign-in in `npm run dev` (never applies to `npm run build`) |
| `VITE_COGNITO_ISSUER` | `https://cognito-idp.eu-central-1.amazonaws.com/<user pool id>` |
| `VITE_COGNITO_CLIENT_ID` | Cognito app client id |
| `VITE_COGNITO_DOMAIN` | Hosted UI domain, e.g. `https://<prefix>.auth.eu-central-1.amazoncognito.com` (used for sign-out) |

`.env.local` is not committed. For a production build the same `VITE_COGNITO_*` values must be set when running `npm run build`.

## Structure

```
src/
  pages/         Home, Catalog, DealPage, Events, Saved
  components/    Header, DealCard, ui/ (shadcn components)
  lib/           api.js (API calls), auth.js (Cognito), devAuth.jsx (local mode),
                 categories.js, themes.js
```
