#!/bin/python2
# encoding: utf-8
from __future__ import unicode_literals

from randomizer import *

@randomizer_games.append
class Telefang(Game):
    name = "Telefang Power"
    filename = "telefang_random.gbc"
    identifier = "telefang"
    
    class Form(Form):
        starter_denjuu = BooleanField("Randomize starter Denjuu (Crypto)")
        wild_denjuu = BooleanField("Randomize wild Denjuu")
        scripted_denjuu = BooleanField("Randomize scripted Denjuu")
        tfanger_denjuu = BooleanField("Randomize T-Fanger Denjuu")
        secret_denjuu = BooleanField("Randomize Secret Denjuu")
        item_prices = BooleanField("Randomize item prices")
        
    DENJUU = 175
    
    def random_denjuu(self):
        return randint(0, self.DENJUU)
    
    def opt_wild_denjuu(self):
        self.rom.seek(0x1d56ee)
        for i in range((0x1D5887 - 0x1d56ee)//5):
            for j in range(4):
                denjuu = self.random_denjuu()
                self.rom.write(chr(denjuu))
            self.rom.read(1)

    def opt_scripted_denjuu(self):
        self.rom.seek(0x9cbfa)
        for i in range(135*5):
            denjuu = self.random_denjuu()
            self.rom.write(chr(denjuu))
            self.rom.read(4)
    
    def opt_tfanger_denjuu(self):
        self.rom.seek(0x9cbfa)
        for i in range(135*5):
            denjuu = self.random_denjuu()
            self.rom.write(chr(denjuu))
            self.rom.read(4)
    
    def opt_secret_denjuu(self):
        self.rom.seek(0x13c0d)
        for i in range(14*4):
            denjuu = self.random_denjuu()
            self.rom.write(chr(denjuu))
            self.rom.read(2)
            self.rom.write(chr(random.randint(0, 11)))
        for i in range(13): # origins follow
            self.rom.write(chr(random.randint(0, 21)))
    
    def opt_item_prices(self):
        self.rom.seek(0x4000*0xb+0x2872)
        for i in range(68):
            price = int(triangular(0, 1000, 0))
            self.rom.writeshort(price)
    
    def opt_starter_denjuu(self):
        self.rom.seek(0x4000*0x32 + 0x1624) # crypto
        self.rom.writebyte(self.random_denjuu())
        self.rom.seek(0x4000*0x32 + 0x1629) # crypto's personality
        self.rom.write(chr(random.randint(0, 11)))

