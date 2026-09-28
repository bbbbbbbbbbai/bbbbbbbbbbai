import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeQuality, qualityBudget } from '../src/performance.js';
import { EcosystemController } from '../src/ecosystem.js';

test('default budget uses full effects without changing fish settings', () => {
  assert.deepEqual(qualityBudget(), {
    maxFps:60,maxInsects:8,maxBirds:2,maxLeaves:24,maxRain:80,waterStrength:1,
  });
});

test('all legacy quality inputs now resolve to the full visual budget', () => {
  for (const value of ['balanced', 'power-save', 'high', 'unknown', null, undefined]) {
    assert.equal(normalizeQuality(value), 'high');
    assert.deepEqual(
      qualityBudget(value, {width:1920, height:1080, devicePixelRatio:1}),
      {maxFps:60,maxInsects:8,maxBirds:2,maxLeaves:24,maxRain:80,waterStrength:1},
    );
  }
});

test('large viewports keep the same full effect budget as the default', () => {
  for (const devicePixelRatio of [1, 2, 3]) {
    const budget = qualityBudget('power-save', {width:3840, height:2160, devicePixelRatio});
    assert.deepEqual(budget, qualityBudget());
    assert.deepEqual(budget, {
      maxFps:60,maxInsects:8,maxBirds:2,maxLeaves:24,maxRain:80,waterStrength:1,
    });
  }
});

test('ecosystem event arrays remain finite and bounded during a long run', () => {
  const controller = new EcosystemController({random:Math.random, width:1920, height:1080});
  controller.setEnvironment({
    period:'autumn',
    weatherKind:'rain',
    season:'autumn',
    quietMode:false,
    reducedMotion:false,
    quality:'high',
  });
  for (let i = 0; i < 3600; i++) controller.update(1 / 60, {fish:[]});
  const snapshot = controller.getSnapshot();
  assert.ok(snapshot.insects.length <= 8);
  assert.ok(snapshot.birds.length <= 2);
  assert.ok(snapshot.leaves.length <= 24);
  assert.ok(snapshot.rain.length <= 80);
  for (const list of Object.values(snapshot)) {
    for (const item of list) {
      for (const key of ['x','y','phase','life']) {
        if (key in item) assert.ok(Number.isFinite(item[key]));
      }
    }
  }
});
