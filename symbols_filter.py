import yfinance as yf
from stock import check_market_cap

symbol_files = ["symbols_gb.txt", "symbols_us.txt"]
for symbol_file in symbol_files: 
    if symbol_file == "symbols_us.txt": 
        with open(symbol_file, "r+") as file1: 
            symbols = file1.read().splitlines()

            for symbol in symbols: 
                try: 
                    stock = yf.Ticker(symbol)

                    market = stock.info['market']

                    if not check_market_cap(stock.info["financialCurrency"], stock.info["marketCap"]): 
                        print(f"Small cap for {symbol}")
                        
                        symbols.remove(symbol)

                        with open("symbols_small_cap.txt", "a") as file2: 
                            file2.write(f"{symbol}\n")

                except Exception as e: 
                    print(f"Exception {e} for {symbol}")
                        
                    symbols.remove(symbol)

                    with open("symbols_info_error.txt", "a") as file3: 
                            file3.write(f"{symbol}\n")

            file1.seek(0)
            for symbol in symbols: 
                    file1.write(f"{symbol}\n")
                    file1.truncate()