import "./style.css";
import { createIcons, Paintbrush, Fish, SlidersHorizontal, Maximize, X, Plus, Pencil, Play, LocateFixed, Locate, Undo2, Redo2, Eraser, Trash2, ArrowUpRight, RotateCcw } from "lucide";
import { createDefaultDocument, createRepository } from "./model.js";
import { createDefaultEnvironment, createEnvironmentRepository, getTimePeriod } from "./environment.js";
import { defaultAtmosphere } from "./atmosphere.js";
import { fetchLocalWeather } from "./weather.js";
import { PondWorld } from "./world.js";
import { PondScene } from "./scene.js";
import { createEditor } from "./editor.js";
import { bakeArtwork } from "./drawing.js";

const icons={Paintbrush,Fish,SlidersHorizontal,Maximize,X,Plus,Pencil,Play,LocateFixed,Locate,Undo2,Redo2,Eraser,Trash2,ArrowUpRight,RotateCcw};
const refreshIcons=()=>createIcons({icons});
const $=s=>document.querySelector(s);
refreshIcons();
let toastTimer;
function toast(message){
  $("#toast").textContent=message;$("#toast").hidden=false;
  clearTimeout(toastTimer);toastTimer=setTimeout(()=>$("#toast").hidden=true,3800);
}
const repository=createRepository({
  getItem:key=>localStorage.getItem(key),setItem:(key,value)=>localStorage.setItem(key,value),removeItem:key=>localStorage.removeItem(key),
});
const loaded=repository.load();
let documentData=loaded.ok?loaded.data:createDefaultDocument();
if(!loaded.ok)toast(loaded.error);
const environmentRepository=createEnvironmentRepository({
  getItem:key=>localStorage.getItem(key),setItem:(key,value)=>localStorage.setItem(key,value),removeItem:key=>localStorage.removeItem(key),
});
const environmentLoaded=environmentRepository.load();
let environment=environmentLoaded.ok?environmentLoaded.data:createDefaultEnvironment();
let weatherState={kind:"clear",label:"等待当地天气",temperature:null};
const world=new PondWorld(innerWidth,innerHeight,documentData.settings);
const scene=new PondScene($("#pond"),world,documentData.settings);
const periodLabels={dawn:"清晨",day:"白天",dusk:"黄昏",night:"夜晚"};
const weatherLabels={clear:"晴天",cloud:"阴天",rain:"雨天",fog:"雾天",snow:"雪天",storm:"暴雨"};
const seasonLabels={spring:"春",summer:"夏",autumn:"秋",winter:"冬"};
function environmentToUI(){
  const activePeriod=environment.timeMode==="auto"?getTimePeriod():environment.manualTime;
  $("#time-output").textContent=periodLabels[activePeriod];
  for(const button of document.querySelectorAll("[data-time-mode]")){
    button.setAttribute("aria-pressed",String(button.dataset.timeMode===environment.timeMode));
  }
  for(const button of document.querySelectorAll("[data-time-period]")){
    button.setAttribute("aria-pressed",String(button.dataset.timePeriod===activePeriod));
    button.disabled=environment.timeMode!=="manual";
  }
  $("#manual-time-controls").hidden=environment.timeMode!=="manual";
  const temperature=Number.isFinite(weatherState.temperature)?` · ${Math.round(weatherState.temperature)}°`:"";
  $("#weather-status").textContent=`${weatherState.label}${temperature}`;
  const weatherMode=environment.weatherMode==="manual"?environment.weatherKind:"local";
  $("#weather-mode").value=weatherMode;
  $("#season-mode").value=environment.season??"summer";
  $("#quiet-mode").checked=Boolean(environment.quietMode);
  $("#quality-mode").value=environment.quality??documentData.settings.quality;
  $("#atmosphere-status").textContent=`${weatherMode==="local"?(weatherState.kind?weatherLabels[weatherState.kind]:"当地天气"):(weatherLabels[weatherMode]??"晴天")} · ${seasonLabels[environment.season??"summer"]}${environment.quietMode?" · 安静":""}`;
}
function applyEnvironment(){
  scene.setEnvironment(environment,weatherState);
  environmentToUI();
}
function saveEnvironment(next){
  const result=environmentRepository.save(next);
  if(result.ok){environment=result.data;applyEnvironment();}
  else toast(result.error);
  return result;
}
let weatherBusy=false;
async function refreshWeather(showToast=true){
  if(weatherBusy)return;
  weatherBusy=true;
  $("#refresh-weather").disabled=true;
  $("#weather-status").textContent="定位中…";
  try{
    weatherState=await fetchLocalWeather();
    environment={...environment,weatherMode:"local",weatherKind:weatherState.kind};
    environmentRepository.save(environment);
    applyEnvironment();
    if(showToast)toast(`已更新当地天气：${weatherState.label}`);
  }catch{
    weatherState={kind:"clear",label:"默认晴天",temperature:null};
    applyEnvironment();
    if(showToast)toast("无法获取当地天气，已使用默认晴天");
  }finally{
    weatherBusy=false;
    $("#refresh-weather").disabled=false;
    environmentToUI();
  }
}
function saveDocument(next){
  const result=repository.save(next);
  if(result.ok){documentData=result.data;$("#save-state").textContent="已保存"; }
  else {$("#save-state").textContent="保存失败";toast(result.error);}
  return result;
}
function updateCount(){
  $("#fish-count").textContent=`${documentData.settings.count+documentData.works.length} 尾`;
  $("#work-badge").textContent=documentData.works.length;$("#work-badge").hidden=!documentData.works.length;
  $("#gallery-count").textContent=`${documentData.works.length} / 20`;
}
const editor=createEditor({
  getDocument:()=>documentData,saveDocument,
  onWorksChanged(works,edited,work){
    scene.setArtworks(works);updateCount();renderGallery();
    scene.welcomeFish(work.id,work.name,{relocate:!edited});
    toast(edited?"小鱼已更新":"你的小鱼入池了");
  },
});
function closePanels(){
  $("#gallery").hidden=true;$("#settings").hidden=true;
  $("#open-gallery").setAttribute("aria-expanded","false");
  $("#open-settings").setAttribute("aria-expanded","false");
}
$("#new-fish").addEventListener("click",()=>{closePanels();editor.open();});
$("#gallery-new").addEventListener("click",()=>{closePanels();editor.open();});
$("#open-gallery").addEventListener("click",()=>{
  const opening=$("#gallery").hidden;closePanels();$("#gallery").hidden=!opening;
  $("#open-gallery").setAttribute("aria-expanded",String(opening));
  if(opening){renderGallery();$("#close-gallery").focus();}
});
$("#close-gallery").addEventListener("click",()=>{closePanels();$("#open-gallery").focus();});
$("#open-settings").addEventListener("click",()=>{
  const opening=$("#settings").hidden;closePanels();$("#settings").hidden=!opening;
  $("#open-settings").setAttribute("aria-expanded",String(opening));
  if(opening){environmentToUI();$("#close-settings").focus();refreshWeather(false);}
});
$("#close-settings").addEventListener("click",()=>{closePanels();$("#open-settings").focus();});
$("#fullscreen").addEventListener("click",async()=>{
  try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}
  catch{toast("当前窗口无法进入全屏");}
});
document.addEventListener("fullscreenchange",()=>{
  const active=Boolean(document.fullscreenElement);
  $("#fullscreen").setAttribute("aria-label",active?"退出全屏":"全屏");
  $("#fullscreen").dataset.tip=active?"退出全屏":"全屏";
});
let deletingId=null;
function renderGallery(){
  $("#gallery-list").replaceChildren();
  $("#gallery-empty").hidden=Boolean(documentData.works.length);
  for(const work of documentData.works){
    const article=document.createElement("article");article.className="work";
    const image=document.createElement("img");image.className="work-preview";image.alt=work.name;
    image.src=bakeArtwork(work)?.toDataURL()??"";
    const name=document.createElement("div");name.className="work-caption";name.textContent=work.name;name.title=work.name;
    const actions=document.createElement("div");actions.className="work-actions";
    const edit=document.createElement("button");edit.className="tool";edit.setAttribute("aria-label",`编辑 ${work.name}`);edit.innerHTML='<i data-lucide="pencil"></i>';
    edit.addEventListener("click",()=>{closePanels();editor.open(work);});
    const remove=document.createElement("button");remove.className="tool";remove.setAttribute("aria-label",`删除 ${work.name}`);remove.innerHTML='<i data-lucide="trash-2"></i>';
    remove.addEventListener("click",()=>{deletingId=work.id;$("#confirm-name").textContent=work.name;$("#confirm-dialog").showModal();});
    actions.append(edit,remove);article.append(image,name,actions);$("#gallery-list").append(article);
  }
  refreshIcons();updateCount();
}
$("#cancel-delete").addEventListener("click",()=>{$("#confirm-dialog").close();deletingId=null;});
$("#confirm-delete").addEventListener("click",()=>{
  const next={...documentData,works:documentData.works.filter(w=>w.id!==deletingId)};
  const result=saveDocument(next);
  if(!result.ok)return;
  scene.setArtworks(next.works);$("#confirm-dialog").close();deletingId=null;renderGallery();toast("小鱼已移除");
});
function settingsToUI(){
  const s=documentData.settings;
  for(const key of ["count","speed","water"])$(`#setting-${key}`).value=s[key];
  $("#count-output").textContent=s.count;$("#speed-output").textContent=`${s.speed.toFixed(1)}×`;$("#water-output").textContent=`${Math.round(s.water*100)}%`;
  for(const b of document.querySelectorAll("[data-quality]"))b.setAttribute("aria-pressed",String(b.dataset.quality===s.quality));
}
for(const key of ["count","speed","water"]){
  $(`#setting-${key}`).addEventListener("input",e=>{
    const value=Number(e.target.value),next={...documentData.settings,[key]:value};
    scene.configure(next);
    if(key==="count")$("#count-output").textContent=value;
    if(key==="speed")$("#speed-output").textContent=`${value.toFixed(1)}×`;
    if(key==="water")$("#water-output").textContent=`${Math.round(value*100)}%`;
  });
  $(`#setting-${key}`).addEventListener("change",e=>{
    const result=saveDocument({...documentData,settings:{...documentData.settings,[key]:Number(e.target.value)}});
    if(!result.ok)scene.configure(documentData.settings);
    settingsToUI();updateCount();
  });
}
for(const b of document.querySelectorAll("[data-quality]"))b.addEventListener("click",()=>{
  const next={...documentData,settings:{...documentData.settings,quality:b.dataset.quality}};
  if(saveDocument(next).ok)scene.configure(next.settings);
  saveEnvironment({...environment,quality:b.dataset.quality});
  settingsToUI();
});
for(const button of document.querySelectorAll("[data-time-mode]"))button.addEventListener("click",()=>{
  saveEnvironment({...environment,timeMode:button.dataset.timeMode});
});
for(const button of document.querySelectorAll("[data-time-period]"))button.addEventListener("click",()=>{
  saveEnvironment({...environment,timeMode:"manual",manualTime:button.dataset.timePeriod});
});
$("#refresh-weather").addEventListener("click",()=>refreshWeather(true));
$("#weather-mode").addEventListener("change",e=>{
  const value=e.target.value;
  saveEnvironment({...environment,weatherMode:value==="local"?"local":"manual",weatherKind:value==="local"?(weatherState.kind??"clear"):value});
});
$("#season-mode").addEventListener("change",e=>saveEnvironment({...environment,season:e.target.value}));
$("#quiet-mode").addEventListener("change",e=>saveEnvironment({...environment,quietMode:e.target.checked}));
$("#quality-mode").addEventListener("change",e=>{
  const quality=e.target.value;
  const next={...documentData,settings:{...documentData.settings,quality}};
  if(saveDocument(next).ok)scene.configure(next.settings);
  saveEnvironment({...environment,quality});
});
$("#reset-settings").addEventListener("click",()=>{
  const next={...documentData,settings:createDefaultDocument().settings};
  if(saveDocument(next).ok)scene.configure(next.settings);settingsToUI();updateCount();
  saveEnvironment({...defaultAtmosphere(), version:1});
});
settingsToUI();updateCount();environmentToUI();
setInterval(()=>{if(environment.timeMode==="auto")environmentToUI();},60000);

