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
  assert.equal(value.quality, 'balanced');
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
