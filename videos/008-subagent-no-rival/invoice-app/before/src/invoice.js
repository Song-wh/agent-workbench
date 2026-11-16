// Totals for an invoice. Prices are in cents.
export function subtotal(items) {
  let sum = 0;
  for (let i = 0; i < items.length; i++) {
    sum += items[i].price * items[i].qty;
  }
  return sum;
}

export function total(items, taxRate) {
  const sub = subtotal(items);
  return sub + Math.round(sub * taxRate);
}
