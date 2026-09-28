import test from 'node:test';
import assert from 'node:assert/strict';
import { qualityBudget } from '../src/performance.js';
import { EcosystemController } from '../src/ecosystem.js';

test('power save reduces dynamic budgets without changing fish count', () => {
  const high = qualityBudget('high', {width:1920, height:1080, devicePixelRatio:1});
  const power = qualityBudget('power-save', {width:1920, height:1080, devicePixelRatio:1});
  assert.ok(power.maxFps < high.maxFps);
  assert.ok(power.maxInsects < high.maxInsects);
  assert.ok(power.waterStrength < high.waterStrength);
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
