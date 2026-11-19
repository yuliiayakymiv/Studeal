// Категорії, які завжди видно на сайті, навіть якщо знижок у них зараз немає.
// value має збігатися з колонкою category у CSV (малі англійські літери).
export const DEAL_CATEGORIES = [
  { value: "coffee", label: "Кава і кафе" },
  { value: "food", label: "Їжа" },
  { value: "coworking", label: "Коворкінги" },
  { value: "sport", label: "Спорт" },
  { value: "cinema", label: "Кіно" },
  { value: "culture", label: "Культура і мистецтво" },
];

export const EVENT_CATEGORIES = [
  { value: "quiz", label: "Квізи" },
  { value: "concert", label: "Концерти" },
  { value: "lecture", label: "Лекції" },
  { value: "workshop", label: "Майстер-класи" },
  { value: "culture", label: "Культура і мистецтво" },
];

// Університети для фільтра. value має збігатися з колонкою university у CSV.
// genitive використовується в реченнях на кшталт «для УКУ зараз немає знижок».
export const UNIVERSITIES = [
  { value: "ucu", label: "УКУ", genitive: "УКУ" },
  { value: "lnu", label: "ЛНУ", genitive: "ЛНУ імені Івана Франка" },
  { value: "lp", label: "Політехніка", genitive: "Львівської політехніки" },
];
