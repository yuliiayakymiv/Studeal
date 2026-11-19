import { THEMES } from "@/lib/themes";

// Кнопка, що переливається основними кольорами всіх тем сайту.
const COLORS = Object.values(THEMES).flatMap((t) =>
  [t.vars["--primary"], t.vars["--ring"]].filter(Boolean),
);
const GRADIENT = `linear-gradient(90deg, ${[...new Set(COLORS)].join(", ")}, ${COLORS[0]})`;

export default function ShimmerButton({ children, className = "", ...props }) {
  return (
    <button
      type="button"
      className={`studeal-shimmer inline-flex items-center justify-center rounded-lg px-6 py-3 text-base font-semibold text-white shadow-md transition-transform hover:scale-[1.03] focus-visible:outline-2 focus-visible:outline-offset-2 ${className}`}
      style={{ backgroundImage: GRADIENT }}
      {...props}
    >
      {children}
    </button>
  );
}
