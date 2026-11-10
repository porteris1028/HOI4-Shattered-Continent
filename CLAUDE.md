# Shattered Continent: context for Claude

A Hearts of Iron IV alternate-history mod. Start of 1946: D-Day stalled, the Soviets stalled in Poland, the US nuked Berlin and Munich instead of Japan, and a chain reaction ruined Europe. The great powers are the USA, Japan and a rising China. Europe is warlords, free states, Cossack hosts, army remnants and SS holdouts.

Read **README.md** (mechanics, workflow, test checklist) and **LORE.md** (setting, open questions) before making changes. `docs/NATIONS.md` lists every nation.

## How the project is built
- **Edit `setup/`, not generated files.** Files that start with `# GENERATED` are rebuilt by the tools:
  - `setup/nations.toml` → `python tools/build_nations.py` (tags, countries, history, leaders, localisation, flags, starting armies)
  - `setup/state_assignments.csv` and `setup/danger_zones.csv` (states listed by name in the `match` column, with `|` between alternative spellings) → `python tools/setup_map.py "<HoI4 game folder>"`. This fills in `state_id` from the game files, then runs `tools/build_setup.py`. See `setup/match_report.txt`.
- Hand-written mechanics live in `common/` (scripted_effects, scripted_triggers, decisions, ideas, dynamic_modifiers, on_actions), plus `events/` and `localisation/english/sc_l_english.yml` (UTF-8 **with BOM**).
- All mod-specific names use the `sc_` prefix.
- The Python tools need Python 3.11+ and Pillow (Pillow only for flags).

## Where we left off (v0.3.0)
1. **Not yet run successfully in game.** In the first test the new nations didn't appear because the state IDs were blank, and the old European nations were still there. v0.3 added the name-based map plan, `setup_map.py`, a second wipe pass (by tag and cores) and `[Shattered Continent]` lines in `game.log`.
2. **Next steps, in order:**
   - Run `python tools/check_tags.py "<game folder>"` and rename any clashing tags in `nations.toml`.
   - Run `python tools/setup_map.py "<game folder>"`. Go through every `CHECK` / `MISSING` line in `setup/match_report.txt`, using the real files in `<game folder>/history/states` and `localisation/english/state_names_l_english.yml`. Fix the `match` names or type in `state_id` until everything is `ok`.
   - Start the 1946 bookmark with `-debug`. Read `Documents/Paradox Interactive/Hearts of Iron IV/logs/game.log` (search `[Shattered Continent]`) and `error.log`, and fix everything in README section 6 (the test checklist).
   - Check the scripting against the real game files: icon names, modifier names, sub-ideology names, `on_monthly`, `create_unit` without a location, `set_variable_to_random`, missions. Vanilla examples are in the game's `common/` folder.
3. **Roadmap after that:** focus trees (SS states, Volkov's Host, Home Army Republic first), the 1946 situation for USA, Japan and China, the colonies of the destroyed powers, province expansion in Europe, real flags and portraits.

## Working with the user
- The user writes the lore and decides story questions; Claude proposes and builds. Record new lore in LORE.md and keep open questions marked **[OPEN]**.
- Leaders are fictional except where the user asked for real figures (Himmler leads the Black Order cult state). Portray SS states as villains, never glorified.
- GitHub repo: `porteris1028/HOI4-Shattered-Continent`, branch `main`. Commit and push when a piece of work is done.
