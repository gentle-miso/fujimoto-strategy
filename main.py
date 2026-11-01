
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
    'SPG', 'FAST', 'LHX', 'D', 'FDX',
    'O', 'MPC', 'PCAR', 'BDX', 'PAYX',
    'GM', 'MET', 'OKE', 'SLB', 'CMI',
    'PSA', 'CTVA', 'PSX', 'AMP', 'KR',
    'DDOG', 'CCI', 'EW', 'CBRE', 'XYZ',
    'TGT', 'KDP', 'EXC', 'ROST', 'DHI',
    'GWW', 'PEG', 'AIG', 'CPRT', 'XEL',
    'KMB', 'MSCI', 'IDXX', 'F', 'BKR',
    'OXY', 'FANG', 'AME', 'GRMN', 'TTD',
    'EBAY', 'KVUE', 'VLO', 'FIS', 'RMD',
    'TTWO', 'YUM', 'CSGP', 'ETR', 'CCL',
    'EA', 'ROK', 'HSY', 'SYY', 'VRSK',
    'ED', 'MPWR', 'CAH', 'VMC', 'CHTR',
    'LVS', 'MCHP', 'WEC', 'PRU', 'TRGP',
    'VICI', 'MLM', 'XYL', 'HIG', 'CTSH',
    'LYV', 'SMCI', 'DAL', 'OTIS', 'FICO',
    'ACGL', 'STX', 'NRG', 'EL', 'EQT',
    'RJF', 'KHC', 'A', 'NUE', 'WAB',
    'GEHC', 'WBD', 'DXCM', 'PCG', 'IQV',
    'STT', 'WTW', 'VTR', 'TSCO', 'BRO',
    'LEN', 'ODFL', 'IR', 'HUM', 'EXR',
    'EFX', 'STZ', 'DD', 'MTB', 'DTE',
    'BR', 'AWK', 'ROL', 'K', 'IRM',
    'AEE', 'UAL', 'FITB', 'KEYS', 'WDC',
    'GIS', 'AVB', 'PPL', 'WRB', 'HPE',
    'VLTO', 'CBOE', 'ADM', 'TDY', 'PTC',
    'CNP', 'IT', 'TYL', 'SYF', 'FE',
    'VRSN', 'ATO', 'MTD', 'SBAC', 'IP',
    'EXE', 'NTRS', 'ES', 'DOV', 'DLTR',
    'DG', 'EQR', 'DRI', 'ON', 'PPG',
    'HBAN', 'JBL', 'LULU', 'SW', 'WSM',
    'PHM', 'HPQ', 'CHD', 'CINF', 'ULTA',
    'HUBB', 'TROW', 'EXPE', 'STE', 'CPAY',
    'GDDY', 'RF', 'CDW', 'CMS', 'TPR',
    'LH', 'NVR', 'TPL', 'AMCR', 'LII',
    'DVN', 'LDOS', 'EIX', 'CFG', 'NTAP',
    'PODD', 'NI', 'FSLR', 'TRMB', 'KEY',
    'BIIB', 'DGX', 'GPN', 'L', 'MKC',
    'TSN', 'INVH', 'HAL', 'ERIE', 'STLD',
    'WY', 'CTRA', 'ZBH', 'GPC', 'RL',
    'FFIV', 'IFF', 'GEN', 'WAT', 'PKG',
    'WST', 'LYB', 'ZBRA', 'PFG', 'LNT',
    'J', 'SNA', 'TER', 'ESS', 'PNR',
    'EVRG', 'MAA', 'BALL', 'DPZ', 'FTV',
    'EXPD', 'LUV', 'BG', 'HRL', 'DOW',
    'DECK', 'CLX', 'HOLX', 'CF', 'FDS',
    'INCY', 'MAS', 'BLDR', 'APTV', 'ALLE',
    'COO', 'KIM', 'EG', 'OMC', 'TXT',
    'BF.B', 'BBY', 'TKO', 'JBHT', 'CHRW',
    'ARE', 'AVY', 'UDR', 'REG', 'CNC',
    'PAYC', 'BEN', 'SOLV', 'JKHY', 'IEX',
    'FOX', 'FOXA', 'NDSN', 'DOC', 'SJM',
    'POOL', 'CPT', 'GNRC', 'GL', 'WYNN',
    'BAX', 'MOS', 'NWSA', 'NCLH', 'PNW',
    'MRNA', 'HST', 'HII', 'AKAM', 'UHS',
    'DVA', 'HAS', 'RVTY', 'SWK', 'VTRS',
    'BXP', 'SWKS', 'WBA', 'ALGN', 'AOS',
    'TAP', 'MGM', 'CPB', 'AIZ', 'AES',
    'IVZ', 'IPG', 'CAG', 'DAY', 'PARA',
    'TECH', 'EPAM', 'HSIC', 'MOH', 'KMX',
    'MTCH', 'CRL', 'ALB', 'FRT', 'LW',
    'MKTX', 'LKQ', 'MHK', 'EMN', 'APA',
    'NWS', 'CZR', 'ENPH'
]


