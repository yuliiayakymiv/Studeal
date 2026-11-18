export async function apiFetch(path, { token, method = "GET", params } = {}) {
  const qs = params
    ? new URLSearchParams(Object.entries(params).filter(([, v]) => v)).toString()
    : "";
  const res = await fetch(`/api${path}${qs ? `?${qs}` : ""}`, {
    method,
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return method === "GET" ? res.json() : null;
}
