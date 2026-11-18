export const oidcConfig = {
  authority: import.meta.env.VITE_COGNITO_ISSUER,
  client_id: import.meta.env.VITE_COGNITO_CLIENT_ID,
  redirect_uri: window.location.origin + "/",
  response_type: "code",
  scope: "openid email profile",
  // Прибираємо ?code=... з адреси після входу.
  onSigninCallback: () => {
    window.history.replaceState({}, document.title, window.location.pathname);
  },
};

// Вихід із Cognito: спершу чистимо сесію, потім Hosted UI.
export function hostedUiLogoutUrl() {
  const params = new URLSearchParams({
    client_id: import.meta.env.VITE_COGNITO_CLIENT_ID,
    logout_uri: window.location.origin + "/",
  });
  return `${import.meta.env.VITE_COGNITO_DOMAIN}/logout?${params}`;
}
