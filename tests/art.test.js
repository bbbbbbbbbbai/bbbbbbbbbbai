import test from 'node:test';
import assert from 'node:assert/strict';
import sharp from 'sharp';
import { FISH_SPECIES, ART, coverFrame, waterBounds, lightForPeriod } from '../src/art.js';
import { paddleVertices } from '../src/geometry.js';

test('art catalog uses distinct generated subjects and separate baked shadows', async () => {
  assert.equal(FISH_SPECIES.length, 6);
  assert.equal(new Set(FISH_SPECIES.map(f => f.texture)).size, 6);
  for (const file of [ART.bed, ART.leaf, ART.flower, ART.turtle,
    ...FISH_SPECIES.flatMap(f => [f.texture, f.shadow])]) {
    assert.ok(file.startsWith('/assets/sunburst/'));
    const meta = await sharp(`public${file}`).metadata();
    assert.ok(meta.width > 100);
    if(file !== ART.bed) assert.equal(meta.hasAlpha, true);
  }
});

test('cover frame retains native aspect and covers portrait and landscape', () => {
  for (const [w,h] of [[1440,900],[2560,1440],[390,844]]) {
    const f=coverFrame(w,h,1536,1024);
    assert.ok(f.width >= w && f.height >= h);
    assert.ok(Math.abs(f.width / f.height - 1.5) < 1e-10);
    const b=waterBounds(w,h,f);
    assert.ok(b.left >= 0 && b.top >= 0 && b.right <= w && b.bottom <= h);
    assert.ok(b.right-b.left > w*.5 && b.bottom-b.top > h*.4);
  }
});

test('night lighting dims the scene but retains legible detail', () => {
  const day=lightForPeriod('day');
  const night=lightForPeriod('night');
  assert.ok(night.every((c,i) => c < day[i] && c > .25));
  assert.ok(night[2] > night[0]);
  assert.deepEqual(lightForPeriod('bad-value'), day);
});

test('turtle paddling preserves the shell and head while moving outer feet', () => {
  const base=new Float32Array([250,150,480,150,320,5,130,295]);
  const out=new Float32Array(base.length);
  paddleVertices(base,out,500,300,1,false);
  assert.deepEqual([...out.slice(0,4)],[...base.slice(0,4)]);
  assert.notDeepEqual([...out.slice(4)],[...base.slice(4)]);
  paddleVertices(base,out,500,300,1,true);
  assert.deepEqual([...out],[...base]);
});

test('ecosystem art catalog exposes local event assets', () => {
  for (const file of [ART.butterfly, ART.dragonfly, ART.firefly, ART.birdShadow, ART.fallingLeaf]) {
    assert.ok(file.startsWith('/assets/'));
    assert.ok(file.endsWith('.svg'));
  }
});
