import { useEffect, useState } from "react";
import { useAuth } from "react-oidc-context";
import { apiFetch } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

// Studeal+ за $5: студент обирає заклади і отримує лист, коли там є знижка.
// Оплата поки демонстраційна: кнопка вмикає підписку, гроші не списуються.
export default function Subscription() {
  const auth = useAuth();
  const token = auth.user?.access_token;
  const [state, setState] = useState(null);
  const [venues, setVenues] = useState([]);
  const [email, setEmail] = useState(auth.user?.profile?.email || "");
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    if (!token) return;
    Promise.all([apiFetch("/me/subscription", { token }), apiFetch("/deals/venues", { token })])
      .then(([s, v]) => {
        setState(s);
        setVenues(v);
        if (s.email) setEmail(s.email);
      })
      .catch(() => setError("Помилка завантаження. Чи запущено API?"));
  }, [token]);

  async function run(action, message) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const next = await action();
      if (next) setState(next);
      else setState(await apiFetch("/me/subscription", { token }));
      if (message) setNotice(message);
    } catch {
      setError("Щось пішло не так. Спробуйте ще раз.");
    } finally {
      setBusy(false);
    }
  }

  function pay(e) {
    e.preventDefault();
    run(
      () => apiFetch("/me/subscription", { token, method: "POST", body: { email } }),
      "Підписку оформлено! Тепер додайте заклади.",
    );
  }

  function follow(e) {
    e.preventDefault();
    const value = name.trim();
    if (value.length < 2) return;
    run(async () => {
      const next = await apiFetch("/me/subscription/venues", {
        token,
        method: "POST",
        body: { name: value },
      });
      setName("");
      const added = next.venues.find((v) => v.name.toLowerCase() === value.toLowerCase());
      setNotice(
        added?.deals_now
          ? `У «${added.name}» вже є знижка: лист відправлено на ${next.email}.`
          : `Додано. Щойно в «${value}» з'явиться знижка, напишемо на ${next.email}.`,
      );
      return next;
    });
  }

  if (error && !state) return <p className="text-destructive">{error}</p>;
  if (!state) return <p className="text-muted-foreground">Завантаження…</p>;

  return (
    <section className="mx-auto max-w-xl space-y-6 py-6">
      <div className="space-y-2 text-center">
        <h1 className="text-3xl font-bold">Studeal+</h1>
        <p className="text-muted-foreground">
          Оберіть магазини, кав'ярні чи ресторани, і ми надішлемо лист, щойно там з'явиться
          студентська знижка.
        </p>
      </div>

      {notice && (
        <p className="rounded-lg border border-primary/30 bg-accent p-3 text-sm">{notice}</p>
      )}
      {error && <p className="text-sm text-destructive">{error}</p>}

      {!state.active ? (
        <form onSubmit={pay} className="space-y-4 rounded-xl border bg-card p-6">
          <div className="flex items-baseline justify-between">
            <span className="text-lg font-semibold">Підписка на місяць</span>
            <span className="text-2xl font-bold">${state.price_usd}</span>
          </div>
          <ul className="list-inside list-disc space-y-1 text-sm text-muted-foreground">
            <li>скільки завгодно закладів</li>
            <li>лист на пошту, коли там є або з'явиться знижка</li>
            <li>скасувати можна будь-коли</li>
          </ul>
          <label className="block space-y-1 text-sm">
            <span>Куди надсилати листи</span>
            <Input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@ucu.edu.ua"
            />
          </label>
          <Button type="submit" className="w-full" disabled={busy}>
            Оплатити ${state.price_usd}
          </Button>
          <p className="text-center text-xs text-muted-foreground">
            Демо-версія: оплата не списується, підписка вмикається одразу.
          </p>
        </form>
      ) : (
        <div className="space-y-4 rounded-xl border bg-card p-6">
          <p className="text-sm text-muted-foreground">
            Підписка активна. Листи надходять на <b className="text-foreground">{state.email}</b>.
          </p>

          <form onSubmit={follow} className="flex gap-2">
            <Input
              list="studeal-venues"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Назва закладу, напр. Aroma Kava"
            />
            <datalist id="studeal-venues">
              {venues.map((v) => (
                <option key={v} value={v} />
              ))}
            </datalist>
            <Button type="submit" disabled={busy || name.trim().length < 2}>
              Додати
            </Button>
          </form>

          {state.venues.length === 0 ? (
            <p className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
              Ви ще не обрали жодного закладу.
            </p>
          ) : (
            <ul className="divide-y rounded-lg border">
              {state.venues.map((v) => (
                <li key={v.id} className="flex items-center justify-between gap-3 p-3">
                  <div>
                    <p className="font-medium">{v.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {v.deals_now > 0
                        ? `Зараз знижок: ${v.deals_now}`
                        : "Поки знижок немає, чекаємо"}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={busy}
                    onClick={() =>
                      run(() =>
                        apiFetch(`/me/subscription/venues/${v.id}`, { token, method: "DELETE" }),
                      )
                    }
                  >
                    Прибрати
                  </Button>
                </li>
              ))}
            </ul>
          )}

          <div className="pt-2 text-right">
            <Button
              variant="outline"
              size="sm"
              disabled={busy}
              onClick={() =>
                run(
                  () => apiFetch("/me/subscription", { token, method: "DELETE" }),
                  "Підписку скасовано. Листи більше не надходитимуть.",
                )
              }
            >
              Скасувати підписку
            </Button>
          </div>
        </div>
      )}
    </section>
  );
}
