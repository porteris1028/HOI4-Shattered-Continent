# Shattered Continent (HoI4 mod) — v0.2.0

**Spring 1946.** D-Day stalled, the Soviets stalled in Poland, and America used its atomic bombs on Berlin and Munich instead of Japan. A chain reaction of collapse followed. Now the USA, Japan and a rising China rule the world, while Europe is a wasteland of warlords, free cities, Cossack hosts and SS fortresses.

- **Setting and story:** [LORE.md](LORE.md)
- **Every nation at a glance:** [docs/NATIONS.md](docs/NATIONS.md) (generated)

The mod has three pillars:
1. **A destroyed Europe**: 26 new nations, plus a dangerous No Man's Land.
2. **More provinces in Europe**: a denser map, so warlord movement means something.
3. **Roaming warlords**: nomadic armies that must keep moving to feed themselves.

---

## 1. Installing for testing

1. Copy `shattered_continent/` into your HoI4 mod folder:
   - Windows: `Documents/Paradox Interactive/Hearts of Iron IV/mod/`
   - Linux: `~/.local/share/Paradox Interactive/Hearts of Iron IV/mod/`
2. In `mod/` (next to the folder, **not inside it**), create `shattered_continent.mod` with the contents of `descriptor.mod` plus:
   ```
   path="mod/shattered_continent"
   ```
3. Enable it in the launcher and start the **"The Shattered Continent"** bookmark.
4. Launch with `-debug` and check `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log` after every test.

`supported_version` is `1.16.*`. Change it to match your game version if the launcher complains.

---

## 2. Workflow: how to edit the mod

Most content is **generated** from three files in `setup/`. Edit those, run the tools, and never hand-edit generated files (they start with a `# GENERATED` line).

| To change… | Edit | Then run |
|---|---|---|
| A nation (name, leader, ideology, army, flag, description…) or add a new one | `setup/nations.toml` | `python3 tools/build_nations.py` |
| Who owns which states in 1946 | `setup/state_assignments.csv` | `python3 tools/build_setup.py` |
| Blast sites, fallout and extra-dangerous areas | `setup/danger_zones.csv` | `python3 tools/build_setup.py` |
| Which vanilla countries survive | `common/scripted_triggers/sc_setup_triggers.txt` | — |

The tools need **Python 3.11+** and **Pillow** (`pip install pillow`).

### First-time setup (needs your game folder)
```
# 1. Make sure none of our 27 tags clash with the game's own tags
python3 tools/check_tags.py "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"

# 2. Look up state IDs and fill them into the two CSVs
python3 tools/list_states.py "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV" --search tyrol

# 3. Generate the setup script
python3 tools/build_setup.py
```
> ⚠️ **The bookmark isn't playable until the state IDs are filled in.** Until then, the new nations own no land and don't exist. The CSVs already list every planned region, so you only need to add the numbers.

To use real flag art, put an 82×52 TGA at `gfx/flags/custom/<TAG>.tga` and re-run `build_nations.py`.

---

## 3. World setup at game start

When the 1946 bookmark loads (once, from `on_startup`):

