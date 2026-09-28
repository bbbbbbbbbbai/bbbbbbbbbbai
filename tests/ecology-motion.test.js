import test from 'node:test';
import assert from 'node:assert/strict';
import { EventScheduler } from '../src/events.js';
import { PondWorld } from '../src/world.js';

const advance=(world,seconds)=>{for(let i=0;i<Math.ceil(seconds*60);i++)world.update(1/60);};

test('birds from either side traverse the viewport before expiring',()=>{
  for(const value of [.2,.8]){
    const events=new EventScheduler({random:()=>value,width:1920,height:1080});
    events.configure({period:'day',season:'summer'});
    advance(events,4);
    const bird=events.birds[0];
    assert.ok(bird,'a first visible flight is scheduled early');
    assert.ok(bird.speed>0,'direction is encoded in angle, never a negative speed');
    const positions=[];
    while(events.birds.includes(bird)){positions.push(bird.x);events.update(1/60);}
    assert.ok(Math.min(...positions)<1920*.2);
    assert.ok(Math.max(...positions)>1920*.8);
  }
});

test('summer has visible leaves that land on water and insects of both day types',()=>{
  const events=new EventScheduler({random:()=>.4,width:1440,height:900});
  events.configure({period:'day',season:'summer',quality:'power-save'});
  advance(events,6);
  assert.ok(events.insects.some(i=>i.kind==='butterfly'));
  assert.ok(events.insects.some(i=>i.kind==='dragonfly'));
  assert.ok(events.leaves.some(l=>l.state==='floating'&&l.y>0&&l.y<900));
});

test('switching to night removes daytime insects and quiet mode suppresses birds',()=>{
  const events=new EventScheduler({random:()=>.7});
  advance(events,4);
  events.configure({period:'night',quietMode:true});
  advance(events,1);
  assert.ok(events.insects.length>0);
  assert.ok(events.insects.every(i=>i.kind==='firefly'));
  assert.equal(events.birds.length,0);
});

test('different depth fish can cross without planar separation',()=>{
  const pond=new PondWorld(1920,1080,{count:8,random:()=>.5});
  pond.fish.slice(2).forEach((f,i)=>Object.assign(f,{x:100+i*200,y:900}));
  const [a,b]=pond.fish;
  Object.assign(a,{x:800,y:400,angle:0,depth:.15});
  Object.assign(b,{x:805,y:400,angle:Math.PI,depth:.85});
  pond.update(1/60);
  assert.equal(pond._agents.get(a.id).vehicle.neighbors.length,0);
  assert.ok(a.x>800&&b.x<805);
});

test('near depth fish still avoid one another',()=>{
  const pond=new PondWorld(1920,1080,{count:8,random:()=>.5});
  pond.fish.slice(2).forEach((f,i)=>Object.assign(f,{x:100+i*200,y:900}));
  const [a,b]=pond.fish;
  Object.assign(a,{x:800,y:400,depth:.5});
  Object.assign(b,{x:805,y:400,depth:.52});
  pond.update(1/60);
  assert.equal(pond._agents.get(a.id).vehicle.neighbors.length,1);
});

test('resizing keeps live events in relative position and birds can still finish a wider crossing',()=>{
  const events=new EventScheduler({random:()=>.8,width:390,height:844});
  events.configure({period:'day',season:'summer'});
  advance(events,4);
  const bird=events.birds[0],insect=events.insects[0];
  const ix=insect.x/390,iy=insect.y/844;
  events.setBounds(2560,1440);
  assert.ok(Math.abs(insect.x/2560-ix)<1e-8);
  assert.ok(Math.abs(insect.y/1440-iy)<1e-8);
  let lastX=bird.x;
  while(events.birds.includes(bird)){lastX=bird.x;events.update(1/60);}
  assert.ok(lastX>2560,'existing flight survives until beyond the resized viewport');
});

test('night stops new flights but lets the current bird finish rather than disappear',()=>{
  const events=new EventScheduler({random:()=>.8,width:1920,height:1080});
  events.configure({period:'day'});
  advance(events,4);
  const bird=events.birds[0];
  events.configure({period:'night'});
  advance(events,1);
  assert.ok(events.birds.includes(bird));
  advance(events,80);
  assert.equal(events.birds.length,0);
});
