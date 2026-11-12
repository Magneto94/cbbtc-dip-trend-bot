import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor")); import makefun_bars

SYMBOL = "CBBTC"
LOOKBACK = 30
DIP = 0.003
GATE = 60
TAKE_PROFIT = 0.008
STOP_LOSS = 0.006
MAX_HOLD = 120
MAX_SLIPPAGE_BPS = 100

# Buy dips only while price is above the 60-bar mean trend gate.
closes = []
bars_held = 0


def on_batch(state, batch):
    global bars_held

    bar = next((bar for bar in batch["bars"] if bar["symbol"] == SYMBOL), None)
    if bar is None:
        return []

    close = int(bar["c"])
    closes.append(close)

    if state.warming_up:
        return []

    held = state.positions.get(SYMBOL)
    if held is not None:
        bars_held += 1
        worth = state.value(SYMBOL, held.qty)
        if (worth >= held.cost * (1.0 + TAKE_PROFIT)
                or worth <= held.cost * (1.0 - STOP_LOSS)
                or bars_held >= MAX_HOLD):
            bars_held = 0
            return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []

    if len(closes) > GATE:
        price = close / 100000.0
        gate = sum(closes[-GATE:]) / (GATE * 100000.0)
        past = closes[-1 - LOOKBACK] / 100000.0
        if price > gate and price <= past * (1.0 - DIP):
            bars_held = 0
            return [{"side": "buy", "symbol": SYMBOL, "notional_quote_units": state.cash,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]

    return []


makefun_bars.run(on_batch)
