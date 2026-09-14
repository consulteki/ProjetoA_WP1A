"""Nomes, tipos e significado documentado das 52 variáveis de processo do TEP.

Referência: Downs & Vogel (1993); Russell, Chiang & Braatz (2000);
schema canônico em ``wp1a.data.schema`` (xmeas_1..41 + xmv_1..11).
"""

from __future__ import annotations

from wp1a.data.schema import FEATURE_COLUMNS

# Significado das variáveis conforme a literatura de referência do TEP
# (Downs & Vogel 1993; Chiang/Russell/Braatz). Índices 1-based alinhados
# aos nomes canônicos xmeas_i / xmv_i.
XMEAS_MEANINGS: dict[int, str] = {
    1: "A Feed (stream 1)",
    2: "D Feed (stream 2)",
    3: "E Feed (stream 3)",
    4: "A and C Feed (stream 4)",
    5: "Recycle Flow (stream 8)",
    6: "Reactor Feed Rate (stream 6)",
    7: "Reactor Pressure",
    8: "Reactor Level",
    9: "Reactor Temperature",
    10: "Purge Rate (stream 9)",
    11: "Product Separator Temperature",
    12: "Product Separator Level",
    13: "Product Separator Pressure",
    14: "Product Separator Underflow (stream 10)",
    15: "Stripper Level",
    16: "Stripper Pressure",
    17: "Stripper Underflow (stream 11)",
    18: "Stripper Temperature",
    19: "Stripper Steam Flow",
    20: "Compressor Work",
    21: "Reactor Cooling Water Outlet Temperature",
    22: "Separator Cooling Water Outlet Temperature",
    23: "Component A to Reactor (stream 6) mole fraction",
    24: "Component B to Reactor (stream 6) mole fraction",
    25: "Component C to Reactor (stream 6) mole fraction",
    26: "Component D to Reactor (stream 6) mole fraction",
    27: "Component E to Reactor (stream 6) mole fraction",
    28: "Component F to Reactor (stream 6) mole fraction",
    29: "Component A in Purge (stream 9) mole fraction",
    30: "Component B in Purge (stream 9) mole fraction",
    31: "Component C in Purge (stream 9) mole fraction",
    32: "Component D in Purge (stream 9) mole fraction",
    33: "Component E in Purge (stream 9) mole fraction",
    34: "Component F in Purge (stream 9) mole fraction",
    35: "Component G in Purge (stream 9) mole fraction",
    36: "Component H in Purge (stream 9) mole fraction",
    37: "Component D in Product (stream 11) mole fraction",
    38: "Component E in Product (stream 11) mole fraction",
    39: "Component F in Product (stream 11) mole fraction",
    40: "Component G in Product (stream 11) mole fraction",
    41: "Component H in Product (stream 11) mole fraction",
}

XMV_MEANINGS: dict[int, str] = {
    1: "D Feed Flow (stream 2)",
    2: "E Feed Flow (stream 3)",
    3: "A Feed Flow (stream 1)",
    4: "A and C Feed Flow (stream 4)",
    5: "Compressor Recycle Valve",
    6: "Purge Valve (stream 9)",
    7: "Separator Pot Liquid Flow (stream 10)",
    8: "Stripper Liquid Product Flow (stream 11)",
    9: "Stripper Steam Valve",
    10: "Reactor Cooling Water Flow",
    11: "Condenser Cooling Water Flow",
}

FAULT_MEANINGS: dict[int, str] = {
    0: "Normal operation",
    1: "IDV(1) A/C Feed Ratio, B Composition Constant (Stream 4) — Step",
    2: "IDV(2) B Composition, A/C Ratio Constant (Stream 4) — Step",
    3: "IDV(3) D Feed Temperature (Stream 2) — Step",
    4: "IDV(4) Reactor Cooling Water Inlet Temperature — Step",
    5: "IDV(5) Condenser Cooling Water Inlet Temperature — Step",
    6: "IDV(6) A Feed Loss (Stream 1) — Step",
    7: "IDV(7) C Header Pressure Loss (Stream 4) — Step",
    8: "IDV(8) A, B, C Feed Composition (Stream 4) — Random",
    9: "IDV(9) D Feed Temperature (Stream 2) — Random",
    10: "IDV(10) C Feed Temperature (Stream 4) — Random",
    11: "IDV(11) Reactor Cooling Water Inlet Temperature — Random",
    12: "IDV(12) Condenser Cooling Water Inlet Temperature — Random",
    13: "IDV(13) Reaction Kinetics — Slow Drift",
    14: "IDV(14) Reactor Cooling Water Valve — Sticking",
    15: "IDV(15) Condenser Cooling Water Valve — Sticking",
    16: "IDV(16) Unknown",
    17: "IDV(17) Unknown",
    18: "IDV(18) Unknown",
    19: "IDV(19) Unknown",
    20: "IDV(20) Unknown",
    21: "IDV(21) Valve position constant (Stream 4) — fora do escopo normativo DS-03",
}


def variable_catalog() -> list[dict[str, str]]:
    """Return the catalog of the 52 canonical process variables."""
    rows: list[dict[str, str]] = []
    for i in range(1, 42):
        name = f"xmeas_{i}"
        rows.append(
            {
                "column": name,
                "dtype_expected": "float64",
                "family": "XMEAS",
                "meaning": XMEAS_MEANINGS[i],
            }
        )
    for i in range(1, 12):
        name = f"xmv_{i}"
        rows.append(
            {
                "column": name,
                "dtype_expected": "float64",
                "family": "XMV",
                "meaning": XMV_MEANINGS[i],
            }
        )
    assert [r["column"] for r in rows] == list(FEATURE_COLUMNS)
    return rows
