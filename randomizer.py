#!/bin/python2

import datetime
from random import randint, choice


class Game():
    name = "Game"
    filename = "game.rom"
    
    options = {"dummy": "Randomize a thing"}
    
    def __init__(self):
        self.choices = {}
        for option in self.options.keys():
            self.choices[option] = False
        pass # merge parent options
    
    def randomize_dummy(self):
        return True

    def produce(self):
        # First let's make sure the input is right...
        for option, value in self.choices.items():
            if option not in self.options.keys():
                raise ValueError('No such option for the game {}: {}'.format(self.name, option))
        
        # Now let's make us a ROM
        
        original = open(self.filename, 'rb').read()
        filename = datetime.datetime.now().strftime("%Y%M%dT%H%m%S_")+self.filename
        self.rom = open(filename, 'w+b')
        self.rom.write(original)
        
        for option, value in self.choices.items():
            if value:
                params = []
                if not isinstance(value, bool):
                    parms = value
                getattr(self, "randomize_"+option)(*params)
        
        return True

class Telefang(Game):
    name = "Telefang"
    filename = "telefang_random.gbc"
    
    options = {"wild_denjuu": "Randomize wild Denjuu"}
    
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

game = Telefang()
game.choices["wild_denjuu"] = True
rom = game.produce()
