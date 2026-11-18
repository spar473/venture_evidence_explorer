export function Pagination({total, offset, limit, onChange, label}: {
  total: number; offset: number; limit: number; onChange: (offset: number) => void; label: string;
}) {
  return <nav className="pagination" aria-label={label}>
    <button type="button" disabled={offset === 0} onClick={() => onChange(Math.max(0, offset - limit))}>Previous</button>
    <span aria-live="polite">{total ? `${offset + 1}–${Math.min(offset + limit, total)}` : "0"} of {total}</span>
    <button type="button" disabled={offset + limit >= total} onClick={() => onChange(offset + limit)}>Next</button>
  </nav>;
}
