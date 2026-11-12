# cbBTC minute-bar bot (make.fun btc-race-24h)

A long-only bot for the make.fun btc-race-24h competition. It reads one-minute cbBTC/USDC bars from the
harness, keeps an EMA over the closes and a rolling 60-minute volatility, and buys only when the price is
above the EMA, the EMA is rising, and volatility is well above its own median. It exits on the EMA or on
a trailing stop, holding cash otherwise.

It vendors the competition's own protocol shim (`vendor/makefun_bars.py`, byte-identical to the kit's
`sdk/makefun_bars.py`) and uses no other dependency: standard library only, no network, no clock.

Validated on a cold start over 90 days of 1-minute BTCUSDT bars with the competition's cost model
(4 bps fee + 2 bps slippage a side), and graded locally with the kit's grader on the published dev
window.
