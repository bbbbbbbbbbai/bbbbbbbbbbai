import assert from 'node:assert/strict';
import test from 'node:test';
import {
  createDefaultDocument,
  createHistory,
  createRepository,
} from '../src/model.js';

const MAX_BYTES = 3 * 1024 * 1024;
const DEFAULT_KEY = 'chijian.pond.v1';
const clone = (value) => structuredClone(value);
const stroke = (overrides = {}) => ({
  mode: 'draw',
  color: '#cf543f',
  width: 0.02,
  points: [[0, 0], [0.5, 0.5], [1, 1]],
  ...overrides,
});
const artwork = (overrides = {}) => ({
  id: 'fish-1',
  name: '小鱼',
  strokes: [stroke()],
  head: { x: 0.82, y: 0.5 },
  tail: { x: 0.18, y: 0.5 },
  createdAt: 0,
  updatedAt: 123,
  ...overrides,
});
const document = () => ({
  ...createDefaultDocument(),
  works: [artwork()],
});

function memoryStorage(initial = null) {
  const records = new Map(initial === null ? [] : [[DEFAULT_KEY, initial]]);
  return {
    writes: 0,
    getItem(key) { return records.get(key) ?? null; },
    setItem(key, value) {
      this.writes += 1;
      records.set(key, value);
    },
    removeItem(key) { records.delete(key); },
  };
}

function assertFailure(result, pattern) {
  assert.equal(result.ok, false);
  assert.equal(typeof result.error, 'string');
  assert.match(result.error, /[\u4e00-\u9fff]/);
  if (pattern) assert.match(result.error, pattern);
}

test('default document has the exact independent initial shape', () => {
  const expected = {
    version: 1,
    works: [],
    draft: {
      name: '',
      strokes: [],
      head: { x: 0.82, y: 0.5 },
      tail: { x: 0.18, y: 0.5 },
    },
    settings: { count: 24, speed: 1, water: 0.65, quality: 'high' },
  };
  assert.deepEqual(createDefaultDocument(), expected);
  const changed = createDefaultDocument();
  changed.draft.head.x = 0;
  changed.draft.strokes.push(stroke());
  changed.settings.count = 48;
  assert.deepEqual(createDefaultDocument(), expected);
});

test('empty storage loads defaults without writing anything', () => {
  const storage = memoryStorage();
  const repository = createRepository(storage);
  assert.deepEqual(repository.load(), { ok: true, data: createDefaultDocument() });
  assert.equal(storage.writes, 0);
  assert.equal(storage.getItem(DEFAULT_KEY), null);
});

test('valid works, erasing strokes and draft round-trip through a fresh repository', () => {
  const storage = memoryStorage();
  const value = document();
  value.works[0].strokes.push(stroke({ mode: 'erase', color: '#FFFFFF' }));
  value.draft.strokes = [stroke({ mode: 'erase' })];
  const before = clone(value);
  const result = createRepository(storage).save(value);
  assert.deepEqual(result, { ok: true, data: value });
  assert.deepEqual(value, before);
  result.data.works[0].strokes[0].points[0][0] = 0.9;
  value.works[0].name = '改名';
  assert.deepEqual(createRepository(storage).load(), { ok: true, data: before });
});

test('repository honors a custom key', () => {
  const storage = memoryStorage();
  const repository = createRepository(storage, 'custom.pond');
  assert.equal(repository.save(document()).ok, true);
  assert.notEqual(storage.getItem('custom.pond'), null);
  assert.equal(storage.getItem(DEFAULT_KEY), null);
  assert.deepEqual(repository.load().data, document());
});

test('valid lower and upper boundaries are accepted', () => {
  for (const count of [8, 48]) {
    const value = document();
    value.settings = {
      count,
      speed: count === 8 ? 0.4 : 1.6,
      water: count === 8 ? 0 : 1,
      quality: count === 8 ? 'balanced' : 'high',
    };
    value.works = Array.from({ length: 20 }, (_, index) => artwork({
      id: `${index}`.padEnd(80, 'x'),
      name: '鱼'.repeat(32),
      head: { x: 0.18, y: 0.5 },
      tail: { x: 0.1, y: 0.5 },
    }));
    value.works[0].strokes = Array.from({ length: 400 }, () => stroke({
      width: 0.002,
      points: [[0, 1]],
    }));
    value.works[1].strokes = [stroke({
      width: 0.12,
      points: Array.from({ length: 5000 }, () => [1, 0]),
    })];
    value.draft.strokes = Array.from({ length: 400 }, () => stroke());
    assert.equal(createRepository(memoryStorage()).save(value).ok, true);
  }
});

