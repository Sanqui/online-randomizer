# set -veuo pipefail
set -v
rm sprites/ backsprites/ backsprites_/ -rf

mkdir sprites

wget -O sprites.png http://wyndows.sweb.cz/Pokemon%20Sprites%20in%20Gen%201%20Style%20fixed.png
wget -O backsprites.png http://wyndows.sweb.cz/Gen%201%20Backsprites.png

convert sprites.png -crop 96x96 +repage -scene 1 +adjoin sprites/%03d.png
mogrify -trim -flop -background white -gravity center -extent 56x56 -dither None -colors 4 sprites/*

#convert xymons.png -crop 59x59 +repage +adjoin -crop 56x56+1+1 -scene 650 -colors 4 sprites/%03d.png

cp sprites backsprites -r

mogrify -trim -flop +repage -background white -gravity northeast -crop 32x32-4+0\! -flatten backsprites/*
mogrify -dither None -colors 4 backsprites/*

mkdir backsprites_
convert backsprites.png -crop 96x96 +repage -scene 1 +adjoin backsprites_/%03d.png
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
mogrify -dither None -colors 4 backsprites_/*

cp -n backsprites/* backsprites_/

python2 gfx.py 2bpp sprites/* backsprites/* backsprites_/*
python2 pic.py compress sprites/*.2bpp backsprites/*.2bpp backsprites_/*.2bpp
python2 rbypals.py
