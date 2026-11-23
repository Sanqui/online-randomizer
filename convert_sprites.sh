#!/usr/bin/env bash
set -veuo pipefail
rm sprites/ backsprites/ backsprites_/ -rf

mkdir sprites

magick gfx/sprite_sheets/sprites.png -crop 96x96 +repage -scene 1 +adjoin sprites/%03d.png
mogrify -trim -flop -background white -gravity center -extent 56x56 sprites/*
# not `-colors 4`: ImageMagick sometimes drops to 3 colours (see reduce_colors.py)
uv run python reduce_colors.py sprites/*

#convert xymons.png -crop 59x59 +repage +adjoin -crop 56x56+1+1 -scene 650 -colors 4 sprites/%03d.png

cp sprites backsprites -r

mogrify -trim -flop +repage -background white -gravity northeast -crop 32x32-4+0\! -flatten backsprites/*
uv run python reduce_colors.py backsprites/*

mkdir backsprites_
magick gfx/sprite_sheets/backsprites.png -crop 96x96 +repage -scene 1 +adjoin backsprites_/%03d.png
mogrify -trim backsprites_/*

set +v # do lots of identifies and delete non-backsprites

for f in backsprites_/*
do
    if [ '(' ` identify -format "%w" $f ` -gt "28" ')' -o '(' ` identify -format "%h" $f ` -gt "28" ')' ]
    then
        rm $f
    fi
done

set -v

mogrify -trim +repage -background white -gravity south -crop 28x28+0+0\! -gravity northwest -crop 32x32-0-0\! -flatten backsprites_/*
uv run python reduce_colors.py backsprites_/*

cp --update=none backsprites/* backsprites_/

uv run python gfx.py 2bpp sprites/* backsprites/* backsprites_/*
uv run python pic.py compress sprites/*.2bpp backsprites/*.2bpp backsprites_/*.2bpp
uv run python rbypals.py
