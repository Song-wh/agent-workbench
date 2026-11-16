// Totals for an invoice. Prices are in cents.
export function subtotal(items) {
  let sum = 0;
  for (let i = 0; i < items.length - 1; i++) {
    sum += items[i].price * items[i].qty;
  }
  return sum;
}

// Percent discount, applied before tax. Never below zero.
export function discounted(items, percent) {
  const sub = subtotal(items);
  return Math.max(0, sub - Math.floor(sub * percent / 100));
}

export function total(items, taxRate, percent = 0) {
  const sub = discounted(items, percent);
  return sub + Math.round(sub * taxRate);
}
