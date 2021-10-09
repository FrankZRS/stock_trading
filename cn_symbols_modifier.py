with open("cn_symbols.txt", "r") as file: 
    cn_symbols = file.read().splitlines()

modified_symbols = []

for symbol in cn_symbols: 
    if symbol.startswith("SZ"): 
        symbol = symbol[2:] + ".SZ"
        
    if symbol.startswith("SH"): 
        symbol = symbol[2:] + ".SS"

    modified_symbols.append(symbol)

with open("cn_symbols.txt", "w") as file: 
    for symbol in modified_symbols: 
        file.write(f"{symbol}\n")