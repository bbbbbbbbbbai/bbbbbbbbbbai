import sharp from 'sharp';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

const rawDir = new URL('../output/imagegen/sunburst/', import.meta.url);
const outDir = new URL('../public/assets/sunburst/', import.meta.url);
await mkdir(outDir, { recursive: true });
const jobs = ['kohaku','ogon','showa','shiro','goldfish','carp','turtle','lily','lotus'];
const records = [];
for (const name of jobs) {
  const source = await readFile(new URL(`${name}-top.png`,rawDir));
  const {data,info} = await sharp(source).ensureAlpha().raw().toBuffer({resolveWithObject:true});
  let left=info.width,top=info.height,right=0,bottom=0;
  for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++){
    const i=(y*info.width+x)*4;
    if(data[i+3]<20)data[i+3]=0;
    if(data[i+3]>32){left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y);}
  }
  if(right<=left || bottom<=top)throw new Error(`Empty image: ${name}`);
  const clean=await sharp(data,{raw:info})
    .extract({left,top,width:right-left+1,height:bottom-top+1})
    .resize({width:512,height:512,fit:'inside',withoutEnlargement:true})
    .extend({top:12,bottom:12,left:12,right:12,background:{r:0,g:0,b:0,alpha:0}})
    .modulate({saturation:.88}).png().toBuffer();
  await writeFile(new URL(`${name}.png`,outDir),clean);
  const shadow=await sharp(clean).raw().toBuffer({resolveWithObject:true});
  for(let i=0;i<shadow.data.length;i+=4){
    shadow.data[i]=22;shadow.data[i+1]=43;shadow.data[i+2]=35;
  }
  await sharp(shadow.data,{raw:shadow.info}).blur(3).png()
    .toFile(fileURLToPath(new URL(`${name}-shadow.png`,outDir)));
  records.push({asset:name,source:`output/imagegen/sunburst/${name}-top.png`,sha256:createHash('sha256').update(source).digest('hex')});
}
const bed=new URL('../output/imagegen/pond-bed-sunburst.png',import.meta.url);
await sharp(await readFile(bed)).webp({quality:92}).toFile(fileURLToPath(new URL('pond-bed.webp',outDir)));
await writeFile(new URL('provenance.json',outDir),JSON.stringify({
  model:'gpt-image-2.5-sunburst',provider:'Quya',
  prompts:'output/imagegen/sunburst/topdown-prompts.json',
  processing:'Alpha trimming, proportional resizing, slight saturation adjustment and baked silhouette shadows. Original generated files retained.',
  background:'output/imagegen/pond-bed-sunburst.png',assets:records,
},null,2));
console.log(`Prepared ${jobs.length} generated sprites, their shadows and pond background.`);
