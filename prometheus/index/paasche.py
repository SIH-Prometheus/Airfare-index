"""
index/paasche.py

Paasche Price Index.

Formula:

P = Σ(P1 * Q1) / Σ(P0 * Q1) * 100

For the prototype, current-period route weights
are used as Q1.

TODO:
Replace the prototype current-period weights with
the exact methodology selected for the competition.
"""

import polars as pl


# ============================================================
# PAASCHE
# ============================================================

def calculate_paasche(
    base_df: pl.DataFrame,
    current_df: pl.DataFrame,
    current_weights_df: pl.DataFrame,
) -> float | None:
    """
    Calculates Paasche index.

    current_weights_df should contain:

        route
        weight
    """

    if (
        base_df.is_empty()
        or current_df.is_empty()
        or current_weights_df.is_empty()
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
    # BASE PRICES
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
    # CURRENT PRICES
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
        .join(
            current_weights_df,
            on="route",
            how="inner"
        )
    )


    if df.is_empty():
        return None


    # --------------------------------------------------------
    # NUMERATOR
    # Σ(P1 × Q1)
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
    # DENOMINATOR
    # Σ(P0 × Q1)
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