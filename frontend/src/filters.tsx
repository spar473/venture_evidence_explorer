import type { Facets } from "./types";
import { label } from "./labels";
export type Filters = { programme: string; year: string; connection: string };
export function FilterControls({
  filters,
  setFilters,
  facets,
}: {
  filters: Filters;
  setFilters: (filters: Filters) => void;
  facets: Facets | null;
}) {
  const { programme, year, connection } = filters;
  return (
    <>
      <label>
        Recorded programme
        <select
          aria-label="Recorded programme"
          value={programme}
          onChange={(e) => setFilters({ ...filters, programme: e.target.value })}
        >
          <option value="">All recorded programmes</option>
          {facets?.programmes.map((p) => (
            <option key={p.programme} value={p.programme}>
              {label(p.programme)}
            </option>
          ))}
        </select>
      </label>
      <label>
        Award year
        <select
          aria-label="Award year"
          value={year}
          onChange={(e) => setFilters({ ...filters, year: e.target.value })}
        >
          <option value="">All award years</option>
          {facets?.years.map((y) => (
            <option key={y}>{y}</option>
          ))}
        </select>
      </label>
      <label>
        University relationship
        <select
          aria-label="University relationship"
          value={connection}
          onChange={(e) => setFilters({ ...filters, connection: e.target.value })}
        >
          <option value="">All relationship types</option>
          {facets?.connection_types.map((c) => (
            <option key={c.connection_type} value={c.connection_type}>
              {label(c.connection_type)}
            </option>
          ))}
        </select>
      </label>
    </>
  );
}
