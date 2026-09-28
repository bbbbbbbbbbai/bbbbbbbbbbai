import sharp from "sharp";
import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const outputDir = fileURLToPath(new URL("../public/assets/", import.meta.url));
await mkdir(outputDir, { recursive: true });

let seed = 21761;
const random = () => ((seed = seed * 16807 % 2147483647) - 1) / 2147483646;
const range = (a, b) => a + (b - a) * random();
const pick = (items) => items[Math.floor(random() * items.length)];
const svg = (w, h, body) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${body}</svg>`;
const raster = async (name, source, webp = false) => {
  const image = sharp(Buffer.from(source));
  await (webp ? image.webp({ quality: 94 }) : image.png()).toFile(`${outputDir}/${name}`);
};

function smoothShape(points) {
  let d = `M${(points[0][0] + points.at(-1)[0]) / 2},${(points[0][1] + points.at(-1)[1]) / 2}`;
  points.forEach((point, index) => {
    const next = points[(index + 1) % points.length];
    d += ` Q${point[0]},${point[1]} ${(point[0] + next[0]) / 2},${(point[1] + next[1]) / 2}`;
  });
  return `${d}Z`;
}

function irregularStone(radius, squish = 1) {
  const points = Array.from({ length: 9 }, (_, index) => {
    const angle = index * Math.PI * 2 / 9;
    const r = radius * range(.72, 1.28);
    return [Math.cos(angle) * r * squish, Math.sin(angle) * r];
  });
  return smoothShape(points);
}

function bladePath(length, lean, width) {
  const bend = range(-width, width);
  return `M0 0 Q${lean * .25} ${-length * .42} ${lean + bend} ${-length} Q${lean + width} ${-length * .46} 0 0Z`;
}

function addGrass(target, x, y, scale = 1, tone = "#3e6e5a") {
  let grass = `<g transform="translate(${x} ${y}) scale(${scale})" opacity="${range(.45, .8).toFixed(2)}">`;
  const count = Math.floor(range(5, 10));
  for (let i = 0; i < count; i++) {
    const angle = range(-1.05, .35);
    const length = range(42, 130);
    const lean = Math.sin(angle) * length;
    grass += `<path d="${bladePath(length, lean, range(4, 10))}" fill="${i % 3 === 0 ? "#78936a" : tone}" opacity="${range(.48, .88).toFixed(2)}" transform="rotate(${range(-24, 24)})"/>`;
  }
  return `${target}${grass}</g>`;
}

const floorDefs = `<defs>
  <linearGradient id="water" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#709c91"/><stop offset=".42" stop-color="#78a89a"/><stop offset="1" stop-color="#5f8f85"/></linearGradient>
  <radialGradient id="openWater" cx=".5" cy=".48" r=".7"><stop stop-color="#a3c1a8" stop-opacity=".36"/><stop offset=".58" stop-color="#7da99a" stop-opacity=".1"/><stop offset="1" stop-color="#375f5d" stop-opacity=".34"/></radialGradient>
  <radialGradient id="stone" cx=".28" cy=".18"><stop stop-color="#c8cfb5"/><stop offset=".4" stop-color="#a1b39b"/><stop offset=".82" stop-color="#6e8d7e"/><stop offset="1" stop-color="#486d66"/></radialGradient>
  <linearGradient id="sand" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#d6cfaa" stop-opacity=".18"/><stop offset="1" stop-color="#857f63" stop-opacity=".05"/></linearGradient>
  <filter id="waterTexture" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".012 .025" numOctaves="4" seed="41" result="noise"/><feColorMatrix in="noise" type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope=".16"/></feComponentTransfer><feBlend in="SourceGraphic" mode="soft-light"/></filter>
  <filter id="soften"><feGaussianBlur stdDeviation="3.5"/></filter>
  <filter id="stoneSoft"><feGaussianBlur stdDeviation="1.2"/></filter>
</defs>`;

let bed = `<rect width="2560" height="1440" fill="url(#water)"/>
  <rect width="2560" height="1440" fill="url(#openWater)"/>
  <path d="M0 340C330 225 570 280 818 360C1100 452 1288 420 1540 314C1830 193 2168 202 2560 346L2560 560C2180 430 1890 449 1615 540C1324 637 1065 612 784 504C510 398 269 407 0 520Z" fill="#a4c6a8" opacity=".09" filter="url(#soften)"/>
  <path d="M0 1080C306 980 596 1009 842 1113C1124 1232 1414 1205 1683 1088C1944 974 2245 960 2560 1080V1439H0Z" fill="#315f5d" opacity=".1" filter="url(#soften)"/>
  <path d="M0 690C260 603 500 624 746 704C992 784 1186 809 1440 731C1708 649 2010 568 2560 678" fill="none" stroke="#d0d6b1" stroke-width="95" opacity=".055" filter="url(#soften)"/>
  <path d="M0 1165C290 1030 568 1062 832 1175C1040 1264 1228 1295 1472 1215C1730 1130 2000 1014 2560 1122L2560 1440H0Z" fill="url(#sand)" opacity=".8"/>`;

