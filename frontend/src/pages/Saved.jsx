import { useEffect, useState } from "react";
import { useAuth } from "react-oidc-context";
import { apiFetch } from "@/lib/api";
import DealCard from "@/components/DealCard";

export default function Saved() {
  const auth = useAuth();
  const token = auth.user?.access_token;
  const [deals, setDeals] = useState([]);
  const [error, setError] = useState("");

  function load() {
    apiFetch("/me/saved", { token })
      .then(setDeals)
      .catch(() => setError("Помилка завантаження."));
  }

  useEffect(() => {
    if (token) load();
  }, [token]);

  async function unsave(id) {
    try {
      await apiFetch(`/me/saved/${id}`, { token, method: "DELETE" });
      load();
    } catch {
      setError("Не вдалося прибрати зі збережених.");
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Збережені знижки</h1>
      {error && <p className="text-destructive">{error}</p>}
      {deals.length === 0 && !error && (
        <p className="text-muted-foreground">Ви ще нічого не зберегли.</p>
      )}
      <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
        {deals.map((d) => (
          <DealCard key={d.id} deal={d} saved onToggleSave={(id) => unsave(id)} />
        ))}
      </div>
    </div>
  );
}
