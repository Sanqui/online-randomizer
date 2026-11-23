#!/usr/bin/env python3
"""Reduce sprite PNGs to at most 4 colours, in place."""

import sys
from collections import Counter

import png


def reduce_colors(pixels, max_colors=4):
    """Map each colour in `pixels` (a Counter of RGB tuples) to a kept colour."""
    counts = dict(pixels)
    mapping = {c: c for c in counts}

    def cost(a, b):
        d2 = sum((x - y) ** 2 for x, y in zip(a, b))
        na, nb = counts[a], counts[b]
        return d2 * na * nb / (na + nb)

    while len(counts) > max_colors:
        a, b = min(
            ((a, b) for i, a in enumerate(counts) for b in list(counts)[i + 1:]),
            key=lambda pair: cost(*pair),
        )
        keep, drop = (a, b) if counts[a] >= counts[b] else (b, a)
        counts[keep] += counts.pop(drop)
        for c, target in mapping.items():
            if target == drop:
                mapping[c] = keep
    return mapping


def process(path, max_colors=4):
    width, height, rows, _ = png.Reader(filename=path).asRGBA8()
    rows = [bytes(r) for r in rows]
    def rgb(r, i):
        if r[i + 3] == 0:
            return (255, 255, 255)
        return tuple(r[i:i + 3])
    image = [[rgb(r, i) for i in range(0, len(r), 4)] for r in rows]
    mapping = reduce_colors(Counter(c for row in image for c in row), max_colors)
    out = [[v for c in row for v in mapping[c]] for row in image]
    png.Writer(width, height, greyscale=False, bitdepth=8).write(open(path, "wb"), out)


if __name__ == "__main__":
    for path in sys.argv[1:]:
        process(path)
