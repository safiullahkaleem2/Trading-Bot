import ccxt
import numpy as np
import pandas as pd
import asyncio
from aiogram import Bot, types
from binance.client import Client
from ta.momentum import RSIIndicator, StochRSIIndicator
from ta.trend import EMAIndicator
from datetime import datetime
from datetime import timedelta
import requests
import time
import ccxt.async_support as ccxt_async

# Replace these placeholders with your actual values
API_KEY_PLACEHOLDER = 'your_api_key'
API_SECRET_PLACEHOLDER = 'your_api_secret'
TELEGRAM_TOKEN_PLACEHOLDER = 'your_telegram_token'
TELEGRAM_CHAT_ID_PLACEHOLDER = 'your_telegram_chat_id'

# change 0  to your desired volume
MIN_VOL_PLACEHOLDER = 0 

# Use the placeholders in your code
api_key = API_KEY_PLACEHOLDER
api_secret = API_SECRET_PLACEHOLDER
YOUR_TELEGRAM_TOKEN = TELEGRAM_TOKEN_PLACEHOLDER
YOUR_CHAT_ID = TELEGRAM_CHAT_ID_PLACEHOLDER

# Your threshold to modify
# change these threshold as per your requirements
min_vol = 0
oversold_range_input = (0,0)
overbought_range_input = (0,0) 

binance = ccxt_async.binance({
    'enableRateLimit': True,
    'rateLimit': 1200,
    'apiKey': api_key,
    'secret': api_secret,
})


async def send_telegram_message(message):
    bot = Bot(token=YOUR_TELEGRAM_TOKEN)
    await bot.send_message(chat_id=YOUR_CHAT_ID, text=message)
    await bot.close()

async def fetch_symbols():
    markets = await binance.fetch_markets()
    symbols = [market["symbol"] for market in markets if market["quote"] == "USDT" and ':' not in market["symbol"] and market["symbol"] != "ERD/USDT"]
    return symbols

async def fetch_daily_volume(symbol):
    kline = await binance.fetch_ohlcv(symbol, "1d", limit=1)
    volume = kline[0][5]
    return volume

async def filter_symbols(symbols):
    filtered_symbols = []
    total_symbols = len(symbols)
    processed_symbols = 0

    for symbol in symbols:
        if any(substring in symbol for substring in ["USTC", "BEAR", "BULL", "DOWN", "UP"]):
            continue

        daily_volume = await fetch_daily_volume(symbol)
        if daily_volume >= min_vol:
            filtered_symbols.append(symbol)

        processed_symbols += 1
        print(f"Filtering symbols: {processed_symbols}/{total_symbols}")

    return filtered_symbols

def calculate_ema(df, window):
    ema_indicator = EMAIndicator(df["close"], window)
    df[f"ema_{window}"] = ema_indicator.ema_indicator()

async def check_stoch_rsi(symbol):
    klines = await binance.fetch_ohlcv(symbol, '4h', limit=36)
    df = pd.DataFrame(klines, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["close"] = pd.to_numeric(df["close"])

    calculate_ema(df, 25)

    stoch_rsi = StochRSIIndicator(df["close"], window=14, smooth1=3, smooth2=3)
    df["k"] = stoch_rsi.stochrsi_k() * 100
    df["d"] = stoch_rsi.stochrsi_d() * 100

    latest_k = df["k"].iloc[-1]
    latest_d = df["d"].iloc[-1]

    # Check if the previous 4h candle was red and the last closed 4h candle is green
    prev_candle_red = df["close"].iloc[-3] < df["open"].iloc[-3]
    prev_candle_green = df["close"].iloc[-3] > df["open"].iloc[-3]
    last_candle_red = df["close"].iloc[-2] < df["open"].iloc[-2]
    last_candle_green = df["close"].iloc[-2] > df["open"].iloc[-2]

    price = df["close"].iloc[-2]
    ema_25 = df["ema_25"].iloc[-2]

    price_above_ema = price > ema_25
    price_below_ema = price < ema_25

    # Check if the Stoch RSI is oversold, overbought, or within the 10% range
    oversold_range = oversold_range_input 
    overbought_range = overbought_range_input  
    is_near_oversold = latest_k <= oversold_range[1] or latest_d <= oversold_range[1]
    is_near_overbought = latest_k >= overbought_range[0] or latest_d >= overbought_range[0]


    if prev_candle_red and last_candle_green and is_near_oversold:
        if price_above_ema:
            signal_type = "Power BUY"
        else:
            signal_type = "Standard BUY"
        await send_telegram_message(f"{symbol} - {signal_type}: 4h green candle with Stoch RSI near or in oversold; price is {'above' if price_above_ema else 'below'} the 25 EMA")
    
    elif prev_candle_green and last_candle_red and is_near_overbought:
        if price_below_ema:
            signal_type = "Power SELL"
        else:
            signal_type = "Standard SELL"
        await send_telegram_message(f"{symbol} - {signal_type}: 4h red candle with Stoch RSI near or in overbought; price is {'below' if price_below_ema else 'above'} the 25 EMA")
    else:
        print(f"Debug info for {symbol}:")
        print(f"Previous candle: Open={df['open'].iloc[-3]}, Close={df['close'].iloc[-3]}, Green={prev_candle_green}")
        print(f"Last closed candle: Open={df['open'].iloc[-2]}, Close={df['close'].iloc[-2]}, Red={last_candle_red}")
        print(f"Stoch RSI: K={latest_k}, D={latest_d}, Near Oversold={is_near_oversold}, Near Overbought={is_near_overbought}")
        print("---")

async def main():
    print("Fetching symbols...")
    symbols = await fetch_symbols()
    print("Filtering symbols...")
    filtered_symbols = await filter_symbols(symbols)

    # Remove NBS/USDT explicitly
    excluded_symbols = ['NBS/USDT']
    filtered_symbols = [symbol for symbol in filtered_symbols if symbol not in excluded_symbols]

    filtered_symbols = list(set(filtered_symbols))  # Remove duplicates
    print(f"Filtered symbols: {filtered_symbols}")

    while True:
        print("Checking Stoch RSI for each symbol...")
        for symbol in filtered_symbols:
            await check_stoch_rsi(symbol)

        # Calculate time left for the next 4-hour candle
        now = datetime.utcnow()
        next_4h_candle = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=4 - (now.hour % 4))
        remaining_minutes = (next_4h_candle - now).seconds // 60

        print(f"Waiting for the next 4h candle... ({remaining_minutes} minutes left)")
        await asyncio.sleep(60 * remaining_minutes)

    await binance.close()

if __name__ == "__main__":
    asyncio.run(main())

