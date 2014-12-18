#!/bin/python2
# encoding: utf-8

from __future__ import unicode_literals

from collections import OrderedDict
from bidict import bidict

import os
import datetime
import struct
import random
import subprocess
from random import randint, choice, sample, triangular, shuffle # choice we redefine

def choice(x): return random.choice(tuple(x))

import yaml

from wtforms import Form, BooleanField, TextField, TextAreaField, PasswordField, RadioField, SelectField, SelectMultipleField, BooleanField, HiddenField, SubmitField, Field, validators, ValidationError, widgets

def dechoices(c):
    return [x.split(':') for x in c.split(';')]

class Heading(Field):
    def __call__(self, **kwargs):
        return "<h3 class='ui header'>"+self.label.text+"</h3>"

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    
    Shamelessly stolen from WTForms FAQ.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

def symfile(filename):
    symbols = {}
    for line in open(filename).readlines():
        if line.startswith(';'): continue
        if not line.strip(): continue
        addr, label = line.strip().split(' ')
        bank, offset = addr.split(':')
        bank, offset = int(bank, 16), int(offset, 16)
        if offset < 0x8000:
            addr = bank*0x4000 + offset % 0x4000
            symbols[label] = addr
    return symbols

class ROM(file):
    def readbyte(self):
        return ord(self.read(1))
    def readshort(self):
        return struct.unpack(b'<H', self.read(2))[0]
    
    def writebyte(self, byte):
        self.write(struct.pack(b'<B', byte))
    def writeshort(self, short):
        self.write(struct.pack(b'<H', short))

def symfile(filename):
    symbols = {}
    for line in open(filename).readlines():
        if line.startswith(';'): continue
        if not line.strip(): continue
        addr, label = line.strip().split(' ')
        bank, offset = addr.split(':')
        bank, offset = int(bank, 16), int(offset, 16)
        if offset < 0x8000:
            addr = bank*0x4000 + offset % 0x4000
            symbols[label] = addr
    return symbols

class ROM(file):
    def readbyte(self):
        return ord(self.read(1))
    def readshort(self):
        return struct.unpack(b'<H', self.read(2))[0]
    
    def writebyte(self, byte):
        self.write(struct.pack(b'<B', byte))
    def writeshort(self, short):
        self.write(struct.pack(b'<H', short))

class Game():
    name = "Game"
    filename = "game.rom"
    identifier = "game"
    
    #options = {"dummy": "Randomize a thing"}
    presets = {}
    
    form_expanded_by = {}
    # TODO form
    
    CHARS = {}
    
    def __init__(self):
        self.debug = False
        self.choices = {}
        for field in self.Form():
            self.choices[field.id] = None
        pass
    
    def opt_dummy(self):
        return True
    
    def write_string(self, string, length=None):
        # TODO no length
        for i in range(length if length else len(string)+1):
            if i < len(string):
                self.rom.write(chr(self.CHARS.get(string[i], 230))) # 230 = ?
            else:
                self.rom.write(chr(self.CHARS['@']))
    
    def finalize(self):
        pass
    
    def produce(self, filename, debug=False):
        # First let's make sure the input is right...
        #for option, value in self.choices.items():
        #    if option not hasattr(self, "opt_"+option):
        #        raise ValueError('No such option for the game {}: {}'.format(self.name, option))
        
        # Now let's make us a ROM
        self.debug = debug
        original = open('roms/'+self.filename, 'rb').read()
        if filename:
            filename = filename.replace('/', '_').replace('\0', '').replace('?', '_').replace('#', '_')
            filename = "static/roms/"+filename
            while os.path.isfile(filename+'.gbc'):
                filename += '_'
            if not filename.endswith('.gbc'):
                filename += '.gbc'
        else:
            filename = "static/roms/"+datetime.datetime.now().strftime("%Y%m%dT%H%M%S_")+self.filename
            while os.path.isfile(filename):
                filename = filename.split('.')
                filename[-2] += '_'
                filename = filename.join('.')
        self.rom = ROM(filename, 'w+b')
        self.rom.write(original)
        
        print("Producing rom: {} with options: {}".format(filename, self.choices))
        
        methods = []
        for option, value in self.choices.items():
            if value and hasattr(self, "opt_"+option):
                params = []
                if value != True:
                    params = [value]
                #print option, value, params
                #print "Randomizing: "+option
                methods.append((option, getattr(self, "opt_"+option), params))
        
        methods.sort(key=lambda x: x[1].layer if hasattr(x[1], 'layer') else 0)
        for option, method, params in methods:
            #print "Randomizing: "+option+" with "+str(params)
            method(*params)
        
        self.finalize()
        self.rom.close()
        
        return filename


randomizer_games = []
import games.pokered
import games.poketcg
import games.telefang
# XXX



'''game = Telefang()
game.choices["wild_denjuu"] = True
game.choices["scripted_denjuu"] = True
game.choices["tfanger_denjuu"] = True
game.choices["item_prices"] = True
rom = game.produce()'''
if __name__ == "__main__":
    game = randomizer_games[0]( ) #PokemonRed()
    '''game.choices["starter_pokemon"] = True
    game.choices["trainer_pokemon"] = True
    game.choices["wild_pokemon"] = True'''
    game.choices["game_pokemon"] = True
    '''game.choices["update_types"] = True
    game.choices["tms"] = True
    game.choices["cries"] = True'''
    game.choices["special_conversion"] = "average"
    #game.choices["instant_text"] = True
    #game.choices["ow_sprites"] = True
    filename = game.produce(None)