const sandRibbons = [
  "M-80 220C250 88 536 104 784 250C1016 386 1092 520 1290 530C1510 540 1690 338 1924 236C2152 137 2360 155 2640 270L2640 368C2380 274 2168 280 1970 370C1740 473 1548 670 1285 650C1044 632 936 472 720 362C488 243 246 246-80 374Z",
  "M-70 1175C232 1014 487 1007 728 1110C1014 1231 1142 1370 1404 1325C1704 1275 1814 1068 2086 1009C2308 960 2472 1011 2630 1086L2630 1230C2430 1150 2250 1134 2080 1191C1810 1280 1650 1444 1385 1444C1110 1444 956 1300 704 1224C472 1154 232 1170-70 1310Z",
];
for (const ribbon of sandRibbons) bed += `<path d="${ribbon}" fill="#d2c99f" opacity=".095" filter="url(#soften)"/>`;

const stoneZones = [
  { x: 70, y: 110, w: 360, h: 560, count: 47 },
  { x: 2250, y: 90, w: 380, h: 620, count: 48 },
  { x: 90, y: 1125, w: 520, h: 365, count: 53 },
  { x: 2050, y: 1128, w: 580, h: 360, count: 60 },
  { x: 1160, y: 20, w: 280, h: 190, count: 17 },
];
let stones = "";
for (const zone of stoneZones) {
  for (let i = 0; i < zone.count; i++) {
    const x = zone.x + range(-80, zone.w + 80);
    const y = zone.y + range(-70, zone.h + 70);
    const radius = range(12, 58) * (random() < .08 ? 1.55 : 1);
    const d = irregularStone(radius, range(.72, 1.38));
    stones += `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${range(0, 180).toFixed(1)})" opacity="${range(.32, .7).toFixed(2)}">
      <path d="${d}" transform="translate(5 10)" fill="#264e50" opacity=".34" filter="url(#stoneSoft)"/>
      <path d="${d}" fill="url(#stone)" stroke="#57796e" stroke-width="${range(.7, 2.2).toFixed(1)}"/>
      <path d="M${(-radius * .58).toFixed(1)} ${(-radius * .24).toFixed(1)}Q${(-radius * .1).toFixed(1)} ${(-radius * .77).toFixed(1)} ${(radius * .54).toFixed(1)} ${(-radius * .38).toFixed(1)}" fill="none" stroke="#e1dfc0" stroke-width="${range(.8, 2.4).toFixed(1)}" opacity=".45"/>
      ${random() > .52 ? `<path d="M${(-radius * .43).toFixed(1)} ${(radius * .38).toFixed(1)}Q0 ${(radius * .02).toFixed(1)} ${(radius * .38).toFixed(1)} ${(-radius * .29).toFixed(1)}" fill="none" stroke="#4c756b" stroke-width="${range(.7, 1.5).toFixed(1)}" opacity=".65"/>` : ""}
      ${random() > .72 ? `<circle cx="${range(-radius * .3, radius * .3).toFixed(1)}" cy="${range(-radius * .2, radius * .3).toFixed(1)}" r="${range(1, 3).toFixed(1)}" fill="#d7d3ad" opacity=".48"/>` : ""}
    </g>`;
  }
}
bed += `<g>${stones}</g>`;

let pebbles = "";
for (let i = 0; i < 180; i++) {
  const side = i % 4;
  const x = side === 0 ? range(110, 480) : side === 1 ? range(2080, 2460) : range(360, 2200);
  const y = side === 0 || side === 1 ? range(260, 1180) : side === 2 ? range(24, 180) : range(1260, 1420);
  const rx = range(3, 16);
  const ry = rx * range(.55, 1.2);
  pebbles += `<ellipse cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" rx="${rx.toFixed(1)}" ry="${ry.toFixed(1)}" transform="rotate(${range(0, 180).toFixed(1)} ${x.toFixed(1)} ${y.toFixed(1)})" fill="${pick(["#839a87", "#aab39a", "#6a8980", "#c4c1a0"])}" opacity="${range(.22, .48).toFixed(2)}"/>`;
}
bed += `<g>${pebbles}</g>`;

