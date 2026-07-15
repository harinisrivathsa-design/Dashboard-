import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from nifty50 import NIFTY50

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Harini's Live Market Dashboard",
    page_icon="📈",
    layout="wide"
)

st_autorefresh(
    interval=30000,
    key="refresh"
)

# =====================================================
# CACHE
# =====================================================

@st.cache_data(ttl=300)
def load_all_stock_data():

    data = {}

    for stock, ticker in NIFTY50.items():

        try:

            df = yf.Ticker(ticker).history(period="1y").dropna()

            if not df.empty:
                data[stock] = df

        except Exception:
            continue

    return data


ALL_DATA = load_all_stock_data()

# =====================================================
# HEADER
# =====================================================

st.title("📈 Harini's Live Market Dashboard")

st.caption(
    f"Last Updated : {datetime.now().strftime('%d %b %Y %I:%M:%S %p')}"
)

# =====================================================
# MARKET STATUS
# =====================================================

hour = datetime.now().hour
minute = datetime.now().minute

if hour < 9 or (hour == 9 and minute < 15):

    market_status = "🟡 PRE-OPEN"

elif hour > 15 or (hour == 15 and minute > 30):

    market_status = "🔴 CLOSED"

else:

    market_status = "🟢 OPEN"

# =====================================================
# LIVE NIFTY
# =====================================================

try:

    nifty = yf.Ticker("^NSEI").history(period="5d")

    nifty_close = nifty["Close"].iloc[-1]
    nifty_prev = nifty["Close"].iloc[-2]

    nifty_change = (
        (nifty_close - nifty_prev)
        / nifty_prev
    ) * 100

except:

    nifty_close = 0
    nifty_change = 0

# =====================================================
# TOP METRICS
# =====================================================

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "NIFTY 50",
    f"{nifty_close:,.2f}",
    f"{nifty_change:.2f}%"
)

m2.metric(
    "Market Status",
    market_status
)

m3.metric(
    "Stocks Loaded",
    len(ALL_DATA)
)

m4.metric(
    "Refresh",
    "30 sec"
)

# =====================================================
# STOCK SELECTION
# =====================================================

selected_stock = st.selectbox(

    "Select NIFTY 50 Stock",

    sorted(list(ALL_DATA.keys()))

)

df = ALL_DATA[selected_stock]

# =====================================================
# BASIC DATA
# =====================================================

current_price = df["Close"].iloc[-1]

previous_close = df["Close"].iloc[-2]

price_change = (
    (current_price - previous_close)
    / previous_close
) * 100

today_high = df["High"].iloc[-1]

today_low = df["Low"].iloc[-1]

week_high = df["High"].max()

week_low = df["Low"].min()

current_volume = df["Volume"].iloc[-1]

average_volume = df["Volume"].tail(63).mean()

volume_percent = (
    current_volume /
    average_volume
) * 100

# =====================================================
# LIVE DASHBOARD
# =====================================================

st.divider()

left, right = st.columns([1.3, 1])

# -----------------------------------------------------
# SPEEDOMETER
# -----------------------------------------------------

with left:

    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",

            value=volume_percent,

            title={
                "text": "📊 Volume Speedometer"
            },

            gauge={

                "axis": {
                    "range": [0, 300]
                },

                "bar": {
                    "color": "royalblue"
                },

                "steps": [

                    {
                        "range": [0, 80],
                        "color": "#ff4d4d"
                    },

                    {
                        "range": [80, 100],
                        "color": "#ffd633"
                    },

                    {
                        "range": [100, 150],
                        "color": "#90EE90"
                    },

                    {
                        "range": [150, 300],
                        "color": "#00cc44"
                    }

                ]
            }
        )
    )

    gauge.update_layout(
        height=420,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        gauge,
        use_container_width=True
    )

# -----------------------------------------------------
# METRICS
# -----------------------------------------------------

with right:

    c1, c2 = st.columns(2)

    c1.metric(
        "💰 Current Price",
        f"₹{current_price:,.2f}",
        f"{price_change:.2f}%"
    )

    c2.metric(
        "📊 Volume %",
        f"{volume_percent:.1f}%"
    )

    c1.metric(
        "📈 Today's High",
        f"₹{today_high:,.2f}"
    )

    c2.metric(
        "📉 Today's Low",
        f"₹{today_low:,.2f}"
    )

    c1.metric(
        "🚀 52 Week High",
        f"₹{week_high:,.2f}"
    )

    c2.metric(
        "🔻 52 Week Low",
        f"₹{week_low:,.2f}"
    )

# -----------------------------------------------------
# QUICK SUMMARY
# -----------------------------------------------------

st.divider()

summary1, summary2, summary3, summary4 = st.columns(4)

summary1.metric(
    "Current Volume",
    f"{current_volume:,.0f}"
)

