import yfinance as yf

import sys
import os
from datetime import datetime
import webbrowser

def enable_print(): 
    sys.stdout = sys.__stdout__

def disable_print(): 
    sys.stdout = open(os.devnull, "w")

def load_symbols(market): 
    """
    Load stock symbols

        Allowed inputs for market: gb, us, cn, all
    """

    symbols = []

    if market == "gb" or market == "all": 
        with open("gb_symbols.txt", "r") as file: 
            gb_symbols = file.read().splitlines()
            symbols.extend(gb_symbols)

    if market == "us" or market == "all": 
        with open("us_symbols.txt", "r") as file: 
            us_symbols = file.read().splitlines()
            symbols.extend(us_symbols)

    if market == "cn" or market == "all": 
        with open("cn_symbols.txt", "r") as file: 
            cn_symbols = file.read().splitlines()
            symbols.extend(cn_symbols)
    return symbols

def check_market(market): 
    """
    Check market of a stock

        Allowed inputs for market: us_market, gb_market, cn_market
    """

    market_list = ["us_market", "gb_market", "cn_market"]
    if market in market_list: 
        return True
    return False

def check_market_cap(currency, market_cap): 
    """
    Filter company size by its market cap

    流通市值
    """

    # enable_print()
    # print(currency)
    # print(market_cap)
    # disable_print()

    if currency == "GBP": 
        if market_cap > 5000000000: 
            return True
        return False

    if currency == "USD": 
        if market_cap > 7000000000: 
            return True
        return False

    # if currency == "CNY": 
    #     if market_cap > 10000000000: 
    #         return True
    #     return False
    return False

def read_single_candle(candle): 
    """
    Virtually create a candlestick

    日K
    """

    candle_data = {}
    candle_data['date'] = candle.index[0].strftime(r"%Y-%m-%d")
    candle_data['open'] = candle.iloc[0][0]
    candle_data['high'] = candle.iloc[0][1]
    candle_data['low'] = candle.iloc[0][2]
    candle_data['close'] = candle.iloc[0][3]

    candle_data['full_range'] = candle_data['high'] - candle_data['low']
    if candle_data['full_range'] == 0: 
        return None
        
    candle_data['upper_shadow'] = candle_data['high'] - max(candle_data['open'], candle_data['close'])
    candle_data['body'] = abs(candle_data['open'] - candle_data['close'])
    candle_data['lower_shadow'] = min(candle_data['open'], candle_data['close']) - candle_data['low']
    return candle_data

def check_hammer(stock, candle): 
    """
    Check for hammer and inverted hammer
    
    锤，倒锤
    """

    candle_data = read_single_candle(candle)
    if candle_data == None: 
        return False

    if candle_data['lower_shadow'] > 2 * candle_data['body'] and candle_data['upper_shadow'] / candle_data['full_range'] <= 0.1: 
        enable_print()
        print(f"Hammer, {stock.info['symbol']} ({stock.info['shortName']}), {candle_data['date']}")
        disable_print()
    elif candle_data['upper_shadow'] > 2 * candle_data['body'] and candle_data['lower_shadow'] / candle_data['full_range'] <= 0.1: 
        enable_print()
        print(f"Inverted hammer, {stock.info['symbol']} ({stock.info['shortName']}), {candle_data['date']}")
        disable_print()
    else: 
        return False
    return True

def check_doji(stock, candle): 
    """
    Check for doji, long-legged doji and propeller

    十字星，长十字星，螺旋桨
    """

    candle_data = read_single_candle(candle)
    if candle_data == None: 
        return False
    
    if candle_data['upper_shadow'] / candle_data['full_range'] >= 0.3 and candle_data['lower_shadow'] / candle_data['full_range'] >= 0.3: 
        if candle_data['body'] / candle_data['full_range'] <= 0.05: 
            if candle_data['upper_shadow'] / candle_data['open'] >= 0.03 and candle_data['lower_shadow'] / candle_data['open'] >= 0.03: 
                enable_print()
                print(f"Long-legged doji, {stock.info['symbol']} ({stock.info['shortName']}), {candle_data['date']}")
                disable_print()
            else: 
                enable_print()
                print(f"Doji, {stock.info['symbol']} ({stock.info['shortName']}), {candle_data['date']}")
                disable_print()
        elif candle_data['body'] / candle_data['full_range'] <= 0.3: 
            enable_print()
            print(f"Propeller, {stock.info['symbol']} ({stock.info['shortName']}), {candle_data['date']}")
            disable_print()
        return True
    else: 
        return False