let gesture=null,feeds=0;
$("#pond").addEventListener("pointerdown",e=>{
  if(e.button!==0)return;
  gesture={x:e.clientX,y:e.clientY,at:performance.now(),drag:false};
});
$("#pond").addEventListener("pointermove",e=>{
  world.disturb(e.clientX,e.clientY);
  if(gesture&&Math.hypot(e.clientX-gesture.x,e.clientY-gesture.y)>7)gesture.drag=true;
});
$("#pond").addEventListener("pointerup",e=>{
  const g=gesture;gesture=null;
  if(e.button!==0||!g||g.drag||performance.now()-g.at>500||Math.hypot(e.clientX-g.x,e.clientY-g.y)>7)return;
  if(scene.feed(e.clientX,e.clientY)){$("#pond").dataset.feeds=String(++feeds);}
});
$("#pond").addEventListener("pointerleave",()=>gesture=null);
window.addEventListener("blur",()=>gesture=null);
document.addEventListener("keydown",e=>{
  if(e.key!=="Escape")return;
  const opener=!$("#settings").hidden?$("#open-settings"):!$("#gallery").hidden?$("#open-gallery"):null;
  closePanels();opener?.focus();
});

try{
  await scene.init();
  scene.setArtworks(documentData.works);scene.configure(documentData.settings);applyEnvironment();
  $("#loading").hidden=true;document.body.dataset.ready="true";
  refreshWeather(false);
}catch(error){
  console.error(error);
  $("#loading").replaceChildren();
  $("#loading").setAttribute("role","alert");
  document.body.dataset.ready="false";
  const text=document.createElement("p");text.textContent="鱼塘暂时无法加载，请刷新页面重试。";
  if(/webgl|renderer|context/i.test(error?.message??"")){
    text.textContent="当前浏览器无法启用 WebGL 鱼塘渲染，请开启硬件加速后重试。";
  }else if(/asset|load|image|texture/i.test(error?.message??"")){
    text.textContent="池塘素材加载失败，请检查本地资源后重试。";
  }
  const retry=document.createElement("button");
  retry.type="button";retry.className="submit-button";retry.id="retry-loading";
  retry.innerHTML='<i data-lucide="rotate-ccw"></i>重新加载';
  retry.addEventListener("click",()=>{
    retry.disabled=true;retry.textContent="正在重试…";location.reload();
  });
  $("#loading").append(text,retry);refreshIcons();retry.focus();
}
