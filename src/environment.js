const TIME_PERIODS = new Set(['dawn', 'day', 'dusk', 'night']);
const TIME_MODES = new Set(['auto', 'manual']);
const WEATHER_MODES = new Set(['local', 'manual', 'off']);
const ATMOSPHERE_FIELDS = ['weatherKind', 'season', 'quietMode', 'quality'];

export function createDefaultEnvironment() {
  return {
    version: 1,
    timeMode: 'auto',
    manualTime: 'day',
    weatherMode: 'local',
  };
}

export function normalizeEnvironment(value) {
  const fallback = createDefaultEnvironment();
  if (!value || typeof value !== 'object' || Array.isArray(value)) return fallback;
  const base = {
    version: 1,
    timeMode: TIME_MODES.has(value.timeMode) ? value.timeMode : fallback.timeMode,
    manualTime: TIME_PERIODS.has(value.manualTime) ? value.manualTime : fallback.manualTime,
    weatherMode: WEATHER_MODES.has(value.weatherMode) ? value.weatherMode : fallback.weatherMode,
  };
  if (!ATMOSPHERE_FIELDS.some((key) => Object.hasOwn(value, key))) return base;
  return {
    ...base,
    weatherKind: typeof value.weatherKind === 'string' ? value.weatherKind : 'clear',
    season: typeof value.season === 'string' ? value.season : 'summer',
    quietMode: Boolean(value.quietMode),
    quality: value.quality === 'high' || value.quality === 'power-save' ? value.quality : 'balanced',
  };
}

export function getTimePeriod(date = new Date()) {
  const hour = date.getHours() + date.getMinutes() / 60;
  if (hour >= 5 && hour < 8) return 'dawn';
  if (hour >= 8 && hour < 17) return 'day';
  if (hour >= 17 && hour < 20) return 'dusk';
  return 'night';
}

export function createEnvironmentRepository(storage, key = 'chijian.environment.v1') {
  return {
    load() {
      try {
        const raw = storage?.getItem?.(key);
        if (!raw) return { ok: true, data: createDefaultEnvironment() };
        return { ok: true, data: normalizeEnvironment(JSON.parse(raw)) };
      } catch {
        return { ok: false, error: '环境设置读取失败，已使用默认环境。' };
      }
    },
    save(value) {
      const data = normalizeEnvironment(value);
      try {
        storage?.setItem?.(key, JSON.stringify(data));
        return { ok: true, data };
      } catch {
        return { ok: false, error: '环境设置保存失败，本次设置仅在当前页面生效。' };
      }
    },
  };
}
