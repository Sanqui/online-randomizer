from randomizer import symfile

symbols = symfile("roms/pokered_original.sym")

FIND = [0x1CC84, 0x1D10E, 0x1D126, 0x39CF8, 0x50FB3, 0x510DD,
0x1CC88, 0x1CDC8, 0x1D11F, 0x1D104, 0x19591, 0x50FAF, 0x510D9, 0x51CAF, 0x6060E, 0x61450, 0x75F9E,
0x1CDD0, 0x1D130, 0x1D115, 0x19599, 0x39CF2, 0x50FB1, 0x510DB, 0x51CB7, 0x60616, 0x61458, 0x75FA6]


symtext = []

for offset in FIND:
    closestsym = None
    closest = 0
    for symbol, symbol_offset in symbols.iteritems():
        if symbol_offset > closest and symbol_offset <= offset:
            closest = symbol_offset
            closestsym = symbol
    symtext.append("self.symbols['{}'] + 0x{:x}".format(closestsym, offset-closest))

print "["+", ".join(symtext)+"]"



