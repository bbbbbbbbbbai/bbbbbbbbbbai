import { readFile, writeFile, mkdir, access } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import sharp from 'sharp';

const prompts = JSON.parse(await readFile(new URL('./ecology-prompts.json', import.meta.url), 'utf8'));
const rawDir = new URL('../output/imagegen/ecology/', import.meta.url);
const outDir = new URL('../public/assets/ecology/', import.meta.url);
const key = process.env.IMAGE_MODEL_API_KEY;
if (!key) throw new Error('IMAGE_MODEL_API_KEY is required');
await mkdir(rawDir, {recursive:true});
await mkdir(outDir, {recursive:true});
const records = [];
for (const [name, subject] of Object.entries(prompts.subjects)) {
  const rawPath = new URL(`${name}.png`, rawDir);
  let source;
  try { await access(rawPath); source = await readFile(rawPath); } catch {
    console.log(`Generating ${name}`);
    const response = await fetch('https://api.quya.org/v1/responses', {
      method:'POST',
      headers:{Authorization:`Bearer ${key}`, 'Content-Type':'application/json'},
      body:JSON.stringify({model:'gpt-image-2.5-sunburst', input:`${prompts.style}\n${subject}`, tools:[{type:'image_generation'}]}),
      signal:AbortSignal.timeout(300000),
    });
    if (!response.ok) throw new Error(`Image API HTTP ${response.status} for ${name}`);
    const payload = await response.json();
    const image = payload.output?.find(item => item.type === 'image_generation_call')?.result;
    const encoded = typeof image === 'string' ? image : image?.b64_json ?? image?.base64 ?? image?.data;
    if (!encoded) throw new Error(`No image in response for ${name}`);
    source = Buffer.from(encoded.replace(/^data:image\/[^;]+;base64,/, ''), 'base64');
    await writeFile(rawPath, source);
  }
  const {data,info} = await sharp(source).ensureAlpha().raw().toBuffer({resolveWithObject:true});
  let transparent = 0;
  let left=info.width, top=info.height, right=-1, bottom=-1;
  for(let y=0;y<info.height;y++) for(let x=0;x<info.width;x++){
    const alpha=data[(y*info.width+x)*4+3];
    if(alpha<20) transparent++;
    if(alpha>32){left=Math.min(left,x);top=Math.min(top,y);right=Math.max(right,x);bottom=Math.max(bottom,y);}
  }
  if(transparent<info.width*info.height*.05) throw new Error(`Nontransparent image for ${name}; inspect raw file`);
  const clean=await sharp(source).extract({left,top,width:right-left+1,height:bottom-top+1})
    .resize({width:640,height:640,fit:'inside',withoutEnlargement:true})
    .extend({top:10,bottom:10,left:10,right:10,background:{r:0,g:0,b:0,alpha:0}}).png().toBuffer();
  await writeFile(new URL(`${name}.png`,outDir),clean);
  const shadow=await sharp(clean).raw().toBuffer({resolveWithObject:true});
  for(let i=0;i<shadow.data.length;i+=4){shadow.data[i]=22;shadow.data[i+1]=43;shadow.data[i+2]=35;}
  await writeFile(new URL(`${name}-shadow.png`,outDir),await sharp(shadow.data,{raw:shadow.info}).blur(3).png().toBuffer());
  records.push({name,sha256:createHash('sha256').update(source).digest('hex')});
  await writeFile(new URL('provenance.json',outDir),JSON.stringify({
    provider:'Quya',model:'gpt-image-2.5-sunburst',prompts:'scripts/ecology-prompts.json',
    processing:'Alpha bounds trim, proportional resize and separate baked shadows',assets:records,
  },null,2));
  console.log(`Prepared ${name}`);
}
