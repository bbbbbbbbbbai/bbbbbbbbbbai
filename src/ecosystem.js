import { EventScheduler } from './events.js';

const TAU = Math.PI * 2;
const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const wrap = (angle) => Math.atan2(Math.sin(angle), Math.cos(angle));

export class EcosystemController {
  constructor({random = Math.random, width = 1920, height = 1080, turtleCount = 3} = {}) {
    this.random = random;
    this.width = Math.max(1, width);
    this.height = Math.max(1, height);
    this.environment = {
      period: 'day',
      weatherKind: 'clear',
      season: 'summer',
      quietMode: false,
      reducedMotion: false,
      quality: 'high',
    };
    this.time = 0;
    this.nextTurtleId = 0;
    this.turtles = [];
    this.events = new EventScheduler({random, width, height});
    for (let i = 0; i < turtleCount; i++) this._addTurtle(i);
  }

  setBounds(bounds) {
    this.width = Math.max(1, bounds.right - bounds.left);
    this.height = Math.max(1, bounds.bottom - bounds.top);
    this.events.setBounds(this.width, this.height);
    for (const turtle of this.turtles) {
      turtle.x = clamp(turtle.x, bounds.left, bounds.right);
      turtle.y = clamp(turtle.y, bounds.top, bounds.bottom);
    }
  }

  setEnvironment(environment = {}) {
    this.environment = {...this.environment, ...environment};
    this.events.configure(this.environment);
  }

  update(dt, worldSnapshot = {fish:[]}) {
    if (!Number.isFinite(dt) || dt <= 0) return;
    dt = Math.min(dt, .05);
    this.time += dt;
    this._updateTurtles(dt);
    this.events.update(dt, worldSnapshot);
  }

  getSnapshot() {
    return {
      turtles: this.turtles.map((turtle) => ({...turtle})),
      ...this.events.getSnapshot(),
    };
  }

  _addTurtle(index) {
    const baseLength = 88 + this.random() * 44;
    this.turtles.push({
      id: `eco-turtle-${this.nextTurtleId++}`,
      x: this.width * (.16 + this.random() * .68),
      y: this.height * (.2 + this.random() * .62),
      angle: this.random() * TAU,
      phase: this.random() * TAU,
      surfaceClock: index === 0 ? 0 : this.random() * 7.5,
      surfaceCycle: 7.5,
      surfaceDuration: 1.6,
      surfacing: false,
      surfaceProgress: 0,
      resting: false,
      variant: Math.floor(this.random() * 2),
      length: baseLength,
    });
  }

  _updateTurtles(dt) {
    for (const turtle of this.turtles) {
      turtle.phase += dt;
      turtle.surfaceClock = (turtle.surfaceClock + dt) % turtle.surfaceCycle;
      if (turtle.surfaceCycle - turtle.surfaceClock < 1e-6) turtle.surfaceClock = 0;
      turtle.surfacing = turtle.surfaceClock < turtle.surfaceDuration;
      turtle.surfaceProgress = turtle.surfacing
        ? turtle.surfaceClock / turtle.surfaceDuration
        : 0;
      turtle.resting = turtle.surfaceClock < turtle.surfaceDuration + .8;
      const speed = turtle.surfacing ? 1.4 : 10 + turtle.variant * 2;
      turtle.angle = wrap(turtle.angle + Math.sin(turtle.phase * .23) * dt * .2);
      turtle.x = clamp(turtle.x + Math.cos(turtle.angle) * speed * dt, 0, this.width);
      turtle.y = clamp(turtle.y + Math.sin(turtle.angle) * speed * dt, 0, this.height);
    }
  }
}
