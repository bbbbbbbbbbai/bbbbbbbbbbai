import { Application, Assets, Container, Sprite, MeshPlane, Graphics, Texture, Filter, Rectangle, UniformGroup } from "pixi.js";
import { bendVertices, paddleVertices } from "./geometry.js";
import { bakeArtwork } from "./drawing.js";
import { getTimePeriod } from "./environment.js";
import { ART, FISH_SPECIES, coverFrame, waterBounds, lightForPeriod } from "./art.js";
import { atmosphereFor, defaultAtmosphere, normalizeAtmosphere, resolveWeatherKind } from "./atmosphere.js";
import { qualityBudget } from "./performance.js";

const vertex = `
in vec2 aPosition;
out vec2 vTextureCoord;
uniform highp vec4 uInputSize;
uniform highp vec4 uOutputFrame;
uniform vec4 uOutputTexture;
void main(){
  vec2 p=aPosition*uOutputFrame.zw+uOutputFrame.xy;
  p.x=p.x*(2.0/uOutputTexture.x)-1.0;
  p.y=p.y*(2.0*uOutputTexture.z/uOutputTexture.y)-uOutputTexture.z;
  gl_Position=vec4(p,0.0,1.0);
  vTextureCoord=aPosition*(uOutputFrame.zw*uInputSize.zw);
}`;
const fragment = `
in vec2 vTextureCoord;
out vec4 finalColor;
uniform sampler2D uTexture;
uniform vec4 uInputClamp;
uniform highp vec4 uInputSize;
uniform highp vec4 uOutputFrame;
uniform float uTime;
uniform float uStrength;
uniform float uAspect;
uniform vec3 uLight;
uniform vec4 uWater;
uniform vec4 uRipple;
uniform float uCloud;
uniform float uFog;
void main(){
  vec2 uv=vTextureCoord*uInputSize.xy/uOutputFrame.zw;
  vec2 inShore=smoothstep(uWater.xy,uWater.xy+vec2(.045),uv)
    *(1.0-smoothstep(uWater.zw-vec2(.045),uWater.zw,uv));
  float water=inShore.x*inShore.y;
  vec2 flow=vec2(sin(uv.y*48.0+uTime*.65)+sin(uv.y*83.0-uTime*.4)*.3,
    cos(uv.x*57.0-uTime*.5)+sin(uv.y*39.0+uTime*.3)*.3);
  vec2 delta=(uv-uRipple.xy)*vec2(uAspect,1.0);
  float distance=length(delta);
  float ring=sin(distance*170.0-uRipple.z*9.0)*exp(-abs(distance-uRipple.z*.065)*45.0);
  float fade=max(0.0,1.0-uRipple.z/3.0)*uRipple.w;
  vec2 ripple=delta/max(.01,distance)*ring*fade*.0014;
  vec2 offset=(flow*.0009*uStrength+ripple)*water;
  vec2 sampleOffset=offset*uOutputFrame.zw*uInputSize.zw;
  vec4 color=texture(uTexture,clamp(vTextureCoord+sampleOffset,uInputClamp.xy,uInputClamp.zw));
  float cloud=.5+.25*sin(uv.x*6.0+uv.y*4.0+uTime*.055)
    +.25*sin(uv.x*3.0-uv.y*7.0-uTime*.035);
  color.rgb*=uLight*(1.0-cloud*uCloud);
  float mist=(.5+.5*sin(uv.y*8.0+sin(uv.x*5.0+uTime*.07)))*uFog;
  color.rgb=mix(color.rgb,vec3(.73,.81,.78)*uLight,mist);
  finalColor=color;
}`;

function meshFor(texture, verticesX=25, verticesY=7) {
  const mesh=new MeshPlane({texture,verticesX,verticesY});
  mesh.pivot.set(texture.width/2,texture.height/2);
  return mesh;
}

