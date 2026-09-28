import {test,expect} from '@playwright/test';

const errors=new WeakMap();
test.beforeEach(async ({page})=>{
  const messages=[];
  errors.set(page,messages);
  page.on('pageerror',error=>messages.push(error.message));
  page.on('console',message=>{
    if(message.type()==='error'||/INVALID_OPERATION|Could not initialize shader/.test(message.text()))messages.push(message.text());
  });
  await page.addInitScript(()=>{
    localStorage.clear();
    Object.defineProperty(navigator,'geolocation',{configurable:true,value:{
      getCurrentPosition(success,failure){failure({code:1});},
    }});
  });
  await page.route('**/src/main.js*',async route=>{
    const response=await route.fetch();
    await route.fulfill({response,body:`${await response.text()}\nwindow.__ecologyScene=scene;`});
  });
  await page.goto('/');
  await expect(page.locator('body')).toHaveAttribute('data-ready','true');
  await page.evaluate(async()=>{
    const s=window.__ecologyScene;s.app.ticker.stop();
    const {EventScheduler}=await import('/src/events.js');
    let seed=7341;
    s.world.ecosystem.events=new EventScheduler({
      width:s.world.width,height:s.world.height,
      random:()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;},
    });
  });
});

test.afterEach(async({page})=>expect(errors.get(page)).toEqual([]));

test('a real feeding click only recruits fish near the click',async({page},info)=>{
  const point=await page.evaluate(()=>{
    const s=window.__ecologyScene,w=s.world.width,h=s.world.height;
    s.setEnvironment({timeMode:'manual',manualTime:'day',weatherMode:'manual',weatherKind:'clear'});
    s.world.setCount(8);
    s.world.fish.forEach((f,i)=>Object.assign(f,{x:w*(.1+i*.1),y:h*.88,angle:0}));
    Object.assign(s.world.fish[0],{x:w*.3,y:h*.4,angle:0});
    Object.assign(s.world.fish[1],{x:w*.85,y:h*.4,angle:0});
    s.sync();s.app.renderer.render(s.app.stage);
    return {x:w*.35,y:h*.4};
  });
  await page.mouse.click(point.x,point.y);
  const result=await page.evaluate(()=>{
    const s=window.__ecologyScene;
    const drop={...s.world.food[0]};
    for(let i=0;i<6;i++){s.time+=1/60;s.world.update(1/60);s.sync();}
    s.renderSurface();s.renderLighting(1);s.app.renderer.render(s.app.stage);
    return {drop,near:s.world.fish[0].targetFoodId,far:s.world.fish[1].targetFoodId};
  });
  expect(result.drop.x).toBeCloseTo(point.x,3);
  expect(result.drop.y).toBeCloseTo(point.y,3);
  expect(result.near).not.toBeNull();
  expect(result.far).toBeNull();
  await page.screenshot({path:`artifacts/local-feeding-${info.project.name}.png`});
});

test('overlapping feeding fish keep visibly moving instead of braking in place',async({page},info)=>{
  const origin=await page.evaluate(()=>{
    const s=window.__ecologyScene,w=s.world.width,h=s.world.height,scale=Math.min(w,h)/1080;
    s.setEnvironment({timeMode:'manual',manualTime:'day',weatherMode:'manual',weatherKind:'clear'});
    s.world.setCount(8);
    s.world.fish.forEach((f,i)=>Object.assign(f,{x:w*(.1+i*.1),y:h*.88,angle:0}));
    const [a,b]=s.world.fish;
    Object.assign(a,{x:w*.4,y:h*.5,angle:0,depth:.1});
    Object.assign(b,{x:w*.4+.001*scale,y:h*.5,angle:0,depth:.1});
    s.world.food.push({id:'overlap-meal',x:w*.4+220*scale,y:h*.5,age:0});
    s.sync();s.renderSurface();s.renderLighting(1);s.app.renderer.render(s.app.stage);
    return a.x;
  });
  const before=await page.locator('#pond canvas').screenshot();
  const result=await page.evaluate(()=>{
    const s=window.__ecologyScene,[a,b]=s.world.fish;
    let slowFrames=0;
    for(let i=0;i<120;i++){
      const x=a.x,y=a.y;
      s.time+=1/60;s.world.update(1/60);s.sync();
      const ratio=Math.hypot(a.x-x,a.y-y)*60/s.world._agents.get(a.id).vehicle.maxSpeed;
      if(ratio<.65)slowFrames++;
    }
    s.renderSurface();s.renderLighting(1);s.app.renderer.render(s.app.stage);
    return {slowFrames,x:a.x,speed:s.world._agents.get(a.id).vehicle.maxSpeed,
      renderedX:s.views.get(a.id).mesh.x,separation:Math.hypot(a.x-b.x,a.y-b.y)};
  });
  expect(result.slowFrames).toBeLessThan(6);
  expect(result.x-origin).toBeGreaterThan(result.speed*1.2);
  expect(result.renderedX).toBe(result.x);
  expect(result.separation).toBeGreaterThan(1);
  const after=await page.locator('#pond canvas').screenshot();
  expect(before.equals(after)).toBe(false);
  await info.attach('encounter-metrics',{body:JSON.stringify(result),contentType:'application/json'});
  await page.screenshot({path:`artifacts/feeding-encounter-${info.project.name}.png`});
});

