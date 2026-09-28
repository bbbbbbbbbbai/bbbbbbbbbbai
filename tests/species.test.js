import test from 'node:test';
import assert from 'node:assert/strict';
import { FISH_PROFILES, getFishProfile } from '../src/species.js';

test('fish profiles expose five distinct ecological roles', () => {
  assert.deepEqual(
    FISH_PROFILES.slice(0, 5).map((profile) => profile.id),
    ['koi', 'carp', 'goldfish', 'grass-carp', 'loach'],
  );
  assert.ok(new Set(FISH_PROFILES.map((profile) => profile.speed)).size >= 3);
  assert.ok(new Set(FISH_PROFILES.map((profile) => profile.foodInterest)).size >= 3);
});

test('unknown fish profile falls back to koi', () => {
  assert.equal(getFishProfile('missing').id, 'koi');
  assert.equal(getFishProfile(999).id, 'koi');
});