let grasses = "";
for (const point of [
  [102, 310, 1.1], [220, 965, .86], [370, 1270, 1.18], [2390, 330, 1.04],
  [2260, 920, .8], [2445, 1195, 1.2], [530, 90, .8], [1980, 84, .72],
]) {
  grasses = addGrass(grasses, ...point, point[0] < 1200 ? "#4e785f" : "#456f5b");
}
bed += grasses;

function distantPad(x, y, scale, rotate, tint) {
  return `<g transform="translate(${x} ${y}) rotate(${rotate}) scale(${scale})" opacity=".46">
    <path d="M0 0C-50-54-130-92-175-74C-212-59-214-18-184 20C-143 73-69 83 0 0Z" fill="${tint}" stroke="#718b68" stroke-width="3"/>
    <path d="M0 0L-176-47M0 0L-119-76M0 0L-50-83M0 0L-184 22" stroke="#aab387" stroke-width="2" opacity=".55"/>
    <path d="M0 0L-14-42" stroke="#d1cda1" stroke-width="2" opacity=".3"/>
  </g>`;
}
bed += distantPad(372, 260, 1.04, -20, "#718a5d");
bed += distantPad(2192, 294, .82, 22, "#617f59");
bed += distantPad(220, 1040, .72, 155, "#6a825d");
bed += distantPad(2365, 1054, 1.05, 178, "#71865e");
bed += `<g opacity=".31">
  <path d="M445 214C410 165 420 107 449 68C458 125 459 165 445 214ZM470 214C474 147 516 100 558 74C531 135 505 180 470 214ZM2170 240C2132 177 2144 119 2176 80C2186 142 2184 193 2170 240ZM2200 242C2215 170 2260 131 2300 112C2274 176 2242 216 2200 242Z" fill="#517c63"/>
  <path d="M447 210L448 73M469 209L552 80M2171 236L2175 86M2201 237L2296 118" stroke="#b5bf8e" stroke-width="2" opacity=".7"/>
</g>`;

let ripples = "";
for (let i = 0; i < 22; i++) {
  const x = range(430, 2140);
  const y = range(250, 1210);
  const width = range(90, 330);
  ripples += `<path d="M${(x - width / 2).toFixed(1)} ${y.toFixed(1)}Q${x.toFixed(1)} ${(y - range(8, 26)).toFixed(1)} ${(x + width / 2).toFixed(1)} ${(y + range(-4, 18)).toFixed(1)}" fill="none" stroke="${pick(["#d6d7b8", "#bdd0aa", "#466f6b"])}" stroke-width="${range(1.4, 4).toFixed(1)}" opacity="${range(.045, .12).toFixed(2)}"/>`;
}
let flecks = "";
for (let i = 0; i < 150; i++) {
  const x = range(320, 2240);
  const y = range(180, 1290);
  flecks += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${range(.7, 2.8).toFixed(1)}" fill="${pick(["#e1dec0", "#426d68", "#c1d1b0"])}" opacity="${range(.08, .23).toFixed(2)}"/>`;
}
bed += `<g>${ripples}${flecks}</g>
  <rect width="2560" height="1440" fill="transparent" filter="url(#waterTexture)"/>
  <rect x="30" y="30" width="2500" height="1380" rx="220" fill="none" stroke="#d1d5b5" stroke-width="44" opacity=".035" filter="url(#soften)"/>`;
await raster("pond-bed.webp", svg(2560, 1440, floorDefs + bed), true);

