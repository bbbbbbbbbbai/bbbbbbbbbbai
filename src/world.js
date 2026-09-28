import {
  FleeBehavior,
  SeekBehavior,
  SeparationBehavior,
  Vector3,
  Vehicle,
  WanderBehavior,
} from 'yuka';
import { FISH_SPECIES } from './art.js';
import { getFishProfile } from './species.js';
import { EcosystemController } from './ecosystem.js';

const TAU = Math.PI * 2;
const FOOD_LIFETIME = 12;
const MAX_FOOD = 128;
const MOUSE_LIFETIME = 0.6;
const TURN_RATE = 3.8;
const NEIGHBOR_DEPTH = 0.18;
const DEPTH_RATE = 0.35;

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const wrap = (angle) => Math.atan2(Math.sin(angle), Math.cos(angle));
const dimension = (value, fallback) => Number.isFinite(value) && value > 0 ? value : fallback;

// Yuka exposes no RNG hook. Seed its wander circle, leaving library jitter at
// zero, so independent worlds never need to replace global Math.random.
class SeededWander extends WanderBehavior {
  constructor(random) {
    super(1, 2, 0);
    this.random = random;
    const angle = random() * TAU;
    this._targetLocal.set(Math.cos(angle), 0, Math.sin(angle));
  }

  calculate(vehicle, force, dt) {
    this._targetLocal.x += (this.random() - 0.5) * dt * 3;
    this._targetLocal.z += (this.random() - 0.5) * dt * 3;
    return super.calculate(vehicle, force, dt);
  }
}

// Yuka's inverse-distance separation can consume all steering at an overlap.
// Use bounded lateral yielding; depth and proximity fade continuously at entry.
class PassingSeparation extends SeparationBehavior {
  constructor(pose) {
    super();
    this.pose = pose;
    this.sides = new Map();
  }

  calculate(vehicle, force) {
    const pose = this.pose;
    const rightX = -Math.sin(pose.angle), rightY = Math.cos(pose.angle);
    const active = new Set();
    let sideways = 0;
    for (const neighbor of vehicle.neighbors) {
      const dx = pose.position.x - neighbor.position.x;
      const dy = pose.position.z - neighbor.position.z;
      const radius = (pose.length + neighbor.length) * .65;
      const proximity = Math.max(0, 1 - Math.hypot(dx, dy) / radius);
      const layer = Math.max(0, 1 - Math.abs(pose.depth - neighbor.depth) / NEIGHBOR_DEPTH);
      active.add(neighbor.id);
      if (!this.sides.has(neighbor.id)) {
        const lateral = dx * rightX + dy * rightY;
        const side = Math.abs(lateral) > radius * .03
          ? Math.sign(lateral)
          : Math.cos(pose.angle - neighbor.angle) < 0
            ? 1
            : pose.id < neighbor.id ? 1 : -1;
        this.sides.set(neighbor.id, side);
      }
      sideways += this.sides.get(neighbor.id) * proximity ** 2 * layer ** 2;
    }
    for (const id of this.sides.keys()) if (!active.has(id)) this.sides.delete(id);
    const strength = clamp(sideways, -1, 1);
    return force.set(rightX * strength, 0, rightY * strength);
  }
}

/** Renderer-independent simulation. Screen (x, y) maps to Yuka's (x, z). */
export class PondWorld {
  constructor(width, height, { count = 24, speed = 1, random = Math.random } = {}) {
    this.width = dimension(width, 1920);
    this.height = dimension(height, 1080);
    this.habitat = {left:0,top:0,right:this.width,bottom:this.height};
    this.fish = [];
    this.turtles = [];
    this.food = [];
    this.speed = 1;
    this.count = 0;
    this._random = () => {
      const value = random();
      return Number.isFinite(value) ? clamp(value, 0, 1 - Number.EPSILON) : 0.5;
    };
    this._agents = new Map();
    this._nextFishId = 0;
    this._nextTurtleId = 0;
    this._nextFoodId = 0;
    this._mouseAge = MOUSE_LIFETIME;
    this._mouse = new Vector3(Infinity, 0, Infinity);
    let ecosystemSeed = 0x6d2b79f5;
    const ecosystemRandom = () => {
      ecosystemSeed = (Math.imul(ecosystemSeed, 1664525) + 1013904223) >>> 0;
      return ecosystemSeed / 4294967296;
    };
    this.ecosystem = new EcosystemController({
      random: ecosystemRandom,
      width: this.width,
      height: this.height,
      turtleCount: 0,
    });
    this.setSpeed(speed);
    this.setCount(Number.isFinite(count) ? count : 24);
    this.setTurtleCount(3);
  }

