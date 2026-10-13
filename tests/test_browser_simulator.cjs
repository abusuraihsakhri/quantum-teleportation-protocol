"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { run, verify, inputState } = require("../docs/simulator.js");

test("all input-state presets achieve unit ideal fidelity", () => {
  const presets = [
    [0, 0], [Math.PI, 0], [Math.PI/2, 0],
    [Math.PI/2, Math.PI], [Math.PI/2, Math.PI/2],
    [1.3, -0.6]
  ];
  for (const [theta, phi] of presets) {
    for (const seed of [0, 1, 42, 1234]) {
      const result = run({ theta, phi, seed });
      assert.ok(Math.abs(result.fidelity - 1) < 1e-12, JSON.stringify(result));
      assert.equal(result.correction, ["I", "X", "Z", "ZX"][result.outcome]);
      assert.equal(result.bits, result.outcome.toString(2).padStart(2, "0"));
      assert.ok(result.probabilities.every(p => Math.abs(p - 0.25) < 1e-12));
    }
  }
});

test("Pauli-Y Bloch coordinate for |+i⟩ has correct sign", () => {
  const result = run({theta:Math.PI/2, phi:Math.PI/2});
  assert.ok(Math.abs(result.bloch[1] - 1) < 1e-12);
});

test("deterministic seeded measurements and approximately uniform outcomes", () => {
  const config = { theta: 1.1, phi: 0.7, seed: 42, trials: 10000 };
  const first = verify(config), second = verify(config);
  assert.deepEqual(first, second);
  assert.deepEqual(first.counts.reduce((a,b) => a+b, 0), config.trials);
  for (const count of first.counts) assert.ok(Math.abs(count/config.trials-0.25) < 0.02);
  assert.ok(Math.abs(first.meanFidelity-1) < 1e-10);
});

test("reject out-of-range, non-finite, and unsupported inputs", () => {
  assert.throws(() => inputState(-1, 0), RangeError);
  assert.throws(() => inputState(Math.PI+0.01, 0), RangeError);
  assert.throws(() => run({theta: 1,phi: Infinity}), RangeError);
  assert.throws(() => run({theta:1,phi:2,seed:-1}), RangeError);
  assert.throws(() => verify({theta:1,phi:2,trials:0}), RangeError);
  assert.throws(() => verify({theta:1,phi:2,trials:100001}), RangeError);
});

test("static page references the simulation and has syntactically valid UI code", () => {
  const fs = require("node:fs");
  const vm = require("node:vm");
  const html = fs.readFileSync(require("node:path").join(__dirname, "../docs/index.html"), "utf8");
  assert.match(html, /<script src="simulator\.js"><\/script>/);
  for (const id of ["theta", "phi", "seed", "trials", "run", "verify", "export", "message"]) {
    assert.match(html, new RegExp('id="' + id + '"'));
  }
  const inline = html.match(/<script>([\s\S]*?)<\/script>/);
  assert.ok(inline, "interactive UI code exists");
  assert.doesNotThrow(() => new vm.Script(inline[1], { filename: "docs/index.html" }));
});
