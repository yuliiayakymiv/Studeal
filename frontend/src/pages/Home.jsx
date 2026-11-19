import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import { Button } from "@/components/ui/button";
import ShimmerButton from "@/components/ShimmerButton";

export default function Home() {
  const auth = useAuth();
  const navigate = useNavigate();
  if (auth.isLoading) return <p className="text-muted-foreground">Завантаження…</p>;

  if (!auth.isAuthenticated) {
    return (
      <section className="mx-auto mt-28 max-w-md space-y-4 text-center">
        <h1 className="text-3xl font-bold">Знижки і події для студентів Львова</h1>
        <p className="text-muted-foreground">
          Щоб побачити знижки й події, увійдіть або зареєструйтеся.
        </p>
        <Button size="lg" onClick={() => auth.signinRedirect()}>
          Sign in / Sign up
        </Button>
        <div className="pt-10">
          <ShimmerButton onClick={() => auth.signinRedirect()}>
            Studeal+ за $5: знижки улюблених закладів на пошту
          </ShimmerButton>
        </div>
      </section>
    );
  }

  return (
    <section className="mx-auto mt-24 max-w-xl space-y-4 text-center">
      <h1 className="text-3xl font-bold">Вітаємо у Studeal</h1>
      <p className="text-muted-foreground">
        Studeal збирає студентські знижки та події у Львові: кав'ярні, коворкінги, спортзали,
        концерти й лекції. Обирайте категорію, шукайте за назвою або перегляньте події свого університету.
        Цікаві пропозиції зберігайте, щоб не загубити їх.
      </p>
      <div className="flex flex-wrap justify-center gap-3 pt-2">
        <Button asChild variant="outline" className="border-transparent bg-[#808080] text-white hover:bg-[#6e6e6e] hover:text-white dark:bg-[#808080] dark:hover:bg-[#6e6e6e]"><Link to="/catalog">Знижки</Link></Button>
        <Button asChild variant="outline" className="border-transparent bg-[#808080] text-white hover:bg-[#6e6e6e] hover:text-white dark:bg-[#808080] dark:hover:bg-[#6e6e6e]"><Link to="/events">Події</Link></Button>
        <Button asChild variant="outline" className="border-transparent bg-[#808080] text-white hover:bg-[#6e6e6e] hover:text-white dark:bg-[#808080] dark:hover:bg-[#6e6e6e]"><Link to="/saved">Збережені</Link></Button>
      </div>
      <div className="pt-10">
        <ShimmerButton onClick={() => navigate("/subscription")}>
          Studeal+ за $5: знижки улюблених закладів на пошту
        </ShimmerButton>
      </div>
    </section>
  );
}