  get _scale() {
    return Math.min(this.width, this.height) / 1080;
  }

  setCount(count) {
    if (!Number.isFinite(count)) return;
    this.count = clamp(Math.round(count), 8, 48);
    const baseline = this.fish.filter((fish) => fish.customId === null);
    for (const fish of baseline.slice(this.count)) this._removeFish(fish);
    for (let i = baseline.length; i < this.count; i++) this._addFish(null);
  }

  setSpeed(speed) {
    if (!Number.isFinite(speed)) return;
    this.speed = clamp(speed, 0.4, 1.6);
  }

  setHabitat(bounds) {
    const b={left:clamp(bounds.left,0,this.width),right:clamp(bounds.right,0,this.width),
      top:clamp(bounds.top,0,this.height),bottom:clamp(bounds.bottom,0,this.height)};
    if(!Object.values(b).every(Number.isFinite)||b.left>=b.right||b.top>=b.bottom)return;
    const old=this.habitat;
    for(const item of [...this.fish,...this.turtles,...this.food]){
      item.x=b.left+clamp((item.x-old.left)/(old.right-old.left),0,1)*(b.right-b.left);
      item.y=b.top+clamp((item.y-old.top)/(old.bottom-old.top),0,1)*(b.bottom-b.top);
    }
    this.habitat=b;
    this.ecosystem.setBounds(b);
  }

  setEnvironment(environment) {
    this.ecosystem.setEnvironment(environment);
  }

  setTurtleCount(count) {
    if (!Number.isFinite(count)) return;
    const target = clamp(Math.round(count), 0, 8);
    while (this.turtles.length > target) this.turtles.pop();
    while (this.turtles.length < target) this._addTurtle();
  }

  setArtworks(works) {
    const unique = new Map();
    for (const work of Array.isArray(works) ? works : []) {
      if (work && typeof work.id === 'string' && work.id.length > 0 && !unique.has(work.id)) {
        unique.set(work.id, work);
      }
      if (unique.size === 20) break;
    }
    const existing = new Set();
    for (const fish of [...this.fish]) {
      if (fish.customId === null) continue;
      if (!unique.has(fish.customId)) {
        this._removeFish(fish);
      } else {
        this._agents.get(fish.id).artwork = unique.get(fish.customId);
        existing.add(fish.customId);
      }
    }
    for (const [id, artwork] of unique) {
      if (!existing.has(id)) this._addFish(id, artwork);
    }
  }

  resize(width, height) {
    const nextWidth = dimension(width, this.width);
    const nextHeight = dimension(height, this.height);
    const xRatio = nextWidth / this.width;
    const yRatio = nextHeight / this.height;
    this.width = nextWidth;
    this.height = nextHeight;
    this.habitat={left:this.habitat.left*xRatio,right:this.habitat.right*xRatio,
      top:this.habitat.top*yRatio,bottom:this.habitat.bottom*yRatio};
    for (const fish of this.fish) {
      fish.x *= xRatio;
      fish.y *= yRatio;
      const agent = this._agents.get(fish.id);
      fish.length = agent.length * this._scale;
      agent.vehicle.position.set(fish.x, 0, fish.y);
      agent.vehicle.velocity.x *= xRatio;
      agent.vehicle.velocity.z *= yRatio;
    }
    for (const food of this.food) {
      food.x *= xRatio;
      food.y *= yRatio;
    }
    for (const turtle of this.turtles) {
      turtle.x *= xRatio;
      turtle.y *= yRatio;
      turtle.length = turtle.baseLength * this._scale;
    }
    this._mouse.x *= xRatio;
    this._mouse.z *= yRatio;
    this.ecosystem.setBounds({left:0,top:0,right:this.width,bottom:this.height});
  }

