const QUALITY = new Set(['high', 'balanced', 'power-save']);

export function normalizeQuality(value) {
  return QUALITY.has(value) ? value : 'balanced';
}

export function qualityBudget(value, {width = 1920, height = 1080, devicePixelRatio = 1} = {}) {
  const quality = normalizeQuality(value);
  const base = {
    high:{maxFps:60,maxInsects:8,maxBirds:2,maxLeaves:24,maxRain:80,waterStrength:1},
    balanced:{maxFps:45,maxInsects:5,maxBirds:1,maxLeaves:12,maxRain:40,waterStrength:.8},
    'power-save':{maxFps:30,maxInsects:2,maxBirds:0,maxLeaves:6,maxRain:16,waterStrength:.55},
  }[quality];
  const pixels = Math.max(1, width * height * Math.max(1, devicePixelRatio ** 2));
  const scale = Math.min(1, Math.sqrt(2073600 / pixels));
  return {
    ...base,
    maxInsects:Math.max(1, Math.floor(base.maxInsects * scale)),
    maxBirds:Math.floor(base.maxBirds * scale),
    maxLeaves:Math.max(2, Math.floor(base.maxLeaves * scale)),
    maxRain:Math.max(8, Math.floor(base.maxRain * scale)),
    waterStrength:base.waterStrength * (.82 + scale * .18),
  };
}
