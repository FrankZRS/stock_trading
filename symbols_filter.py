import yfinance as yf
from stock import check_market_cap

with open("symbols_gb.txt", "r+") as file1: 
    gb_symbols = file1.read().splitlines()

    for gb_symbol in gb_symbols: 
        try: 
            stock = yf.Ticker(gb_symbol)

            market = stock.info['market']

            if not check_market_cap(stock.info["financialCurrency"], stock.info["marketCap"]): 
                print(f"Small cap for {gb_symbol}")
                
                gb_symbols.remove(gb_symbol)

                with open("symbols_small_cap.txt", "a") as file2: 
                    file2.write(f"{gb_symbol}\n")

        except Exception as e: 
            print(f"Exception {e} for {gb_symbol}")
                
            gb_symbols.remove(gb_symbol)

            with open("symbols_info_error.txt", "a") as file3: 
                    file3.write(f"{gb_symbol}\n")

    file1.seek(0)
    for gb_symbol in gb_symbols: 
            file1.write(f"{gb_symbol}\n")