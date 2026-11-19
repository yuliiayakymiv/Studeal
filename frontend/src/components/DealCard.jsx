import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function DealCard({ deal, saved, onToggleSave }) {
  return (
    <Card className="overflow-hidden">
      {deal.image_url ? (
        <img src={deal.image_url} alt={deal.venue} loading="lazy" className="h-40 w-full object-cover" />
      ) : (
        <div className="flex h-40 items-center justify-center bg-muted text-sm text-muted-foreground">
          Фото ще немає
        </div>
      )}
      <CardContent className="space-y-2 p-4">
        <p className="text-sm text-muted-foreground">{deal.venue}</p>
        <p className="font-semibold">{deal.title}</p>
        {deal.discount && (
          <div className="pt-1">
            <Badge>{deal.discount}</Badge>
          </div>
        )}
        {deal.address && <p className="text-sm text-muted-foreground">{deal.address}</p>}
        {deal.description && <p className="text-sm text-muted-foreground">Умови: {deal.description}</p>}
        <div className="flex flex-wrap items-center gap-3 pt-1">
          <Button
            size="sm"
            variant={saved ? "default" : "outline"}
            onClick={() => onToggleSave(deal.id, !saved)}
          >
            {saved ? "♥ Збережено" : "♡ Зберегти"}
          </Button>
          <Link
            to={`/deals/${deal.id}`}
            className="text-sm font-medium text-primary underline-offset-4 transition-colors hover:text-primary/80 hover:underline"
          >
            Детальніше →
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
