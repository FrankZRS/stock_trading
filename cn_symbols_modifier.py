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

# Old cn_symbols loader
# if market == "cn" or market == "all": 
#         SS_A = 600000 # 沪A
#         SZ_A = 0      # 深A
#         CYB = 300000  # 创业板
#         ZXB = 2000    # 中小板
#         SS_B = 900000 # 沪B
#         SZ_B = 200000 # 深B

#         # 沪A
#         while SS_A <= 601999: 
#             symbols.append(f"{SS_A:06d}.SS")
#             SS_A += 1

#         SS_A = 603000
#         while SS_A <= 603999: 
#             symbols.append(f"{SS_A:06d}.SS")
#             SS_A += 1

#         SS_A = 605000
#         while SS_A <= 605999: 
#             symbols.append(f"{SS_A:06d}.SS")
#             SS_A += 1
        
#         # 深A
#         while SZ_A <= 999: 
#             symbols.append(f"{SZ_A:06d}.SZ")
#             SZ_A += 1

#         symbols.append("001696")
#         symbols.append("001896")
#         symbols.append("001979")

#         # 创业板
#         while CYB <= 301200: 
#             symbols.append(f"{CYB:06d}.SZ")
#             CYB += 1

#         # 中小板
#         while ZXB <= 2999: 
#             symbols.append(f"{ZXB:06d}.SZ")
#             ZXB += 1