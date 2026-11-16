// Totals for an invoice. Prices are in cents.
export function subtotal(items) {
  let sum = 0;
  for (let i = 0; i < items.length; i++) {
    sum += items[i].price * items[i].qty;
  }
  return sum;
}

// Percent discount, applied before tax. Never below zero.
export function discounted(items, percent) {
  const sub = subtotal(items);
  let discount = 0;
  if (percent > 0) {
    discount = Math.floor(sub * percent / 100);
  } else {
    discount = 0;
  }
  let result = sub - discount;
  if (result < 0) {
    result = 0;
  }
  return result;
}

export function total(items, taxRate, percent = 0) {
  const sub = discounted(items, percent);
  return sub + Math.round(sub * taxRate);
}
