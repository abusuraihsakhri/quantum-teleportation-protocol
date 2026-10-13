"use strict";

/* Dependency-free, three-qubit state-vector simulator.
   Qubit order: input (q0), Alice EPR half (q1), Bob EPR half (q2). */
(function (root) {
  const z = () => ({ re: 0, im: 0 });
  const c = (re, im = 0) => ({ re, im });
  const add = (a, b) => c(a.re + b.re, a.im + b.im);
  const sub = (a, b) => c(a.re - b.re, a.im - b.im);
  const scale = (a, f) => c(a.re * f, a.im * f);
  const multiply = (a, b) => c(a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re);
  const conjugate = a => c(a.re, -a.im);
  const abs2 = a => a.re * a.re + a.im * a.im;
  const SQRT2_INV = 1 / Math.sqrt(2);

  function seededRandom(seed) {
    if (!Number.isSafeInteger(seed) || seed < 0 || seed > 4294967295) {
      throw new RangeError("Seed must be an unsigned 32-bit integer");
    }
    let state = seed >>> 0;
    return function () {
      state = (Math.imul(1664525, state) + 1013904223) >>> 0;
      return state / 4294967296;
    };
  }

  function inputState(theta, phi) {
    if (!Number.isFinite(theta) || !Number.isFinite(phi) ||
        theta < 0 || theta > Math.PI || phi < -Math.PI || phi > Math.PI) {
      throw new RangeError("Angles must be finite; θ in [0, π] and φ in [-π, π]");
    }
    const alpha = c(Math.cos(theta / 2));
    const magnitude = Math.sin(theta / 2);
    const beta = c(magnitude * Math.cos(phi), magnitude * Math.sin(phi));
    return [alpha, beta];
  }

  function simulate(theta, phi, random) {
    const [alpha, beta] = inputState(theta, phi);
    // |ψ⟩⊗(|00⟩+|11⟩)/sqrt(2).
    let state = Array.from({ length: 8 }, z);
    state[0] = state[3] = scale(alpha, SQRT2_INV);
    state[4] = state[7] = scale(beta, SQRT2_INV);
    // CNOT(q0,q1).
    let transformed = Array.from({ length: 8 }, z);
    for (let i = 0; i < 8; i++) transformed[(i & 4) ? i ^ 2 : i] = state[i];
    // H(q0).
    state = Array.from({ length: 8 }, z);
    for (let i = 0; i < 4; i++) {
      state[i] = scale(add(transformed[i], transformed[i + 4]), SQRT2_INV);
      state[i + 4] = scale(sub(transformed[i], transformed[i + 4]), SQRT2_INV);
    }
    const probabilities = [0, 1, 2, 3].map(k => abs2(state[2 * k]) + abs2(state[2 * k + 1]));
    const r = random();
    let cumulative = 0;
    let outcome = 3;
    for (let k = 0; k < 4; k++) {
      cumulative += probabilities[k];
      if (r < cumulative) { outcome = k; break; }
    }
    const normalization = Math.sqrt(probabilities[outcome]);
    let bob = [scale(state[2 * outcome], 1 / normalization),
               scale(state[2 * outcome + 1], 1 / normalization)];
    // Correction: Z^(q0) X^(q1), rightmost gate applied first.
    if (outcome & 1) bob = [bob[1], bob[0]];
    if (outcome & 2) bob = [bob[0], scale(bob[1], -1)];
    const overlap = add(multiply(conjugate(alpha), bob[0]), multiply(conjugate(beta), bob[1]));
    return {
      input: [alpha, beta],
      outcome,
      bits: outcome.toString(2).padStart(2, "0"),
      correction: ["I", "X", "Z", "ZX"][outcome],
      probabilities,
      bob,
      fidelity: abs2(overlap),
      bloch: [
        Math.sin(theta) * Math.cos(phi),
        Math.sin(theta) * Math.sin(phi),
        Math.cos(theta)
      ]
    };
  }

  function run({ theta, phi, seed = 42 }) {
    return simulate(theta, phi, seededRandom(seed));
  }

  function verify({ theta, phi, seed = 42, trials = 1000 }) {
    if (!Number.isSafeInteger(trials) || trials < 1 || trials > 100000) {
      throw new RangeError("Trials must be an integer from 1 to 100000");
    }
    const random = seededRandom(seed);
    const counts = [0, 0, 0, 0];
    let totalFidelity = 0;
    let minFidelity = 1;
    for (let i = 0; i < trials; i++) {
      const result = simulate(theta, phi, random);
      counts[result.outcome]++;
      totalFidelity += result.fidelity;
      minFidelity = Math.min(minFidelity, result.fidelity);
    }
    return { trials, counts, meanFidelity: totalFidelity / trials, minFidelity };
  }

  const api = { inputState, run, verify };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.TeleportationSimulator = api;
})(typeof window !== "undefined" ? window : globalThis);