const malformedCases = [
  ['missing version', (d) => { delete d.version; }],
  ['future version', (d) => { d.version = 2; }],
  ['old version', (d) => { d.version = 0; }],
  ['string version', (d) => { d.version = '1'; }],
  ['unknown document field', (d) => { d.unexpected = true; }],
  ['null works', (d) => { d.works = null; }],
  ['too many works', (d) => { d.works = Array.from({ length: 21 }, (_, i) => artwork({ id: String(i) })); }],
  ['duplicate ID', (d) => { d.works.push(artwork()); }],
  ['empty ID', (d) => { d.works[0].id = ''; }],
  ['long ID', (d) => { d.works[0].id = 'x'.repeat(81); }],
  ['numeric ID', (d) => { d.works[0].id = 1; }],
  ['long name', (d) => { d.works[0].name = '鱼'.repeat(33); }],
  ['null name', (d) => { d.works[0].name = null; }],
  ['missing timestamp', (d) => { delete d.works[0].updatedAt; }],
  ['negative timestamp', (d) => { d.works[0].createdAt = -1; }],
  ['infinite timestamp', (d) => { d.works[0].updatedAt = Infinity; }],
  ['NaN timestamp', (d) => { d.works[0].createdAt = NaN; }],
  ['string timestamp', (d) => { d.works[0].updatedAt = '123'; }],
  ['empty work', (d) => { d.works[0].strokes = []; }],
  ['erase-only work', (d) => { d.works[0].strokes[0].mode = 'erase'; }],
  ['too many strokes', (d) => { d.works[0].strokes = Array.from({ length: 401 }, () => stroke()); }],
  ['unknown mode', (d) => { d.works[0].strokes[0].mode = 'paint'; }],
  ['invalid hex color', (d) => { d.works[0].strokes[0].color = '#ggffff'; }],
  ['short color', (d) => { d.works[0].strokes[0].color = '#fff'; }],
  ['color with trailing newline', (d) => { d.works[0].strokes[0].color = '#ffffff\n'; }],
  ['small width', (d) => { d.works[0].strokes[0].width = 0.0019; }],
  ['large width', (d) => { d.works[0].strokes[0].width = 0.1201; }],
  ['string width', (d) => { d.works[0].strokes[0].width = '0.02'; }],
  ['empty points', (d) => { d.works[0].strokes[0].points = []; }],
  ['too many points', (d) => { d.works[0].strokes[0].points = Array.from({ length: 5001 }, () => [0, 0]); }],
  ['missing point coordinate', (d) => { d.works[0].strokes[0].points = [[0]]; }],
  ['extra point coordinate', (d) => { d.works[0].strokes[0].points = [[0, 0, 0]]; }],
  ['negative coordinate', (d) => { d.works[0].strokes[0].points[0][0] = -0.01; }],
  ['large coordinate', (d) => { d.works[0].strokes[0].points[0][1] = 1.01; }],
  ['nonfinite coordinate', (d) => { d.works[0].strokes[0].points[0][1] = Infinity; }],
  ['string coordinate', (d) => { d.works[0].strokes[0].points[0][0] = '0'; }],
  ['null stroke', (d) => { d.works[0].strokes[0] = null; }],
  ['sparse strokes', (d) => { d.works[0].strokes = new Array(2); }],
  ['sparse points', (d) => { d.works[0].strokes[0].points = new Array(2); }],
  ['head outside canvas', (d) => { d.works[0].head.x = 2; }],
  ['missing tail', (d) => { delete d.works[0].tail; }],
  ['short axis', (d) => { d.works[0].head = { x: 0.25, y: 0.5 }; }],
  ['null draft', (d) => { d.draft = null; }],
  ['long draft name', (d) => { d.draft.name = 'x'.repeat(33); }],
  ['short draft axis', (d) => { d.draft.head = clone(d.draft.tail); }],
  ['too many draft strokes', (d) => { d.draft.strokes = Array.from({ length: 401 }, () => stroke()); }],
  ['invalid draft stroke', (d) => { d.draft.strokes = [stroke({ width: 0 })]; }],
  ['null settings', (d) => { d.settings = null; }],
  ['missing setting', (d) => { delete d.settings.water; }],
  ['small count', (d) => { d.settings.count = 7; }],
  ['large count', (d) => { d.settings.count = 49; }],
  ['fractional count', (d) => { d.settings.count = 8.5; }],
  ['string count', (d) => { d.settings.count = '24'; }],
  ['slow speed', (d) => { d.settings.speed = 0.399; }],
  ['fast speed', (d) => { d.settings.speed = 1.601; }],
  ['negative water', (d) => { d.settings.water = -0.001; }],
  ['excessive water', (d) => { d.settings.water = 1.001; }],
  ['NaN water', (d) => { d.settings.water = NaN; }],
  ['unsupported quality', (d) => { d.settings.quality = 'low'; }],
  ['unknown stroke field', (d) => { d.works[0].strokes[0].pressure = 1; }],
  ['custom prototype', (d) => { Object.setPrototypeOf(d.settings, { inherited: true }); }],
  ['cyclic data', (d) => { d.draft.strokes = [d]; }],
  ['accessor', (d) => { Object.defineProperty(d.settings, 'water', { get() { throw new Error('Getter'); } }); }],
  ['JSON conversion hook', (d) => { d.toJSON = () => createDefaultDocument(); }],
];

