from numpy import result_type, short
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
        with open("symbols_gb.txt", "r") as file: 
            gb_symbols = file.read().splitlines()
            symbols.extend(gb_symbols)

    if market == "us" or market == "all": 
        with open("symbols_us.txt", "r") as file: 
            us_symbols = file.read().splitlines()
            symbols.extend(us_symbols)

    if market == "cn" or market == "all": 
        with open("symbols_cn.txt", "r") as file: 
            cn_symbols = file.read().splitlines()
            symbols.extend(cn_symbols)
    return symbols

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

    if currency == "CNY": 
        return True
        # if market_cap > 10000000000: 
        #     return True
        # return False
    return False

def calculate_moving_average(data, days): 
    return data.tail(days).iloc[:,3].mean()

def check_downtrend(data): 
    total_days = len(data.index)
    MA5 = []
    MA10 = []
    MA20 = []
    
    candle_count = total_days - 10
    while candle_count < total_days: 
        MA5.append(calculate_moving_average(data.iloc[ : candle_count + 1], 5))
        MA10.append(calculate_moving_average(data.iloc[ : candle_count + 1], 10))
        MA20.append(calculate_moving_average(data.iloc[ : candle_count + 1], 20))
        candle_count += 1

    checker_count = 0
    day_count = 0
    while checker_count < 10: 
        if MA20[checker_count] > MA10[checker_count] > MA5[checker_count]: 
            day_count += 1
        else: 
            day_count = 0
        
        if day_count == 3: 
            return True
        
        checker_count += 1

    return False
    
def read_single_candle(data): 
    """
    Virtually create a candlestick

    日K
    """

    candle = {}
    candle['date'] = data.index[0].strftime(r'%Y-%m-%d')
    candle['open'] = data.iloc[0]['Open']
    candle['high'] = data.iloc[0]['High']
    candle['low'] = data.iloc[0]['Low']
    candle['close'] = data.iloc[0]['Close']

    candle['full_range'] = candle['high'] - candle['low']
    if candle['full_range'] == 0: 
        return None
        
    candle['upper_shadow'] = candle['high'] - max(candle['open'], candle['close'])
    candle['body'] = abs(candle['open'] - candle['close'])
    candle['lower_shadow'] = min(candle['open'], candle['close']) - candle['low']
    return candle

def check_hammer(stock, data): 
    """
    Check for hammer and inverted hammer
    
    锤，倒锤
    """

    if not check_downtrend(data.tail(30)): 
        return False

    data = data.tail(1)
    candle = read_single_candle(data)
    if candle == None: 
        return False

    if candle['lower_shadow'] > 2 * candle['body'] and candle['upper_shadow'] / candle['full_range'] <= 0.1: 
        enable_print()
        print(f"Hammer, {stock.info['symbol']} ({stock.info['shortName']}), {candle['date']}")
        disable_print()
    elif candle['upper_shadow'] > 2 * candle['body'] and candle['lower_shadow'] / candle['full_range'] <= 0.1: 
        enable_print()
        print(f"Inverted hammer, {stock.info['symbol']} ({stock.info['shortName']}), {candle['date']}")
        disable_print()
    else: 
        return False
    return True

def check_doji(stock, data): 
    """
    Check for doji, long-legged doji and spinning top

    十字星，长十字星，螺旋桨
    """
    
    if not check_downtrend(data.tail(30)): 
        return False

    data = data.tail(1)
    candle = read_single_candle(data)
    if candle == None: 
        return False
    
    if candle['upper_shadow'] / candle['full_range'] >= 0.3 and candle['lower_shadow'] / candle['full_range'] >= 0.3: 
        if candle['body'] / candle['full_range'] <= 0.05: 
            if candle['upper_shadow'] / candle['open'] >= 0.03 and candle['lower_shadow'] / candle['open'] >= 0.03: 
                enable_print()
                print(f"Long-legged doji, {stock.info['symbol']} ({stock.info['shortName']}), {candle['date']}")
                disable_print()
            else: 
                enable_print()
                print(f"Doji, {stock.info['symbol']} ({stock.info['shortName']}), {candle['date']}")
                disable_print()
        elif candle['body'] / candle['full_range'] <= 0.3: 
            enable_print()
            print(f"Spinning top, {stock.info['symbol']} ({stock.info['shortName']}), {candle['date']}")
            disable_print()
        return True
    else: 
        return False

def check_marubozu(stock, data): 
    """
    Check for marubozu

    光头光脚阳线
    """
    
    if not check_downtrend(data.tail(30)): 
        return False

    data = data.tail(1)
    candle = read_single_candle(data)
    if candle == None: 
        return False

    short_upper_shadow = True if candle['upper_shadow'] / candle['full_range'] <= 0.05 else False
    short_lower_shadow = True if candle['lower_shadow'] / candle['full_range'] <= 0.05 else False
    long_body = True if candle['body'] / candle['full_range'] >= 0.7 else False
    soar = True if (candle['close'] - candle['open']) / candle['open'] >= 0.01 else False
    
    if long_body and soar: 
        if short_upper_shadow and short_lower_shadow: 
            enable_print()
            print(f"Marubozu, {stock.info['symbol']} ({stock.info['shortName']}), {candle['date']}")
            disable_print()
            return True
        elif short_upper_shadow: 
            enable_print()
            print(f"Marubozu closing, {stock.info['symbol']} ({stock.info['shortName']}), {candle['date']}")
            disable_print()
            return True
        elif short_lower_shadow: 
            enable_print()
            print(f"Marubozu opening, {stock.info['symbol']} ({stock.info['shortName']}), {candle['date']}")
            disable_print()
            return True
    
    return False

