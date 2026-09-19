import re, sys

SRC = r"D:\Projects\Iron-Filter\Iron-Filter.rs2f"
DST = r"D:\Projects\rune-loot-filter\.sync_new_custom.rs2f"

EXEMPT = {
    "KEY_SHADES_BRONZE","KEY_SHADES_STEEL","KEY_SHADES_BLACK","KEY_SHADES_SILVER","KEY_SHADES_GOLD",
    "KEY_SHADES_RED","KEY_SHADES_BROWN","KEY_SHADES_CRIMSON","KEY_SHADES_BLACK2","KEY_SHADES_PURPLE",
    "COX_PLANKS","COX_GOLPAR","COX_BUCHU","COX_NOXIFER",
}

lines = open(SRC, encoding="utf-8", errors="replace").read().splitlines()

out = []
i = 0
n = len(lines)
stats = {"blocks": 0, "style_blocks": 0, "exempt": 0, "transformed": 0, "bg_zeroed": 0,
         "text_swapped": 0, "border_zeroed": 0, "no_bg_border": 0, "untouched_no_bg": 0}

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
        if fname in ("textColor", "color") and old_bg is not None and val_l == "ffffffff":
            newval = old_bg  # keep original bg case
            stats["text_swapped"] += 1
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

open(DST, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("stats:", stats)
print("output lines:", len(out), "src lines:", n)
