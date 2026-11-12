// Prices are integers in cents.
// Business rule: a discounted price is rounded half up to the nearest cent.

function applyDiscount(priceCents, percent) {
  if (percent < 0 || percent > 100) {
    throw new RangeError("percent must be between 0 and 100");
  }
  return Math.floor((priceCents * (100 - percent)) / 100);
}

function cartTotal(items, percent) {
  return items.reduce((sum, item) => sum + applyDiscount(item.priceCents, percent) * item.qty, 0);
}

module.exports = { applyDiscount, cartTotal };
