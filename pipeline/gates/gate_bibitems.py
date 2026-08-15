#!/usr/bin/env python
"""Citation-integrity gate for a manuscript with an inline \\bibitem bibliography.

The reusable gate_cites.py from the PsychBench suite assumes a BibTeX .bib file. This paper
carries its references as \\bibitem entries inside the .tex, so that gate reports every key as
missing. This variant checks the same property against the inline bibliography:
  - every \\cite key resolves to a \\bibitem
  - every \\bibitem is cited at least once
  - every \\ref resolves to a \\label

Usage:  python gate_bibitems.py path/to/main.tex
Exit 0 clean, 1 on any hit.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: gate_bibitems.py <main.tex>")
        return 2
    p = Path(sys.argv[1])
    t = p.read_text(encoding="utf-8", errors="replace")

    cited: set[str] = set()
    for grp in re.findall(r"\\cite\{([^}]*)\}", t):
        cited.update(k.strip() for k in grp.split(",") if k.strip())
    defined = set(re.findall(r"\\bibitem\{([^}]*)\}", t))

    refs: set[str] = set()
    for grp in re.findall(r"\\ref\{([^}]*)\}", t):
        refs.update(k.strip() for k in grp.split(",") if k.strip())
    labels = set(re.findall(r"\\label\{([^}]*)\}", t))

    fails = 0
    print(f"gate_bibitems: {p.name}")
    print(f"  cite keys used   : {len(cited)}")
    print(f"  bibitems defined : {len(defined)}")
    print(f"  \\ref targets used: {len(refs)}")
    print(f"  labels defined   : {len(labels)}\n")

    missing = sorted(cited - defined)
    if missing:
        fails += 1
        print(f"  FAIL  {len(missing)} cited key(s) with no \\bibitem: {missing}")
    else:
        print("  OK    every \\cite resolves to a \\bibitem")

    orphan = sorted(defined - cited)
    if orphan:
        fails += 1
        print(f"  FAIL  {len(orphan)} \\bibitem(s) never cited: {orphan}")
    else:
        print("  OK    every \\bibitem is cited")

    dangling = sorted(refs - labels)
    if dangling:
        fails += 1
        print(f"  FAIL  {len(dangling)} \\ref(s) with no \\label: {dangling}")
    else:
        print("  OK    every \\ref resolves to a \\label")

    print()
    if fails:
        print("gate_bibitems: FAIL")
        return 1
    print("gate_bibitems: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
