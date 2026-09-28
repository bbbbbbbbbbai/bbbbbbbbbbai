import { test, expect } from "@playwright/test";
import sharp from "sharp";

const assetResponses=new WeakMap();
const renderErrors=new WeakMap();

async function draw(page) {
  const b = await page.locator("#drawing").boundingBox();
  // Begin on the canvas, not on the draggable tail handle.
  await page.mouse.move(b.x+b.width*.3, b.y+b.height*.5);
  await page.mouse.down();
  for (const [x,y] of [[.35,.32],[.6,.29],[.8,.5],[.6,.7],[.35,.68],[.3,.5]]) {
    await page.mouse.move(b.x+b.width*x,b.y+b.height*y,{steps:5});
  }
  await page.mouse.up();
}
test.beforeEach(async ({page}) => {
  const loaded=[];
  assetResponses.set(page,loaded);
  const errors=[];
  renderErrors.set(page,errors);
  page.on("pageerror",error=>errors.push(error.message));
  page.on("console",message=>{
    if(message.type()==="error"||/INVALID_OPERATION|Could not initialize shader/.test(message.text())){
      errors.push(message.text());
    }
  });
  page.context().on("response",response=>{
    if(response.ok()&&response.url().includes("/assets/"))loaded.push(response.url());
  });
  await page.addInitScript(()=>{
    Object.defineProperty(navigator,"geolocation",{configurable:true,value:{
      getCurrentPosition(success,failure){failure({code:1,message:"Test location disabled"});}
    }});
  });
  await page.goto("/");
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await expect(page.locator("body")).toHaveAttribute("data-ready","true");
});

test.afterEach(async ({page})=>{
  expect(renderErrors.get(page)).toEqual([]);
});

test("draw, preview, release, reload, edit and delete a fish", async ({page}) => {
  await page.getByRole("button",{name:"画一条鱼",exact:true}).click();
  await draw(page);
  await page.getByLabel("小鱼名字").fill("我的红锦鲤");
  await page.getByRole("button",{name:"预览游动",exact:true}).click();
  await expect(page.locator("#preview-canvas")).toBeVisible();
  await page.getByRole("button",{name:"放入鱼塘",exact:true}).click();
  await expect(page.locator("#editor-dialog")).not.toBeVisible();
  await page.reload();
  await page.getByRole("button",{name:"我的小鱼",exact:true}).click();
  await expect(page.locator("#gallery").getByText("我的红锦鲤",{exact:true})).toBeVisible();
  await page.getByRole("button",{name:"编辑 我的红锦鲤"}).click();
  await page.getByLabel("小鱼名字").fill("新的名字");
  await page.getByRole("button",{name:"保存修改"}).click();
  await page.getByRole("button",{name:"我的小鱼",exact:true}).click();
  await expect(page.locator("#gallery").getByText("新的名字",{exact:true})).toBeVisible();
  await page.getByRole("button",{name:"删除 新的名字"}).click();
  await page.getByRole("button",{name:"确认删除",exact:true}).click();
  await expect(page.locator("#gallery").getByText("新的名字",{exact:true})).not.toBeVisible();
});

test("pond clicks feed, drags do not, and editor history is functional", async ({page}) => {
  const viewport=page.viewportSize();
  const feedPoint={x:Math.min(650,viewport.width-40),y:Math.min(400,viewport.height-80)};
  const dragStart={x:Math.min(550,viewport.width-90),y:Math.min(350,viewport.height-120)};
  const dragEnd={x:Math.min(750,viewport.width-25),y:Math.min(430,viewport.height-45)};
  await page.mouse.click(feedPoint.x,feedPoint.y);
  await expect(page.locator("#pond")).toHaveAttribute("data-feeds","1");
  await page.mouse.move(dragStart.x,dragStart.y);
  await page.mouse.down();
  await page.mouse.move(dragEnd.x,dragEnd.y,{steps:12});
  await page.mouse.up();
  await expect(page.locator("#pond")).toHaveAttribute("data-feeds","1");
  await page.getByRole("button",{name:"画一条鱼",exact:true}).click();
  await draw(page);
  await page.getByRole("button",{name:"撤销",exact:true}).click();
  await expect(page.getByRole("button",{name:"放入鱼塘",exact:true})).toBeDisabled();
  await page.getByRole("button",{name:"重做",exact:true}).click();
  await expect(page.getByRole("button",{name:"放入鱼塘",exact:true})).toBeEnabled();
  await expect(page.locator("#pond")).toHaveAttribute("data-feeds","1");
});

