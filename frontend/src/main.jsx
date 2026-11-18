import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "react-oidc-context";
import "./index.css";
import App from "./App.jsx";
import { oidcConfig } from "./lib/auth.js";
import { DEV_NO_AUTH, DevAuthProvider } from "./lib/devAuth.jsx";
import { applyTheme, getTheme } from "./lib/themes.js";

// Тему застосовуємо до першого показу, щоб не було миготіння.
applyTheme(getTheme());

const app = (
  <BrowserRouter>
    <App />
  </BrowserRouter>
);

createRoot(document.getElementById("root")).render(
  DEV_NO_AUTH ? (
    <DevAuthProvider>{app}</DevAuthProvider>
  ) : (
    <AuthProvider {...oidcConfig}>{app}</AuthProvider>
  )
);
