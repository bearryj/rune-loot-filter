#!/usr/bin/env python3
"""Generate a fresh-account variant from the current custom OSRS loot filter.

The variant keeps the Ironman rules and custom styling, but relaxes selected
E-tier quantity and unnoted-item gates for early-game gear and supplies.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

# Lower low-tier minimum stacks and allow useful unnoted drops through.
# Keep HIDE_USER unchanged: the upstream filter uses it for boss-area overrides,
# not as a global hide list.
MIN_QUANTITIES = {
    "TELEPORTS_E_MIN_QUANT": "1",
    "SEEDS_E_MIN_QUANT": "1",
    "HERBLORE_SECONDARIES_E_MIN_QUANT": "1",
    "COOKING_E_MIN_QUANT": "1",
    "RUNES_E_MIN_QUANT": "1",
    "ORES_AND_BARS_E_MIN_QUANT": "1",
    "LOGS_E_MIN_QUANT": "1",
    "PLANKS_E_MIN_QUANT": "1",
    "CRAFTING_E_MIN_QUANT": "1",
    "PRAYER_ASHES_E_MIN_QUANT": "1",
    "FLETCHING_E_MIN_QUANT": "1",
    "ADAMANTITE_GEAR_E_MIN_QUANT": "1",
    "MITHRIL_GEAR_E_MIN_QUANT": "1",
    "BLACK_GEAR_E_MIN_QUANT": "1",
    "STEEL_GEAR_E_MIN_QUANT": "1",
    "IRON_GEAR_E_MIN_QUANT": "1",
    "BRONZE_GEAR_E_MIN_QUANT": "1",
}

SHOW_UNNOTED = {
    "COOKING_E_SHOW_UNNOTED",
    "FOOD_AND_POTS_STOCKPILE_E_SHOW_UNNOTED",
    "ORES_AND_BARS_E_SHOW_UNNOTED",
    "LOGS_E_SHOW_UNNOTED",
    "PLANKS_E_SHOW_UNNOTED",
    "CRAFTING_E_SHOW_UNNOTED",
    "PRAYER_BONES_E_SHOW_UNNOTED",
    "PRAYER_ASHES_E_SHOW_UNNOTED",
    "PRAYER_HEADS_E_SHOW_UNNOTED",
    "FLETCHING_E_SHOW_UNNOTED",
    "ADAMANTITE_GEAR_E_SHOW_UNNOTED",
    "MITHRIL_GEAR_E_SHOW_UNNOTED",
    "BLACK_GEAR_E_SHOW_UNNOTED",
    "STEEL_GEAR_E_SHOW_UNNOTED",
    "IRON_GEAR_E_SHOW_UNNOTED",
    "BRONZE_GEAR_E_SHOW_UNNOTED",
}

META_NAME = "Iron Filter Custom - Fresh Account"
META_DESCRIPTION = (
    "Ironman-focused fresh-account preset: shows low-quantity and unnoted "
    "early-game gear, food, runes, and resources."
)


def set_meta_property(lines: list[str], start: int, end: int, prop: str, value: str) -> None:
    pattern = re.compile(rf'^(\s*{re.escape(prop)}\s*=\s*)"[^"]*"(;\s*)$')
    matches = [i for i in range(start, end) if pattern.match(lines[i])]
    if len(matches) != 1:
        raise ValueError(f"expected one meta {prop} property, found {len(matches)}")
    index = matches[0]
    match = pattern.match(lines[index])
    assert match is not None
    lines[index] = f'{match.group(1)}"{value}"{match.group(2)}'


def set_define(lines: list[str], name: str, value: str) -> None:
    pattern = re.compile(rf'^(\s*#define\s+{re.escape(name)}\s+)(\S+)(\s*)$')
    matches = [i for i, line in enumerate(lines) if pattern.match(line)]
    if len(matches) != 1:
        raise ValueError(f"expected one #define {name}, found {len(matches)}")
    index = matches[0]
    match = pattern.match(lines[index])
    assert match is not None
    lines[index] = f"{match.group(1)}{value}{match.group(3)}"


def transform(source: Path, destination: Path) -> None:
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    try:
        meta_start = next(i for i, line in enumerate(lines) if line.strip() == "meta {")
        meta_end = next(i for i in range(meta_start + 1, len(lines)) if lines[i].strip() == "}")
    except StopIteration as exc:
        raise ValueError("could not locate the meta block") from exc

    set_meta_property(lines, meta_start, meta_end, "name", META_NAME)
    set_meta_property(lines, meta_start, meta_end, "description", META_DESCRIPTION)

    for name, value in MIN_QUANTITIES.items():
        set_define(lines, name, value)
    for name in SHOW_UNNOTED:
        set_define(lines, name, "true")

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="main custom .rs2f source")
    parser.add_argument("destination", type=Path, help="fresh-account .rs2f output")
    args = parser.parse_args()
    try:
        transform(args.source, args.destination)
    except Exception as exc:
        parser.exit(1, f"fresh-account transform failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
