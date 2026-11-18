import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import { apiFetch } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import DealCard from "@/components/DealCard";

export default function Catalog() {
  const auth = useAuth();
  const token = auth.user?.access_token;
  const [params, setParams] = useSearchParams();
  const category = params.get("category") || "";
  const university = params.get("university") || "";
  const q = params.get("q") || "";

  const [search, setSearch] = useState(q);
  const [categories, setCategories] = useState([]);
  const [deals, setDeals] = useState([]);
  const [savedIds, setSavedIds] = useState(new Set());
  const [error, setError] = useState("");

  function updateParam(key, value) {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next, { replace: true });
  }

  // Пошук із затримкою 300 мс.
  useEffect(() => {
    const t = setTimeout(() => updateParam("q", search), 300);
    return () => clearTimeout(t);
  }, [search]);

  useEffect(() => {
    if (!token) return;
    apiFetch("/deals/categories", { token })
      .then(setCategories)
      .catch(() => setError("Не вдалося завантажити категорії."));
  }, [token]);

  useEffect(() => {
    if (!token) return;
    setError("");
    Promise.all([
      apiFetch("/me/saved", { token }),
      apiFetch("/deals", { token, params: { category, university, q } }),
    ])
      .then(([saved, list]) => {
        setSavedIds(new Set(saved.map((d) => d.id)));
        setDeals(list);
      })
      .catch(() => setError("Помилка завантаження. Чи запущено API?"));
  }, [token, category, university, q]);

  async function toggleSave(id, on) {
    try {
      await apiFetch(`/me/saved/${id}`, { token, method: on ? "POST" : "DELETE" });
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
        {categories.map((c) => (
          <Button
            key={c}
            size="sm"
            variant={category === c ? "default" : "outline"}
            onClick={() => updateParam("category", c)}
          >
            {c}
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

      <Input placeholder="Пошук: кава, спортзал, коворкінг…" value={search} onChange={(e) => setSearch(e.target.value)} />

      {error && <p className="text-destructive">{error}</p>}
      <p className="text-sm text-muted-foreground">Знайдено: {deals.length}</p>

      <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
        {deals.map((d) => (
          <DealCard key={d.id} deal={d} saved={savedIds.has(d.id)} onToggleSave={toggleSave} />
        ))}
      </div>
    </div>
  );
}