function leaf(variant) {
  const rotation = variant ? -5 : 4;
  const points = [];
  for (let i = 0; i <= 80; i++) {
    const angle = .22 + i / 80 * (Math.PI * 2 - .44);
    const wobble = Math.sin(angle * 7 + variant * 1.7) * 4 + Math.sin(angle * 15) * 2;
    const radius = 199 + wobble;
    points.push([256 + Math.cos(angle) * radius, 256 + Math.sin(angle) * radius * (.92 + variant * .025)]);
  }
  const path = `M256 256L${points.map((point) => point.join(",")).join("L")}Z`;
  const veinColors = variant ? ["#a9b57f", "#879b6b", "#d0ca97"] : ["#b0b783", "#7d9a68", "#cbc89a"];
  let details = "";
  for (let i = 0; i < 25; i++) {
    const angle = .26 + i / 24 * (Math.PI * 2 - .52);
    const dx = Math.cos(angle);
    const dy = Math.sin(angle);
    const endX = 256 + dx * range(170, 202);
    const endY = 256 + dy * range(160, 192);
    const bendX = 256 + dx * 76 - dy * range(10, 28);
    const bendY = 256 + dy * 76 + dx * range(10, 28);
    details += `<path d="M255 256Q${bendX.toFixed(1)} ${bendY.toFixed(1)} ${endX.toFixed(1)} ${endY.toFixed(1)}" fill="none" stroke="${veinColors[i % veinColors.length]}" stroke-width="${i % 3 ? 1.2 : 2.1}" opacity="${i % 3 ? .31 : .4}"/>`;
    if (i % 2 === 0) {
      for (let j = 1; j < 4; j++) {
        const d = j * 43;
        const px = 256 + dx * d;
        const py = 256 + dy * d;
        details += `<path d="M${px.toFixed(1)} ${py.toFixed(1)}q${(-dy * 12 + dx * 27).toFixed(1)} ${(dx * 12 + dy * 27).toFixed(1)} ${(-dy * 20 + dx * 43).toFixed(1)} ${(dx * 20 + dy * 43).toFixed(1)}" fill="none" stroke="${veinColors[(i + 1) % veinColors.length]}" stroke-width=".8" opacity=".2"/>`;
      }
    }
  }
  let marks = "";
  for (let i = 0; i < 26; i++) {
    const angle = range(0, Math.PI * 2);
    const r = range(40, 185);
    const x = 256 + Math.cos(angle) * r;
    const y = 256 + Math.sin(angle) * r * .92;
    marks += `<ellipse cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" rx="${range(3, 12).toFixed(1)}" ry="${range(2, 7).toFixed(1)}" transform="rotate(${range(0, 180).toFixed(1)} ${x.toFixed(1)} ${y.toFixed(1)})" fill="${pick(["#b2ae78", "#718a59", "#d1c995", "#516f52"])}" opacity="${range(.05, .16).toFixed(2)}"/>`;
  }
  return svg(512, 512, `<defs>
    <radialGradient id="leaf" cx=".36" cy=".26"><stop stop-color="${variant ? "#8d9d69" : "#879b69"}"/><stop offset=".48" stop-color="${variant ? "#6d8658" : "#71895a"}"/><stop offset=".82" stop-color="#4f704e"/><stop offset="1" stop-color="#405f48"/></radialGradient>
    <linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#bcc18a" stop-opacity=".64"/><stop offset=".5" stop-color="#829866" stop-opacity=".28"/><stop offset="1" stop-color="#d3c895" stop-opacity=".55"/></linearGradient>
    <filter id="leafTexture" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence baseFrequency=".038" numOctaves="4" seed="${variant + 14}" result="noise"/><feColorMatrix in="noise" type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope=".26"/></feComponentTransfer><feComposite in2="SourceGraphic" operator="in" result="clipped"/><feBlend in="SourceGraphic" in2="clipped" mode="soft-light"/></filter>
    <clipPath id="leafClip"><path d="${path}"/></clipPath>
  </defs>
  <g transform="rotate(${rotation} 256 256)">
    <path d="${path}" transform="translate(2 8)" fill="#274e43" opacity=".34"/>
    <path d="${path}" fill="url(#leaf)" stroke="url(#rim)" stroke-width="3" filter="url(#leafTexture)"/>
    <g clip-path="url(#leafClip)">${marks}</g>
    ${details}
    <path d="M256 256L439 216" stroke="#e1d8a2" stroke-width="2" opacity=".38"/>
    <path d="M256 256L437 216" stroke="#536e4d" stroke-width="4" opacity=".16"/>
    <circle cx="256" cy="256" r="7" fill="#c6c189" opacity=".72"/>
    <circle cx="254" cy="254" r="2.5" fill="#ede6bb" opacity=".58"/>
  </g>`);
}
await raster("lily-a.png", leaf(0));
await raster("lily-b.png", leaf(1));

