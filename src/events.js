const TAU = Math.PI * 2;
const LIMITS = Object.freeze({
  insects: 8,
  birds: 2,
  leaves: 24,
  rain: 80,
});

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

export class EventScheduler {
  constructor({random = Math.random, width = 1920, height = 1080} = {}) {
    this.random = random;
    this.width = width;
    this.height = height;
    this.environment = {};
    this.clock = 0;
    this.nextId = 0;
    this.insects = [];
    this.birds = [];
    this.leaves = [];
    this.rain = [];
    this.spawnClock = 0;
  }

  configure(environment = {}) {
    this.environment = {...this.environment, ...environment};
  }

  setBounds(width, height) {
    this.width = Math.max(1, width);
    this.height = Math.max(1, height);
  }

  clear() {
    this.insects.length = 0;
    this.birds.length = 0;
    this.leaves.length = 0;
    this.rain.length = 0;
  }

  update(dt) {
    if (!Number.isFinite(dt) || dt <= 0) return;
    dt = Math.min(dt, .05);
    this.clock += dt;
    this.spawnClock += dt;
    this._expire(this.insects, dt);
    this._expire(this.birds, dt);
    this._expire(this.leaves, dt);
    this._expire(this.rain, dt);

    const quiet = Boolean(this.environment.quietMode);
    const reduced = Boolean(this.environment.reducedMotion);
    const quality = this.environment.quality ?? 'high';
    const period = this.environment.period ?? 'day';
    const weather = this.environment.weatherKind ?? 'clear';
    const season = this.environment.season ?? 'summer';
    const maxInsects = quiet || reduced ? 2 : quality === 'power-save' ? 2 : quality === 'balanced' ? 5 : 8;
    if (this.spawnClock >= .8) {
      this.spawnClock = 0;
      if (period === 'night') {
        this._spawnInsect('firefly', maxInsects);
      } else if (!reduced) {
        this._spawnInsect(season === 'summer' ? 'dragonfly' : 'butterfly', maxInsects);
        if (season === 'spring' && this.insects.length < maxInsects) this._spawnInsect('butterfly', maxInsects);
      }
      if (!quiet && !reduced && this.clock % 8 < 1) this._spawnBird(quality);
      if (!quiet && season === 'autumn' && this.clock % 2.4 < .8) this._spawnLeaf(quality);
      if ((weather === 'rain' || weather === 'storm') && !reduced) this._spawnRain(quality);
    }
  }

  getSnapshot() {
    return {
      insects: this.insects.map((item) => ({...item})),
      birds: this.birds.map((item) => ({...item})),
      leaves: this.leaves.map((item) => ({...item})),
      rain: this.rain.map((item) => ({...item})),
    };
  }

  _expire(list, dt) {
    for (let i = list.length - 1; i >= 0; i--) {
      const item = list[i];
      item.life -= dt;
      item.phase = (item.phase + dt * (item.rate ?? 1)) % TAU;
      item.x += Math.cos(item.angle ?? 0) * (item.speed ?? 0) * dt;
      item.y += Math.sin(item.angle ?? 0) * (item.speed ?? 0) * dt;
      if (item.life <= 0) list.splice(i, 1);
    }
  }

  _spawnInsect(kind, limit) {
    if (this.insects.length >= limit) return;
    const speed = kind === 'firefly' ? 4 : kind === 'dragonfly' ? 28 : 16;
    this.insects.push({
      id: `insect-${this.nextId++}`,
      kind,
      x: this.random() * this.width,
      y: this.random() * this.height * .7,
      angle: this.random() * TAU,
      phase: this.random() * TAU,
      rate: .8 + this.random() * .5,
      speed,
      life: kind === 'firefly' ? 10 : 7,
    });
  }

  _spawnBird(quality) {
    const limit = quality === 'power-save' ? 0 : quality === 'balanced' ? 1 : LIMITS.birds;
    if (this.birds.length >= limit) return;
    const fromLeft = this.random() > .5;
    this.birds.push({
      id: `bird-${this.nextId++}`,
      x: fromLeft ? -50 : this.width + 50,
      y: this.height * (.12 + this.random() * .28),
      angle: fromLeft ? 0 : Math.PI,
      phase: this.random() * TAU,
      speed: fromLeft ? 120 : -120,
      life: 5,
    });
  }

  _spawnLeaf(quality) {
    const limit = quality === 'power-save' ? 6 : quality === 'balanced' ? 12 : LIMITS.leaves;
    if (this.leaves.length >= limit) return;
    this.leaves.push({
      id: `leaf-${this.nextId++}`,
      x: this.random() * this.width,
      y: -20,
      angle: this.random() * TAU,
      phase: this.random() * TAU,
      rate: .6 + this.random() * .5,
      speed: 12 + this.random() * 14,
      life: 14,
      rotation: this.random() * TAU,
    });
  }

  _spawnRain(quality) {
    const limit = quality === 'power-save' ? 16 : quality === 'balanced' ? 40 : LIMITS.rain;
    if (this.rain.length >= limit) return;
    this.rain.push({
      id: `rain-${this.nextId++}`,
      x: this.random() * this.width,
      y: this.random() * this.height,
      angle: 0,
      phase: 0,
      rate: 2,
      speed: 0,
      life: .9,
      radius: 2 + this.random() * 5,
    });
  }
}
