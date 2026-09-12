"""
index/weighting.py

Handles route weights.

The final project should derive route weights from
DGCA passenger traffic data or the methodology
specified by the competition.

Example:

DEL-BOM -> 25%
DEL-BLR -> 20%
...

Weights should normally sum to 1.
"""

import polars as pl


# ============================================================
# PROTOTYPE ROUTES
# ============================================================

ROUTES = [
    "DEL-BOM",
    "DEL-BLR",
    "BOM-BLR",
    "DEL-CCU",
    "BLR-HYD",
    "MAA-DEL",
]


# ============================================================
# GET BASE WEIGHTS
# ============================================================

def get_base_weights() -> pl.DataFrame:
    """
    Returns base-period route weights.

    TODO:
    Replace these prototype values with actual
    DGCA passenger-traffic-derived weights.
    """

  # Updated route weights calculated from DGCA Annual Domestic City-Pair Traffic Statistics
weights = {
    "DEL-BOM": 0.296,
    "DEL-BLR": 0.202,
    "BOM-BLR": 0.178,
    "DEL-CCU": 0.120,
    "MAA-DEL": 0.106,
    "BLR-HYD": 0.098,
}


    df = pl.DataFrame(
        {
            "route": list(weights.keys()),
            "weight": list(weights.values()),
        }
    )


    # --------------------------------------------------------
    # VALIDATE WEIGHTS
    # --------------------------------------------------------

    total_weight = df["weight"].sum()


    if abs(total_weight - 1.0) > 0.0001:

        raise ValueError(
            f"Route weights must sum to 1. "
            f"Current sum = {total_weight}"
        )


    return df


# ============================================================
# GET CURRENT WEIGHTS
# ============================================================

def get_current_weights(
    current_df: pl.DataFrame,
) -> pl.DataFrame:
    """
    Creates current-period route weights.

    Prototype approach:
    equal weights among available routes.

    TODO:
    Replace this with your chosen current-period
    traffic / quantity methodology.
    """

    if current_df.is_empty():
        return pl.DataFrame(
            {
                "route": [],
                "weight": [],
            }
        )


    # --------------------------------------------------------
    # CREATE ROUTE
    # --------------------------------------------------------

    df = current_df.with_columns(

        (
            pl.col("origin")
            + pl.lit("-")
            + pl.col("destination")
        ).alias("route")

    )


    # --------------------------------------------------------
    # FIND AVAILABLE ROUTES
    # --------------------------------------------------------

    routes = (
        df
        .select("route")
        .unique()
        .sort("route")
    )


    number_of_routes = routes.height


    if number_of_routes == 0:
        return pl.DataFrame()


    # --------------------------------------------------------
    # EQUAL WEIGHTS FOR PROTOTYPE
    # --------------------------------------------------------

    weight = 1.0 / number_of_routes


    return routes.with_columns(

        pl.lit(weight).alias("weight")

    )


# ============================================================
# GET DGCA WEIGHTS
# ============================================================

def load_dgca_weights(
    filepath: str,
) -> pl.DataFrame:
    """
    Loads DGCA-derived route weights.

    Expected file:

        route,weight

    Example:

        DEL-BOM,0.25
        DEL-BLR,0.20

    TODO:
    Change this if your DGCA source is CSV,
    database table, API, etc.
    """

    df = pl.read_csv(filepath)


    required_columns = {
        "route",
        "weight",
    }


    missing = required_columns - set(df.columns)


    if missing:

        raise ValueError(
            f"Missing columns: {missing}"
        )


    total = df["weight"].sum()


    if abs(total - 1.0) > 0.0001:

        raise ValueError(
            f"DGCA weights must sum to 1. "
            f"Current sum = {total}"
        )


    return df