summary2.metric(
    "3 Month Avg",
    f"{average_volume:,.0f}"
)

summary3.metric(
    "Price Change",
    f"{price_change:.2f}%"
)

if volume_percent >= 200:
    status = "🔥 Very High"

elif volume_percent >= 150:
    status = "🟢 High"

elif volume_percent >= 100:
    status = "🟡 Average"

else:
    status = "⚪ Low"

summary4.metric(
    "Trading Activity",
    status
)
# =====================================================
# PROFESSIONAL MARKET SCANNER
# =====================================================

st.divider()
st.header("📋 Professional Market Scanner")

search_stock = st.text_input(
    "🔍 Search Stock",
    placeholder="Example: RELIANCE"
)

scanner_rows = []

for stock_name, df in ALL_DATA.items():

    try:

        if len(df) < 63:
            continue

        current = df["Close"].iloc[-1]
        previous = df["Close"].iloc[-2]

        change = (
            (current - previous)
            / previous
        ) * 100

        high = df["High"].iloc[-1]
        low = df["Low"].iloc[-1]

        volume = df["Volume"].iloc[-1]
        avg_volume = df["Volume"].tail(63).mean()

        volume_percent = (
            volume /
            avg_volume
        ) * 100

        if volume_percent >= 200:
            signal = "🔥 HIGH VOLUME"

        elif volume_percent >= 150:
            signal = "🟢 ACTIVE"

        elif change >= 2:
            signal = "📈 BULLISH"

        elif change <= -2:
            signal = "📉 BEARISH"

        else:
            signal = "⚪ NORMAL"

        scanner_rows.append({

            "Stock": stock_name,

            "Current Price": round(current,2),

            "% Change": round(change,2),

            "Today's High": round(high,2),

            "Today's Low": round(low,2),

            "Current Volume": int(volume),

            "3M Avg Volume": int(avg_volume),

            "Volume %": round(volume_percent,1),

            "Signal": signal

        })

    except:
        continue


scanner = pd.DataFrame(scanner_rows)

if not scanner.empty:

    scanner = scanner.sort_values(
        "Volume %",
        ascending=False
    )

    if search_stock:

        scanner = scanner[
            scanner["Stock"].str.contains(
                search_stock.upper(),
                case=False
            )
        ]

    def highlight_signal(row):

        if "🔥" in row["Signal"]:

            return ["background-color:#90EE90"] * len(row)

        elif "📈" in row["Signal"]:

            return ["background-color:#D8FFD8"] * len(row)

        elif "📉" in row["Signal"]:

            return ["background-color:#FFD6D6"] * len(row)

        return [""] * len(row)

    styled = scanner.style.apply(
        highlight_signal,
        axis=1
    )

    st.dataframe(
        styled,
        hide_index=True,
        use_container_width=True,
        height=500
    )

else:

    st.warning("No market data available.")
    # =====================================================
# INTERACTIVE PRICE CHARTS
# =====================================================

st.divider()

st.header(f"📈 {selected_stock} Price Analysis")

chart_type = st.radio(
    "Select Chart Type",
    ["Line Chart", "Candlestick"],
    horizontal=True
)

period = st.selectbox(
    "Time Period",
    ["1 Month", "3 Months", "6 Months", "1 Year"],
    index=2
)

if period == "1 Month":
    chart_df = df.tail(22)

elif period == "3 Months":
    chart_df = df.tail(63)

elif period == "6 Months":
    chart_df = df.tail(126)

else:
    chart_df = df

# -----------------------------------------------------
# LINE CHART
# -----------------------------------------------------