let flower = `<defs>
  <linearGradient id="petalOuter" x1="0" y1="1" x2=".6" y2="0"><stop stop-color="#bd6d86"/><stop offset=".44" stop-color="#e3a3b1"/><stop offset="1" stop-color="#fff1ed"/></linearGradient>
  <linearGradient id="petalInner" x1="0" y1="1" x2=".4" y2="0"><stop stop-color="#d98298"/><stop offset=".62" stop-color="#f1c4c8"/><stop offset="1" stop-color="#fff8ee"/></linearGradient>
  <radialGradient id="center" cx=".35" cy=".3"><stop stop-color="#ffe7a9"/><stop offset="1" stop-color="#c48c50"/></radialGradient>
  <filter id="petalSoft"><feGaussianBlur stdDeviation=".18"/></filter>
</defs>`;
for (let layer = 0; layer < 4; layer++) {
  const count = [15, 13, 10, 7][layer];
  for (let i = 0; i < count; i++) {
    const rotation = i * 360 / count + layer * 17 + range(-4, 4);
    const length = [112, 96, 76, 53][layer];
    const width = [33, 30, 25, 19][layer];
    const fill = layer > 1 ? "petalInner" : "petalOuter";
    flower += `<g transform="translate(160 164) rotate(${rotation.toFixed(1)})" opacity="${(.82 + layer * .04).toFixed(2)}" filter="url(#petalSoft)">
      <path d="M0 18C${(-width * 1.08).toFixed(1)} ${(-length * .02).toFixed(1)} ${(-width * .86).toFixed(1)} ${(-length * .64).toFixed(1)} 0 ${(-length).toFixed(1)}C${(width * .82).toFixed(1)} ${(-length * .62).toFixed(1)} ${(width * 1.02).toFixed(1)} ${(-length * .06).toFixed(1)} 0 18Z" fill="url(#${fill})" stroke="#a95f7b" stroke-opacity=".3" stroke-width="1"/>
      <path d="M0 12Q${(-width * .14).toFixed(1)} ${(-length * .38).toFixed(1)} 0 ${(-length * .88).toFixed(1)}" stroke="#fff8ef" stroke-width="1.5" fill="none" opacity=".53"/>
      <path d="M0 15Q${(width * .16).toFixed(1)} ${(-length * .34).toFixed(1)} 0 ${(-length * .74).toFixed(1)}" stroke="#c87991" stroke-width=".9" fill="none" opacity=".36"/>
    </g>`;
  }
}
flower += `<ellipse cx="160" cy="164" rx="19" ry="16" fill="url(#center)" stroke="#b47c4d" stroke-width="1.2"/>`;
for (let i = 0; i < 32; i++) {
  const angle = i * 2.4;
  const radius = 4 + (i % 7) * 1.55;
  flower += `<circle cx="${(160 + Math.cos(angle) * radius).toFixed(1)}" cy="${(164 + Math.sin(angle) * radius * .8).toFixed(1)}" r="${range(1, 2.1).toFixed(1)}" fill="${i % 3 ? "#a36d3f" : "#f1c979"}" opacity=".86"/>`;
}
flower += `<path d="M149 179Q160 186 171 179" fill="none" stroke="#9e6843" stroke-width="1" opacity=".44"/>`;
await raster("lotus.png", svg(320, 320, flower));

const bodyPath = "M150 160C218 119 300 90 406 78C500 67 591 76 657 108C685 121 706 142 716 160C706 178 685 199 657 212C591 244 500 253 406 242C300 230 218 201 150 160Z";
const tailPath = "M170 160C111 143 79 107 32 90C48 124 68 145 92 160C68 175 48 196 32 230C79 213 111 177 170 160Z";
const finTop = "M448 93C458 49 493 25 535 34C514 70 507 102 506 129C485 117 464 105 448 93Z";
const finBottom = "M445 227C462 211 484 201 507 191C508 222 517 257 535 286C490 287 458 269 445 227Z";

const koiPalettes = [
  { base: "#eee9d2", light: "#fffdf1", shade: "#839891", accent: "#bd3d2f", dark: "#647d79", pattern: "kohaku" },
  { base: "#d7a83d", light: "#fff0a1", shade: "#8d6c2e", accent: "#e5ba45", dark: "#6f592d", pattern: "ogon" },
  { base: "#e6e9df", light: "#fffdf4", shade: "#364c4c", accent: "#bd4436", dark: "#263c3c", pattern: "showa" },
  { base: "#d36b45", light: "#f6a16c", shade: "#4c3c3a", accent: "#d84f36", dark: "#302d31", pattern: "utsuri" },
  { base: "#8ca49e", light: "#d7e4d7", shade: "#3f6565", accent: "#b9503d", dark: "#315451", pattern: "asagi" },
  { base: "#ead8b8", light: "#fff3d7", shade: "#71857a", accent: "#d56b36", dark: "#536b65", pattern: "bekko" },
  { base: "#d9a66e", light: "#ffe6bd", shade: "#71554b", accent: "#b95e43", dark: "#4c3a38", pattern: "kohaku" },
  { base: "#bbc9bf", light: "#f2f6e9", shade: "#4a625e", accent: "#8d4f43", dark: "#334947", pattern: "asagi" },
  { base: "#c98b68", light: "#f6ceb0", shade: "#694d4b", accent: "#d24e3a", dark: "#44363a", pattern: "showa" },
  { base: "#b7a97d", light: "#e9dfb5", shade: "#59634d", accent: "#aa573b", dark: "#3e493d", pattern: "bekko" },
];

