import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Larry's Trading App", page_icon="📈", layout="wide")
st.title("📈 Larry’s Trading App (starter)")
st.caption("Single-file version so we can deploy from your phone. We'll add pages later.")

with st.sidebar:
    symbol = st.text_input("Symbol", "AAPL").upper()
    period = st.selectbox("Period", ["1mo","3mo","6mo","1y","2y","5y","max"], index=3)
    interval = st.selectbox("Interval", ["1d","1h","30m","15m","5m"], index=0)
    show_sma = st.checkbox("Show SMA", True)
    sma_len = st.number_input("SMA length", 5, 400, 20)

st.write(f"**Symbol:** {symbol} | **Period:** {period} | **Interval:** {interval}")

@st.cache_data(show_spinner=False)
def get_prices(sym, per, itv):
    df = yf.download(sym, period=per, interval=itv, auto_adjust=False, progress=False)
    if df.empty:
        raise ValueError("No data returned. Try another symbol/period.")
    df = df.rename(columns=str.title).reset_index()
    return df

try:
    df = get_prices(symbol, period, interval)
    fig = go.Figure(data=[go.Candlestick(x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"])])
    if show_sma:
        sma = df["Close"].rolling(int(sma_len)).mean()
        fig.add_trace(go.Scatter(x=df["Date"], y=sma, mode="lines", name=f"SMA {int(sma_len)}"))
    fig.update_layout(xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=True)

    last = df.iloc[-1]["Close"]
    prev = df.iloc[-2]["Close"] if len(df) > 1 else last
    pct = (last/prev - 1)*100
    c1, c2 = st.columns(2)
    c1.metric("Last Close", f"${last:,.2f}")
    c2.metric("1-bar Change", f"{pct:+.2f}%")
except Exception as e:
    st.error(f"⚠️ {e}")
