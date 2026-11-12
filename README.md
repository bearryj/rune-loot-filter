# BearryJ's RuneLite Loot Filters

Custom OSRS Ironman loot-filter presets maintained by BearryJ, derived from the upstream Iron-Filter project. The scheduled sync keeps both presets current while applying BearryJ's branding and custom rules.

## What's changed

- Transparent item backgrounds
- Transparent borders
- Tier-colored item text (readable without the highlight boxes)
- BearryJ-branded filter names and welcome text

## Files

- `Iron-Filter-CUSTOM.rs2f` — BearryJ's standard Ironman filter
- `Iron-Filter-CUSTOM-FRESH-ACCOUNT.rs2f` — BearryJ's fresh-account variant; opens single-count D-tier gear, runes, seeds, bow strings, planks, and unnoted Limpwurt roots alongside the relaxed E-tier supplies
- `sync_transform.py` — regenerates the standard filter from upstream and applies BearryJ branding
- `fresh_account_transform.py` — derives the fresh-account variant; the scheduled sync regenerates both files

## Install

1. In RuneLite, enable the **Loot Filter** plugin.
2. Loot Filter panel → **Import** → choose one filter:
   - `Iron-Filter-CUSTOM.rs2f` for BearryJ's standard filter
   - `Iron-Filter-CUSTOM-FRESH-ACCOUNT.rs2f` for BearryJ's fresh, low-level Ironman filter