function patternFor(palette) {
  const patches = {
    kohaku: [
      "M273 103C300 75 357 76 381 106C396 125 377 151 339 153C304 154 274 139 273 103Z",
      "M424 166C453 133 510 136 535 164C550 182 533 211 496 218C459 225 423 205 424 166Z",
      "M575 93C599 76 639 83 652 108C660 126 649 144 622 146C596 148 575 133 575 93Z",
    ],
    showa: [
      "M244 82C278 58 329 69 347 96C351 120 324 139 284 133C255 128 237 106 244 82Z",
      "M375 166C404 133 467 131 489 163C496 185 474 210 435 213C403 214 375 195 375 166Z",
      "M548 102C577 75 620 87 637 113C641 136 617 153 584 147C558 142 543 126 548 102Z",
    ],
    utsuri: [
      "M231 86C264 67 308 75 326 105C331 128 308 142 274 135C245 129 226 108 231 86Z",
      "M359 163C387 136 438 136 462 164C470 186 447 208 411 210C380 210 359 192 359 163Z",
      "M515 106C545 82 584 87 601 113C604 137 581 153 548 147C523 142 511 125 515 106Z",
    ],
    bekko: [
      "M310 94C338 75 380 83 393 108C397 129 377 143 348 139C323 136 306 117 310 94Z",
      "M479 161C503 135 549 137 568 161C573 182 554 201 524 202C496 202 478 186 479 161Z",
    ],
  };
  if (palette.pattern === "ogon") return "";
  if (palette.pattern === "asagi") {
    return `<path d="M204 160C271 136 334 120 402 118C432 119 454 132 464 160C451 188 423 201 393 202C324 201 263 184 204 160Z" fill="#6f908a" opacity=".3"/>
      <path d="M544 106C568 91 600 94 618 116C624 139 607 153 581 149C559 145 544 130 544 106Z" fill="${palette.accent}" opacity=".8"/>`;
  }
  return patches[palette.pattern].map((path, index) => `<path d="${path}" fill="${index === 2 && palette.pattern === "showa" ? palette.dark : palette.accent}" opacity=".94"/>`).join("");
}

function scales(palette, variant) {
  let output = "";
  for (let row = -4; row <= 4; row++) {
    for (let col = 0; col < 24; col++) {
      const x = 202 + col * 18 + (row % 2 ? 9 : 0);
      const y = 160 + row * 13;
      const opacity = palette.pattern === "ogon" ? .19 : palette.pattern === "asagi" ? .14 : .1;
      output += `<path d="M${x - 9} ${y - 5}Q${x} ${y + 5} ${x + 9} ${y - 5}" fill="none" stroke="${palette.shade}" stroke-width="${variant === 1 ? 1.15 : .9}" opacity="${opacity}"/>
        <path d="M${x - 7} ${y - 4}Q${x} ${y + 1} ${x + 6} ${y - 4}" fill="none" stroke="${palette.light}" stroke-width=".7" opacity="${opacity * .85}"/>`;
    }
  }
  return output;
}

