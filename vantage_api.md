# Alpha Vantage API Documentation

## 1. Overview
Alpha Vantage provides real-time and historical stock APIs, forex (FX), and cryptocurrency data feeds. The data is accessible via simple HTTP GET requests returning JSON or CSV formats.

**Base URL:**
```
https://www.alphavantage.co/query
```

**Authentication:**
All API requests require an API key parameter: `apikey=YOUR_API_KEY`.
- [Claim a free API key](https://www.alphavantage.co/support/#api-key)

**Common Request Structure:**
`GET /query?function=[FUNCTION_NAME]&symbol=[SYMBOL]&apikey=[KEY]&...`

---

## 2. Core Stock APIs (Time Series)
These APIs provide global equity data in various temporal resolutions.

### 2.1 Intraday & Daily Series

| Function Name | Description | Required Parameters | Optional Parameters |
| :--- | :--- | :--- | :--- |
| `TIME_SERIES_INTRADAY` | Intraday OHLCV (1min, 5min, etc.) | `symbol`, `interval` | `adjusted`, `extended_hours`, `month`, `outputsize`, `datatype` |
| `TIME_SERIES_DAILY` | Daily OHLCV (20+ years) | `symbol` | `outputsize`, `datatype` |
| `TIME_SERIES_DAILY_ADJUSTED` | Daily OHLCV + Split/Div Adjustments | `symbol` | `outputsize`, `datatype` |

**Parameters:**
- `interval`: `1min`, `5min`, `15min`, `30min`, `60min`
- `outputsize`: `compact` (latest 100), `full` (history)
- `datatype`: `json` (default), `csv`

### 2.2 Weekly & Monthly Series

| Function Name | Description | Required Parameters | Optional Parameters |
| :--- | :--- | :--- | :--- |
| `TIME_SERIES_WEEKLY` | Weekly OHLCV | `symbol` | `datatype` |
| `TIME_SERIES_WEEKLY_ADJUSTED` | Weekly OHLCV + Adjustments | `symbol` | `datatype` |
| `TIME_SERIES_MONTHLY` | Monthly OHLCV | `symbol` | `datatype` |
| `TIME_SERIES_MONTHLY_ADJUSTED` | Monthly OHLCV + Adjustments | `symbol` | `datatype` |

### 2.3 Quote & Search

| Function Name | Description | Parameters |
| :--- | :--- | :--- |
| `GLOBAL_QUOTE` | Latest price & volume for a ticker | `symbol` |
| `REALTIME_BULK_QUOTES` | (Premium) Realtime quotes for up to 100 symbols | `symbol` (comma-separated) |
| `SYMBOL_SEARCH` | Search for ticker by keywords | `keywords` |
| `MARKET_STATUS` | Global market open/close status | (None) |

---

## 3. Options Data APIs (US Markets)

| Function Name | Description | Parameters |
| :--- | :--- | :--- |
| `REALTIME_OPTIONS` | (Premium) Realtime US options chain | `symbol`, `contract` (optional), `require_greeks` |
| `HISTORICAL_OPTIONS` | (Premium) Historical options chain | `symbol`, `date` (YYYY-MM-DD) |

---

## 4. Alpha Intelligence & Market News

| Function Name | Description | Key Parameters |
| :--- | :--- | :--- |
| `NEWS_SENTIMENT` | Live & historical news with sentiment | `tickers`, `topics`, `time_from`, `time_to`, `sort`, `limit` |
| `TOP_GAINERS_LOSERS` | Top 20 gainers, losers, active (US) | (None) |
| `INSIDER_TRANSACTIONS` | Insider transaction history | `symbol` |
| `EARNINGS_CALL_TRANSCRIPT` | Quarterly earnings transcripts | `symbol`, `quarter` (YYYYQM) |
| `ANALYTICS_FIXED_WINDOW` | Return, volatility, correlation (Fixed) | `SYMBOLS`, `RANGE`, `INTERVAL`, `CALCULATIONS`, `OHLC` |
| `ANALYTICS_SLIDING_WINDOW` | Return, volatility, correlation (Sliding) | `SYMBOLS`, `RANGE`, `INTERVAL`, `WINDOW_SIZE`, `CALCULATIONS` |

---

## 5. Fundamental Data
Financial statements and company metrics.

| Function Name | Description | Parameters |
| :--- | :--- | :--- |
| `OVERVIEW` | Company profile & financial ratios | `symbol` |
| `INCOME_STATEMENT` | Annual & quarterly income statements | `symbol` |
| `BALANCE_SHEET` | Annual & quarterly balance sheets | `symbol` |
| `CASH_FLOW` | Annual & quarterly cash flow | `symbol` |
| `EARNINGS` | Earnings history (EPS) | `symbol` |
| `EARNINGS_ESTIMATES` | Analyst estimates (EPS, Revenue) | `symbol` |
| `DIVIDENDS` | Historical dividend data | `symbol` |
| `SPLITS` | Historical split data | `symbol` |
| `SHARES_OUTSTANDING` | Quarterly shares outstanding | `symbol` |
| `ETF_PROFILE` | ETF details & holdings | `symbol` |
| `LISTING_STATUS` | Active/Delisted tokens (CSV preferred) | `date`, `state` (active/delisted) |
| `EARNINGS_CALENDAR` | Upcoming earnings (3/6/12 months) | `symbol`, `horizon` |
| `IPO_CALENDAR` | Upcoming IPOs | (None) |

---

## 6. Forex & Cryptocurrencies

### 6.1 Exchange Rates
| Function Name | Description | Parameters |
| :--- | :--- | :--- |
| `CURRENCY_EXCHANGE_RATE` | Realtime exchange rate (Crypto/Forex) | `from_currency`, `to_currency` |

### 6.2 Forex Time Series
| Function Name | Description | Parameters |
| :--- | :--- | :--- |
| `FX_INTRADAY` | Intraday FX (1/5/15/30/60 min) | `from_symbol`, `to_symbol`, `interval`, `outputsize` |
| `FX_DAILY` | Daily FX rates | `from_symbol`, `to_symbol`, `outputsize` |
| `FX_WEEKLY` | Weekly FX rates | `from_symbol`, `to_symbol` |
| `FX_MONTHLY` | Monthly FX rates | `from_symbol`, `to_symbol` |

### 6.3 Crypto Time Series
| Function Name | Description | Parameters |
| :--- | :--- | :--- |
| `CRYPTO_INTRADAY` | (Premium) Intraday Crypto | `symbol`, `market`, `interval`, `outputsize` |
| `DIGITAL_CURRENCY_DAILY` | Daily Crypto | `symbol`, `market` |
| `DIGITAL_CURRENCY_WEEKLY` | Weekly Crypto | `symbol`, `market` |
| `DIGITAL_CURRENCY_MONTHLY` | Monthly Crypto | `symbol`, `market` |

---

## 7. Commodities & Economic Indicators

### 7.1 Commodities
**Function Names:**
`WTI`, `BRENT`, `NATURAL_GAS`, `COPPER`, `ALUMINUM`, `WHEAT`, `CORN`, `COTTON`, `SUGAR`, `COFFEE`, `ALL_COMMODITIES`

**Parameters:** `interval` (monthly/quarterly/annual)

### 7.2 Economic Indicators
**Function Names:**
`REAL_GDP`, `REAL_GDP_PER_CAPITA`, `TREASURY_YIELD`, `FEDERAL_FUNDS_RATE`, `CPI`, `INFLATION`, `RETAIL_SALES`, `DURABLES`, `UNEMPLOYMENT`, `NONFARM_PAYROLL`

**Parameters:** `interval` (varies by indicator), `maturity` (for Treasury)

---

## 8. Technical Indicators
All indicators use the base URL structure: `function=[INDICATOR]&symbol=[SYM]&interval=[INT]...`

**Common Parameters for almost all indicators:**
- `symbol`: Ticker name.
- `interval`: `1min`, `5min`, `15min`, `30min`, `60min`, `daily`, `weekly`, `monthly`.
- `month`: (Optional) Specific month YYYY-MM.
- `datatype`: `json` or `csv`.

### 8.1 Moving Averages & Overlays
| Indicator | Name | Specific Parameters |
| :--- | :--- | :--- |
| `SMA` | Simple Moving Average | `time_period`, `series_type` |
| `EMA` | Exponential Moving Average | `time_period`, `series_type` |
| `WMA` | Weighted Moving Average | `time_period`, `series_type` |
| `DEMA` | Double EMA | `time_period`, `series_type` |
| `TEMA` | Triple EMA | `time_period`, `series_type` |
| `TRIMA` | Triangular Moving Average | `time_period`, `series_type` |
| `KAMA` | Kaufman Adaptive MA | `time_period`, `series_type` |
| `MAMA` | MESA Adaptive MA | `series_type`, `fastlimit`, `slowlimit` |
| `T3` | T3 Moving Average | `time_period`, `series_type` |
| `VWAP` | Volume Weighted Avg Price | (Intraday only) |
| `BBANDS` | Bollinger Bands | `time_period`, `series_type`, `nbdevup`, `nbdevdn`, `matype` |
| `HT_TRENDLINE` | Hilbert Transform Trendline | `series_type` |
| `SAR` | Parabolic SAR | `acceleration`, `maximum` |

### 8.2 Momentum & Oscillators
| Indicator | Name | Specific Parameters |
| :--- | :--- | :--- |
| `RSI` | Relative Strength Index | `time_period`, `series_type` |
| `STOCH` | Stochastic | `fastkperiod`, `slowkperiod`, `slowdperiod`, `slowkmatype`, `slowdmatype` |
| `STOCHF` | Stochastic Fast | `fastkperiod`, `fastdperiod`, `fastdmatype` |
| `STOCHRSI` | Stochastic RSI | `time_period`, `series_type`, `fastkperiod`, `fastdperiod`, `fastdmatype` |
| `MACD` | Moving Avg Conv/Div | `series_type`, `fastperiod`, `slowperiod`, `signalperiod` |
| `MACDEXT` | MACD Extended | `series_type`, `fastperiod`, `slowperiod`, `signalperiod`, `fastmatype`, `slowmatype`, `signalmatype` |
| `WILLR` | Williams %R | `time_period` |
| `ADX` | Avg Directional Index | `time_period` |
| `ADXR` | ADX Rating | `time_period` |
| `APO` | Absolute Price Oscillator | `series_type`, `fastperiod`, `slowperiod`, `matype` |
| `PPO` | Percentage Price Oscillator | `series_type`, `fastperiod`, `slowperiod`, `matype` |
| `MOM` | Momentum | `time_period`, `series_type` |
| `BOP` | Balance of Power | (None) |
| `CCI` | Commodity Channel Index | `time_period` |
| `CMO` | Chande Momentum Oscillator | `time_period`, `series_type` |
| `ROC` | Rate of Change | `time_period`, `series_type` |
| `ROCR` | Rate of Change Ratio | `time_period`, `series_type` |
| `AROON` | Aroon Values | `time_period` |
| `AROONOSC` | Aroon Oscillator | `time_period` |
| `MFI` | Money Flow Index | `time_period` |
| `TRIX` | 1-day ROC of Triple Smooth EMA | `time_period`, `series_type` |
| `ULTOSC` | Ultimate Oscillator | `timeperiod1`, `timeperiod2`, `timeperiod3` |
| `DX` | Directional Movement Index | `time_period` |
| `MINUS_DI` | Minus Directional Indicator | `time_period` |
| `PLUS_DI` | Plus Directional Indicator | `time_period` |
| `MINUS_DM` | Minus Directional Movement | `time_period` |
| `PLUS_DM` | Plus Directional Movement | `time_period` |

### 8.3 Other Indicators
| Indicator | Name | Specific Parameters |
| :--- | :--- | :--- |
| `MIDPOINT` | Midpoint (Price) | `time_period`, `series_type` |
| `MIDPRICE` | Midpoint (High/Low) | `time_period` |
| `TRANGE` | True Range | (None) |
| `ATR` | Average True Range | `time_period` |
| `NATR` | Normalized ATR | `time_period` |
| `AD` | Chaikin A/D Line | (None) |
| `ADOSC` | Chaikin A/D Oscillator | `fastperiod`, `slowperiod` |
| `OBV` | On Balance Volume | (None) |
| `HT_SINE` | Hilbert Transform Sine Wave | `series_type` |
| `HT_TRENDMODE`| Hilbert Transform Trend vs Cycle | `series_type` |
| `HT_DCPERIOD` | Hilbert Transform Dominant Cycle Period | `series_type` |
| `HT_DCPHASE` | Hilbert Transform Dominant Cycle Phase | `series_type` |
| `HT_PHASOR` | Hilbert Transform Phasor Components | `series_type` |

---

## 9. Handling Errors & Rates
- **Success:** JSON response usually contains `Meta Data` and the data key (e.g., `Time Series (5min)`).
- **Error:** JSON response with `{"Error Message": "..."}`.
- **Rate Limit:** JSON response with `{"Note": "Thank you for using Alpha Vantage! Our standard API call frequency is 25 calls per day..."}`.
- **Empty Data:** `{}` or missing keys implies no data for range.

**Best Practices:**
- Check for `Note` key to handle rate limits gracefully.
- Use `outputsize=compact` to reduce latency.
- Cache received data; historical data is immutable.
