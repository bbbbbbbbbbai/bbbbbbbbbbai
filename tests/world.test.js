import test from 'node:test';
import assert from 'node:assert/strict';
import { PondWorld } from '../src/world.js';

function random(seed = 12345) {
  return () => {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    return seed / 4294967296;
  };
}

function world(options = {}, width = 1920, height = 1080) {
  return new PondWorld(width, height, { random: random(), ...options });
}

function advance(pond, seconds, step = 1 / 60) {
  for (let i = 0; i < Math.ceil(seconds / step); i++) pond.update(step);
}

function valid(pond) {
  assert.equal(new Set(pond.fish.map((fish) => fish.id)).size, pond.fish.length);
  for (const fish of pond.fish) {
    for (const key of ['x', 'y', 'angle', 'length', 'phase', 'swimSpeed']) {
      assert.ok(Number.isFinite(fish[key]), `${fish.id}.${key} must be finite`);
    }
    assert.ok(fish.x >= 0 && fish.x <= pond.width, `${fish.id}.x in viewport`);
    assert.ok(fish.y >= 0 && fish.y <= pond.height, `${fish.id}.y in viewport`);
    assert.ok(fish.length > 0);
    assert.ok(fish.swimSpeed >= 0);
    assert.ok(Number.isInteger(fish.variant) && fish.variant >= 0 && fish.variant <= 9);
    assert.ok(fish.customId === null || typeof fish.customId === 'string');
  }
}

function difference(a, b) {
  return Math.atan2(Math.sin(a - b), Math.cos(a - b));
}

function parkOthers(pond) {
  pond.fish.slice(1).forEach((fish, index) => {
    fish.x = 120 + index * 180;
    fish.y = 950;
    fish.angle = 0;
  });
}

test('default population exposes stable finite render state at viewport scale', () => {
  const pond = world();
  assert.equal(pond.fish.length, 24);
  assert.equal(pond.food.length, 0);
  assert.ok(pond.fish.every((fish) => fish.customId === null));
  assert.ok(pond.fish.every((fish) => fish.length >= 45 && fish.length <= 85));
  valid(pond);
  const smaller = world({}, 960, 540);
  assert.deepEqual(smaller.fish.map((fish) => fish.length), pond.fish.map((fish) => fish.length / 2));
});

test('default pond includes a small calm turtle population', () => {
  const pond = world();
  assert.equal(pond.turtles.length, 3);
  assert.ok(pond.turtles.every((turtle) => turtle.variant >= 0 && turtle.variant <= 1));
  assert.ok(pond.turtles.every((turtle) => Number.isFinite(turtle.x) && Number.isFinite(turtle.y)));
  assert.ok(pond.turtles.every((turtle) => turtle.length >= 88 && turtle.length <= 132));
});

test('turtles drift independently and preserve normalized positions when resized', () => {
  const pond = world({}, 1000, 800);
  const before = pond.turtles.map((turtle) => ({ x: turtle.x, y: turtle.y }));
  pond.update(1);
  assert.ok(pond.turtles.some((turtle, index) => turtle.x !== before[index].x || turtle.y !== before[index].y));
  const moved = pond.turtles.map((turtle) => ({ x: turtle.x / pond.width, y: turtle.y / pond.height }));
  pond.resize(2000, 1600);
  pond.turtles.forEach((turtle, index) => {
    assert.ok(Math.abs(turtle.x / pond.width - moved[index].x) < 1e-12);
    assert.ok(Math.abs(turtle.y / pond.height - moved[index].y) < 1e-12);
  });
});

test('the interaction world covers the entire viewport before and after resizing', () => {
  const pond=world();
  assert.deepEqual(pond.habitat,{left:0,top:0,right:1920,bottom:1080});
  assert.equal(pond.feed(20,20),true);
  advance(pond,.15);
  assert.equal(pond.feed(700,450),true);
  advance(pond,45);
  for(const animal of [...pond.fish,...pond.turtles]) {
    assert.ok(animal.x>=0 && animal.x<=1920);
    assert.ok(animal.y>=0 && animal.y<=1080);
  }
  pond.resize(960,540);
  assert.deepEqual(pond.habitat,{left:0,top:0,right:960,bottom:540});
});

