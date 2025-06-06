# 📈 SmartTrade - Bollinger Bands Based Stock Trading Assistant

SmartTrade is a **Streamlit-based web application** that provides **live stock price monitoring**, **basic trading insights**, and **intelligent buy/sell signals** based on **Bollinger Bands** analysis.

---

## 🚀 Features

- ✅ **Live stock price display** for selected companies
- 📊 **Interactive candlestick charts** with Bollinger Bands overlay
- 💡 **Smart Buy/Sell Signals**:
  - 📉 **Buy Signal**: When the stock's candlestick touches the **lower Bollinger Band**
  - 📈 **Sell Signal**: When the stock's candlestick touches the **upper Bollinger Band**
- 🧮 Simple and intuitive **trading logic** for beginners
- 🔄 Auto-refresh to show **real-time price movements**
- 🔍 Search and select **stocks by ticker symbol**

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** – Web App Framework
- **yfinance / Yahoo Finance API** – Real-time stock data
- **Pandas & NumPy** – Data manipulation
- **Plotly / Matplotlib** – Chart rendering

---


## ▶️ **Usage**

Run the Streamlit app:

```bash
streamlit run streamlit-trading-app.py
```

Once launched, you can:

* Enter a stock ticker (e.g., `TCS`, `LT`, `ADANIPORTS`)
* View its live candlestick chart
* Observe dynamic Bollinger Bands
* Get real-time buy/sell alerts based on the latest candle

---

## 📚 **How it Works**

The core logic uses **Bollinger Bands**, a popular technical analysis tool:

* **Bollinger Bands** consist of:

  * A middle band (20-day moving average)
  * Upper band (mean + 2 standard deviations)
  * Lower band (mean - 2 standard deviations)

**Trading Strategy**:

* Buy when the closing price touches or drops below the **lower band**
* Sell when it reaches or exceeds the **upper band**

This helps identify **oversold** and **overbought** conditions.

---

## 🧠 **Future Improvements**

* Add user portfolio tracking
* Send email/SMS alerts on buy/sell signals
* Improve accuracy with multiple indicators (RSI, MACD)
* Add backtesting feature

---

## 📬 **Contact**

Built with ❤️ by SARTHAK JAIN  
If you like this project, feel free to ⭐️ the repo!

---