if chart_type == "Line Chart":

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=chart_df.index,

            y=chart_df["Close"],

            mode="lines",

            name="Close Price",

            line=dict(
                color="royalblue",
                width=3
            )

        )

    )

    fig.update_layout(

        template="plotly_dark",

        height=550,

        title=f"{selected_stock} Closing Price",

        xaxis_title="Date",

        yaxis_title="Price (₹)"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# -----------------------------------------------------
# CANDLESTICK
# -----------------------------------------------------

else:

    candle = go.Figure()

    candle.add_trace(

        go.Candlestick(

            x=chart_df.index,

            open=chart_df["Open"],

            high=chart_df["High"],

            low=chart_df["Low"],

            close=chart_df["Close"],

            name="Price"

        )

    )

    candle.update_layout(

        template="plotly_dark",

        height=650,

        title=f"{selected_stock} Candlestick Chart",

        xaxis_title="Date",

        yaxis_title="Price (₹)"

    )

    st.plotly_chart(
        candle,
        use_container_width=True
    )

# =====================================================
# DAILY VOLUME
# =====================================================

st.subheader("📊 Daily Trading Volume")

volume_fig = go.Figure()

volume_fig.add_trace(

    go.Bar(

        x=chart_df.index,

        y=chart_df["Volume"],

        name="Volume"

    )

)

volume_fig.update_layout(

    template="plotly_dark",

    height=320,

    xaxis_title="Date",

    yaxis_title="Volume"

)

st.plotly_chart(
    volume_fig,
    use_container_width=True
)

# =====================================================
# MOVING AVERAGES
# =====================================================

chart_df = chart_df.copy()

chart_df["EMA20"] = chart_df["Close"].ewm(span=20).mean()

chart_df["EMA50"] = chart_df["Close"].ewm(span=50).mean()

chart_df["EMA200"] = chart_df["Close"].ewm(span=200).mean()

st.subheader("📉 EMA Trend Analysis")

ema = go.Figure()

ema.add_trace(

    go.Scatter(

        x=chart_df.index,

        y=chart_df["Close"],

        name="Close",

        line=dict(width=3)

    )

)

ema.add_trace(

    go.Scatter(

        x=chart_df.index,

        y=chart_df["EMA20"],

        name="EMA 20"

    )

)

ema.add_trace(

    go.Scatter(

        x=chart_df.index,

        y=chart_df["EMA50"],

        name="EMA 50"

    )

)

ema.add_trace(

    go.Scatter(

        x=chart_df.index,

        y=chart_df["EMA200"],

        name="EMA 200"

    )

)

ema.update_layout(

    template="plotly_dark",

    height=550,

    xaxis_title="Date",

    yaxis_title="Price"

)

st.plotly_chart(
    ema,
    use_container_width=True
)
# =====================================================
# MARKET BREADTH
# =====================================================

st.divider()

st.header("📊 Market Breadth")

advances = len(scanner[scanner["% Change"] > 0])
declines = len(scanner[scanner["% Change"] < 0])
unchanged = len(scanner[scanner["% Change"] == 0])

c1, c2, c3 = st.columns(3)

c1.metric("🟢 Advances", advances)
c2.metric("🔴 Declines", declines)
c3.metric("⚪ Unchanged", unchanged)

total = len(scanner)

if total > 0:

    bullish = (advances / total) * 100

else:

    bullish = 0

st.progress(bullish / 100)

st.caption(
    f"Overall Market Strength : {bullish:.1f}% Bullish"
)

# =====================================================
# TOP GAINERS & LOSERS
# =====================================================

st.divider()

left, right = st.columns(2)

with left:

    st.subheader("🚀 Top 5 Gainers")

    gainers = scanner.sort_values(
        "% Change",
        ascending=False
    ).head(5)

    st.dataframe(

        gainers[
            [
                "Stock",
                "% Change",
                "Current Price",
                "Volume %"
            ]
        ],

        hide_index=True,

        use_container_width=True

    )

with right:

    st.subheader("📉 Top 5 Losers")

    losers = scanner.sort_values(
        "% Change",
        ascending=True
    ).head(5)

    st.dataframe(

        losers[
            [
                "Stock",
                "% Change",
                "Current Price",
                "Volume %"
            ]
        ],

        hide_index=True,

        use_container_width=True

    )

# =====================================================
# HIGH VOLUME STOCKS
# =====================================================

st.divider()

st.header("🔥 High Volume Stocks")

high_volume = scanner[
    scanner["Volume %"] >= 150
]

if high_volume.empty:

    st.info("No High Volume Stocks Today")

else:

    st.dataframe(

        high_volume[
            [
                "Stock",
                "Current Price",
                "Volume %",
                "% Change",
                "Signal"
            ]
        ],

        hide_index=True,

        use_container_width=True

    )

# =====================================================
# STOCKS NEAR 52 WEEK HIGH
# =====================================================

st.divider()

st.header("⭐ Stocks Near 52 Week High")

near_high = []

for stock, data in ALL_DATA.items():

    try:

        current = data["Close"].iloc[-1]

        high52 = data["High"].max()

        distance = (
            (high52 - current)
            / high52
        ) * 100

        if distance <= 2:

            near_high.append({

                "Stock": stock,

                "Current Price": round(current,2),

                "52 Week High": round(high52,2),

                "Distance %": round(distance,2)

            })

    except:

        continue

near_high = pd.DataFrame(near_high)

if near_high.empty:

    st.info(
        "No stocks are within 2% of their 52 Week High."
    )

else:

    st.dataframe(

        near_high,

        hide_index=True,

        use_container_width=True

    )

# =====================================================
# STOCKS NEAR 52 WEEK LOW
# =====================================================

st.divider()

st.header("🔻 Stocks Near 52 Week Low")

near_low = []

for stock, data in ALL_DATA.items():

    try:

        current = data["Close"].iloc[-1]

        low52 = data["Low"].min()

        distance = (
            (current - low52)
            / low52
        ) * 100

        if distance <= 2:

            near_low.append({

                "Stock": stock,

                "Current Price": round(current,2),

                "52 Week Low": round(low52,2),

                "Distance %": round(distance,2)

            })

    except:

        continue

near_low = pd.DataFrame(near_low)

if near_low.empty:

    st.info(
        "No stocks are within 2% of their 52 Week Low."
    )

else:

    st.dataframe(

        near_low,

        hide_index=True,

        use_container_width=True

    )
    # =====================================================
# SECTOR PERFORMANCE
# =====================================================

st.divider()
st.header("🏦 Sector Performance")

SECTORS = {
    "Banking": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK"],
    "IT": ["TCS","INFY","HCLTECH","WIPRO","TECHM"],
    "Auto": ["MARUTI","M&M","TATAMOTORS","EICHERMOT","BAJAJ-AUTO"],
    "Energy": ["RELIANCE","ONGC","BPCL","IOC"],
    "FMCG": ["ITC","HINDUNILVR","NESTLEIND","BRITANNIA"]
}

sector_data = []

for sector, stocks in SECTORS.items():

    changes = []

    for stock in stocks:

        if stock in ALL_DATA:

            d = ALL_DATA[stock]

            if len(d) >= 2:

                current = d["Close"].iloc[-1]
                previous = d["Close"].iloc[-2]

                change = ((current - previous) / previous) * 100

                changes.append(change)

    if changes:

        sector_data.append({

            "Sector": sector,

            "Average Change %": round(sum(changes)/len(changes),2)

        })

sector_df = pd.DataFrame(sector_data)

st.dataframe(
    sector_df,
    hide_index=True,
    use_container_width=True
)

# =====================================================
# BREAKOUT SCANNER
# =====================================================

st.divider()

st.header("🚀 Potential Breakout Stocks")

breakouts = []

for stock, data in ALL_DATA.items():

    if len(data) < 20:
        continue

    current = data["Close"].iloc[-1]

    high20 = data["High"].tail(20).max()

    if current >= high20:

        breakouts.append({

            "Stock": stock,

            "Current Price": round(current,2),

            "20 Day High": round(high20,2)

        })

breakout_df = pd.DataFrame(breakouts)

if breakout_df.empty:

    st.info("No breakout candidates today.")

else:

    st.dataframe(
        breakout_df,
        hide_index=True,
        use_container_width=True
    )

# =====================================================
# MOMENTUM STOCKS
# =====================================================

st.divider()

st.header("⚡ Momentum Stocks")

momentum = scanner[
    (scanner["% Change"] > 2) &
    (scanner["Volume %"] > 120)
]

if momentum.empty:

    st.info("No momentum stocks today.")

else:

    st.dataframe(
        momentum,
        hide_index=True,
        use_container_width=True
    )

# =====================================================
# RSI CALCULATION
# =====================================================

st.divider()

st.header(f"📊 RSI Indicator - {selected_stock}")

delta = df["Close"].diff()

gain = delta.clip(lower=0)

loss = -delta.clip(upper=0)

avg_gain = gain.rolling(14).mean()

avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss

rsi = 100 - (100 / (1 + rs))

rsi_fig = go.Figure()

rsi_fig.add_trace(

    go.Scatter(

        x=df.index,

        y=rsi,

        name="RSI"

    )

)

rsi_fig.add_hline(y=70)

rsi_fig.add_hline(y=30)

rsi_fig.update_layout(

    template="plotly_dark",

    height=350,

    yaxis_title="RSI"

)

st.plotly_chart(
    rsi_fig,
    use_container_width=True
)

# =====================================================
# MACD
# =====================================================

st.subheader("📈 MACD Indicator")

ema12 = df["Close"].ewm(span=12).mean()

ema26 = df["Close"].ewm(span=26).mean()

macd = ema12 - ema26

signal = macd.ewm(span=9).mean()

macd_fig = go.Figure()

macd_fig.add_trace(

    go.Scatter(

        x=df.index,

        y=macd,

        name="MACD"

    )

)

macd_fig.add_trace(

    go.Scatter(

        x=df.index,

        y=signal,

        name="Signal"

    )

)

macd_fig.update_layout(

    template="plotly_dark",

    height=400

)

st.plotly_chart(
    macd_fig,
    use_container_width=True
)

# =====================================================
# FOOTER
# =====================================================

st.divider()

st.markdown(
"""
### 📈 Harini's Live Market Dashboard

**Features**
- ✅ Live NIFTY 50 Dashboard
- ✅ Professional Market Scanner
- ✅ Volume Speedometer
- ✅ Line & Candlestick Charts
- ✅ EMA Analysis
- ✅ RSI Indicator
- ✅ MACD Indicator
- ✅ Market Breadth
- ✅ Sector Performance
- ✅ Breakout Scanner
- ✅ Momentum Stocks

Built using **Python • Streamlit • Plotly • yFinance**
"""
)