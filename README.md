randomizer
===
Central repository for Sanqui's Online randomizer, to-be randomized.games.

License
---
* Do not run this in production (i.e., host it) without my permission.
* Do not use the sprites without the express permission of their authors.

State of the Sanqui Randomizer (2016)
---

Hi! I made the Online Pokémon randomizer like two years ago at this point. Unfortunately, I haven't brought myself to work on it in a long time, which I feel really bad about. If anybody is perhaps interested in taking over or maintaining it, here's everything you need to know.

### State of the Randomizer

Sadly, when I stopped working on it, the randomizer was left in a direly unfinished state. There are a few bugs that were never fixed, and the structure isn't sustainable.

What I had planned was create a rewrite with a whole new architecture that would make it easy to extend the randomizer, but sadly I never got too far.

I simply don't have the time or will to create the new version at the moment.

In the short term, it might be worth shaping up the current version, but I'd really love to see the rewrite happen... anyway, here's a description of how current randomizer works in all, in case you're interested in working on it. I'm going to cover every part of the randomizer.

### The data

#### Pokémon sprites
Although only graphics, the sprites are arguably one of the most important things about the randomizer, because without them, it would be no fun to play at all.

What stood at the initial resource for the randomizer's sprites was a sheet of gen 1 styled Pokémon sprites that was created or collected by /vp/. Since it claimed anything can be done with the sheet without credit, I used it. Only later I learned that some sprites were put on it without the knowledge of their authors.

The sprites were closer to "shitty MS Paint" style than "Gen 1 style", so me and my friend Behold3r started working on replacing them with better sprites available on DeviantArt and other sites - always making sure to ask for permission from the artist. I believe about 2/3 of the sprites were replaced. I also drew some of the new sprites myself :)

The /vp/ sheet was also lacking Gen 6 Pokémon entirely, so we there was a bit of a team effort to draw new sprites for the randomizer.

Unlike the front sprites, there wasn't a good collection of backsprites. A little over half Pokémon got backsprites until now, the ones that don't have the frontsprite, cropped to the top right corner.

I always put a lot of value in making the game look "authentic", so to speak. I wanted sprites to be consistent to some extent with the original gen 1 look, which is why I kept the original palettes, backsprite sizes, and forbade the use of gen 2 sprites. Some guidelines for new sprites could be made.

I've been asked over the years to give away the sprites. I've been kind of dodging that issue, not for being selfish, but due to the vague licensing most of them have. Some are leftovers from the /vp/ sheet, with authors unknown, and for many, I've gotten exclusive license for randomizer usage, and no more. So that's probably how it's going to stay.

My friend, Behold3r, has a sheet with all the sprites, with one layer per author, and used to export it after each update. I can get it from him.

The shell script, convert_sprites.sh, downloads the sprite sheet, splits it up, generates backsprites, palettes, and compresses the sprites for use in the disassembly. It uses imagemagick. It requires gfx.py and pic.py from pokemon-reverse-engineering-tools to be in the same directory. Possibly old versions too.

#### Overworld sprites
My randomizer features randomized (actually shuffled) overworld sprites, which is certainly a fun feature. What most people probably don't realize is that about half the sprites in Red and Blue actually lack walking variants. All of those were done for my randomizer at some point by Reimu. They're in gfx/ow_sprites/ and probably end up in the ROM by some terrible black magic.

#### Pokédex

The Pokédex data is stored in a file called `minidex.yaml`. It was exported as a one-off from the open-source pokedex[1] database of veekun.com at the time of Pokémon X and Y, and uses learnsets from then. I will find the script that exported it. It should be possible to update to OR/AS immediately.

#### Music

The new songs (like gen 4 demixes) were mainly arranged by FroggestSpirit. He has done many more songs since then, I just haven't added them to the randomizer. The songs need to be in pokered-randomizer, and can be gotten from CrystalComplete, but check with FroggestSpirit. They work with the Gen 2 sound engine.

`data/song_sources.yaml` contains information on where each song came from.

`data/songs.txt` contains possible song substitutions for each song from the original game.

#### Other data

There's some other data that was mostly done as one-offs. It should be self-explanatory, let me know if you're missing something though.

### The code

Now this is scary!

The randomizer could be split roughly into four major parts... The pokered-randomizer disassembly, the PokemonRed randomizer class, the randomizer code, and the website frontend. Let me go over these.

#### [pokered-randomizer](https://github.com/Sanqui/pokered-randomizer)
pokered-randomizer is an outdated fork of pokered with new features used in the randomizer. Contrary to logic, the ROM is built *first*, and the randomizer script works on the resulting binary. This is probably the biggest Achilles' heel. It allowed the randomizer to generate a ROM pretty fast, but the actual process of modifying data in the binary is extremely error prone...

I'm going to try and list the major changes done in this fork.

