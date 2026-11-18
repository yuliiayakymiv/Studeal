// Теми сайту. Кольори задаються CSS-змінними shadcn, тому змінюються всі елементи разом.
// Кольори університетів узято з опису їхньої айдентики. Міняти їх можна лише тут.

// Спільні для всіх тем.
const base = {
  "--destructive": "#dc2626",
  "--destructive-foreground": "#ffffff",
};

// Допоміжна функція: гарантує, що кожна тема задає один і той самий набір змінних.
function theme(label, dark, v) {
  return {
    label,
    dark,
    vars: {
      ...base,
      "--background": v.background,
      "--foreground": v.foreground,
      "--card": v.card ?? v.background,
      "--card-foreground": v.foreground,
      "--popover": v.card ?? v.background,
      "--popover-foreground": v.foreground,
      "--primary": v.primary,
      "--primary-foreground": v.primaryForeground ?? "#ffffff",
      "--secondary": v.muted,
      "--secondary-foreground": v.foreground,
      "--muted": v.muted,
      "--muted-foreground": v.mutedForeground,
      "--accent": v.accent,
      "--accent-foreground": v.foreground,
      "--border": v.border,
      "--input": v.border,
      "--ring": v.ring ?? v.primary,
    },
  };
}

export const THEMES = {
  light: theme("Світла", false, {
    background: "#ffffff",
    foreground: "#1d2433",
    primary: "#4f46e5",
    muted: "#f3f4f6",
    mutedForeground: "#6b7280",
    accent: "#eef2ff",
    border: "#e5e7eb",
  }),

  dark: theme("Чорна", true, {
    background: "#0f0f14",
    foreground: "#f4f4f5",
    card: "#18181f",
    primary: "#6366f1",
    muted: "#23232d",
    mutedForeground: "#a1a1aa",
    accent: "#2a2a36",
    border: "#2e2e3a",
  }),

  // УКУ: бордовий, молочний фон, золотий акцент, графітовий текст.
  ucu: theme("УКУ", false, {
    background: "#ffffff",
    foreground: "#23262b",
    primary: "#8b1d3d",
    muted: "#faf8f5",
    mutedForeground: "#5d6168",
    accent: "#f3e8cc", // світла версія золотого #C89D3C
    border: "#e8e2d9",
    ring: "#c89d3c",
  }),

  // Львівська політехніка: індиго, ціановий акцент, холодний світло-сірий фон.
  lp: theme("Політехніка", false, {
    background: "#ffffff",
    foreground: "#1b2233",
    primary: "#282d78",
    muted: "#f4f7fa",
    mutedForeground: "#586377",
    accent: "#dff2fb", // світла версія ціанового #00A1E4
    border: "#dce4ec",
    ring: "#00a1e4",
  }),

  // ЛНУ імені Івана Франка: королівський синій, золото, кремовий фон.
  lnu: theme("ЛНУ ім. Франка", false, {
    background: "#ffffff",
    foreground: "#22252a",
    primary: "#141b4d",
    muted: "#f9f8f4",
    mutedForeground: "#5c6068",
    accent: "#f4ecd0", // світла версія золотого #C9A236
    border: "#e7e2d2",
    ring: "#c9a236",
  }),
};

const KEY = "studeal-theme";

export function getTheme() {
  const saved = localStorage.getItem(KEY);
  return THEMES[saved] ? saved : "light";
}

export function applyTheme(name) {
  const t = THEMES[name] || THEMES.light;
  const root = document.documentElement;
  Object.entries(t.vars).forEach(([key, value]) => root.style.setProperty(key, value));
  // Клас .dark потрібен компонентам shadcn із варіантом dark:.
  root.classList.toggle("dark", t.dark);
  root.style.colorScheme = t.dark ? "dark" : "light";
  root.dataset.theme = name;
  localStorage.setItem(KEY, name);
}