export class PondScene {
  constructor(host,world,settings) {
    this.host=host;this.world=world;this.settings={...settings};
    this.views=new Map();this.turtleViews=new Map();this.artworks=new Map();
    this.eventViews={insects:new Map(),birds:new Map(),leaves:new Map(),rain:new Map()};
    this.time=0;this.ripples=[];this.paused=false;
    this.environment=defaultAtmosphere();
    this.weather={kind:"clear"};
    this.light=lightForPeriod(getTimePeriod());
    this.cloud=0;this.fog=0;this.atmosphereParams=atmosphereFor({period:"day",weatherKind:"clear",season:"summer",quality:settings.quality});
    this.budget=qualityBudget(settings.quality,{width:innerWidth,height:innerHeight,devicePixelRatio:devicePixelRatio||1});
  }
  async init() {
    this.app=new Application();
    await this.app.init({
      preference:"webgl",antialias:true,autoDensity:true,
      resolution:this.resolution(),background:"#315f50",
      powerPreference:"low-power",preserveDrawingBuffer:true,
    });
    this.host.append(this.app.canvas);
    this.arrivalLabel=document.createElement("div");
    this.arrivalLabel.className="arrival-marker";this.arrivalLabel.hidden=true;
    this.arrivalLabel.setAttribute("aria-hidden","true");
    this.host.append(this.arrivalLabel);
    this.motionPreference=matchMedia("(prefers-reduced-motion: reduce)");
    this.app.canvas.setAttribute("aria-label","锦鲤鱼塘");
    const paths=[...Object.values(ART),...FISH_SPECIES.flatMap(s=>[s.texture,s.shadow])];
    this.textures=await Assets.load([...new Set(paths)]);
    this.root=new Container();
    this.root.eventMode="none";
    this.bed=new Sprite(this.textures[ART.bed]);
    this.shadows=new Container();this.animals=new Container();
    this.animals.sortableChildren=true;
    this.surface=new Graphics();this.plants=new Container();this.atmosphere=new Graphics();
    this.root.addChild(this.bed,this.shadows,this.animals,this.surface,this.plants);
    this.eventLayer=new Container();this.eventLayer.sortableChildren=true;
    this.waterFilter=Filter.from({
      gl:{vertex,fragment},
      resources:{pondUniforms:new UniformGroup({
        uTime:{value:0,type:"f32"},uStrength:{value:this.settings.water,type:"f32"},
        uAspect:{value:1,type:"f32"},uLight:{value:new Float32Array(this.light),type:"vec3<f32>"},
        uWater:{value:new Float32Array([0,0,1,1]),type:"vec4<f32>"},
        uRipple:{value:new Float32Array([0,0,4,0]),type:"vec4<f32>"},
        uCloud:{value:0,type:"f32"},uFog:{value:0,type:"f32"},
      })},
    });
    // One composite pass; animal shadows are baked, not dozens of live blur passes.
    this.root.filters=[this.waterFilter];
    this.app.stage.addChild(this.root,this.eventLayer,this.atmosphere);
    const specs=[
      [.18,.39,118,-.65],[.22,.44,77,1.6],[.78,.28,94,2.3],
      [.81,.69,114,-.8],[.77,.74,68,1.1],[.20,.70,84,2.6],
    ];
    this.plantViews=specs.map((spec,index)=>{
      const leaf=new Sprite(this.textures[ART.leaf]);leaf.anchor.set(.5);
      const shadow=new Sprite(this.textures[ART.leafShadow]);shadow.anchor.set(.5);shadow.alpha=.28;
      leaf.tint=index%2 ? 0xe0efcc : 0xffffff;
      this.plants.addChild(shadow,leaf);
      return {leaf,shadow,spec,index};
    });
    this.flowers=[[.184,.375,66,-.2],[.812,.681,72,.4]].map(spec=>{
      const flower=new Sprite(this.textures[ART.flower]);flower.anchor.set(.5);
      this.plants.addChild(flower);return {flower,spec};
    });
    this.resize();
    this.observer=new ResizeObserver(()=>this.resize());this.observer.observe(this.host);
    this.app.ticker.maxFPS=this.settings.quality==="high"?60:30;
    this.app.ticker.add(ticker=>{
      if(this.paused||document.hidden)return;
      const dt=Math.min(ticker.deltaMS/1000,.05);
      this.time+=dt;this.world.update(dt);this.sync();
      this.renderLighting(dt);this.renderSurface();this.renderAtmosphere();
      if(import.meta.env.DEV){
        const snapshot=this.getEcosystemSnapshot();
        window.__pondDiagnostics={
          quality:this.environment.quality??this.settings.quality,
          period:this.environment.timeMode==="manual"?this.environment.manualTime:getTimePeriod(),
          weather:resolveWeatherKind(this.environment,this.weather),
          counts:{fish:this.world.fish.length,insects:snapshot.insects.length,birds:snapshot.birds.length,leaves:snapshot.leaves.length,rain:snapshot.rain.length},
          lastFrameMS:ticker.deltaMS,
        };
      }
      for(const p of this.plantViews){
        p.leaf.rotation=p.spec[3]+Math.sin(this.time*.45+p.index)*.017;
        p.shadow.rotation=p.leaf.rotation;
        p.leaf.y=p.baseY+Math.sin(this.time*.65+p.index)*.9;
        p.shadow.y=p.leaf.y+5;
      }
    });
    this.sync();this.renderSurface();this.renderLighting(1);
  }
  resolution() {
    const w=this.host.clientWidth||innerWidth,h=this.host.clientHeight||innerHeight;
    const limit=this.settings.quality==="high"?3_000_000:1_500_000;
    return Math.min(devicePixelRatio||1,this.settings.quality==="high"?1.5:1,Math.sqrt(limit/(w*h)));
  }
  resize() {
    if(!this.bed)return;
    const width=this.host.clientWidth,height=this.host.clientHeight;
    if(width<=0||height<=0)return;
    this.app.renderer.resolution=this.resolution();
    this.app.renderer.resize(width,height);
    this.world.resize(width,height);
    this.frame=coverFrame(width,height,this.bed.texture.width,this.bed.texture.height);
    this.bed.scale.set(this.frame.scale);this.bed.position.set(this.frame.x,this.frame.y);
    // The image has an internal pond shape, but the interaction surface is
    // the complete desktop viewport. Fish and food must follow the cursor
    // anywhere on the visible canvas.
    this.world.setHabitat({left:0,top:0,right:width,bottom:height});
    this.root.filterArea=new Rectangle(0,0,width,height);
    const uniforms=this.waterFilter.resources.pondUniforms.uniforms;
    uniforms.uAspect=width/height;
    const b=this.world.habitat;
    uniforms.uWater=new Float32Array([b.left/width,b.top/height,b.right/width,b.bottom/height]);
    const scale=Math.min(width,height)/900;
    const plantX=x=>Math.max(width*.08,Math.min(width*.92,this.frame.x+this.frame.width*x));
    for(const p of this.plantViews){
      p.leaf.position.set(plantX(p.spec[0]),this.frame.y+this.frame.height*p.spec[1]);
      p.baseY=p.leaf.y;p.leaf.rotation=p.spec[3];
      p.leaf.scale.set(p.spec[2]*scale/p.leaf.texture.width);
      p.shadow.scale.copyFrom(p.leaf.scale);p.shadow.position.set(p.leaf.x+3,p.leaf.y+5);
    }
    for(const {flower,spec} of this.flowers){
      flower.position.set(plantX(spec[0]),this.frame.y+this.frame.height*spec[1]);
      flower.scale.set(spec[2]*scale/flower.texture.width);flower.rotation=spec[3];
    }
  }
  setArtworks(works) {
    for(const [id,v] of this.views)if(v.customId){v.mesh.destroy();v.shadow.destroy();this.views.delete(id);}
    for(const texture of this.artworks.values())texture.destroy(true);
    this.artworks.clear();
    for(const work of works){const canvas=bakeArtwork(work);if(canvas)this.artworks.set(work.id,Texture.from(canvas));}
    this.world.setArtworks(works);this.sync();
  }
  welcomeFish(customId,name,{relocate=false}={}) {
    const fish=this.world.fish.find(f=>f.customId===customId);
    if(!fish||!this.arrivalLabel)return;
    if(relocate){
      const b=this.world.habitat;
      fish.x=b.left+(b.right-b.left)*.5;fish.y=b.top+(b.bottom-b.top)*.56;
      fish.angle=-.3;
    }
    this.arrival={id:fish.id,at:this.time};
    this.arrivalLabel.textContent=name;this.arrivalLabel.hidden=false;
    if(!this.motionPreference.matches)this.ripples.push({x:fish.x,y:fish.y,at:this.time});
    this.sync();this.renderSurface();
  }
  configure(settings) {
    this.settings={...settings};
    this.world.setCount(settings.count);this.world.setSpeed(settings.speed);
    this.budget=qualityBudget(settings.quality,{width:this.host.clientWidth||innerWidth,height:this.host.clientHeight||innerHeight,devicePixelRatio:devicePixelRatio||1});
    if(!this.waterFilter)return;
    this.waterFilter.resources.pondUniforms.uniforms.uStrength=settings.water;
    this.app.ticker.maxFPS=settings.quality==="high"?60:30;
    this.resize();this.sync();
  }
  setEnvironment(environment,weather) {
    this.environment=normalizeAtmosphere({...this.environment,...environment},this.environment);
    this.weather={...this.weather,...weather};
    this.world.setEnvironment({
      period:this.environment.timeMode==="manual"?this.environment.manualTime:getTimePeriod(),
      weatherKind:resolveWeatherKind(this.environment,this.weather),
      season:this.environment.season,
      quietMode:this.environment.quietMode,
      reducedMotion:this.motionPreference?.matches ?? false,
      quality:this.environment.quality ?? this.settings.quality,
    });
    this.atmosphereParams=atmosphereFor({
      period:this.environment.timeMode==="manual"?this.environment.manualTime:getTimePeriod(),
      weatherKind:resolveWeatherKind(this.environment,this.weather),
      season:this.environment.season,
      quietMode:this.environment.quietMode,
      reducedMotion:this.motionPreference?.matches ?? false,
      quality:this.environment.quality ?? this.settings.quality,
    });
  }
  getEcosystemSnapshot() { return this.world.getEcosystemSnapshot(); }
  sync() {
    if(!this.textures)return;
    const ids=new Set(this.world.fish.map(f=>f.id));
    for(const [id,v] of this.views)if(!ids.has(id)){v.mesh.destroy();v.shadow.destroy();this.views.delete(id);}
    for(const fish of this.world.fish){
      const spec=FISH_SPECIES[fish.variant]??FISH_SPECIES[0];
      let v=this.views.get(fish.id);
      if(!v){
        const texture=fish.customId?this.artworks.get(fish.customId):this.textures[spec.texture];
        if(!texture)continue;
        const mesh=meshFor(texture);
        const shadow=new Sprite(fish.customId?texture:this.textures[spec.shadow]);shadow.anchor.set(.5);
        if(fish.customId)shadow.tint=0x142a23;
        this.animals.addChild(mesh);this.shadows.addChild(shadow);
        const index=Number(String(fish.id).replace(/\D/g,""))||0;
        v={mesh,shadow,customId:fish.customId,base:new Float32Array(mesh.geometry.positions),index};
        this.views.set(fish.id,v);
      }
      const texture=v.mesh.texture;
      const depth=.86+(v.index%5)*.037+Math.sin(this.time*.11+v.index)*.025;
      const width=fish.length*1.18*depth;
      v.mesh.scale.set(width/texture.width);
      v.mesh.position.set(fish.x,fish.y);v.mesh.rotation=fish.angle;v.mesh.zIndex=fish.y;
      v.mesh.alpha=fish.customId?1:.87+(depth-.86)*.5;
      v.mesh.tint=fish.customId?0xffffff:0xe2efdf;
      bendVertices(v.base,v.mesh.geometry.positions,texture.width,0,fish.phase,
        texture.width*(fish.customId ? .04 : spec.bend));
      v.mesh.geometry.getBuffer("aPosition").update();
      v.shadow.scale.copyFrom(v.mesh.scale);v.shadow.rotation=fish.angle;
      v.shadow.position.set(fish.x+6,fish.y+8+(1-depth)*25);
      v.shadow.alpha=.14+(depth-.86)*.18;
    }
    this.syncTurtles();
    this.syncEcosystem();
  }
  syncTurtles() {
    const ids=new Set(this.world.turtles.map(t=>t.id));
    for(const [id,v] of this.turtleViews)if(!ids.has(id)){v.mesh.destroy();v.shadow.destroy();this.turtleViews.delete(id);}
    for(const turtle of this.world.turtles){
      let v=this.turtleViews.get(turtle.id);
      if(!v){
        const mesh=meshFor(this.textures[ART.turtle],23,17);
        const shadow=new Sprite(this.textures[ART.turtleShadow]);shadow.anchor.set(.5);shadow.alpha=.23;
        this.animals.addChild(mesh);this.shadows.addChild(shadow);
        v={mesh,shadow,base:new Float32Array(mesh.geometry.positions)};this.turtleViews.set(turtle.id,v);
      }
      const texture=v.mesh.texture;
      v.mesh.scale.set(turtle.length*1.03/texture.width);
      v.mesh.position.set(turtle.x,turtle.y-(turtle.surfacing?Math.sin((turtle.surfaceProgress??0)*Math.PI)*4:0));v.mesh.rotation=turtle.angle;v.mesh.zIndex=turtle.y;
      v.mesh.alpha=.91;v.mesh.tint=turtle.variant?0xd4e3cc:0xe5ecd8;
      paddleVertices(v.base,v.mesh.geometry.positions,texture.width,texture.height,turtle.phase,turtle.resting);
      v.mesh.geometry.getBuffer("aPosition").update();
      v.shadow.scale.copyFrom(v.mesh.scale);v.shadow.rotation=turtle.angle;
      v.shadow.position.set(turtle.x+4,turtle.y+6);
    }
  }
  syncEcosystem() {
    if(!this.eventLayer)return;
    const snapshot=this.getEcosystemSnapshot();
    const maps=[
      ["insects",this.eventViews.insects,item=>item.kind==="butterfly"?ART.butterfly:item.kind==="dragonfly"?ART.dragonfly:ART.firefly],
      ["birds",this.eventViews.birds,()=>ART.birdShadow],
      ["leaves",this.eventViews.leaves,()=>ART.fallingLeaf],
      ["rain",this.eventViews.rain,null],
    ];
    for(const [kind,map,asset] of maps){
      const current=new Set(snapshot[kind].map(item=>item.id));
      for(const [id,view] of map){
        if(!current.has(id)){view.destroy();map.delete(id);}
      }
      for(const item of snapshot[kind]){
        let view=map.get(item.id);
        if(!view){
          view=asset?new Sprite(this.textures[asset]):new Graphics();
          if(asset)view.anchor.set(.5);
          map.set(item.id,view);this.eventLayer.addChild(view);
        }
        if(kind==="rain"){
          view.clear();
          view.circle(item.x,item.y,item.radius).stroke({color:0xcbe0cf,width:1,alpha:Math.min(.24,item.life*.25)});
        }else{
          view.position.set(item.x,item.y);
          view.rotation=item.rotation??item.angle??0;
          view.zIndex=item.y;
          view.alpha=kind==="insects"&&item.kind==="firefly"
            ? .35+.65*Math.max(0,Math.sin(this.time*2+item.phase))
            : Math.min(1,item.life);
          const scale=kind==="birds"?Math.min(this.world.width,this.world.height)/1200:.55;
          view.scale.set(scale);
        }
      }
    }
  }
  feed(x,y) {
    if(!this.world.feed(x,y))return false;
    const point=this.world.getFeedingPoint(x,y);
    this.ripples.push({...point,at:this.time});return true;
  }
  renderLighting(dt) {
    const period=this.environment.timeMode==="manual"?this.environment.manualTime:getTimePeriod();
    this.atmosphereParams=atmosphereFor({
      period,
      weatherKind:resolveWeatherKind(this.environment,this.weather),
      season:this.environment.season,
      quietMode:this.environment.quietMode,
      reducedMotion:this.motionPreference?.matches ?? false,
      quality:this.environment.quality ?? this.settings.quality,
    });
    const target=this.atmosphereParams.light,mix=1-Math.exp(-dt*2.8);
    for(let i=0;i<3;i++)this.light[i]+=(target[i]-this.light[i])*mix;
    this.cloud+=(this.atmosphereParams.cloud-this.cloud)*mix;
    this.fog+=(this.atmosphereParams.fog-this.fog)*mix;
    const u=this.waterFilter.resources.pondUniforms.uniforms;
    u.uTime=this.time;u.uLight=new Float32Array(this.light);u.uCloud=this.cloud;u.uFog=this.fog;
    const last=this.ripples.at(-1);
    u.uRipple=last?new Float32Array([last.x/this.host.clientWidth,last.y/this.host.clientHeight,this.time-last.at,1]):
      new Float32Array([0,0,4,0]);
  }
  renderSurface() {
    const g=this.surface;g.clear();
    if(this.arrival){
      const fish=this.world.fish.find(f=>f.id===this.arrival.id);
      const age=this.time-this.arrival.at;
      if(!fish||age>=5){
        this.arrival=null;this.arrivalLabel.hidden=true;
      }else{
        const x=Math.max(100,Math.min(this.world.width-100,fish.x));
        const y=Math.max(18,fish.y-fish.length*.75-28);
        this.arrivalLabel.style.left=`${x}px`;this.arrivalLabel.style.top=`${y}px`;
        this.arrivalLabel.style.opacity=String(Math.min(1,(5-age)*2));
        const radius=fish.length*.62;
        g.ellipse(fish.x,fish.y,radius,radius*.65).stroke({
          color:0xf7efd4,width:1.3,alpha:.45*Math.min(1,5-age),
        });
      }
    }
    for(const food of this.world.food){
      const r=Math.max(1.3,this.world.height/600);
      g.circle(food.x+1,food.y+2,r).fill({color:0x183f2c,alpha:.25});
      g.circle(food.x,food.y,r).fill({color:0xddb879,alpha:Math.min(1,(12-food.age)/2)});
    }
    this.ripples=this.ripples.filter(r=>this.time-r.at<3);
    for(const r of this.ripples){
      const age=this.time-r.at;
      for(let i=0;i<3;i++){
        const radius=age*28-i*8;
        if(radius<0)continue;
        g.ellipse(r.x,r.y,radius+2,radius*.65+2).stroke({color:0xe2edcf,width:.8,alpha:(1-age/3)*.26});
      }
    }
    for(const fish of this.world.fish){
      if(fish.swimSpeed<6)continue;
      const x=fish.x-Math.cos(fish.angle)*fish.length*.4;
      const y=fish.y-Math.sin(fish.angle)*fish.length*.4;
      g.moveTo(x,y).lineTo(x-Math.cos(fish.angle)*5,y-Math.sin(fish.angle)*5)
        .stroke({color:0xddebc9,width:.8,alpha:.08});
    }
  }
  renderAtmosphere() {
    const g=this.atmosphere;g.clear();
    const w=this.host.clientWidth,h=this.host.clientHeight,b=this.world.habitat;
    const kind=resolveWeatherKind(this.environment,this.weather);
    if(kind==="rain"||kind==="storm"){
      for(let i=0;i<(kind==="storm"?62:36);i++){
        const x=(i*137.31+this.time*33)%w,y=(i*79.7+this.time*285)%h;
        g.moveTo(x,y).lineTo(x-3,y+11).stroke({color:0xdde5dc,width:.8,alpha:.16});
        const rx=b.left+((i*.618)%1)*(b.right-b.left),ry=b.top+((i*.414)%1)*(b.bottom-b.top);
        const age=(this.time*.7+i*.137)%1;
        g.ellipse(rx,ry,age*12+1,age*5+1).stroke({color:0xcbe0cf,width:.7,alpha:(1-age)*.13});
      }
    }
    if(kind==="snow")for(let i=0;i<28;i++){
      const x=(i*103.1+Math.sin(this.time*.5+i)*12+w)%w,y=(i*59.7+this.time*17)%h;
      g.circle(x,y,1+i%2*.5).fill({color:0xf0f4ed,alpha:.48});
    }
    const period=this.environment.timeMode==="manual"?this.environment.manualTime:getTimePeriod();
    if(period==="night"&&kind!=="rain"&&kind!=="storm"){
      for(let i=0;i<9;i++){
        const x=(i%2 ? .86:.12)*w+Math.sin(this.time*.18+i*3)*w*.065;
        const y=(.2+(i/9)*.6)*h+Math.cos(this.time*.3+i)*8;
        const pulse=Math.max(0,Math.sin(this.time*1.1+i*2));
        g.circle(x,y,1.2).fill({color:0xddeaa1,alpha:pulse*.68});
      }
    }
  }
}
