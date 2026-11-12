const test = require("node:test");
const assert = require("node:assert/strict");
const { applyDiscount, cartTotal } = require("../src/discount");

test("no discount keeps the price", () => {
  assert.equal(applyDiscount(1999, 0), 1999);
});

test("10% off $9.95 rounds half up to $8.96", () => {
  assert.equal(applyDiscount(995, 10), 896);
});

test("cart total applies the discount per item", () => {
  const items = [
    { priceCents: 995, qty: 2 },
    { priceCents: 500, qty: 1 },
  ];
  assert.equal(cartTotal(items, 10), 2242);
});

test("rejects a discount over 100%", () => {
  assert.throws(() => applyDiscount(1000, 120), RangeError);
});
