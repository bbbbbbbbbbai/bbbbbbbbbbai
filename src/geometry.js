export function bendVertices(base, out, width, time, phase, amplitude) {
  for (let i = 0; i < base.length; i += 2) {
    const t = base[i] / width;
    out[i] = base[i];
    out[i + 1] = base[i + 1] + Math.sin(time * 5 + phase - t * 4.6) * (1 - t) ** 2 * amplitude;
  }
}

export function artworkTransform(head, tail, width, height) {
  return {
    angle: -Math.atan2((head.y - tail.y) * height, (head.x - tail.x) * width),
    cx: (head.x + tail.x) * width / 2,
    cy: (head.y + tail.y) * height / 2,
  };
}

export function paddleVertices(base, out, width, height, phase, resting) {
  for(let i=0;i<base.length;i+=2){
    const x=base[i]/width,y=base[i+1]/height;
    const outsideShell=Math.max(0,(Math.abs(y-.5)-.32)/.18);
    const foot=x>.18 && x<.8 ? outsideShell : 0;
    const swing=resting ? 0 : Math.sin(phase*2.2+(y<.5 ? 0 : Math.PI)+(x<.5 ? Math.PI : 0));
    out[i]=base[i]+swing*width*.024*foot;
    out[i+1]=base[i+1]+swing*height*.018*foot;
  }
}
