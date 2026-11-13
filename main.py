
import os
import io
import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import yfinance as yf

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


# ============================================================
# 1. 기본 설정
# ============================================================

KST = ZoneInfo("Asia/Seoul")

SCOPES = [
    "https://www.googleapis.com/auth/drive"
]

DRIVE_FOLDER_ID = os.environ["DRIVE_FOLDER_ID"]
GOOGLE_TOKEN_JSON = os.environ["GOOGLE_TOKEN_JSON"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ============================================================
# 2. 종목 리스트
# ============================================================

Nasdaq_tickers = [
    "NVDA", "MSFT", "AAPL", "AMZN", "META", "AVGO", "GOOGL", "GOOG", "TSLA", "NFLX",
    "COST", "PLTR", "AMD", "ASML", "TMUS", "CSCO", "AZN", "INTU", "LIN", "PEP",
    "BKNG", "ISRG", "TXN", "QCOM", "AMGN", "PDD", "SHOP", "ADBE", "ARM", "AMAT",
    "GILD", "HON", "APP", "LRCX", "ADP", "MELI", "CMCSA", "VRTX", "MU", "KLAC",
    "PANW", "SNPS", "CRWD", "ADI", "CEG", "DASH", "MSTR", "SBUX", "CDNS", "TRI",
    "CTAS", "INTC", "ORLY", "MDLZ", "ABNB", "FTNT", "MAR", "CSX", "MRVL", "PYPL",
    "ADSK", "AEP", "WDAY", "REGN", "ROP", "AXON", "MNST", "NXPI", "FAST", "PCAR",
    "PAYX", "TEAM", "DDOG", "KDP", "EXC", "ROST", "CCEP", "CPRT", "ZS", "XEL",
    "IDXX", "BKR", "FANG", "TTD", "TTWO", "CSGP", "EA", "VRSK", "CHTR", "MCHP",
    "CTSH", "KHC", "GEHC", "WBD", "DXCM", "ODFL", "ON", "LULU", "CDW", "GFS", "BIIB"
]


SnP_tickers = [
    "NVDA", "MSFT", "AAPL", "AMZN", "META", "AVGO", "GOOGL", "GOOG", "BRK.B", "TSLA",
    "JPM", "WMT", "ORCL", "LLY", "V", "MA", "NFLX", "XOM", "COST", "JNJ",
    "HD", "PLTR", "PG", "ABBV", "BAC", "CVX", "KO", "GE", "AMD", "TMUS",
    "CSCO", "PM", "WFC", "CRM", "IBM", "MS", "ABT", "MCD", "INTU", "UNH",
    "LIN", "GS", "RTX", "DIS", "AXP", "CAT", "MRK", "T", "PEP", "NOW",
    "UBER", "VZ", "GEV", "TMO", "BKNG", "SCHW", "ISRG", "C", "BLK", "BA",
    "SPGI", "TXN", "QCOM", "AMGN", "ACN", "BSX", "ETN", "ANET", "ADBE", "NEE",
    "AMAT", "SYK", "PGR", "DHR", "GILD", "TJX", "HON", "DE", "PFE", "BX",
    "COF", "UNP", "APH", "KKR", "LOW", "LRCX", "ADP", "CMCSA", "VRTX", "MU",
    "KLAC", "COP", "PANW", "SNPS", "MDT", "CRWD", "WELL", "NKE", "ADI", "CEG",
    "CB", "ICE", "DASH", "SO", "MO", "CME", "AMT", "SBUX", "LMT", "TT", "PLD",
    "CDNS", "MMC", "DUK", "WM", "PH", "BMY", "MCO", "CTAS", "TDG", "MCK",
    "DELL", "HCA", "SHW", "RCL", "INTC", "ORLY", "NOC", "GD", "MDLZ", "COIN",
    "EMR", "CVS", "APO", "ABNB", "MMM", "AON", "EQIX", "FTNT", "HWM", "ECL",
    "WMB", "FI", "ITW", "PNC", "MSI", "AJG", "RSG", "UPS", "VST", "BK",
    "JCI", "CI", "MAR", "NEM", "USB", "CL", "ZTS", "CSX", "AZO", "PYPL",
    "EOG", "ADSK", "APD", "KMI", "ELV", "NSC", "HLT", "AEP", "TEL", "WDAY",
    "REGN", "PWR", "DLR", "ROP", "TRV", "AXON", "MNST", "CMG", "CARR", "FCX",
    "COR", "TFC", "URI", "NDAQ", "GLW", "AFL", "NXPI", "SRE", "ALL", "SPG",
    "FAST", "LHX", "D", "FDX", "O", "MPC", "PCAR", "BDX", "PAYX", "GM",
    "MET", "OKE", "SLB", "CMI", "PSA", "CTVA", "PSX", "AMP", "KR", "DDOG",
    "CCI", "EW", "CBRE", "XYZ", "TGT", "KDP", "EXC", "ROST", "DHI", "GWW",
    "PEG", "AIG", "CPRT", "XEL", "KMB", "MSCI", "IDXX", "F", "BKR", "OXY",
    "FANG", "AME", "GRMN", "TTD", "EBAY", "KVUE", "VLO", "FIS", "RMD", "TTWO",
    "YUM", "CSGP", "ETR", "CCL", "EA", "ROK", "HSY", "SYY", "VRSK", "ED",
    "MPWR", "CAH", "VMC", "CHTR", "LVS", "MCHP", "WEC", "PRU", "TRGP", "VICI",
    "MLM", "XYL", "HIG", "CTSH", "LYV", "SMCI", "DAL", "OTIS", "FICO", "ACGL",
    "STX", "NRG", "EL", "EQT", "RJF", "KHC", "A", "NUE", "WAB", "GEHC", "WBD",
    "DXCM", "PCG", "IQV", "STT", "WTW", "VTR", "TSCO", "BRO", "LEN", "ODFL",
    "IR", "HUM", "EXR", "EFX", "STZ", "DD", "MTB", "DTE", "BR", "AWK", "ROL",
    "K", "IRM", "AEE", "UAL", "FITB", "KEYS", "WDC", "GIS", "AVB", "PPL",
    "WRB", "HPE", "VLTO", "CBOE", "ADM", "TDY", "PTC", "CNP", "IT", "TYL",
    "SYF", "FE", "VRSN", "ATO", "MTD", "SBAC", "IP", "EXE", "NTRS", "ES",
    "DOV", "DLTR", "DG", "EQR", "DRI", "ON", "PPG", "HBAN", "JBL", "LULU",
    "SW", "WSM", "PHM", "HPQ", "CHD", "CINF", "ULTA", "HUBB", "TROW", "EXPE",
    "STE", "CPAY", "GDDY", "RF", "CDW", "CMS", "TPR", "LH", "NVR", "TPL",
    "AMCR", "LII", "DVN", "LDOS", "EIX", "CFG", "NTAP", "PODD", "NI", "FSLR",
    "TRMB", "KEY", "BIIB", "DGX", "GPN", "L", "MKC", "TSN", "INVH", "HAL",
    "ERIE", "STLD", "WY", "CTRA", "ZBH", "GPC", "RL", "FFIV", "IFF", "GEN",
    "WAT", "PKG", "WST", "LYB", "ZBRA", "PFG", "LNT", "J", "SNA", "TER",
    "ESS", "PNR", "EVRG", "MAA", "BALL", "DPZ", "FTV", "EXPD", "LUV", "BG",
    "HRL", "DOW", "DECK", "CLX", "HOLX", "CF", "FDS", "INCY", "MAS", "BLDR",
    "APTV", "ALLE", "COO", "KIM", "EG", "OMC", "TXT", "BF.B", "BBY", "TKO",
    "JBHT", "CHRW", "ARE", "AVY", "UDR", "REG", "CNC", "PAYC", "BEN", "SOLV",
    "JKHY", "IEX", "FOX", "FOXA", "NDSN", "DOC", "SJM", "POOL", "CPT", "GNRC",
    "GL", "WYNN", "BAX", "MOS", "NWSA", "NCLH", "PNW", "MRNA", "HST", "HII",
    "AKAM", "UHS", "DVA", "HAS", "RVTY", "SWK", "VTRS", "BXP", "SWKS", "WBA",
    "ALGN", "AOS", "TAP", "MGM", "CPB", "AIZ", "AES", "IVZ", "IPG", "CAG",
    "DAY", "PARA", "TECH", "EPAM", "HSIC", "MOH", "KMX", "MTCH", "CRL", "ALB",
    "FRT", "LW", "MKTX", "LKQ", "MHK", "EMN", "APA", "NWS", "CZR", "ENPH"
]


# 중복 제거 통합 리스트
all_tickers = list(
    dict.fromkeys(Nasdaq_tickers + SnP_tickers)
)


# ============================================================
# 3. 보조지표 계산 함수
# ============================================================

def calculate_rsi(data, window=14):

    delta = data["Close"].diff()

    gain = (
        delta.where(delta > 0, 0)
        .rolling(window=window)
        .mean()
    )

    loss = (
        (-delta.where(delta < 0, 0))
        .rolling(window=window)
        .mean()
    )

    rs = gain / loss

    return 100 - (100 / (1 + rs))


def calculate_macd(data, fast=12, slow=26, signal=9):

    exp1 = data["Close"].ewm(
        span=fast,
        adjust=False
    ).mean()

    exp2 = data["Close"].ewm(
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

    # 전환선: 9일 최고가와 최저가
    nine_high = data["High"].rolling(
        window=9
    ).max()

    nine_low = data["Low"].rolling(
        window=9
    ).min()

    tenkan_sen = (nine_high + nine_low) / 2

    # 기준선: 26일 최고가와 최저가
    twenty_six_high = data["High"].rolling(
        window=26
    ).max()

    twenty_six_low = data["Low"].rolling(
        window=26
    ).min()

    kijun_sen = (
        twenty_six_high + twenty_six_low
    ) / 2

    # 선행스팬 A
    senkou_span_a = (
        tenkan_sen + kijun_sen
    ) / 2

    # 선행스팬 B
    fifty_two_high = data["High"].rolling(
        window=52
    ).max()

    fifty_two_low = data["Low"].rolling(
        window=52
    ).min()

    senkou_span_b = (
        fifty_two_high + fifty_two_low
    ) / 2

    # 구름대 상단 및 하단
    cloud_top = pd.DataFrame({
        "span_a": senkou_span_a,
        "span_b": senkou_span_b
    }).max(axis=1)

    cloud_bottom = pd.DataFrame({
        "span_a": senkou_span_a,
        "span_b": senkou_span_b
    }).min(axis=1)

    return cloud_top, cloud_bottom


# ============================================================
# 4. 개별 종목 분석 함수
# ============================================================

def analyze_fujimoto_strategy(ticker):

    try:

        # 최근 1년 일봉 데이터 수집
        df = yf.download(
            ticker,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=False
        )

        if df.empty or len(df) < 65:

            logging.warning(
                f"{ticker}: 데이터 부족"
            )

            return None

        # yfinance MultiIndex 처리
        if isinstance(df.columns, pd.MultiIndex):

            df.columns = df.columns.get_level_values(0)

        # 보조지표 계산
        df["RSI"] = calculate_rsi(df)

        df["MACD"], df["Signal"] = calculate_macd(df)

        df["Cloud_Top"], df["Cloud_Bottom"] = (
            calculate_ichimoku(df)
        )

        history_buy_stages = []
        history_sell_stages = []

        # 최근 5거래일 매수/매도 단계 계산
        for i in range(-5, 0):

            sub_df = df.iloc[
                :len(df) + i + 1
            ]

            if len(sub_df) < 60:
                continue

            cur = sub_df.iloc[-1]
            prv = sub_df.iloc[-2]

            # ----------------------------------------
            # 매수 단계 판별
            # ----------------------------------------

            b_stage = 0

            rsi_c1 = (
                prv["RSI"] <= 30
                and cur["RSI"] > 30
            )

            macd_g = (
                prv["MACD"] <= prv["Signal"]
                and cur["MACD"] > cur["Signal"]
            )

            r_lows = sub_df["Low"].iloc[-5:-1]

            r_clouds = (
                sub_df["Cloud_Top"].iloc[-5:-1]
            )

            c_retest = (
                cur["Close"] > cur["Cloud_Top"]
                and (r_lows <= r_clouds).any()
            )

            if c_retest and macd_g and rsi_c1:

                b_stage = 3

            elif macd_g:

                b_stage = 2

            elif rsi_c1:

                b_stage = 1

            # ----------------------------------------
            # 매도 단계 판별
            # ----------------------------------------

            s_stage = 0

            macd_d = (
                prv["MACD"] >= prv["Signal"]
                and cur["MACD"] < cur["Signal"]
            )

            rsi_bear = (
                prv["RSI"] >= 50
                and cur["RSI"] < 50
            )

            c_break = (
                cur["Close"] < cur["Cloud_Bottom"]
            )

            if c_break:

                s_stage = 3

            elif rsi_bear and macd_d:

                s_stage = 2

            elif macd_d:

                s_stage = 1

            history_buy_stages.append(
                str(b_stage)
            )

            history_sell_stages.append(
                str(s_stage)
            )

        # --------------------------------------------
        # 당일 마지막 거래일 기준 정보
        # --------------------------------------------

        current = df.iloc[-1]

        buy_stage = (
            int(history_buy_stages[-1])
            if history_buy_stages else 0
        )

        sell_stage = (
            int(history_sell_stages[-1])
            if history_sell_stages else 0
        )

        # --------------------------------------------
        # 매수 사유
        # --------------------------------------------

        buy_reason = "관망 (신호 대기)"

        if buy_stage == 3:

            buy_reason = (
                "매수 3단계 (최종 확신 - 누적 비중 9: "
                "구름대 리테스트)"
            )

        elif buy_stage == 2:

            buy_reason = (
                "매수 2단계 (확인 - 누적 비중 3: "
                "MACD 골든크로스)"
            )

        elif buy_stage == 1:

            buy_reason = (
                "매수 1단계 (탐색전 - 비중 1: "
                "RSI 30 상향 돌파)"
            )

        # --------------------------------------------
        # 매도 사유
        # --------------------------------------------

        sell_reason = "보유 유지"

        if sell_stage == 3:

            sell_reason = (
                "매도 3단계 (추세 파괴 - 비중 6 전량 청산: "
                "구름대 이탈)"
            )

        elif sell_stage == 2:

            sell_reason = (
                "매도 2단계 (추세 약화 - 비중 2 추가 매도: "
                "RSI 약세)"
            )

        elif sell_stage == 1:

            sell_reason = (
                "매도 1단계 (경고등 - 비중 1 매도: "
                "MACD 데드크로스)"
            )

        # --------------------------------------------
        # 매수 또는 매도 신호가 있는 종목만 반환
        # --------------------------------------------

        if buy_stage > 0 or sell_stage > 0:

            return {

                "Ticker": ticker,

                "Close Price": round(
                    float(current["Close"]), 2
                ),

                "RSI": round(
                    float(current["RSI"]), 2
                ),

                "Buy Stage": f"{buy_stage}단계",

                "Buy Reason": buy_reason,

                "Sell Stage": f"{sell_stage}단계",

                "Sell Reason": sell_reason,

                "5Day Buy History": " ➔ ".join(
                    history_buy_stages
                ),

                "5Day Sell History": " ➔ ".join(
                    history_sell_stages
                )

            }

        return None

    except Exception as e:

        logging.error(
            f"{ticker} 분석 실패: {e}"
        )

        return None


# ============================================================
# 5. Google Drive 인증
# ============================================================

def get_drive_service():

    token_info = json.loads(
        GOOGLE_TOKEN_JSON
    )

    credentials = (
        Credentials.from_authorized_user_info(
            token_info,
            SCOPES
        )
    )

    # Access Token 만료 시 자동 갱신
    if credentials.expired:

        if credentials.refresh_token:

            credentials.refresh(Request())

        else:

            raise RuntimeError(
                "Google Drive Refresh Token이 없습니다."
            )

    if not credentials.valid:

        raise RuntimeError(
            "Google Drive 인증이 유효하지 않습니다."
        )

    service = build(
        "drive",
        "v3",
        credentials=credentials
    )

    return service


# ============================================================
# 6. Google Drive CSV 업로드
# ============================================================

def upload_to_google_drive(file_path):

    logging.info(
        "Google Drive 업로드 시작"
    )

    service = get_drive_service()

    file_name = os.path.basename(
        file_path
    )

    file_metadata = {

        "name": file_name,

        "parents": [
            DRIVE_FOLDER_ID
        ]

    }

    with open(file_path, "rb") as f:

        media = MediaIoBaseUpload(
            f,
            mimetype="text/csv",
            resumable=True
        )

        uploaded_file = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id,name"
            )
            .execute()
        )

    logging.info(
        f"Google Drive 업로드 완료: "
        f"{uploaded_file['name']}"
    )

    logging.info(
        f"Google Drive 파일 ID: "
        f"{uploaded_file['id']}"
    )


