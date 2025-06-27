import pandas as pd
import ta

def get_rsi(df, period=14):
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=period).rsi()
    return df['rsi'].iloc[-1]