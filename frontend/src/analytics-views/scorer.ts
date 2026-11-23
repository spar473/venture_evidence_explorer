import type { Peer, Profile, RoleMap, Scenario, Scorer, Snapshot, Value } from "./data";

function tokenize(value: Value | undefined, model: Scorer) {
  const stops = new Set(model.stop);
  return new Set(
    (
      String(value ?? "")
        .toLowerCase()
        .match(/[a-z0-9]+/g) ?? []
    )
      .map((word) => model.inflections[word] ?? word)
      .filter((word) => word.length > 2 && !stops.has(word)),
  );
}

function describe(model: Scorer, subject: Snapshot, minFields: number) {
  const corpus = [
    subject,
    ...Object.values(model.peers)
      .map(({ values }) => values)
      .filter((values) => Object.keys(values).length >= minFields),
  ]
    .filter((values) => values.description)
    .map((values) => tokenize(values.description, model));
  const frequency = new Map<string, number>();
  for (const doc of corpus)
    for (const token of doc) frequency.set(token, (frequency.get(token) ?? 0) + 1);
  return (a: Value, b: Value) => {
    const left = tokenize(a, model);
    const right = tokenize(b, model);
    let total = 0;
    let overlap = 0;
    for (const token of [...new Set([...left, ...right])].sort()) {
      const mass = 1 + Math.log((corpus.length + 1) / ((frequency.get(token) ?? 0) + 1));
      total += mass;
      if (left.has(token) && right.has(token)) overlap += mass;
    }
    return total ? overlap / total : undefined;
  };
}

function compareField(model: Scorer, field: string, left: Value, right: Value) {
  const vocab = model.vocabulary[field];
  if (vocab) {
    const a = String(left);
    const b = String(right);
    if (!Object.hasOwn(vocab.nodes, a) || !Object.hasOwn(vocab.nodes, b)) return undefined;
    if (a === b) return 1;
    const parentA = vocab.nodes[a];
    const parentB = vocab.nodes[b];
    return !vocab.flat &&
      (parentA === b || parentB === a || (parentA !== null && parentA === parentB))
      ? 0.5
      : 0;
  }
  if (field === "months_since_founding")
    return Math.max(0, 1 - Math.abs(Number(left) - Number(right)) / 120);
  if (field === "round_size_band")
    return 1 - Math.abs(model.bands.indexOf(String(left)) - model.bands.indexOf(String(right))) / 4;
  return Number(left === right);
}

function computeRoles(peers: Peer[], model: Scorer, thresholds: Scenario["thresholds"]): RoleMap {
  const qualifying = peers.filter((peer) => peer.qualifies);
  if (qualifying.length < thresholds.peers) return {};
  const byScore = (peer: Peer) => Math.round((peer.similarity ?? 0) * 1e12);
  const ranked = qualifying.sort(
    (a, b) =>
      (b.similarity ?? 0) - (a.similarity ?? 0) || a.company_id.localeCompare(b.company_id, "en"),
  );
  const pool = ranked
    .slice(0, thresholds.top_k)
    .filter((peer) => model.peers[peer.company_id].rank != null);
  if (!pool.length) return {};
  const rank = (peer: Peer) => model.peers[peer.company_id].rank!;
  const ranks = pool.map(rank).sort((a, b) => a - b);
  const sortedIds = (group: Peer[]) => group.map((peer) => peer.company_id).sort();
  const best = (group: Peer[]) => group.filter((peer) => byScore(peer) === byScore(group[0]));
  const low = ranks[0];
  const high = ranks[ranks.length - 1];
  if (low === high) return { representative: sortedIds(best(pool)) };
  const ceiling = best(pool.filter((peer) => rank(peer) === high));
  const floor = best(pool.filter((peer) => rank(peer) === low));
  const median = ranks[Math.floor((ranks.length - 1) / 2)];
  const typical = new Set<string>();
  for (const hi of ceiling) {
    for (const lo of floor) {
      const remaining = pool.filter((peer) => peer !== hi && peer !== lo);
      if (!remaining.length) continue;
      const distance = Math.min(...remaining.map((peer) => Math.abs(rank(peer) - median)));
      for (const peer of best(
        remaining.filter((peer) => Math.abs(rank(peer) - median) === distance),
      ))
        typical.add(peer.company_id);
    }
  }
  return {
    ceiling: sortedIds(ceiling),
    floor: sortedIds(floor),
    ...(typical.size ? { typical: [...typical].sort() } : {}),
  };
}

export function scoreScenario(profile: Profile, overrides: Snapshot): Scenario {
  const model = profile.scorer;
  const { thresholds } = profile.recorded;
  const subject = { ...model.subject, ...overrides };
  const description = describe(model, subject, thresholds.fields);
  const peers = Object.entries(model.peers).map(([id, { values }]): Peer => {
    const fieldScores: Record<string, number> = {};
    let weighted = 0;
    let active = 0;
    let coverage = 0;
    const dimensions = model.dimensions.map(({ name, weight, fields }) => {
      const comparable = fields.flatMap((field) => {
        if (!Object.hasOwn(subject, field) || !Object.hasOwn(values, field)) return [];
        const a = subject[field];
        const b = values[field];
        const value =
          field === "description" ? description(a, b) : compareField(model, field, a, b);
        if (value === undefined) return [];
        fieldScores[field] = value;
        return [{ field, value }];
      });
      const observed = comparable.length / fields.length;
      coverage += weight * observed;
      const similarity = comparable.length
        ? comparable.reduce((sum, item) => sum + item.value, 0) / comparable.length
        : null;
      if (similarity != null) {
        weighted += weight * similarity;
        active += weight;
      }
      return {
        dimension: name,
        similarity,
        coverage: observed,
        matched_fields: comparable.filter((item) => item.value > 0).map((item) => item.field),
        different_fields: comparable.filter((item) => item.value < 1).map((item) => item.field),
      };
    });
    const similarity = active ? weighted / active : null;
    const product = dimensions[0].similarity;
    const failed =
      similarity === null
        ? ["no_shared_evidence"]
        : [
            ...(similarity < thresholds.similarity ? ["similarity"] : []),
            ...(coverage < thresholds.coverage ? ["coverage"] : []),
            ...((product ?? 0) < thresholds.product_customer ? ["product_customer"] : []),
            ...(Object.keys(subject).length < thresholds.fields ? ["subject_fields"] : []),
            ...(Object.keys(values).length < thresholds.fields ? ["peer_fields"] : []),
          ];
    return {
      company_id: id,
      similarity,
      coverage,
      product_customer: product,
      shared_fields: Object.keys(fieldScores).length,
      field_scores: fieldScores,
      dimensions: active ? dimensions : [],
      qualifies: !failed.length,
      failed_bars: failed,
    };
  });
  const roles = computeRoles(peers, model, thresholds);
  const recorded = profile.recorded.roles;
  const changed = [...new Set([...Object.keys(roles), ...Object.keys(recorded)])]
    .sort()
    .filter((role) => JSON.stringify(roles[role] ?? []) !== JSON.stringify(recorded[role] ?? []));
  return {
    ...profile.recorded,
    scenario: true,
    overrides,
    peers,
    roles,
    qualifying_count: peers.filter((peer) => peer.qualifies).length,
    changed_roles: Object.fromEntries(
      changed.map((role) => [
        role,
        { recorded: recorded[role] ?? [], scenario: roles[role] ?? [] },
      ]),
    ),
  };
}