# ============================================================
# 3. 중복 제거 후 통합 리스트 생성
# ============================================================

all_tickers = list(
    dict.fromkeys(Nasdaq_tickers + SnP_tickers)
)

logging.info(f'나스닥 종목 수: {len(Nasdaq_tickers)}')
logging.info(f'S&P 500 종목 수: {len(SnP_tickers)}')
logging.info(f'중복 제거 후 전체 분석 종목 수: {len(all_tickers)}')


# ============================================================
# 4. 보조지표 계산 함수
# ============================================================

def calculate_rsi(data, window=14):
    """
    기존 방식 유지:
    상승폭/하락폭의 단순 이동평균으로 RSI 계산
    0으로 나누는 경우만 안전하게 처리
    """
    delta = data['Close'].diff()

    gain = (
        delta.where(delta > 0, 0)
        .rolling(window=window)
        .mean()
    )

    loss = (
        -delta.where(delta < 0, 0)
        .rolling(window=window)
        .mean()
    )

    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    # 하락폭이 0이고 상승폭이 있으면 RSI 100
    rsi = rsi.mask((loss == 0) & (gain > 0), 100)

    # 상승폭과 하락폭이 모두 0이면 중립값 50
    rsi = rsi.mask((loss == 0) & (gain == 0), 50)

    return rsi


def calculate_macd(data, fast=12, slow=26, signal=9):

    exp1 = data['Close'].ewm(
        span=fast,
        adjust=False
    ).mean()

    exp2 = data['Close'].ewm(
        span=slow,
        adjust=False
    ).mean()

    macd = exp1 - exp2

    macd_signal = macd.ewm(
        span=signal,
        adjust=False
    ).mean()

    return macd, macd_signal


def calculate_ichimoku(data):

    nine_high = data['High'].rolling(
        window=9
    ).max()

    nine_low = data['Low'].rolling(
        window=9
    ).min()

    tenkan_sen = (
        nine_high + nine_low
    ) / 2

    twenty_six_high = data['High'].rolling(
        window=26
    ).max()

    # 기존 코드의 High/Low 계산 오류 수정
    twenty_six_low = data['Low'].rolling(
        window=26
    ).min()

    kijun_sen = (
        twenty_six_high + twenty_six_low
    ) / 2

    senkou_span_a = (
        tenkan_sen + kijun_sen
    ) / 2

    fifty_two_high = data['High'].rolling(
        window=52
    ).max()

    fifty_two_low = data['Low'].rolling(
        window=52
    ).min()

    senkou_span_b = (
        fifty_two_high + fifty_two_low
    ) / 2

    cloud_top = pd.DataFrame({
        'span_a': senkou_span_a,
        'span_b': senkou_span_b
    }).max(axis=1)

    cloud_bottom = pd.DataFrame({
        'span_a': senkou_span_a,
        'span_b': senkou_span_b
    }).min(axis=1)

    return cloud_top, cloud_bottom


