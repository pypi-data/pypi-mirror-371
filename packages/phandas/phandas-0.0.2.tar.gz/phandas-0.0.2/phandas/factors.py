import pandas as pd
from typing import Dict

def generate_return_matrix(data: Dict[str, pd.DataFrame], price_col: str = 'close') -> pd.DataFrame:
    """
    從多個加密貨幣的 DataFrame 生成每日收益率矩陣。

    Args:
        data (Dict[str, pd.DataFrame]): 每個幣種的歷史數據 DataFrame 字典。
                                         鍵為幣種名稱，值為 DataFrame，需包含時間索引和價格列。
        price_col (str): 用於計算收益率的價格列名稱 (例如: 'close', 'open'). 預設為 'close'.

    Returns:
        pd.DataFrame: 每日收益率矩陣，索引為日期，列為幣種名稱。
    """
    all_returns = []
    for symbol, df in data.items():
        if price_col in df.columns:
            returns = df[price_col].pct_change().rename(symbol)
            all_returns.append(returns)
        else:
            print(f"警告: 幣種 {symbol} 的 DataFrame 中沒有找到價格列 '{price_col}'，將跳過此幣種。")

    if not all_returns:
        return pd.DataFrame() # 如果沒有任何收益率數據，回傳空 DataFrame

    return_matrix = pd.concat(all_returns, axis=1)
    return return_matrix.dropna()

def neutralize_returns(returns_df: pd.DataFrame) -> pd.DataFrame:
    """
    對收益率矩陣進行中性化處理 (減去每日平均收益率)。

    Args:
        returns_df (pd.DataFrame): 每日收益率矩陣。

    Returns:
        pd.DataFrame: 中性化後的收益率矩陣。
    """
    if returns_df.empty:
        return pd.DataFrame()

    daily_average_return = returns_df.mean(axis=1)
    neutralized_df = returns_df.sub(daily_average_return, axis=0)
    return neutralized_df

def calculate_neutralized_returns(
    data: Dict[str, pd.DataFrame], 
    price_col: str = 'close', 
    neutralize: bool = True
) -> pd.DataFrame:
    """
    從下載的數據生成收益率矩陣，並可選擇進行中性化處理。

    Args:
        data (Dict[str, pd.DataFrame]): 每個幣種的歷史數據 DataFrame 字典。
        price_col (str): 用於計算收益率的價格列名稱. 預設為 'close'.
        neutralize (bool): 是否對收益率進行中性化處理. 預設為 True.

    Returns:
        pd.DataFrame: 處理後的收益率矩陣 (可能已中性化)。
    """
    return_matrix = generate_return_matrix(data, price_col)
    if neutralize:
        return neutralize_returns(return_matrix)
    return return_matrix