test("feeding works across the whole canvas while settings clicks never feed", async ({page},testInfo) => {
  await page.route("**/src/main.js*",async route=>{
    const response=await route.fetch();
    await route.fulfill({response,body:`${await response.text()}\nwindow.__feedingScene=scene;`});
  });
  await page.reload();
  await expect(page.locator("body")).toHaveAttribute("data-ready","true");
  const {width:w,height:h}=page.viewportSize();
  const points=[[16,h*.3],[w-16,h*.3],[w*.5,16],[w*.5,h-16],
    [16,h-80],[w-16,h-80],[w*.18,h*.39],[w*.81,h*.69]];
  let count=0,nextFeedAt=0;
  for(const [x,y] of points){
    await expect.poll(()=>page.evaluate(()=>window.__feedingScene.time)).toBeGreaterThanOrEqual(nextFeedAt);
    await page.mouse.click(x,y);
    await expect(page.locator("#pond")).toHaveAttribute("data-feeds",String(++count));
    nextFeedAt=await page.evaluate(()=>window.__feedingScene.time+.15);
  }
  await page.getByRole("button",{name:"鱼塘设置",exact:true}).click();
  await page.getByRole("heading",{name:"鱼塘设置",exact:true}).click();
  await page.getByRole("button",{name:"关闭设置",exact:true}).click();
  await expect(page.locator("#pond")).toHaveAttribute("data-feeds",String(count));
  await page.screenshot({path:`artifacts/full-canvas-feeding-${testInfo.project.name}.png`});
});

test("pond draws real assets and moves; desktop screenshot", async ({page},testInfo) => {
  const errors=[];
  page.on("pageerror",e=>errors.push(e.message));
  await page.getByRole("button",{name:"鱼塘设置",exact:true}).click();
  await page.locator('[data-time-mode="manual"]').click();
  await page.locator('[data-time-period="day"]').click();
  await page.getByRole("button",{name:"关闭设置",exact:true}).click();
  await page.waitForTimeout(1800);
  const before=await page.locator("#pond canvas").screenshot();
  await page.waitForTimeout(350);
  const after=await page.locator("#pond canvas").screenshot();
  expect(before.equals(after)).toBe(false);
  const stats=await sharp(after).stats();
  expect(stats.channels[0].stdev).toBeGreaterThan(8);
  expect(stats.channels[1].mean).toBeGreaterThan(65);
  expect(errors).toEqual([]);
  await page.screenshot({path:`artifacts/pond-${testInfo.project.name}.png`});
});

test("generated art is loaded and day-night lighting changes actual canvas pixels", async ({page},testInfo) => {
  const assets=assetResponses.get(page);
  expect(assets.some(url=>url.includes("/assets/sunburst/pond-bed.webp"))).toBe(true);
  expect(assets.some(url=>url.includes("/assets/sunburst/turtle.png"))).toBe(true);
  await page.getByRole("button",{name:"鱼塘设置",exact:true}).click();
  await page.locator('[data-time-mode="manual"]').click();
  await page.locator('[data-time-period="day"]').click();
  await page.getByRole("button",{name:"关闭设置",exact:true}).click();
  await page.waitForTimeout(1800);
  const day=await page.locator("#pond canvas").screenshot();
  await page.getByRole("button",{name:"鱼塘设置",exact:true}).click();
  await page.locator('[data-time-period="night"]').click();
  await page.getByRole("button",{name:"关闭设置",exact:true}).click();
  await page.waitForTimeout(1800);
  const night=await page.locator("#pond canvas").screenshot();
  const a=await sharp(day).stats(),b=await sharp(night).stats();
  expect(b.channels[1].mean).toBeLessThan(a.channels[1].mean*.85);
  expect(b.channels[1].stdev).toBeGreaterThan(10);
  await page.screenshot({path:`artifacts/pond-night-${testInfo.project.name}.png`});
  await page.getByRole("button",{name:"鱼塘设置",exact:true}).click();
  await page.locator('[data-time-period="day"]').click();
  await page.getByRole("button",{name:"关闭设置",exact:true}).click();
  await page.waitForTimeout(1800);
  await page.screenshot({path:`artifacts/pond-day-${testInfo.project.name}.png`});
});

