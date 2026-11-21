/** Shared JSON transport. Requests are cancellable by the owning view. */
export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch("/api" + path, init);
  if (!res.ok)
    throw new Error(
      res.status === 503
        ? "Database unavailable. Run the bootstrap command and retry."
        : `Request failed (${res.status}). Please retry.`,
    );
  return res.json();
}
