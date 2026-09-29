"""Convert [@key; @key2] citations in paper2.md to IEEE numbers in order of first
appearance, and append the numbered reference list. Writes paper2_numbered.md."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
refs = json.load(open(os.path.join(HERE, "references.json")))
text = open(os.path.join(HERE, "paper2.md")).read()

order = []
def num(key):
    if key not in refs:
        raise KeyError(f"Unknown reference key: {key}")
    if key not in order:
        order.append(key)
    return order.index(key) + 1

def repl(m):
    keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
    return ", ".join(f"[{num(k)}]" for k in keys)

text = re.sub(r"\[(@[^\]]+)\]", repl, text)
unused = sorted(set(refs) - set(order))
text = text.rstrip() + "\n\n" + "\n\n".join(f"[{i + 1}] {refs[k]}" for i, k in enumerate(order)) + "\n"
open(os.path.join(HERE, "paper2_numbered.md"), "w").write(text)
print(f"{len(order)} references cited; unused keys: {unused}")
