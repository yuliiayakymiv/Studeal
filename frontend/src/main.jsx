import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "react-oidc-context";
import "./index.css";
import App from "./App.jsx";
import { oidcConfig } from "./lib/auth.js";

createRoot(document.getElementById("root")).render(
  <AuthProvider {...oidcConfig}>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </AuthProvider>
);