test("settings persist and narrow viewport editor has no overflow", async ({page}) => {
  await page.getByRole("button",{name:"鱼塘设置",exact:true}).click();
  await page.getByLabel("内置鱼数量").fill("16");
  await page.getByLabel("内置鱼数量").dispatchEvent("change");
  await page.reload();
  await page.getByRole("button",{name:"鱼塘设置",exact:true}).click();
  await expect(page.getByLabel("内置鱼数量")).toHaveValue("16");
  await page.getByRole("button",{name:"关闭设置",exact:true}).click();
  await page.setViewportSize({width:390,height:844});
  await page.getByRole("button",{name:"画一条鱼",exact:true}).click();
  await draw(page);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  const b=await page.getByRole("button",{name:"放入鱼塘",exact:true}).boundingBox();
  expect(b.y+b.height).toBeLessThanOrEqual(844);
  await page.screenshot({path:"artifacts/editor-mobile.png"});
});

test("manual atmosphere controls override local weather and preserve fish interaction", async ({page}) => {
  await page.route("**/src/main.js*",async route=>{
    const response=await route.fetch();
    await route.fulfill({response,body:`${await response.text()}\nwindow.__atmosphereScene=scene;`});
  });
  await page.reload();
  await expect(page.locator("body")).toHaveAttribute("data-ready","true");
  await page.getByRole("button",{name:"鱼塘设置",exact:true}).click();
  await page.locator("#weather-mode").selectOption("rain");
  await page.locator("#season-mode").selectOption("autumn");
  await page.locator("#quiet-mode").check();
  await expect(page.locator("#atmosphere-status")).toContainText("雨");
  await expect.poll(()=>page.evaluate(()=>window.__atmosphereScene.atmosphereParams.rainIntensity)).toBeGreaterThan(0);
  await expect.poll(()=>page.evaluate(()=>window.__pondDiagnostics.weather)).toBe("rain");
  await page.getByRole("button",{name:"关闭设置",exact:true}).click();
  await page.mouse.click(80,80);
  await expect(page.locator("#pond")).toHaveAttribute("data-feeds","1");
});

test("reduced motion keeps core fish and feeding available", async ({page}) => {
  await page.emulateMedia({reducedMotion:"reduce"});
  await page.goto("/");
  await expect(page.locator("body")).toHaveAttribute("data-ready","true");
  await page.mouse.click(120,120);
  await expect(page.locator("#pond")).toHaveAttribute("data-feeds","1");
});

