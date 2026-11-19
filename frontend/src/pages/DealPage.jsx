import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import { apiFetch } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function DealPage() {
  const { id } = useParams();
  const auth = useAuth();
  const token = auth.user?.access_token;
  const [deal, setDeal] = useState(null);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    Promise.all([apiFetch(`/deals/${id}`, { token }), apiFetch("/me/saved", { token })])
      .then(([d, list]) => {
        setDeal(d);
        setSaved(list.some((x) => x.id === d.id));
      })
      .catch(() => setError("Знижку не знайдено або сталася помилка."));
  }, [id, token]);

  async function toggle() {
    try {
      await apiFetch(`/me/saved/${id}`, { token, method: saved ? "DELETE" : "POST" });
      setSaved(!saved);
    } catch {
      setError("Не вдалося зберегти.");
    }
  }

  if (error) return <p className="text-destructive">{error}</p>;
  if (!deal) return <p className="text-muted-foreground">Завантаження…</p>;

  return (
    <Card className="overflow-hidden">
      {deal.image_url ? (
        <img src={deal.image_url} alt={deal.venue} className="h-64 w-full object-cover" />
      ) : (
        <div className="flex h-64 items-center justify-center bg-muted text-muted-foreground">Фото ще немає</div>
      )}
      <CardContent className="space-y-3 p-6">
        <p className="text-muted-foreground">{deal.venue}</p>
        <h1 className="text-2xl font-bold">{deal.title}</h1>
        {deal.discount && <Badge>{deal.discount}</Badge>}
        {deal.address && <p>{deal.address}</p>}
        {deal.description && <p>Умови: {deal.description}</p>}
        {deal.valid_until && <p className="text-sm text-muted-foreground">Діє до {deal.valid_until}</p>}
        <div className="flex flex-wrap gap-2">
          <Button variant={saved ? "default" : "outline"} onClick={toggle}>
            {saved ? "♥ Збережено" : "♡ Зберегти"}
          </Button>
          {deal.source_url && (
            <Button asChild variant="ghost">
              <a href={deal.source_url} target="_blank" rel="noopener noreferrer">Детальніше →</a>
            </Button>
          )}
        </div>
        <Link
          to="/catalog"
          className="text-sm font-medium text-primary underline-offset-4 transition-colors hover:text-primary/80 hover:underline"
        >
          ← До каталогу
        </Link>
      </CardContent>
    </Card>
  );
}