for (let variant = 0; variant < koiPalettes.length; variant++) {
  const palette = koiPalettes[variant];
  const bodyId = `body${variant}`;
  let fish = `<defs>
    <linearGradient id="${bodyId}" x1="0" y1="0" x2="0" y2="1"><stop stop-color="${palette.shade}"/><stop offset=".19" stop-color="${palette.base}"/><stop offset=".42" stop-color="${palette.light}"/><stop offset=".67" stop-color="${palette.base}"/><stop offset="1" stop-color="${palette.shade}"/></linearGradient>
    <linearGradient id="fin${variant}" x1="0" y1="0" x2="1" y2="0"><stop stop-color="${palette.shade}" stop-opacity=".14"/><stop offset=".5" stop-color="${palette.light}" stop-opacity=".5"/><stop offset="1" stop-color="${palette.light}" stop-opacity=".12"/></linearGradient>
    <radialGradient id="cheek${variant}" cx=".5" cy=".35"><stop stop-color="${palette.light}" stop-opacity=".9"/><stop offset="1" stop-color="${palette.base}" stop-opacity=".1"/></radialGradient>
    <filter id="fishShadow${variant}" x="-15%" y="-30%" width="140%" height="180%"><feGaussianBlur stdDeviation="5"/></filter>
    <clipPath id="bodyClip${variant}"><path d="${bodyPath}"/></clipPath>
  </defs>
  <ellipse cx="379" cy="245" rx="300" ry="17" fill="#173f3f" opacity=".27" filter="url(#fishShadow${variant})"/>
  <path d="${tailPath}" fill="url(#fin${variant})" stroke="${palette.light}" stroke-opacity=".34" stroke-width="1.4"/>
  <g fill="none" stroke="${palette.shade}" stroke-width=".9" opacity=".38">`;
  for (let i = 0; i < 12; i++) fish += `<path d="M160 160Q${108 - i * 3} ${128 - i * 4.3} ${48 + i * 4} ${96 + i * 10.8}"/>`;
  fish += `</g>
  <path d="${finTop}" fill="url(#fin${variant})" stroke="${palette.light}" stroke-opacity=".32" stroke-width="1"/>
  <path d="${finBottom}" fill="url(#fin${variant})" stroke="${palette.light}" stroke-opacity=".32" stroke-width="1"/>
  <g fill="none" stroke="${palette.shade}" stroke-width=".85" opacity=".3">`;
  for (let i = 0; i < 8; i++) {
    fish += `<path d="M470 ${93 + i * 4}Q${487 + i * 2} ${65 + i * 7} ${515 + i * 2} ${40 + i * 3}"/>
      <path d="M468 ${227 - i * 4}Q${488 + i * 2} ${250 - i * 5} ${515 + i * 2} ${280 - i * 3}"/>`;
  }
  fish += `</g>
  <path d="${bodyPath}" fill="url(#${bodyId})" stroke="${palette.shade}" stroke-opacity=".74" stroke-width="1.7"/>
  <g clip-path="url(#bodyClip${variant})">
    <ellipse cx="598" cy="145" rx="78" ry="69" fill="url(#cheek${variant})" opacity=".7"/>
    ${patternFor(palette)}
    ${scales(palette, variant)}
    <path d="M194 148C331 116 515 108 663 148" fill="none" stroke="${palette.light}" stroke-width="7" opacity=".2"/>
    <path d="M196 182C344 220 526 221 658 178" fill="none" stroke="${palette.dark}" stroke-width="8" opacity=".13"/>
    <path d="M187 160C323 150 500 151 662 160" fill="none" stroke="${palette.dark}" stroke-width="1.8" opacity=".29"/>
    <path d="M190 159C335 143 516 144 661 155" fill="none" stroke="${palette.light}" stroke-width="1.2" opacity=".4"/>
  </g>
  <path d="M598 100Q632 160 598 220" fill="none" stroke="${palette.shade}" stroke-width="2" opacity=".58"/>
  <path d="M602 103Q632 158 604 216" fill="none" stroke="${palette.light}" stroke-width="1.1" opacity=".42"/>
  <ellipse cx="670" cy="132" rx="7" ry="5.5" fill="#193437"/><ellipse cx="670" cy="188" rx="7" ry="5.5" fill="#193437"/>
  <circle cx="672" cy="130.5" r="2.1" fill="#fff8df"/><circle cx="672" cy="186.5" r="2.1" fill="#fff8df"/>
  <path d="M708 151Q683 141 681 121M708 169Q683 179 681 199" fill="none" stroke="${palette.light}" stroke-width="1.7" opacity=".64"/>
  <path d="M713 157Q700 160 713 163" fill="none" stroke="${palette.shade}" stroke-width="1.3" opacity=".84"/>
  <path d="M640 116Q669 125 692 153" fill="none" stroke="#fff9e8" stroke-width="2.3" opacity=".24"/>`;
  await raster(`koi-${variant}.png`, svg(736, 320, fish));
}

