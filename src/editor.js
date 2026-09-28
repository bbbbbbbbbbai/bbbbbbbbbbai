import { createHistory, createDefaultDocument } from "./model.js";
import { paintStrokes, bakeArtwork, previewFrame } from "./drawing.js";

export function createEditor({getDocument,saveDocument,onWorksChanged}) {
  const $=s=>document.querySelector(s),dialog=$("#editor-dialog"),canvas=$("#drawing");
  let history=createHistory(),strokes=[],current=null,draft=null,editingId=null;
  let mode="draw",color="#d6503e",mark=null,preview=false,image=null,previewTime=0;
  let anchorDrag=null;
  let clearTimer;
  const colors=["#d6503e","#e8b659","#f6f4e6","#27493e","#759590","#91b6ba","#c795ac","#6d748a","#98ad72","#975744"];
  const colorNames=["朱红","金黄","米白","墨绿","青灰","湖蓝","藕粉","靛灰","草绿","赭石"];
  for(const [index,value]of colors.entries()){
    const swatch=document.createElement("button");
    swatch.className="swatch";swatch.style.setProperty("--color",value);
    swatch.setAttribute("aria-label",colorNames[index]);swatch.title=colorNames[index];
    swatch.setAttribute("aria-pressed",String(index===0));
    swatch.addEventListener("click",()=>chooseColor(value));swatch.dataset.color=value;
    $("#palette").append(swatch);
  }
  function chooseColor(value){
    color=value;$("#custom-color").value=value;
    for(const button of $("#palette").children)button.setAttribute("aria-pressed",String(button.dataset.color===value));
    mode="draw";mark=null;updateModes();
  }
  function updateModes(){
    $("#pen").setAttribute("aria-pressed",String(mode==="draw"));
    $("#eraser").setAttribute("aria-pressed",String(mode==="erase"));
    $("#mark-head").setAttribute("aria-pressed",String(mark==="head"));
    $("#mark-tail").setAttribute("aria-pressed",String(mark==="tail"));
  }
  function readDraft(){
    return {name:$("#fish-name").value,strokes:history.getStrokes(),head:{...draft.head},tail:{...draft.tail}};
  }
  function persistDraft(){
    if(!draft)return;
    const result=saveDocument({...getDocument(),draft:readDraft()});
    $("#editor-status").textContent=result.ok?"草稿已保存":result.error;
  }
  function redraw(){
    paintStrokes(canvas,current?[...strokes,current]:strokes);
    $("#undo").disabled=!history.canUndo;$("#redo").disabled=!history.canRedo;
    $("#release").disabled=!strokes.some(s=>s.mode==="draw");
    $("#stroke-indicator").textContent=`${strokes.length} 笔`;
    for(const key of ["head","tail"]){
      $(`#${key}-marker`).style.left=`${draft[key].x*100}%`;
      $(`#${key}-marker`).style.top=`${draft[key].y*100}%`;
    }
  }
  function showDraw(){
    preview=false;$("#draw-wrap").hidden=false;$("#preview-wrap").hidden=true;
    $("#tab-draw").setAttribute("aria-selected","true");$("#tab-preview").setAttribute("aria-selected","false");
  }
  function finish(){
    if(!current)return;
    try{strokes=history.push(current);}catch(error){$("#editor-status").textContent=error.message;}
    current=null;redraw();persistDraft();
  }
  function position(event){
    const r=canvas.getBoundingClientRect();
    return [Math.max(0,Math.min(1,(event.clientX-r.left)/r.width)),Math.max(0,Math.min(1,(event.clientY-r.top)/r.height))];
  }
  function moveAnchor(key,x,y){
    x=Math.max(0,Math.min(1,x));y=Math.max(0,Math.min(1,y));
    const opposite=key==="head"?draft.tail:draft.head;
    if(Math.hypot(x-opposite.x,y-opposite.y)<.08){
      $("#editor-status").textContent="鱼头和鱼尾需要分开一点";return false;
    }
    draft[key]={x,y};redraw();return true;
  }
  function finishAnchor(cancel=false){
    if(!anchorDrag)return;
    if(cancel)draft[anchorDrag.key]=anchorDrag.origin;
    anchorDrag=null;redraw();persistDraft();
  }
  for(const key of ["head","tail"]){
    const handle=$(`#${key}-marker`);
    handle.addEventListener("pointerdown",event=>{
      if(event.button!==0)return;
      finish();mark=null;updateModes();
      anchorDrag={key,pointerId:event.pointerId,origin:{...draft[key]}};
      handle.setPointerCapture(event.pointerId);event.preventDefault();
      handle.focus({preventScroll:true});
    });
    handle.addEventListener("pointermove",event=>{
      if(anchorDrag?.key!==key||anchorDrag.pointerId!==event.pointerId)return;
      const [x,y]=position(event);moveAnchor(key,x,y);
    });
    handle.addEventListener("pointerup",()=>finishAnchor());
    handle.addEventListener("pointercancel",()=>finishAnchor(true));
    handle.addEventListener("lostpointercapture",()=>finishAnchor());
    handle.addEventListener("keydown",event=>{
      const direction={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]}[event.key];
      if(!direction)return;
      event.preventDefault();const step=event.shiftKey?.05:.01;
      if(moveAnchor(key,draft[key].x+direction[0]*step,draft[key].y+direction[1]*step))persistDraft();
    });
  }
  canvas.addEventListener("pointerdown",event=>{
    if(event.button!==0)return;
    const [x,y]=position(event);
    if(mark){
      if(!moveAnchor(mark,x,y))return;
      mark=null;updateModes();persistDraft();return;
    }
    if(strokes.length>=400){$("#editor-status").textContent="笔画已达到上限";return;}
    canvas.setPointerCapture(event.pointerId);
    current={mode,color,width:Number($("#brush-width").value)/960,points:[[x,y]]};
    redraw();event.preventDefault();
  });
  canvas.addEventListener("pointermove",event=>{
    if(!current)return;
    if(current.points.length>=5000){finish();return;}
    const p=position(event),last=current.points.at(-1);
    if(Math.hypot(p[0]-last[0],p[1]-last[1])>.001)current.points.push(p);
    redraw();
  });
  canvas.addEventListener("pointerup",finish);
  canvas.addEventListener("pointercancel",finish);
  canvas.addEventListener("lostpointercapture",finish);
  $("#undo").addEventListener("click",()=>{finish();strokes=history.undo();redraw();persistDraft();});
  $("#redo").addEventListener("click",()=>{finish();strokes=history.redo();redraw();persistDraft();});
  $("#pen").addEventListener("click",()=>{mode="draw";mark=null;updateModes();});
  $("#eraser").addEventListener("click",()=>{mode="erase";mark=null;updateModes();});
  $("#custom-color").addEventListener("input",e=>chooseColor(e.target.value));
  $("#brush-width").addEventListener("input",e=>{$("#brush-output").textContent=e.target.value;});
  $("#fish-name").addEventListener("change",persistDraft);
  for(const key of ["head","tail"])$(`#mark-${key}`).addEventListener("click",()=>{showDraw();mark=mark===key?null:key;updateModes();});
  $("#tab-draw").addEventListener("click",showDraw);
  $("#tab-preview").addEventListener("click",()=>{
    finish();image=bakeArtwork(readDraft());preview=true;previewTime=0;
    $("#draw-wrap").hidden=true;$("#preview-wrap").hidden=false;
    $("#tab-draw").setAttribute("aria-selected","false");$("#tab-preview").setAttribute("aria-selected","true");
    if(!image)$("#editor-status").textContent="画布里还没有可见的图案";
  });
  $("#clear").addEventListener("click",()=>{
    if(!strokes.length)return;
    if(!clearTimer){
      $("#clear span").textContent="确认清空";
      clearTimer=setTimeout(()=>{clearTimer=null;$("#clear span").textContent="清空画布";},3000);
      return;
    }
    clearTimeout(clearTimer);clearTimer=null;$("#clear span").textContent="清空画布";
    finish();strokes=history.clear();redraw();persistDraft();showDraw();
  });
  function close(){
    finishAnchor();finish();persistDraft();dialog.close();preview=false;
  }
  $("#close-editor").addEventListener("click",close);
  dialog.addEventListener("cancel",e=>{e.preventDefault();close();});
  $("#release").addEventListener("click",()=>{
    finish();
    const drawing=readDraft();
    if(!bakeArtwork(drawing)){$("#editor-status").textContent="画布里还没有可见的图案";return;}
    const doc=getDocument();
    if(!editingId&&doc.works.length>=20){$("#editor-status").textContent="已拥有 20 条小鱼，请先移除一条";return;}
    const previous=doc.works.find(w=>w.id===editingId);
    const now=Date.now();
    const work={
      ...drawing,id:editingId??crypto.randomUUID(),name:drawing.name.trim()||"未命名的小鱼",
      createdAt:previous?.createdAt??now,updatedAt:now,
    };
    const works=editingId?doc.works.map(w=>w.id===editingId?work:w):[...doc.works,work];
    const next={...doc,works,draft:createDefaultDocument().draft};
    const result=saveDocument(next);
    if(!result.ok){$("#editor-status").textContent=result.error;return;}
    onWorksChanged(works,Boolean(editingId),work);dialog.close();preview=false;
  });
  let last=0;
  function tick(now){
    requestAnimationFrame(tick);
    if(!preview||!dialog.open||document.hidden){last=now;return;}
    previewTime+=Math.min((now-last)/1000,.05);last=now;
    previewFrame($("#preview-canvas"),image,previewTime);
  }
  requestAnimationFrame(tick);
  return {
    open(work=null){
      const initial=work??getDocument().draft;
      editingId=work?.id??null;
      draft={head:{...initial.head},tail:{...initial.tail}};
      history=createHistory(initial.strokes);strokes=history.getStrokes();current=null;
      anchorDrag=null;
      $("#fish-name").value=initial.name;
      $("#editor-title").textContent=work?"编辑小鱼":"画一条鱼";
      $("#release span").textContent=work?"保存修改":"放入鱼塘";
      $("#editor-status").textContent=work?"原来的小鱼会保留在鱼塘中":"草稿自动保存在本机";
      mark=null;updateModes();showDraw();redraw();dialog.showModal();
    },
  };
}
