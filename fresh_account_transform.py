#!/usr/bin/env python3
"""Generate a fresh-account variant from the current custom OSRS loot filter.

The variant keeps the Ironman rules and styling, relaxes useful early-game E- and
selected D-tier gates, and preserves higher-tier clutter filters.
"""

from __future__ import annotations

import argparse
import json
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
    "BLACK_GEAR_D_MIN_QUANT": "1",
    "BRONZE_GEAR_D_MIN_QUANT": "1",
    "STEEL_GEAR_D_MIN_QUANT": "1",
    "FLETCHING_D_MIN_QUANT": "1",
    "PLANKS_D_MIN_QUANT": "1",
    "RUNES_D_MIN_QUANT": "1",
    "SEEDS_D_MIN_QUANT": "1",
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
    "ADAMANTITE_GEAR_D_SHOW_UNNOTED",
    "BLACK_GEAR_D_SHOW_UNNOTED",
    "BRONZE_GEAR_D_SHOW_UNNOTED",
    "FLETCHING_D_SHOW_UNNOTED",
    "IRON_GEAR_D_SHOW_UNNOTED",
    "MITHRIL_GEAR_D_SHOW_UNNOTED",
    "PLANKS_D_SHOW_UNNOTED",
    "RUNES_D_SHOW_UNNOTED",
    "SEEDS_D_SHOW_UNNOTED",
    "STEEL_GEAR_D_SHOW_UNNOTED",
}

# These are useful early-account unnoted drops assigned to a higher upstream
# tier. Exclude only these names from that tier's hide gate; their original tier
# style remains in effect and unrelated D-tier clutter stays hidden.
UNNOTED_EXCEPTIONS = {
    "HERBLORE_SECONDARIES_D": {"Limpwurt root"},
}

INTENTIONALLY_HIDDEN_E_SHOW_UNNOTED = {
    "BLIGHTED_FOOD_AND_POTS_STOCKPILE_E_SHOW_UNNOTED",
}

META_NAME = "BearryJ's Iron Filter - Fresh Account"
META_DESCRIPTION = (
    "BearryJ's Ironman fresh-account preset: shows low-quantity and unnoted "
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


def set_greeting(lines: list[str]) -> None:
    for i, line in enumerate(lines):
        if line.strip() != "/*@ define:module:greetings":
            continue
        for j in range(i + 1, len(lines)):
            if lines[j].strip() == "*/":
                break
            match = re.match(r'^(\s*name:\s*).+$', lines[j])
            if match:
                lines[j] = f"{match.group(1)}Welcome to BearryJ's Iron Filter - Fresh Account"
                return
        raise ValueError("greetings module has no name")
    raise ValueError("could not locate the greetings module")


def set_define(lines: list[str], name: str, value: str) -> None:
    pattern = re.compile(rf'^(\s*#define\s+{re.escape(name)}\s+)(\S+)(\s*)$')
    matches = [i for i, line in enumerate(lines) if pattern.match(line)]
    if len(matches) != 1:
        raise ValueError(f"expected one #define {name}, found {len(matches)}")
    index = matches[0]
    match = pattern.match(lines[index])
    assert match is not None
    lines[index] = f"{match.group(1)}{value}{match.group(3)}"


def validate_e_tier_coverage(lines: list[str]) -> None:
    definitions: dict[str, str] = {}
    for line in lines:
        parts = line.split(None, 2)
        if len(parts) == 3 and parts[0] == "#define":
            definitions[parts[1]] = parts[2]

    missing_quantities = []
    missing_unnoted = []
    for name, value in definitions.items():
        if name.endswith("_E_MIN_QUANT"):
            try:
                threshold = int(value)
            except ValueError:
                continue
            if threshold > 1 and name not in MIN_QUANTITIES:
                missing_quantities.append(name)
        elif name.endswith("_E_SHOW_UNNOTED") and value.lower() == "false":
            if name not in SHOW_UNNOTED and name not in INTENTIONALLY_HIDDEN_E_SHOW_UNNOTED:
                missing_unnoted.append(name)

    if missing_quantities or missing_unnoted:
        raise ValueError(
            "unreviewed E-tier settings: "
            f"minimum quantities={sorted(missing_quantities)}, "
            f"unnoted gates={sorted(missing_unnoted)}"
        )


def apply_unnoted_exceptions(lines: list[str]) -> None:
    for group, items in UNNOTED_EXCEPTIONS.items():
        names_define = f"{group}_NAMES"
        names_line = next((line for line in lines if line.startswith(f"#define {names_define} ")), None)
        if names_line is None:
            raise ValueError(f"missing #define {names_define}")
        try:
            names = json.loads(names_line.split(None, 2)[2])
        except (IndexError, json.JSONDecodeError) as exc:
            raise ValueError(f"could not parse {names_define}") from exc
        if not items.issubset(set(names)):
            raise ValueError(f"fresh-account exception missing from {names_define}: {sorted(items - set(names))}")

        marker = f"name:{names_define} && !{group}_SHOW_UNNOTED && stackable:false"
        matching_rules = [i for i, line in enumerate(lines) if marker in line]
        if len(matching_rules) != 2:
            raise ValueError(f"expected two unnoted hide rules for {group}, found {len(matching_rules)}")

        exclusion = "".join(f' && !name:"{item}"' for item in sorted(items))
        for index in matching_rules:
            if exclusion not in lines[index]:
                lines[index] = lines[index].replace(marker, marker + exclusion, 1)


def transform(source: Path, destination: Path) -> None:
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    validate_e_tier_coverage(lines)
    try:
        meta_start = next(i for i, line in enumerate(lines) if line.strip() == "meta {")
        meta_end = next(i for i in range(meta_start + 1, len(lines)) if lines[i].strip() == "}")
    except StopIteration as exc:
        raise ValueError("could not locate the meta block") from exc

    set_meta_property(lines, meta_start, meta_end, "name", META_NAME)
    set_meta_property(lines, meta_start, meta_end, "description", META_DESCRIPTION)
    set_greeting(lines)

    for name, value in MIN_QUANTITIES.items():
        set_define(lines, name, value)
    for name in SHOW_UNNOTED:
        set_define(lines, name, "true")
    apply_unnoted_exceptions(lines)

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
