import { artworkTransform } from "./geometry.js";

export function paintStrokes(canvas, strokes) {
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0,0,canvas.width,canvas.height);
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  for (const s of strokes) {
    ctx.globalCompositeOperation = s.mode === "erase" ? "destination-out" : "source-over";
    ctx.strokeStyle = ctx.fillStyle = s.color;
    ctx.lineWidth = s.width * canvas.width;
    ctx.beginPath();
    const [x,y] = s.points[0];
    ctx.moveTo(x*canvas.width,y*canvas.height);
    if (s.points.length === 1) {
      ctx.arc(x*canvas.width,y*canvas.height,ctx.lineWidth/2,0,Math.PI*2);
      ctx.fill();
    } else {
      for (const [px,py] of s.points.slice(1)) ctx.lineTo(px*canvas.width,py*canvas.height);
      ctx.stroke();
    }
  }
  ctx.globalCompositeOperation = "source-over";
}

export function bakeArtwork(drawing) {
  const source = document.createElement("canvas");
  source.width=960;source.height=540;
  paintStrokes(source,drawing.strokes);
  const rotated = document.createElement("canvas");
  rotated.width=rotated.height=1500;
  const ctx=rotated.getContext("2d",{willReadFrequently:true});
  const t=artworkTransform(drawing.head,drawing.tail,source.width,source.height);
  ctx.translate(750,750);ctx.rotate(t.angle);ctx.translate(-t.cx,-t.cy);
  ctx.drawImage(source,0,0);
  const pixels=ctx.getImageData(0,0,1500,1500).data;
  let minX=1500,minY=1500,maxX=0,maxY=0;
  for (let y=0;y<1500;y++) for(let x=0;x<1500;x++) {
    if (pixels[(y*1500+x)*4+3]>8) {
      minX=Math.min(minX,x);maxX=Math.max(maxX,x);
      minY=Math.min(minY,y);maxY=Math.max(maxY,y);
    }
  }
  if (minX>maxX) return null;
  const w=maxX-minX+1,h=maxY-minY+1,scale=Math.min(1,512/Math.max(w,h));
  const result=document.createElement("canvas");
  result.width=Math.ceil(w*scale)+32;result.height=Math.ceil(h*scale)+32;
  result.getContext("2d").drawImage(rotated,minX,minY,w,h,16,16,w*scale,h*scale);
  return result;
}

export function previewFrame(canvas, image, time) {
  const ctx=canvas.getContext("2d");
  const w=canvas.width,h=canvas.height;
  ctx.clearRect(0,0,w,h);
  ctx.fillStyle="#89a99a";ctx.fillRect(0,0,w,h);
  ctx.strokeStyle="#eaf3da20";ctx.lineWidth=1;
  for(let i=0;i<8;i++) {
    ctx.beginPath();
    for(let x=0;x<=w;x+=16) {
      const y=i*90+Math.sin(x/130+time*.2+i)*17;
      x?ctx.lineTo(x,y):ctx.moveTo(x,y);
    }
    ctx.stroke();
  }
  if(!image) return;
  const width=Math.min(w*.57,h*.65*image.width/image.height);
  const height=width*image.height/image.width;
  ctx.save();
  ctx.translate(w/2+Math.sin(time*.3)*28,h/2+Math.sin(time*.55)*7);
  ctx.rotate(Math.sin(time*.4)*.05);
  for(let i=0;i<32;i++){
    const t=i/32,next=(i+1)/32;
    const y=Math.sin(time*5-t*4.6)*(1-t)**2*width*.055;
    const ny=Math.sin(time*5-next*4.6)*(1-next)**2*width*.055;
    ctx.save();
    ctx.transform(1,(ny-y)/(width/32),0,1,-width/2+t*width,-height/2+y);
    ctx.drawImage(image,t*image.width,0,image.width/32+1,image.height,0,0,width/32+1,height);
    ctx.restore();
  }
  ctx.restore();
}
