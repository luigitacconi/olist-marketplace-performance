import pathlib as pt

import pandas as pd


RAW = pt.Path(__file__).parent.parent / "data" / "raw"

_CACHE = {}


def load(file_name):
    if file_name not in _CACHE:
        _CACHE[file_name] = pd.read_csv(RAW / file_name)
    return _CACHE[file_name].copy()
