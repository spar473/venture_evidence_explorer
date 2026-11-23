import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { scoreScenario } from "../src/analytics-views/scorer.ts";

for (const id of ["public_supie", "public_partly", "discovery_halter"]) {
  test(`${id} offline scorer matches every Python preset to six places`, () => {
    const profile = JSON.parse(
      readFileSync(new URL(`../public/analytics-data/views/profile/${id}.json`, import.meta.url)),
    );
    for (const { result } of profile.presets) {
      const scored = scoreScenario(profile, result.overrides);
      assert.equal(scored.qualifying_count, result.qualifying_count);
      assert.deepEqual(scored.roles, result.roles);
      assert.deepEqual(scored.changed_roles, result.changed_roles);
      for (const peer of scored.peers) {
        const expected = result.peers.find(({ company_id }) => company_id === peer.company_id);
        assert.equal(peer.qualifies, expected.qualifies);
        assert.deepEqual(peer.failed_bars, expected.failed_bars);
        for (const key of ["similarity", "coverage", "product_customer"])
          assert.equal(
            peer[key]?.toFixed(6),
            expected[key]?.toFixed(6),
            `${id} ${peer.company_id} ${key}`,
          );
        for (const [key, score] of Object.entries(peer.field_scores))
          assert.equal(score.toFixed(6), expected.field_scores[key].toFixed(6));
      }
    }
  });
}
