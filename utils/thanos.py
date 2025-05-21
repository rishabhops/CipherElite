import os
import random
from typing import List

_s1 = [chr(c) for c in [113, 74, 55, 110, 76, 48, 102, 80, 98, 88]]
_s2 = [chr(c) for c in [85, 53, 109, 89, 81, 51, 114, 75, 100, 90, 57, 119, 71, 108, 49]]

SALT1 = "".join(_s1)
SALT2 = "".join(_s2)


if len(SALT1) != 10 or len(SALT2) != 15:
    raise RuntimeError("don't try to kang 🤫")

def _positions(length: int, count: int, seed: str) -> List[int]:
    
    rng = random.Random(seed)
    return sorted(rng.sample(range(length + count), count))

def thanos_protect(obf: str) -> str:


    pos2 = _positions(len(obf) - len(SALT2), len(SALT2), seed=SALT2)
    lst = list(obf)
    for idx in sorted(pos2, reverse=True):
        lst.pop(idx)
    s1 = "".join(lst)

    pos1 = _positions(len(s1) - len(SALT1), len(SALT1), seed=SALT1)
    lst = list(s1)
    for idx in sorted(pos1, reverse=True):
        lst.pop(idx)
    return "".join(lst)
