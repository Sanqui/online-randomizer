#!/bin/python2
# encoding: utf-8
from __future__ import unicode_literals

from randomizer import *

minidex = yaml.load(open('data/minidex.yaml'))
type_names = "- normal fighting flying poison ground rock bug ghost steel fire water grass electric psychic ice dragon dark fairy".split()
type_efficacy = []
for row in open('data/type_efficacy.csv').readlines():
    type0, type1, factor = [int(x) for x in row.split(',')]
    type_efficacy.append((type_names[type0], type_names[type1], factor))
monpals = open('data/monpals.txt').read().split('\n')

menu_icons = ['mon ball helix fairy bird water bug grass snake quadruped -'.split().index(l.strip()) for l in open('data/menu_icons.txt')]

subprocess.check_call("make -C sources/pokered/ red".split(' '))
subprocess.check_call("cp sources/pokered/pokered.gbc roms/pokered.gbc".split(' '))
subprocess.check_call("cp sources/pokered/pokered.sym roms/pokered.sym".split(' '))

@randomizer_games.append
class PokemonRed(Game):
    name = "Pokémon Red"
    filename = "pokered.gbc" # randomizer rom with some different offsets
    identifier = "pokered"
    symbols = symfile("roms/pokered.sym")
    
    form_expanded_by = {'game_pokemon_source_generations': 'game_pokemon',
        'pokedex_size': 'game_pokemon',
        'special_conversion': 'game_pokemon',
        'force_attacking': 'movesets',
        'force_four_moves': 'movesets',
        'move_rules': 'movesets',
        'soundtrack_sources': 'soundtrack',
        'pitches': 'soundtrack',}
    class Form(Form):        
        h_randomize = Heading("Randomizations")
        
        game_pokemon = BooleanField("Include Pokémon from later generations", description="This is exactly what it sounds like.  150 random Pokémon from all 721 will be picked and inserted into the game's Pokédex.  Check it out.")
        game_pokemon_source_generations = MultiCheckboxField("Source generations", choices=list(enumerate("I II III IV V VI".split(), start=1)), default=(1, 2, 3, 4, 5, 6), coerce=int, description="This lets you somewhat whitelist the Pokémon you'd like to see.  Try playing with just Gen V, for example!")
        pokedex_size = SelectField('Pokédex size', choices=dechoices("151:151;251:251"), default="251")
        special_conversion = SelectField('Special stat conversion', choices=dechoices("average:Average;spa:Sp. Attack;spd:Sp. Defense;higher:Higher stat;random:Random stat"), default="average", description="Since Pokémon Red only has one Special stat, we need to decide on how to transform the two stats of new Pokémon.")
        starter_pokemon = SelectField('Starter Pokémon', choices=dechoices(":Keep;randomize:Random;basics:Random basics;three-basic:Random three stage basics;single:Single random (yellow style)"), default="")
        trainer_pokemon = BooleanField("Randomize trainer Pokémon", description="This option randomizes the Pokémon opponent trainers carry.  The levels stay the same.")
        wild_pokemon = BooleanField("Randomize wild Pokémon", description="This option randomizes the ten possible wild Pokémon in each area.")
        ow_pokemon = BooleanField("Randomize gift and overworld Pokémon", description="This randomizes the Pokémon you can encounter on the overworld and the Pokémon you can receive or buy.")
        movesets = BooleanField("Randomize movesets", description="Randomizes which moves Pokémon learn, both on level up and TM compatibility.")
        force_attacking = BooleanField("Always start with an attacking move", description="Don't pick this if you enjoy having Splash as your only move.")
        force_four_moves = BooleanField("Always start with four moves", description="This makes more Pokémon usable on average.")
        move_rules = SelectField('Fair random move rules', choices=dechoices(":All moves;no-hms:No HMs;no-broken:No broken moves;no-hms-broken:No HMs and broken moves"), default="no-hms-broken", description="This opinion is useful for races, for example, to prevent skipping the whole Nugget Bridge and S. S. Anne if somebody gets lucky with Cut.  Broken moves are Sonicboom, Dragon Rage, Spore, Guillotine, Horn Drill, Fissure.")
        tms = BooleanField("Randomize the moves TMs teach", description="Note that Gym Leaders will still announce their old TM for now, so make sure to check!")
        trainer_classes = BooleanField("Shuffle trainer classes", description="This affects payouts too, but not AI.")
        ow_sprites = BooleanField("Shuffle overworld sprites", description="This is purely visual and for fun.")
        field_items = SelectField('Field items', choices=dechoices(":-;shuffle-no-tm:Shuffle, keep TMs;shuffle:Shuffle;random-no-tm:Random, keep TMs;random:Random;random-key:Random with Key Items"), default="", description="This option randomizes what you can find lying on the ground.")
        soundtrack = BooleanField("Randomize the soundtrack", description="Picks random fitting songs for each song in Red.  Enjoy listening to new music while you play.")
        soundtrack_sources = MultiCheckboxField("Sources", choices=dechoices("red:Red;crystal:Crystal;side:TCG & Pinball;demixes:Demixes;fan:Fan (Prism)"), default="red crystal side demixes fan".split(), description="If there's no alternative song choose, you get the Red song.")
        pitches = BooleanField("Randomize note pitch", description="Randomly transposes musical pieces in the game.  May sound pretty bad at times, but is mostly just interesting.")
    
        h_tweaks = Heading("Tweaks")
        change_trade_evos = BooleanField("Perform trade evos at lv. 42", description="This changes all trade evolutions into standard level-up ones.  Doesn't work in classic (no new Pokémon) yet!")
        update_types = BooleanField("Update types to X/Y", description="This option updates the whole type table to Gen 6's, including the new types.  If you don't choose this, types that didn't exist in Gen 1 become Normal.")
        update_moves = BooleanField("Update moves to X/Y", description="This option partially updates move data to Gen 6's.  Effects are not affected.")
        new_moves = BooleanField("Add new moves", description="This option adds some 45 new moves from later games.  Not all effects are perfectly accurate.  Forces updating moves to X/Y.")
        yellow_gym_leaders = BooleanField("Yellow gym leader levels", description="Changes Gym leader levels to match Yellow, mostly making them tougher.")
        instant_text = BooleanField("Instant text speed", description="This makes all dialogue display instantly, instead of delaying after each letter.")
    
    presets = {
        'race': {
            'starter_pokemon': 'randomize', 'ow_pokemon': True, 'pokedex_size': "251",
            'trainer_pokemon': True, 'wild_pokemon': True, 'game_pokemon': True, 'movesets': True,
            'force_attacking': True, 'force_four_moves': True, 'change_trade_evos': True,
            'special_conversion': 'average', 'move_rules': 'no-hms-broken', 'cries': True,
            'trainer_classes': True, 'ow_sprites': True, 'backsprites': 'back',
            'tms': True, 'field_items': 'shuffle-no-tm', 'update_types': True, 'update_moves': True,
            'new_moves': True,
            'yellow_gym_leaders': True,
            'soundtrack': True, 'pitches': False, 'soundtrack_sources-4': False,
        },
        'casual': {
            'starter_pokemon': 'three-basic', 'ow_pokemon': True, 'pokedex_size': "251", 
            'trainer_pokemon': True, 'wild_pokemon': True, 'game_pokemon': True, 'movesets': True,
            'force_attacking': True, 'force_four_moves': False, 'change_trade_evos': True,
            'special_conversion': 'average', 'move_rules': '', 'cries': True,
            'trainer_classes': True, 'ow_sprites': True, 'backsprites': 'back',
            'tms': True, 'field_items': 'shuffle', 'update_types': True, 'update_moves': True,
            'new_moves': True,
            'yellow_gym_leaders': True,
            'soundtrack': True, 'pitches': False, 'soundtrack_sources-4': False,
        },
        'classic': {
            'starter_pokemon': 'randomize', 'ow_pokemon': True, 
            'trainer_pokemon': True, 'wild_pokemon': True, 'game_pokemon': False, 'movesets': True,
            'force_attacking': True, 'force_four_moves': False,
            'special_conversion': 'average', 'move_rules': 'no-hms', 'cries': False,
            'trainer_classes': False,
            'yellow_gym_leaders': False,
            'tms': True, 'field_items': '', 'update_types': False, 'update_moves': False,
            'new_moves': False,
            'music': False, 'pitches': False
        }
    }
    
    ROM_FLAGS = "instant_text debug update_moves".split()
    
    CHARS = {' ': 127, '!': 231, '#': 84, '&': 233, "'": 224, "é": 0xba, "É": 0xba, "'d": 208, "'l": 209, "'m": 210, "'r": 211, "'s": 212, "'t": 213, "'v": 214, '(': 154, ')': 155, ',': 244, '-': 227, '.': 232, '/': 243, '0': 246, '1': 247, '2': 248, '3': 249, '4': 250, '5': 251, '6': 252, '7': 253, '8': 254, '9': 255, ':': 156, ';': 157, '?': 230, '@': 80, 'A': 128, 'B': 129, 'C': 130, 'D': 131, 'E': 132, 'F': 133, 'G': 134, 'H': 135, 'I': 136, 'J': 137, 'K': 138, 'L': 139, 'M': 140, 'N': 141, 'O': 142, 'P': 143, 'Q': 144, 'R': 145, 'S': 146, 'T': 147, 'U': 148, 'V': 149, 'W': 150, 'X': 151, 'Y': 152, 'Z': 153, '[': 158, ']': 159, 'a': 160, 'b': 161, 'c': 162, 'd': 163, 'e': 164, 'f': 165, 'g': 166, 'h': 167, 'i': 168, 'j': 169, 'k': 170, 'l': 171, 'm': 172, 'n': 173, 'o': 174, 'p': 175, 'q': 176, 'r': 177, 's': 178, 't': 179, 'u': 180, 'v': 181, 'w': 182, 'x': 183, 'y': 184, 'z': 185, '¥': 240, '×': 241, '…': 117, '№': 116, '→': 235, '─': 122, '│': 124, '┌': 121, '┐': 123, '└': 125, '┘': 126, '▶': 237, '▷': 236, '▼': 238, '♀': 245, '♂': 239, '<': 0xe1, '>': 0xe2,}
        
    STARTER_OFFESTS = [[symbols['OaksLabScript8'] + 0x4, symbols['OaksLabText2'] + 0xc, symbols['OaksLabText4'] + 0x2, symbols['ReadTrainer'] + 0xa5, symbols['StarterMons_50faf'] + 0x4, symbols['StarterMons_510d9'] + 0x4],
[symbols['OaksLabScript8'] + 0x8, symbols['OaksLabScript11'] + 0xf, symbols['OaksLabText3'] + 0xc, symbols['OaksLabText2'] + 0x2, symbols['CeruleanCityScript1'] + 0x2a, symbols['StarterMons_50faf'] + 0x0, symbols['StarterMons_510d9'] + 0x0, symbols['SilphCo7Script3'] + 0x2d, symbols['PokemonTower2Text1'] + 0x2f, symbols['SSAnne2Script1'] + 0x20, symbols['GaryScript2'] + 0x34],
[symbols['OaksLabScript11'] + 0x17, symbols['OaksLabText4'] + 0xc, symbols['OaksLabText3'] + 0x2, symbols['CeruleanCityScript1'] + 0x32, symbols['ReadTrainer'] + 0x9f, symbols['StarterMons_50faf'] + 0x2, symbols['StarterMons_510d9'] + 0x2, symbols['SilphCo7Script3'] + 0x35, symbols['PokemonTower2Text1'] + 0x37, symbols['SSAnne2Script1'] + 0x28, symbols['GaryScript2'] + 0x3c]]
    
    #  Dabomstew: eevee, hitmonchan, hitmonlee, 6 voltorbs, 2 electrodes, legendary birds, mewtwo, 2 snorlaxes, aerodactyl, omanyte, kabuto, lapras, magikarp, 6 game corner pokemon
    GIFT_POKEMON_ADDRESSES = [symbols['CeladonMansion5Text2']+3, symbols['FightingDojoText6']+19, symbols['FightingDojoText7']+19,
        ] + [symbols['PowerPlantObject'] + 22 + 8*i  for i in range(9)] + [
        symbols['SeafoamIslands5Object'] + 44, symbols['VictoryRoad2Object'] + 78, symbols['UnknownDungeon3Object'] + 14,
        symbols['Route12Script0'] + 25-2, symbols['Route16Script0'] + 25-2, 
        symbols['GiveFossilToCinnabarLab'] + 0x5e, symbols['GiveFossilToCinnabarLab'] + 0x62, symbols['GiveFossilToCinnabarLab'] + 0x66,
        symbols['SilphCo7Text1'] + 0x1f, symbols['MtMoonPokecenterText4'] + 0x34]
    
    
    EVOLUTION_METHODS = {'level-up': 1, 'use-item': 2, 'trade': 3}

    TYPES = {'normal': 0x00, 'fighting': 0x01, 'flying': 0x02, 'poison': 0x03, 'ground': 0x04,
             'rock': 0x05, 'bug': 0x07, 'ghost': 0x08,
             'fire': 0x14, 'water': 0x15, 'grass': 0x16, 'electric': 0x17, 'psychic': 0x18,
             'ice': 0x19, 'dragon': 0x1a,
             'dark': 0x00, 'steel': 0x00, 'fairy': 0x00}
    
    ITEMS = bidict({"MASTER_BALL": 0x01, "ULTRA_BALL": 0x02, "GREAT_BALL": 0x03, "POKE_BALL": 0x04, "TOWN_MAP": 0x05, "BICYCLE": 0x06, "SAFARI_BALL": 0x08, "POKEDEX": 0x09, "MOON_STONE": 0x0A, "ANTIDOTE": 0x0B, "BURN_HEAL": 0x0C, "ICE_HEAL": 0x0D, "AWAKENING": 0x0E, "PARLYZ_HEAL": 0x0F, "FULL_RESTORE": 0x10, "MAX_POTION": 0x11, "HYPER_POTION": 0x12, "SUPER_POTION": 0x13, "POTION": 0x14, "ESCAPE_ROPE": 0x1D, "REPEL": 0x1E, "OLD_AMBER": 0x1F, "FIRE_STONE": 0x20, "THUNDER_STONE": 0x21, "WATER_STONE": 0x22, "HP_UP": 0x23, "PROTEIN": 0x24, "IRON": 0x25, "CARBOS": 0x26, "CALCIUM": 0x27, "RARE_CANDY": 0x28, "DOME_FOSSIL": 0x29, "HELIX_FOSSIL": 0x2A, "SECRET_KEY": 0x2B, "BIKE_VOUCHER": 0x2D, "X_ACCURACY": 0x2E, "LEAF_STONE": 0x2F, "CARD_KEY": 0x30, "NUGGET": 0x31, "POKE_DOLL": 0x33, "FULL_HEAL": 0x34, "REVIVE": 0x35, "MAX_REVIVE": 0x36, "GUARD_SPEC_": 0x37, "SUPER_REPEL": 0x38, "MAX_REPEL": 0x39, "DIRE_HIT": 0x3A, "FRESH_WATER": 0x3C, "SODA_POP": 0x3D, "LEMONADE": 0x3E, "S_S__TICKET": 0x3F, "GOLD_TEETH": 0x40, "X_ATTACK": 0x41, "X_DEFEND": 0x42, "X_SPEED": 0x43, "X_SPECIAL": 0x44, "COIN_CASE": 0x45, "OAKS_PARCEL": 0x46, "ITEMFINDER": 0x47, "SILPH_SCOPE": 0x48, "POKE_FLUTE": 0x49, "LIFT_KEY": 0x4A, "EXP__ALL": 0x4B, "OLD_ROD": 0x4C, "GOOD_ROD": 0x4D, "SUPER_ROD": 0x4E, "PP_UP": 0x4F, "ETHER": 0x50, "MAX_ETHER": 0x51, "ELIXER": 0x52, "MAX_ELIXER": 0x53, "HM_01": 0xC4, "HM_02": 0xC5, "HM_03": 0xC6, "HM_04": 0xC7, "HM_05": 0xC8, "TM_01": 0xC9, "TM_02": 0xCA, "TM_03": 0xCB, "TM_04": 0xCC, "TM_05": 0xCD, "TM_06": 0xCE, "TM_07": 0xCF, "TM_08": 0xD0, "TM_09": 0xD1, "TM_10": 0xD2, "TM_11": 0xD3, "TM_12": 0xD4, "TM_13": 0xD5, "TM_14": 0xD6, "TM_15": 0xD7, "TM_16": 0xD8, "TM_17": 0xD9, "TM_18": 0xDA, "TM_19": 0xDB, "TM_20": 0xDC, "TM_21": 0xDD, "TM_22": 0xDE, "TM_23": 0xDF, "TM_24": 0xE0, "TM_25": 0xE1, "TM_26": 0xE2, "TM_27": 0xE3, "TM_28": 0xE4, "TM_29": 0xE5, "TM_30": 0xE6, "TM_31": 0xE7, "TM_32": 0xE8, "TM_33": 0xE9, "TM_34": 0xEA, "TM_35": 0xEB, "TM_36": 0xEC, "TM_37": 0xED, "TM_38": 0xEE, "TM_39": 0xEF, "TM_40": 0xF0, "TM_41": 0xF1, "TM_42": 0xF2, "TM_43": 0xF3, "TM_44": 0xF4, "TM_45": 0xF5, "TM_46": 0xF6, "TM_47": 0xF7, "TM_48": 0xF8, "TM_49": 0xF9, "TM_50": 0xFA})
    BANNED_ITEMS = "TOWN_MAP BICYCLE SAFARI_BALL POKEDEX OLD_AMBER DOME_FOSSIL HELIX_FOSSIL SECRET_KEY BIKE_VOUCHER CARD_KEY S_S__TICKET GOLD_TEETH COIN_CASE OAKS_PARCEL ITEMFINDER SILPH_SCOPE POKE_FLUTE LIFT_KEY EXP__ALL OLD_ROD GOOD_ROD SUPER_ROD HM_01 HM_02 HM_03 HM_04 HM_05".split()
    #KEY_ITEMS = [0x2B, 0x30, 0x3B, 0x40, 0x48, 0x4A, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8]
    EVO_ITEMS = {'moon-stone': 0x0a, 'fire-stone': 0x20, 'thunder-stone': 0x21,
             'water-stone': 0x22, 'leaf-stone': 0x2f} # TODO
             
    MAXMOVE = 0xa4 # substitute
    FAIR_MOVES = set(range(1, MAXMOVE+1)) - {144, 0x5a, 0x0c, 0x20} # +1 ? # transform # temp ohko moves
    ATTACKING_MOVES = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0c, 0x0d, 0x0f, 0x10, 0x11, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1d, 0x1e, 0x1f, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x28, 0x29, 0x2a, 0x2c, 0x31, 0x32, 0x33, 0x34, 0x35, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f, 0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x4b, 0x4c, 0x50, 0x52, 0x53, 0x54, 0x55, 0x57, 0x58, 0x59, 0x5b, 0x5d, 0x5e, 0x62, 0x63, 0x65, 0x79, 0x7a, 0x7b, 0x7c, 0x7d, 0x7e, 0x7f, 0x80, 0x81, 0x82, 0x83, 0x84, 0x88, 0x8c, 0x8d, 0x8f, 0x91, 0x92, 0x95, 0x98, 0x9a, 0x9b, 0x9d, 0x9e, 0xa1, 0xa3} - {0x5a, 0x0c, 0x20}
    NEW_MOVES = bidict({204: 409, 205: 183, 206: 457, 207: 350, 208: 317, 209: 337, 210: 530, 211: 242, 212: 399, 213: 400, 214: 313, 215: 418, 216: 430, 217: 442, 218: 211, 219: 232, 220: 605, 221: 577, 222: 583, 223: 585, 224: 441, 225: 305, 226: 198, 227: 523, 228: 405, 229: 224, 230: 324, 231: 404, 232: 247, 233: 325, 234: 425, 235: 421, 236: 331, 237: 412, 238: 532, 239: 345, 240: 402, 241: 352, 242: 332, 243: 403, 244: 355, 245: 609, 246: 351, 247: 192, 248: 200}).inv
    NEW_ATTACKING_MOVES = set(range(204, 249)) - {214, 244}
    
    DEX_FAMILIES = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [19, 20], [21, 22], [23, 24], [25, 26], [27, 28], [29, 30, 31], [32, 33, 34], [35, 36], [37, 38], [39, 40], [41, 42], [43, 44, 45], [46, 47], [48, 49], [50, 51], [52, 53], [54, 55], [56, 57], [58, 59], [60, 61, 62], [63, 64, 65], [66, 67, 68], [69, 70, 71], [72, 73], [74, 75, 76], [77, 78], [79, 80], [81, 82], [83], [84, 85], [86, 87], [88, 89], [90, 91], [92, 93, 94], [95], [96, 97], [98, 99], [100, 101], [102, 103], [104, 105], [106, 107], [108], [109, 110], [111, 112], [113], [114], [115], [116, 117], [118, 119], [120, 121], [122], [123], [124], [125], [126], [127], [128], [129, 130], [131], [132], [133, 134, 135, 136], [137], [138, 139], [140, 141], [142], [143], [144], [145], [146], [147, 148, 149], [150], [151]]
    DEX = range(1, 152)
    POKEMON = range(1, 152)
    
    OBJECT_MAPS = "CeladonCity PalletTown ViridianCity PewterCity CeruleanCity VermilionCity FuchsiaCity BluesHouse VermilionHouse3 IndigoPlateauLobby SilphCo4 SilphCo5 SilphCo6 CinnabarIsland Route1 OaksLab ViridianMart School ViridianHouse PewterHouse1 PewterHouse2 CeruleanHouseTrashed CeruleanHouse1 BikeShop LavenderHouse1 LavenderHouse2 NameRater VermilionHouse1 VermilionDock CeladonMansion5 FuchsiaMart SaffronHouse1 SaffronHouse2 DiglettsCaveRoute2 Route2House Route5Gate Route6Gate Route7Gate Route8Gate UndergroundPathEntranceRoute8 PowerPlant DiglettsCaveEntranceRoute11 Route16House Route22Gate BillsHouse LavenderTown ViridianPokecenter Mansion1 RockTunnel1 SeafoamIslands1 SSAnne3 VictoryRoad3 RocketHideout1 RocketHideout2 RocketHideout3 RocketHideout4 RocketHideoutElevator SilphCoElevator SafariZoneEast SafariZoneNorth SafariZoneCenter SafariZoneRestHouse1 SafariZoneRestHouse2 SafariZoneRestHouse3 SafariZoneRestHouse4 UnknownDungeon2 UnknownDungeon3 RockTunnel2 SeafoamIslands2 SeafoamIslands3 SeafoamIslands4 SeafoamIslands5 Route7 RedsHouse1F CeladonMart3 CeladonMart4 CeladonMartRoof CeladonMartElevator CeladonMansion1 CeladonMansion2 CeladonMansion3 CeladonMansion4 CeladonPokecenter CeladonGym CeladonGameCorner CeladonMart5 CeladonPrizeRoom CeladonDiner CeladonHouse CeladonHotel MtMoonPokecenter RockTunnelPokecenter Route11Gate Route11GateUpstairs Route12Gate Route12GateUpstairs Route15Gate Route15GateUpstairs Route16Gate Route16GateUpstairs Route18Gate Route18GateUpstairs MtMoon1 MtMoon3 SafariZoneWest SafariZoneSecretHouse BattleCenterM TradeCenterM Route22 Route20 Route23 Route24 Route25 IndigoPlateau SaffronCity VictoryRoad2 MtMoon2 SilphCo7 Mansion2 Mansion3 Mansion4 Route2 Route3 Route4 Route5 Route9 Route13 Route14 Route17 Route19 Route21 VermilionHouse2 CeladonMart2 FuchsiaHouse3 DayCareM Route12House SilphCo8 Route6 Route8 Route10 Route11 Route12 Route15 Route16 Route18 FanClub SilphCo2 SilphCo3 SilphCo10 Lance HallofFameRoom RedsHouse2F Museum1F Museum2F PewterGym PewterPokecenter CeruleanPokecenter CeruleanGym CeruleanMart LavenderPokecenter LavenderMart VermilionPokecenter VermilionMart VermilionGym CopycatsHouse2F FightingDojo SaffronGym SaffronMart SilphCo1 SaffronPokecenter ViridianForestExit Route2Gate ViridianForestEntrance UndergroundPathEntranceRoute5 UndergroundPathEntranceRoute6 UndergroundPathEntranceRoute7 UndergroundPathEntranceRoute7Copy SilphCo9 VictoryRoad1 PokemonTower1 PokemonTower2 PokemonTower3 PokemonTower4 PokemonTower5 PokemonTower6 PokemonTower7 CeladonMart1 ViridianForest SSAnne1 SSAnne2 SSAnne4 SSAnne5 SSAnne6 SSAnne7 SSAnne8 SSAnne9 SSAnne10 UndergroundPathNS UndergroundPathWE DiglettsCave SilphCo11 ViridianGym PewterMart UnknownDungeon1 CeruleanHouse2 FuchsiaHouse1 FuchsiaPokecenter FuchsiaHouse2 SafariZoneEntrance FuchsiaGym FuchsiaMeetingRoom CinnabarGym Lab1 Lab2 Lab3 Lab4 CinnabarPokecenter CinnabarMart CopycatsHouse1F Gary Lorelei Bruno Agatha".split()
    HIDDEN_OBJECT_MAPS = "RedsHouse2F BluesHouse OaksLab ViridianPokecenter ViridianMart ViridianSchool ViridianGym Museum1F PewterGym PewterMart PewterPokecenter CeruleanPokecenter CeruleanGym CeruleanMart LavenderPokecenter VermilionPokecenter VermilionGym CeladonMansion2 CeladonPokecenter CeladonGym GameCorner CeladonHotel FuchsiaPokecenter FuchsiaGym CinnabarGym CinnabarPokecenter SaffronGym MtMoonPokecenter RockTunnelPokecenter BattleCenter TradeCenter ViridianForest MtMoon3 IndigoPlateau Route25 Route9 SSAnne6 SSAnne10 RocketHideout1 RocketHideout3 RocketHideout4 SaffronPokecenter PokemonTower5 Route13 SafariZoneEntrance SafariZoneWest SilphCo5F SilphCo9F CopycatsHouse2F UnknownDungeon1 UnknownDungeon3 PowerPlant SeafoamIslands3 SeafoamIslands5 Mansion1 Mansion3 Route23 VictoryRoad2 Unused6F BillsHouse ViridianCity SafariZoneRestHouse2 SafariZoneRestHouse3 SafariZoneRestHouse4 Route15GateUpstairs LavenderHouse1 CeladonMansion5 FightingDojo Route10 IndigoPlateauLobby CinnabarLab4 BikeShop Route11 Route12 Mansion2 Mansion4 SilphCo11F Route17 UndergroundPathNs UndergroundPathWe CeladonCity SeafoamIslands4 VermilionCity CeruleanCity Route4".split()
    FIELD_ITEMS = []
    EXISTING_CRIES = []
    TMS = []
    HMS = []
    
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
            while True:
                end = ord(rom.read(1))
                if end == 0xff: break
                rom.read(1)
                item = ord(rom.read(1))
                bank, offset = rom.readbyte(), rom.readshort()
                if bank * 0x4000 + (offset % 0x4000) == symbols["HiddenItems"]:
                    FIELD_ITEMS.append((rom.tell()-4, item))
        
        for symbol in symbols.keys():
            if symbol.startswith("OWItem"):
                rom.seek(symbols[symbol])
                item = ord(rom.read(1))
                FIELD_ITEMS.append((symbols[symbol], item))
        
        rom.seek(symbols['CryHeaders'])
        for i in range(251):
            EXISTING_CRIES.append(rom.read(6))
        
        rom.seek(symbols['TechnicalMachines'])
        for i in range(50):
            TMS.append(rom.readbyte())
        for i in range(5):
            HMS.append(rom.readbyte())
    
    PALS = {"PAL_MEWMON": 0x10,    "PAL_BLUEMON": 0x11,    "PAL_REDMON": 0x12,    "PAL_CYANMON": 0x13,    "PAL_PURPLEMON": 0x14,    "PAL_BROWNMON": 0x15,    "PAL_GREENMON": 0x16,    "PAL_PINKMON": 0x17,    "PAL_YELLOWMON": 0x18,    "PAL_GREYMON": 0x19}
    
    TRAINER_CLASSES = ["YOUNGSTER", "BUG CATCHER", "LASS", "SAILOR", "JR.TRAINER♂", "JR.TRAINER♀", "POKéMANIAC", "SUPER NERD", "HIKER", "BIKER", "BURGLAR", "ENGINEER", "JUGGLER", "FISHERMAN", "SWIMMER", "CUE BALL", "GAMBLER", "BEAUTY", "PSYCHIC", "ROCKER", "JUGGLER", "TAMER", "BIRD KEEPER", "BLACKBELT", "RIVAL1", "PROF.OAK", "CHIEF", "SCIENTIST", "GIOVANNI", "ROCKET", "COOLTRAINER♂", "COOLTRAINER♀", "BRUNO", "BROCK", "MISTY", "LT.SURGE", "ERIKA", "KOGA", "BLAINE", "SABRINA", "GENTLEMAN", "RIVAL2", "RIVAL3", "LORELEI", "CHANNELER", "AGATHA", "LANCE"]
    
    OW_SPRITES = "red blue oak bug_catcher slowbro lass black_hair_boy_1 little_girl bird fat_bald_guy gambler black_hair_boy_2 girl hiker foulard_woman gentleman daisy biker sailor cook bike_shop_guy mr_fuji giovanni rocket medium waiter erika mom_geisha brunette_girl lance oak_aide oak_aide rocker swimmer white_player gym_helper old_person mart_guy fisher old_medium_woman nurse cable_club_woman mr_masterball lapras_giver warden ss_captain fisher2 blackbelt guard mom balding_guy young_boy gameboy_kid gameboy_kid clefairy agatha bruno lorelei seel".split()
    
    SONGS = [line.split() for line in open("data/songs.txt").read().split('\n') if line.strip()]
    for song in SONGS:
        for s in song:
            if "Music_"+s not in symbols:
                raise KeyError("Music_{} not in symfile. There could be a typo, or the symbol wasn't exported.".format(s))
    SONG_SOURCES = yaml.load(open("data/song_sources.yaml"))
    
    def random_pokemon(self):
        return choice(self.POKEMON)
    
    def get_move(self, move):
        if move <= self.MAXMOVE and move in self.FAIR_MOVES:
            return move
        elif self.choices['new_moves'] and move in self.NEW_MOVES.keys():
            return self.NEW_MOVES[move]
        else:
            return None
    
    #":All moves;no-hms:No HMs;no-broken:No Dragon Rage, Spore;no-hms-broken:No HMs, Dragon Rage, Spore"
    def opt_move_rules(self, rule):
        if not self.choices['movesets']: return
        if rule in ('no-hms', 'no-hms-broken'):
            self.FAIR_MOVES -= {57, 70, 19, 15, 148}
            self.ATTACKING_MOVES -= {57, 70, 19, 15, 148}
        if rule in ('no-broken', 'no-hms-broken'):
            # SONICBOOM, Dragon Rage, Spore, GUILLOTINE HORN_DRILL FISSURE
            self.FAIR_MOVES -= {0x30, 0x52, 0x93, 0x0c, 0x1e, 0x5a}
            self.ATTACKING_MOVES -= {0x30, 0x52, 0x93, 0x0c, 0x1e, 0x5a}
        return
    opt_move_rules.layer = -5
    
    def opt_new_moves(self):
        self.opt_update_moves()
        self.FAIR_MOVES = self.FAIR_MOVES.copy()
        self.FAIR_MOVES.update(set(self.NEW_MOVES.values()))
        self.ATTACKING_MOVES = self.ATTACKING_MOVES.copy()
        self.ATTACKING_MOVES.update(self.NEW_ATTACKING_MOVES)
    opt_new_moves.layer = -6
    
    #:Keep,randomize:Random,basics:Random basics,three-basic:Random three stage basics,single:Single random (yellow style)
    def opt_starter_pokemon(self, mode):
        #starters = [self.random_pokemon() for i in range(3)]
        if mode == 'randomize':
            starters = [1+self.DEX.index(mon) for mon in sample(self.DEX, 3)]
        elif mode == 'basics':
            families = sample(self.DEX_FAMILIES, 3)
            starters = [1+self.DEX.index(family[0]) for family in families]
        elif mode == 'three-basic':
            three_stage_families = []
            for family in self.DEX_FAMILIES:
                if len(family) == 3: three_stage_families.append(family)
            if len(three_stage_families) >= 3:
                families = sample(three_stage_families, 3)
            else:
                families = [choice(three_stage_families) for i in range(3)]
            starters = [1+self.DEX.index(family[0]) for family in families]
        elif mode == 'single':
            starters = [1+self.DEX.index(choice(self.DEX))]*3
        
        for i, starter in enumerate(starters):
            for offset in self.STARTER_OFFESTS[i]:
                self.rom.seek(offset)
                self.rom.writebyte(starter)
    opt_starter_pokemon.layer = 10
    
    def opt_trainer_pokemon(self):
        rom = self.rom
        rom.seek(self.symbols["TrainerData"])
        while rom.tell() < self.symbols["TrainerDataEnd"]:
            first_byte = ord(rom.read(1))
            if first_byte == 0xff:
                while ord(rom.read(1)) != 0:
                    rom.writebyte(self.random_pokemon())
            else:
                while ord(rom.read(1)) != 0:
                    rom.seek(rom.tell()-1)
                    rom.writebyte(self.random_pokemon())
    opt_starter_pokemon.layer = 1
    
    def opt_yellow_gym_leaders(self):
        # A hack.
        rom = self.rom
        YELLOW_GYM_LEADER_LEVELS = (
            (10, 12,  ), # lowered
            (18, 21,  ), # unchanged
            (28,  0,  0,  ),
            (30, 32, 32,  ),
            (44, 46, 48, 50,  ),
            (48, 50, 54,  0,  ),
            (50, 50, 50,  ),
        )
        YELLOW_GYM_GIOVANNI_LEVELS = (50, 53, 53, 55, 55, )
        rom.seek(self.symbols["BrockData"])
        for levels in YELLOW_GYM_LEADER_LEVELS:
            self.rom.writebyte(0xff)
            for level in levels:
                self.rom.writebyte(level)
                self.rom.readbyte()
            self.rom.writebyte(0x00)
        rom.seek(self.symbols["Giovanni3Data"])
        self.rom.writebyte(0xff)
        for level in YELLOW_GYM_GIOVANNI_LEVELS:
            self.rom.writebyte(level)
            self.rom.readbyte()
    opt_starter_pokemon.layer = 2
    
    def opt_wild_pokemon(self):
        rom = self.rom
        rom.seek(self.symbols["Route1Mons"])
        while rom.tell() < 0xd5b1+22:
            rate = ord(rom.read(1)) # rate
            if rate != 0:
                for i in range(10):
                    rom.read(1)
                    rom.writebyte(self.random_pokemon())

    # ":-;shuffle-no-tm:Shuffle, keep TMs;shuffle:Shuffle;random-no-tm:Random, keep TMs;random:Random;random-key:Random with Key Items"
    def opt_field_items(self, mode):
        items = []
        addresses = []
        tm = mode not in ('shuffle-no-tm', 'random-no-tm')
        for address, item in self.FIELD_ITEMS:
            if self.ITEMS.inv[item] not in self.BANNED_ITEMS and (tm or item not in range(self.ITEMS['TM_01'], self.ITEMS['TM_50']+1)):
                items.append(item)
                addresses.append(address)
        
        if mode in ("random-no-tm", "random", "random-key"):
            new_items = []
            free_items = self.ITEMS.keys()
            if mode != "random-key":
                for item in self.BANNED_ITEMS:
                    free_items.remove(item)
            if not tm:
                for tm in range(1, 51):
                    free_items.remove("TM_{:02}".format(tm))
            for i in range(len(items)-len(new_items)):
                item = choice(free_items)
                new_items.append(self.ITEMS[item])
                if item in self.BANNED_ITEMS:
                    free_items.remove(item)
            items = new_items
        
        shuffle(items)
        for address in addresses:
            self.rom.seek(address)
            self.rom.writebyte(items.pop())
        
    def opt_tms(self):
        rom = self.rom
        rom.seek(self.symbols["TechnicalMachines"])
        self.TMS = sample(self.FAIR_MOVES, 50)
        for move in self.TMS:
            rom.writebyte(move)
    opt_tms.layer = -2
        
    #def opt_ow_sprites(self):
    #    rom = self.rom
    #    rom.seek(0x17ab9) # sprite sets
    #    for i in range(0xa):
    #        for i in range(8):
    #            rom.write(chr(randint(1, 0x3b)))
    #        rom.read(2)
    
    def opt_game_pokemon(self):
        original_151 = not all(self.choices[c] for c in "wild_pokemon trainer_pokemon ow_pokemon starter_pokemon".split())
        families = minidex['evolution_chains']
        
        generation_ranges = (range(  1, 152), range(152, 252), range(252, 387),
                             range(387, 494), range(494, 650), range(650, 723))
        if self.choices['game_pokemon_source_generations']:
            allowed_pokemon = sum((r for gen, r in enumerate(generation_ranges, 1) if gen in self.choices['game_pokemon_source_generations']), [])
        else:
            allowed_pokemon = range(1, 723)
        
        families_ = []
        # this could be rewritten as a generator but meh
        for family in families:
            family_ = []
            for mon in family:
                if mon in allowed_pokemon:
                    family_.append(mon)
            if family_: families_.append(family_)
        
        families = families_
        
        dex_size = min(251 if self.choices['pokedex_size']=="251" else 151, len(allowed_pokemon))
        if original_151:
            dex = self.DEX
            dex_families = self.DEX_FAMILIES
            for family in families:
                for mon in dex:
                    if mon in family:
                        family.remove(mon)
            families = [f for f in families if f]
        else:
            dex = []
            dex_families = []
        popcount = 0
        while True:
            shuffle(families)
            for family in families:
                if family not in dex_families and len(dex) + len(family) <= dex_size:
                    dex_families.append(family)
                    dex += family
                if len(dex) == dex_size: break
            if len(dex) == dex_size: break
            break
        
        self.POKEMON = range(1, len(dex)+1)
        
        types = self.TYPES
        rom = self.rom
        
        self.DEX_FAMILIES = dex_families
        self.DEX = dex
        #print 'Picked {} mons for dex'.format(len(dex))
        
        # sprites
        #self.patch_sprite_loading_routine() # no need to do that, our hack will use
                                             # the bank if it's present, otherwise default behavior
        pokemon_sprite_addresses = []
        banki = self.symbols['SpriteBank1']//0x4000 # 38: first new sprite bank
        # when symfiles are better use BANK(SpriteBank1)
        bank = b""
        for num in dex:
            addresses = []
            addresses.append((banki, len(bank)))
            sprites = b""
            sprites += open('sprites/{:03}.pic'.format(num)).read()
            addresses.append((banki, len(bank)+len(sprites)))
            sprites += open('backsprites_/{:03}.pic'.format(num)).read()
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
                sprites += open('backsprites_/{:03}.pic'.format(num)).read()
                
                bank += sprites
                pokemon_sprite_addresses.append(addresses)
        
        
        rom.seek(banki*0x4000)
        rom.write(bank)
        #print "Wrote sprites (last bank: {})".format(hex(banki))
        
        # base stats
        self.rom.seek(self.symbols["BaseStats"]) # BulbasaurBaseStats
        for i, mon in enumerate(dex):
            data = minidex['pokemon'][mon]
            rom.writebyte(i+1)
            rom.writebyte(data['stats'][0])
            rom.writebyte(data['stats'][1])
            rom.writebyte(data['stats'][2])
            rom.writebyte(data['stats'][5])
            spa, spd = data['stats'][3], data['stats'][4]
            special = {
                'average': (spa + spd) // 2,
                'spa': spa,
                'spd': spd,
                'higher': max(spa, spd),
                'random': choice((spa, spd))
            }[self.choices['special_conversion'] or 'average']
            rom.writebyte(special) # special
            rom.writebyte(types[data['type0']])
            rom.writebyte(types[data['type1']] if data['type1'] else types[data['type0']])
            rom.writebyte(data['catch_rate'])
            rom.writebyte(min(data['exp_yield'], 255))
            rom.writebyte(0x77) # sprite dimensions
            rom.writeshort(pokemon_sprite_addresses[i][0][1] + 0x4000)
            rom.writeshort(pokemon_sprite_addresses[i][1][1] + 0x4000)
            
            
            if self.choices['movesets']:
                moves = [0, 0, 0, 0]
                if self.choices['force_four_moves']:
                    num_moves = 4
                else:
                    num_moves = sum([level == 1 for level, move in data['learnset']])
                for movei in range(min(num_moves, 4)):
                    if movei == 0 and self.choices['force_attacking']:
                        move = choice(self.ATTACKING_MOVES)
                    else:
                        move = choice(self.FAIR_MOVES)
                    while move in moves:
                        move = choice(self.FAIR_MOVES)
                    moves[movei] = move
            else:
                moves = []
                for level, move in data['learnset']:
                    if level == 1 and self.get_move(move):
                        moves.append(self.get_move(move))
                moves = moves[-4:]
                if not moves:
                    moves.append(0x21) # Tackle XXX
                while len(moves) < 4:
                    moves.append(0)
            
            assert len(moves) == 4
            for move in moves:
                rom.writebyte(move)
            
            rom.writebyte({1:5, 2:0, 3:4, 4:3, 5:6, 6:7}[data['growth_rate']])
            
            if self.choices['movesets']:
                for x in range(7): # TMHM
                    rom.writebyte(randint(0, 255))
            else:
                tm_compatibility = [(move if move <= self.MAXMOVE else self.NEW_MOVES.inv[move]) in data['moveset'] for move in self.TMS+self.HMS]
                for j in range(7):
                    byte = 0 if j != 6 else 0xff
                    for k in range(8):
                        if j*8+k < len(tm_compatibility) and tm_compatibility[j*8+k]:
                            byte |= 1 << k
                    rom.writebyte(byte)
            
            rom.writebyte(pokemon_sprite_addresses[i][0][0])
        
        # evos moves
        evo_move_pointers = []
        self.rom.seek(self.symbols['Mon001_EvosMoves'])
        for dexnum in range(1, len(dex)):
            evo_move_pointers.append(rom.tell())
            num = dex[dexnum - 1]
            # evolutions
            for evolution in minidex['pokemon'][num]['evolutions']:
                if evolution['evolved_species'] not in dex: continue
                trigger = {'shed': 'level-up'}.get(evolution['trigger'], evolution['trigger'])
                if trigger == "trade" and self.choices['change_trade_evos']:
                    trigger = 'level-up'
                    evolution['minimum_level'] = 42
                
                rom.write(chr(self.EVOLUTION_METHODS[trigger]))
                if trigger == 'level-up':
                    rom.write(chr(evolution['minimum_level'] if evolution['minimum_level'] else 30))
                elif trigger == 'use-item':
                    rom.write(chr(self.EVO_ITEMS.get(evolution['trigger_item'], self.EVO_ITEMS['moon-stone'])))
                    rom.writebyte(1)
                elif trigger == 'trade':
                    rom.writebyte(1)
                rom.writebyte(1+dex.index(evolution['evolved_species']))
            rom.writebyte(0)
            # moves
            for movei, m in enumerate(minidex['pokemon'][num]['learnset']):
                level, move = m
                if self.choices['movesets']:
                    if level != 1 and (movei <= 2 or movei % 2 == 0):
                        rom.writebyte(level)
                        rom.writebyte(choice(self.FAIR_MOVES))
                else:
                    if level != 1 and self.get_move(move):
                        rom.writebyte(level)
                        rom.writebyte(self.get_move(move))
            rom.writebyte(0) # end moves
        # TODO we still need an assert here!
        #assert rom.tell() < 0x3c000, hex(rom.tell())
        
        rom.seek(self.symbols["EvosMovesPointerTable"])
        for evo_move_pointer in evo_move_pointers:
            rom.write(struct.pack(b"<H", evo_move_pointer % 0x4000 + 0x4000))
        
        self.rom.seek(self.symbols["MonsterNames"]) # MonsterNames
        
        for num in dex:
            self.write_string(minidex['pokemon'][num]['name'].upper(), 10)
        
        # menu icons
        self.rom.seek(self.symbols["MonPartyData"]) # what a bad name
        for i in range((len(dex)+1)/2):
            self.rom.writebyte( ((menu_icons[dex[i*2]]   if i*2  <len(dex) else 0) << 4) |
                                 (menu_icons[dex[i*2+1]] if i*2+1<len(dex) else 0))
        
        # Write palettes
        self.rom.seek(self.symbols["MonsterPalettes"]+1)
        for i in range(len(dex)):
            self.rom.writebyte(self.PALS[monpals[dex[i]-1]])
        
        # cries
        
        self.rom.seek(self.symbols["CryHeaders"])
        for i, mon in enumerate(self.DEX):
            if mon <= 251:
                self.rom.write(self.EXISTING_CRIES[mon-1])
            else:
                self.rom.writeshort(randint(0, 0x43)) # base cry
                self.rom.writebyte(randint(0, 0xff))  # pitch
                self.rom.writebyte(randint(0, 0xff))  # echo
                self.rom.writeshort(randint(0, 0x80)) # length
    opt_game_pokemon.layer = -1
    
    def opt_movesets(self):
        if self.choices['game_pokemon']: return
        rom = self.rom
        for i in range(150):
            rom.seek(self.symbols["BaseStats"] + 15 + (28 * i))
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
            
            rom.seek(self.symbols["EvosMovesPointerTable"] + (2 * (1+i)))
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
        self.TYPES = self.TYPES.copy()
        self.TYPES.update({'dark': 0x1b, 'steel': 0x09, 'fairy': 0x1c})
        # TODO this needs to be per-instance!  we're updating the class
        # TYPES dictionary now which is wrong
        
        # We don't need to update the type names any more, they're
        # in pokered-randomizer.
        
        self.rom.seek(self.symbols["TypeEffects"])
        for type0, type1, factor in type_efficacy:
            if factor != 100:
                self.rom.writebyte(self.TYPES[type0])
                self.rom.writebyte(self.TYPES[type1])
                self.rom.writebyte({0:0x00, 50: 0x05, 200: 0x20}[factor])
        self.rom.writebyte(0xff)
    opt_update_types.layer = -5
        
    def opt_update_moves(self):
        self.rom_flags['update_moves'] = True
        
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
        for bank, sprites in ((0x3e, self.OW_SPRITES[:42]), (0x3f, self.OW_SPRITES[42:])):
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
    
    def opt_soundtrack(self):
        self.rom.seek(self.symbols["Music"])
        for songs in self.SONGS:
            if self.choices['soundtrack_sources']:
                songs_ = []
                for song in songs:
                    for source in self.choices['soundtrack_sources']:
                        if song in self.SONG_SOURCES[source]:
                            songs_.append(song)
                if not songs_: songs_ = [songs[0]]
                songs = songs_
            song = "Music_"+choice(songs)
            self.rom.writebyte(self.symbols[song] / 0x4000)
            self.rom.writeshort((self.symbols[song] % 0x4000) + 0x4000)
    
    def opt_pitches(self):
        self.rom.seek(self.symbols["SongTranspositions"])
        for i in range(46):
            # lazy
            self.rom.writebyte(int(triangular(-4, 4, 0)))
    
    def opt_instant_text(self):
        self.rom_flags['instant_text'] = True
                
    def finalize(self):
        self.rom.seek(self.symbols['TitleMons'])
        for mon in sample(self.POKEMON, 16):
            self.rom.writebyte(mon)
        
        intromon = self.random_pokemon()
        self.rom.seek(self.symbols['TextCommandSoundsIntroMon'])
        self.rom.writebyte(intromon)
        self.rom.seek(self.symbols['OakSpeechPokemon'])
        self.rom.writebyte(intromon)
        
        
        if self.debug:
            self.rom_flags['debug'] = True
        
        assert len(self.ROM_FLAGS) <= 8
        byte = 0x00
        for i, flag in enumerate(self.ROM_FLAGS):
            if self.rom_flags[flag]:
                byte |= 1 << i
        self.rom.seek(0x00ff)
        self.rom.writebyte(byte)
            
        
        self.rom.seek(self.symbols['TitleScreenText'])
        if not self.debug:
            text = """                    
Randomizer options  
are returning soon! 
                    
This ROM comes from:
http://tinyurl.com  
         /pkmnrandom
                    
(commit:)           """
        else:
            text = """                    
This is a DEBUG ROM.
Do not distribute!  
                    
Get your ROM at:    
http://tinyurl.com  
         /pkmnrandom
                    
(commit:)           """
        text = text.replace('\n', '')
        for commit in repo.iter_commits('master'):
            if not commit.message.startswith("Merge "):
                break
        
        text += commit.hexsha[0:20]
        text += "@"
        '''text = ""
        text += "{:20}".format("Randomizer options:")
        option_strings = []
        for choice, value in self.choices.items():
            ot = ""
            if value:
                ot += choice
                if value != True:
                    ot += ": "+str(value)
                option_strings.append(ot)
        text += ", ".join(option_strings) + "@"
        text = text.replace('_', '-').replace('-pokemon','<>')'''
        self.write_string(text)
    
