#!/bin/python2
# encoding: utf-8


import datetime
import struct
from random import randint, choice, triangular

class ROM(file):
    def writebyte(self, byte):
        self.write(struct.pack('<B', byte))
    def writeshort(self, short):
        self.write(struct.pack('<H', short))


class Game():
    name = "Game"
    filename = "game.rom"
    
    options = {"dummy": "Randomize a thing"}
    
    def __init__(self):
        self.choices = {}
        for option in self.options.keys():
            self.choices[option] = False
        pass # TODO merge parent options
    
    def randomize_dummy(self):
        return True

    def produce(self):
        # First let's make sure the input is right...
        for option, value in self.choices.items():
            if option not in self.options.keys():
                raise ValueError('No such option for the game {}: {}'.format(self.name, option))
        
        # Now let's make us a ROM
        
        original = open(self.filename, 'rb').read()
        filename = datetime.datetime.now().strftime("%Y%m%dT%H%M%S_")+self.filename
        self.rom = ROM(filename, 'w+b')
        self.rom.write(original)
        
        for option, value in self.choices.items():
            if value:
                params = []
                if not isinstance(value, bool):
                    parms = value
                getattr(self, "randomize_"+option)(*params)
        
        return self.rom

class PokemonRed(Game):
    name = "Pokémon Red"
    filename = "pokered.gb"
    
    options = {"starter_pokemon": "Randomize wild Pokémon",
        }
    
    POKEMON = [0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f, 0x30, 0x31, 0x33, 0x35, 0x36, 0x37, 0x39, 0x3a, 0x3b, 0x3c, 0x40, 0x41, 0x42, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e, 0x52, 0x53, 0x54, 0x55, 0x58, 0x59, 0x5a, 0x5b, 0x5c, 0x5d, 0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x6b, 0x6c, 0x6d, 0x6e, 0x6f, 0x70, 0x71, 0x72, 0x74, 0x75, 0x76, 0x77, 0x78, 0x7b, 0x7c, 0x7d, 0x7e, 0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x88, 0x8a, 0x8b, 0x8d, 0x8e, 0x8f, 0x90, 0x91, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0x9b, 0x9d, 0x9e, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xab, 0xad, 0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb9, 0xba, 0xbb, 0xbc, 0xbd, 0xbe]
    
    STARTER_OFFESTS = [[0x1CC84, 0x1D10E, 0x1D126, 0x39CF8, 0x50FB3, 0x510DD],
[0x1CC88, 0x1CDC8, 0x1D11F, 0x1D104, 0x19591, 0x50FAF, 0x510D9, 0x51CAF, 0x6060E, 0x61450, 0x75F9E],
[0x1CDD0, 0x1D130, 0x1D115, 0x19599, 0x39CF2, 0x50FB1, 0x510DB, 0x51CB7, 0x60616, 0x61458, 0x75FA6]]
    
    def random_pokemon(self):
        return choice(self.POKEMON)
    
    def randomize_starter_pokemon(self):
        starters = [self.random_pokemon() for i in range(3)]
        for i, starter in enumerate(starters):
            for offset in self.STARTER_OFFESTS[i]:
                self.rom.seek(offset)
                self.rom.writebyte(starter)
    

class Telefang(Game):
    name = "Telefang"
    filename = "telefang_random.gbc"
    
    options = {"wild_denjuu": "Randomize wild Denjuu",
        "scripted_denjuu": "Randomize scripted Denjuu",
        "tfanger_denjuu": "Randomize T-Fanger Denjuu",
        "secret_denjuu": "Randomize Secret Denjuu",
        "item_prices": "Randomize item prices"}
    
    DENJUU = 175
    
    def random_denjuu(self):
        return randint(0, self.DENJUU)
    
    def randomize_wild_denjuu(self):
        self.rom.seek(0x1d56ee)
        for i in range((0x1D5887 - 0x1d56ee)//5):
            for j in range(4):
                denjuu = self.random_denjuu()
                self.rom.write(chr(denjuu))
            self.rom.read(1)

    def randomize_scripted_denjuu(self):
        self.rom.seek(0x9cbfa)
        for i in range(135*5):
            denjuu = self.random_denjuu()
            self.rom.write(chr(denjuu))
            self.rom.read(4)
    
    def randomize_tfanger_denjuu(self):
        self.rom.seek(0x9cbfa)
        for i in range(135*5):
            denjuu = self.random_denjuu()
            self.rom.write(chr(denjuu))
            self.rom.read(4)
    
    def randomize_secret_denjuu(self):
        self.rom.seek(0x13c0d)
        for i in range(14*4):
            denjuu = self.random_denjuu()
            self.rom.write(chr(denjuu))
            self.rom.read(2)
            self.rom.write(chr(random.randint(0, 11)))
        for i in range(13): # origins follow
            self.rom.write(chr(random.randint(0, 21)))
    
    def randomize_item_prices(self):
        self.rom.seek(0x4000*0xb+0x2872)
        for i in range(68):
            price = int(triangular(0, 1000, 0))
            self.rom.writeshort(price)

'''game = Telefang()
game.choices["wild_denjuu"] = True
game.choices["scripted_denjuu"] = True
game.choices["tfanger_denjuu"] = True
game.choices["item_prices"] = True
rom = game.produce()'''

game = PokemonRed()
game.choices["starter_pokemon"] = True
rom = game.produce()