test("live fish turn away from corners and lily-covered banks", async ({page},testInfo) => {
  // Expose the actual scene only in this test response, including Vite HMR imports.
  await page.route("**/src/main.js*",async route=>{
    const response=await route.fetch();
    await route.fulfill({response,body:`${await response.text()}\nwindow.__shorelineScene=scene;`});
  });
  await page.reload();
  await expect(page.locator("body")).toHaveAttribute("data-ready","true");
  const result=await page.evaluate(async()=>{
    const scene=window.__shorelineScene;
    const pond=scene.world,b=pond.habitat,frame=scene.frame;
    const poses=[
      [b.left,b.top,-Math.PI*.75],[b.right,b.top,-Math.PI*.25],
      [b.left,b.bottom,Math.PI*.75],[b.right,b.bottom,Math.PI*.25],
      [b.left,frame.y+frame.height*.39,Math.PI],
      [b.right,frame.y+frame.height*.69,0],
    ];
    const tracked=pond.fish.slice(0,6).map((fish,i)=>{
      const [x,y,angle]=poses[i];
      Object.assign(fish,{x,y,angle});
      return {fish,x,y};
    });
    const start=scene.time;
    return new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>{
        scene.app.ticker.remove(inspect);
        reject(new Error("Live shoreline simulation did not finish"));
      },20000);
      const inspect=()=>{
        if(scene.time-start>=5){
          clearTimeout(timer);
          scene.app.ticker.remove(inspect);
          resolve(tracked.map(({fish,x,y})=>({
            distance:Math.hypot(fish.x-x,fish.y-y)/fish.length,
            clearance:Math.min(fish.x-b.left,b.right-fish.x,fish.y-b.top,b.bottom-fish.y)/fish.length,
          })));
        }
      };
      scene.app.ticker.add(inspect);
    });
  });
  for(const fish of result){
    expect(fish.distance).toBeGreaterThan(.6);
    expect(fish.clearance).toBeGreaterThan(.15);
  }
  await page.screenshot({path:`artifacts/shoreline-recovery-${testInfo.project.name}.png`});
});

test("time atmosphere supports automatic and manual modes", async ({page}) => {
  await page.getByRole("button",{name:"鱼塘设置",exact:true}).click();
  await expect(page.locator('[data-time-mode="auto"]')).toHaveAttribute("aria-pressed","true");
  await expect(page.locator('[data-time-period="night"]')).toBeDisabled();
  await page.locator('[data-time-mode="manual"]').click();
  await page.locator('[data-time-period="night"]').click();
  await expect(page.locator('[data-time-mode="manual"]')).toHaveAttribute("aria-pressed","true");
  await expect(page.locator('[data-time-period="night"]')).toHaveAttribute("aria-pressed","true");
  await page.reload();
  await page.getByRole("button",{name:"鱼塘设置",exact:true}).click();
  await expect(page.locator('[data-time-mode="manual"]')).toHaveAttribute("aria-pressed","true");
  await expect(page.locator('[data-time-period="night"]')).toHaveAttribute("aria-pressed","true");
  await expect(page.locator("#weather-status")).not.toHaveText("定位中…");
});

test("storage failure retains the current drawing", async ({page}) => {
  await page.getByRole("button",{name:"画一条鱼",exact:true}).click();
  await draw(page);
  await page.evaluate(()=>{Storage.prototype.setItem=()=>{throw new Error("denied");};});
  await page.getByRole("button",{name:"放入鱼塘",exact:true}).click();
  await expect(page.locator("#editor-dialog")).toBeVisible();
  await expect(page.locator("#editor-status")).toContainText("保存失败");
});

test("automatic time hides manual choices and keeps the current period consistent", async ({page}) => {
  await page.clock.setFixedTime(new Date(2026,0,1,23,0));
  await page.getByRole("button",{name:"鱼塘设置",exact:true}).click();
  await expect(page.locator("#time-output")).toHaveText("夜晚");
  await expect(page.locator("#manual-time-controls")).not.toBeVisible();
  await page.locator('[data-time-mode="manual"]').click();
  await expect(page.locator("#manual-time-controls")).toBeVisible();
  await page.locator('[data-time-period="dusk"]').click();
  await expect(page.locator("#time-output")).toHaveText("黄昏");
  await page.locator('[data-time-mode="auto"]').click();
  await expect(page.locator("#time-output")).toHaveText("夜晚");
  await expect(page.locator("#manual-time-controls")).not.toBeVisible();
});

