"""
index/laspeyres.py

Laspeyres Price Index.

Formula:

L = Σ(P1 * Q0) / Σ(P0 * Q0) * 100

where:

P1 = current-period price
P0 = base-period price
Q0 = base-period quantity/weight

For airfare, Q0 can be represented by a suitable
base-period route/traffic weight.

TODO:
Replace the prototype weighting logic with your
DGCA-based basket/weights.
"""

import polars as pl


# ============================================================
# LASPEYRES
# ============================================================

def calculate_laspeyres(
    base_df: pl.DataFrame,
    current_df: pl.DataFrame,
    weights_df: pl.DataFrame,
) -> float | None:
    """
    Calculates the Laspeyres index.

    Expected weights_df columns:

        route
        weight

    Example:

        DEL-BOM    0.25
        DEL-BLR    0.20
    """

    if (
        base_df.is_empty()
        or current_df.is_empty()
        or weights_df.is_empty()
    ):
        return None


    # --------------------------------------------------------
    # CREATE ROUTE
    # --------------------------------------------------------

    base_df = base_df.with_columns(
        (
            pl.col("origin")
            + pl.lit("-")
            + pl.col("destination")
        ).alias("route")
    )

    current_df = current_df.with_columns(
        (
            pl.col("origin")
            + pl.lit("-")
            + pl.col("destination")
        ).alias("route")
    )


    # --------------------------------------------------------
    # BASE PRICE
    # --------------------------------------------------------

    base_prices = (
        base_df
        .group_by("route")
        .agg(
            pl.col("total_fare")
            .mean()
            .alias("P0")
        )
    )


    # --------------------------------------------------------
    # CURRENT PRICE
    # --------------------------------------------------------

    current_prices = (
        current_df
        .group_by("route")
        .agg(
            pl.col("total_fare")
            .mean()
            .alias("P1")
        )
    )


    # --------------------------------------------------------
    # JOIN
    # --------------------------------------------------------

    df = (
        base_prices
        .join(current_prices, on="route", how="inner")
        .join(weights_df, on="route", how="inner")
    )


    if df.is_empty():
        return None


    # --------------------------------------------------------
    # CALCULATE NUMERATOR
    # --------------------------------------------------------

    numerator = (
        df
        .select(
            (
                pl.col("P1")
                * pl.col("weight")
            )
            .sum()
        )
        .item()
    )


    # --------------------------------------------------------
    # CALCULATE DENOMINATOR
    # --------------------------------------------------------

    denominator = (
        df
        .select(
            (
                pl.col("P0")
                * pl.col("weight")
            )
            .sum()
        )
        .item()
    )


    if denominator == 0:
        return None


    return (numerator / denominator) * 100