def check_engulfing(stock, candles): 
    """
    Check for bullish engulfing

    阳包阴
    """

    start_date = candles.index[0].strftime(r"%Y-%m-%d")
    end_date = candles.index[1].strftime(r"%Y-%m-%d")

    day1_open = candles.iloc[0][0]
    day1_close = candles.iloc[0][3]
    day2_open = candles.iloc[1][0]
    day2_close = candles.iloc[1][3]

    if day1_close < day1_open and day2_close > day2_open and day2_open < day1_close and day2_close > day1_open: 
        enable_print()
        print(f"Engulfing, {stock.info['symbol']} ({stock.info['shortName']}), {start_date} ~ {end_date}")
        disable_print()
        return True
    else: 
        return False

def check_island(stock, data, max_days): 
    """
    Check for island reversal

    岛形反转
    """

    total_days = len(data.index)
    highs = []
    lows = []

    # Save high and low prices into lists
    data_count = 0

    while data_count < total_days: 
        highs.append(data.iloc[data_count][1])
        lows.append(data.iloc[data_count][2])

        data_count += 1

    day_count_start = 0

    # Check start of island
    while day_count_start < total_days - 1: # No need to check the last day 
        if lows[day_count_start] > highs[day_count_start + 1]: 
            day_count_end = day_count_start + 2

            # Check end of island
            while day_count_end < total_days: 
                if lows[day_count_start] > max(highs[day_count_start + 1: day_count_end + 1]): 
                    day_count_end += 1

                    if day_count_end == total_days: 
                        return False # This is a cliff (half island)
                else: 
                    break # This is a potential end of island

            if lows[day_count_end] > max(highs[day_count_start + 1: day_count_end]): 
                start_date = data.index[day_count_start].strftime(r"%Y-%m-%d")
                end_date = data.index[day_count_end].strftime(r"%Y-%m-%d")
                current_date = datetime.now()

                delta = current_date - data.index[day_count_end]
                delta_days = delta.days
                
                if delta_days < max_days:  # The island is formed recently enough
                    enable_print()
                    print(f"Island, {stock.info['symbol']} ({stock.info['shortName']}), {start_date} ~ {end_date}")
                    disable_print()
                    return True # This is an island
            
        day_count_start += 1
    
    return False # There is no island
        
def main(): 
    symbols = load_symbols("all")
    
    for symbol in symbols: 

        # enable_print()
        # print(symbol)
        # disable_print()

        try: 
            disable_print()

            stock = yf.Ticker(symbol)

            # enable_print()
            # for key in stock.info: 
            #     print(f"{key}: {stock.info[key]}\n")
            # disable_print()

            if not check_market(stock.info['market']): 
                continue

            if not check_market_cap(stock.info["financialCurrency"], stock.info["marketCap"]): 
                continue

            # get data of this stock
            data = yf.download(stock.info['symbol'], period="3mo", show_errors=False)
            
            # enable_print()
            # print(data)
            # disable_print()

            result = any([check_hammer(stock, data.tail(1)), 
                         check_doji(stock, data.tail(1)), 
                         check_engulfing(stock, data.tail(2)), 
                         check_island(stock, data, 3)])
            
            if result: 
                webbrowser.open(f"https://uk.finance.yahoo.com/chart/{stock.info['symbol']}")
        except Exception as e: 
            pass

if __name__ == "__main__":
    main()