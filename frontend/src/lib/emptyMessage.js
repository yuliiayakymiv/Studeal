import { DEAL_CATEGORIES, EVENT_CATEGORIES, UNIVERSITIES } from "@/lib/categories";

// Пояснення, чому список порожній. noun: "знижок" або "подій".
export function emptyMessage(noun, { university, category }) {
  const uni = UNIVERSITIES.find((u) => u.value === university);
  if (uni) {
    return `На жаль, для ${uni.genitive} зараз немає ${noun}. Спробуйте обрати інший університет або переглянути всі пропозиції.`;
  }

  const categories = noun === "знижок" ? DEAL_CATEGORIES : EVENT_CATEGORIES;
  const cat = categories.find((c) => c.value === category);
  if (cat) {
    return `На жаль, у категорії «${cat.label}» зараз немає ${noun}. Спробуйте обрати іншу категорію.`;
  }

  return `На жаль, зараз немає дійсних ${noun}. Завітайте пізніше.`;
}
