"""
index/fisher.py

Fisher Ideal Price Index.

Formula:

F = sqrt(L × P)

L = Laspeyres index
P = Paasche index
"""

import math

import polars as pl

from index.laspeyres import calculate_laspeyres
from index.paasche import calculate_paasche


# ============================================================
# FISHER INDEX
# ============================================================

def calculate_fisher(
    base_df: pl.DataFrame,
    current_df: pl.DataFrame,
    base_weights_df: pl.DataFrame,
    current_weights_df: pl.DataFrame,
) -> float | None:
    """
    Calculates Fisher Ideal Index.
    """

    laspeyres = calculate_laspeyres(
        base_df,
        current_df,
        base_weights_df
    )


    paasche = calculate_paasche(
        base_df,
        current_df,
        current_weights_df
    )


    if laspeyres is None or paasche is None:
        return None


    if laspeyres < 0 or paasche < 0:
        return None


    fisher = math.sqrt(
        laspeyres * paasche
    )


    return fisher