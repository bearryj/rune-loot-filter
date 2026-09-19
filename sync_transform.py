import re, sys

SRC = r"D:\Projects\Iron-Filter\Iron-Filter.rs2f"
DST = r"D:\Projects\rune-loot-filter\.sync_new_custom.rs2f"

EXEMPT = {
    "KEY_SHADES_BRONZE","KEY_SHADES_STEEL","KEY_SHADES_BLACK","KEY_SHADES_SILVER","KEY_SHADES_GOLD",
    "KEY_SHADES_RED","KEY_SHADES_BROWN","KEY_SHADES_CRIMSON","KEY_SHADES_BLACK2","KEY_SHADES_PURPLE",
    "COX_PLANKS","COX_GOLPAR","COX_BUCHU","COX_NOXIFER",
}

# Custom: stretch the tier alpha ladder up so faint tiers stay readable.
# Storn: ff(SS/S) cc(A) 99(B) 66(E) 33(C), 70 on fallback B.
# New:   ff(SS/S) e6(A 90%) cc(B 80%) 99(E 60%) 66(C 40%).
ALPHA_STRETCH = {"cc": "e6", "99": "cc", "70": "cc", "66": "99", "33": "66"}

# Custom: rune text color matches the rune's in-game color.
# name -> (hex6, SS-quant define of the rune's tier, menuSort or None)
RUNE_COLORS = {
    # D tier
    "Cosmic rune": ("a88fd8", "RUNES_D_SS_QUANT", None),
    "Chaos rune":  ("e17000", "RUNES_D_SS_QUANT", None),
    "Nature rune": ("2e8b3c", "RUNES_D_SS_QUANT", None),
    "Law rune":    ("86aae8", "RUNES_D_SS_QUANT", None),
    "Death rune":  ("f2f2f2", "RUNES_D_SS_QUANT", None),
    "Sunfire rune":("e8a020", "RUNES_D_SS_QUANT", None),
    "Astral rune": ("e3cf8f", "RUNES_D_SS_QUANT", None),
    "Blood rune":  ("b01010", "RUNES_D_SS_QUANT", None),
    "Soul rune":   ("6f2fb5", "RUNES_D_SS_QUANT", None),
    "Wrath rune":  ("39415a", "RUNES_D_SS_QUANT", None),
    # E tier (menuSort matches RUNES_E_STYLE)
    "Air rune":    ("aac8ff", "RUNES_E_SS_QUANT", -10000),
    "Water rune":  ("3d5fd9", "RUNES_E_SS_QUANT", -10000),
    "Earth rune":  ("8f5e2a", "RUNES_E_SS_QUANT", -10000),
    "Fire rune":   ("d5420f", "RUNES_E_SS_QUANT", -10000),
    "Mind rune":   ("3e6fd8", "RUNES_E_SS_QUANT", -10000),
    "Body Rune":   ("6274a3", "RUNES_E_SS_QUANT", -10000),
    "Mist rune":   ("c0c8d4", "RUNES_E_SS_QUANT", -10000),
    "Dust rune":   ("b08a50", "RUNES_E_SS_QUANT", -10000),
    "Mud rune":    ("6b4428", "RUNES_E_SS_QUANT", -10000),
    "Smoke rune":  ("7e7e7e", "RUNES_E_SS_QUANT", -10000),
    "Steam rune":  ("a2b8d2", "RUNES_E_SS_QUANT", -10000),
    "Lava rune":   ("e04800", "RUNES_E_SS_QUANT", -10000),
    # C tier
    "Aether rune": ("3fc5e8", "RUNES_C_SS_QUANT", None),
}

lines = open(SRC, encoding="utf-8", errors="replace").read().splitlines()

out = []
i = 0
n = len(lines)
stats = {"blocks": 0, "style_blocks": 0, "exempt": 0, "transformed": 0, "bg_zeroed": 0,
         "text_swapped": 0, "border_zeroed": 0, "no_bg_border": 0, "untouched_no_bg": 0, "icon_removed": 0,
         "rune_colors": 0, "meta_renamed": 0, "text_stretched": 0, "menu_stretched": 0}

field_pat = re.compile(r'^([ \t]*)(\w+)\s*=\s*"#([0-9a-fA-F]{8})"(\s*;.*)$')