def check_engulfing(stock, data): 
    """
    Check for bullish engulfing

    阳包阴
    """
    
    if not check_downtrend(data.tail(30)): 
        return False

    data = data.tail(2)
    total_days = len(data.index)
    candles = []

    candle_count = 0
    while candle_count < total_days: 
        candles.append(read_single_candle(data.iloc[candle_count : candle_count + 1]))
        candle_count += 1

    if candles[0]['close'] < candles[0]['open'] and candles[1]['close'] > candles[1]['open'] and candles[1]['open'] < candles[0]['close'] and candles[1]['close'] > candles[0]['open']: 
        enable_print()
        print(f"Engulfing, {stock.info['symbol']} ({stock.info['shortName']}), {candles[0]['date']} ~ {candles[1]['date']}")
        disable_print()
        return True
    else: 
        return False

def check_three_white_soldiers(stock, data): 
    """
    Check for three white soldiers

    红三兵
    """

    if not check_downtrend(data.tail(30)): 
        return False

    data = data.tail(3)
    total_days = len(data.index)
    candles = []

    candle_count = 0
    while candle_count < total_days: 
        candles.append(read_single_candle(data.iloc[candle_count : candle_count + 1]))

        candle_count += 1

    all_rise = True if candles[0]['close'] > candles[0]['open'] and candles[1]['close'] > candles[1]['open'] and candles[2]['close'] > candles[2]['open'] else False
    all_long_body = True if candles[0]['body'] / candles[0]['full_range'] >= 0.7 and candles[1]['body'] / candles[1]['full_range'] >= 0.7 and candles[2]['body'] / candles[2]['full_range'] >= 0.7 else False

    if all_rise and all_long_body: 
        for index in range(total_days - 1): 
            if not (candles[index + 1]['close'] > candles[index]['high'] and candles[index]['open'] <= candles[index + 1]['open'] <= candles[index]['close']): 
                return False
        
        enable_print()
        print(f"Three white soldiers, {stock.info['symbol']} ({stock.info['shortName']}), {candles[0]['date']} ~ {candles[2]['date']}")
        disable_print()
        return True
    
    return False

def check_twin_needle(stock, data): 
    """
    Check for twin needle (bottom)

    双针探底
    """
    
    if not check_downtrend(data.tail(30)): 
        return False

    data = data.tail(5)
    total_days = len(data.index)
    candles = []
    lows = []

    candle_count = 0
    while candle_count < total_days: 
        candles.append(read_single_candle(data.iloc[candle_count : candle_count + 1]))

        lows.append(candles[candle_count]['low'])
        candle_count += 1
    
    # Find 2 smallest lows
    lowest_index_1 = lows.index(min(lows))
    lowest_candle_1 = candles.pop(lowest_index_1)
    lows.pop(lowest_index_1)

    lowest_index_2 = lows.index(min(lows))
    lowest_candle_2 = candles.pop(lowest_index_2)

    all_long_candle = True if lowest_candle_1['full_range'] / lowest_candle_1['open'] >= 0.01 and lowest_candle_2['full_range'] / lowest_candle_2['open'] >= 0.01 else False

    if abs(lowest_candle_1['low'] - lowest_candle_2['low']) / lowest_candle_2['close'] <= 0.003 and all_long_candle and lowest_candle_1['lower_shadow'] / lowest_candle_1['full_range'] >= 0.3 and lowest_candle_2['lower_shadow'] / lowest_candle_2['full_range'] >= 0.3: 
        enable_print()
        print(f"Twin needle, {stock.info['symbol']} ({stock.info['shortName']}), {lowest_candle_1['date']} & {lowest_candle_2['date']}")
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
    candles = []
    highs = []
    lows = []

    candle_count = 0
    while candle_count < total_days: 
        candles.append(read_single_candle(data.iloc[candle_count : candle_count + 1]))

        highs.append(candles[candle_count]['high'])
        lows.append(candles[candle_count]['low'])
        candle_count += 1

    # Save high and low prices into lists
    candle_count = 0
    while candle_count < total_days: 
        highs.append(data.iloc[candle_count]['High'])
        lows.append(data.iloc[candle_count]['Low'])
        candle_count += 1

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
                current_date = datetime.now()

                delta = current_date - data.index[day_count_end]
                delta_days = delta.days
                
                if delta_days < max_days:  # The island is formed recently enough
                    enable_print()
                    print(f"Island, {stock.info['symbol']} ({stock.info['shortName']}), {candles[day_count_start]['date']} ~ {candles[day_count_end]['date']}")
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

            if not check_market_cap(stock.info["financialCurrency"], stock.info["marketCap"]): 
                continue

            # get data of this stock
            data = yf.download(stock.info['symbol'], period="3mo", show_errors=False)
            
            # enable_print()
            # print(data.tail(1+1).iloc[:,3].pct_change())
            # disable_print()

            result = any([check_hammer(stock, data), 
                         check_doji(stock, data), 
                         check_marubozu(stock, data), 
                         check_engulfing(stock, data), 
                         check_three_white_soldiers(stock, data), 
                         check_twin_needle(stock, data), 
                         check_island(stock, data, 3)])
            
            # if result: 
            #     webbrowser.open(f"https://uk.finance.yahoo.com/chart/{stock.info['symbol']}")
        except Exception as e: 
            pass

if __name__ == "__main__":
    main()