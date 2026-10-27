"""Emit the KALQ .keyman-touch-layout. Grid is Figure 1 of Oulasvirta et al, CHI 2013."""
import json, sys

# left block 4x4, right block 4x3; "" == the two KALQ space keys
LEFT  = [list("MBWH"), ["P", "", "X", "C"], list("RYSZ"), list("DNFV")]
RIGHT = [list("GTOJ"), ["I", "E", "", "U"], list("KALQ")]

LETTER_W = "125"   # 8 letter keys fill the row; KALQ's blocks touch in the middle

# the globe is a longpress, not a key: never used, but Keyman requires one per layer
GLOBE_SK = [{"id": "K_LOPT", "text": "*Menu*", "sp": "1"}]

def letter(ch, upper):
    if ch == "":
        return {"id": "K_SPACE", "text": "", "width": LETTER_W, "sp": "0"}
    return {"id": "K_" + ch, "text": ch if upper else ch.lower(), "width": LETTER_W}

def digits(upper):
    # on the shift layer the digit keys must stay digits, not !@#
    return [dict({"id": "K_" + d, "text": d}, **({"layer": "default"} if upper else {}))
            for d in "1234567890"]

def letter_rows(upper):
    rows = []
    for i in range(4):
        keys = [letter(c, upper) for c in LEFT[i]]
        if i < 3:
            keys += [letter(c, upper) for c in RIGHT[i]]
        else:  # bottom-right slots are empty in KALQ; the frame keys go there
            keys += [
                {"id": "K_SHIFT", "text": "*Shifted*" if upper else "*Shift*",
                 "width": "100", "sp": "2" if upper else "1",
                 "nextlayer": "default" if upper else "shift"},
                {"id": "K_NUMLOCK", "text": "*123*", "width": "100", "sp": "1",
                 "nextlayer": "numeric", "sk": GLOBE_SK},
                {"id": "K_BKSP", "text": "*BkSp*", "width": "150", "sp": "1"},
                {"id": "K_ENTER", "text": "*Enter*", "width": "150", "sp": "1"},
            ]
        rows.append(keys)
    return rows

def sym(ch, vk, shifted):
    return {"id": vk, "text": ch, "layer": "shift" if shifted else "default"}

SYMBOLS = [
    [("!", "K_1", 1), ("@", "K_2", 1), ("#", "K_3", 1), ("$", "K_4", 1), ("%", "K_5", 1),
     ("^", "K_6", 1), ("&", "K_7", 1), ("*", "K_8", 1), ("(", "K_9", 1), (")", "K_0", 1)],
    [("-", "K_HYPHEN", 0), ("_", "K_HYPHEN", 1), ("=", "K_EQUAL", 0), ("+", "K_EQUAL", 1),
     ("[", "K_LBRKT", 0), ("]", "K_RBRKT", 0), ("{", "K_LBRKT", 1), ("}", "K_RBRKT", 1),
     ("\\", "K_BKSLASH", 0), ("|", "K_BKSLASH", 1)],
    [(";", "K_COLON", 0), (":", "K_COLON", 1), ("'", "K_QUOTE", 0), ('"', "K_QUOTE", 1),
     (",", "K_COMMA", 0), (".", "K_PERIOD", 0), ("?", "K_SLASH", 1), ("/", "K_SLASH", 0),
     ("<", "K_COMMA", 1), (">", "K_PERIOD", 1)],
]

numeric_rows = [digits(False)] + [[sym(*s) for s in r] for r in SYMBOLS] + [[
    {"id": "K_LOWER", "text": "*abc*", "width": "150", "sp": "1",
     "nextlayer": "default", "sk": GLOBE_SK},
    {"id": "K_SPACE", "text": "", "width": "520", "sp": "0"},
    {"id": "K_BKSP", "text": "*BkSp*", "width": "165", "sp": "1"},
    {"id": "K_ENTER", "text": "*Enter*", "width": "165", "sp": "1"},
]]

def layer(lid, rows):
    return {"id": lid, "row": [{"id": str(i + 1), "key": k} for i, k in enumerate(rows)]}

APPLE_FONT = "-apple-system, system-ui, 'Helvetica Neue', Helvetica, Arial, sans-serif"

out = {"phone": {"font": APPLE_FONT, "layer": [
    layer("default", [digits(False)] + letter_rows(False)),
    layer("shift",   [digits(True)]  + letter_rows(True)),
    layer("numeric", numeric_rows),
]}}

# every row must total 1000 units or the engine stretches its last key
for L in out["phone"]["layer"]:
    for r in L["row"]:
        w = sum(int(k.get("width", "100")) + int(k.get("pad", "0")) for k in r["key"])
        assert w == 1000, (L["id"], r["id"], w)

json.dump(out, open(sys.argv[1], "w"), indent=2, ensure_ascii=False)
print("wrote", sys.argv[1])