  getFeedingPoint(x, y) {
    if (!Number.isFinite(x) || !Number.isFinite(y)) return null;
    return {x:clamp(x,0,this.width),y:clamp(y,0,this.height)};
  }

  getBehaviorSnapshot() {
    return {
      fish: this.fish.map((fish) => ({
        id: fish.id,
        profileId: fish.profileId,
        depth: fish.depth,
        behaviorState: fish.behaviorState,
        targetFoodId: fish.targetFoodId,
      })),
      food: this.food.map((food) => ({...food})),
    };
  }

  feed(x, y) {
    const point=this.getFeedingPoint(x,y);
    if(!point)return false;
    const count = 5 + Math.floor(this._random() * 4);
    while (this.food.length + count > MAX_FOOD) this.food.shift();
    const radius = 16 * this._scale;
    for (let i = 0; i < count; i++) {
      const angle = this._random() * TAU;
      const spread = i === 0 ? 0 : Math.sqrt(this._random()) * radius;
      this.food.push({
        id: `food-${this._nextFoodId++}`,
        x: clamp(point.x + Math.cos(angle) * spread, 0, this.width),
        y: clamp(point.y + Math.sin(angle) * spread, 0, this.height),
        age: 0,
      });
    }
    return true;
  }

  disturb(x, y) {
    if (!Number.isFinite(x) || !Number.isFinite(y)) return;
    if (this._mouse.x === x && this._mouse.z === y) return;
    this._mouse.set(x, 0, y);
    this._mouseAge = 0;
  }

  update(dt) {
    if (!Number.isFinite(dt) || dt <= 0) return;
    dt = Math.min(dt, 0.05);
    this._mouseAge = Math.min(MOUSE_LIFETIME, this._mouseAge + dt);
    for (let i = this.food.length - 1; i >= 0; i--) {
      this.food[i].age += dt;
      if (this.food[i].age + 1e-9 >= FOOD_LIFETIME) this.food.splice(i, 1);
    }

    // Sync public poses before finding neighbors, also allowing callers to
    // relocate fish intentionally without reaching into Yuka's vehicle state.
    const agents = this.fish.map((fish) => this._agents.get(fish.id));
    for (const agent of agents) {
      const { fish, vehicle } = agent;
      vehicle.position.set(fish.x, 0, fish.y);
      agent.pose.position.copy(vehicle.position);
      agent.pose.depth = fish.depth;
      agent.pose.angle = fish.angle;
      agent.pose.length = fish.length;
      vehicle.rotation.fromEuler(0, Math.PI / 2 - fish.angle, 0);
      const cruise = agent.cruise * this._scale * this.speed;
      const previousSpeed = vehicle.velocity.length();
      const speed = previousSpeed > 0 ? previousSpeed : cruise;
      vehicle.velocity.set(Math.cos(fish.angle) * speed, 0, Math.sin(fish.angle) * speed);
      vehicle.neighbors.length = 0;
    }
    for (let i = 0; i < agents.length; i++) {
      for (let j = i + 1; j < agents.length; j++) {
        const a = agents[i];
        const b = agents[j];
        const radius = (a.fish.length + b.fish.length) * 0.65;
        if (Math.abs(a.fish.depth - b.fish.depth) < NEIGHBOR_DEPTH
          && a.vehicle.position.squaredDistanceTo(b.vehicle.position) < radius * radius) {
          a.vehicle.neighbors.push(b.pose);
          b.vehicle.neighbors.push(a.pose);
        }
      }
    }
    // Configure forces against the same snapshot, then integrate all vehicles.
    for (const agent of agents) this._configure(agent);
    for (const agent of agents) this._move(agent, dt);
    this._updateTurtles(dt);
    this._eat();
    this.ecosystem.update(dt, this.getBehaviorSnapshot());
  }

  getEcosystemSnapshot() {
    return {
      ...this.ecosystem.getSnapshot(),
      turtles: this.turtles.map((turtle) => ({...turtle})),
    };
  }

  _removeFish(fish) {
    this.fish.splice(this.fish.indexOf(fish), 1);
    this._agents.delete(fish.id);
  }