for (const [label, mutate] of malformedCases) {
  test(`save rejects ${label} without changing the old record or input`, () => {
    const original = JSON.stringify(document());
    const storage = memoryStorage(original);
    const candidate = document();
    mutate(candidate);
    assertFailure(createRepository(storage).save(candidate));
    assert.equal(storage.getItem(DEFAULT_KEY), original);
    assert.equal(storage.writes, 0);
  });
}

for (const [label, raw] of [
  ['invalid JSON', '{"version":'],
  ['empty string', ''],
  ['null', 'null'],
  ['array', '[]'],
  ['primitive', '42'],
  ['future version', '{"version":9}'],
  ['incomplete document', '{"version":1}'],
  ['prototype field', '{"version":1,"__proto__":{"polluted":true}}'],
]) {
  test(`load and save protect an existing ${label} record`, () => {
    const storage = memoryStorage(raw);
    const repository = createRepository(storage);
    assertFailure(repository.load());
    assertFailure(repository.save(document()));
    assert.equal(storage.getItem(DEFAULT_KEY), raw);
    assert.equal(storage.writes, 0);
  });
}

test('save independently detects corruption introduced after a successful load', () => {
  const storage = memoryStorage(JSON.stringify(document()));
  const repository = createRepository(storage);
  assert.equal(repository.load().ok, true);
  storage.setItem(DEFAULT_KEY, '{broken');
  assertFailure(repository.save(document()));
  assert.equal(storage.getItem(DEFAULT_KEY), '{broken');
  assert.equal(storage.writes, 1);
});

test('storage access exceptions and absent storage return Chinese failures', () => {
  const storage = {
    getItem() { throw new Error('SecurityError'); },
    setItem() { assert.fail('must not write'); },
  };
  for (const unavailable of [storage, null, undefined, {}]) {
    const repository = createRepository(unavailable);
    assertFailure(repository.load(), /读取/);
    assertFailure(repository.save(document()), /读取/);
  }
});

test('quota write failure retains the previous record and the caller draft', () => {
  const original = JSON.stringify(document());
  const storage = memoryStorage(original);
  storage.setItem = () => { throw Object.assign(new Error('full'), { name: 'QuotaExceededError' }); };
  const candidate = document();
  candidate.draft.strokes.push(stroke());
  const before = clone(candidate);
  assertFailure(createRepository(storage).save(candidate), /空间|配额|容量/);
  assert.equal(storage.getItem(DEFAULT_KEY), original);
  assert.deepEqual(candidate, before);
});

test('generic write errors are returned without overwriting the previous record', () => {
  const original = JSON.stringify(document());
  const storage = memoryStorage(original);
  storage.setItem = () => { throw new Error('denied'); };
  assertFailure(createRepository(storage).save(document()), /写入|保存/);
  assert.equal(storage.getItem(DEFAULT_KEY), original);
});

