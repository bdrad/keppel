import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple

from pdfplumber.page import Page

round_to_nearest_k: callable = lambda number, k: round(number * k) / k


def term_str(s, terms=(".", "!", "?", ":")) -> bool:
    return s and s.rstrip().endswith(terms)


def clip_overlap(body, txt, min_overlap=8):
    # Find the longest common suffix between body and txt
    overlap = 0
    body, txt = body.rstrip(), txt.lstrip()
    for i in range(1, min(len(body), len(txt)) + 1):
        if body[-i:] == txt[:i]:
            overlap = i
    # rt the non-overlapping part of txt to body
    return txt[overlap:] if overlap >= min_overlap else txt


def extract_chapters(fname: Path) -> List[int]:
    # TODO implement this
    # - this works only iff the PDF has indexs (embedded Table of Contents)
    # - this lacks the final page of end of final chapter
    import fitz

    pdf = fitz.open(fname)

    chapters = []
    for lvl, title, pg in pdf.get_toc():
        if lvl != 1:
            continue
        # if re.search(r"chapter \d+", title, flags=re.IGNORECASE):
        # print(f"{title}\tPage: {pg}")
        chapters.append(pg - 1)  # 0-indexed
    return chapters


def compact_json(s: str) -> str:
    # % See appendix for example
    # Remove leading and tRailing whitespace within JSON objects
    s = re.sub(r"{\s+", "{ ", s)
    s = re.sub(r"\s+}", " }", s)

    # Remove whitespace after commas within JSON arrays
    s = re.sub(r",\s+", ", ", s)

    # Remove leading and trailing whitespace within JSON arrays
    s = re.sub(r"\[\s+", "[ ", s)
    s = re.sub(r"\s+\]", " ]", s)

    s = re.sub(r' ("body_font")', r"\n    \1", s)
    s = re.sub(r"( },) ({)", r"\1\n  \2", s)
    return s


def merge_dicts(base_data: dict, new_data: dict) -> dict:
    out = dict(base_data)
    for k, v in new_data.items():
        if k in out:
            if isinstance(v, dict) and isinstance(out[k], dict):
                out[k] = merge_dicts(out[k], v)
            else:
                out[k] = v
        else:
            out[k] = v
    return out
