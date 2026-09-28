import test from 'node:test';
import assert from 'node:assert/strict';
import { PondWorld } from '../src/world.js';
import { ART, FISH_SPECIES } from '../src/art.js';
import { getFishProfile } from '../src/species.js';

const advance = (pond, seconds, dt = 1 / 60) => {
  for (let i = 0; i < Math.round(seconds / dt); i++) pond.update(dt);
};

function isolatedWorld(value = .5) {
  const pond = new PondWorld(1920, 1080, { count: 8, random: () => value });
  pond.fish.slice(1).forEach((fish, index) => {
    Object.assign(fish, { x: 100 + index * 240, y: 950, angle: 0 });
  });
  Object.assign(pond.fish[0], { x: 700, y: 400, angle: 0 });
  return pond;
}

test('spawn depth is bounded and varies by identity without consuming random draws', () => {
  let calls = 0;
  const pond = new PondWorld(1920, 1080, {
    count: 8,
    random: () => { calls++; return .5; },
  });
  assert.equal(calls, 267, 'retain the existing spawn random stream');
  assert.ok(pond.fish.every(fish => Number.isFinite(fish.depth) && fish.depth >= 0 && fish.depth <= 1));
  assert.ok(new Set(pond.fish.map(fish => fish.depth)).size > 4);
  const other = new PondWorld(1920, 1080, { count: 8, random: () => .8 });
  assert.deepEqual(pond.fish.map(fish => fish.depth), other.fish.map(fish => fish.depth));
});

test('cruising depth evolves smoothly and persists across resize and population edits', () => {
  const pond = isolatedWorld();
  const fish = pond.fish[0];
  const initialDepth = fish.depth;
  let changed = false;
  for (let i = 0; i < 600; i++) {
    const previous = fish.depth;
    pond.update(1 / 60);
    assert.ok(fish.depth >= 0 && fish.depth <= 1);
    assert.ok(Math.abs(fish.depth - previous) <= .35 / 60 + 1e-9);
    changed ||= Math.abs(fish.depth - initialDepth) > .01;
  }
  assert.ok(changed, 'depth is simulated rather than fixed render metadata');
  const before = pond.fish.map(fish => fish.depth);
  pond.resize(960, 540);
  pond.setCount(12);
  assert.deepEqual(pond.fish.slice(0, 8).map(fish => fish.depth), before);
});

test('food attraction smoothly lifts deep fish and they descend again after feeding', () => {
  for (const dt of [1 / 120, 1 / 60, 1 / 30, .05]) {
    const pond = isolatedWorld();
    const fish = pond.fish[0];
    fish.depth = .85;
    pond.food.push({ id: 'meal', x: 900, y: 400, age: 0 });
    for (let i = 0; i < Math.round(2 / dt); i++) {
      const previous = fish.depth;
      pond.update(dt);
      assert.equal(fish.behaviorState, 'seek-food');
      assert.ok(fish.depth < previous, 'zero denotes the surface');
      assert.ok(previous - fish.depth <= .35 * dt + 1e-9);
    }
    assert.ok(fish.depth < .5, 'a deep fish makes visible progress toward the surface');
    for(let i=0;i<Math.round(5/dt)&&pond.food.length;i++)pond.update(dt);
    assert.equal(pond.food.length, 0, 'the target is eaten before expiry');
    const surfacedDepth = fish.depth;
    advance(pond, 3, dt);
    assert.ok(fish.depth > surfacedDepth + .03, 'return toward cruising depth');
  }
});

test('depth layers affect actual crossing trajectories without affecting the wander random stream', () => {
  const worlds = [];
  for (const depth of [.5, .52, .9]) {
    let calls = 0;
    const pond = new PondWorld(1920, 1080, {
      count: 8,
      random: () => { calls++; return .5; },
    });
    pond.fish.slice(2).forEach((fish, index) => {
      Object.assign(fish, { x: 100 + index * 240, y: 950, angle: 0 });
    });
    Object.assign(pond.fish[0], { x: 700, y: 400, angle: 0, depth: .5 });
    Object.assign(pond.fish[1], {
      x: depth === .5 ? 1500 : 700,
      y: depth === .5 ? 800 : 402,
      angle: 0,
      depth,
    });
    pond.update(1 / 60);
    worlds.push({ fish: pond.fish[0], calls });
  }
  const [alone, near, deep] = worlds;
  assert.equal(alone.calls, near.calls);
  assert.equal(alone.calls, deep.calls);
  assert.equal(deep.fish.angle, alone.fish.angle, 'deep neighbors do not deflect this fish');
  assert.notEqual(near.fish.angle, alone.fish.angle, 'same-layer neighbors gently deflect this fish');
  assert.ok(Math.abs(near.fish.angle - alone.fish.angle) < .08);
});

test('each visual species spawns with its own ecological profile, including shiro and new species', () => {
  const expected = [
    ['kohaku', 'koi'], ['ogon', 'koi'], ['showa', 'koi'], ['shiro', 'koi'],
    ['goldfish', 'goldfish'], ['carp', 'carp'], ['grass-carp', 'grass-carp'], ['loach', 'loach'],
  ];
  for (const [id, profileId] of expected) {
    const index = FISH_SPECIES.findIndex(species => species.id === id);
    assert.ok(index >= 0, `${id} is available for spawning`);
    const pond = isolatedWorld((index + .5) / FISH_SPECIES.length);
    for (const fish of pond.fish) {
      assert.equal(FISH_SPECIES[fish.variant].id, id);
      assert.equal(fish.profileId, profileId, id);
      assert.equal(fish.profile, getFishProfile(profileId));
      assert.equal(pond._agents.get(fish.id).profile, getFishProfile(profileId));
    }
    pond.setArtworks([{ id: 'drawing' }]);
    assert.equal(pond.fish.at(-1).profileId, 'custom');
  }
});

test('new ecological species and events use paired generated ecology PNG assets', () => {
  for (const [key, id] of [
    ['egret', 'egret'], ['swallow', 'swallow'], ['butterfly', 'butterfly'],
    ['dragonfly', 'dragonfly'], ['fallingLeaf', 'falling-leaf'],
  ]) {
    assert.equal(ART[key], `/assets/ecology/${id}.png`);
    assert.equal(ART[`${key}Shadow`], `/assets/ecology/${id}-shadow.png`);
  }
  for (const id of ['grass-carp', 'loach']) {
    const species = FISH_SPECIES.find(species => species.id === id);
    assert.equal(species?.texture, `/assets/ecology/${id}.png`);
    assert.equal(species?.shadow, `/assets/ecology/${id}-shadow.png`);
  }
});
