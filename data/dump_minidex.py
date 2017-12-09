from pokedex.db import connect, tables, util
from tqdm import tqdm
session = connect()

import yaml

VERSION = "ultra-sun-ultra-moon"

version = session.query(tables.VersionGroup).filter(tables.VersionGroup.identifier==VERSION).one()

mons = {}

pokemon_query = session.query(tables.PokemonSpecies).order_by(tables.PokemonSpecies.id)

for pokemon_species in tqdm(pokemon_query, total=pokemon_query.count()):
    data = {}
    pokemon = pokemon_species.default_pokemon
    data['id'] = pokemon_species.id
    data['name'] = pokemon_species.name
    data['catch_rate'] = pokemon_species.capture_rate
    data['growth_rate'] = pokemon_species.growth_rate.id
    data['genus'] = pokemon_species.genus
    data['evolutions'] = []
    for evolved_pokemon_species in pokemon_species.child_species:
        pokemon_evolution = evolved_pokemon_species.evolutions[0]
        data['evolutions'].append({'trigger': pokemon_evolution.trigger.identifier,
                                   'minimum_level': pokemon_evolution.minimum_level,
                                   'trigger_item': pokemon_evolution.trigger_item.identifier if pokemon_evolution.trigger_item else None,
                                   'evolved_species': pokemon_evolution.evolved_species_id})
            
    data['exp_yield'] = pokemon.base_experience
    data['height'] = pokemon.height
    data['weight'] = pokemon.weight
    data['learnset'] = []
    for pokemon_move in session.query(tables.PokemonMove).filter(tables.PokemonMove.pokemon==pokemon, tables.PokemonMove.version_group==version, tables.PokemonMove.level > 0):
        data['learnset'].append([pokemon_move.level, pokemon_move.move_id])
    data['learnset'].sort()
    moveset = set()
    for pokemon_move in session.query(tables.PokemonMove).filter(tables.PokemonMove.pokemon==pokemon).all():
        moveset.add(pokemon_move.move_id)
    data['moveset'] = list(moveset)
    data['stats'] = []
    for i in range(6):
        data['stats'].append(pokemon.stats[i].base_stat)
    data['type0'] = pokemon.types[0].identifier
    data['type1'] = pokemon.types[1].identifier if len(pokemon.types) > 1 else None
    
    mons[data['id']] = data
    #print data['id'], data['name']
    
print 'Got pokemon'

evolution_chains = []
for evolution_chain in session.query(tables.EvolutionChain):
    s = [species.id for species in evolution_chain.species]
    evolution_chains.append(s)
    
print 'Got evolution chains'

open('minidex.yaml', 'w').write(yaml.safe_dump(
    {'pokemon': mons,
     'evolution_chains': evolution_chains}))  # safe_dump to avoid !!python/unicode
