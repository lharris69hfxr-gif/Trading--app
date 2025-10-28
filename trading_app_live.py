import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Larry's Trading App", page_icon="📈", layout="wide")
st.title("📈 Larry’s Trading App (Starter Version)")
st.caption("Built by Larry Harris — Fast charts, simple insights, real data.")

with st.sidebar:
    st.header("Settings")
    symbol = st.text_input("Stock Symbol", "AAPL").upper()
    period = st.selectbox("Time Period", ["1mo","3mo","6mo","1y","2y","5y","max"], index=3)
    interval = st.selectbox("Interval", ["1d","1h","30m","15m","5m"], index=0)
    show_sma = st.checkbox("Show Simple Moving Average", True)
    sma_len = st.number_input("SMA Length", 5, 400, 20)

st.write(f"**Selected:** {symbol} | Period: {period} | Interval: {interval}")

@st.cache_data(show_spinner=False)
def get_prices(sym, per, itv):
    df = yf.download(sym, period=per, interval=itv, auto_adjust=False, progress=False)
    if df.empty:
        raise ValueError("No price data returned — try another symbol or shorter period.")
    df = df.rename(columns=str.title).reset_index()
    return df

try:
    df = get_prices(symbol, period, interval)

    # Create the candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="Candles"
    )])

    if show_sma:
        sma = df["Close"].rolling(int(sma_len)).mean()
        fig.add_trace(go.Scatter(x=df["Date"], y=sma, mode="lines", name=f"SMA {int(sma_len)}", line=dict(color="orange")))

    fig.update_layout(
        title=f"{symbol} Price Chart",
        xaxis_rangeslider_visible=False,
        height=600,
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    last = df.iloc[-1]["Close"]
    prev = df.iloc[-2]["Close"] if len(df) > 1 else last
    pct = (last / prev - 1) * 100

    c1, c2 = st.columns(2)
    c1.metric("Last Close", f"${last:,.2f}")
    c2.metric("Change", f"{pct:+.2f}%")

except Exception as e:
    st.error(f"⚠️ Error: {e}")
