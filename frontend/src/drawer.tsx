import { useEffect, useRef, useState } from "react";
import type { Venture, VentureSummary } from "./types";
import { Profile } from "./profile";
import { Status } from "./shared";
import { useResource } from "./hooks";

/** A directory row carries only a summary; fetch its evidence when opened. */
export function EvidenceDrawer({
  v,
  onCompare,
  onClose,
}: {
  v: VentureSummary | Venture;
  onCompare: (v: Venture) => void;
  onClose: () => void;
}) {
  const drawer = useRef<HTMLDialogElement>(null);
  const [retry, setRetry] = useState(0);
  const { data, loading, error } = useResource<Venture>(
    "/ventures/" + encodeURIComponent(v.venture_id),
    retry,
  );
  useEffect(() => {
    const node = drawer.current;
    const opener = document.querySelector<HTMLButtonElement>(
      `.venture-open[data-venture-id="${CSS.escape(v.venture_id)}"]`,
    );
    node?.showModal();
    return () => {
      node?.close();
      opener?.focus({ preventScroll: true });
    };
  }, [v.venture_id]);
  useEffect(() => {
    drawer.current?.querySelector<HTMLButtonElement>("button")?.focus();
  }, [loading, error]);
  return (
    <dialog
      ref={drawer}
      className="profile-wrap"
      aria-label={v.display_name}
      onCancel={(e) => {
        e.preventDefault();
        onClose();
      }}
    >
      {data ? (
        <Profile v={data} onCompare={onCompare} onClose={onClose} />
      ) : (
        <section className="profile">
          <div className="section-head">
            <h2>{v.display_name}</h2>
            <button className="text" onClick={onClose}>
              Close profile
            </button>
          </div>
          {error ? (
            <Status error>
              {error} <button onClick={() => setRetry((n) => n + 1)}>Retry profile</button>
            </Status>
          ) : (
            <Status>Loading venture evidence…</Status>
          )}
        </section>
      )}
    </dialog>
  );
}
