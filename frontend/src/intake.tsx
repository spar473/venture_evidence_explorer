import { useEffect, useRef, useState } from "react";
import type {
  Draft,
  DraftPage,
  DraftContent,
  DuplicatePage,
  IntakeComparison,
  SuppliedClaim,
  ResearchSubjectsResponse,
  SaveDraft,
} from "./api-schema";
import { useResource } from "./hooks";
import { Status } from "./shared";

import {
  blank,
  draftForm,
  newEditor,
  readEditor,
  storageKey,
  type ClaimForm,
  type Editor,
  type Form,
} from "./intake-session";
const unknown = { precision: "unknown" as const, lower_bound: null, upper_bound: null };
const newClaim = (): ClaimForm => ({
  source: {
    field: "solution",
    text: "",
    source_url: "",
    source_title: "",
    publisher: "",
    locator: "",
    source_relationship: "other_identified",
    retrieved_on: "",
    published_date: unknown,
    effective_date: unknown,
  },
  precision: "unknown",
  value: "",
});
function toDate(c: ClaimForm) {
  if (c.precision === "unknown") return unknown;
  if (c.precision === "day")
    return { precision: c.precision, lower_bound: c.value, upper_bound: c.value };
  if (c.precision === "year") {
    if (!/^\d{4}$/.test(c.value)) throw Error("Publication year must be YYYY");
    return {
      precision: c.precision,
      lower_bound: c.value + "-01-01",
      upper_bound: c.value + "-12-31",
    };
  }
  if (!/^\d{4}-\d{2}$/.test(c.value)) throw Error("Publication month must be YYYY-MM");
  const [y, m] = c.value.split("-").map(Number);
  const last = new Date(Date.UTC(y, m, 0)).getUTCDate();
  return {
    precision: c.precision,
    lower_bound: c.value + "-01",
    upper_bound: c.value + "-" + String(last).padStart(2, "0"),
  };
}
class IntakeError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}
async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch("/api" + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const d = await response.json().catch(() => null);
    throw new IntakeError(
      typeof d?.detail === "string"
        ? d.detail
        : response.status >= 500
          ? "Saving unavailable. Your input is retained; retry the same save."
          : "Check required fields, source URLs and dates. Your input is retained.",
      response.status,
    );
  }
  return response.json();
}
export function IntakeWorkspace() {
  const [editor, setEditor] = useState<Editor>(readEditor);
  const current = useRef(editor);
  const form = editor.form;
  const [saved, setSaved] = useState<Draft | null>(null);
  const [comparison, setComparison] = useState<IntakeComparison | null>(null);
  const [error, setError] = useState("");
  const [storageError, setStorageError] = useState("");
  const [busy, setBusy] = useState(false);
  const [checking, setChecking] = useState(!!editor.draft_id);
  const [restoreError, setRestoreError] = useState(false);
  const [retry, setRetry] = useState(0);
  const [policy, setPolicy] = useState<"exploration" | "accepted">("exploration");
  const generation = useRef(0);
  const mounted = useRef(true);
  const active = (ticket: number, id: string) =>
    mounted.current && ticket === generation.current && current.current.editor_id === id;
  function commit(next: Editor) {
    let persisted = true;
    current.current = next;
    try {
      localStorage.setItem(storageKey, JSON.stringify(next));
      setStorageError("");
    } catch {
      persisted = false;
      setStorageError(
        "Browser recovery storage is unavailable. Keep this editor open to retain your input.",
      );
    }
    setEditor(next);
    return persisted;
  }
  function setForm(update: Form | ((f: Form) => Form)) {
    if (locked) return;
    generation.current++;
    setComparison(null);
    commit({
      ...current.current,
      form: typeof update === "function" ? update(current.current.form) : update,
    });
  }
  const { data: research } = useResource<ResearchSubjectsResponse>("/research/subjects");
  const { data: list, error: listError } = useResource<DraftPage>("/intake/drafts", retry);
  const { data: duplicates } = useResource<DuplicatePage>(
    "/intake/duplicates?q=" +
      encodeURIComponent(form.name) +
      "&aliases=" +
      encodeURIComponent(form.aliases) +
      "&exclude_draft=" +
      encodeURIComponent(editor.draft_id || ""),
    0,
    150,
  );
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      generation.current++;
    };
  }, []);
  useEffect(() => {
    let live = true;
    const id = editor.editor_id;
    const draftId = editor.draft_id;
    if (!draftId) {
      setChecking(false);
      setRestoreError(false);
      return;
    }
    setChecking(true);
    setRestoreError(false);
    fetch("/api/intake/drafts/" + encodeURIComponent(draftId))
      .then(async (r) => {
        if (!r.ok)
          throw Error(
            "The saved draft cannot be reopened. Your edits and draft identity are retained; reload to retry.",
          );
        return r.json() as Promise<Draft>;
      })
      .then((d) => {
        if (live && current.current.editor_id === id) {
          setSaved((old) =>
            old?.draft_id === d.draft_id && old.revision_number > d.revision_number ? old : d,
          );
          setRestoreError(false);
        }
      })
      .catch((e) => {
        if (live && current.current.editor_id === id) {
          setError((e as Error).message);
          setRestoreError(true);
        }
      })
      .finally(() => {
        if (live && current.current.editor_id === id) setChecking(false);
      });
    return () => {
      live = false;
    };
  }, [editor.editor_id, editor.draft_id, retry]);
  const conflict = !!(
    editor.draft_id &&
    saved &&
    saved.revision_number !== editor.base_revision &&
    !editor.pending
  );
  const locked = busy || !!editor.pending;
  function open(d: Draft) {
    if (locked) return;
    generation.current++;
    setComparison(null);
    setError("");
    setSaved((old) =>
      old?.draft_id === d.draft_id && old.revision_number > d.revision_number ? old : d,
    );
    setRestoreError(false);
    // Lock the form in the same render that installs the draft. Setting this only in the
    // identity-check effect left a window where the form was enabled, then disabled, and a
    // keystroke typed in between was silently dropped before the next save.
    setChecking(true);
    commit(newEditor(current.current.legacy ? current.current.form : draftForm(d), d));
  }
  function start() {
    if (locked) return;
    generation.current++;
    setSaved(null);
    setComparison(null);
    setError("");
    setChecking(false);
    setRestoreError(false);
    commit(newEditor());
  }
  function claim(i: number, key: keyof SuppliedClaim, value: string) {
    setForm((f) => ({
      ...f,
      claims: f.claims.map((c, n) =>
        n === i ? { ...c, source: { ...c.source, [key]: value } } : c,
      ),
    }));
  }
  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (busy || checking || restoreError || conflict || editor.legacy) return;
    const snapshot = current.current;
    const ticket = ++generation.current;
    const id = snapshot.editor_id;
    let sent = false;
    setBusy(true);
    setError("");
    try {
      let request = snapshot.pending;
      if (!request) {
        const contentForm = snapshot.form;
        const content: DraftContent = {
          format_version: "venture-intake:1",
          name: contentForm.name,
          aliases: contentForm.aliases
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
          description: contentForm.description,
          research_subject_id: contentForm.research_subject_id,
          claims: contentForm.claims.map((c) => ({ ...c.source, published_date: toDate(c) })),
        };
        request = {
          path: snapshot.draft_id
            ? `/intake/drafts/${snapshot.draft_id}/revisions`
            : "/intake/drafts",
          body: {
            ...content,
            request_id: crypto.randomUUID(),
            expected_revision: snapshot.base_revision,
          } as SaveDraft,
        };
        // Persist the exact route, identity, base and retry key before sending bytes.
        if (!commit({ ...snapshot, pending: request }))
          throw Error(
            "Recovery storage is unavailable; save was not sent. Your input is retained.",
          );
      }
      sent = true;
      const d = await post<Draft>(request.path, request.body);
      if (!active(ticket, id)) return;
      commit({
        ...current.current,
        draft_id: d.draft_id,
        base_revision: d.revision_number,
        pending: null,
      });
      setSaved(d);
      setRetry((n) => n + 1);
      // A replay acknowledges its original revision; inspect newer server revisions
      // without replacing the recovered local form or silently rebasing it.
      const r = await fetch("/api/intake/drafts/" + encodeURIComponent(d.draft_id));
      if (!r.ok)
        throw Error(
          "Save acknowledged, but the latest revision could not be checked. Your edits are retained; reload to reconcile.",
        );
      const latest = (await r.json()) as Draft;
      if (active(ticket, id)) setSaved(latest);
    } catch (e) {
      if (active(ticket, id)) {
        if (!sent) {
          commit({ ...current.current, pending: null });
        } else if (e instanceof IntakeError && e.status >= 400 && e.status < 500) {
          commit({ ...current.current, pending: null });
          if (current.current.draft_id) {
            try {
              const r = await fetch(
                "/api/intake/drafts/" + encodeURIComponent(current.current.draft_id),
              );
              if (r.ok) {
                const d = (await r.json()) as Draft;
                if (active(ticket, id)) setSaved(d);
              } else if (active(ticket, id)) setRestoreError(true);
            } catch {
              if (active(ticket, id)) setRestoreError(true);
            }
          }
        } else if (!current.current.pending) setRestoreError(true);
        if (active(ticket, id)) setError((e as Error).message);
      }
    } finally {
      if (active(ticket, id)) setBusy(false);
    }
  }
  async function compare() {
    if (!saved || busy || editor.pending) return;
    const ticket = ++generation.current,
      key = editor.editor_id;
    setBusy(true);
    setError("");
    try {
      const result = await post<IntakeComparison>(`/intake/drafts/${saved.draft_id}/compare`, {
        policy,
        mode: "product_customer",
      });
      if (active(ticket, key)) setComparison(result);
    } catch (e) {
      if (active(ticket, key)) setError((e as Error).message);
    } finally {
      if (active(ticket, key)) setBusy(false);
    }
  }
  return (
    <section className="intake-workspace">
      <p className="notice">
        Saved drafts are local user assertions. Supplied source attributions remain unreviewed.
        Saving never accepts identity, legal facts or retrieval evidence.
      </p>
      <div className="intake-layout">
        <section>
          <h2>{editor.draft_id ? "Edit saved draft" : "Add venture"}</h2>
          <form onSubmit={save}>
            <fieldset disabled={locked || checking || restoreError} className="intake-form">
              <label>
                Venture or project name
                <input
                  aria-label="Venture or project name"
                  required
                  maxLength={300}
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </label>
              <label>
                Aliases (comma separated)
                <input
                  value={form.aliases}
                  onChange={(e) => setForm({ ...form, aliases: e.target.value })}
                />
              </label>
              <label>
                Description
                <textarea
                  aria-label="Description"
                  maxLength={5000}
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </label>
              <label>
                Existing research query subject (optional)
                <select
                  value={form.research_subject_id || ""}
                  onChange={(e) =>
                    setForm({ ...form, research_subject_id: e.target.value || null })
                  }
                >
                  <option value="">Unresolved new subject</option>
                  {research?.items.map((s) => (
                    <option key={s.subject_id} value={s.subject_id}>
                      {s.display_name} · {s.identity_link_status}
                    </option>
                  ))}
                </select>
              </label>
              {!!duplicates?.items.length && (
                <aside className="notice">
                  <strong>Possible identity duplicates — unresolved</strong>
                  <ul>
                    {duplicates.items.map((d) => (
                      <li key={d.kind + d.subject_id}>
                        {d.display_name} · {d.kind} · {d.basis}
                      </li>
                    ))}
                  </ul>
                  No name-based merge.
                </aside>
              )}
              {form.claims.map((c, i) => (
                <fieldset key={i}>
                  <legend>Optional source attribution {i + 1} · unreviewed</legend>
                  {(
                    [
                      ["text", "Attributed claim"],
                      ["source_url", "Source URL"],
                      ["source_title", "Source title"],
                      ["publisher", "Publisher"],
                      ["locator", "Passage locator"],
                      ["retrieved_on", "Retrieval date"],
                    ] as const
                  ).map(([key, title]) => (
                    <label key={key}>
                      {title}
                      <input
                        required
                        type={
                          key === "source_url" ? "url" : key === "retrieved_on" ? "date" : "text"
                        }
                        value={c.source[key]}
                        onChange={(e) => claim(i, key, e.target.value)}
                      />
                    </label>
                  ))}
                  <label>
                    Assertion field
                    <select
                      value={c.source.field}
                      onChange={(e) => claim(i, "field", e.target.value)}
                    >
                      {[
                        "problem",
                        "solution",
                        "intended_user",
                        "buyer",
                        "technology",
                        "business_model",
                        "validation",
                        "deployment",
                        "other",
                      ].map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Claim responsibility
                    <select
                      value={c.source.source_relationship}
                      onChange={(e) => claim(i, "source_relationship", e.target.value)}
                    >
                      {[
                        "entrant",
                        "company",
                        "university",
                        "customer",
                        "regulator",
                        "investor",
                        "project_team",
                        "other_identified",
                      ].map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Publication precision
                    <select
                      value={c.precision}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          claims: form.claims.map((v, n) =>
                            n === i
                              ? { ...v, precision: e.target.value as ClaimForm["precision"] }
                              : v,
                          ),
                        })
                      }
                    >
                      {["unknown", "year", "month", "day"].map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                  </label>
                  {c.precision !== "unknown" && (
                    <label>
                      Publication value
                      <input
                        required
                        value={c.value}
                        onChange={(e) =>
                          setForm({
                            ...form,
                            claims: form.claims.map((v, n) =>
                              n === i ? { ...v, value: e.target.value } : v,
                            ),
                          })
                        }
                      />
                    </label>
                  )}
                  <p className="muted">
                    User-supplied attribution, not authenticated publisher evidence. Occurrence
                    dates stay unknown unless supplied separately through the versioned API.
                  </p>
                  <button
                    type="button"
                    onClick={() =>
                      setForm({ ...form, claims: form.claims.filter((_, n) => n !== i) })
                    }
                  >
                    Remove attribution {i + 1}
                  </button>
                </fieldset>
              ))}
              <button
                type="button"
                onClick={() => setForm({ ...form, claims: [...form.claims, newClaim()] })}
              >
                Add optional source attribution
              </button>
              <button type="submit" disabled={conflict || restoreError || editor.legacy}>
                {busy ? "Working…" : editor.draft_id ? "Save revision" : "Save draft"}
              </button>
            </fieldset>
            <button type="button" disabled={locked} onClick={start}>
              Start another draft
            </button>
            {editor.pending && !busy && (
              <button type="submit" disabled={checking || restoreError}>
                Retry uncertain save
              </button>
            )}
            {checking && <Status>Checking saved draft identity and revision…</Status>}
            {editor.pending && (
              <Status>
                A save may have completed. Retry the same request before editing or switching
                drafts. Your input is retained.
              </Status>
            )}
            {editor.legacy && (
              <div role="alert">
                Recovered input has no saved-draft identity. Select an existing draft to use as its
                revision base, or{" "}
                <button type="button" onClick={() => commit({ ...current.current, legacy: false })}>
                  Treat recovered input as a new draft
                </button>
                .
              </div>
            )}
            {restoreError && (
              <button type="button" onClick={() => setRetry((n) => n + 1)}>
                Retry checking saved draft
              </button>
            )}
            {conflict && (
              <div role="alert">
                A newer server revision exists (revision {saved?.revision_number}); your edits still
                use revision {editor.base_revision}. No automatic overwrite or new draft was made.
                <button
                  type="button"
                  disabled={locked}
                  onClick={() => {
                    generation.current++;
                    setComparison(null);
                    setError("");
                    commit({ ...current.current, base_revision: saved!.revision_number });
                  }}
                >
                  Use latest revision as base, keeping my edits
                </button>
              </div>
            )}

            {storageError && <Status error>{storageError}</Status>}
          </form>
          {error && <Status error>{error}</Status>}
          {saved && (
            <section className="saved-draft">
              <h3>Saved: {saved.content.name}</h3>
              <p>Draft / unreviewed · revision {saved.revision_number} · identity unresolved</p>
              <p>Unknown / unverified: {saved.unknowns.join(", ")}</p>
              <label>
                Candidate evidence policy
                <select
                  disabled={locked}
                  value={policy}
                  onChange={(e) => {
                    generation.current++;
                    setBusy(false);
                    setComparison(null);
                    setPolicy(e.target.value as typeof policy);
                  }}
                >
                  <option value="exploration">Exploration</option>
                  <option value="accepted">Accepted only</option>
                </select>
              </label>
              <button disabled={locked || checking || restoreError} type="button" onClick={compare}>
                Compare saved draft
              </button>
              <p className="muted">
                Uses the last saved revision. Unsaved edits remain in the form.
              </p>
            </section>
          )}
        </section>
        <aside>
          <h2>Saved local drafts</h2>
          {listError && <Status error>{listError}</Status>}
          {list?.items.map((d) => (
            <p key={d.draft_id}>
              <button type="button" disabled={locked} onClick={() => open(d)}>
                {d.content.name} · revision {d.revision_number}
              </button>
            </p>
          ))}
          {list?.total === 0 && <p>No saved drafts.</p>}
        </aside>
      </div>
      {comparison && (
        <section className="intake-comparison">
          <h2>Saved-draft comparison</h2>
          <p>{comparison.identity_limitation}</p>
          <p>
            Query inputs: {comparison.query_fields.join(", ") || "No descriptive evidence supplied"}{" "}
            · {comparison.wrapper_version} · base {comparison.baseline_version}
          </p>
          <div className="table-scroll" tabIndex={0}>
            <table>
              <thead>
                <tr>
                  <th>Record</th>
                  <th>Disposition</th>
                  <th>Matching evidence</th>
                  <th>Unknown / unverified</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th>{comparison.draft.content.name}</th>
                  <td>Saved draft · query only</td>
                  <td>{comparison.effective_query || "No informative input"}</td>
                  <td>{comparison.draft.unknowns.join(", ")}</td>
                </tr>
                {comparison.results.map((r) => (
                  <tr key={r.venture.venture_id}>
                    <th>{r.venture.display_name}</th>
                    <td>Lexical score {r.ranking_score.toFixed(3)}</td>
                    <td>
                      {r.matched_terms.join(", ")}
                      {r.evidence.map((e) => (
                        <p key={e.observation.observation_id}>
                          <a href={e.observation.url} target="_blank" rel="noreferrer">
                            {e.observation.source_title}
                          </a>{" "}
                          · {e.observation.locator} · {e.observation.review_status}
                        </p>
                      ))}
                    </td>
                    <td>{r.unavailable_evidence.join(", ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {comparison.abstention_reason && <Status>{comparison.abstention_reason}</Status>}
        </section>
      )}
    </section>
  );
}
