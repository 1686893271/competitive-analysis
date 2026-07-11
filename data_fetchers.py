import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

PROXY_URL = os.getenv("PROXY_URL")
BTC_ID = os.getenv("BTC_ID", "90")
ETH_ID = os.getenv("ETH_ID", "80")

proxies = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None


def fetch_price_coinlore(coin_id: str) -> dict:
    try:
        url = f"https://api.coinlore.com/api/ticker/?id={coin_id}"
        resp = requests.get(url, proxies=proxies, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            return {
                "source": "coinlore",
                "price": float(data[0].get("price_usd", 0)),
                "percent_change_24h": float(data[0].get("percent_change_24h", 0)),
                "high_24h": float(data[0].get("price_usd", 0)) * 1.02,
                "low_24h": float(data[0].get("price_usd", 0)) * 0.98,
            }
    except Exception as e:
        print(f"Coinlore fetch failed: {e}")
    return None


def fetch_price_binance(symbol: str) -> dict:
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        resp = requests.get(url, proxies=proxies, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "source": "binance",
            "price": float(data.get("lastPrice", 0)),
            "percent_change_24h": float(data.get("priceChangePercent", 0)),
            "high_24h": float(data.get("highPrice", 0)),
            "low_24h": float(data.get("lowPrice", 0)),
        }
    except Exception as e:
        print(f"Binance fetch failed: {e}")
    return None


def fetch_price_coingecko(coin_id: str) -> dict:
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
        resp = requests.get(url, proxies=proxies, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if coin_id in data:
            return {
                "source": "coingecko",
                "price": float(data[coin_id].get("usd", 0)),
                "percent_change_24h": float(data[coin_id].get("usd_24h_change", 0)),
                "high_24h": float(data[coin_id].get("usd", 0)) * 1.02,
                "low_24h": float(data[coin_id].get("usd", 0)) * 0.98,
            }
    except Exception as e:
        print(f"CoinGecko fetch failed: {e}")
    return None


def fetch_price_with_fallback(coin_type: str) -> dict:
    if coin_type == "btc":
        coin_id = BTC_ID
        binance_symbol = "BTCUSDT"
        coingecko_id = "bitcoin"
    elif coin_type == "eth":
        coin_id = ETH_ID
        binance_symbol = "ETHUSDT"
        coingecko_id = "ethereum"
    else:
        raise ValueError("coin_type must be 'btc' or 'eth'")

    result = fetch_price_coinlore(coin_id)
    if result and result["price"] > 0:
        return result

    result = fetch_price_binance(binance_symbol)
    if result and result["price"] > 0:
        return result

    result = fetch_price_coingecko(coingecko_id)
    if result and result["price"] > 0:
        return result

    raise Exception(f"All price sources failed for {coin_type}")


def fetch_klines_binance(symbol: str, interval: str, limit: int = 24) -> list:
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        resp = requests.get(url, params=params, proxies=proxies, timeout=15)
        resp.raise_for_status()
        klines = resp.json()
        result = []
        for kline in klines:
            result.append({
                "timestamp": int(kline[0]),
                "open": float(kline[1]),
                "high": float(kline[2]),
                "low": float(kline[3]),
                "close": float(kline[4]),
                "volume": float(kline[5]),
            })
        return result
    except Exception as e:
        print(f"Binance klines fetch failed: {e}")
        return []


def fetch_btc_1h_klines(limit: int = 24) -> list:
    return fetch_klines_binance("BTCUSDT", "1h", limit)


def fetch_btc_daily_klines(limit: int = 20) -> list:
    return fetch_klines_binance("BTCUSDT", "1d", limit)


def fetch_eth_1h_klines(limit: int = 24) -> list:
    return fetch_klines_binance("ETHUSDT", "1h", limit)


def fetch_eth_daily_klines(limit: int = 20) -> list:
    return fetch_klines_binance("ETHUSDT", "1d", limit)