test('every canvas region drops a pellet exactly at the click without snapping', () => {
  for(const [x,y] of [[0,0],[1920,0],[0,1080],[1920,1080],[50,500],[1800,500],[800,20],[800,1060],[800,500]]){
    const pond=world({count:8});
    assert.equal(pond.feed(x,y),true,`canvas click ${x},${y} is accepted`);
    assert.ok(pond.food.length>=5);
    assert.deepEqual({x:pond.food[0].x,y:pond.food[0].y},{x,y},'the first pellet marks the exact click');
    for(const food of pond.food){
      assert.ok(food.x>=0&&food.x<=1920&&food.y>=0&&food.y<=1080);
      assert.ok(Math.hypot(food.x-x,food.y-y)<=16+1e-9,'scatter stays around the click, not around a remapped point');
    }
    assert.ok(new Set(pond.food.map(f=>`${f.x},${f.y}`)).size>1,'edge drops retain a natural spread');
  }
});

test('feeding impact preserves screen coordinates and rejects invalid input', () => {
  const pond=world();
  assert.deepEqual(pond.getFeedingPoint(800,500),{x:800,y:500});
  assert.deepEqual(pond.getFeedingPoint(20,20),{x:20,y:20});
  assert.deepEqual(pond.getFeedingPoint(1910,1070),{x:1910,y:1070});
  assert.deepEqual(pond.getFeedingPoint(0,0),{x:0,y:0});
  assert.equal(pond.getFeedingPoint(NaN,20),null);
  assert.equal(pond.getFeedingPoint(20,Infinity),null);
  assert.equal(pond.feed(20,20),true);
  const point=pond.getFeedingPoint(20,20);
  assert.ok(pond.food.every(food=>Math.hypot(food.x-point.x,food.y-point.y)<=16+1e-9));
});

test('mouse disturbance only flees nearby fish', () => {
  const pond = world({count: 8});
  Object.assign(pond.fish[0], {x:400,y:400});
  Object.assign(pond.fish[1], {x:1700,y:900});
  pond.disturb(410, 400);
  pond.update(1 / 60);
  assert.equal(pond.fish[0].behaviorState, 'flee');
  assert.notEqual(pond.fish[1].behaviorState, 'flee');
});

test('food states recover after the target disappears', () => {
  const pond = world({count: 8});
  pond.feed(800, 500);
  pond.update(1 / 60);
  assert.ok(pond.fish.some((fish) => fish.behaviorState === 'seek-food'));
  pond.food.length = 0;
  pond.update(1 / 60);
  assert.ok(pond.fish.every((fish) => fish.targetFoodId === null
    || pond.food.some((food) => food.id === fish.targetFoodId)));
});

test('food dropped from all canvas corners is eaten before expiration', () => {
  for(const [x,y] of [[0,0],[1920,0],[0,1080],[1920,1080]]){
    const pond=world({count:8});
    pond.fish.slice(1).forEach((fish,i)=>Object.assign(fish,{x:750+i*65,y:500,angle:0}));
    const fish=pond.fish[0];
    const target={x,y};
    fish.x=target.x+(x===0?120:-120);
    fish.y=target.y+(y===0?120:-120);
    fish.angle=Math.atan2(target.y-fish.y,target.x-fish.x);
    assert.equal(pond.feed(x,y),true);
    assert.deepEqual({x:pond.food[0].x,y:pond.food[0].y},target);
    const exactDropId=pond.food[0].id;
    advance(pond,10);
    assert.ok(!pond.food.some((food)=>food.id===exactDropId),
      `the exact corner drop at ${x},${y} is eaten before the 12-second expiry`);
  }
});

test('baseline count is clamped and existing fish retain identity and position', () => {
  const pond = world();
  const original = pond.fish.slice(0, 8);
  const states = original.map((fish) => ({ ...fish }));
  pond.setCount(-10);
  assert.equal(pond.fish.length, 8);
  assert.deepEqual(pond.fish, states);
  pond.setCount(500);
  assert.equal(pond.fish.length, 48);
  original.forEach((fish, index) => assert.equal(pond.fish[index], fish));
  pond.setCount(17.8);
  assert.equal(pond.fish.length, 18);
  pond.setCount(NaN);
  assert.equal(pond.fish.length, 18);
});

