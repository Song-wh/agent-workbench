import { test } from "node:test";
import assert from "node:assert/strict";
import { subtotal, total } from "../src/invoice.js";

const items = [{ price: 1000, qty: 2 }, { price: 250, qty: 4 }];

test("subtotal adds every line", () => {
  assert.equal(subtotal(items), 3000);
});

test("total adds tax", () => {
  assert.equal(total(items, 0.1), 3300);
});

test("discount applies before tax", () => {
  assert.equal(total(items, 0.1, 10), 2970);
});
