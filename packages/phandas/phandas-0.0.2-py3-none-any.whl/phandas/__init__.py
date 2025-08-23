# -*- coding: utf-8 -*-

"""
Phandas: Quantitative analysis and backtesting for cryptocurrency markets.
"""

__author__ = "Phantom Management"
__version__ = "0.0.2"

from .data_fetcher import fetch_crypto_data, clean_data, normalize_data
from .factors import generate_return_matrix, neutralize_returns, calculate_neutralized_returns