function turtle(variant) {
  const shell = variant
    ? { dark: "#415e52", mid: "#6f8a69", light: "#b4b889", rim: "#d0c994", skin: "#708d77" }
    : { dark: "#3f6658", mid: "#7d936d", light: "#c0c18a", rim: "#d8d19a", skin: "#78977d" };
  let scutes = "";
  for (let row = -2; row <= 2; row++) {
    for (let col = -2; col <= 2; col++) {
      const x = 292 + col * 48 + (row % 2 ? 22 : 0);
      const y = 187 + row * 34;
      scutes += `<path d="M${x - 21} ${y}Q${x} ${y - 19} ${x + 21} ${y}Q${x} ${y + 19} ${x - 21} ${y}Z" fill="none" stroke="${shell.light}" stroke-width="2" opacity=".46"/>
        <path d="M${x - 15} ${y - 2}Q${x} ${y - 12} ${x + 14} ${y - 2}" fill="none" stroke="${shell.dark}" stroke-width="1.4" opacity=".42"/>`;
    }
  }
  let legs = "";
  for (const [x, y, rotate] of [[176, 130, -22], [208, 254, 20], [410, 126, 18], [440, 248, -20]]) {
    legs += `<g transform="translate(${x} ${y}) rotate(${rotate})">
      <path d="M0 0C-29 6-49 28-54 54C-35 52-17 41 2 23Z" fill="${shell.skin}" stroke="${shell.dark}" stroke-width="2"/>
      <path d="M-42 42l-13 10M-31 36l-11 17M-20 29l-6 17" stroke="${shell.light}" stroke-width="2" opacity=".48"/>
    </g>`;
  }
  const headX = 490;
  const spots = variant
    ? `<path d="M486 159C514 146 543 155 554 177C544 198 517 202 492 190Z" fill="#4f6b5e" opacity=".7"/>
      <path d="M511 211C531 206 548 215 552 232C536 242 516 237 506 226Z" fill="#526e5d" opacity=".65"/>`
    : `<path d="M493 158C518 150 540 159 548 177C538 193 516 195 497 187Z" fill="#98aa7a" opacity=".72"/>
      <path d="M514 212C532 208 546 218 548 232C532 240 517 235 508 225Z" fill="#9cac7b" opacity=".62"/>`;
  return svg(640, 360, `<defs>
    <radialGradient id="shell${variant}" cx=".36" cy=".26"><stop stop-color="${shell.light}"/><stop offset=".38" stop-color="${shell.mid}"/><stop offset=".78" stop-color="${shell.dark}"/><stop offset="1" stop-color="#294a44"/></radialGradient>
    <linearGradient id="skin${variant}" x1="0" y1="0" x2="1" y2="1"><stop stop-color="${shell.light}"/><stop offset=".55" stop-color="${shell.skin}"/><stop offset="1" stop-color="${shell.dark}"/></linearGradient>
    <filter id="turtleShadow${variant}" x="-15%" y="-30%" width="140%" height="180%"><feGaussianBlur stdDeviation="6"/></filter>
    <filter id="shellTexture${variant}" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence baseFrequency=".035" numOctaves="3" seed="${variant + 31}" result="noise"/><feColorMatrix in="noise" type="saturate" values=".2"/><feComponentTransfer><feFuncA type="linear" slope=".16"/></feComponentTransfer><feBlend in="SourceGraphic" mode="soft-light"/></filter>
    <clipPath id="shellClip${variant}"><ellipse cx="313" cy="185" rx="173" ry="111"/></clipPath>
  </defs>
  <ellipse cx="318" cy="302" rx="220" ry="20" fill="#173f3f" opacity=".3" filter="url(#turtleShadow${variant})"/>
  ${legs}
  <path d="M446 180C466 147 495 134 531 146C560 156 577 179 570 202C563 224 534 235 503 226C478 219 458 204 446 180Z" fill="url(#skin${variant})" stroke="${shell.dark}" stroke-width="2"/>
  ${spots}
  <ellipse cx="313" cy="185" rx="179" ry="117" fill="#274a43" opacity=".28" transform="translate(5 11)"/>
  <ellipse cx="313" cy="185" rx="173" ry="111" fill="url(#shell${variant})" stroke="${shell.rim}" stroke-width="5"/>
  <g clip-path="url(#shellClip${variant})">${scutes}
    <path d="M164 159C226 98 352 87 455 143" fill="none" stroke="#f0e7b6" stroke-width="8" opacity=".22"/>
    <path d="M175 235C256 277 367 276 451 219" fill="none" stroke="#203f3c" stroke-width="10" opacity=".16"/>
  </g>
  <path d="M183 169C207 109 287 75 359 85C421 94 461 129 470 178" fill="none" stroke="#f4e8b3" stroke-width="3" opacity=".38"/>
  <ellipse cx="${headX}" cy="174" rx="9" ry="7" fill="#20383a"/><circle cx="${headX + 3}" cy="171" r="2.5" fill="#fff7df"/>
  <path d="M548 194Q563 198 570 189" fill="none" stroke="#365149" stroke-width="2" opacity=".7"/>
  <path d="M479 153Q505 139 531 151" fill="none" stroke="#eef0c2" stroke-width="3" opacity=".24"/>`);
}
await raster("turtle-0.png", turtle(0));
await raster("turtle-1.png", turtle(1));

await writeFile(`${outputDir}/provenance.json`, JSON.stringify({
  origin: "Original procedural game artwork authored for this project; SVG shapes rasterized by Sharp.",
  generator: "scripts/make-assets.mjs",
  note: "No assets extracted from the reference screenshot; no external media dependencies.",
}, null, 2));

console.log("Created pond bed, lily pads, lotus flower, ten fish textures and two turtle textures.");