def transform_block(header_idx, name, block_lines):
    """block_lines: list of (raw_line). header_idx: index of the #define line in block_lines.
    Returns new block lines."""
    exempt = name in EXEMPT
    stats["blocks"] += 1
    has_field = any(field_pat.match(l) for l in block_lines)
    if not has_field:
        return block_lines  # value defines, HIDE lists etc.
    stats["style_blocks"] += 1
    if exempt:
        stats["exempt"] += 1
        return block_lines

    # extract old values
    old_bg = None; old_text = None; old_border = None
    for l in block_lines:
        m = field_pat.match(l)
        if not m: continue
        fname, val = m.group(2), m.group(3).lower()
        if fname == "backgroundColor": old_bg = m.group(3)   # keep original case
        if fname == "textColor": old_text = val
        if fname == "borderColor": old_border = val

    transformed = False
    new_lines = []
    for l in block_lines:
        m = field_pat.match(l)
        if not m:
            new_lines.append(l); continue
        indent, fname, val, rest = m.groups()
        val_l = val.lower()
        newval = val
        if fname == "backgroundColor" and old_bg is not None:
            newval = "00" + old_bg[2:]
            stats["bg_zeroed"] += 1
            transformed = True
        if fname in ("textColor", "color"):
            if old_bg is not None and val_l == "ffffffff":
                newval = old_bg  # keep original bg case
                stats["text_swapped"] += 1
                transformed = True
            a = newval.lower()[:2]
            if a in ALPHA_STRETCH:
                newval = ALPHA_STRETCH[a] + newval[2:]
                stats["text_stretched"] += 1
                transformed = True
        elif fname == "menuTextColor":
            a = val_l[:2]
            if a in ALPHA_STRETCH:
                newval = ALPHA_STRETCH[a] + val[2:]
                stats["menu_stretched"] += 1
                transformed = True
        elif fname == "borderColor":
            if old_bg is not None and val_l == "ffffffff":
                newval = "00" + old_bg[2:]
            else:
                newval = "00" + val[2:]
            stats["border_zeroed"] += 1
            transformed = True
        if newval != val:
            new_lines.append(f'{indent}{fname} = "#{newval}"{rest}')
        else:
            new_lines.append(l)
    if transformed:
        stats["transformed"] += 1
    else:
        stats["untouched_no_bg"] += 1
    if name.startswith("ALCHS_"):
        # custom change: no high-alch coin icon
        filtered = [l for l in new_lines if not re.match(r'^\s*icon\s*=\s*Sprite\(41,0\)', l)]
        stats["icon_removed"] += len(new_lines) - len(filtered)
        new_lines = filtered
    return new_lines

while i < n:
    line = lines[i]
    m = re.match(r'^#define\s+(\S+)', line)
    if m:
        name = m.group(1)
        block = [line]
        # multi-line continuation
        while line.rstrip().endswith("\\") and i + 1 < n:
            i += 1
            line = lines[i]
            block.append(line)
        out.extend(transform_block(i, name, block))
    else:
        out.append(line)
    i += 1

def add_rune_colors(out):
    """Insert per-rune style rules BEFORE the rune quantity ladder.
    First-match-wins semantics: below SS quantity the per-rune rule matches first
    (rune-colored text); at SS+ the ladder still applies (lootbeam + tier style).
    Hide rules live earlier in the module, so hiding is unaffected."""
    anchor = re.compile(r'^rule \(name:RUNES_SS_NAMES\) \{RUNES_SS_STYLE\}$')
    idx = next((j for j, l in enumerate(out) if anchor.match(l.strip())), None)
    if idx is None:
        print("WARNING: rune ladder anchor not found - skipping rune colors")
        return out
    block = ["/* Rune text colors match in-game rune colors (generated by sync_transform.py, edit RUNE_COLORS) */"]
    for rname, (hex6, guard, menu_sort) in RUNE_COLORS.items():
        slug = re.sub(r'[^A-Z]', '_', rname.upper())
        style = f"RUNE_{slug}_STYLE"
        block.append(f"#define {style} \\")
        block.append(f"\tcolor = \"#ff{hex6}\"; \\")
        block.append(f"\tmenuTextColor = \"#ff{hex6}\";")
        if menu_sort is not None:
            block[-1] += " \\"
            block.append(f"\tmenuSort = {menu_sort};")
        block.append(f"rule (name:\"{rname}\" && quantity:<{guard}) {{{style}}}")
        block.append("")
    stats["rune_colors"] = len(RUNE_COLORS)
    return out[:idx] + block + out[idx:]

def preserve_meta_name(out):
    """Keep the user's manual rename through regeneration."""
    for j, l in enumerate(out):
        if l.strip() == 'name = "Storn\'s Iron Filter";':
            out[j] = l.replace("Storn's Iron Filter", "Iron Filter Custom")
            stats["meta_renamed"] = 1
            return out
    print("WARNING: meta name line not found")
    return out

out = add_rune_colors(out)
out = preserve_meta_name(out)

open(DST, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("stats:", stats)
print("output lines:", len(out), "src lines:", n)
