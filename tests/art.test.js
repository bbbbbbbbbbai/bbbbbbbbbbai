import test from 'node:test';
import assert from 'node:assert/strict';
import sharp from 'sharp';
import { FISH_SPECIES, ART, coverFrame, waterBounds, lightForPeriod } from '../src/art.js';
import { paddleVertices } from '../src/geometry.js';

async function rasterMetadata(file, format = 'png') {
  const meta = await sharp(`public${file}`).metadata();
  assert.equal(meta.format, format, `${file} must contain real ${format} data`);
  assert.ok(meta.width > 100 && meta.height > 0, `${file} must have valid raster dimensions`);
  if (format === 'png') assert.equal(meta.hasAlpha, true, `${file} needs an alpha channel`);
  return meta;
}

async function assertAssetPair(texture, shadow) {
  const image = await rasterMetadata(texture);
  const shade = await rasterMetadata(shadow);
  assert.equal(shade.width, image.width, `${shadow} must align with its subject`);
  assert.equal(shade.height, image.height, `${shadow} must align with its subject`);
}

test('art catalog uses distinct generated subjects and separate baked shadows', async () => {
  const expectedSpecies = [
    ['kohaku', 'sunburst'],
    ['ogon', 'sunburst'],
    ['showa', 'sunburst'],
    ['shiro', 'sunburst'],
    ['goldfish', 'sunburst'],
    ['carp', 'sunburst'],
    ['grass-carp', 'ecology'],
    ['loach', 'ecology'],
  ];
  assert.equal(FISH_SPECIES.length, 8);
  assert.deepEqual(FISH_SPECIES.map(f => f.id), expectedSpecies.map(([id]) => id));
  assert.equal(new Set(FISH_SPECIES.flatMap(f => [f.texture, f.shadow])).size, 16);
  for (const [index, [id, directory]] of expectedSpecies.entries()) {
    assert.equal(FISH_SPECIES[index].texture, `/assets/${directory}/${id}.png`);
    assert.equal(FISH_SPECIES[index].shadow, `/assets/${directory}/${id}-shadow.png`);
  }
  for (const [key, filename] of [
    ['bed', 'pond-bed.webp'], ['leaf', 'lily.png'], ['leafShadow', 'lily-shadow.png'],
    ['flower', 'lotus.png'], ['turtle', 'turtle.png'], ['turtleShadow', 'turtle-shadow.png'],
  ]) {
    assert.equal(ART[key], `/assets/sunburst/${filename}`);
    await rasterMetadata(ART[key], key === 'bed' ? 'webp' : 'png');
  }
  for (const fish of FISH_SPECIES) await assertAssetPair(fish.texture, fish.shadow);
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

test('ecosystem art catalog exposes generated PNG pairs and the existing firefly SVG', async () => {
  const expectedEvents = [
    ['egret', 'egret'], ['swallow', 'swallow'], ['butterfly', 'butterfly'],
    ['dragonfly', 'dragonfly'], ['fallingLeaf', 'falling-leaf'],
  ];
  for (const [key, id] of expectedEvents) {
    assert.equal(ART[key], `/assets/ecology/${id}.png`);
    assert.equal(ART[`${key}Shadow`], `/assets/ecology/${id}-shadow.png`);
  }
  assert.equal(ART.birdShadow, '/assets/ecology/egret-shadow.png');
  assert.equal(ART.firefly, '/assets/firefly.svg');
  const firefly = await sharp(`public${ART.firefly}`).metadata();
  assert.equal(firefly.format, 'svg');
  assert.ok(firefly.width > 0 && firefly.height > 0);
  for (const [key] of expectedEvents) await assertAssetPair(ART[key], ART[`${key}Shadow`]);
});