test('resize preserves normalized positions, headings, identity and relative size', () => {
  const pond = world();
  const before = pond.fish.map((fish) => ({ ...fish }));
  pond.resize(390, 844);
  pond.fish.forEach((fish, index) => {
    assert.equal(fish.id, before[index].id);
    assert.ok(Math.abs(fish.x / 390 - before[index].x / 1920) < 1e-12);
    assert.ok(Math.abs(fish.y / 844 - before[index].y / 1080) < 1e-12);
    assert.equal(fish.angle, before[index].angle);
    assert.ok(Math.abs(fish.length - before[index].length * 390 / 1080) < 1e-10);
  });
  advance(pond, 2);
  valid(pond);
});

test('injected randomness makes complete movement and feeding reproducible', () => {
  const a = world();
  const b = world();
  a.feed(700, 450);
  b.feed(700, 450);
  for (let i = 0; i < 300; i++) {
    if (i === 100) {
      a.disturb(1000, 600);
      b.disturb(1000, 600);
    }
    a.update(1 / 60);
    b.update(1 / 60);
  }
  assert.deepEqual(a.fish, b.fish);
  assert.deepEqual(a.food, b.food);
});

test('update caps elapsed time and ignores invalid or nonpositive deltas', () => {
  const a = world();
  const b = world();
  a.feed(500, 500);
  b.feed(500, 500);
  a.update(30);
  b.update(0.05);
  assert.deepEqual(a.fish, b.fish);
  assert.deepEqual(a.food, b.food);
  const before = a.fish.map((fish) => ({ ...fish }));
  for (const dt of [0, -1, NaN, Infinity, undefined]) a.update(dt);
  assert.deepEqual(a.fish, before);
});

test('each click emits 5 to 8 unique particles even when no animation frame has run', () => {
  const pond = world();
  assert.equal(pond.feed(500, 500), true);
  assert.ok(pond.food.length >= 5 && pond.food.length <= 8);
  assert.ok(pond.food.every((food) => food.age === 0 && Number.isFinite(food.x + food.y)));
  for(const [x,y] of [[20,500],[1900,500],[800,20],[800,1060]]){
    const count=pond.food.length;
    assert.equal(pond.feed(x,y),true);
    assert.ok(pond.food.length-count>=5&&pond.food.length-count<=8);
    assert.deepEqual({x:pond.food[count].x,y:pond.food[count].y},{x,y});
  }
  assert.equal(new Set(pond.food.map((food) => food.id)).size, pond.food.length);
});

test('food capacity replaces old pellets instead of silently rejecting new clicks', () => {
  const pond = world({ count: 8 }, 100000, 100000);
  pond.fish.forEach((fish, index) => {
    fish.x = 70000 + index * 1000;
    fish.y = 70000;
  });
  for (let i = 0; i < 80; i++) {
    const before = new Set(pond.food.map(food=>food.id));
    const accepted = pond.feed(500, 500);
    assert.equal(accepted,true);
    const added=pond.food.filter(food=>!before.has(food.id));
    assert.ok(added.length>=5&&added.length<=8);
    assert.ok(pond.food.length <= 128);
    advance(pond, 0.15, 0.05);
  }
  assert.ok(pond.food.length > 100);
});

test('food expires at 12 simulation seconds without being refreshed', () => {
  const pond = world({ count: 8 }, 100000, 100000);
  pond.fish.forEach((fish, index) => {
    fish.x = 70000 + index * 1000;
    fish.y = 70000;
  });
  pond.feed(500, 500);
  advance(pond, 11.9, 0.05);
  assert.ok(pond.food.length > 0);
  assert.ok(pond.food.every((food) => food.age >= 11.8));
  advance(pond, 0.15, 0.05);
  assert.equal(pond.food.length, 0);
});

