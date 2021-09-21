import yfinance as yf

import sys
import os
from datetime import datetime
import webbrowser

def enable_print(): 
    sys.stdout = sys.__stdout__

def disable_print(): 
    sys.stdout = open(os.devnull, "w")

def check_market_cap(currency, market_cap): 
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
    return False

def single_candle(stock, candle): 
    date = candle.index[0].strftime(r"%Y-%m-%d")
    Open = candle.iloc[0][0]
    High = candle.iloc[0][1]
    Low = candle.iloc[0][2]
    Close = candle.iloc[0][3]

    full_range = High - Low
    upper_shadow = High - max(Open, Close)
    body = abs(Open - Close)
    lower_shadow = min(Open, Close) - Low

    enable_print()
    if lower_shadow > 2 * body and upper_shadow / full_range <= 0.1: 
        print(f"Hammer, {stock.info['symbol']} ({stock.info['shortName']}), {date}")
    elif upper_shadow > 2 * body and lower_shadow / full_range <= 0.1: 
        print(f"Inverted hammer, {stock.info['symbol']} ({stock.info['shortName']}), {date}")
    elif body / full_range <= 0.1 and upper_shadow / full_range >= 0.3 and lower_shadow / full_range >= 0.3: 
        print(f"Doji, {stock.info['symbol']} ({stock.info['shortName']}), {date}")
    else: 
        return
    disable_print()

    webbrowser.open(f"https://uk.finance.yahoo.com/chart/{stock.info['symbol']}")

# Check for an island reversal
def check_island(stock, data, max_days): 
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
                        return # This is a cliff (half island)
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

                    webbrowser.open(f"https://uk.finance.yahoo.com/chart/{stock.info['symbol']}")
                
                return # This is an island
            
        day_count_start += 1
    
    return # There is no island
        
def main(): 
    with open("stock.txt", "r") as file: 
        symbols = file.readlines()
    
    for symbol in symbols: 
        symbol = symbol.strip()
        # print(symbol)

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
            # print(data)
            # disable_print()

            latest = data.tail(1)
            single_candle(stock, latest)
            
            check_island(stock, data, 3)
        except Exception as e: 
            pass

if __name__ == "__main__":
    main()