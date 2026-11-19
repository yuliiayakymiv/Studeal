export async function apiFetch(path, { token, method = "GET", params, body } = {}) {
  const qs = params
    ? new URLSearchParams(Object.entries(params).filter(([, v]) => v)).toString()
    : "";
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const res = await fetch(`/api${path}${qs ? `?${qs}` : ""}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  if (res.status === 204) return null;
  return (res.headers.get("content-type") || "").includes("json") ? res.json() : null;
}
