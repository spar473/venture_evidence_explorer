import { useEffect, useRef, useState, type Dispatch, type SetStateAction } from "react";
import type { Comparison, VenturePage } from "./types";
import type { ComparisonRequest } from "./api-schema";
import type { Filters } from "./filters";
import { api } from "./api";

/** Abort on replacement/unmount, and guard commits even if a transport ignores abort. */
export function useResource<T>(path: string, retry = 0, delay = 0) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let live = true;
    const controller = new AbortController();
    setLoading(true); setError(""); setData(null);
    const timer = setTimeout(() => {
      api<T>(path, { signal: controller.signal })
        .then(value => { if (live) setData(value); })
        .catch((e: Error) => { if (live && e.name !== "AbortError") setError(e.message); })
        .finally(() => { if (live) setLoading(false); });
    }, delay);
    return () => { live = false; clearTimeout(timer); controller.abort(); };
  }, [path, retry, delay]);
  return { data, error, loading };
}

export function useVenturePage(filters: Partial<Filters> & { q?: string }, offset: number, limit: number, retry = 0) {
  const params = new URLSearchParams({ q: filters.q || "", programme: filters.programme || "", connection_type: filters.connection || "", limit: String(limit), offset: String(offset) });
  if (filters.year) params.set("year", filters.year);
  return useResource<VenturePage>("/ventures?" + params.toString(), retry, 120);
}

/** Only view/session inputs survive navigation; inactive views do not keep requests mounted. */
export type ComparisonSession = {
  subject: string;
  subjectName: string;
  subjectSearch: string;
  subjectOffset: number;
  description: string;
  mode: NonNullable<ComparisonRequest["mode"]>;
  comparison: Comparison | null;
  comparisonKey: string | null;
};

export function useComparison(session: ComparisonSession, setSession: Dispatch<SetStateAction<ComparisonSession>>, filters: Filters) {
  const {subject, description, mode} = session;
  const {programme, year, connection} = filters;
  const configKey = JSON.stringify([subject, description, mode, programme, year, connection]);
  const request = useRef(0);
  const pending = useRef<AbortController | null>(null);
  const [busy, setBusy] = useState(false);
  const [compareError, setCompareError] = useState("");
  const comparison = session.comparisonKey === configKey ? session.comparison : null;
  function setComparison(value: Comparison | null) {
    setSession(s => ({...s, comparison: value, comparisonKey: value ? configKey : null}));
  }
  useEffect(() => {
    request.current++; pending.current?.abort();
    if (session.comparisonKey !== configKey) setSession(s => ({...s, comparison: null, comparisonKey: null}));
    setBusy(false); setCompareError("");
    return () => { request.current++; pending.current?.abort(); };
    // Session data is keyed to these inputs; completing a request must not reset it.
  }, [subject, description, mode, programme, year, connection]);
  async function runCompare(event: React.FormEvent) {
    event.preventDefault();
    pending.current?.abort();
    const controller = new AbortController();
    pending.current = controller;
    const current = ++request.current;
    setBusy(true); setCompareError(""); setComparison(null);
    try {
      const value = await api<Comparison>("/compare", {
        method: "POST", signal: controller.signal,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({subject_id: subject || null, query: description, mode, programme, year: year ? Number(year) : null, connection_type: connection}),
      });
      if (current === request.current) setComparison(value);
    } catch (e) {
      if (current === request.current && (e as Error).name !== "AbortError") setCompareError((e as Error).message);
    } finally {
      if (current === request.current) setBusy(false);
    }
  }
  return {comparison, setComparison, busy, compareError, runCompare};
}