test('generated ecology has visible textured pixels, wings move, and layers have distinct depth',async({page},info)=>{
  const result=await page.evaluate(async()=>{
    const scene=window.__ecologyScene;
    scene.app.ticker.stop();
    scene.setEnvironment({timeMode:'manual',manualTime:'day',weatherMode:'manual',weatherKind:'clear',season:'summer',quietMode:false});
    const flightMidpoint=3+(scene.world.width/2+130)/145;
    for(let i=0;i<Math.ceil(flightMidpoint*60);i++){scene.time+=1/60;scene.world.update(1/60);}
    scene.sync();scene.renderLighting(2);scene.renderSurface();scene.renderAtmosphere();
    const pixelCount=async target=>{
      const canvas=await scene.app.renderer.extract.canvas({target});
      const pixels=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;
      let opaque=0,color=0;
      for(let i=0;i<pixels.length;i+=4){
        if(pixels[i+3]>40){opaque++;if(Math.max(pixels[i],pixels[i+1],pixels[i+2])-Math.min(pixels[i],pixels[i+1],pixels[i+2])>15)color++;}
      }
      return {opaque,color};
    };
    const bird=[...scene.eventViews.birds.values()][0];
    const insects=[...scene.eventViews.insects.values()];
    const leaf=[...scene.eventViews.leaves.values()].find(view=>view.parent===scene.floatingLeaves);
    if(!bird||!leaf||!insects.length)return {missing:true};
    const butterfly=insects.find(view=>view.ecologyKind==='butterfly');
    const vertices=Array.from(butterfly.geometry.positions);
    const before=await scene.app.renderer.extract.base64({target:butterfly});
    for(let i=0;i<12;i++){scene.time+=1/60;scene.world.update(1/60);}
    scene.sync();
    const after=await scene.app.renderer.extract.base64({target:butterfly});
    const stagePixels=async()=>{
      const canvas=await scene.app.renderer.extract.canvas({target:scene.app.stage});
      return canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;
    };
    // Inspect the composite: extracting a child bypasses its water filter and
    // does not prove the leaf is visible in the user's final scene.
    const withLeaves=await stagePixels();
    scene.floatingLeaves.visible=false;
    const withoutLeaves=await stagePixels();
    scene.floatingLeaves.visible=true;
    let leafPixels=0;
    for(let i=0;i<withLeaves.length;i+=4){
      if(Math.abs(withLeaves[i]-withoutLeaves[i])+Math.abs(withLeaves[i+1]-withoutLeaves[i+1])+Math.abs(withLeaves[i+2]-withoutLeaves[i+2])>20)leafPixels++;
    }
    const sampled={
      bird:await pixelCount(bird),insect:await pixelCount(butterfly),leafPixels,
      textures:[bird.texture.width,butterfly.texture.width,leaf.texture.width],
      meshMoved:vertices.some((v,i)=>Math.abs(v-butterfly.geometry.positions[i])>.01),
      pixelsMoved:before!==after,
      layered:bird.parent===scene.birdLayer&&butterfly.parent===scene.insectLayer&&leaf.parent===scene.floatingLeaves,
      depthSorted:scene.world.fish.every(f=>Math.abs(scene.views.get(f.id).mesh.zIndex-(1-f.depth)*1000)<.01),
      species:scene.world.fish.map(f=>f.profileId),
      missing:false,
    };
    scene.app.renderer.render(scene.app.stage);
    return sampled;
  });
  await info.attach('ecology-pixel-metrics',{body:JSON.stringify(result,null,2),contentType:'application/json'});
  expect(result.missing).toBe(false);
  expect(result.textures.every(w=>w>32)).toBe(true);
  expect(result.bird.opaque).toBeGreaterThan(300);
  expect(result.insect.color).toBeGreaterThan(80);
  expect(result.leafPixels).toBeGreaterThan(60);
  expect(result.meshMoved&&result.pixelsMoved&&result.layered&&result.depthSorted).toBe(true);
  await page.screenshot({path:`artifacts/ecology-day-${info.project.name}.png`});
});

