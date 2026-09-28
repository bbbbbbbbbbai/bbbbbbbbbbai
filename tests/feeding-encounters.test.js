import test from 'node:test';
import assert from 'node:assert/strict';
import {Vector3} from 'yuka';
import {PondWorld} from '../src/world.js';

function isolated(width=1920,height=1080) {
  const pond=new PondWorld(width,height,{count:8,random:()=>.5});
  pond.fish.forEach((fish,i)=>Object.assign(fish,{x:width*.12+i*width*.1,y:height*.88,angle:0}));
  return pond;
}
const advance=(pond,seconds,dt=1/60)=>{for(let i=0;i<Math.ceil(seconds/dt);i++)pond.update(dt);};

test('a new feeding spot attracts local fish, never fish across the pond',()=>{
  for(const [width,height] of [[1920,1080],[390,844],[2560,1440]]){
    const pond=isolated(width,height);
    const [near,far]=pond.fish;
    Object.assign(near,{x:width*.35,y:height*.4});
    Object.assign(far,{x:width*.84,y:height*.4,angle:Math.PI});
    pond.feed(width*.35+near.length*1.5,height*.4);
    pond.update(1/60);
    assert.equal(near.behaviorState,'seek-food');
    assert.equal(far.targetFoodId,null,`${width}: remote fish cannot see the feeding spot`);
    assert.equal(far.behaviorState,'cruise');
  }
});

test('distant food does not alter an unaware fish trajectory or depth',()=>{
  const fed=isolated(),control=isolated();
  for(const pond of [fed,control])Object.assign(pond.fish[0],{x:1500,y:400,angle:0});
  fed.food.push({id:'distant',x:400,y:400,age:0});
  advance(fed,1);advance(control,1);
  assert.deepEqual(fed.fish[0],control.fish[0]);
});

test('fish discover existing food when swimming into range and abandon out-of-range targets',()=>{
  const pond=isolated(),fish=pond.fish[0];
  Object.assign(fish,{x:1600,y:400});
  pond.food.push({id:'meal',x:600,y:400,age:0});
  pond.update(1/60);
  assert.equal(fish.targetFoodId,null);
  Object.assign(fish,{x:480,y:400,angle:0});
  pond.update(1/60);
  assert.equal(fish.targetFoodId,'meal');
  Object.assign(fish,{x:1600,y:400});
  pond.update(1/60);
  assert.equal(fish.targetFoodId,null);
});

test('overlap avoidance stays bounded, leaves forward speed intact and fades at the depth boundary',()=>{
  const sample=(gap,depth)=>{
    const pond=isolated(),[a,b]=pond.fish;
    Object.assign(a,{x:800,y:400,angle:0,depth:.5});
    Object.assign(b,{x:800+gap,y:400,angle:0,depth});
    pond.update(.00001);
    const agent=pond._agents.get(a.id),force=new Vector3();
    agent.separation.calculate(agent.vehicle,force,1/60);
    force.multiplyScalar(agent.separation.weight);
    return {force,max:agent.vehicle.maxForce};
  };
  const touching=sample(.001,.5);
  assert.ok(touching.force.length()<=touching.max*.4,'overlap cannot exhaust steering capacity');
  assert.ok(Math.abs(touching.force.x)<touching.max*.01,'yield sideways rather than brake');
  const edge=sample(4,.5+.18-.0001);
  assert.ok(edge.force.length()<edge.max*.001,'no abrupt force switch at a depth boundary');
});

test('same-depth head-on feeding encounters keep advancing without sudden speed jumps',()=>{
  for(const dt of [1/120,1/60,1/30]){
    const pond=isolated(),[a,b]=pond.fish;
    Object.assign(a,{x:760,y:400,angle:0,depth:.1});
    Object.assign(b,{x:840,y:400,angle:Math.PI,depth:.1});
    pond.food.push({id:'meal',x:800,y:400,age:0});
    const previousSpeed=new Map();
    for(let i=0;i<Math.ceil(2/dt);i++){
      const previous=[{...a},{...b}];
      pond.update(dt);
      for(const [index,fish] of [a,b].entries()){
        const speed=Math.hypot(fish.x-previous[index].x,fish.y-previous[index].y)/dt;
        const agent=pond._agents.get(fish.id);
        assert.ok(speed>agent.vehicle.maxSpeed*.65,`${dt}: fish must not brake to the speed floor`);
        if(previousSpeed.has(fish.id))assert.ok(Math.abs(speed-previousSpeed.get(fish.id))<agent.vehicle.maxSpeed*dt*2,'no stop-start impulse');
        previousSpeed.set(fish.id,speed);
      }
    }
  }
});

test('almost coincident fish chasing the same food do not lock in a braking queue',()=>{
  for(const gap of [0,.001,.1,1,4]){
    const pond=isolated(),[a,b]=pond.fish;
    Object.assign(a,{x:800,y:400,angle:0,depth:.1});
    Object.assign(b,{x:800+gap,y:400,angle:0,depth:.1});
    pond.food.push({id:'meal',x:1000,y:400,age:0});
    let slowFrames=0;
    for(let i=0;i<120;i++){
      const x=a.x,y=a.y;
      pond.update(1/60);
      const speed=Math.hypot(a.x-x,a.y-y)*60;
      if(speed<pond._agents.get(a.id).vehicle.maxSpeed*.65)slowFrames++;
    }
    assert.ok(slowFrames<6,`gap ${gap}: ${slowFrames} braking frames`);
    assert.ok(a.x>885,'the following fish keeps progressing toward the food');
  }
});
