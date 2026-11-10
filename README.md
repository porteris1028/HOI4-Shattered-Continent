# Shattered Continent (HoI4 mod) — v0.1.0

**Spring 1946.** The war never really ended. Berlin, Paris, Rome, London and Moscow are gone, and so are the governments that ruled from them. Warlords ride from valley to valley, free cities hide behind their walls, and in the mountains the last SS fortresses wait for orders that will never come.

The mod has three pillars:

1. **A destroyed Europe**: the major powers are removed and the map is filled with warlords, free states and SS holdouts.
2. **More provinces in Europe**: a denser map, so small warlord states and their movements actually mean something.
3. **Roaming warlords**: nomadic armies that have to keep moving their camp across Europe to feed themselves.

---

## 1. Installing for testing

1. Copy the `shattered_continent` folder into your HoI4 mod folder:
   - Windows: `Documents/Paradox Interactive/Hearts of Iron IV/mod/`
   - Linux: `~/.local/share/Paradox Interactive/Hearts of Iron IV/mod/`
2. Next to the folder (in `mod/`, **not inside** the folder), create `shattered_continent.mod` with the contents of `descriptor.mod` plus one extra line:
   ```
   path="mod/shattered_continent"
   ```
3. Enable it in the launcher's playset and start the **"The Shattered Continent"** bookmark.
4. Launch with `-debug` (Steam → HoI4 → Properties → Launch options) and read `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log` after every test.

`supported_version` is set to `1.16.*`. Change it to match your game version if the launcher complains.

---

## 2. What is in v0.1

| Area | Files | Status |
|---|---|---|
| 7 new country tags | `common/country_tags`, `common/countries`, `history/countries` | ✅ written |
| Fictional leaders | `common/characters/sc_characters.txt` | ✅ written |
| 1946 bookmark | `common/bookmarks/sc_1946.txt` | ✅ written |
| World setup (wipe Europe → hand out states) | `common/on_actions`, `common/scripted_effects/sc_setup_effects.txt` | ✅ written, **needs state IDs** |
| Warband mechanic | `sc_warband_*` effects, triggers, decisions, modifiers, events | ✅ first version |
| Localisation | `localisation/english/sc_l_english.yml` | ✅ written |
| Placeholder flags | `gfx/flags/` | ✅ generated |
| Province expansion | `map/` (not yet created) | 🔜 workflow + tools ready |

> ⚠️ **Not yet tested in game.** This was written without access to the game, so expect a few `error.log` lines on first launch (icon names, a modifier name, an effect argument). The checklist in section 7 lists the spots most likely to need fixing.

### Before the bookmark is playable
The new nations don't own any land until you fill in **`setup/state_assignments.csv`**. Look up vanilla state IDs with:
```
python3 tools/list_states.py "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV" --search tyrol
```
Put the IDs in the CSV, then run:
```
python3 tools/build_setup.py
```
That regenerates `common/scripted_effects/sc_generated_setup_effects.txt`. **Edit the CSV, never the generated file.** The CSV is also a handy document for workshopping the starting borders.

---

## 3. How the world is set up

When the 1946 bookmark starts (`on_startup`, run once, guarded by a global flag):

1. **Every state in Europe is handed to `WST` "No Man's Land"**, a placeholder owner with zero industry, manpower and research. Vanilla countries that are left with no land (GER, FRA, ITA, ENG…) disappear. Countries with land outside Europe survive as rumps (the USSR in Siberia, colonies, the USA). Whether that's what we want is an open question below.
2. States from the CSV go to the new nations.
3. Starting divisions spawn at each capital.
4. Roaming warlords get their first camp.

This approach means **we never have to copy and edit hundreds of vanilla `history/states` files**. Once the map is expanded (section 5) we'll probably switch to proper state history files, because the new map will need its own state files anyway.

---

## 4. The Warband mechanic (roaming warlords)

