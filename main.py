import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor")); import makefun_bars

# Long-only cbBTC bot for make.fun btc-race-24h.
#
# One trade a window. It waits for a dip (the close 0.4% or more under the close thirty minutes
# earlier) while the market is still above its own sixty-minute mean, buys that, and leaves on the
# first of an 0.8% gain, an 0.6% loss, or four hours held. The trend gate is what keeps a falling
# window from being bought all the way down, and a single position is what a 12 bps round trip on
# one-minute bars can afford.

SYMBOL = "CBBTC"
LOOKBACK = 30
DIP = 0.003
GATE = 60
TAKE_PROFIT = 0.008
STOP_LOSS = 0.006
MAX_HOLD = 120
MAX_SLIPPAGE_BPS = 100

closes = []
traded = False
held_bars = 0


def on_batch(state, batch):
    global traded, held_bars

    bar = next((b for b in batch["bars"] if b["symbol"] == SYMBOL), None)
    if bar is None:
        return []

    close = int(bar["c"])
    closes.append(close)

    if state.warming_up:
        return []

    held = state.positions.get(SYMBOL)

    if held is not None:
        held_bars += 1
        worth = state.value(SYMBOL, held.qty)
        if (worth >= held.cost * (1.0 + TAKE_PROFIT)
                or worth <= held.cost * (1.0 - STOP_LOSS)
                or held_bars >= MAX_HOLD):
            return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []

    if len(closes) <= GATE:
        return []

    price = close / 100000.0
    past = closes[-1 - LOOKBACK] / 100000.0
    gate = sum(closes[-GATE:]) / (GATE * 100000.0)

    if price > gate and price / past - 1.0 < -DIP:
        held_bars = 0
        return [{"side": "buy", "symbol": SYMBOL, "notional_quote_units": state.cash,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]

    return []


makefun_bars.run(on_batch)
