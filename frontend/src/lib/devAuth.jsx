import { AuthContext } from "react-oidc-context";

// Локальний режим без Cognito: сайт вважає, що користувач уже увійшов.
// Працює лише в `npm run dev` і лише якщо в frontend/.env.local є VITE_DEV_NO_AUTH=true.
// У продакшн-збірці (npm run build) цей режим вимкнений завжди.
export const DEV_NO_AUTH =
  import.meta.env.DEV && import.meta.env.VITE_DEV_NO_AUTH === "true";

const fakeAuth = {
  isAuthenticated: true,
  isLoading: false,
  user: { access_token: "dev-token", profile: { email: "dev@local" } },
  removeUser: async () => {},
  signinRedirect: async () => {},
};

export function DevAuthProvider({ children }) {
  return <AuthContext.Provider value={fakeAuth}>{children}</AuthContext.Provider>;
}