1. Every European state **not owned by a spared nation** (ENG, IRE, SWI, SWE, SPR, POR, TUR) goes to **No Man's Land** (`WST`). Germany, France, Italy, the European USSR and the rest disappear.
2. States are handed out from `state_assignments.csv`. This includes **Japan's gains on the Pacific coast** and the **Siberian generals**.
3. Anything the USSR still holds east of the Urals becomes empty taiga (No Man's Land), and the USSR is gone.
4. Every wasteland state gets a random **danger** (10–60), then the blast zones are applied.
5. Armies spawn, warbands pitch camp, the **Black Order** gets its devotion, and **Britain's uprisings** begin.

USA, Japan and China keep their vanilla setup for now (see the roadmap).

---

## 4. Mechanics

### 4.1 No Man's Land danger
Every wasteland state has **danger** from 0 to 100: raiders, mines, wild packs, collapsed cities.

| Rule | Detail |
|---|---|
| Rising danger | +1 per month in unclaimed land, up to 80 |
| **Irradiated** zones | Berlin and Munich plus nearby states (`danger_zones.csv`). Danger stays at 70–100, there's **no forage**, and any warband that camps there gets **Radiation Sickness** for 180 days (the Ashen Riders get a milder version) |
| Border raids | countries next to wasteland with danger above 60 have a monthly chance of a **Raiders from the Wastes** event |
| Ambushes | warbands entering a state may be **ambushed**: 10% chance at low danger, 25% at medium, 50% at high. There's also a 15% chance of finding a **supply cache** |
| Forage | wasteland with danger above 60 has 20 less forage |

**"The Wastes" decisions** (any country that borders wasteland):
- **Sweep [state]**: costs 20 PP and 500 manpower, and lowers that state's danger by 30.
- **Settle [state]**: available once danger is below 25. Costs 50 PP, and the state becomes yours after 45 days. This is how settled nations expand into the wasteland.

### 4.2 Roaming warbands
Applies to Volkov's Host, the Lost Legion, the Ashen Riders, the Po Valley Brigands and the Carpathian Wolves.
- The warband's camp (its capital) has **forage**. Every month the warband eats 15 forage, which becomes **supplies**, and upkeep costs 8 supplies.
- If supplies fall **below 20**, the warband is Starving. **At 0**, men desert. **At 70 or more**, it is Well-Fed.
- **March** to a neighbouring wasteland state: takes 14 days and costs 10 supplies. The old camp goes back to the wastes.
- **Raid** a neighbouring state: +20 supplies, but that land is ruined.
- **Put Down Roots**: settle permanently and become a normal nation.

### 4.3 SS holdouts
| Nation | Playstyle | Mechanics |
|---|---|---|
| **Alpenfestung** | Defence | *Mountain Redoubt* spirit: defence and dig-in bonuses, an attack penalty. Upgrade it twice with **Fortify the Passes**. **Call the Faithful** for manpower. |
| **Festung Nord** | Expansion | *Northern Offensive*: attack and speed bonuses, war goals justified 50% faster. **Plan the Invasion of [country]** gives a war goal against any European neighbour or coastal country. **Colonise** lets it claim wasteland with danger up to 50, where others are limited to 25. |
| **Ordensstaat Banat** | Fanaticism | *Fanatical Order*: big attack, morale and war-support bonuses, but low stability. **Loses stability every month at peace.** **Declare Crusade** gives a cheap war goal on any neighbour. **Blood Levy** trades stability for manpower. |
| **The Black Order** | Cult (Himmler) | **Devotion** (0–100) falls by 3 every month. It scales stability from −15% to +15% and war support from 0% to +20%. Below 20, **Heresy** events fire. Raise it with **Rites**, **Visions** (a gamble) and **Induct New Knights**. |

### 4.4 Britain: "A Kingdom Divided"
Two timed missions start at game start:
- **Red Clydeside** (270 days): crack down (costs war support and manpower) or negotiate (socialists grow). If the timer runs out, a **communist civil war** breaks out.
- **Irish Rising** (365 days): reinforce Ulster (costs 10k manpower) or let it go peacefully. If the timer runs out, **Ulster goes to Ireland** anyway, with a stability hit.

---

## 5. Expanding the provinces in Europe

The plan is to roughly double land-province density between the Pyrenees and the Urals. This means editing the game's map files, so copy them into `shattered_continent/map/` first.

| File | What to do |
|---|---|
| `map/provinces.bmp` | split provinces. Each needs a unique RGB colour. No anti-aliasing |
| `map/definition.csv` | one line per new province. IDs must stay sequential |
| `history/states/*.txt` | add the new province IDs to their state |
| `map/strategicregions/*.txt` | add the new province IDs to their region |
| `map/buildings.txt`, `map/unitstacks.txt` | regenerate with the in-game Nudger |
| `map/adjacencies.csv`, `railways.txt`, `supply_nodes.txt` | fix wherever the splits touch them |

```
python3 tools/province_tool.py density  shattered_continent/map 2400 300 3600 1100   # measure
python3 tools/province_tool.py newcolors shattered_continent/map 50 land plains 1      # new colours
python3 tools/province_tool.py check    shattered_continent/map                        # validate
```
Split one region at a time and test in between.

---

## 6. First in-game test checklist

These were written without the game available. Check `error.log` for:

- [ ] Tag clashes (`check_tags.py`). Cossack and Siberian tags are the most likely to clash with DLC releasables.
- [ ] `on_monthly` fires per country.
- [ ] `create_unit` without a location spawns at the capital.
- [ ] `set_variable_to_random` works in state scope (used for starting danger).
- [ ] Missions `activate_mission` / `days_mission_timeout` behave as expected for ENG.
- [ ] State- and country-targeted decisions show the right targets (and aren't slow with no `targets` list).
- [ ] Icon names: decision categories (`generic_military`, `generic_political_actions`), decisions, idea pictures, dynamic-modifier icons. A missing icon only shows up blank.
- [ ] Variable-valued dynamic modifier for Black Order devotion.
- [ ] Sub-ideology names (`oligarchism`, `leninism`, `stalinism`, `anarchism`) exist in your version.
- [ ] Units in the abandoned camp get moved to the new camp when a warband marches.
- [ ] The WST AI doesn't build or recruit.

---

## 7. Roadmap
- **v0.3**: fill in the state IDs, run the first in-game test, fix `error.log`.
- **Focus trees**: start with the four SS states, Volkov's Host and the Home Army Republic.
- **USA / Japan / China**: 1946 situation (wars, alliances), and US relief or intervention in Europe.
- **Warband v2**: tribute from weak neighbours, seasons, camp followers, smarter AI marching.
- **Wasteland v2**: decontamination, radiation spreading on the wind, wasteland "tribes" to recruit.
- **Map**: province expansion, starting with Poland and Germany.
- **Art**: real flags, leader portraits, event pictures.

---

## Folder map
```
shattered_continent/
├── README.md  LORE.md  descriptor.mod
├── setup/                       ← EDIT THESE
│   ├── nations.toml             all nations
│   ├── state_assignments.csv    1946 borders
│   └── danger_zones.csv         blast sites / fallout
├── tools/
│   ├── build_nations.py         nations.toml → countries, history, leaders, names, flags, armies
│   ├── build_setup.py           CSVs → setup script
│   ├── check_tags.py            tag clash check against the game
│   ├── list_states.py           look up vanilla state IDs
│   └── province_tool.py         map checker / colours / density
├── common/
│   ├── bookmarks/  characters/  countries/  country_tags/
│   ├── decisions/               warband, wastes, factions (+ categories/)
│   ├── dynamic_modifiers/       starving, well-fed, radiation, devotion
│   ├── ideas/                   national spirits
│   ├── on_actions/              startup + monthly ticks
│   ├── scripted_effects/        setup, warband, danger, factions (+ generated)
│   └── scripted_triggers/       spared nations, march/raid/wastes rules
├── events/                      warband, danger, cult
├── gfx/flags/                   generated (custom art in gfx/flags/custom/)
├── history/countries/           generated
├── localisation/english/        mechanics text + generated nation names
└── docs/NATIONS.md              generated nation overview
```