# ============================================================
# 7. 전체 종목 분석 및 CSV 저장
# ============================================================

def run_analysis():

    results = []

    total = len(all_tickers)

    logging.info("=" * 60)

    logging.info(
        "후지모토 1:2:6 전략 분석 시작"
    )

    logging.info(
        f"전체 분석 대상 종목: {total}개"
    )

    logging.info("=" * 60)

    # 전체 종목 분석
    for idx, ticker in enumerate(
        all_tickers, 1
    ):

        logging.info(
            f"[{idx}/{total}] 분석 중: {ticker}"
        )

        res = analyze_fujimoto_strategy(
            ticker
        )

        if res is not None:

            results.append(res)

            logging.info(
                f"{ticker}: 매수/매도 신호 포착"
            )

    # --------------------------------------------
    # CSV 생성
    # --------------------------------------------

    columns = [

        "Ticker",
        "Close Price",
        "RSI",
        "Buy Stage",
        "Buy Reason",
        "Sell Stage",
        "Sell Reason",
        "5Day Buy History",
        "5Day Sell History"

    ]

    df_result = pd.DataFrame(
        results,
        columns=columns
    )

    # 한국시간 기준 파일명
    now = datetime.now(KST)

    file_name = (
        "fujimoto_strategy_results_"
        + now.strftime("%Y%m%d_%H%M%S")
        + ".csv"
    )

    output_path = os.path.join(
        os.getcwd(),
        file_name
    )

    # CSV 저장
    df_result.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    logging.info("=" * 60)

    logging.info(
        f"분석 완료: {total}개 종목"
    )

    logging.info(
        f"신호 포착 종목: {len(results)}개"
    )

    logging.info(
        f"CSV 파일 생성 완료: {file_name}"
    )

    logging.info("=" * 60)

    # 결과 출력
    if results:

        print(
            df_result.to_string(index=False)
        )

    else:

        logging.warning(
            "현재 1~3단계 매수/매도 신호가 없습니다."
        )

        print(
            "현재 1~3단계 매수/매도 신호가 없습니다."
        )

    # --------------------------------------------
    # Google Drive 업로드
    # --------------------------------------------

    upload_to_google_drive(
        output_path
    )

    logging.info("=" * 60)

    logging.info(
        "전체 주식 분석 및 Google Drive 저장 완료"
    )

    logging.info("=" * 60)


# ============================================================
# 8. 프로그램 실행
# ============================================================

if __name__ == "__main__":

    try:

        run_analysis()

    except Exception:

        logging.exception(
            "주식 분석 프로그램 실행 실패"
        )

        raise
