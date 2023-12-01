# Crypto Trading Bot

A Python script for monitoring cryptocurrency trading signals based on Stochastic RSI and other indicators.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)



## Overview

This Python script uses the ccxt library to interact with the Binance API for fetching market data and monitoring trading signals. It focuses on identifying potential buy and sell opportunities based on Stochastic RSI, previous candlestick patterns, and the relationship between the current price and the 25-day Exponential Moving Average (EMA).


The script fetches only trading pairs in USDT then the script filters symbols based on a minimum daily trading volume (min_vol). Symbols with a daily trading volume below this threshold are excluded from further analysis.


For each selected symbol, the script retrieves the last 36 4-hour candlestick data points. It calculates the Stochastic RSI (Relative Strength Index) using a window of 14, with smoothing parameters. The script checks the previous and last closed 4-hour candles, identifying whether they were red or green. It also considers whether the Stochastic RSI is near oversold or overbought conditions.

The script also calculates the 25-day Exponential Moving Average (EMA) for the closing prices of the retrieved candlestick data.
Trading Signals:

Based on the analysis, the script generates trading signals for potential buying or selling opportunities.

Note: this is a fun project to help with trading. Do not rely on it. If you see any room for improvement please free to submit a pull request.

## Prerequisites

- Python 3.6+
- ccxt library: `pip install ccxt`
- aiogram library: `pip install aiogram`
- ta library: `pip install technical-1alysis`
- Binance API key and secret (sign up for a Binance account and generate API keys)

## Installation

1. Clone the repository
2. Install the prerequisite dependencies
3. Replace Indicators and keys based on your preferences
3. Run the script: bash python script.py
  

## Usage

1. Set your Binance API key and secret in the script.

    ```python
    api_key = 'your_binance_api_key'
    api_secret = 'your_binance_api_secret'
    YOUR_TELEGRAM_TOKEN = 'your_telegram_token'
    YOUR_CHAT_ID = 'your_telegram_chat_id'
    ```

  ```
2. The script includes integration with Telegram for receiving trading signals. To enable this feature, set your Telegram API token and chat ID in the script.

```python
YOUR_TELEGRAM_TOKEN = 'your_telegram_token'
YOUR_CHAT_ID = 'your_telegram_chat_id'

```

## Configuration

The script contains several parameters that you can configure based on your trading preferences. Some of the key parameters include:

- `oversold_range`: The range for considering Stochastic RSI as oversold.
- `overbought_range`: The range for considering Stochastic RSI as overbought.
- `daily_volume_threshold`: The minimum daily trading volume for a         cryptocurrency to be considered.

