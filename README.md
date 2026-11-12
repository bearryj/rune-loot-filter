# rune-loot-filter

Custom OSRS loot filter based on [Storn's Iron-Filter](https://github.com/Storn42/Iron-Filter).

## What's changed

- Transparent item backgrounds
- Transparent borders
- Tier-colored item text (readable without the highlight boxes)

## Files

- `Iron-Filter-CUSTOM.rs2f` — main custom filter, tracking Storn's latest release
- `Iron-Filter-CUSTOM-FRESH-ACCOUNT.rs2f` — Ironman fresh-account variant; relaxes low-tier quantity and unnoted-item filters for early gear and supplies
- `sync_transform.py` — regenerates the main custom filter from upstream
- `fresh_account_transform.py` — derives the fresh-account variant; the scheduled sync regenerates both files

## Install

1. In RuneLite, enable the **Loot Filter** plugin.
2. Loot Filter panel → **Import** → choose one filter:
   - `Iron-Filter-CUSTOM.rs2f` for the standard custom filter
   - `Iron-Filter-CUSTOM-FRESH-ACCOUNT.rs2f` for a fresh, low-level Ironman account