* Pokémon and Trainer IDs were successfully decoupled, meaning the game supports up to ~253 Pokémon (for the sake of simplicity, I went with 251). This has been done many times over and could probably be redone easily and better.
* The sound engine from pokecrystal was backported. This wasn't a trivial task, but not exactly complicated either. It allowed for use of real cries for Gen 2 pokémon, as well as all the gen 2 music, and new music that used the format. Danny-E has reproduced my commits against clean pokered at some point, as well as done some further fixes which I'm not sure if I cherry-picked.
* The sound engine gained support for pitch transposition (lol)
* Around 40 new moves were added, as well as old moves having their values changed to current values. This involved adding some new move effects, as well as animations for each of the new moves. This change is optional and set with a bitflag by the randomizer.
* Instant text was added, and toggled by a bitflag.
* Erratic and Fluctuating EXP groups were added.
* Probably more misc. stuff, as well as stuff being moved around for various reasons.

pokered-randomizer is included under the randomizer as a submodule. It needs to be bumped when updated.

#### PokemonRed
The randomizer contains a Game class. The class represents a game able to be randomized. PokemonRed is the only relevant subclass here. An instance of PokemonRed is a Red ROM, ready to be randomized by method calls, such as opt_starter_pokemon(), opt_wild_pokemon(), etc. You don't generally want to call those manually. Instead, you set the options in the choices dictionary, then run the produce() method, which respects priority. Sigh... Okay.

So when you look at the PokemonRed class, you'll see a few sections. First, a few constants relevant to the randomizer are defined. What follows is the form used by the website. It's defined using wtforms. This form is important, because the input names are used directly as methods on this class, and the option is passed as the argument. So even the possible parameters are defined here.

Afterwards, a lot of constants are defined through various ways - hardcoded, calculated from symbols, or even read from the ROM at start time. Honestly, it's pretty awful stuff.

Next, after auxillary methods, the methods for each randomization option are defined. Each of these methods begin with `opt_` and perform their operation directly on the ROM in the works. Sometimes, things need to be done in a certain order, such as, if certain moves are banned (like Dragon Rage), that needs to be set before Pokémon learnsets or TM contents are generated. This is done using the `.layer` variable on the methods themselves.

The nastiest method here is `opt_game_pokemon()`, which is responsible for putting all the new Pokémon in. It actually works on an evolutionary family basis, pulling in family after family until the dex is full. (I fear that the routine at the heart of this is broken and may result in an infinite loop, but I haven't seen it happen yet.) Then it writes in the Pokémon data proper, base data, learnsets and evolutions, pics, etc.

There's of course many other routines here, some of them pretty scary in how they write in data without any real bounds checking and such.

#### randomizer
The randomizer, at the higher level, is pretty straightforward. It does some sanity checking on the options and has some methods to make working with the ROM easier. It also defines the games, which, besides Pokémon Red, happen to include Pokémon TCG and Telefang. Those are, however, incredibly basic in what they do, compared to the monster that is Pokémon Red. The idea was, of course, to support many more games over time, but it never became relevant.

#### app
The app is a dynamic website coded with Flask. There's some javascript in the frontend, written with jQuery (I swear that in 2014, it was still relevant), mainly to handle the forms and do an AJAX request for the ROM.

The website handles filename sanitation, as well as minute long cooldowns for IPs (too short? you decide). That's about.. it, really. I had it deployed with uwsgi_python behind nginx.

### The Future of the Randomizer
I'm hesistant to straight up open source the whole thing. I'm not proud of it. It's not well written. I don't really want people to use it. But there's no way I'll be working on it myself any further.

If anybody wants to give a shot at fixing the few bugs or adding some features it direly needs, good luck... I'll be giving repo access to anybody who asks.

I've learned from the way I've done the randomizer and I hope that with this overview, you've learned something as well.

My plans for the actual replacement of the randomizer were, of course, grandiose. It wasn't meant to happen. But here's an overview of what I had planned, and what I'd still like to see one day.

#### Crowdsprite
Crowdsprite was a website which was to hold all the user-contributed data for the randomizer. This is primarily sprites. Gone would be coordinating with people over Skype, instead everybody could instantly see what sprites are done, which need replacement, and which are missing. Sprites could be validated for dimensions and the color palette, and replacements could be done and approved easily.

The plan was to extend Crowdsprite beyond sprites. People could submit text (e.g., for trainer names), as well as some more dreamy things, like maps or fakemons. It was fun to think about.

#### Randomizer 2.0
The next version of the randomizer would be tightly coupled with the relevant disassembly, building a ROM for each randomization request anew. Randomization would still be done in a Python script, which would export a huge list of constants. I was working on array support in rgbds, so that various stuff could be exported as lists, and easily iterated over in the source code. Could make do with just constants, though, it'd still be much better than modifying the binary.

#### Frontend
The frontend is easy, of course, but the current version isn't optimized for mobile at all. So the important bit here would be to make it responsive. The inputs could be made nicer or more dynamic, but that's not a priority.

#### Future games
Pokémon Crystal was the next step. With Crowdsprite under my belt, I figured sprite collection would be a pleasant activity. I also had some ideas for other games, like MMBN, but I'm sure anybody could come up with a ton of games they'd like to see randomized. The idea was to make it fairly easy to add new games, though.

### What can be done?
Is there any interest in fixing the current version of the randomizer? Working on a new one? I'm sorry, but I can't do the lion's share of the work like I had planned.

As I've said before: if anybody with coding skills wants to take over the project, I can offer advice and consultation. It doesn't have to be in Python. I'd just love to see it happen somehow, and I'm sure there are many other people who would.

Feel free to ask me anything or brainstorm ideas. Also feel free to ask for access to the repo.