test("drawing handles drag and support keyboard movement without adding strokes", async ({page}) => {
  await page.getByRole("button",{name:"画一条鱼",exact:true}).click();
  const head=page.getByRole("button",{name:"鱼头位置",exact:true});
  await expect(head).toBeVisible();
  const canvas=await page.locator("#drawing").boundingBox();
  const start=await head.boundingBox();
  await page.mouse.move(start.x+start.width/2,start.y+start.height/2);
  await page.mouse.down();
  await page.mouse.move(canvas.x+canvas.width*.7,canvas.y+canvas.height*.3,{steps:6});
  await page.mouse.up();
  const moved=await head.getAttribute("style");
  expect(parseFloat(await head.evaluate(el=>el.style.top))).toBeCloseTo(30,0);
  await head.press("ArrowRight");
  expect(await head.getAttribute("style")).not.toEqual(moved);
  const saved=await head.getAttribute("style");
  await expect(page.locator("#stroke-indicator")).toHaveText("0 笔");
  await page.getByRole("button",{name:"关闭画板",exact:true}).click();
  await page.reload();
  await page.getByRole("button",{name:"画一条鱼",exact:true}).click();
  await expect(head).toHaveAttribute("style",saved);
});

test("compact controls have comfortable targets and legible form labels", async ({page},testInfo) => {
  await page.getByRole("button",{name:"画一条鱼",exact:true}).click();
  for(const selector of ["#close-editor","#undo","#redo","#palette button","#pen","#eraser"]){
    for(const control of await page.locator(selector).all()){
      const b=await control.boundingBox();
      expect(b.width).toBeGreaterThanOrEqual(43);
      expect(b.height).toBeGreaterThanOrEqual(43);
    }
  }
  expect(await page.locator(".field-label").first().evaluate(el=>parseFloat(getComputedStyle(el).fontSize)))
    .toBeGreaterThanOrEqual(14);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:`artifacts/ux-editor-${testInfo.project.name}.png`});
});

test("new artwork arrives with a visible temporary name marker", async ({page},testInfo) => {
  await page.getByRole("button",{name:"画一条鱼",exact:true}).click();
  await draw(page);
  await page.getByLabel("小鱼名字").fill("水中的第一笔");
  await page.getByRole("button",{name:"放入鱼塘",exact:true}).click();
  await expect(page.locator(".arrival-marker")).toBeVisible();
  await expect(page.locator(".arrival-marker")).toHaveText("水中的第一笔");
  await page.screenshot({path:`artifacts/ux-arrival-${testInfo.project.name}.png`});
  await expect(page.locator(".arrival-marker")).not.toBeVisible({timeout:12000});
  await page.reload();
  await expect(page.locator(".arrival-marker")).not.toBeVisible();
});

test("loading errors offer a retry that preserves saved settings", async ({page}) => {
  await page.getByRole("button",{name:"鱼塘设置",exact:true}).click();
  await page.getByLabel("内置鱼数量").fill("16");
  await page.getByLabel("内置鱼数量").dispatchEvent("change");
  let failLoad=true;
  await page.route("**/src/main.js*",async route=>{
    const response=await route.fetch();
    const source=await response.text();
    await route.fulfill({response,headers:{...response.headers(),"cache-control":"no-store"},
      body:failLoad?source.replace("await scene.init();",'throw new Error("Asset unavailable (test)");'):source});
  });
  await page.reload();
  const retry=page.getByRole("button",{name:"重新加载",exact:true});
  await expect(retry).toBeVisible();
  await expect(page.locator("#loading")).toHaveAttribute("role","alert");
  const errors=renderErrors.get(page);
  expect(errors.some(error=>error.includes("Asset unavailable (test)"))).toBe(true);
  errors.splice(0,errors.length,...errors.filter(error=>!error.includes("Asset unavailable (test)")));
  failLoad=false;
  await retry.click();
  await expect(page.locator("body")).toHaveAttribute("data-ready","true");
  await expect(page.locator("#loading")).not.toBeVisible();
  await expect(page.locator("#pond canvas")).toHaveCount(1);
  await page.getByRole("button",{name:"鱼塘设置",exact:true}).click();
  await expect(page.getByLabel("内置鱼数量")).toHaveValue("16");
});
