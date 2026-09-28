import test from 'node:test';
import assert from 'node:assert/strict';
import { EcosystemController } from '../src/ecosystem.js';

function random(seed = 12345) {
  return () => {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    return seed / 4294967296;
  };
}

function environment(overrides = {}) {
  return {
    period:'day',
    weatherKind:'clear',
    season:'summer',
    quietMode:false,
    reducedMotion:false,
    quality:'high',
    ...overrides,
  };
}

test('turtles periodically surface without changing their identity', () => {
  const controller = new EcosystemController({random: random(), width:1000, height:700});
  const first = controller.getSnapshot().turtles.map((turtle) => turtle.id);
  controller.setEnvironment(environment());
  for (let i = 0; i < 900; i++) controller.update(1 / 60, {fish:[]});
  const snapshot = controller.getSnapshot();
  assert.deepEqual(snapshot.turtles.map((turtle) => turtle.id), first);
  assert.ok(snapshot.turtles.some((turtle) => turtle.surfacing));
});

test('night uses fireflies and no daytime insects', () => {
  const controller = new EcosystemController({random: random(), width:1000, height:700});
  controller.setEnvironment(environment({period:'night'}));
  for (let i = 0; i < 300; i++) controller.update(1 / 60, {fish:[]});
  assert.ok(controller.getSnapshot().insects.every((insect) => insect.kind === 'firefly'));
});

test('quiet mode keeps event counts bounded and suppresses birds', () => {
  const controller = new EcosystemController({random:random(), width:1000, height:700});
  controller.setEnvironment(environment({weatherKind:'rain', season:'autumn', quietMode:true}));
  for (let i = 0; i < 3600; i++) controller.update(1 / 60, {fish:[]});
  const snapshot = controller.getSnapshot();
  assert.equal(snapshot.birds.length, 0);
  assert.ok(snapshot.insects.length <= 2);
  assert.ok(snapshot.leaves.length <= 8);
  assert.ok(snapshot.rain.length <= 24);
});
