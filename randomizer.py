#!/bin/python2
# encoding: utf-8

from __future__ import unicode_literals

from collections import OrderedDict

import os
import datetime
import struct
import random
from random import randint, choice, sample, triangular, shuffle # choice we redefine

def choice(x): return random.choice(tuple(x))

import yaml

from wtforms import Form, BooleanField, TextField, TextAreaField, PasswordField, RadioField, SelectField, SelectMultipleField, BooleanField, HiddenField, SubmitField, Field, validators, ValidationError, widgets

def dechoices(c):
    return [x.split(':') for x in c.split(';')]

class Heading(Field):
    def __call__(self, **kwargs):
        return "<h3 class='ui header'>"+self.label.text+"</h3>"

minidex = yaml.load(open('data/minidex.yaml'))
type_names = "- normal fighting flying poison ground rock bug ghost steel fire water grass electric psychic ice dragon dark fairy".split()
type_efficacy = []
for row in open('data/type_efficacy.csv').readlines():
    type0, type1, factor = [int(x) for x in row.split(',')]
    type_efficacy.append((type_names[type0], type_names[type1], factor))
monpals = open('data/monpals.txt').read().split('\n')

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
    def readbyte(self):
        return ord(self.read(1))
    def readshort(self):
        return struct.unpack(b'<H', self.read(2))[0]
    
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
    presets = {}
    
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
    
    def produce(self, filename):
        # First let's make sure the input is right...
        #for option, value in self.choices.items():
        #    if option not hasattr(self, "opt_"+option):
        #        raise ValueError('No such option for the game {}: {}'.format(self.name, option))
        
        # Now let's make us a ROM
        
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
        
        methods = []
        for option, value in self.choices.items():
            if value and hasattr(self, "opt_"+option):
                params = []
                if value != True:
                    params = [value]
                print option, value, params
                #print "Randomizing: "+option
                methods.append((option, getattr(self, "opt_"+option), params))
        
        methods.sort(key=lambda x: x[1].layer if hasattr(x[1], 'layer') else 0)
        for option, method, params in methods:
            print "Randomizing: "+option+" with "+str(params)
            method(*params)
        
        self.finalize()
        self.rom.close()
        
        return filename

