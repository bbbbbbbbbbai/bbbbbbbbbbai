import test from 'node:test';
import assert from 'node:assert/strict';
import {
  atmosphereFor,
  defaultAtmosphere,
  normalizeAtmosphere,
  resolveWeatherKind,
} from '../src/atmosphere.js';

test('old environment records gain safe atmosphere defaults', () => {
  const value = normalizeAtmosphere({timeMode:'manual', manualTime:'night'}, defaultAtmosphere());
  assert.equal(value.weatherMode, 'local');
  assert.equal(value.weatherKind, 'clear');
  assert.equal(value.season, 'summer');
  assert.equal(value.quality, 'high');
});

test('legacy atmosphere quality no longer lowers motion on its own', () => {
  const legacy = atmosphereFor({
    weatherKind:'clear',
    quietMode:false,
    reducedMotion:false,
    quality:'power-save',
  });
  const full = atmosphereFor({
    weatherKind:'clear',
    quietMode:false,
    reducedMotion:false,
    quality:'high',
  });
  assert.equal(legacy.motionScale, full.motionScale);
  assert.equal(legacy.waterStrength, full.waterStrength);
  assert.equal(legacy.birdRate, 1);
  assert.equal(normalizeAtmosphere({quality:'power-save'}, {quality:'balanced'}).quality, 'high');
});

test('quiet and reduced motion remain stronger than full visual defaults', () => {
  const quiet = atmosphereFor({quietMode:true, season:'autumn'});
  const reduced = atmosphereFor({reducedMotion:true, season:'autumn'});
  const both = atmosphereFor({quietMode:true, reducedMotion:true, season:'autumn'});
  assert.equal(quiet.motionScale, .55);
  assert.equal(reduced.motionScale, .35);
  assert.equal(both.motionScale, .35);
  for (const value of [quiet, reduced, both]) {
    assert.ok(value.waterStrength < 1);
    assert.equal(value.birdRate, 0);
    assert.equal(value.leafRate, 0);
  }
});

test('rain and night reduce light but preserve readable motion', () => {
  const clear = atmosphereFor({
    period:'day',
    weatherKind:'clear',
    season:'summer',
    quietMode:false,
    reducedMotion:false,
    quality:'high',
  });
  const rainNight = atmosphereFor({
    period:'night',
    weatherKind:'rain',
    season:'winter',
    quietMode:false,
    reducedMotion:false,
    quality:'high',
  });
  assert.ok(rainNight.light[0] < clear.light[0]);
  assert.ok(rainNight.rainIntensity > 0);
  assert.ok(rainNight.motionScale > 0);
});

test('manual weather overrides local weather while local mode follows the fetched kind', () => {
  assert.equal(
    resolveWeatherKind({weatherMode:'manual', weatherKind:'rain'}, {kind:'clear'}),
    'rain',
  );
  assert.equal(
    resolveWeatherKind({weatherMode:'local', weatherKind:'rain'}, {kind:'cloud'}),
    'cloud',
  );
});
