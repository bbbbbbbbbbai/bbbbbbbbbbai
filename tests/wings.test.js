import test from 'node:test';
import assert from 'node:assert/strict';
import {wingVertices} from '../src/geometry.js';

test('wing animation keeps the central body stable and moves both wing tips',()=>{
  const base=new Float32Array([50,50,50,0,50,100,100,50]);
  const out=new Float32Array(base.length);
  wingVertices(base,out,100,Math.PI/2,.3);
  assert.equal(out[1],50);
  assert.equal(out[7],50);
  assert.ok(out[3]>0&&out[5]<100);
  assert.equal(out[0],50);
  assert.deepEqual(Array.from(base),[50,50,50,0,50,100,100,50]);
});
