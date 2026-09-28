const profile = (value) => Object.freeze(value);

export const FISH_PROFILES = Object.freeze([
  profile({id:'koi', name:'锦鲤', speed:1, turnRate:1, size:1, depth:.9, foodInterest:1, schoolAffinity:.7, shelterAffinity:.35}),
  profile({id:'carp', name:'鲤鱼', speed:.78, turnRate:.72, size:1.12, depth:.82, foodInterest:.72, schoolAffinity:.45, shelterAffinity:.25}),
  profile({id:'goldfish', name:'金鱼', speed:1.22, turnRate:1.3, size:.72, depth:.98, foodInterest:.86, schoolAffinity:.82, shelterAffinity:.18}),
  profile({id:'grass-carp', name:'草鱼', speed:.92, turnRate:.62, size:1.05, depth:.76, foodInterest:.52, schoolAffinity:.34, shelterAffinity:.3}),
  profile({id:'loach', name:'泥鳅', speed:1.38, turnRate:1.5, size:.52, depth:.68, foodInterest:.66, schoolAffinity:.22, shelterAffinity:.72}),
  profile({id:'custom', name:'自定义小鱼', speed:1, turnRate:1, size:1, depth:.9, foodInterest:.75, schoolAffinity:.55, shelterAffinity:.4}),
]);

export function getFishProfile(value) {
  if (typeof value === 'string') return FISH_PROFILES.find((item) => item.id === value) ?? FISH_PROFILES[0];
  if (Number.isInteger(value) && value >= 0 && value < FISH_PROFILES.length) return FISH_PROFILES[value];
  return FISH_PROFILES[0];
}