  _addFish(customId, artwork = null) {
    const length = 45 + this._random() * 40;
    const angle = this._random() * TAU;
    const variant = Math.floor(this._random() * FISH_SPECIES.length);
    const visualProfile = FISH_SPECIES[variant] ?? FISH_SPECIES[0];
    const profile = getFishProfile(customId ? 'custom' : visualProfile.profileId);
    const sequenceId = this._nextFishId++;
    // Identity-derived layers do not consume the shared movement/feeding RNG.
    const depth = .22 + ((sequenceId * .137508) % 1) * .56;
    const fish = {
      id: `fish-${sequenceId}`,
      x: 0,
      y: 0,
      angle: wrap(angle),
      length: length * this._scale,
      variant,
      species: visualProfile.name,
      depth,
      profileId: profile.id,
      profile,
      behaviorState: 'cruise',
      targetFoodId: null,
      phase: this._random() * TAU,
      swimSpeed: 0,
      customId,
    };
    // Best-candidate placement avoids creating an overlapping school, including
    // deterministic constant-random fixtures, without moving existing fish.
    let bestDistance = -1;
    for (let i = 0; i < 12; i++) {
      const sequence = i + (this._nextFishId - 1) * 12;
      const b=this.habitat;
      const x = b.left+(0.08 + ((this._random() + sequence * 0.61803398875) % 1) * 0.84) * (b.right-b.left);
      const y = b.top+(0.08 + ((this._random() + sequence * 0.41421356237) % 1) * 0.84) * (b.bottom-b.top);
      let nearest = Infinity;
      for (const other of this.fish) nearest = Math.min(nearest, Math.hypot(x - other.x, y - other.y));
      if (nearest > bestDistance) {
        bestDistance = nearest;
        fish.x = x;
        fish.y = y;
      }
    }
    const vehicle = new Vehicle();
    vehicle.updateOrientation = false;
    vehicle.position.set(fish.x, 0, fish.y);
    vehicle.rotation.fromEuler(0, Math.PI / 2 - fish.angle, 0);
    const boundary = new SeekBehavior();
    const flee = new FleeBehavior(this._mouse);
    const pose = {id: sequenceId, position: new Vector3(), angle: fish.angle, depth, length: fish.length};
    const separation = new PassingSeparation(pose);
    const seek = new SeekBehavior();
    const wander = new SeededWander(this._random);
    for (const behavior of [boundary, flee, separation, seek, wander]) vehicle.steering.add(behavior);
    // Keep the established visual-species speed baseline; ecological speed
    // differences are applied by the behavior layer so existing feeding
    // response remains stable while profiles are introduced.
    const cruise = length * visualProfile.speed * (0.8 + this._random() * 0.45);
    const speed = cruise * this._scale * this.speed;
    vehicle.velocity.set(Math.cos(angle) * speed, 0, Math.sin(angle) * speed);
    fish.swimSpeed = 2 + speed / fish.length * 4;
    const agent = {
      fish, vehicle, boundary, flee, separation, seek, wander, cruise, length, artwork, pose,
      targetId: null,
      boundaryTurn: 0,
      turnSign: this._nextFishId % 2 ? 1 : -1,
      profile,
      regroupTimer: 0,
      cruiseDepth: depth,
      depthPhase: (sequenceId * 2.4) % TAU,
    };
    this._agents.set(fish.id, agent);
    this.fish.push(fish);
  }

  _addTurtle() {
    const baseLength = 88 + this._random() * 44;
    const b=this.habitat;
    const turtle = {
      id: `turtle-${this._nextTurtleId++}`,
      x: b.left+(0.16 + this._random() * 0.68) * (b.right-b.left),
      y: b.top+(0.2 + this._random() * 0.62) * (b.bottom-b.top),
      angle: wrap(this._random() * TAU),
      length: baseLength * this._scale,
      baseLength,
      baseSpeed: 10 + this._random() * 8,
      phase: this._random() * TAU,
      variant: Math.floor(this._random() * 2),
      restCycle: 12 + this._random() * 5,
      restDuration: 2.2 + this._random() * 1.2,
      surfacing: false,
      surfaceProgress: 0,
    };
    this.turtles.push(turtle);
  }

