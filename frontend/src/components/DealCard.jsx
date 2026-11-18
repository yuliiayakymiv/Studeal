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
        <Link to={`/deals/${deal.id}`} className="font-semibold hover:underline">
          {deal.title}
        </Link>
        {deal.discount && <Badge>{deal.discount}</Badge>}
        {deal.address && <p className="text-sm text-muted-foreground">{deal.address}</p>}
        {deal.description && <p className="text-sm text-muted-foreground">Умови: {deal.description}</p>}
        <Button
          size="sm"
          variant={saved ? "default" : "outline"}
          onClick={() => onToggleSave(deal.id, !saved)}
        >
          {saved ? "♥ Збережено" : "♡ Зберегти"}
        </Button>
      </CardContent>
    </Card>
  );
}