def normalize_yfinance_columns(data):
    """
    yfinance 버전에 따라 달라질 수 있는 MultiIndex 컬럼을
    Open/High/Low/Close/Adj Close/Volume 형태로 정리합니다.
    """
    if not isinstance(data.columns, pd.MultiIndex):
        return data

    required = {'Open', 'High', 'Low', 'Close', 'Volume'}

    # OHLCV 필드명이 들어 있는 MultiIndex 레벨을 우선 선택
    for level in range(data.columns.nlevels):
        values = set(data.columns.get_level_values(level))
        if required.issubset(values):
            data.columns = data.columns.get_level_values(level)
            return data

    # 레벨 구조가 예상과 다를 때 각 튜플에서 OHLCV 필드를 추출
    flattened = []
    for column in data.columns:
        parts = list(column) if isinstance(column, tuple) else [column]
        field = next(
            (part for part in parts if part in required or part == 'Adj Close'),
            parts[0]
        )
        flattened.append(field)

    data.columns = flattened
    return data


# ============================================================
# 5. 개별 종목 분석 함수
# ============================================================

def analyze_fujimoto_strategy(ticker):

    try:

        df = yf.download(
            ticker,
            period='1y',
            interval='1d',
            progress=False,
            auto_adjust=False,
            threads=False
        )

        if df is None or df.empty or len(df) < 60:
            logging.warning(f'{ticker}: 데이터 부족')
            return None

        # yfinance 버전별 MultiIndex 컬럼 구조 정규화
        df = normalize_yfinance_columns(df)

        required_columns = {'High', 'Low', 'Close'}
        missing_columns = required_columns.difference(df.columns)

        if missing_columns:
            logging.warning(
                f'{ticker}: 필수 가격 컬럼 누락 - {sorted(missing_columns)}'
            )
            return None

        # 숫자형 데이터로 정리
        for column in ['High', 'Low', 'Close']:
            df[column] = pd.to_numeric(df[column], errors='coerce')

        df = df.dropna(subset=['High', 'Low', 'Close'])

        if len(df) < 60:
            logging.warning(f'{ticker}: 유효한 가격 데이터가 부족합니다.')
            return None

        # 보조지표 계산
        df['RSI'] = calculate_rsi(df)

        df['MACD'], df['Signal'] = calculate_macd(df)

        (
            df['Cloud_Top'],
            df['Cloud_Bottom']
        ) = calculate_ichimoku(df)

        current = df.iloc[-1]

        prev = df.iloc[-2]

        # 지표 유효성 확인
        required_values = [
            current['RSI'],
            current['MACD'],
            current['Signal'],
            current['Cloud_Top'],
            current['Cloud_Bottom'],
            prev['RSI'],
            prev['MACD'],
            prev['Signal']
        ]

        if not np.isfinite(
            np.array(required_values, dtype=float)
        ).all():

            logging.warning(
                f'{ticker}: 보조지표 계산값이 유효하지 않습니다.'
            )

            return None

        # ====================================================
        # 매수 1:2:6 판별
        # ====================================================

        buy_stage = 0

        buy_reason = '관망 (신호 대기)'

        rsi_cond_1 = (
            (prev['RSI'] <= 30)
            and (current['RSI'] > 30)
        )

        macd_golden = (
            (prev['MACD'] <= prev['Signal'])
            and (current['MACD'] > current['Signal'])
        )

        recent_lows = df['Low'].iloc[-5:-1]

        recent_clouds = df['Cloud_Top'].iloc[-5:-1]

        cloud_retest = (
            (current['Close'] > current['Cloud_Top'])
            and (recent_lows <= recent_clouds).any()
        )

        if cloud_retest and macd_golden and rsi_cond_1:

            buy_stage = 3

            buy_reason = (
                '매수 3단계 '
                '(최종 확신 - 누적 비중 9: 구름대 리테스트)'
            )

        elif macd_golden:

            buy_stage = 2

            buy_reason = (
                '매수 2단계 '
                '(확인 - 누적 비중 3: MACD 골든크로스)'
            )

        elif rsi_cond_1:

            buy_stage = 1

            buy_reason = (
                '매수 1단계 '
                '(탐색전 - 비중 1: RSI 30 상향 돌파)'
            )

        # ====================================================
        # 매도 1:2:6 판별
        # ====================================================

        sell_stage = 0

        sell_reason = '보유 유지'

        macd_dead = (
            (prev['MACD'] >= prev['Signal'])
            and (current['MACD'] < current['Signal'])
        )

        rsi_bearish = (
            (prev['RSI'] >= 50)
            and (current['RSI'] < 50)
        )

        cloud_breakdown = (
            current['Close'] < current['Cloud_Bottom']
        )

        if cloud_breakdown:

            sell_stage = 3

            sell_reason = (
                '매도 3단계 '
                '(추세 파괴 - 비중 6 전량 청산: 구름대 이탈)'
            )

        elif rsi_bearish and macd_dead:

            sell_stage = 2

            sell_reason = (
                '매도 2단계 '
                '(추세 약화 - 비중 2 추가 매도: RSI 약세)'
            )

        elif macd_dead:

            sell_stage = 1

            sell_reason = (
                '매도 1단계 '
                '(경고등 - 비중 1 매도: MACD 데드크로스)'
            )

        # ====================================================
        # 분석 결과 반환
        # ====================================================

        return {

            'Ticker': ticker,

            'Close Price': round(
                float(current['Close']), 2
            ),

            'RSI': round(
                float(current['RSI']), 2
            ),

            'Buy Stage': f'{buy_stage}단계',

            'Buy Reason': buy_reason,

            'Sell Stage': f'{sell_stage}단계',

            'Sell Reason': sell_reason,

        }

    except Exception as e:

        logging.error(
            f'{ticker} 분석 실패: {e}'
        )

        return None