  _updateTurtles(dt) {
    const b=this.habitat;
    for (const turtle of this.turtles) {
      turtle.phase += dt;
      const restPhase = turtle.phase % turtle.restCycle;
      const resting = restPhase < turtle.restDuration;
      turtle.surfacing = restPhase < .9;
      turtle.surfaceProgress = turtle.surfacing ? restPhase / .9 : 0;
      const steering = Math.sin(turtle.phase * 0.23 + turtle.variant * 1.7) * 0.28;
      turtle.angle = wrap(turtle.angle + steering * dt * (resting ? 0.2 : 1));
      const speed = this._scale * (resting ? 1.2 : turtle.baseSpeed);
      const margin=turtle.length*.65;
      let desired=turtle.angle+steering*dt;
      if(turtle.x<b.left+margin)desired=0;
      else if(turtle.x>b.right-margin)desired=Math.PI;
      if(turtle.y<b.top+margin)desired=Math.PI/2;
      else if(turtle.y>b.bottom-margin)desired=-Math.PI/2;
      turtle.angle=wrap(turtle.angle+clamp(wrap(desired-turtle.angle),-.65*dt,.65*dt));
      turtle.x += Math.cos(turtle.angle) * speed * dt;
      turtle.y += Math.sin(turtle.angle) * speed * dt;
      turtle.x=clamp(turtle.x,b.left,b.right);
      turtle.y=clamp(turtle.y,b.top,b.bottom);
      turtle.resting = resting;
    }
  }

  _configure(agent) {
    const { fish, vehicle, boundary, flee, separation, seek, wander } = agent;
    const cruise = agent.cruise * this._scale * this.speed * agent.profile.speed;
    const panic = fish.length * 2.6;
    const distance = vehicle.position.distanceTo(this._mouse);
    const intensity = distance < panic
      ? Math.max(0, 1 - this._mouseAge / MOUSE_LIFETIME) * (1 - distance / panic)
      : 0;
    agent.regroupTimer = Math.max(0, agent.regroupTimer - 1 / 60);
    flee.active = intensity > 0;
    flee.panicDistance = panic;
    flee.weight = intensity * 5;
    vehicle.maxSpeed = cruise * (1 + intensity * 0.4);
    vehicle.maxForce = cruise * 4;
    separation.weight = cruise * 1.2;

    let target = this.food.find((food) => food.id === agent.targetId);
    const foodRadius = this._scale * (220 + agent.profile.foodInterest * 100) * (1 - fish.depth * .25);
    // A small retention margin avoids flickering at the perception boundary,
    // without allowing a previously seen pellet to attract fish across the pond.
    if (target && Math.hypot(target.x - fish.x, target.y - fish.y) > foodRadius * 1.2) target = null;
    if (!target) {
      let nearest = foodRadius ** 2;
      for (const food of this.food) {
        const distanceSq = (food.x - fish.x) ** 2 + (food.y - fish.y) ** 2;
        if (distanceSq < nearest) {
          nearest = distanceSq;
          target = food;
        }
      }
      agent.targetId = target?.id ?? null;
    }
    fish.targetFoodId = target?.id ?? null;
    fish.behaviorState = intensity > 0
      ? 'flee'
      : target
        ? 'seek-food'
        : agent.regroupTimer > 0
          ? 'regroup'
          : 'cruise';
    seek.active = Boolean(target);
    seek.weight = 2.8 * (.86 + agent.profile.foodInterest * .14);
    if (target) seek.target.set(target.x, 0, target.y);
    wander.weight = cruise * (target ? 0.035 : 0.28);

    // Steer away from the approached wall using a local target with a tangent.
    // There is deliberately no shared center target or cohesion behavior.
    const margin = target ? fish.length * 0.35 : fish.length * 2.2 + cruise * 0.4;
    const b=this.habitat;
    const marginX = Math.min((b.right-b.left) * 0.22, margin);
    const marginY = Math.min((b.bottom-b.top) * 0.22, margin);
    const lookAhead = target ? 0.1 : 0.8;
    const targetOnEdge = target && (
      target.x <= 1 || target.x >= this.width - 1 ||
      target.y <= 1 || target.y >= this.height - 1
    );
    const headingX = Math.cos(fish.angle);
    const headingY = Math.sin(fish.angle);
    const aheadX = fish.x + headingX * cruise * lookAhead;
    const aheadY = fish.y + headingY * cruise * lookAhead;
    let dx = headingX;
    let dy = headingY;
    boundary.active = false;
    if (!targetOnEdge && (aheadX < b.left+marginX || aheadX > b.right - marginX)) {
      dx = aheadX < b.left+marginX ? Math.abs(dx) + 0.8 : -Math.abs(dx) - 0.8;
      if (Math.abs(dy) < 0.4) dy += agent.turnSign * 0.85;
      boundary.active = true;
    }
    if (!targetOnEdge && (aheadY < b.top+marginY || aheadY > b.bottom - marginY)) {
      dy = aheadY < b.top+marginY ? Math.abs(dy) + 0.8 : -Math.abs(dy) - 0.8;
      if (Math.abs(dx) < 0.4) dx += agent.turnSign * 0.85;
      boundary.active = true;
    }
    boundary.target.set(fish.x + dx * fish.length * 3, 0, fish.y + dy * fish.length * 3);
    boundary.weight = 5;
  }

