set -v
rm sprites/ backsprites/ -r

mkdir sprites

wget -O sprites.png http://wyndows.sweb.cz/Pokemon%20Sprites%20in%20Gen%201%20Style%20fixed.png

convert sprites.png -crop 96x96 +repage -scene 1 +adjoin sprites/%03d.png
mogrify -trim -flop -background white -gravity center -extent 56x56 -dither None -colors 4 sprites/*

#convert xymons.png -crop 59x59 +repage +adjoin -crop 56x56+1+1 -scene 650 -colors 4 sprites/%03d.png

cp sprites backsprites -r

mogrify -trim -flop +repage -background white -gravity northeast -crop 32x32-4+0\! -flatten backsprites/*
mogrify -dither None -colors 4 backsprites/*

python2 gfx.py 2bpp sprites/* backsprites/*
python2 pic.py compress sprites/*.2bpp backsprites/*.2bpp
python2 rbypals.py
