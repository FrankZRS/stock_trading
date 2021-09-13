import yfinance as yf

import sys
import os
from datetime import datetime
import webbrowser

def check_market_cap(currency, market_cap): 
    print(currency)
    print(market_cap)
    # return True
    if currency == "GBP": 
        if market_cap > 5000000000: 
            return True
        return False

    if currency == "USD": 
        if market_cap > 7000000000: 
            return True
        return False
    return False

# def check_open(date): 
#     current_date = datetime.now()
#     current_date_str = current_date.strftime(r"%Y-%m-%d")

#     date_str = date.strftime(r"%Y-%m-%d")
#     if current_date_str == date_str: 
#         return True
#     return False

# Check for an island reversal
def check_island(stock): 
    #get data of this stock
    data = yf.download(stock.info['symbol'], period="1mo", show_errors=False)

    #print(data)

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

                sys.stdout = sys.__stdout__

                print(f"{stock.info['symbol']} ({stock.info['shortName']}): Island from {start_date} to {end_date}")
                webbrowser.open(f"https://uk.finance.yahoo.com/chart/{stock.info['symbol']}")
                
                return True # This is an island
            
        day_count_start += 1
    
    return False # There is no island
        
def main(): 
    with open("stock.txt", "r") as file: 
        symbols = file.readlines()
    
    for symbol in symbols: 
        symbol = symbol.strip()

        try: 
            sys.stdout = open(os.devnull, "w")

            stock = yf.Ticker(symbol)
            # for key in stock.info: 
            #     print(f"{key}: {stock.info[key]}\n")

            if not check_market_cap(stock.info["financialCurrency"], stock.info["marketCap"]): 
                continue

            if not check_island(stock): 
                continue

            # More filters here
        except: 
            pass

if __name__ == "__main__":
    main()