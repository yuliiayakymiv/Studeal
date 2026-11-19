import { emptyMessage } from "@/lib/emptyMessage";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import { apiFetch } from "@/lib/api";
import { DEAL_CATEGORIES, UNIVERSITIES } from "@/lib/categories";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import EventCard from "@/components/EventCard";

export default function Events() {
  const auth = useAuth();
  const token = auth.user?.access_token;
  const [params, setParams] = useSearchParams();
  const category = params.get("category") || "";
  const university = params.get("university") || "";
  const q = params.get("q") || "";

  const [search, setSearch] = useState(q);
  const [events, setEvents] = useState([]);
  const [savedIds, setSavedIds] = useState(new Set());
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
    Promise.all([
      apiFetch("/me/saved-events", { token }),
      apiFetch("/events", { token, params: { category, university, q } }),
    ])
      .then(([saved, list]) => {
        setSavedIds(new Set(saved.map((e) => e.id)));
        setEvents(list);
      })
      .catch(() => setError("Помилка завантаження. Чи запущено API?"))
      .finally(() => setLoaded(true));
  }, [token, category, university, q]);

  async function toggleSave(id, on) {
    try {
      await apiFetch(`/me/saved-events/${id}`, { token, method: on ? "POST" : "DELETE" });
      setSavedIds((prev) => {
        const next = new Set(prev);
        if (on) next.add(id);
        else next.delete(id);
        return next;
      });
    } catch {
      setError("Не вдалося зберегти.");
    }
  }

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
      </div>

      <div className="flex">
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
          {emptyMessage("подій", { university, category })}
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
        {events.map((e) => (
          <EventCard key={e.id} event={e} saved={savedIds.has(e.id)} onToggleSave={toggleSave} />
        ))}
      </div>
    </div>
  );
}