test('artworks add at most 20 unique custom fish beyond the baseline', () => {
  const pond = world({ count: 8 });
  const baseline = pond.fish.slice();
  const works = Array.from({ length: 25 }, (_, index) => ({ id: `work-${index}`, name: `Fish ${index}` }));
  pond.setArtworks([...works, works[0], null, { id: '' }]);
  assert.equal(pond.fish.length, 28);
  assert.equal(pond.fish.filter((fish) => fish.customId !== null).length, 20);
  assert.equal(new Set(pond.fish.filter((fish) => fish.customId).map((fish) => fish.customId)).size, 20);
  baseline.forEach((fish, index) => assert.equal(pond.fish[index], fish));
  pond.setCount(48);
  assert.equal(pond.fish.length, 68);
  valid(pond);
});

test('artwork edits and reordering preserve fish physical state; deletes remove only that fish', () => {
  const pond = world({ count: 8 });
  pond.setArtworks([{ id: 'a', name: 'Original' }, { id: 'b' }]);
  advance(pond, 0.5);
  const custom = pond.fish.find((fish) => fish.customId === 'a');
  const before = { ...custom };
  pond.setArtworks([{ id: 'b' }, { id: 'a', name: 'Edited', updatedAt: 2 }]);
  assert.equal(pond.fish.find((fish) => fish.customId === 'a'), custom);
  assert.deepEqual(custom, before);
  pond.setArtworks([{ id: 'a', name: 'Edited' }, { id: 'c' }]);
  assert.equal(pond.fish.length, 10);
  assert.equal(pond.fish.find((fish) => fish.customId === 'a'), custom);
  assert.ok(!pond.fish.some((fish) => fish.customId === 'b'));
  pond.setArtworks([]);
  assert.equal(pond.fish.length, 8);
  advance(pond, 0.5);
  valid(pond);
});

test('speed is clamped and changes actual travel and swimming cadence', () => {
  const slow = world({ speed: -1, count: 8 }, 10000, 10000);
  const fast = world({ speed: 99, count: 8 }, 10000, 10000);
  assert.equal(slow.speed, 0.4);
  assert.equal(fast.speed, 1.6);
  for (const pond of [slow, fast]) {
    pond.fish.forEach((fish, index) => Object.assign(fish, { x: 1500 + index * 1000, y: 1500, angle: 0 }));
    Object.assign(pond.fish[0], { x: 5000, y: 5000, angle: 0 });
  }
  const origin = { ...slow.fish[0] };
  advance(slow, 0.5);
  advance(fast, 0.5);
  const slowDistance = Math.hypot(slow.fish[0].x - origin.x, slow.fish[0].y - origin.y);
  const fastDistance = Math.hypot(fast.fish[0].x - origin.x, fast.fish[0].y - origin.y);
  assert.ok(fastDistance > slowDistance * 2);
  assert.ok(fast.fish[0].swimSpeed > slow.fish[0].swimSpeed);
  slow.setSpeed(1.2);
  assert.equal(slow.speed, 1.2);
  slow.setSpeed(NaN);
  assert.equal(slow.speed, 1.2);
  valid(slow);
});

test('only food near a fish head is consumed, not food touching its tail', () => {
  const pond = world({ count: 8 });
  parkOthers(pond);
  const fish = pond.fish[0];
  Object.assign(fish, { x: 800, y: 400, angle: 0 });
  const head = { id: 'head', x: fish.x + fish.length * 0.4, y: fish.y, age: 0 };
  const tail = { id: 'tail', x: fish.x - fish.length * 0.4, y: fish.y, age: 0 };
  pond.food.push(head, tail);
  pond.update(0.001);
  assert.ok(!pond.food.includes(head));
  assert.ok(pond.food.includes(tail));
});

test('food targets disappearing are reselected and nearby food is actually reached', () => {
  const pond = world({ count: 8 });
  parkOthers(pond);
  const fish = pond.fish[0];
  Object.assign(fish, { x: 800, y: 400, angle: 0 });
  pond.food.push({ id: 'removed', x: 1000, y: 400, age: 0 });
  advance(pond, 0.2);
  pond.food.length = 0;
  pond.food.push({ id: 'new', x: 1100, y: 430, age: 0 });
  advance(pond, 6);
  assert.equal(pond.food.length, 0);
  assert.ok(fish.x > 900);
  valid(pond);
});

test('distant mouse movement has no effect on an identical seeded simulation', () => {
  const a = world();
  const b = world();
  a.disturb(-100000, -100000);
  advance(a, 1);
  advance(b, 1);
  assert.deepEqual(a.fish, b.fish);
});

