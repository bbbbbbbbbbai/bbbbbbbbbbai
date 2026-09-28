const MAX_BYTES = 3 * 1024 * 1024;
const MAX_STROKES = 400;
const encoder = new TextEncoder();

function requireValid(condition, message) {
  if (!condition) throw new Error(message);
}

function record(value, keys, label) {
  requireValid(
    value !== null && typeof value === 'object' && !Array.isArray(value),
    `${label}必须是对象。`,
  );
  const prototype = Object.getPrototypeOf(value);
  requireValid(
    prototype === Object.prototype || prototype === null,
    `${label}包含不支持的对象类型。`,
  );
  requireValid(Reflect.ownKeys(value).length === keys.length, `${label}字段不完整或含有未知字段。`);
  for (const key of keys) {
    const descriptor = Object.getOwnPropertyDescriptor(value, key);
    requireValid(descriptor && Object.hasOwn(descriptor, 'value'), `${label}的 ${key} 字段无效。`);
  }
}

function number(value, min, max, label) {
  requireValid(
    typeof value === 'number' && Number.isFinite(value) && value >= min && value <= max,
    `${label}必须是 ${min} 到 ${max} 之间的有限数值。`,
  );
  return value;
}

function text(value, max, label, min = 0) {
  requireValid(
    typeof value === 'string' && value.length >= min && value.length <= max,
    `${label}必须是长度 ${min} 到 ${max} 的字符串。`,
  );
  return value;
}

function list(value, max, label, min = 0) {
  requireValid(Array.isArray(value), `${label}必须是数组。`);
  requireValid(Object.getPrototypeOf(value) === Array.prototype, `${label}必须是普通数组。`);
  requireValid(value.length >= min && value.length <= max, `${label}数量必须在 ${min} 到 ${max} 之间。`);
  // Only dense, ordinary array entries are accepted; accessors and JSON hooks cannot rewrite a save.
  requireValid(Reflect.ownKeys(value).length === value.length + 1, `${label}包含空项或未知字段。`);
  for (let index = 0; index < value.length; index += 1) {
    const descriptor = Object.getOwnPropertyDescriptor(value, String(index));
    requireValid(descriptor && Object.hasOwn(descriptor, 'value'), `${label}包含无效项。`);
  }
}

function copyPoint(value, label) {
  record(value, ['x', 'y'], label);
  return {
    x: number(value.x, 0, 1, `${label}横坐标`),
    y: number(value.y, 0, 1, `${label}纵坐标`),
  };
}

