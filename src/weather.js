const WEATHER_LABELS = {
  clear: '晴',
  cloud: '多云',
  rain: '有雨',
  storm: '雷雨',
  snow: '降雪',
  fog: '雾',
};

export function weatherToAtmosphere(code) {
  if (code >= 95 && code <= 99) return { kind: 'storm', label: WEATHER_LABELS.storm };
  if (code >= 71 && code <= 86) return { kind: 'snow', label: WEATHER_LABELS.snow };
  if (code >= 51 && code <= 67) return { kind: 'rain', label: WEATHER_LABELS.rain };
  if (code >= 45 && code <= 48) return { kind: 'fog', label: WEATHER_LABELS.fog };
  if (code >= 1 && code <= 3) return { kind: 'cloud', label: WEATHER_LABELS.cloud };
  return { kind: 'clear', label: WEATHER_LABELS.clear };
}

function getPosition(geolocation) {
  return new Promise((resolve, reject) => {
    if (!geolocation?.getCurrentPosition) {
      reject(new Error('当前浏览器不支持定位。'));
      return;
    }
    geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: false,
      maximumAge: 15 * 60 * 1000,
      timeout: 8000,
    });
  });
}

export async function fetchLocalWeather({
  geolocation = globalThis.navigator?.geolocation,
  fetchImpl = globalThis.fetch,
} = {}) {
  const position = await getPosition(geolocation);
  const latitude = Number(position.coords.latitude);
  const longitude = Number(position.coords.longitude);
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) throw new Error('定位坐标无效。');
  const url = new URL('https://api.open-meteo.com/v1/forecast');
  url.search = new URLSearchParams({
    latitude: String(latitude),
    longitude: String(longitude),
    current: 'temperature_2m,weather_code',
    timezone: 'auto',
  });
  const response = await fetchImpl(url);
  if (!response.ok) throw new Error(`天气请求失败：${response.status}`);
  const payload = await response.json();
  const code = Number(payload?.current?.weather_code);
  const atmosphere = weatherToAtmosphere(Number.isFinite(code) ? code : 0);
  return {
    ...atmosphere,
    code: Number.isFinite(code) ? code : 0,
    temperature: Number(payload?.current?.temperature_2m),
    latitude,
    longitude,
    updatedAt: Date.now(),
  };
}
