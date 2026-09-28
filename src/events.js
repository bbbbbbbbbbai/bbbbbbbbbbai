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
    this.nextInsect = .2;
    this.nextBird = 3;
    this.nextLeaf = .6;
    this.nextRain = 0;
    this.insectSequence = 0;
    this.birdSequence = 0;
  }

  configure(environment = {}) {
    this.environment = {...this.environment, ...environment};
    const night = this.environment.period === 'night';
    this.insects = this.insects.filter(item => (item.kind === 'firefly') === night);
    // A dusk transition stops new flights; birds already overhead finish crossing.
    if (this.environment.quietMode || this.environment.reducedMotion) {
      this.birds.length = 0;
      this.insects.length = Math.min(this.insects.length, 2);
      this.leaves.length = Math.min(this.leaves.length, 8);
      this.rain.length = Math.min(this.rain.length, 24);
    }
    if (!['rain', 'storm'].includes(this.environment.weatherKind)) this.rain.length = 0;
  }

  setBounds(width, height) {
    const oldWidth = this.width, oldHeight = this.height;
    this.width = Math.max(1, width);
    this.height = Math.max(1, height);
    for (const list of [this.insects, this.birds, this.leaves, this.rain]) {
      for (const item of list) {
        item.x *= this.width / oldWidth;
        item.y *= this.height / oldHeight;
      }
    }
    for (const bird of this.birds) {
      const remaining = Math.cos(bird.angle) > 0 ? this.width + 130 - bird.x : bird.x + 130;
      bird.life = Math.max(0, remaining / bird.speed);
    }
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
    this._expire(this.insects, dt);
    this._expire(this.birds, dt);
    this._expire(this.leaves, dt);
    this._expire(this.rain, dt);

    const quiet = Boolean(this.environment.quietMode);
    const reduced = Boolean(this.environment.reducedMotion);
    const period = this.environment.period ?? 'day';
    const weather = this.environment.weatherKind ?? 'clear';
    const season = this.environment.season ?? 'summer';
    const maxInsects = quiet || reduced ? 2 : LIMITS.insects;
    if (this.clock >= this.nextInsect) {
      this.nextInsect = this.clock + .65;
      if (period === 'night') {
        this._spawnInsect('firefly', maxInsects);
      } else if (!reduced) {
        this._spawnInsect(this.insectSequence++ % 2 ? 'dragonfly' : 'butterfly', maxInsects);
      }
    }
    if (this.clock >= this.nextBird) {
      this.nextBird = this.clock + 22 + this.random() * 12;
      if (!quiet && !reduced && period !== 'night') this._spawnBird();
    }
    if (this.clock >= this.nextLeaf) {
      this.nextLeaf = this.clock + (season === 'autumn' ? 1.4 : 3.2);
      if (!quiet && !reduced) this._spawnLeaf();
    }
    if (this.clock >= this.nextRain) {
      this.nextRain = this.clock + (quiet ? .18 : weather === 'storm' ? .025 : .055);
      if ((weather === 'rain' || weather === 'storm') && !reduced) this._spawnRain(quiet ? 24 : LIMITS.rain);
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
      item.age = (item.age ?? 0) + dt;
      if (list === this.insects) {
        item.angle += Math.sin(item.phase) * dt * .8;
        if (item.x < 24 || item.x > this.width - 24) item.angle = Math.atan2(Math.sin(item.angle), this.width / 2 - item.x);
        if (item.y < 24 || item.y > this.height - 24) item.angle = Math.atan2(this.height / 2 - item.y, Math.cos(item.angle));
      }
      if (list === this.leaves) {
        item.altitude = Math.max(0, 65 * (1 - item.age / 2.6));
        item.state = item.altitude > 0 ? 'falling' : 'floating';
        item.speed = item.state === 'falling' ? 12 : 3;
        item.rotation += Math.sin(item.phase) * dt * .25;
      }
      item.x += Math.cos(item.angle ?? 0) * (item.speed ?? 0) * dt;
      item.y += Math.sin(item.angle ?? 0) * (item.speed ?? 0) * dt;
      if (list === this.insects || list === this.leaves) {
        item.x = clamp(item.x, 12, Math.max(12, this.width - 12));
        item.y = clamp(item.y, 12, Math.max(12, this.height - 12));
      }
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
      rate: kind === 'firefly' ? 1.5 : kind === 'dragonfly' ? 35 : 12,
      speed,
      life: kind === 'firefly' ? 15 : 18,
    });
  }

  _spawnBird() {
    if (this.birds.length >= LIMITS.birds) return;
    const fromLeft = this.random() > .5;
    const kind = this.birdSequence++ % 2 ? 'swallow' : 'egret';
    const speed = kind === 'egret' ? 145 : 220;
    this.birds.push({
      id: `bird-${this.nextId++}`,
      kind,
      x: fromLeft ? -130 : this.width + 130,
      y: this.height * (.22 + this.random() * .48),
      angle: fromLeft ? 0 : Math.PI,
      phase: this.random() * TAU,
      rate: kind === 'egret' ? 4 : 9,
      speed,
      life: (this.width + 260) / speed,
    });
  }

  _spawnLeaf() {
    if (this.leaves.length >= LIMITS.leaves) return;
    this.leaves.push({
      id: `leaf-${this.nextId++}`,
      x: (.1 + this.random() * .8) * this.width,
      y: (.2 + this.random() * .6) * this.height,
      angle: .2 + this.random() * .7,
      phase: this.random() * TAU,
      rate: .6 + this.random() * .5,
      speed: 12 + this.random() * 14,
      life: 28,
      altitude: 65,
      state: 'falling',
      rotation: this.random() * TAU,
    });
  }

  _spawnRain(limit) {
    if (this.rain.length >= limit) return;
    this.rain.push({
      id: `rain-${this.nextId++}`,
      x: this.random() * this.width,
      y: this.random() * this.height,
      angle: 0,
      phase: 0,
      rate: 2,
      speed: 0,
      life: 1.4,
      radius: 2 + this.random() * 5,
    });
  }
}