test('a silently ignored write does not report success', () => {
  const storage = memoryStorage(JSON.stringify(document()));
  storage.setItem = () => {};
  const value = document();
  value.draft.name = '新草稿';
  assertFailure(createRepository(storage).save(value), /验证|核验/);
  assert.deepEqual(JSON.parse(storage.getItem(DEFAULT_KEY)), document());
});

for (const readBack of ['{corrupt', JSON.stringify({ version: 99 }), null, 'throw']) {
  test(`read-back failure (${readBack}) rolls back a valid previous record`, () => {
    const original = JSON.stringify(document());
    const storage = memoryStorage(original);
    const read = storage.getItem.bind(storage);
    let reads = 0;
    storage.getItem = (key) => {
      reads += 1;
      if (reads === 2) {
        if (readBack === 'throw') throw new Error('read-back blocked');
        return readBack;
      }
      return read(key);
    };
    const candidate = document();
    candidate.draft.name = '暂存';
    assertFailure(createRepository(storage).save(candidate), /验证|核验/);
    assert.equal(read(DEFAULT_KEY), original);
  });
}

test('a failed first save removes its unverified record when removeItem is available', () => {
  const storage = memoryStorage();
  const read = storage.getItem.bind(storage);
  let reads = 0;
  storage.getItem = (key) => (++reads === 2 ? '{bad' : read(key));
  assertFailure(createRepository(storage).save(document()));
  assert.equal(read(DEFAULT_KEY), null);
});

test('failed rollback is explicitly reported without throwing or discarding caller data', () => {
  const original = JSON.stringify(document());
  const storage = memoryStorage(original);
  const write = storage.setItem.bind(storage);
  let writes = 0;
  storage.setItem = (key, value) => {
    writes += 1;
    if (writes > 1) throw new Error('rollback blocked');
    write(key, '{corrupt');
  };
  assertFailure(createRepository(storage).save(document()), /恢复|回滚/);
});

test('JSON limit is measured in UTF-8 bytes, including existing record whitespace', () => {
  const raw = JSON.stringify(document());
  const extra = MAX_BYTES - Buffer.byteLength(raw);
  const exact = `${raw}${' '.repeat(extra)}`;
  assert.equal(createRepository(memoryStorage(exact)).load().ok, true);
  const storage = memoryStorage(`${exact} `);
  const repository = createRepository(storage);
  assertFailure(repository.load(), /3\s*MB/);
  assertFailure(repository.save(document()), /3\s*MB/);
  assert.equal(storage.writes, 0);
});

test('an otherwise valid document over 3 MB is rejected before writing', () => {
  const value = document();
  value.works[0].strokes = Array.from({ length: 100 }, () => stroke({
    points: Array.from({ length: 5000 }, () => [0.123456789, 0.987654321]),
  }));
  assert.ok(Buffer.byteLength(JSON.stringify(value)) > MAX_BYTES);
  const storage = memoryStorage();
  assertFailure(createRepository(storage).save(value), /3\s*MB/);
  assert.equal(storage.writes, 0);
});

test('history exposes independent stroke snapshots and protects input strokes', () => {
  const first = stroke();
  const initial = [first];
  const history = createHistory(initial);
  first.points[0][0] = 0.9;
  initial.length = 0;
  assert.deepEqual(history.getStrokes(), [stroke()]);
  const snapshot = history.getStrokes();
  snapshot[0].points[0][0] = 0.8;
  snapshot.push(stroke());
  assert.deepEqual(history.getStrokes(), [stroke()]);
  assert.equal(history.canUndo, false);
  assert.equal(history.canRedo, false);
});

test('push, undo and redo return independent snapshots and stable boundary states', () => {
  const history = createHistory();
  assert.deepEqual(history.undo(), []);
  assert.deepEqual(history.redo(), []);
  const next = stroke();
  const pushed = history.push(next);
  next.points[0][0] = 1;
  pushed[0].color = '#ffffff';
  assert.deepEqual(history.getStrokes(), [stroke()]);
  assert.equal(history.canUndo, true);
  assert.equal(history.canRedo, false);
  assert.deepEqual(history.undo(), []);
  assert.equal(history.canUndo, false);
  assert.equal(history.canRedo, true);
  const restored = history.redo();
  restored[0].points.pop();
  assert.deepEqual(history.getStrokes(), [stroke()]);
  assert.deepEqual(history.redo(), [stroke()]);
});

