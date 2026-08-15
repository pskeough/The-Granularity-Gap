"""Scan prose for the rhetorical shapes Patrick rejects by name.

The mimesis scrubber tests em-dashes, hedging, an AI-word blocklist and stylometric distance.
gate_prose.py covers meta-announcement, self-ranking, consequence-attachers and clause accretion.
Neither flags "Two exposures we disclose rather than defend", which is the construction he quoted
back as the thing he does not want: the sentence is built as a contrast so the contrast can do the
work the finding should be doing.

Five classes, from his own list:

  ANTI    antithesis and reversal: "not X, but Y", "X rather than Y", "does not X, it Y"
  APPOS   appositive stacking: "the X is, the Y is"
  POINTER "which is what", "which means", "worth knowing", "the point is"
  APHOR   aphorism-shaped closer: a short sentence ending a paragraph that states no number
  SPLICE  comma-spliced clause chains that keep qualifying

ANTI, APPOS and POINTER are hard failures. Say the thing once, with the number.
APHOR and SPLICE are rate limits; both are legitimate occasionally.

Usage:  python gate_antithesis.py path/to/main.tex
Exit 0 clean, 1 on any hard failure or exceeded rate.
"""
import os
import re
import sys

ANTI = [
    r"\brather than\b",
    r"\bnot (a|an|the)?\s?\w+[^.,;]{0,30}, (but|it|they|that) ",
    r"\bdoes not \w+[^.,;]{0,40}, it \w+",
    r"\bis not \w+[^.,;]{0,40}, it is\b",
    r"\bnot because\b[^.]{0,60}\bbut because\b",
    r"\bless (a|an)\b[^.]{0,40}\bthan (a|an)\b",
    r"\bis less about\b[^.]{0,40}\bthan about\b",
    r"\bwhat .{0,30} is not\b",
]

APPOS = [
    r"\bthe \w+ is, the \w+ is\b",
    r"\bthe \w+ is that, the \w+\b",
]

POINTER = [
    r"\bwhich is what\b",
    r"\bwhich means\b",
    r"\bworth knowing\b",
    r"\bthe point (here )?is\b",
    r"\bthat is the (point|finding|result)\b",
    r"\bwhat this means is\b",
]

APHOR_MAX_WORDS = 12     # a closer this short that carries no digit is an epigram
APHOR_RATE = 1.5         # percent of sentences
SPLICE_MIN_COMMAS = 3    # clauses strung with commas inside one sentence
SPLICE_RATE = 4.0        # percent of sentences


def sentences_with_lines(path):
    out = []
    for i, raw in enumerate(open(path, encoding="utf-8-sig").read().split("\n"), 1):
        st = raw.lstrip()
        # \item entries, headers and colon-introduced stubs are list scaffolding, not prose.
        # Counting them as paragraph-closers made the APHOR rate meaningless.
        if len(raw.strip()) < 40 or st.startswith(
            ("\\begin", "\\end", "\\caption", "%", "\\bibitem", "\\item", "\\section",
             "\\subsection", "\\subsubsection", "\\title", "\\author", "\\Description")
        ):
            continue
        if raw.rstrip().endswith((":", "\\\\")):
            continue
        s = re.sub(r"\\(label|ref|cite[a-z]*)\{[^}]*\}", " ", raw)
        s = re.sub(r"\\(section|subsection|subsubsection)\{[^}]*\}", " ", s)
        s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)
        s = re.sub(r"[{}$&~\\\[\]]", " ", s)
        s = re.sub(r"[ \t]+", " ", s).strip()
        parts = [p.strip() for p in re.split(r"(?<=[.!?]) +", s)]
        for j, sent in enumerate(parts):
            if len(sent) > 25:
                out.append((i, sent, j == len(parts) - 1))
    return out


def check(path):
    sents = sentences_with_lines(path)
    words = sum(len(s.split()) for _, s, _ in sents)
    print(f"\n=== {os.path.basename(path)}  ({len(sents)} sentences, {words} words) ===")
    failed = False

    for label, pats, desc in (
        ("ANTI", ANTI, "antithesis / reversal: state it once, with the magnitude"),
        ("APPOS", APPOS, "appositive stacking"),
        ("POINTER", POINTER, "pointer phrase standing in for the finding"),
    ):
        hits = [(ln, s, next(p for p in pats if re.search(p, s, re.I)))
                for ln, s, _ in sents if any(re.search(p, s, re.I) for p in pats)]
        if hits:
            failed = True
            print(f"  FAIL  {label}  {len(hits)} instance(s) -- {desc}")
            for ln, s, p in hits:
                print(f"        L{ln}: {s[:112]}")
        else:
            print(f"  PASS  {label}  none")

    # ADVISORY, not a gate. A short numberless closing sentence is sometimes an epigram and
    # sometimes a definition, a quoted prompt line or a cross-reference. The regex cannot tell
    # them apart, so this reports and does not fail. Read the list; do not tune it until it agrees.
    closers = [(ln, s) for ln, s, last in sents
               if last and len(s.split()) <= APHOR_MAX_WORDS and not re.search(r"\d", s)]
    pct = 100 * len(closers) / max(len(sents), 1)
    print(f"  NOTE  APHOR  {len(closers)} short numberless closers, {pct:.1f}% (advisory, needs eyes)")
    for ln, s in closers[:10]:
        print(f"        L{ln}: {s[:112]}")
    if len(closers) > 10:
        print(f"        ... and {len(closers)-10} more")

    splices = [(ln, s) for ln, s, _ in sents
               if s.count(",") >= SPLICE_MIN_COMMAS and len(s.split()) >= 30]
    pct = 100 * len(splices) / max(len(sents), 1)
    if pct > SPLICE_RATE:
        failed = True
        print(f"  FAIL  SPLICE  {len(splices)} sentences with {SPLICE_MIN_COMMAS}+ commas past 30 "
              f"words, {pct:.1f}% (ceiling {SPLICE_RATE}%)")
        for ln, s in sorted(splices, key=lambda x: -x[1].count(","))[:8]:
            print(f"        L{ln} [{s.count(',')} commas]: {s[:104]}")
        if len(splices) > 8:
            print(f"        ... and {len(splices)-8} more")
    else:
        print(f"  PASS  SPLICE  {len(splices)} comma-chained sentences, {pct:.1f}% (ceiling {SPLICE_RATE}%)")

    return failed


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit("usage: gate_antithesis.py <main.tex> [...]")
    bad = False
    for a in args:
        bad |= check(a)
    print("\nGATE FAILED." if bad else "\nGATE PASSED.")
    sys.exit(1 if bad else 0)
