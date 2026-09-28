import assert from 'node:assert/strict';
import test from 'node:test';
import {
  createDefaultEnvironment,
  createEnvironmentRepository,
  getTimePeriod,
  normalizeEnvironment,
} from '../src/environment.js';
import { weatherToAtmosphere } from '../src/weather.js';

function memoryStorage(initial = null) {
  let value = initial;
  return {
    getItem() { return value; },
    setItem(key, next) { value = next; },
    removeItem() { value = null; },
  };
}

test('environment defaults to local weather and automatic time', () => {
  assert.deepEqual(createDefaultEnvironment(), {
    version: 1,
    timeMode: 'auto',
    manualTime: 'day',
    weatherMode: 'local',
  });
});

test('automatic time maps local hours to four visual periods', () => {
  assert.equal(getTimePeriod(new Date(2026, 8, 27, 6)), 'dawn');
  assert.equal(getTimePeriod(new Date(2026, 8, 27, 12)), 'day');
  assert.equal(getTimePeriod(new Date(2026, 8, 27, 18)), 'dusk');
  assert.equal(getTimePeriod(new Date(2026, 8, 27, 23)), 'night');
});

test('environment normalizes unsupported values back to safe defaults', () => {
  assert.deepEqual(normalizeEnvironment({
    version: 99,
    timeMode: 'broken',
    manualTime: 'broken',
    weatherMode: 'broken',
  }), createDefaultEnvironment());
});

test('environment preferences persist independently from pond artwork data', () => {
  const storage = memoryStorage();
  const repository = createEnvironmentRepository(storage);
  const value = { version: 1, timeMode: 'manual', manualTime: 'dusk', weatherMode: 'local' };
  assert.deepEqual(repository.save(value), { ok: true, data: value });
  assert.deepEqual(repository.load(), { ok: true, data: value });
});

test('weather codes map to calm visual atmosphere categories', () => {
  assert.equal(weatherToAtmosphere(0).kind, 'clear');
  assert.equal(weatherToAtmosphere(3).kind, 'cloud');
  assert.equal(weatherToAtmosphere(63).kind, 'rain');
  assert.equal(weatherToAtmosphere(95).kind, 'storm');
  assert.equal(weatherToAtmosphere(71).kind, 'snow');
  assert.equal(weatherToAtmosphere(45).kind, 'fog');
  assert.equal(weatherToAtmosphere(999).kind, 'clear');
});