function copyStroke(value) {
  record(value, ['mode', 'color', 'width', 'points'], '笔画');
  requireValid(value.mode === 'draw' || value.mode === 'erase', '笔画模式必须为 draw 或 erase。');
  requireValid(typeof value.color === 'string' && /^#[0-9a-f]{6}$/i.test(value.color), '笔画颜色必须为六位十六进制颜色。');
  const width = number(value.width, 0.002, 0.12, '笔画宽度');
  list(value.points, 5000, '笔画坐标点', 1);
  const points = [];
  for (const point of value.points) {
    list(point, 2, '坐标', 2);
    points.push([
      number(point[0], 0, 1, '横坐标'),
      number(point[1], 0, 1, '纵坐标'),
    ]);
  }
  return { mode: value.mode, color: value.color, width, points };
}

function copyStrokes(value) {
  list(value, MAX_STROKES, '笔画');
  return value.map(copyStroke);
}

function copyDrawing(value, isWork) {
  const keys = ['name', 'strokes', 'head', 'tail'];
  if (isWork) keys.push('id', 'createdAt', 'updatedAt');
  const label = isWork ? '作品' : '草稿';
  record(value, keys, label);
  const name = text(value.name, 32, `${label}名称`);
  const strokes = copyStrokes(value.strokes);
  requireValid(!isWork || strokes.some((stroke) => stroke.mode === 'draw'), '作品必须至少包含一个绘制笔画。');
  const head = copyPoint(value.head, '鱼头');
  const tail = copyPoint(value.tail, '鱼尾');
  // Decimal coordinates at the exact boundary can differ by a few floating-point ULPs.
  requireValid(Math.hypot(head.x - tail.x, head.y - tail.y) + Number.EPSILON >= 0.08, '鱼头与鱼尾的距离不能小于 0.08。');
  const drawing = { name, strokes, head, tail };
  if (!isWork) return drawing;
  return {
    id: text(value.id, 80, '作品 ID', 1),
    ...drawing,
    createdAt: number(value.createdAt, 0, Number.MAX_VALUE, '创建时间'),
    updatedAt: number(value.updatedAt, 0, Number.MAX_VALUE, '更新时间'),
  };
}

function copyDocument(value) {
  requireValid(value !== null && typeof value === 'object' && !Array.isArray(value), '鱼塘数据必须是对象。');
  const version = Object.getOwnPropertyDescriptor(value, 'version');
  requireValid(version && Object.hasOwn(version, 'value') && version.value === 1, '数据版本不受支持，不能读取或覆盖该版本。');
  record(value, ['version', 'works', 'draft', 'settings'], '鱼塘数据');
  list(value.works, 20, '作品');
  const ids = new Set();
  const works = value.works.map((item) => {
    const work = copyDrawing(item, true);
    requireValid(!ids.has(work.id), '作品 ID 不能重复。');
    ids.add(work.id);
    return work;
  });
  const draft = copyDrawing(value.draft, false);
  record(value.settings, ['count', 'speed', 'water', 'quality'], '设置');
  const count = number(value.settings.count, 8, 48, '鱼群数量');
  requireValid(Number.isInteger(count), '鱼群数量必须是整数。');
  const speed = number(value.settings.speed, 0.4, 1.6, '游动速度');
  number(value.settings.water, 0, 1, '波光强度');
  const quality = value.settings.quality;
  requireValid(quality === 'high' || quality === 'balanced' || quality === 'power-save', '质量档必须为 high、balanced 或 power-save。');
  return { version: 1, works, draft, settings: { count, speed, water: 1, quality: 'high' } };
}

function checkSize(raw) {
  requireValid(typeof raw === 'string', '存储数据必须是 JSON 字符串。');
  requireValid(raw.length <= MAX_BYTES && encoder.encode(raw).byteLength <= MAX_BYTES, '鱼塘 JSON 数据不能超过 3 MB。');
}

function parseDocument(raw) {
  checkSize(raw);
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch {
    throw new Error('鱼塘 JSON 数据已损坏，无法解析。');
  }
  return copyDocument(parsed);
}

function errorDetail(error) {
  return error instanceof Error && /[\u4e00-\u9fff]/.test(error.message)
    ? error.message
    : '数据格式无效。';
}

function failure(error) {
  return { ok: false, error };
}

export function createDefaultDocument() {
  return {
    version: 1,
    works: [],
    draft: {
      name: '',
      strokes: [],
      head: { x: 0.82, y: 0.5 },
      tail: { x: 0.18, y: 0.5 },
    },
    settings: { count: 24, speed: 1, water: 1, quality: 'high' },
  };
}

export function createRepository(storage, key = 'chijian.pond.v1') {
  function readStored() {
    let raw;
    try {
      raw = storage.getItem(key);
    } catch {
      return failure('无法读取本地存储，请检查浏览器的存储权限。');
    }
    if (raw === null) return { ok: true, raw, data: createDefaultDocument() };
    try {
      return { ok: true, raw, data: parseDocument(raw) };
    } catch (error) {
      return failure(`无法读取本地鱼塘，旧记录已保留。${errorDetail(error)}`);
    }
  }

  function restore(raw) {
    try {
      if (raw !== null) {
        storage.setItem(key, raw);
      } else if (typeof storage.removeItem === 'function') {
        storage.removeItem(key);
      } else {
        return false;
      }
      return storage.getItem(key) === raw;
    } catch {
      return false;
    }
  }

  return {
    load() {
      const result = readStored();
      return result.ok ? { ok: true, data: result.data } : result;
    },

    save(value) {
      let raw;
      try {
        raw = JSON.stringify(copyDocument(value));
        checkSize(raw);
      } catch (error) {
        return failure(`无法保存鱼塘。${errorDetail(error)}`);
      }

      // Check the current record on every save, including saves made without a preceding load.
      const previous = readStored();
      if (!previous.ok) return previous;
      try {
        storage.setItem(key, raw);
      } catch (error) {
        const quota = error?.name === 'QuotaExceededError'
          || error?.name === 'NS_ERROR_DOM_QUOTA_REACHED';
        return failure(quota
          ? '本地存储空间不足，保存失败；请保留当前画作后释放存储空间。'
          : '无法写入本地存储，保存失败；请保留当前画作并检查浏览器权限。');
      }

      try {
        const saved = storage.getItem(key);
        requireValid(saved !== null, '读回的记录不存在。');
        const data = parseDocument(saved);
        requireValid(saved === raw, '读回的数据与本次保存不一致。');
        return { ok: true, data };
      } catch {
        const restored = restore(previous.raw);
        return failure(restored
          ? '保存后的读回验证失败，已恢复之前的记录；请保留当前画作。'
          : '保存后的读回验证失败，无法确认旧记录已恢复；请保留当前画作，勿关闭页面。');
      }
    },
  };
}

function cloneStrokes(strokes) {
  return strokes.map((stroke) => ({
    mode: stroke.mode,
    color: stroke.color,
    width: stroke.width,
    points: stroke.points.map((point) => [...point]),
  }));
}

export function createHistory(strokes = []) {
  // Internal strokes are immutable and shared between snapshots; callers only receive deep copies.
  let states = [copyStrokes(strokes)];
  let cursor = 0;
  const current = () => states[cursor];
  const snapshot = () => cloneStrokes(current());
  function append(next) {
    states = states.slice(0, cursor + 1);
    states.push(next);
    cursor += 1;
    return snapshot();
  }

  return {
    getStrokes: snapshot,
    push(stroke) {
      requireValid(current().length < MAX_STROKES, '笔画数量不能超过 400。');
      const next = copyStroke(stroke);
      return append([...current(), next]);
    },
    undo() {
      if (cursor > 0) cursor -= 1;
      return snapshot();
    },
    redo() {
      if (cursor < states.length - 1) cursor += 1;
      return snapshot();
    },
    clear() {
      return current().length ? append([]) : snapshot();
    },
    replace(next) {
      const replacement = copyStrokes(next);
      states = [replacement];
      cursor = 0;
      return snapshot();
    },
    get canUndo() { return cursor > 0; },
    get canRedo() { return cursor < states.length - 1; },
  };
}