test('nearby disturbance changes movement without instant reversal', () => {
  const a = world({ count: 8 });
  const b = world({ count: 8 });
  for (const pond of [a, b]) {
    parkOthers(pond);
    Object.assign(pond.fish[0], { x: 800, y: 400, angle: 0 });
  }
  a.disturb(835, 410);
  const previous = a.fish[0].angle;
  a.update(1 / 60);
  b.update(1 / 60);
  assert.ok(Math.abs(difference(a.fish[0].angle, previous)) < 0.12);
  advance(a, 0.4);
  advance(b, 0.4);
  assert.ok(Math.hypot(a.fish[0].x - b.fish[0].x, a.fish[0].y - b.fish[0].y) > 0.5);
});

test('a stationary mouse stops refreshing disturbance after 0.6 seconds', () => {
  const a = world({ count: 8 });
  const b = world({ count: 8 });
  const x = a.fish[0].x + 20;
  const y = a.fish[0].y + 5;
  a.disturb(x, y);
  b.disturb(x, y);
  for (let i = 0; i < 100; i++) {
    a.disturb(x, y);
    a.update(1 / 60);
    b.update(1 / 60);
  }
  assert.deepEqual(a.fish, b.fish);
});

test('after 0.6 seconds an old nearby mouse has no more influence than a distant mouse', () => {
  const a = world({ count: 8 });
  const b = world({ count: 8 });
  for (const pond of [a, b]) {
    parkOthers(pond);
    Object.assign(pond.fish[0], { x: 800, y: 400, angle: 0 });
    pond.disturb(835, 410);
    advance(pond, 0.65);
  }
  b.disturb(-100000, -100000);
  advance(a, 0.5);
  advance(b, 0.5);
  assert.deepEqual(a.fish, b.fish);
});

test('competing fish consume a shared pellet once without deleting other food', () => {
  const pond = world({ count: 8 });
  parkOthers(pond);
  const [a, b] = pond.fish;
  Object.assign(a, { x: 800 - a.length * 0.4, y: 400, angle: 0 });
  Object.assign(b, { x: 800 - b.length * 0.4, y: 400, angle: 0 });
  pond.food.push(
    { id: 'shared', x: 800, y: 400, age: 0 },
    { id: 'untouched', x: 1750, y: 100, age: 0 },
  );
  pond.update(0.001);
  assert.deepEqual(pond.food.map((food) => food.id), ['untouched']);
  pond.update(0.001);
  assert.deepEqual(pond.food.map((food) => food.id), ['untouched']);
  valid(pond);
});

test('long running dense simulations stay finite, in bounds and keep moving smoothly', () => {
  const pond = world({ count: 48 }, 390, 844);
  pond.setArtworks(Array.from({ length: 20 }, (_, index) => ({ id: `art-${index}` })));
  const initial = pond.fish.map((fish) => ({ ...fish }));
  for (let step = 0; step < 1200; step++) {
    if (step % 100 === 0) pond.feed(200, 450);
    if (step % 75 === 0) pond.disturb(80 + step % 230, 300);
    const angles = pond.fish.map((fish) => fish.angle);
    pond.update(0.05);
    pond.fish.forEach((fish, index) => {
      assert.ok(Math.abs(difference(fish.angle, angles[index])) <= 0.31, 'turns are bounded');
    });
    if (step % 60 === 0) valid(pond);
  }
  valid(pond);
  assert.ok(pond.fish.filter((fish, index) => Math.hypot(fish.x - initial[index].x, fish.y - initial[index].y) > 20).length > 50);
});

test('screen headings point right at zero and down at positive pi over two', () => {
  for (const angle of [0, Math.PI / 2]) {
    const pond = world({ count: 8 });
    parkOthers(pond);
    const fish = pond.fish[0];
    Object.assign(fish, { x: 800, y: 400, angle });
    pond.update(0.01);
    if (angle === 0) {
      assert.ok(fish.x > 800);
      assert.ok(Math.abs(fish.y - 400) < 0.02);
    } else {
      assert.ok(fish.y > 400);
      assert.ok(Math.abs(fish.x - 800) < 0.02);
    }
  }
});

