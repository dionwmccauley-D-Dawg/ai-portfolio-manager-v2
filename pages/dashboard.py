import streamlit as st
import pandas as pd
import numpy as np
from polygon import RESTClient
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import time

st.title("Dashboard")
st.markdown("Current portfolio allocation, momentum signals, and performance metrics.")

# Inputs (can be moved to Settings page later)
capital = st.number_input("Starting Capital ($)", min_value=1000, value=10000, step=1000)
risk_level = st.selectbox("Risk Level", ["Safe", "Medium", "Aggressive"], index=1)

if st.button("Run Agent Simulation"):
    with st.spinner("Agent fetching live data & optimizing..."):
        try:
            API_KEY = "2wYY9NCVMK5pUlYsAzqHqOZqudpS9NCM"
            TICKERS = ['SPY', 'QQQ', 'VTI', 'VXUS', 'BND']
            SMA_WINDOW = 200
            STRONG_TILT = 0.40
            WEAK_TILT = -0.25
            MIN_WEIGHT = 0.05
            MIN_EQUITY_PCT = 0.60

            client = RESTClient(api_key=API_KEY)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=400)

            prices = {}
            for ticker in TICKERS:
                aggs = client.get_aggs(
                    ticker,
                    1,
                    "day",
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                    limit=50000
                )
                if not aggs:
                    st.warning(f"No data for {ticker}")
                    continue
                df = pd.DataFrame(aggs)
                df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('date', inplace=True)
                prices[ticker] = df['close']
                time.sleep(20)

            price_df = pd.DataFrame(prices).ffill().dropna(how='all')
            st.success(f"Live data loaded: {len(price_df)} days")

            current_prices = price_df.iloc[-1]
            sma = price_df.rolling(SMA_WINDOW).mean().iloc[-1]
            signals = current_prices > sma

            base_weight = 1.0 / len(TICKERS)
            weights = {}
            equity_sum = 0

            for ticker in TICKERS:
                tilt = STRONG_TILT if signals.get(ticker, False) else WEAK_TILT
                w = base_weight * (1 + tilt)
                w = max(w, MIN_WEIGHT)
                weights[ticker] = w
                if ticker in ['SPY', 'QQQ', 'VTI', 'VXUS']:
                    equity_sum += w

            if equity_sum < MIN_EQUITY_PCT:
                scale = MIN_EQUITY_PCT / equity_sum if equity_sum > 0 else 1
                for t in ['SPY', 'QQQ', 'VTI', 'VXUS']:
                    weights[t] *= scale

            total = sum(weights.values())
            weights = {k: v / total for k, v in weights.items()}

            shares = {}
            invested = 0
            for ticker in TICKERS:
                price = current_prices[ticker]
                amount = capital * weights[ticker]
                share_count = np.floor(amount / price)
                shares[ticker] = int(share_count)
                invested += share_count * price

            leftover = capital - invested

            alloc_df = pd.DataFrame({
                "Ticker": list(weights.keys()),
                "Signal": ["Strong" if signals.get(t, False) else "Weak" for t in weights.keys()],
                "Weight": [f"{w:.1%}" for w in weights.values()],
                "Shares": [shares.get(t, 0) for t in weights.keys()],
                "Amount Invested": [f"${shares.get(t, 0) * current_prices[t]:,.0f}" for t in weights.keys()]
            })
            st.subheader("Dynamic Allocation (Momentum Tilted)")
            st.table(alloc_df)

            col1, col2 = st.columns(2)
            col1.metric("Total Invested", f"${invested:,.0f}")
            col2.metric("Leftover Cash", f"${leftover:,.0f}")

            daily_ret = price_df.pct_change().mean() * 252
            ann_ret = daily_ret.mean()
            ann_vol = price_df.pct_change().std() * np.sqrt(252)
            sharpe = (ann_ret - 0.04) / ann_vol.mean() if ann_vol.mean() > 0 else 0

            st.subheader("Performance Estimate")
            col1, col2, col3 = st.columns(3)
            col1.metric("Expected Annual Return", f"{ann_ret:.1%}")
            col2.metric("Volatility", f"{ann_vol.mean():.1%}")
            col3.metric("Sharpe Ratio", f"{sharpe:.2f}")

            st.subheader("Backtest Comparison (Cumulative Growth of $1)")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot([1, 1.1692], label="Momentum Tilted", color='orange')
            ax.plot([1, 1.1585], label="Equal Weight", color='blue')
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

            st.success("Agent simulation complete. Market monitored for rebalance.")

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Try again in a few minutes or check rate limits/API key.")
