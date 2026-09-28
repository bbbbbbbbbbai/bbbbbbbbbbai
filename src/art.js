const path = name => `/assets/sunburst/${name}`;

export const ART = Object.freeze({
  bed: path('pond-bed.webp'),
  leaf: path('lily.png'),
  leafShadow: path('lily-shadow.png'),
  flower: path('lotus.png'),
  turtle: path('turtle.png'),
  turtleShadow: path('turtle-shadow.png'),
  butterfly: '/assets/butterfly.svg',
  dragonfly: '/assets/dragonfly.svg',
  firefly: '/assets/firefly.svg',
  birdShadow: '/assets/bird-shadow.svg',
  fallingLeaf: '/assets/falling-leaf.svg',
});

export const FISH_SPECIES = Object.freeze([
  { name: '红白锦鲤', id: 'kohaku', speed: 1, bend: .035 },
  { name: '黄金锦鲤', id: 'ogon', speed: .94, bend: .03 },
  { name: '昭和锦鲤', id: 'showa', speed: .92, bend: .033 },
  { name: '白写锦鲤', id: 'shiro', speed: 1.02, bend: .035 },
  { name: '彗星金鱼', id: 'goldfish', speed: .78, bend: .055 },
  { name: '青铜鲤鱼', id: 'carp', speed: 1.08, bend: .025 },
].map(spec => Object.freeze({
  ...spec, texture: path(`${spec.id}.png`), shadow: path(`${spec.id}-shadow.png`),
})));

export function coverFrame(width, height, nativeWidth, nativeHeight) {
  const scale = Math.max(width / nativeWidth, height / nativeHeight);
  const w = nativeWidth * scale, h = nativeHeight * scale;
  return { x: (width-w)/2, y: (height-h)/2, width: w, height: h, scale };
}

export function waterBounds(width, height, frame) {
  return {
    left: Math.max(width*.025, frame.x + frame.width*.19),
    right: Math.min(width*.975, frame.x + frame.width*.81),
    top: Math.max(height*.06, frame.y + frame.height*.20),
    bottom: Math.min(height*.94, frame.y + frame.height*.78),
  };
}

const LIGHT = {
  dawn: [.93, .97, .91],
  day: [1, 1, 1],
  dusk: [1.04, .82, .70],
  night: [.40, .56, .70],
};
export function lightForPeriod(period) {
  return [...(LIGHT[period] ?? LIGHT.day)];
}