test('invalid dimensions and coordinates cannot poison the simulation', () => {
  const pond = world({ count: NaN, speed: NaN }, 0, NaN);
  assert.equal(pond.fish.length, 24);
  assert.equal(pond.speed, 1);
  valid(pond);
  const before = pond.fish.map((fish) => ({ ...fish }));
  pond.resize(Infinity, -1);
  assert.deepEqual(pond.fish, before);
  assert.equal(pond.feed(NaN, 200), false);
  assert.equal(pond.feed(200, Infinity), false);
  pond.disturb(NaN, Infinity);
  advance(pond, 1);
  valid(pond);
});

test('food is viewport-clamped and follows normalized positions on resize', () => {
  const pond = world();
  pond.feed(-1000, 100000);
  assert.ok(pond.food.every((food) => food.x >= 0 && food.x <= 1920 && food.y >= 0 && food.y <= 1080));
  const food = pond.food.map((item) => ({ ...item }));
  pond.resize(960, 540);
  pond.food.forEach((item, index) => {
    assert.equal(item.x, food[index].x / 2);
    assert.equal(item.y, food[index].y / 2);
    assert.equal(item.id, food[index].id);
    assert.equal(item.age, 0);
  });
});

test('nearby fish separate instead of continuing as an overlapping pair', () => {
  const pond = world({ count: 8 });
  parkOthers(pond);
  Object.assign(pond.fish[0], { x: 700, y: 400, angle: 0 });
  Object.assign(pond.fish[1], { x: 700, y: 402, angle: 0 });
  advance(pond, 2);
  const [a, b] = pond.fish;
  assert.ok(Math.hypot(a.x - b.x, a.y - b.y) > (a.length + b.length) * 0.3);
  valid(pond);
});

test('boundary turning is gradual, resumes inward travel and does not gather the school at center', () => {
  const pond = world({ count: 24 });
  const fish = pond.fish[0];
  Object.assign(fish, { x: 1900, y: 540, angle: 0 });
  pond.update(0.05);
  assert.ok(Math.abs(fish.angle) < 0.2);
  advance(pond, 4);
  assert.ok(fish.x < 1860, 'fish escapes the right wall');
  advance(pond, 56);
  const center = pond.fish.filter((item) => Math.abs(item.x - 960) < 240 && Math.abs(item.y - 540) < 135);
  assert.ok(center.length < pond.fish.length / 2, 'no collective center target');
  const quadrants = new Set(pond.fish.map((item) => `${item.x < 960}:${item.y < 540}`));
  assert.equal(quadrants.size, 4);
  valid(pond);
});

test('dense schools do not accumulate large numbers of severely overlapping bodies', () => {
  const pond = world({ count: 48 }, 390, 844);
  pond.setArtworks(Array.from({ length: 20 }, (_, index) => ({ id: `work-${index}` })));
  let overlaps = 0;
  let samples = 0;
  for (let step = 0; step < 600; step++) {
    pond.update(0.05);
    if (step < 100 || step % 20 !== 0) continue;
    samples++;
    for (let i = 0; i < pond.fish.length; i++) {
      for (let j = i + 1; j < pond.fish.length; j++) {
        const a = pond.fish[i];
        const b = pond.fish[j];
        if (Math.hypot(a.x - b.x, a.y - b.y) < Math.min(a.length, b.length) * 0.3) overlaps++;
      }
    }
  }
  assert.ok(overlaps / samples < 4, `mean severely overlapping pairs: ${overlaps / samples}`);
});

test('fish can eat near the pond edge without wall avoidance making food unreachable', () => {
  for (const target of [{ x: 1918, y: 500 }, { x: 2, y: 500 }, { x: 800, y: 2 }]) {
    const pond = world({ count: 8 });
    parkOthers(pond);
    const fish = pond.fish[0];
    const origin = target.x > 1900 ? { x: 1750, y: 500, angle: 0 }
      : target.x < 10 ? { x: 170, y: 500, angle: Math.PI }
        : { x: 800, y: 170, angle: -Math.PI / 2 };
    Object.assign(fish, origin);
    pond.food.push({ id: 'edge', ...target, age: 0 });
    advance(pond, 8);
    assert.equal(pond.food.length, 0, `food at ${target.x},${target.y} is reached before expiration`);
    valid(pond);
  }
});

