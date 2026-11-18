import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import { apiFetch } from "@/lib/api";
import { EVENT_CATEGORIES } from "@/lib/categories";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";

// Час показуємо за Києвом, бо так записано в CSV.
function formatDate(iso) {
  return new Date(iso).toLocaleString("uk-UA", {
    timeZone: "Europe/Kyiv",
    weekday: "short",
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function Events() {
  const auth = useAuth();
  const token = auth.user?.access_token;
  const [params, setParams] = useSearchParams();
  const category = params.get("category") || "";
  const university = params.get("university") || "";
  const q = params.get("q") || "";

  const [search, setSearch] = useState(q);
  const [events, setEvents] = useState([]);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState("");

  function updateParam(key, value) {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next, { replace: true });
  }

  useEffect(() => {
    const t = setTimeout(() => updateParam("q", search), 300);
    return () => clearTimeout(t);
  }, [search]);

  useEffect(() => {
    if (!token) return;
    setError("");
    setLoaded(false);
    apiFetch("/events", { token, params: { category, university, q } })
      .then(setEvents)
      .catch(() => setError("Помилка завантаження. Чи запущено API?"))
      .finally(() => setLoaded(true));
  }, [token, category, university, q]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Button size="sm" variant={!category ? "default" : "outline"} onClick={() => updateParam("category", "")}>
          Усі категорії
        </Button>
        {EVENT_CATEGORIES.map((c) => (
          <Button
            key={c.value}
            size="sm"
            variant={category === c.value ? "default" : "outline"}
            onClick={() => updateParam("category", c.value)}
          >
            {c.label}
          </Button>
        ))}
        <Button
          size="sm"
          variant={university === "ucu" ? "default" : "outline"}
          onClick={() => updateParam("university", university === "ucu" ? "" : "ucu")}
        >
          УКУ
        </Button>
      </div>

      <Input
        placeholder="Пошук: квіз, концерт, лекція…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {error && <p className="text-destructive">{error}</p>}

      {!error && loaded && events.length === 0 && (
        <p className="rounded-lg border border-dashed p-8 text-center text-muted-foreground">
          Вибачте, зараз нема дійсних подій.
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
        {events.map((e) => (
          <Card key={e.id} className="overflow-hidden">
            {e.image_url ? (
              <img src={e.image_url} alt={e.title} loading="lazy" className="h-40 w-full object-cover" />
            ) : (
              <div className="flex h-40 items-center justify-center bg-muted text-sm text-muted-foreground">
                Фото ще немає
              </div>
            )}
            <CardContent className="space-y-2 p-4">
              <p className="text-sm font-semibold text-primary">{formatDate(e.starts_at)}</p>
              <p className="font-semibold">{e.title}</p>
              {e.venue && <p className="text-sm text-muted-foreground">{e.venue}</p>}
              {e.address && <p className="text-sm text-muted-foreground">{e.address}</p>}
              {e.price && <p className="text-sm">{e.price}</p>}
              {e.source_url && (
                <a href={e.source_url} target="_blank" rel="noopener noreferrer" className="text-sm underline">
                  Детальніше →
                </a>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
