#!/bin/python2
# encoding: utf-8

from __future__ import unicode_literals

from collections import OrderedDict

import datetime
import struct
import random
from random import randint, choice, sample, triangular # choice we redefine

def choice(x): return random.choice(tuple(x))

import yaml

from wtforms import Form, BooleanField, TextField, TextAreaField, PasswordField, RadioField, SelectField, SelectMultipleField, BooleanField, HiddenField, SubmitField, Field, validators, ValidationError, widgets

class Heading(Field):
    def __call__(self, **kwargs):
        return "<h3>"+self.label.text+"</h3>"

minidex = yaml.load(open('data/minidex.yaml'))
type_names = "- normal fighting flying poison ground rock bug ghost steel fire water grass electric psychic ice dragon dark fairy".split()
type_efficacy = []
for row in open('data/type_efficacy.csv').readlines():
    type0, type1, factor = [int(x) for x in row.split(',')]
    type_efficacy.append((type_names[type0], type_names[type1], factor))


menu_icons = ['mon ball helix fairy bird water bug grass snake quadruped -'.split().index(l.strip()) for l in open('data/menu_icons.txt')]

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
    def writebyte(self, byte):
        self.write(struct.pack(b'<B', byte))
    def writeshort(self, short):
        self.write(struct.pack(b'<H', short))

games = []

class Game():
    name = "Game"
    filename = "game.rom"
    identifier = "game"
    
    #options = {"dummy": "Randomize a thing"}
    
    # TODO form
    
    CHARS = {}
    
    def __init__(self):
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
    
    def produce(self):
        # First let's make sure the input is right...
        #for option, value in self.choices.items():
        #    if option not hasattr(self, "opt_"+option):
        #        raise ValueError('No such option for the game {}: {}'.format(self.name, option))
        
        # Now let's make us a ROM
        
        original = open('roms/'+self.filename, 'rb').read()
        filename = "static/roms/"+datetime.datetime.now().strftime("%Y%m%dT%H%M%S_")+self.filename
        self.rom = ROM(filename, 'w+b')
        self.rom.write(original)
        
        for option, value in self.choices.items():
            if value and hasattr(self, "opt_"+option):
                params = []
                if not isinstance(value, bool):
                    parms = value
                print "Randomizing: "+option
                getattr(self, "opt_"+option)(*params)
        
        self.finalize()
        self.rom.close()
        
        return filename

