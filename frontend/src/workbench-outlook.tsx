/// <reference types="vite/client" />
import type {ReactNode} from "react";
import type {WorkbenchGates} from "./api-schema";
import limits from "../../docs/healthtech-pilot/PUBLIC_DATA_LIMITS.md?raw";
import {GateProgress} from "./workbench-shared";
import {Status} from "./shared";

const documentation = "https://github.com/spar473/venture_evidence_explorer/blob/implementation/precedent-workbench/docs/healthtech-pilot/PUBLIC_DATA_LIMITS.md";

function inlineMarkdown(text: string): ReactNode[] {
  const inline = /(\*\*([^*]+)\*\*|`([^`]+)`|\[([^\]]+)\]\(([^)]+)\))/g;
  const out: ReactNode[] = [];
  let start = 0;
  for (const match of text.matchAll(inline)) {
    const index = match.index ?? 0;
    out.push(text.slice(start, index));
    if (match[2]) out.push(<strong key={index}>{match[2]}</strong>);
    else if (match[3]) out.push(<code key={index}>{match[3]}</code>);
    else {
      const url = new URL(match[5], documentation);
      out.push(url.protocol === "https:" ? <a key={index} href={url.href} target="_blank" rel="noreferrer">{match[4]}</a> : match[4]);
    }
    start = index + match[0].length;
  }
  out.push(text.slice(start));
  return out;
}

function PublicDataLimits() {
  return <section className="wb-card wb-limits">
    {limits.trim().split(/\r?\n\s*\r?\n/).map((block, key) => {
      if (block.startsWith("# ")) return <h2 key={key}>{block.slice(2)}</h2>;
      if (!block.startsWith("|")) return <p key={key}>{inlineMarkdown(block)}</p>;
      const [header, , ...body] = block.split(/\r?\n/).map(line => line.split("|").slice(1, -1).map(cell => cell.trim()));
      return <div className="wb-table-scroll" key={key}><table className="wb-table">
        <thead><tr>{header.map((cell, i) => <th scope="col" key={i}>{inlineMarkdown(cell)}</th>)}</tr></thead>
        <tbody>{body.map((row, i) => <tr key={i}>{row.map((cell, j) => j === 0
          ? <th scope="row" key={j}>{inlineMarkdown(cell)}</th> : <td key={j}>{inlineMarkdown(cell)}</td>)}</tr>)}</tbody>
      </table></div>;
    })}
  </section>;
}

export function Outlook({gates, error}: {gates: WorkbenchGates | null; error: string}) {
  return <>
    <section className="wb-card">
      <h2>Outcome rates locked</h2>
      <p>Release requires cohort coverage for the selected endpoint and successful validation on later entry vintages.</p>
      {gates ? <GateProgress gates={gates}/> : <Status error={Boolean(error)}>{error || "Loading cohort audit…"}</Status>}
    </section>
    <PublicDataLimits/>
  </>;
}