test('automatic time updates the ecology as well as lighting and airborne art',async({page})=>{
  await page.clock.setFixedTime('2026-09-28T12:00:00');
  await page.evaluate(()=>{
    const s=window.__ecologyScene;
    s.setEnvironment({timeMode:'auto',weatherMode:'manual',weatherKind:'clear',quietMode:false});
    for(let i=0;i<240;i++){s.time+=1/60;s.world.update(1/60);}
    s.sync();s.renderLighting(3);
  });
  await page.clock.setFixedTime('2026-09-28T23:00:00');
  const result=await page.evaluate(()=>{
    const s=window.__ecologyScene;
    s.renderLighting(3);
    for(let i=0;i<180;i++){s.time+=1/60;s.world.update(1/60);}
    s.sync();s.renderAtmosphere();
    return {
      period:s.world.ecosystem.environment.period,
      insects:s.getEcosystemSnapshot().insects.map(i=>i.kind),
      tint:s.birdLayer.tint,
      waterBelowAir:s.waterEffects?.parent===s.root
        &&s.waterEffects.context.instructions.length>0
        &&s.app.stage.getChildIndex(s.root)<s.app.stage.getChildIndex(s.eventLayer),
    };
  });
  expect(result.period).toBe('night');
  expect(result.insects.length).toBeGreaterThan(0);
  expect(result.insects.every(k=>k==='firefly')).toBe(true);
  expect(result.tint).not.toBe(0xffffff);
  expect(result.waterBelowAir).toBe(true);
});

test('snow is visible and reduced motion removes precipitation without removing fish',async({page},info)=>{
  const snow=await page.evaluate(async()=>{
    const s=window.__ecologyScene;
    s.setEnvironment({timeMode:'manual',manualTime:'day',weatherMode:'manual',weatherKind:'snow'});
    s.time=5;s.renderLighting(2);s.renderAtmosphere();s.sync();
    const canvas=await s.app.renderer.extract.canvas({target:s.atmosphere});
    const pixels=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;
    let visible=0;for(let i=3;i<pixels.length;i+=4)if(pixels[i]>70)visible++;
    s.app.renderer.render(s.app.stage);
    return visible;
  });
  expect(snow).toBeGreaterThan(500);
  await page.screenshot({path:`artifacts/ecology-snow-${info.project.name}.png`});
  await page.emulateMedia({reducedMotion:'reduce'});
  await expect.poll(()=>page.evaluate(()=>window.__ecologyScene.world.ecosystem.environment.reducedMotion)).toBe(true);
  const reduced=await page.evaluate(()=>{
    const s=window.__ecologyScene;
    s.renderAtmosphere();
    return {fish:s.world.fish.length,precipitation:s.atmosphere.context.instructions.length,birds:s.getEcosystemSnapshot().birds.length};
  });
  expect(reduced.fish).toBeGreaterThan(0);
  expect(reduced.precipitation).toBe(0);
  expect(reduced.birds).toBe(0);
});

test('manual weather creates substantial visible precipitation and night replaces daytime insects',async({page},info)=>{
  const result=await page.evaluate(async()=>{
    const s=window.__ecologyScene;s.app.ticker.stop();
    s.setEnvironment({timeMode:'manual',manualTime:'day',weatherMode:'manual',weatherKind:'rain',quietMode:false});
    for(let i=0;i<180;i++){s.time+=1/60;s.world.update(1/60);}
    s.sync();s.renderAtmosphere();s.renderLighting(2);s.renderSurface();
    const canvas=await s.app.renderer.extract.canvas({target:s.atmosphere});
    const data=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;
    let precipitation=0;
    for(let i=3;i<data.length;i+=4)if(data[i]>35)precipitation++;
    const rings=s.eventViews.rain.size;
    s.app.renderer.render(s.app.stage);
    return {precipitation,rings};
  });
  expect(result.precipitation).toBeGreaterThan(1500);
  expect(result.rings).toBeGreaterThan(10);
  await page.screenshot({path:`artifacts/ecology-rain-${info.project.name}.png`});
  const night=await page.evaluate(()=>{
    const s=window.__ecologyScene;
    s.setEnvironment({manualTime:'night',weatherKind:'clear'});
    for(let i=0;i<180;i++){s.time+=1/60;s.world.update(1/60);}
    s.sync();s.renderLighting(2);s.renderSurface();s.renderAtmosphere();s.app.renderer.render(s.app.stage);
    return s.getEcosystemSnapshot().insects.map(i=>i.kind);
  });
  expect(night.length).toBeGreaterThan(0);
  expect(night.every(k=>k==='firefly')).toBe(true);
  await page.screenshot({path:`artifacts/ecology-night-${info.project.name}.png`});
});
