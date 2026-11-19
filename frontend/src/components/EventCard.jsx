import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

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

export default function EventCard({ event, saved, onToggleSave }) {
  return (
    <Card className="overflow-hidden">
      {event.image_url ? (
        <img src={event.image_url} alt={event.title} loading="lazy" className="h-40 w-full object-cover" />
      ) : (
        <div className="flex h-40 items-center justify-center bg-muted text-sm text-muted-foreground">
          Фото ще немає
        </div>
      )}
      <CardContent className="space-y-2 p-4">
        <p className="text-sm font-semibold text-primary">{formatDate(event.starts_at)}</p>
        <p className="font-semibold">{event.title}</p>
        {event.venue && <p className="text-sm text-muted-foreground">{event.venue}</p>}
        {event.address && <p className="text-sm text-muted-foreground">{event.address}</p>}
        {event.price && <p className="text-sm">{event.price}</p>}
        <div className="flex flex-wrap items-center gap-3 pt-1">
          <Button
            size="sm"
            variant={saved ? "default" : "outline"}
            onClick={() => onToggleSave(event.id, !saved)}
          >
            {saved ? "♥ Збережено" : "♡ Зберегти"}
          </Button>
          {event.source_url && (
            <a
              href={event.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-primary underline-offset-4 transition-colors hover:text-primary/80 hover:underline"
            >
              Детальніше →
            </a>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
