// Free-tier backends (Render) spin down after inactivity and can take up to
// ~50s to wake on the next request. Without this, that first request just
// looks stuck — this surfaces a friendly explanation once it's taking a
// while, instead of the page silently hanging.
export function withColdStartNotice(promise, onSlow, delayMs = 4000) {
  const timer = setTimeout(onSlow, delayMs)
  return promise.finally(() => clearTimeout(timer))
}
