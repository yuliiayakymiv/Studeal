import { Link } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import { Button } from "@/components/ui/button";

export default function Home() {
  const auth = useAuth();
  if (auth.isLoading) return <p className="text-muted-foreground">Завантаження…</p>;

  if (!auth.isAuthenticated) {
    return (
      <section className="mx-auto mt-16 max-w-md space-y-4 text-center">
        <h1 className="text-3xl font-bold">Знижки і події для студентів Львова</h1>
        <p className="text-muted-foreground">
          Щоб побачити знижки й події, увійдіть або зареєструйтеся.
        </p>
        <Button size="lg" onClick={() => auth.signinRedirect()}>
          Sign in / Зареєструватися
        </Button>
      </section>
    );
  }

  return (
    <section className="mt-10 space-y-4 text-center">
      <h1 className="text-3xl font-bold">Вітаємо у Studeal</h1>
      <div className="flex flex-wrap justify-center gap-3">
        <Button asChild><Link to="/catalog">Знижки</Link></Button>
        <Button asChild variant="outline"><Link to="/events">Події</Link></Button>
        <Button asChild variant="outline"><Link to="/saved">Збережені</Link></Button>
      </div>
    </section>
  );
}