  _move(agent, dt) {
    const { fish, vehicle, boundary } = agent;
    const x = fish.x;
    const y = fish.y;
    vehicle.update(dt);
    // The speed floor can keep velocity pointing outwards while braking at a
    // shore. Turn toward the boundary's safe heading, not that residual velocity.
    const desiredAngle = boundary.active
      ? Math.atan2(boundary.target.z - y, boundary.target.x - x)
      : Math.atan2(vehicle.velocity.z, vehicle.velocity.x);
    let turn = wrap(desiredAngle - fish.angle);
    // Adjacent shores can move the safe heading across the +/- PI seam.
    // Keep one turn direction until the safe heading is in front of the fish.
    if (boundary.active && Math.abs(turn) > Math.PI / 2) {
      agent.boundaryTurn ||= Math.sign(turn);
      turn = agent.boundaryTurn * Math.abs(turn);
    } else {
      agent.boundaryTurn = 0;
    }
    const angleRate = TURN_RATE * (.82 + agent.profile.turnRate * .18);
    const turnRate = boundary.active ? Math.min(TURN_RATE, angleRate) : angleRate;
    const angleChange = clamp(turn, -turnRate * dt, turnRate * dt);
    fish.angle = wrap(fish.angle + angleChange);
    const speed = clamp(vehicle.velocity.length(), vehicle.maxSpeed * 0.4, vehicle.maxSpeed);
    vehicle.velocity.set(Math.cos(fish.angle) * speed, 0, Math.sin(fish.angle) * speed);
    fish.x = clamp(x + vehicle.velocity.x * dt, this.habitat.left, this.habitat.right);
    fish.y = clamp(y + vehicle.velocity.z * dt, this.habitat.top, this.habitat.bottom);
    vehicle.position.set(fish.x, 0, fish.y);
    fish.swimSpeed = 2 + speed / fish.length * 4;
    fish.phase = (fish.phase + fish.swimSpeed * dt) % TAU;
    agent.depthPhase = (agent.depthPhase + dt * .23) % TAU;
    const depthTarget = agent.seek.active
      ? .06
      : agent.cruiseDepth + Math.sin(agent.depthPhase) * .07;
    const depthChange = (depthTarget - fish.depth) * (1 - Math.exp(-dt * .7));
    fish.depth = clamp(fish.depth + clamp(depthChange, -DEPTH_RATE * dt, DEPTH_RATE * dt), 0, 1);
  }

  _eat() {
    for (let index = this.food.length - 1; index >= 0; index--) {
      const food = this.food[index];
      for (const fish of this.fish) {
        const headX = fish.x + Math.cos(fish.angle) * fish.length * 0.4;
        const headY = fish.y + Math.sin(fish.angle) * fish.length * 0.4;
        const radius = fish.length * 0.18;
        if ((food.x - headX) ** 2 + (food.y - headY) ** 2 <= radius * radius) {
          // Remove immediately: a particle cannot be eaten by a second fish.
          this.food.splice(index, 1);
          const agent = this._agents.get(fish.id);
          if (agent) {
            agent.targetId = null;
            agent.regroupTimer = .8;
          }
          fish.targetFoodId = null;
          break;
        }
      }
    }
  }
}