# ============================================================
# 6. Google Drive 업로드 함수
# ============================================================

def upload_to_google_drive(file_path):

    logging.info(
        'Google Drive 업로드를 시작합니다.'
    )

    # GitHub Actions 환경변수 확인
    credentials_file = os.environ.get(
        'GOOGLE_APPLICATION_CREDENTIALS'
    )

    folder_id = os.environ.get(
        'GOOGLE_DRIVE_FOLDER_ID'
    )

    if not credentials_file:

        raise ValueError(
            'GOOGLE_APPLICATION_CREDENTIALS 설정이 없습니다.'
        )

    if not folder_id:

        raise ValueError(
            'GOOGLE_DRIVE_FOLDER_ID 설정이 없습니다.'
        )

    if not os.path.exists(credentials_file):

        raise FileNotFoundError(
            'Google 인증 JSON 파일을 찾을 수 없습니다.'
        )

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f'CSV 파일을 찾을 수 없습니다: {file_path}'
        )

    # 인증 JSON 파일이 정상적인 JSON인지, 서비스 계정 키인지 확인
    try:
        credentials = (
            service_account.Credentials
            .from_service_account_file(
                credentials_file,
                scopes=['https://www.googleapis.com/auth/drive']
            )
        )
    except Exception as e:
        raise RuntimeError(
            f'Google 서비스 계정 JSON 인증에 실패했습니다: {e}'
        ) from e

    # Google Drive API 연결
    service = build(
        'drive',
        'v3',
        credentials=credentials,
        cache_discovery=False
    )

    # 폴더 접근 권한 확인
    try:
        folder_info = service.files().get(
            fileId=folder_id,
            fields='id,name,mimeType',
            supportsAllDrives=True
        ).execute()
    except Exception as e:
        raise RuntimeError(
            'Google Drive 폴더에 접근할 수 없습니다. '
            '폴더 ID와 서비스 계정 공유 권한을 확인하세요. '
            f'상세 오류: {e}'
        ) from e

    if folder_info.get('mimeType') != 'application/vnd.google-apps.folder':
        raise ValueError('GOOGLE_DRIVE_FOLDER_ID가 Google Drive 폴더 ID가 아닙니다.')

    logging.info(
        f"업로드 대상 폴더 확인: {folder_info.get('name')}"
    )

    # 파일명
    file_name = os.path.basename(file_path)

    # 업로드 파일 정보
    file_metadata = {

        'name': file_name,

        'parents': [folder_id]

    }

    # CSV 업로드
    media = MediaFileUpload(

        file_path,

        mimetype='text/csv',

        resumable=True

    )

    try:
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name,webViewLink',
            supportsAllDrives=True
        ).execute()
    except Exception as e:
        raise RuntimeError(
            'Google Drive CSV 업로드에 실패했습니다. '
            '서비스 계정의 폴더 접근 권한과 Drive 계정 유형을 확인하세요. '
            f'상세 오류: {e}'
        ) from e

    logging.info('Google Drive 업로드 성공!')

    logging.info(
        f"파일명: {uploaded_file.get('name')}"
    )

    logging.info(
        f"파일 ID: {uploaded_file.get('id')}"
    )

    logging.info(
        f"파일 URL: {uploaded_file.get('webViewLink')}"
    )

    return uploaded_file