Any country with the flag `sc_nomadic` is a roaming warlord (currently **HST** Volkov's Host and **LGN** the Lost Legion).

```
         ┌───────── every month ─────────┐
 camp FORAGE ──(-15)──► warband SUPPLIES ──(-8 upkeep)──►
         │                                  │
   forage hits 0                     supplies < 20 → Starving (org/attack penalties, pop loss)
         │                           supplies = 0  → Desertion event (−manpower)
         ▼                           supplies ≥ 70 → Well-Fed (org/speed bonus)
   MARCH to a neighbouring empty state (14 days, −10 supplies)
   → old camp goes back to No Man's Land and is "raided" for a year
```

| Concept | Where it's stored | Notes |
|---|---|---|
| **Camp** | the country's capital | the warband owns only its camp, plus any cored or `sc_holdfast` states |
| **Forage** | state variable `sc_forage` | 60 base, +20 for populous states, +20 more for big cities |
| **Supplies** | country variable `warband_supplies` (0–100) | shown in the decision category |
| **Raided** | state flag `sc_raided` | a raided state has no forage for 365 days |

**Decisions** (category "The Warband"):
- **March the Warband to [state]**: click a highlighted state on the map. Target must be No Man's Land next to your territory, and you must not be at war.
- **Raid [state]**: +20 supplies right away, but wipes that state's forage. Costs 15 political power.
- **Put Down Roots**: needs 50+ supplies on a camp with 40+ forage. Ends the nomad life: you core your camp and become a normal country.

The numbers are `@variables` at the top of `sc_warband_effects.txt`, so they're easy to tune.

### Ideas for v0.2 of the mechanic
- Let warbands march **into land owned by weak free states** (a "demand tribute or we camp here" event chain).
- **Camp followers**: population that travels with the warband and acts as manpower.
- **Seasons**: winter cuts forage and slows marches.
- A **"Horde size"** variable that grows with recruits and makes the warband eat faster.
- An AI that prefers to march **toward** rich land, not just whatever is nearby.
- Showing the warband's route as a map mode or with state flags.

---

## 5. Expanding the provinces in Europe

Vanilla Europe has fairly large provinces. To give warlords room to move, the plan is to roughly **double the land-province density between the Pyrenees and the Urals**.

### Files that change
All of these get **copied from the game into `shattered_continent/map/`** and edited there:

| File | What to do |
|---|---|
| `map/provinces.bmp` | paint new provinces by splitting existing ones. Every province needs a unique RGB colour |
| `map/definition.csv` | one line per new province. **IDs must stay sequential, with no gaps** |
| `history/states/*.txt` | add the new province IDs to the right state's `provinces = { }` list |
| `map/strategicregions/*.txt` | add the new province IDs to their strategic region |
| `map/buildings.txt`, `map/unitstacks.txt` | regenerate with the in-game **Nudger** (`nudge` in the console) |
| `map/adjacencies.csv` | only if new straits or impassable borders are needed |
| `map/railways.txt`, `map/supply_nodes.txt` | fix any rail lines that go through split provinces |
| `map/rivers.bmp`, `map/terrain.bmp`, `map/heightmap.bmp` | usually don't need changes for splits |

### Workflow with the helper tool
```
# 1. Measure how dense Europe is now (pixel box roughly covering Europe — adjust)
python3 tools/province_tool.py density shattered_continent/map 2400 300 3600 1100

# 2. Get 50 fresh colours as ready-to-paste definition.csv lines
python3 tools/province_tool.py newcolors shattered_continent/map 50 land plains 1

# 3. Paint the new provinces in provinces.bmp with those exact colours
#    (GIMP / Paint.NET, pencil tool, NO anti-aliasing, save as 24-bit BMP)

# 4. Check everything matches before launching the game
python3 tools/province_tool.py check shattered_continent/map
```

### Tips
- Split **one region at a time** (for example Poland), test in game, then move on. Debugging 2,000 new provinces at once is miserable.
- Never anti-alias or blur `provinces.bmp`. A single stray pixel colour becomes an "unknown province" error.
- Very small provinces (under ~8 px) cause errors and ugly unit placement.
- Total province count affects performance. Vanilla has around 13k provinces, and a few thousand more is generally fine.
- `history/states` province lists must cover every new land province exactly once.

---

## 6. Nations to workshop

| Tag | Name | Type | Ideology | Concept |
|---|---|---|---|---|
| WST | No Man's Land | placeholder | — | owns all unclaimed land, does nothing |
| ALP | Alpenfestung | SS holdout | fascism | SS mountain redoubt in Tyrol and Salzburg. Strong defence, can't feed itself |
| FNO | Festung Nord | SS holdout | fascism | the stranded garrison in Norway, fighting a Norwegian resistance |
| HNS | Free Hanse | free state | democratic | Hamburg, Bremen and Lübeck. Trade, militia, elections |
| LYO | Lyon Commune | free state | communism | former Resistance holding the fertile Rhône valley |
| HST | Volkov's Host | roaming warlord | despotism | Cossack cavalry host on the eastern plains |
| LGN | The Lost Legion | roaming warlord | despotism | deserters from every army, in the Ardennes |

All leaders are **fictional** on purpose, so we can shape them however we like and avoid glorifying real war criminals.

### Adding a new nation (checklist)
1. Pick an unused 3-letter tag and add it to `common/country_tags/sc_countries.txt`.
2. Create `common/countries/SC <Name>.txt` (colour, graphical culture).
3. Create `history/countries/<TAG> - <Name>.txt` (politics, tech, division template; add `set_country_flag = sc_nomadic` and `warband_supplies` for a warlord).
4. Add a leader in `common/characters/sc_characters.txt`.
5. Add name keys (`TAG`, `TAG_DEF`, `TAG_ADJ`, plus `TAG_<ideology>` versions) to the localisation file.
6. Add a flag design to `tools/make_placeholder_flags.py` and run it (or drop in real art).
7. Add its states to `setup/state_assignments.csv` and run `build_setup.py`.
8. Add starting divisions in `sc_spawn_starting_armies`.

### Open questions for the group
1. **What destroyed Europe?** Atomic war in 1945? A war that never ended and ground everything down? A famine-and-plague collapse? This decides the tone, how many people are left, and whether some areas are *irradiated wasteland*.
2. **What about the USSR, UK and USA?** Destroyed too, survive as distant rumps, or outside powers meddling in Europe?
3. **Is No Man's Land empty, or does it have people?** It could have raiders, a "wasteland danger" level, or minor tribes the warlords can recruit.
4. **How should SS holdouts play?** Siege-defence gameplay, slowly collapsing fanaticism, or expansionist villains the other nations have to unite against?
5. **More nations to sketch out:** e.g. a Vatican-led Catholic league, a Polish Home Army republic, Balkan partisan federations, a Swiss "neutral bank" state, Iberian survivors, a Danish–Swedish refuge.
6. **Endgame:** Does someone reunify Europe? Is there a crisis event (like an outside power invading) in the 1950s?

---

## 7. First in-game test checklist

Things written from memory of the HoI4 script language that may need adjusting:

- [ ] `on_monthly` fires per country (if not, move the tick to `on_weekly` or a monthly self-repeating event).
- [ ] `create_unit` without `prioritize_location` spawns at the capital (if not, add a province ID).
- [ ] When the old camp goes back to WST, units standing there get moved to the new camp.
- [ ] Decision and category icon names (`generic_military`, `generic_army_support`, …) exist. A missing icon only shows up blank.
- [ ] `state_target = yes` decisions with no `targets` list check all states (if it's slow, add `target_array`).
- [ ] The dynamic-modifier icons exist.
- [ ] The decision text shows `[?warband_supplies]` and `[?sc_camp_forage]` properly.
- [ ] The WST "No Man's Land" AI doesn't build or recruit anything.

---

## Folder map
```
shattered_continent/
├── descriptor.mod
├── common/
│   ├── bookmarks/            1946 start
│   ├── characters/           leaders
│   ├── countries/            colours + graphics culture
│   ├── country_tags/         tag list
│   ├── decisions/            warband decisions (+ categories/)
│   ├── dynamic_modifiers/    starving / well-fed
│   ├── ideas/                No Man's Land idea
│   ├── on_actions/           startup + monthly tick
│   ├── scripted_effects/     setup + warband logic (+ GENERATED setup file)
│   └── scripted_triggers/    march / raid target rules
├── events/                   warband events
├── gfx/flags/                flags (82x52, medium 41x26, small 10x7)
├── history/countries/        starting politics, tech, templates
├── localisation/english/     all text (UTF-8 with BOM!)
├── setup/state_assignments.csv   ← workshop the starting borders here
└── tools/
    ├── list_states.py            look up vanilla state IDs
    ├── build_setup.py            CSV → setup effect
    ├── province_tool.py          map checker / colour generator / density
    └── make_placeholder_flags.py
```
