
import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import yfinance as yf

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# ============================================================
# 0. 로깅 설정
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# ============================================================
# 1. 나스닥 종목 리스트
# ============================================================

Nasdaq_tickers = [
    'NVDA', 'MSFT', 'AAPL', 'AMZN', 'META',
    'AVGO', 'GOOGL', 'GOOG', 'TSLA', 'NFLX',
    'COST', 'PLTR', 'AMD', 'ASML', 'TMUS',
    'CSCO', 'AZN', 'INTU', 'LIN', 'PEP',
    'BKNG', 'ISRG', 'TXN', 'QCOM', 'AMGN',
    'PDD', 'SHOP', 'ADBE', 'ARM', 'AMAT',
    'GILD', 'HON', 'APP', 'LRCX', 'ADP',
    'MELI', 'CMCSA', 'VRTX', 'MU', 'KLAC',
    'PANW', 'SNPS', 'CRWD', 'ADI', 'CEG',
    'DASH', 'MSTR', 'SBUX', 'CDNS', 'TRI',
    'CTAS', 'INTC', 'ORLY', 'MDLZ', 'ABNB',
    'FTNT', 'MAR', 'CSX', 'MRVL', 'PYPL',
    'ADSK', 'AEP', 'WDAY', 'REGN', 'ROP',
    'AXON', 'MNST', 'NXPI', 'FAST', 'PCAR',
    'PAYX', 'TEAM', 'DDOG', 'KDP', 'EXC',
    'ROST', 'CCEP', 'CPRT', 'ZS', 'XEL',
    'IDXX', 'BKR', 'FANG', 'TTD', 'TTWO',
    'CSGP', 'EA', 'VRSK', 'CHTR', 'MCHP',
    'CTSH', 'KHC', 'GEHC', 'WBD', 'DXCM',
    'ODFL', 'ON', 'LULU', 'CDW', 'GFS', 'BIIB'
]


# ============================================================
# 2. S&P 500 종목 리스트
# ============================================================

SnP_tickers = [
    'NVDA', 'MSFT', 'AAPL', 'AMZN', 'META',
    'AVGO', 'GOOGL', 'GOOG', 'BRK.B', 'TSLA',
    'JPM', 'WMT', 'ORCL', 'LLY', 'V',
    'MA', 'NFLX', 'XOM', 'COST', 'JNJ',
    'HD', 'PLTR', 'PG', 'ABBV', 'BAC',
    'CVX', 'KO', 'GE', 'AMD', 'TMUS',
    'CSCO', 'PM', 'WFC', 'CRM', 'IBM',
    'MS', 'ABT', 'MCD', 'INTU', 'UNH',
    'LIN', 'GS', 'RTX', 'DIS', 'AXP',
    'CAT', 'MRK', 'T', 'PEP', 'NOW',
    'UBER', 'VZ', 'GEV', 'TMO', 'BKNG',
    'SCHW', 'ISRG', 'C', 'BLK', 'BA',
    'SPGI', 'TXN', 'QCOM', 'AMGN', 'ACN',
    'BSX', 'ETN', 'ANET', 'ADBE', 'NEE',
    'AMAT', 'SYK', 'PGR', 'DHR', 'GILD',
    'TJX', 'HON', 'DE', 'PFE', 'BX',
    'COF', 'UNP', 'APH', 'KKR', 'LOW',
    'LRCX', 'ADP', 'CMCSA', 'VRTX', 'MU',
    'KLAC', 'COP', 'PANW', 'SNPS', 'MDT',
    'CRWD', 'WELL', 'NKE', 'ADI', 'CEG',
    'CB', 'ICE', 'DASH', 'SO', 'MO',
    'CME', 'AMT', 'SBUX', 'LMT', 'TT',
    'PLD', 'CDNS', 'MMC', 'DUK', 'WM',
    'PH', 'BMY', 'MCO', 'CTAS', 'TDG',
    'MCK', 'DELL', 'HCA', 'SHW', 'RCL',
    'INTC', 'ORLY', 'NOC', 'GD', 'MDLZ',
    'COIN', 'EMR', 'CVS', 'APO', 'ABNB',
    'MMM', 'AON', 'EQIX', 'FTNT', 'HWM',
    'ECL', 'WMB', 'FI', 'ITW', 'PNC',
    'MSI', 'AJG', 'RSG', 'UPS', 'VST',
    'BK', 'JCI', 'CI', 'MAR', 'NEM',
    'USB', 'CL', 'ZTS', 'CSX', 'AZO',
    'PYPL', 'EOG', 'ADSK', 'APD', 'KMI',
    'ELV', 'NSC', 'HLT', 'AEP', 'TEL',
    'WDAY', 'REGN', 'PWR', 'DLR', 'ROP',
    'TRV', 'AXON', 'MNST', 'CMG', 'CARR',
    'FCX', 'COR', 'TFC', 'URI', 'NDAQ',
    'GLW', 'AFL', 'NXPI', 'SRE', 'ALL',
