#!/bin/python2
# encoding: utf-8
from __future__ import unicode_literals

from randomizer import *

# TODO make good use of https://github.com/dannye/tcg !
@randomizer_games.append
class PokemonTCG(Game):
    name = "Pokémon TCG"
    filename = "poketcg.gbc"
    identifier = "poketcg"
    #symbols = symfile("pokered.sym")
    
    class Form(Form):
        shuffle_decks = BooleanField("Shuffle decks")
        remove_tutorial = BooleanField("Remove tutorial")


    def opt_shuffle_decks(self):
        self.rom.seek(0x30000)
        decks = []
        while True:
            deck = self.rom.readshort()
            if deck == 0: break
            decks.append(deck)
        shuffle(decks)
        
        self.rom.seek(0x30000)
        for deck in decks:
            self.rom.writeshort(deck)

    def opt_remove_tutorial(self):
        self.rom.seek(0xd76f)
        self.rom.write(b'\x43' * (0xd854 - 0xd76f))
