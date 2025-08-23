import ccxt
import pandas as pd
import time
from datetime import datetime
from typing import Union, Dict

# Predefined L1 public chain symbols
L1_CHAINS = {
    'ETH': ['ETH/USDT'],
    'SOL': ['SOL/USDT'],
    'BNB': ['BNB/USDT'],
    'MATIC': ['MATIC/USDT'],
    'OP': ['OP/USDT'],
    'ARB': ['ARB/USDT'],
}

def _download_ohlcv(
    symbol: str, 
    timeframe: str, 
    exchange_name: str = 'binance',
    since: str = '2010-01-01T00:00:00Z'
) -> pd.DataFrame:
    """
    內部函式：使用 ccxt 下載指定交易對的歷史K線數據。
    預設從幣安下載。
    """
    print(f"--- 開始下載任務: {symbol} ({timeframe}) from {exchange_name} ---")

    try:
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class({
            'options': { 'defaultType': 'spot', 'adjustForTimeDifference': True },
            'rateLimit': 1200, # 幣安現貨默認速率限制為 1200ms
        })
    except AttributeError:
        print(f"錯誤: 不支援的交易所名稱 '{exchange_name}'。")
        return pd.DataFrame()

    limit = 1000
    all_ohlcv = []
    _since = exchange.parse8601(since)

    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=_since, limit=limit)
            
            if not ohlcv:
                break
            
            all_ohlcv.extend(ohlcv)
            _since = ohlcv[-1][0] + 1
            
            time.sleep(exchange.rateLimit / 1000)

        except Exception as e:
            print(f"  獲取數據時發生錯誤: {e}")
            if 'BadSymbol' in str(e):
                print(f"  交易對 {symbol} 在 {exchange_name} 上不存在。")
                return pd.DataFrame()
            break

    if not all_ohlcv:
        print(f"未能為 {symbol} 下載任何數據。")
        return pd.DataFrame()

    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.drop_duplicates(subset=['timestamp'], inplace=True)
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True) # 確保時間順序

    print(f"下載完成。總共獲取到 {len(df)} 根 K線 for {symbol}.")
    return df

def _get_l1_chain_data(
    timeframe: str, 
    exchange_name: str = 'binance'
) -> Dict[str, pd.DataFrame]:
    """
    內部函式：下載預定義 L1 公鏈組合的數據。
    """
    print(f"--- 開始下載 L1 公鏈數據 (Timeframe: {timeframe}, Exchange: {exchange_name}) ---")
    l1_data = {}
    for name, symbols in L1_CHAINS.items():
        print(f"--- 正在處理: {name} ---")
        for symbol in symbols:
            df = _download_ohlcv(symbol, timeframe, exchange_name)
            if not df.empty:
                l1_data[name] = df
                break
        if name not in l1_data:
            print(f"!!! 未能為 {name} 下載任何數據。")
    print("--- L1 公鏈數據下載完成 ---")
    return l1_data

def _get_btc_data(
    timeframe: str, 
    exchange_name: str = 'binance'
) -> pd.DataFrame:
    """
    內部函式：下載 BTC/USDT 的數據。
    """
    print(f"--- 開始下載 BTC/USDT 數據 (Timeframe: {timeframe}, Exchange: {exchange_name}) ---")
    df = _download_ohlcv('BTC/USDT', timeframe, exchange_name)
    print("--- BTC/USDT 數據下載完成 ---")
    return df

def _get_symbol_data(
    symbol: str, 
    timeframe: str, 
    exchange_name: str = 'binance'
) -> pd.DataFrame:
    """
    內部函式：下載單一指定符號的數據。
    """
    print(f"--- 開始下載 {symbol} 數據 (Timeframe: {timeframe}, Exchange: {exchange_name}) ---")
    df = _download_ohlcv(symbol, timeframe, exchange_name)
    print(f"--- {symbol} 數據下載完成 ---")
    return df

def fetch_crypto_data(
    target: str, 
    timeframe: str,
    exchange_name: str = 'binance'
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    自訂下載函數：根據指定目標和時間週期下載加密貨幣數據。

    Args:
        target (str): 要下載的項目。
                      可以是 'L1_CHAINS' (下載預定義的 L1 公鏈組合數據),
                      'BTC' (下載 BTC/USDT 數據), 或一個單一交易對符號 (e.g., "ETH/USDT", "OP/USDT").
        timeframe (str): K線時間週期 (e.g., "1d", "1h", "5m").
        exchange_name (str): 交易所名稱 (e.g., "binance", "okx"). 預設為 'binance'.

    Returns:
        Union[pd.DataFrame, Dict[str, pd.DataFrame]]: 
            如果 target 是 'L1_CHAINS'，返回包含每個 L1 公鏈數據的字典。
            否則，返回包含單一 DataFrame 的數據。
    """
    if target == 'L1_CHAINS':
        return _get_l1_chain_data(timeframe, exchange_name)
    elif target == 'BTC':
        return _get_btc_data(timeframe, exchange_name)
    else:
        return _get_symbol_data(target, timeframe, exchange_name)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    清理輸入的 DataFrame，處理缺失值和異常值。

    Args:
        df (pd.DataFrame): 輸入的 DataFrame。

    Returns:
        pd.DataFrame: 清理後的 DataFrame。
    """
    print("清理數據中...")
    return df.dropna().reset_index(drop=True)

def normalize_data(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    使用 Min-Max 縮放正規化 DataFrame 中指定的列。

    Args:
        df (pd.DataFrame): 輸入的 DataFrame。
        columns (list[str]): 需要正規化的列名列表。

    Returns:
        pd.DataFrame: 包含正規化列的 DataFrame。
    """
    print(f"正規化列: {columns}...")
    _df = df.copy() # 避免修改原始 DataFrame
    for col in columns:
        if col in _df.columns:
            min_val = _df[col].min()
            max_val = _df[col].max()
            if max_val - min_val > 0:
                _df[col] = (_df[col] - min_val) / (max_val - min_val)
            else:
                _df[col] = 0.0 # 處理所有值都相同的情況
    return _df
