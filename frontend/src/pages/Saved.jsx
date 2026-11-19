import { useEffect, useState } from "react";
import { useAuth } from "react-oidc-context";
import { apiFetch } from "@/lib/api";
import DealCard from "@/components/DealCard";
import EventCard from "@/components/EventCard";

export default function Saved() {
  const auth = useAuth();
  const token = auth.user?.access_token;
  const [deals, setDeals] = useState([]);
  const [events, setEvents] = useState([]);
  const [error, setError] = useState("");

  function load() {
    Promise.all([apiFetch("/me/saved", { token }), apiFetch("/me/saved-events", { token })])
      .then(([d, e]) => {
        setDeals(d);
        setEvents(e);
      })
      .catch(() => setError("Помилка завантаження."));
  }

  useEffect(() => {
    if (token) load();
  }, [token]);

  async function unsaveDeal(id) {
    try {
      await apiFetch(`/me/saved/${id}`, { token, method: "DELETE" });
      load();
    } catch {
      setError("Не вдалося прибрати зі збережених.");
    }
  }

  async function unsaveEvent(id) {
    try {
      await apiFetch(`/me/saved-events/${id}`, { token, method: "DELETE" });
      load();
    } catch {
      setError("Не вдалося прибрати зі збережених.");
    }
  }

  const nothingSaved = deals.length === 0 && events.length === 0;

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Збережені</h1>
      {error && <p className="text-destructive">{error}</p>}
      {nothingSaved && !error && <p className="text-muted-foreground">Ви ще нічого не зберегли.</p>}

      {deals.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-xl font-semibold">Знижки</h2>
          <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
            {deals.map((d) => (
              <DealCard key={d.id} deal={d} saved onToggleSave={(id) => unsaveDeal(id)} />
            ))}
          </div>
        </section>
      )}

      {events.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-xl font-semibold">Події</h2>
          <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
            {events.map((e) => (
              <EventCard key={e.id} event={e} saved onToggleSave={(id) => unsaveEvent(id)} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