test('even a constant random fixture produces distinct spawn positions', () => {
  const pond = world({ count: 48, random: () => 0.5 });
  const positions = new Set(pond.fish.map((fish) => `${fish.x.toFixed(6)},${fish.y.toFixed(6)}`));
  assert.equal(positions.size, 48);
  advance(pond, 1);
  valid(pond);
});

test('fish facing out of screen corners turn back smoothly at different frame rates', () => {
  const corners = [
    { x: 0, y: 0, angle: -Math.PI * .75 },
    { x: 1920, y: 0, angle: -Math.PI * .25 },
    { x: 0, y: 1080, angle: Math.PI * .75 },
    { x: 1920, y: 1080, angle: Math.PI * .25 },
  ];
  for (const dt of [1/120, 1/60, 1/30, .05]) {
    for (const pose of corners) {
      const pond = world({ count: 8 });
      pond.fish.slice(1).forEach((fish, i) => Object.assign(fish, { x: 700+i*70, y: 500, angle: 0 }));
      const fish = pond.fish[0];
      Object.assign(fish, pose);
      for (let i = 0; i < Math.ceil(4/dt); i++) {
        const angle = fish.angle;
        pond.update(dt);
        assert.ok(Math.abs(difference(fish.angle, angle)) <= 3.8*dt+1e-9, 'no instant reversal');
      }
      assert.ok(fish.x > 15 && fish.x < 1905 && fish.y > 15 && fish.y < 1065,
        `corner ${pose.x},${pose.y} at dt=${dt}: fish remains at ${fish.x},${fish.y}`);
    }
  }
});

test('full-screen schools never remain pinned while their tails keep moving', () => {
  for (const [width, height, bounds, count] of [
    [1440, 900, { left: 0, top: 0, right: 1440, bottom: 900 }, 24],
    [390, 844, { left: 0, top: 0, right: 390, bottom: 844 }, 48],
  ]) {
    const pond = world({ count }, width, height);
    const stalled = new Map();
    for (let second = 0; second < 120; second++) {
      const travel = new Map(pond.fish.map(f => [f.id, 0]));
      for (let frame = 0; frame < 60; frame++) {
        const before = pond.fish.map(f => ({x: f.x, y: f.y}));
        pond.update(1/60);
        pond.fish.forEach((f, i) => travel.set(f.id,
          travel.get(f.id)+Math.hypot(f.x-before[i].x, f.y-before[i].y)));
      }
      for (const fish of pond.fish) {
        const seconds = travel.get(fish.id) < fish.length*.08 ? (stalled.get(fish.id) ?? 0)+1 : 0;
        stalled.set(fish.id, seconds);
        assert.ok(seconds < 3, `${width}x${height}: ${fish.id} pinned for ${seconds}s at t=${second}`);
        assert.ok(fish.x >= bounds.left && fish.x <= bounds.right && fish.y >= bounds.top && fish.y <= bounds.bottom);
      }
    }
  }
});

test('fish cross the former internal rectangle to eat at actual outer click locations', () => {
  for (const [target, origin] of [
    [{x:1800,y:500}, {x:1560,y:500,angle:0}],
    [{x:120,y:500}, {x:340,y:500,angle:Math.PI}],
    [{x:800,y:30}, {x:800,y:240,angle:-Math.PI/2}],
    [{x:800,y:1050}, {x:800,y:870,angle:Math.PI/2}],
  ]) {
    const pond = world({count:8});
    pond.fish.slice(1).forEach((fish,i)=>Object.assign(fish,{x:1000+i*60,y:650,angle:0}));
    Object.assign(pond.fish[0],origin);
    assert.equal(pond.feed(target.x,target.y),true);
    assert.ok(pond.food.every(food=>Math.hypot(food.x-target.x,food.y-target.y)<=16+1e-9));
    const exactDropId=pond.food[0].id;
    advance(pond,8);
    assert.ok(!pond.food.some((food)=>food.id===exactDropId),
      `the exact drop at ${target.x},${target.y} is eaten`);
  }
});