test('drawing after undo discards the redo branch', () => {
  const history = createHistory();
  history.push(stroke());
  history.push(stroke({ mode: 'erase' }));
  history.undo();
  const newest = stroke({ color: '#ffffff' });
  history.push(newest);
  assert.equal(history.canRedo, false);
  assert.deepEqual(history.redo(), [stroke(), newest]);
});

test('clear is undoable while replace establishes an isolated fresh baseline', () => {
  const history = createHistory([stroke()]);
  assert.deepEqual(history.clear(), []);
  assert.equal(history.canUndo, true);
  assert.deepEqual(history.undo(), [stroke()]);
  assert.deepEqual(history.redo(), []);
  const replacement = [stroke({ mode: 'erase' })];
  const returned = history.replace(replacement);
  returned.length = 0;
  replacement[0].points.length = 0;
  assert.deepEqual(history.getStrokes(), [stroke({ mode: 'erase' })]);
  assert.equal(history.canUndo, false);
  assert.equal(history.canRedo, false);
  assert.deepEqual(history.replace([]), []);
});

test('clear on an empty state preserves redo and does not add an undo entry', () => {
  const history = createHistory();
  assert.deepEqual(history.clear(), []);
  assert.equal(history.canUndo, false);
  history.push(stroke());
  history.undo();
  history.clear();
  assert.equal(history.canRedo, true);
  assert.equal(history.canUndo, false);
});

test('history validates incoming strokes without damaging current state or redo', () => {
  assert.throws(() => createHistory([stroke({ points: [] })]), /[\u4e00-\u9fff]/);
  const history = createHistory([stroke()]);
  history.push(stroke({ mode: 'erase' }));
  history.undo();
  assert.throws(() => history.push(stroke({ width: 1 })), /[\u4e00-\u9fff]/);
  assert.throws(() => history.replace([null]), /[\u4e00-\u9fff]/);
  assert.deepEqual(history.getStrokes(), [stroke()]);
  assert.equal(history.canRedo, true);
});

test('history applies the 400 stroke limit without losing the last valid snapshot', () => {
  const initial = Array.from({ length: 400 }, () => stroke());
  const history = createHistory(initial);
  assert.throws(() => history.push(stroke()), /400/);
  assert.deepEqual(history.getStrokes(), initial);
  assert.equal(history.canUndo, false);
  assert.throws(() => history.replace([...initial, stroke()]), /400/);
});

test('custom array prototypes cannot replace points during validation', () => {
  const points = [[0.5, 0.5]];
  const prototype = Object.create(Array.prototype);
  prototype[Symbol.iterator] = function* () {};
  Object.setPrototypeOf(points, prototype);
  assert.throws(() => createHistory([stroke({ points })]), /[\u4e00-\u9fff]/);
  const value = document();
  value.works[0].strokes = [stroke({ points })];
  const storage = memoryStorage();
  assertFailure(createRepository(storage).save(value));
  assert.equal(storage.writes, 0);
});

test('existing schema-invalid documents cannot be replaced by a valid save', () => {
  for (const change of [
    (value) => { value.works.push(artwork()); },
    (value) => { value.works[0].strokes = []; },
    (value) => { value.draft.head.x = -1; },
    (value) => { value.settings.count = 1; },
  ]) {
    const value = document();
    change(value);
    const raw = JSON.stringify(value);
    const storage = memoryStorage(raw);
    const repository = createRepository(storage);
    assertFailure(repository.load());
    assertFailure(repository.save(document()));
    assert.equal(storage.getItem(DEFAULT_KEY), raw);
    assert.equal(storage.writes, 0);
  }
});

test('getItem/setItem-only storage supports normal saves and reports unavailable rollback', () => {
  let raw = null;
  let reads = 0;
  const storage = {
    getItem() { return raw; },
    setItem(key, value) { raw = value; },
  };
  assert.equal(createRepository(storage).save(document()).ok, true);
  assert.deepEqual(createRepository(storage).load().data, document());
  raw = null;
  storage.getItem = () => (++reads === 2 ? '{bad' : raw);
  assertFailure(createRepository(storage).save(document()), /无法.*恢复/);
});