@games.append
class PokemonRed(Game):
    name = "Pokémon Red"
    filename = "pokered.gb" # randomizer rom with some different offsets
    identifier = "pokered"
    symbols = symfile("roms/pokered.sym")
    
    class Form(Form):
        h_randomize = Heading("Randomizations")
        
        game_pokemon = BooleanField("Include Pokémon from all generations")
        starter_pokemon = SelectField('Starter Pokémon', choices=dechoices(":Keep;randomize:Random;basics:Random basics;three-basic:Random three stage basics;single:Single random (yellow style)"), default="")
        trainer_pokemon = BooleanField("Randomize trainer Pokémon")
        wild_pokemon = BooleanField("Randomize wild Pokémon")
        #ow_pokemon = BooleanField("Randomize gift and overworld Pokémon")
        special_conversion = SelectField('Special stat conversion', choices=dechoices("average:Average;spa:Sp. Attack;spd:Sp. Defense;higher:Higher stat;random:Random stat"), default="average")
        movesets = BooleanField("Randomize movesets")
        force_attacking = BooleanField("Always start with an attacking move")
        tms = BooleanField("Randomize the moves TMs teach")
        move_rules = SelectField('Fair random move rules', choices=dechoices(":All moves;no-hms:No HMs;no-broken:No Dragon Rage, Spore;no-hms-broken:No HMs, Dragon Rage, Spore"), default="no-hms-broken")
        cries = BooleanField("Randomize Pokémon cries")
        trainer_classes = BooleanField("Shuffle trainer classes")
        ow_sprites = BooleanField("Shuffle overworld sprites")
        field_items = SelectField('Field items', choices=dechoices(":-;shuffle:Shuffle;shuffle-no-tm:Shuffle, keep TMs"), default="")
    
        h_tweaks = Heading("Tweaks")
        update_types = BooleanField("Update types to X/Y")
        instant_text = BooleanField("Instant text speed")
    
    presets = {
        'race': {
            'starter_pokemon': 'randomize', 'ow_pokemon': True,
            'trainer_pokemon': True, 'wild_pokemon': True, 'game_pokemon': True, 'movesets': True,
            'force_attacking': True,
            'special_conversion': 'average', 'move_rules': 'no-hms-broken', 'cries': True,
            'trainer_classes': True, 'ow_sprites': True,
            'tms': True, 'field_items': 'shuffle-no-tm', 'update_types': True
        },
        'casual': {
            'starter_pokemon': 'three-basic', 'ow_pokemon': True,
            'trainer_pokemon': True, 'wild_pokemon': True, 'game_pokemon': True, 'movesets': True,
            'force_attacking': True,
            'special_conversion': 'average', 'move_rules': '', 'cries': True,
            'trainer_classes': True, 'ow_sprites': True,
            'tms': True, 'field_items': 'shuffle', 'update_types': True
        },
        'classic': {
            'starter_pokemon': 'randomize', 'ow_pokemon': True,
            'trainer_pokemon': True, 'wild_pokemon': True, 'game_pokemon': False, 'movesets': True,
            'force_attacking': True,
            'special_conversion': 'average', 'move_rules': 'no-hms', 'cries': False,
            'trainer_classes': False,
            'tms': True, 'field_items': '', 'update_types': False
        }
    }
    
    CHARS = {' ': 127, '!': 231, '#': 84, '&': 233, "'": 224, "é": 0xba, "É": 0xba, "'d": 208, "'l": 209, "'m": 210, "'r": 211, "'s": 212, "'t": 213, "'v": 214, '(': 154, ')': 155, ',': 244, '-': 227, '.': 232, '/': 243, '0': 246, '1': 247, '2': 248, '3': 249, '4': 250, '5': 251, '6': 252, '7': 253, '8': 254, '9': 255, ':': 156, ';': 157, '?': 230, '@': 80, 'A': 128, 'B': 129, 'C': 130, 'D': 131, 'E': 132, 'F': 133, 'G': 134, 'H': 135, 'I': 136, 'J': 137, 'K': 138, 'L': 139, 'M': 140, 'N': 141, 'O': 142, 'P': 143, 'Q': 144, 'R': 145, 'S': 146, 'T': 147, 'U': 148, 'V': 149, 'W': 150, 'X': 151, 'Y': 152, 'Z': 153, '[': 158, ']': 159, 'a': 160, 'b': 161, 'c': 162, 'd': 163, 'e': 164, 'f': 165, 'g': 166, 'h': 167, 'i': 168, 'j': 169, 'k': 170, 'l': 171, 'm': 172, 'n': 173, 'o': 174, 'p': 175, 'q': 176, 'r': 177, 's': 178, 't': 179, 'u': 180, 'v': 181, 'w': 182, 'x': 183, 'y': 184, 'z': 185, '¥': 240, '×': 241, '…': 117, '№': 116, '→': 235, '─': 122, '│': 124, '┌': 121, '┐': 123, '└': 125, '┘': 126, '▶': 237, '▷': 236, '▼': 238, '♀': 245, '♂': 239, '<': 0xe1, '>': 0xe2,}
    
    POKEMON = [0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f, 0x30, 0x31, 0x33, 0x35, 0x36, 0x37, 0x39, 0x3a, 0x3b, 0x3c, 0x40, 0x41, 0x42, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e, 0x52, 0x53, 0x54, 0x55, 0x58, 0x59, 0x5a, 0x5b, 0x5c, 0x5d, 0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x6b, 0x6c, 0x6d, 0x6e, 0x6f, 0x70, 0x71, 0x72, 0x74, 0x75, 0x76, 0x77, 0x78, 0x7b, 0x7c, 0x7d, 0x7e, 0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x88, 0x8a, 0x8b, 0x8d, 0x8e, 0x8f, 0x90, 0x91, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0x9b, 0x9d, 0x9e, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xab, 0xad, 0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb9, 0xba, 0xbb, 0xbc, 0xbd, 0xbe]
    # TODO fix mew???
    
    POKEMON_MAPPINGS = [None, 112, 115, 32, 35, 21, 100, 34, 80, 2, 103, 108, 102, 88, 94, 29, 31, 104, 111, 131, 59, 151, 130, 90, 72, 92, 123, 120, 9, 127, 114, None, None, 58, 95, 22, 16, 79, 64, 75, 113, 67, 122, 106, 107, 24, 47, 54, 96, 76, None, 126, None, 125, 82, 109, None, 56, 86, 50, 128, None, None, None, 83, 48, 149, None, None, None, 84, 60, 124, 146, 144, 145, 132, 52, 98, None, None, None, 37, 38, 25, 26, None, None, 147, 148, 140, 141, 116, 117, None, None, 27, 28, 138, 139, 39, 40, 133, 136, 135, 134, 66, 41, 23, 46, 61, 62, 13, 14, 15, None, 85, 57, 51, 49, 87, None, None, 10, 11, 12, 68, None, 55, 97, 42, 150, 143, 129, None, None, 89, None, 99, 91, None, 101, 36, 110, 53, 105, None, 93, 63, 65, 17, 18, 121, 1, 3, 73, None, 118, 119, None, None, None, None, 77, 78, 19, 20, 33, 30, 74, 137, 142, None, 81, None, None, 4, 7, 5, 8, 6, None, None, None, None, 43, 44, 45, 69, 70, 71]
    
    STARTER_OFFESTS = [[0x1CC84, 0x1D10E, 0x1D126, 0x39CF8, 0x50FB3, 0x510DD],
[0x1CC88, 0x1CDC8, 0x1D11F, 0x1D104, 0x19591, 0x50FAF, 0x510D9, 0x51CAF, 0x6060E, 0x61450, 0x75F9E],
[0x1CDD0, 0x1D130, 0x1D115, 0x19599, 0x39CF2, 0x50FB1, 0x510DB, 0x51CB7, 0x60616, 0x61458, 0x75FA6]]
    
    #  Dabomstew: eevee, hitmonchan, hitmonlee, 6 voltorbs, 2 electrodes, legendary birds, mewtwo, 2 snorlaxes, aerodactyl, omanyte, kabuto, lapras, magikarp, 6 game corner pokemon
    GIFT_POKEMON_ADDRESSES = [symbols['CeladonMansion5Text2']+3, symbols['FightingDojoText6']+18, symbols['FightingDojoText7']+18,
        ] + [symbols['PowerPlantObject'] + 22 + 8*i  for i in range(9)] + [
        symbols['SeafoamIslands5Object'] + 45, symbols['VictoryRoad2Object'] + 79, symbols['UnknownDungeon3Object'] + 15,
        symbols['Route12Script0'] + 25, symbols['Route16Script0'] + 25, 
        symbols['GiveFossilToCinnabarLab'] + 0x5e, symbols['GiveFossilToCinnabarLab'] + 0x62, symbols['GiveFossilToCinnabarLab'] + 0x66,
        symbols['SilphCo7Text1'] + 0x1f, symbols['MtMoonPokecenterText4'] + 0x34]
    
    
    EVOLUTION_METHODS = {'level-up': 1, 'use-item': 2, 'trade': 3}

    TYPES = {'normal': 0x00, 'fighting': 0x01, 'flying': 0x02, 'poison': 0x03, 'ground': 0x04,
             'rock': 0x05, 'bug': 0x06, 'ghost': 0x07, 'ghost': 0x08,
             'fire': 0x14, 'water': 0x15, 'grass': 0x16, 'electric': 0x17, 'psychic': 0x18,
             'ice': 0x19, 'dragon': 0x1a,
             'dark': 0x00, 'steel': 0x00, 'fairy': 0x00}
     
    ITEMS = {'moon-stone': 0x0a, 'fire-stone': 0x20, 'thunder-stone': 0x21,
             'water-stone': 0x22, 'leaf-stone': 0x2f} # TODO
             
    MAXMOVE = 0xa4 # substitute
    FAIR_MOVES = set(range(1, MAXMOVE+1)) - {144} # +1 ? # transform
    ATTACKING_MOVES = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0d, 0x0f, 0x10, 0x11, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1d, 0x1e, 0x1f, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x28, 0x29, 0x2a, 0x2c, 0x31, 0x32, 0x33, 0x34, 0x35, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f, 0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x4b, 0x4c, 0x50, 0x52, 0x53, 0x54, 0x55, 0x57, 0x58, 0x59, 0x5b, 0x5d, 0x5e, 0x62, 0x63, 0x65, 0x79, 0x7a, 0x7b, 0x7c, 0x7d, 0x7e, 0x7f, 0x80, 0x81, 0x82, 0x83, 0x84, 0x88, 0x8c, 0x8d, 0x8f, 0x91, 0x92, 0x95, 0x98, 0x9a, 0x9b, 0x9d, 0x9e, 0xa1, 0xa3}
    
    DEX_FAMILIES = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [19, 20], [21, 22], [23, 24], [25, 26], [27, 28], [29, 30, 31], [32, 33, 34], [35, 36], [37, 38], [39, 40], [41, 42], [43, 44, 45], [46, 47], [48, 49], [50, 51], [52, 53], [54, 55], [56, 57], [58, 59], [60, 61, 62], [63, 64, 65], [66, 67, 68], [69, 70, 71], [72, 73], [74, 75, 76], [77, 78], [79, 80], [81, 82], [83], [84, 85], [86, 87], [88, 89], [90, 91], [92, 93, 94], [95], [96, 97], [98, 99], [100, 101], [102, 103], [104, 105], [106, 107], [108], [109, 110], [111, 112], [113], [114], [115], [116, 117], [118, 119], [120, 121], [122], [123], [124], [125], [126], [127], [128], [129, 130], [131], [132], [133, 134, 135, 136], [137], [138, 139], [140, 141], [142], [143], [144], [145], [146], [147, 148, 149], [150], [151]]
    DEX = range(1, 152)
    
    OBJECT_MAPS = "CeladonCity PalletTown ViridianCity PewterCity CeruleanCity VermilionCity FuchsiaCity BluesHouse VermilionHouse3 IndigoPlateauLobby SilphCo4 SilphCo5 SilphCo6 CinnabarIsland Route1 OaksLab ViridianMart School ViridianHouse PewterHouse1 PewterHouse2 CeruleanHouseTrashed CeruleanHouse1 BikeShop LavenderHouse1 LavenderHouse2 NameRater VermilionHouse1 VermilionDock CeladonMansion5 FuchsiaMart SaffronHouse1 SaffronHouse2 DiglettsCaveRoute2 Route2House Route5Gate Route6Gate Route7Gate Route8Gate UndergroundPathEntranceRoute8 PowerPlant DiglettsCaveEntranceRoute11 Route16House Route22Gate BillsHouse LavenderTown ViridianPokecenter Mansion1 RockTunnel1 SeafoamIslands1 SSAnne3 VictoryRoad3 RocketHideout1 RocketHideout2 RocketHideout3 RocketHideout4 RocketHideoutElevator SilphCoElevator SafariZoneEast SafariZoneNorth SafariZoneCenter SafariZoneRestHouse1 SafariZoneRestHouse2 SafariZoneRestHouse3 SafariZoneRestHouse4 UnknownDungeon2 UnknownDungeon3 RockTunnel2 SeafoamIslands2 SeafoamIslands3 SeafoamIslands4 SeafoamIslands5 Route7 RedsHouse1F CeladonMart3 CeladonMart4 CeladonMartRoof CeladonMartElevator CeladonMansion1 CeladonMansion2 CeladonMansion3 CeladonMansion4 CeladonPokecenter CeladonGym CeladonGameCorner CeladonMart5 CeladonPrizeRoom CeladonDiner CeladonHouse CeladonHotel MtMoonPokecenter RockTunnelPokecenter Route11Gate Route11GateUpstairs Route12Gate Route12GateUpstairs Route15Gate Route15GateUpstairs Route16Gate Route16GateUpstairs Route18Gate Route18GateUpstairs MtMoon1 MtMoon3 SafariZoneWest SafariZoneSecretHouse BattleCenterM TradeCenterM Route22 Route20 Route23 Route24 Route25 IndigoPlateau SaffronCity VictoryRoad2 MtMoon2 SilphCo7 Mansion2 Mansion3 Mansion4 Route2 Route3 Route4 Route5 Route9 Route13 Route14 Route17 Route19 Route21 VermilionHouse2 CeladonMart2 FuchsiaHouse3 DayCareM Route12House SilphCo8 Route6 Route8 Route10 Route11 Route12 Route15 Route16 Route18 FanClub SilphCo2 SilphCo3 SilphCo10 Lance HallofFameRoom RedsHouse2F Museum1F Museum2F PewterGym PewterPokecenter CeruleanPokecenter CeruleanGym CeruleanMart LavenderPokecenter LavenderMart VermilionPokecenter VermilionMart VermilionGym CopycatsHouse2F FightingDojo SaffronGym SaffronMart SilphCo1 SaffronPokecenter ViridianForestExit Route2Gate ViridianForestEntrance UndergroundPathEntranceRoute5 UndergroundPathEntranceRoute6 UndergroundPathEntranceRoute7 UndergroundPathEntranceRoute7Copy SilphCo9 VictoryRoad1 PokemonTower1 PokemonTower2 PokemonTower3 PokemonTower4 PokemonTower5 PokemonTower6 PokemonTower7 CeladonMart1 ViridianForest SSAnne1 SSAnne2 SSAnne4 SSAnne5 SSAnne6 SSAnne7 SSAnne8 SSAnne9 SSAnne10 UndergroundPathNS UndergroundPathWE DiglettsCave SilphCo11 ViridianGym PewterMart UnknownDungeon1 CeruleanHouse2 FuchsiaHouse1 FuchsiaPokecenter FuchsiaHouse2 SafariZoneEntrance FuchsiaGym FuchsiaMeetingRoom CinnabarGym Lab1 Lab2 Lab3 Lab4 CinnabarPokecenter CinnabarMart CopycatsHouse1F Gary Lorelei Bruno Agatha".split()
    HIDDEN_OBJECT_MAPS = "RedsHouse2F BluesHouse OaksLab ViridianPokecenter ViridianMart ViridianSchool ViridianGym Museum1F PewterGym PewterMart PewterPokecenter CeruleanPokecenter CeruleanGym CeruleanMart LavenderPokecenter VermilionPokecenter VermilionGym CeladonMansion2 CeladonPokecenter CeladonGym GameCorner CeladonHotel FuchsiaPokecenter FuchsiaGym CinnabarGym CinnabarPokecenter SaffronGym MtMoonPokecenter RockTunnelPokecenter BattleCenter TradeCenter ViridianForest MtMoon3 IndigoPlateau Route25 Route9 SSAnne6 SSAnne10 RocketHideout1 RocketHideout3 RocketHideout4 SaffronPokecenter PokemonTower5 Route13 SafariZoneEntrance SafariZoneWest SilphCo5F SilphCo9F CopycatsHouse2F UnknownDungeon1 UnknownDungeon3 PowerPlant SeafoamIslands3 SeafoamIslands5 Mansion1 Mansion3 Route23 VictoryRoad2 Unused6F BillsHouse ViridianCity SafariZoneRestHouse2 SafariZoneRestHouse3 SafariZoneRestHouse4 Route15GateUpstairs LavenderHouse1 CeladonMansion5 FightingDojo Route10 IndigoPlateauLobby CinnabarLab4 BikeShop Route11 Route12 Mansion2 Mansion4 SilphCo11F Route17 UndergroundPathNs UndergroundPathWe CeladonCity SeafoamIslands4 VermilionCity CeruleanCity Route4".split()
    FIELD_ITEMS = []
    with ROM('roms/'+filename, 'rb') as rom:
        for objectmap in OBJECT_MAPS:
            rom.seek(symbols[objectmap+'Object'])
            rom.read(1) # border block
            skip = ord(rom.read(1))
            rom.read(4*skip)
            skip = ord(rom.read(1))
            rom.read(3*skip)
            people = ord(rom.read(1))
            for i in range(people):
                rom.read(5)
                person_type = ord(rom.read(1))
                if person_type & 0x80: # item
                    item = ord(rom.read(1))
                    if item: FIELD_ITEMS.append((rom.tell()-1, item))
                elif person_type & 0x40: # trainer
                    rom.read(2)
        
	    #db $07,$0e,ETHER
	    #dbw BANK(HiddenItems),HiddenItems
	    #db $FF
        
        for hiddenobjectmap in HIDDEN_OBJECT_MAPS:
            rom.seek(symbols[hiddenobjectmap+'HiddenObjects'])
            end = ord(rom.read(1))
            if end == 0xff: continue
            rom.read(1)
            item = ord(rom.read(1))
            bank, offset = rom.readbyte(), rom.readshort()
            if bank * 0x4000 + (offset % 0x4000) == symbols["HiddenItems"]:
                FIELD_ITEMS.append((rom.tell()-4, item))
    
    KEY_ITEMS = [0x2B, 0x30, 0x3B, 0x40, 0x48, 0x4A, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8]
    
    PALS = {"PAL_MEWMON": 0x10,    "PAL_BLUEMON": 0x11,    "PAL_REDMON": 0x12,    "PAL_CYANMON": 0x13,    "PAL_PURPLEMON": 0x14,    "PAL_BROWNMON": 0x15,    "PAL_GREENMON": 0x16,    "PAL_PINKMON": 0x17,    "PAL_YELLOWMON": 0x18,    "PAL_GREYMON": 0x19}
    
    TRAINER_CLASSES = ["YOUNGSTER", "BUG CATCHER", "LASS", "SAILOR", "JR.TRAINER♂", "JR.TRAINER♀", "POKéMANIAC", "SUPER NERD", "HIKER", "BIKER", "BURGLAR", "ENGINEER", "JUGGLER", "FISHERMAN", "SWIMMER", "CUE BALL", "GAMBLER", "BEAUTY", "PSYCHIC", "ROCKER", "JUGGLER", "TAMER", "BIRD KEEPER", "BLACKBELT", "RIVAL1", "PROF.OAK", "CHIEF", "SCIENTIST", "GIOVANNI", "ROCKET", "COOLTRAINER♂", "COOLTRAINER♀", "BRUNO", "BROCK", "MISTY", "LT.SURGE", "ERIKA", "KOGA", "BLAINE", "SABRINA", "GENTLEMAN", "RIVAL2", "RIVAL3", "LORELEI", "CHANNELER", "AGATHA", "LANCE"]
    
    OW_SPRITES = "red blue oak bug_catcher slowbro lass black_hair_boy_1 little_girl bird fat_bald_guy gambler black_hair_boy_2 girl hiker foulard_woman gentleman daisy biker sailor cook bike_shop_guy mr_fuji giovanni rocket medium waiter erika mom_geisha brunette_girl lance oak_aide oak_aide rocker swimmer white_player gym_helper old_person mart_guy fisher old_medium_woman nurse cable_club_woman mr_masterball lapras_giver warden ss_captain fisher2 blackbelt guard mom balding_guy young_boy gameboy_kid gameboy_kid clefairy agatha bruno lorelei seel".split()
    
    def random_pokemon(self):
        return choice(self.POKEMON)
    
    #":All moves;no-hms:No HMs;no-broken:No Dragon Rage, Spore;no-hms-broken:No HMs, Dragon Rage, Spore"
    def opt_move_rules(self, rule):
        if rule in ('no-hms', 'no-hms-broken'):
            self.FAIR_MOVES -= {57, 70, 19, 15, 148}
            self.ATTACKING_MOVES -= {57, 70, 19, 15, 148}
        if rule in ('no-broken', 'no-hms-broken'):
            self.FAIR_MOVES -= {0x52, 0x93} # Dragon Rage, Spore
            self.ATTACKING_MOVES -= {0x52, 0x93} # Dragon Rage, Spore
        return
    opt_move_rules.layer = -5
    
    #:Keep,randomize:Random,basics:Random basics,three-basic:Random three stage basics,single:Single random (yellow style)
    def opt_starter_pokemon(self, mode):
        #starters = [self.random_pokemon() for i in range(3)]
        if mode == 'randomize':
            starters = sample(self.POKEMON, 3)
        elif mode == 'basics':
            families = sample(self.DEX_FAMILIES, 3)
            starters = [self.POKEMON_MAPPINGS.index(1+self.DEX.index(family[0])) for family in families]
        elif mode == 'three-basic':
            three_stage_families = []
            for family in self.DEX_FAMILIES:
                if len(family) == 3: three_stage_families.append(family)
            if len(three_stage_families) >= 3:
                families = sample(three_stage_families, 3)
            else:
                families = [choice(three_stage_families) for i in range(3)]
            starters = [self.POKEMON_MAPPINGS.index(1+self.DEX.index(family[0])) for family in families]
        elif mode == 'single':
            starters = [choice(self.POKEMON)]*3
        
        for i, starter in enumerate(starters):
            for offset in self.STARTER_OFFESTS[i]:
                self.rom.seek(offset)
                self.rom.writebyte(starter)
    opt_starter_pokemon.layer = 10
    
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

    def opt_field_items(self, mode):
        items = []
        addresses = []
        for address, item in self.FIELD_ITEMS:
            if item not in self.KEY_ITEMS + range(0xc4, 0xfb) if mode == "shuffle-no-tm" else []:
                items.append(item)
                addresses.append(address)
        
        shuffle(items)
        for address in addresses:
            self.rom.seek(address)
            self.rom.writebyte(items.pop())
        
    def opt_tms(self):
        rom = self.rom
        rom.seek(self.symbols["TechnicalMachines"])
        tms = sample(self.FAIR_MOVES, 50)
        for move in tms:
            rom.write(chr(move))
    opt_tms.layer = 5
        
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
        rom = self.rom
        dex = []
        dex_families = []
        while len(dex) < 150:
            randfamily = choice(minidex['evolution_chains'])
            #if randfamily[0] >= 719: continue # Diancie, no sprites
            if randfamily[0] == 151: pass
            if randfamily not in dex_families and len(dex)+len(randfamily) <= 150:
                dex += randfamily
                dex_families.append(randfamily)
        
        self.DEX_FAMILIES = dex_families
        self.DEX = dex
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
                if movei == 0 and self.choices['force_attacking']:
                    move = choice(self.ATTACKING_MOVES)
                else:
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
                        rom.writebyte(1)
                    elif trigger == 'trade':
                        rom.writebyte(1)
                    rom.writebyte(self.POKEMON_MAPPINGS.index(1+dex.index(evolution['evolved_species'])))
                rom.writebyte(0)
                # moves
                for level in minidex['pokemon'][num]['moveset']:
                    if level != 0 and randint(0, 1):
                        rom.write(chr(level))
                        rom.write(chr(choice(self.FAIR_MOVES)))
                rom.writebyte(0) # end moves
            if dexnum == 151:
                rom.writebyte(0)
                rom.writebyte(0)
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
        
        # Write palettes
        self.rom.seek(self.symbols["MonsterPalettes"]+1)
        for i in range(150):
            self.rom.writebyte(self.PALS[monpals[dex[i]-1]])
    opt_game_pokemon.layer = -1
    
    def opt_movesets(self):
        if self.choices['game_pokemon']: return
        rom = self.rom
        for i in range(150):
            rom.seek(self.symbols["BulbasaurBaseStats"] + 15 + (28 * i))
            # moves known at lv 0
            moves = []
            for i in range(4):
                move = rom.readbyte()
                if move != 0:
                    if i == 0 and self.choices['force_attacking']:
                        move = choice(self.ATTACKING_MOVES)
                    else:
                        move = choice(self.FAIR_MOVES)
                    while move in moves:
                        move = choice(self.FAIR_MOVES)
                moves.append(move)
            assert len(moves) == 4
            rom.seek(rom.tell() - 4)
            for move in moves:
                rom.writebyte(move)
            
            rom.readbyte()
            # tm/hm
            for i in range(7):
                rom.writebyte(randint(0, 255))
            
            rom.seek(self.symbols["EvosMovesPointerTable"] - 2 + (2 * self.POKEMON_MAPPINGS.index(1+i)))
            rom.seek((self.symbols["EvosMovesPointerTable"] // 0x4000) * 0x4000 + (rom.readshort() % 0x4000))
            # evolutions
            while rom.readbyte() != 0: pass
            # learnset
            while True:
                if rom.readbyte() == 0: break
                move = choice(self.FAIR_MOVES)
                while move in moves:
                    move = choice(self.FAIR_MOVES)
                moves.append(move)
                rom.writebyte(move)
    
    def opt_update_types(self):
        self.TYPES.update({'dark': 0x09, 'steel': 0x0a, 'fairy': 0x0b})
        types = self.TYPES
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
    opt_update_types.layer = -5
        
    def opt_trainer_classes(self):
        classes = range(len(self.TRAINER_CLASSES))
        shuffle(classes)
        # TODO maybe TrainerClassMoveChoiceModifications ?
        
        class_data = []
        self.rom.seek(self.symbols["TrainerPicAndMoneyPointers"])
        for i in range(len(classes)):
            class_data.append(self.rom.read(5))
        
        self.rom.seek(self.symbols["TrainerPicAndMoneyPointers"])
        for c in classes:
            self.rom.write(class_data[c])
        
        assert self.rom.tell() == self.symbols["TrainerNames"]
        
        for c in classes:
            self.write_string(self.TRAINER_CLASSES[c])
    
    def opt_ow_pokemon(self):
        rom = self.rom
        for address in self.GIFT_POKEMON_ADDRESSES:
            self.rom.seek(address)
            self.rom.writebyte(choice(self.POKEMON))
        prizemons = sample(self.POKEMON, 6)
        for j in range(2):
            rom.seek(self.symbols['PrizeMenuMon{}Entries'.format(j+1)])
            for i in range(3):
                rom.writebyte(prizemons[j*3 + i])
        
        rom.seek(self.symbols['PrizeMonLevelDictionary'])
        for prizemon in prizemons:
            rom.writebyte(prizemon)
            rom.readbyte()
    
    def opt_ow_sprites(self):
        # 59 sprites total, 0x180 bytes per sprite, 42 fit in one bank
        locs = {}
        for bank, sprites in ((0x3a, self.OW_SPRITES[:42]), (0x3b, self.OW_SPRITES[42:])):
            self.rom.seek(0x3f * 0x4000)
            for sprite in sprites:
                locs[sprite] = self.rom.tell()
                self.rom.write(open('gfx/ow_sprites/{}.2bpp'.format(sprite)).read())
        assert self.rom.tell() <= 0x40 * 0x4000
        
        self.rom.seek(self.symbols['SpriteSheetPointerTable'])
        sprites = self.OW_SPRITES
        shuffle(sprites)
        for sprite in sprites:
            self.rom.writeshort(locs[sprite] % 0x4000 + 0x4000)
            self.rom.writebyte(0xc0)
            self.rom.writebyte(locs[sprite] // 0x4000)
    
    def opt_instant_text(self):
        self.rom.seek(0x00ff)
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
    
# TODO make good use of https://github.com/dannye/tcg !
@games.append
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
