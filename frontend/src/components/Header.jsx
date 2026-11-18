import { Link } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import { Button } from "@/components/ui/button";
import { hostedUiLogoutUrl } from "@/lib/auth";

export default function Header() {
  const auth = useAuth();
  const email = auth.user?.profile?.email;

  function signOut() {
    auth.removeUser();
    window.location.href = hostedUiLogoutUrl();
  }

  return (
    <header className="border-b bg-background">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 p-4">
        <Link to="/" className="text-xl font-bold">Studeal</Link>

        {auth.isAuthenticated && (
          <nav className="flex flex-wrap gap-2">
            <Button asChild variant="ghost" size="sm"><Link to="/catalog">Знижки</Link></Button>
            <Button asChild variant="ghost" size="sm"><Link to="/events">Події</Link></Button>
            <Button asChild variant="ghost" size="sm"><Link to="/saved">Збережені</Link></Button>
          </nav>
        )}

        <div className="flex items-center gap-3">
          {auth.isAuthenticated ? (
            <>
              <span className="text-sm text-muted-foreground">{email}</span>
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