# ============================================================
# 7. 전체 종목 분석 및 CSV 저장
# ============================================================

def main():

    results = []

    total = len(all_tickers)

    logging.info('=' * 60)

    logging.info(
        f'총 {total}개 종목 분석을 시작합니다.'
    )

    logging.info(
        '후지모토 1:2:6 전략 스캔'
    )

    logging.info('=' * 60)

    # --------------------------------------------------------
    # 종목별 분석
    # --------------------------------------------------------

    for idx, ticker in enumerate(
        all_tickers, 1
    ):

        logging.info(
            f'진행률: {idx}/{total} ({ticker})'
        )

        try:
            res = analyze_fujimoto_strategy(ticker)

            if res is not None:
                results.append(res)

        except Exception:
            logging.exception(
                f'{ticker}: 종목 분석 중 예기치 못한 오류가 발생했습니다.'
            )
            continue

    # --------------------------------------------------------
    # CSV 생성
    # --------------------------------------------------------

    if not results:

        logging.warning(
            '분석 결과가 없습니다. CSV를 생성하지 않습니다.'
        )

        return

    df_result = pd.DataFrame(results)

    # 한국 시간 기준 날짜
    today = datetime.now(
        ZoneInfo('Asia/Seoul')
    ).strftime('%Y%m%d_%H%M')

    output_path = (
        f'fujimoto_strategy_results_{today}.csv'
    )

    # CSV 저장
    df_result.to_csv(

        output_path,

        index=False,

        encoding='utf-8-sig'

    )

    logging.info(
        f'CSV 생성 완료: {output_path}'
    )

    logging.info(
        f'분석 성공 종목 수: {len(results)}'
    )

    # --------------------------------------------------------
    # 매수 및 매도 신호 집계
    # --------------------------------------------------------

    buy_count = df_result[
        df_result['Buy Stage'] != '0단계'
    ].shape[0]

    sell_count = df_result[
        df_result['Sell Stage'] != '0단계'
    ].shape[0]

    logging.info(
        f'매수 신호 종목 수: {buy_count}'
    )

    logging.info(
        f'매도 신호 종목 수: {sell_count}'
    )

    # --------------------------------------------------------
    # Google Drive 업로드
    # --------------------------------------------------------

    upload_to_google_drive(
        output_path
    )

    logging.info('=' * 60)

    logging.info(
        '전체 종목 분석 및 Google Drive 업로드 완료'
    )

    logging.info('=' * 60)


# ============================================================
# 8. 프로그램 실행
# ============================================================

if __name__ == '__main__':

    main()
