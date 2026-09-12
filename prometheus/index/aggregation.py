"""
index/aggregation.py

Aggregates route-level indices into the overall
Airfare Price Index (APIx).
"""

import polars as pl

from index.jevons import calculate_route_jevons
from index.weighting import get_base_weights


# ============================================================
# AGGREGATE ROUTE INDICES
# ============================================================

def aggregate_route_indices(
    route_indices: pl.DataFrame,
    weights_df: pl.DataFrame,
) -> float | None:
    """
    Aggregates route-level indices using route weights.

    Expected route_indices:

        route | jevons_index

    Expected weights_df:

        route | weight
    """

    if (
        route_indices.is_empty()
        or weights_df.is_empty()
    ):
        return None


    # --------------------------------------------------------
    # JOIN INDICES WITH WEIGHTS
    # --------------------------------------------------------

    df = route_indices.join(
        weights_df,
        on="route",
        how="inner",
    )


    if df.is_empty():
        return None


    # --------------------------------------------------------
    # WEIGHTED INDEX
    # --------------------------------------------------------

    weighted_sum = (
        df
        .select(
            (
                pl.col("jevons_index")
                * pl.col("weight")
            )
            .sum()
        )
        .item()
    )


    # --------------------------------------------------------
    # HANDLE MISSING ROUTES
    # --------------------------------------------------------

    total_available_weight = (
        df["weight"].sum()
    )


    if total_available_weight == 0:
        return None


    # --------------------------------------------------------
    # NORMALISE AVAILABLE WEIGHTS
    # --------------------------------------------------------

    # Important:
    #
    # If one route has no data today, we should not
    # automatically let its missing value make the
    # entire index zero.
    #
    # We re-normalise the available route weights.

    api_x = (
        weighted_sum
        / total_available_weight
    )


    return api_x


# ============================================================
# COMPLETE APIx CALCULATION
# ============================================================

def calculate_api_x(
    base_df: pl.DataFrame,
    current_df: pl.DataFrame,
) -> float | None:
    """
    Complete pipeline:

        Base fares
             ↓
        Current fares
             ↓
        Route Jevons
             ↓
        DGCA route weights
             ↓
        Overall APIx
    """

    # --------------------------------------------------------
    # 1. CALCULATE ROUTE INDICES
    # --------------------------------------------------------

    route_indices = calculate_route_jevons(
        base_df,
        current_df
    )


    if route_indices.is_empty():
        return None


    # --------------------------------------------------------
    # 2. LOAD ROUTE WEIGHTS
    # --------------------------------------------------------

    weights_df = get_base_weights()


    # --------------------------------------------------------
    # 3. AGGREGATE
    # --------------------------------------------------------

    api_x = aggregate_route_indices(
        route_indices,
        weights_df
    )


    return api_x


# ============================================================
# GENERATE FULL INDEX RESULT
# ============================================================

def generate_index_result(
    base_df: pl.DataFrame,
    current_df: pl.DataFrame,
) -> dict:
    """
    Generates a complete APIx result.

    Useful for passing the result to FastAPI
    or saving it into PostgreSQL.
    """

    route_indices = calculate_route_jevons(
        base_df,
        current_df
    )


    weights_df = get_base_weights()


    api_x = aggregate_route_indices(
        route_indices,
        weights_df
    )


    return {

        # TODO:
        # Replace these with actual observation dates.

        "base_period": "TODO_BASE_PERIOD",

        "current_period": "TODO_CURRENT_PERIOD",

        "index_type": "JEVONS",

        "api_x": api_x,

        "route_indices":
            route_indices.to_dicts(),

        "weights":
            weights_df.to_dicts(),
    }