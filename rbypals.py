pals = {
    "PAL_MEWMON":    [[30, 22, 17],  [16, 14, 19]],
    "PAL_BLUEMON":   [[18, 20, 27],  [11, 15, 23]],
    "PAL_REDMON":    [[31, 20, 10],  [26, 10,  6]],
    "PAL_CYANMON":   [[21, 25, 29],  [14, 19, 25]],
    "PAL_PURPLEMON": [[27, 22, 24],  [21, 15, 23]],
    "PAL_BROWNMON":  [[28, 20, 15],  [21, 14,  9]],
    "PAL_GREENMON":  [[20, 26, 16],  [ 9, 20, 11]],
    "PAL_PINKMON":   [[30, 22, 24],  [28, 15, 21]],
    "PAL_YELLOWMON": [[31, 28, 14],  [26, 20,  0]],
    "PAL_GREYMON":   [[26, 21, 22],  [15, 15, 18]]
}

out = []

for mon in range(1, 722):
    monpal = []
    for i, line in enumerate(open('sprites/{:03}.pal'.format(mon), 'r')):
        if i in (1, 2):
            nums = line.split("RGB ")[1].split(',')
            nums = [int(num.strip()) for num in nums]
            monpal.append(nums)
    distances = {}
    for name, pal in pals.items():
        d = 0
        for j in (0, 1):
            d += (pal[j][0]-monpal[j][0])**2 + (pal[j][1]-monpal[j][1])**2 + (pal[j][2]-monpal[j][2])**2
        distances[name] = d
    name = min(distances, key=distances.get)
    out.append(name)
    #print "{:03} - with distance {}, picking {}".format(mon, distances[name], name)
    #print monpal, monpal in pals.values()

open('data/monpals.txt', 'w').write('\n'.join(out))
