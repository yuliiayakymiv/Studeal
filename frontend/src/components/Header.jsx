import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import { Button } from "@/components/ui/button";
import { hostedUiLogoutUrl } from "@/lib/auth";
import { DEV_NO_AUTH } from "@/lib/devAuth";
import { THEMES, getTheme, applyTheme } from "@/lib/themes";

export default function Header() {
  const auth = useAuth();
  const email = auth.user?.profile?.email;
  const [theme, setTheme] = useState(getTheme());

  function changeTheme(name) {
    applyTheme(name);
    setTheme(name);
  }

  function signOut() {
    auth.removeUser();
    window.location.href = hostedUiLogoutUrl();
  }

  return (
    <header className="border-b bg-background">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 p-4">
        <Link to="/" className="flex items-center gap-2 text-xl font-bold">
          <img src="/favicon.svg" alt="" className="h-8 w-8" />
          Studeal
        </Link>

        {auth.isAuthenticated && (
          <nav className="flex flex-wrap gap-2">
            <Button asChild variant="ghost" size="sm"><Link to="/catalog">Знижки</Link></Button>
            <Button asChild variant="ghost" size="sm"><Link to="/events">Події</Link></Button>
            <Button asChild variant="ghost" size="sm"><Link to="/saved">Збережені</Link></Button>
            <Button asChild variant="ghost" size="sm"><Link to="/subscription">Studeal+</Link></Button>
          </nav>
        )}

        <div className="flex items-center gap-3">
          <select
            value={theme}
            onChange={(e) => changeTheme(e.target.value)}
            className="rounded-md border border-input bg-background px-2 py-1 text-sm text-foreground"
            aria-label="Тема сайту"
          >
            {Object.entries(THEMES).map(([key, t]) => (
              <option key={key} value={key}>{t.label}</option>
            ))}
          </select>

          {DEV_NO_AUTH ? (
            <span className="rounded-md bg-accent px-2 py-1 text-xs text-accent-foreground">
              Локальний режим
            </span>
          ) : auth.isAuthenticated ? (
            <>
              <span className="hidden text-sm text-muted-foreground sm:inline">{email}</span>
              <Button variant="outline" size="sm" onClick={signOut}>Sign out</Button>
            </>
          ) : (
            <Button size="sm" onClick={() => auth.signinRedirect()}>Sign in</Button>
          )}
        </div>
      </div>
    </header>
  );
}
