(function () {
  const cfg = window.STUDEAL_CONFIG || {};
  const enabled = Boolean(cfg.cognitoDomain && cfg.clientId);
  const TOKEN_KEY = "studeal_access_token";
  const EXPIRES_KEY = "studeal_access_expires";
  const VERIFIER_KEY = "studeal_pkce_verifier";

  // Адреса поточної сторінки, яка має бути в списку Callback URLs у Cognito.
  function pageUrl() {
    let path = window.location.pathname;
    if (path.endsWith("/")) path += "index.html";
    return window.location.origin + path;
  }

  function base64Url(bytes) {
    let binary = "";
    bytes.forEach((b) => (binary += String.fromCharCode(b)));
    return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }

  async function signIn() {
    const bytes = new Uint8Array(32);
    crypto.getRandomValues(bytes);
    const verifier = base64Url(bytes);
    const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier));
    sessionStorage.setItem(VERIFIER_KEY, verifier);
    const params = new URLSearchParams({
      client_id: cfg.clientId,
      response_type: "code",
      scope: "openid email profile",
      redirect_uri: pageUrl(),
      code_challenge_method: "S256",
      code_challenge: base64Url(new Uint8Array(digest)),
    });
    window.location.href = `${cfg.cognitoDomain}/oauth2/authorize?${params}`;
  }

  // Міняємо код з адреси на токен (після повернення з Cognito).
  async function exchangeCode(code) {
    const verifier = sessionStorage.getItem(VERIFIER_KEY);
    sessionStorage.removeItem(VERIFIER_KEY);
    const res = await fetch(`${cfg.cognitoDomain}/oauth2/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        client_id: cfg.clientId,
        code,
        redirect_uri: pageUrl(),
        code_verifier: verifier,
      }),
    });
    if (!res.ok) throw new Error(`token exchange failed: ${res.status}`);
    const data = await res.json();
    sessionStorage.setItem(TOKEN_KEY, data.access_token);
    sessionStorage.setItem(EXPIRES_KEY, String(Date.now() + data.expires_in * 1000 - 60000));
  }

  function getToken() {
    if (!enabled) return null;
    if (Date.now() > Number(sessionStorage.getItem(EXPIRES_KEY) || 0)) return null;
    return sessionStorage.getItem(TOKEN_KEY);
  }

  function signOut() {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(EXPIRES_KEY);
    const params = new URLSearchParams({ client_id: cfg.clientId, logout_uri: pageUrl() });
    window.location.href = `${cfg.cognitoDomain}/logout?${params}`;
  }

  // Показує блоки з data-auth="in" (після входу) або data-auth="out" (лендинг).
  function render(signedIn) {
    document.querySelectorAll('[data-auth="in"]').forEach((e) => (e.hidden = !signedIn));
    document.querySelectorAll('[data-auth="out"]').forEach((e) => (e.hidden = signedIn));
    const box = document.getElementById("auth-box");
    if (box && enabled) {
      const btn = document.createElement("button");
      btn.className = "login";
      btn.textContent = signedIn ? "Вийти" : "Увійти";
      btn.onclick = signedIn ? signOut : signIn;
      box.replaceChildren(btn);
    }
  }

  // Викликається на кожній сторінці. Повертає true, якщо користувач увійшов.
  async function init() {
    if (!enabled) {
      render(true);
      return true;
    }
    const url = new URL(window.location.href);
    if (url.searchParams.get("code")) {
      try {
        await exchangeCode(url.searchParams.get("code"));
      } catch (e) {
        console.error(e);
      }
      window.history.replaceState({}, "", window.location.pathname);
    }
    const signedIn = getToken() !== null;
    render(signedIn);
    const loginBtn = document.getElementById("login-btn");
    if (loginBtn) loginBtn.onclick = signIn;
    return signedIn;
  }

  window.Studeal = { init, getToken, signIn, signOut };
})();
