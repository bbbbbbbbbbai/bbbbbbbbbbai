const path = name => `/assets/sunburst/${name}`;
const ecologyPath = name => `/assets/ecology/${name}`;

export const ART = Object.freeze({
  bed: path('pond-bed.webp'),
  leaf: path('lily.png'),
  leafShadow: path('lily-shadow.png'),
  flower: path('lotus.png'),
  turtle: path('turtle.png'),
  turtleShadow: path('turtle-shadow.png'),
  egret: ecologyPath('egret.png'),
  egretShadow: ecologyPath('egret-shadow.png'),
  swallow: ecologyPath('swallow.png'),
  swallowShadow: ecologyPath('swallow-shadow.png'),
  butterfly: ecologyPath('butterfly.png'),
  butterflyShadow: ecologyPath('butterfly-shadow.png'),
  dragonfly: ecologyPath('dragonfly.png'),
  dragonflyShadow: ecologyPath('dragonfly-shadow.png'),
  firefly: '/assets/firefly.svg',
  birdShadow: ecologyPath('egret-shadow.png'),
  fallingLeaf: ecologyPath('falling-leaf.png'),
  fallingLeafShadow: ecologyPath('falling-leaf-shadow.png'),
});

export const FISH_SPECIES = Object.freeze([
  { name: '红白锦鲤', id: 'kohaku', profileId: 'koi', speed: 1, bend: .035 },
  { name: '黄金锦鲤', id: 'ogon', profileId: 'koi', speed: .94, bend: .03 },
  { name: '昭和锦鲤', id: 'showa', profileId: 'koi', speed: .92, bend: .033 },
  { name: '白写锦鲤', id: 'shiro', profileId: 'koi', speed: 1.02, bend: .035 },
  { name: '彗星金鱼', id: 'goldfish', profileId: 'goldfish', speed: .78, bend: .055 },
  { name: '青铜鲤鱼', id: 'carp', profileId: 'carp', speed: 1.08, bend: .025 },
  { name: '草鱼', id: 'grass-carp', profileId: 'grass-carp', speed: .92, bend: .03 },
  { name: '泥鳅', id: 'loach', profileId: 'loach', speed: 1.38, bend: .075 },
].map(spec => Object.freeze({
  ...spec,
  texture: (['grass-carp', 'loach'].includes(spec.id) ? ecologyPath : path)(`${spec.id}.png`),
  shadow: (['grass-carp', 'loach'].includes(spec.id) ? ecologyPath : path)(`${spec.id}-shadow.png`),
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
