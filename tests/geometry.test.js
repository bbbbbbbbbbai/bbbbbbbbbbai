import test from "node:test";
import assert from "node:assert/strict";
import { bendVertices, artworkTransform } from "../src/geometry.js";

test("body bending keeps the nose fixed and moves the tail smoothly", () => {
  const base = new Float32Array([0, 0, 50, 10, 100, 0]);
  const out = new Float32Array(base.length);
  bendVertices(base, out, 100, 0.4, 1, 10);
  assert.equal(out[0], 0);
  assert.notEqual(out[1], 0);
  assert.equal(out[4], 100);
  assert.equal(out[5], 0);
  assert.deepEqual([...base], [0, 0, 50, 10, 100, 0]);
});

test("artwork orientation maps its tail-to-head direction to the right", () => {
  const transform = artworkTransform({ x: .5, y: .1 }, { x: .5, y: .9 }, 800, 400);
  assert.ok(Math.abs(transform.angle - Math.PI / 2) < 1e-8);
  assert.equal(transform.cx, 400);
  assert.equal(transform.cy, 200);
});