@games.append
class PokemonRed(Game):
    name = "Pokémon Red"
    filename = "pokered.gb" # randomizer rom with some different offsets
    identifier = "pokered"
    symbols = symfile("pokered.sym")
    
    '''options = {"starter_pokemon": "Randomize starter Pokémon",
    "trainer_pokemon": "Randomize trainer Pokémon",
    "wild_pokemon": "Randomize wild Pokémon",
    "game_pokemon": "Randomize Pokémon in the game",
    "cries": "Randomize Pokémon cries",
    "tms": "Randomize the moves TMs teach",
    "update_types": "Update types to X/Y"
    #"ow_sprites": "Randomize overworld sprites",
        }'''
    
    class Form(Form):
        h_randomize = Heading("Randomizations")
        
        starter_pokemon = SelectField('Starter Pokémon', choices=[x.split(':') for x in ":Keep,randomize:Random,basics:Random basics,three-basic:Random three stage basics,single:Single random (yellow style)".split(',')], default="")
        trainer_pokemon = BooleanField("Randomize trainer Pokémon")
        wild_pokemon = BooleanField("Randomize wild Pokémon")
        game_pokemon = BooleanField("Randomize Pokémon from all gens in")
        special_conversion = SelectField('Special stat conversion', choices=OrderedDict(average="Average", spa="Sp. Attack", spd="Sp. Defense", higher="Higher stat", random="Random stat").items(), default="average")
        move_rules = SelectField('Fair random move rules', choices=[x.split(':') for x in ":All moves;no-hms:No HMs;no-broken:No Dragon Rage, Spore;no-hms-broken:No HMs, Dragon Rage, Spore".split(';')], default="no-hms-broken")
        cries = BooleanField("Randomize Pokémon cries")
        tms = BooleanField("Randomize the moves TMs teach")
        field_items = SelectField('Field items', choices=[('','-'),('shuffle','Shuffle'),('randomize','Randomize')], default="")
    
        h_tweaks = Heading("Tweaks")
        update_types = BooleanField("Update types to X/Y")
        instant_text = BooleanField("Instant text speed")
    
    
    CHARS = {' ': 127,
 '!': 231,
 '#': 84,
 '&': 233,
 "'": 224,
 "'d": 208,
 "'l": 209,
 "'m": 210,
 "'r": 211,
 "'s": 212,
 "'t": 213,
 "'v": 214,
 '(': 154,
 ')': 155,
 ',': 244,
 '-': 227,
 '.': 232,
 '/': 243,
 '0': 246,
 '1': 247,
 '2': 248,
 '3': 249,
 '4': 250,
 '5': 251,
 '6': 252,
 '7': 253,
 '8': 254,
 '9': 255,
 ':': 156,
 ';': 157,
 '?': 230,
 '@': 80,
 'A': 128,
 'B': 129,
 'C': 130,
 'D': 131,
 'E': 132,
 'F': 133,
 'G': 134,
 'H': 135,
 'I': 136,
 'J': 137,
 'K': 138,
 'L': 139,
 'M': 140,
 'N': 141,
 'O': 142,
 'P': 143,
 'Q': 144,
 'R': 145,
 'S': 146,
 'T': 147,
 'U': 148,
 'V': 149,
 'W': 150,
 'X': 151,
 'Y': 152,
 'Z': 153,
 '[': 158,
 ']': 159,
 'a': 160,
 'b': 161,
 'c': 162,
 'd': 163,
 'e': 164,
 'f': 165,
 'g': 166,
 'h': 167,
 'i': 168,
 'j': 169,
 'k': 170,
 'l': 171,
 'm': 172,
 'n': 173,
 'o': 174,
 'p': 175,
 'q': 176,
 'r': 177,
 's': 178,
 't': 179,
 'u': 180,
 'v': 181,
 'w': 182,
 'x': 183,
 'y': 184,
 'z': 185,
 '¥': 240,
 '×': 241,
 '…': 117,
 '№': 116,
 '→': 235,
 '─': 122,
 '│': 124,
 '┌': 121,
 '┐': 123,
 '└': 125,
 '┘': 126,
 '▶': 237,
 '▷': 236,
 '▼': 238,
 '♀': 245,
 '♂': 239,
 '<': 0xe1,
 '>': 0xe2,}
    
    POKEMON = [0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f, 0x30, 0x31, 0x33, 0x35, 0x36, 0x37, 0x39, 0x3a, 0x3b, 0x3c, 0x40, 0x41, 0x42, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e, 0x52, 0x53, 0x54, 0x55, 0x58, 0x59, 0x5a, 0x5b, 0x5c, 0x5d, 0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x6b, 0x6c, 0x6d, 0x6e, 0x6f, 0x70, 0x71, 0x72, 0x74, 0x75, 0x76, 0x77, 0x78, 0x7b, 0x7c, 0x7d, 0x7e, 0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x88, 0x8a, 0x8b, 0x8d, 0x8e, 0x8f, 0x90, 0x91, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0x9b, 0x9d, 0x9e, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xab, 0xad, 0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb9, 0xba, 0xbb, 0xbc, 0xbd, 0xbe]
    
    POKEMON_MAPPINGS = [None, 112, 115, 32, 35, 21, 100, 34, 80, 2, 103, 108, 102, 88, 94, 29, 31, 104, 111, 131, 59, 151, 130, 90, 72, 92, 123, 120, 9, 127, 114, None, None, 58, 95, 22, 16, 79, 64, 75, 113, 67, 122, 106, 107, 24, 47, 54, 96, 76, None, 126, None, 125, 82, 109, None, 56, 86, 50, 128, None, None, None, 83, 48, 149, None, None, None, 84, 60, 124, 146, 144, 145, 132, 52, 98, None, None, None, 37, 38, 25, 26, None, None, 147, 148, 140, 141, 116, 117, None, None, 27, 28, 138, 139, 39, 40, 133, 136, 135, 134, 66, 41, 23, 46, 61, 62, 13, 14, 15, None, 85, 57, 51, 49, 87, None, None, 10, 11, 12, 68, None, 55, 97, 42, 150, 143, 129, None, None, 89, None, 99, 91, None, 101, 36, 110, 53, 105, None, 93, 63, 65, 17, 18, 121, 1, 3, 73, None, 118, 119, None, None, None, None, 77, 78, 19, 20, 33, 30, 74, 137, 142, None, 81, None, None, 4, 7, 5, 8, 6, None, None, None, None, 43, 44, 45, 69, 70, 71]
    
    STARTER_OFFESTS = [[0x1CC84, 0x1D10E, 0x1D126, 0x39CF8, 0x50FB3, 0x510DD],
[0x1CC88, 0x1CDC8, 0x1D11F, 0x1D104, 0x19591, 0x50FAF, 0x510D9, 0x51CAF, 0x6060E, 0x61450, 0x75F9E],
[0x1CDD0, 0x1D130, 0x1D115, 0x19599, 0x39CF2, 0x50FB1, 0x510DB, 0x51CB7, 0x60616, 0x61458, 0x75FA6]]

    EVOLUTION_METHODS = {'level-up': 1, 'use-item': 2, 'trade': 3}

    TYPES = {'normal': 0x00, 'fighting': 0x01, 'flying': 0x02, 'poison': 0x03, 'ground': 0x04,
             'rock': 0x05, 'bug': 0x06, 'ghost': 0x07, 'ghost': 0x08,
             'fire': 0x14, 'water': 0x15, 'grass': 0x16, 'electric': 0x17, 'psychic': 0x18,
             'ice': 0x19, 'dragon': 0x1a,
             'dark': 0x00, 'steel': 0x00, 'fairy': 0x00}
     
    ITEMS = {'moon-stone': 0x0a, 'fire-stone': 0x20, 'thunder-stone': 0x21,
             'water-stone': 0x22, 'leaf-stone': 0x2f} # TODO
             
    MAXMOVE = 0xa4 # substitute
    FAIR_MOVES = set(range(1, MAXMOVE+1)) - {57, 70, 19, 15, 148, 144}
    
    def random_pokemon(self):
        return choice(self.POKEMON)
    
    def opt_starter_pokemon(self):
        starters = [self.random_pokemon() for i in range(3)]
        for i, starter in enumerate(starters):
            for offset in self.STARTER_OFFESTS[i]:
                self.rom.seek(offset)
                self.rom.writebyte(starter)
    
    def opt_trainer_pokemon(self):
        rom = self.rom
        rom.seek(self.symbols["YoungsterData"])
        while rom.tell() < 0x3a522 + 12:
            first_byte = ord(rom.read(1))
            if first_byte == 0xff:
                while ord(rom.read(1)) != 0:
                    rom.writebyte(self.random_pokemon())
            else:
                while ord(rom.read(1)) != 0:
                    rom.seek(rom.tell()-1)
                    rom.writebyte(self.random_pokemon())
                
    def opt_wild_pokemon(self):
        rom = self.rom
        rom.seek(self.symbols["Route1Mons"])
        while rom.tell() < 0xd5b1+22:
            rate = ord(rom.read(1)) # rate
            if rate != 0:
                for i in range(10):
                    rom.read(1)
                    rom.write(chr(self.random_pokemon()))
        
    def opt_tms(self):
        rom = self.rom
        rom.seek(self.symbols["TechnicalMachines"])
        tms = sample(self.FAIR_MOVES, 50)
        for move in tms:
            rom.write(chr(move))
        
    #def opt_ow_sprites(self):
    #    rom = self.rom
    #    rom.seek(0x17ab9) # sprite sets
    #    for i in range(0xa):
    #        for i in range(8):
    #            rom.write(chr(randint(1, 0x3b)))
    #        rom.read(2)
    
    def opt_cries(self):
        self.rom.seek(self.symbols["CryData"])
        for i in range(190):
            self.rom.write(chr(randint(0, 0x25)))
            self.rom.write(chr(randint(0, 0xff)))
            self.rom.write(chr(randint(0, 0xa0))) # could be ff
    
    def opt_game_pokemon(self):
        types = self.TYPES
        if self.choices['update_types']: types.update({'dark': 0x09, 'steel': 0x0a, 'fairy': 0x0b})
        rom = self.rom
        dex = []
        dex_families = []
        while len(dex) < 150:
            randfamily = choice(minidex['evolution_chains'])
            if randfamily[0] >= 719: continue # Diancie, no sprites
            if randfamily not in dex_families and len(dex)+len(randfamily) <= 150:
                dex += randfamily
                dex_families.append(randfamily)
        
        print 'Picked {} mons for dex'.format(len(dex))
        
        # sprites
        #self.patch_sprite_loading_routine() # no need to do that, our hack will use
                                             # the bank if it's present, otherwise default behavior
        pokemon_sprite_addresses = []
        banki = 0x2d # 2D: first new sprite bank
        bank = b""
        for num in dex:
            addresses = []
            addresses.append((banki, len(bank)))
            sprites = b""
            sprites += open('sprites/{:03}.pic'.format(num)).read()
            addresses.append((banki, len(bank)+len(sprites)))
            sprites += open('backsprites/{:03}.pic'.format(num)).read()
            if len(bank + sprites) < 0x4000:
                bank += sprites
                pokemon_sprite_addresses.append(addresses)
            else:
                rom.seek(banki*0x4000)
                rom.write(bank)
                banki += 1
                bank = b""
                # derp copypasta
                addresses = []
                addresses.append((banki, len(bank)))
                sprites = b""
                sprites += open('sprites/{:03}.pic'.format(num)).read()
                addresses.append((banki, len(bank)+len(sprites)))
                sprites += open('backsprites/{:03}.pic'.format(num)).read()
                
                bank += sprites
                pokemon_sprite_addresses.append(addresses)
        
        
        rom.seek(banki*0x4000)
        rom.write(bank)
        print "Wrote sprites (last bank: {})".format(hex(banki))
        
        # base stats
        self.rom.seek(self.symbols["BulbasaurBaseStats"]) # BulbasaurBaseStats
        for i, mon in enumerate(dex):
            data = minidex['pokemon'][mon]
            rom.read(1)
            rom.write(chr(data['stats'][0]))
            rom.write(chr(data['stats'][1]))
            rom.write(chr(data['stats'][2]))
            rom.write(chr(data['stats'][5]))
            spa, spd = data['stats'][3], data['stats'][4]
            special = {
                'average': (spa + spd) // 2,
                'spa': spa,
                'spd': spd,
                'higher': max(spa, spd),
                'random': choice((spa, spd))
            }[self.choices['special_conversion'] or 'average']
            rom.write(chr(special)) # special
            rom.write(chr(types[data['type0']]))
            rom.write(chr(types[data['type1']] if data['type1'] else types[data['type0']]))
            rom.write(chr(data['catch_rate']))
            rom.write(chr(min(data['exp_yield'], 255)))
            rom.write(chr(0x77)) # sprite dimensions
            rom.write(struct.pack(b"<H", pokemon_sprite_addresses[i][0][1] + 0x4000))
            rom.write(struct.pack(b"<H", pokemon_sprite_addresses[i][1][1] + 0x4000))
            
            moves = [0, 0, 0, 0]
            num_moves = sum([level == 1 for level in data['moveset']])
            for movei in range(min(num_moves, 4)):
                move = choice(self.FAIR_MOVES)
                while move in moves:
                    move = choice(self.FAIR_MOVES)
                moves[movei] = move
            assert len(moves) == 4
            for move in moves:
                rom.write(chr(move))
            
            rom.write(chr({1:5, 2:0, 3:4, 4:3, 5:3, 6:5}[data['growth_rate']]))
            """
1	slow
2	medium
3	fast
4	medium-slow
5	slow-then-very-fast
6	fast-then-very-slow"""
            """
GrowthRateTable: ; 5901d (16:501d)
	db $11,$00,$00,$00 ; medium fast      n^3
	db $34,$0A,$00,$1E ; (unused?)    3/4 n^3 + 10 n^2         - 30
	db $34,$14,$00,$46 ; (unused?)    3/4 n^3 + 20 n^2         - 70
	db $65,$8F,$64,$8C ; medium slow: 6/5 n^3 - 15 n^2 + 100 n - 140
	db $45,$00,$00,$00 ; fast:        4/5 n^3
	db $54,$00,$00,$00 ; slow:        5/4 n^3"""
            
            for x in range(7): # TMHM
                rom.write(chr(randint(0, 255)))
            
            rom.write(chr(pokemon_sprite_addresses[i][0][0]))
        
        # evos moves
        evo_move_pointers = []
        self.rom.seek(self.symbols['Mon112_EvosMoves']) # First mon's EvosMoves in the modified rom
        # there is about $200 free bytes usually, we can hopefully fit in that
        for i in range(1, 191):
            evo_move_pointers.append(rom.tell())
            dexnum = self.POKEMON_MAPPINGS[i]
            if dexnum and dexnum != 151:
                num = dex[dexnum - 1]
                # evolutions
                for evolution in minidex['pokemon'][num]['evolutions']:
                    trigger = {'shed': 'level-up'}.get(evolution['trigger'], evolution['trigger'])
                    rom.write(chr(self.EVOLUTION_METHODS[trigger]))
                    if trigger == 'level-up':
                        rom.write(chr(evolution['minimum_level'] if evolution['minimum_level'] else 30))
                    elif trigger == 'use-item':
                        rom.write(chr(self.ITEMS.get(evolution['trigger_item'], self.ITEMS['moon-stone'])))
                    rom.writebyte(self.POKEMON_MAPPINGS.index(1+dex.index(evolution['evolved_species'])))
                rom.writebyte(0)
                # moves
                for level in minidex['pokemon'][num]['moveset']:
                    if level != 0 and randint(0, 1):
                        rom.write(chr(level))
                        rom.write(chr(choice(self.FAIR_MOVES)))
        assert rom.tell() < 0x3c000
        
        rom.seek(self.symbols["EvosMovesPointerTable"])
        for evo_move_pointer in evo_move_pointers:
            rom.write(struct.pack(b"<H", evo_move_pointer % 0x4000 + 0x4000))
        
        self.rom.seek(self.symbols["MonsterNames"]) # MonsterNames
        
        for i in range(1, 191):
            dexnum = self.POKEMON_MAPPINGS[i]
            if dexnum and dexnum != 151:
                num = dex[dexnum - 1]
                self.write_string(minidex['pokemon'][num]['name'].upper(), 10)
            else:
                self.write_string("MEW", 10)
        
        # menu icons
        self.rom.seek(self.symbols["MonPartyData"]) # what a bad name
        for i in range(150/2):
            self.rom.writebyte( (menu_icons[dex[i*2]] << 4) | menu_icons[dex[i*2+1]])
        
        # We don't have palettes yet, so at least don't show wrong ones.
        self.rom.seek(self.symbols["MonsterPalettes"])
        for i in range(152):
            self.rom.writebyte(0x19)
        
    def opt_update_types(self):
        types = self.TYPES
        types.update({'dark': 0x09, 'steel': 0x0a, 'fairy': 0x0b})
        name_offsets = []
        self.rom.seek(self.symbols["Type00Name"])
        for i in range(0x1b):
            name_offsets.append(self.rom.tell())
            type_ = None
            for tname, ti in types.items():
                #print tname, ti, i, ti==i, type_
                if ti == i:
                    type_ = tname
                    break
            if type_:
                self.write_string(tname.upper())
        self.rom.seek(self.symbols["TypeNamePointers"])
        for ptr in name_offsets:
            self.rom.write(struct.pack(b"<H", ptr % 0x4000 + 0x4000))
        self.rom.seek(self.symbols["TypeEffects"])
        for type0, type1, factor in type_efficacy:
            if factor != 100:
                self.rom.write(chr(types[type0]))
                self.rom.write(chr(types[type1]))
                self.rom.write(chr({0:0x00, 50: 0x05, 200: 0x20}[factor]))
        self.rom.writebyte(0xff)
        
    def opt_instant_text(self):
        self.rom.seek(0x0001)
        self.rom.writebyte(0x01) # bit 0 but i have no other stuff yet
                
    def finalize(self):
        self.rom.seek(self.symbols['TitleScreenText'])
        text = ""
        text += "{:20}".format("Randomizer options:")
        option_strings = []
        for choice, value in self.choices.items():
            ot = ""
            if value:
                ot += choice
                if value != True:
                    ot += ": "+value
                option_strings.append(ot)
        text += ", ".join(option_strings) + "@"
        text = text.replace('_', '-').replace('-pokemon','<>')
        self.write_string(text)
    

@games.append
class PokemonTCG(Game):
    name = "Pokémon TCG"
    filename = "poketcg.gb" # randomizer rom with some different offsets
    identifier = "poketcg"
    #symbols = symfile("pokered.sym")
    
    class Form(Form):
        remove_tutorial = BooleanField("Remove tutorial")

    def opt_remove_tutorial(self):
        pass
    
@games.append
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


'''game = Telefang()
game.choices["wild_denjuu"] = True
game.choices["scripted_denjuu"] = True
game.choices["tfanger_denjuu"] = True
game.choices["item_prices"] = True
rom = game.produce()'''
if __name__ == "__main__":
    game = games[0]( ) #PokemonRed()
    game.choices["starter_pokemon"] = True
    game.choices["trainer_pokemon"] = True
    game.choices["wild_pokemon"] = True
    game.choices["game_pokemon"] = True
    game.choices["update_types"] = True
    game.choices["tms"] = True
    game.choices["cries"] = True
    game.choices["special_conversion"] = "average"
    #game.choices["instant_text"] = True
    #game.choices["ow_sprites"] = True
    filename = game.produce()
