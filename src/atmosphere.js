import { lightForPeriod } from './art.js';

const TIMES = new Set(['dawn', 'day', 'dusk', 'night']);
const TIME_MODES = new Set(['auto', 'manual']);
const WEATHER_MODES = new Set(['local', 'manual', 'off']);
const WEATHER = new Set(['clear', 'cloud', 'rain', 'fog', 'snow', 'storm']);
const SEASONS = new Set(['spring', 'summer', 'autumn', 'winter']);
const QUALITY = new Set(['high', 'balanced', 'power-save']);

export function defaultAtmosphere() {
  return {
    timeMode:'auto',
    manualTime:'day',
    weatherMode:'local',
    weatherKind:'clear',
    season:'summer',
    quietMode:false,
    quality:'balanced',
  };
}

export function normalizeAtmosphere(value, fallback = defaultAtmosphere()) {
  const base = {...defaultAtmosphere(), ...(fallback && typeof fallback === 'object' ? fallback : {})};
  const input = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
  return {
    timeMode: TIME_MODES.has(input.timeMode) ? input.timeMode : base.timeMode,
    manualTime: TIMES.has(input.manualTime) ? input.manualTime : base.manualTime,
    weatherMode: WEATHER_MODES.has(input.weatherMode) ? input.weatherMode : base.weatherMode,
    weatherKind: WEATHER.has(input.weatherKind) ? input.weatherKind : base.weatherKind,
    season: SEASONS.has(input.season) ? input.season : base.season,
    quietMode: typeof input.quietMode === 'boolean' ? input.quietMode : Boolean(base.quietMode),
    quality: QUALITY.has(input.quality) ? input.quality : base.quality,
  };
}

export function resolveWeatherKind(environment = {}, weather = {}) {
  return environment.weatherMode === 'manual'
    ? (WEATHER.has(environment.weatherKind) ? environment.weatherKind : 'clear')
    : (WEATHER.has(weather.kind) ? weather.kind : 'clear');
}

export function atmosphereFor({
  period = 'day',
  weatherKind = 'clear',
  season = 'summer',
  quietMode = false,
  reducedMotion = false,
  quality = 'balanced',
} = {}) {
  const light = lightForPeriod(TIMES.has(period) ? period : 'day');
  const weather = WEATHER.has(weatherKind) ? weatherKind : 'clear';
  const seasonMix = {
    spring:[1.02, 1.03, .98],
    summer:[1.03, 1.02, .94],
    autumn:[1.04, .98, .86],
    winter:[.88, .95, 1.06],
  }[SEASONS.has(season) ? season : 'summer'];
  const weatherMix = {
    clear:[1, 1, 1],
    cloud:[.9, .94, .95],
    rain:[.78, .86, .9],
    fog:[.86, .91, .93],
    snow:[.88, .94, 1.02],
    storm:[.68, .77, .84],
  }[weather];
  const motionScale = reducedMotion ? .35 : quietMode ? .55 : quality === 'power-save' ? .62 : quality === 'balanced' ? .82 : 1;
  const lightOut = light.map((value, index) => Math.max(.35, Math.min(1.2, value * seasonMix[index] * weatherMix[index])));
  const effect = {
    clear:{cloud:.025, fog:0, rain:0, snow:0},
    cloud:{cloud:.2, fog:0, rain:0, snow:0},
    rain:{cloud:.26, fog:.02, rain:.72, snow:0},
    fog:{cloud:.12, fog:.2, rain:0, snow:0},
    snow:{cloud:.16, fog:.04, rain:0, snow:.5},
    storm:{cloud:.4, fog:.05, rain:1, snow:0},
  }[weather];
  return {
    light:lightOut,
    waterStrength:Math.max(.15, Math.min(1, (weather === 'storm' ? .55 : 1) * motionScale)),
    cloud:effect.cloud,
    fog:effect.fog,
    rainIntensity:effect.rain,
    snowIntensity:effect.snow,
    insectRate:period === 'night' ? .5 : season === 'winter' ? .35 : .9,
    birdRate:quietMode || reducedMotion || quality === 'power-save' ? 0 : 1,
    leafRate:quietMode || reducedMotion ? 0 : season === 'autumn' ? .8 : .12,
    rippleRate:Math.max(.2, motionScale * (weather === 'rain' || weather === 'storm' ? 1.4 : 1)),
    motionScale,
  };
}
