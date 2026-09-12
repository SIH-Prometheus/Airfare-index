"""
index/jevons.py

Calculates the Jevons Price Index.

Basic formula:

J = (Product of price relatives) ^ (1/n)

where:

price relative = current price / base price

Index = J * 100
"""

import math

import polars as pl
from sqlalchemy import text

from database.connection import engine


# ============================================================
# CONFIGURATION
# ============================================================

FARES_TABLE = "fares"


# ============================================================
# FETCH FARES FROM POSTGRESQL
# ============================================================

def get_fares(
    start_date: str,
    end_date: str,
    routes: list[str] | None = None,
    lead_days: list[int] | None = None,
) -> pl.DataFrame:
    """
    Fetch fare observations from PostgreSQL.

    Parameters
    ----------
    start_date:
        Start of observation period.

    end_date:
        End of observation period.

    routes:
        Optional list such as:
        ["DEL-BOM", "DEL-BLR"]

    lead_days:
        Optional list such as:
        [1, 7, 15, 30]

    Returns
    -------
    Polars DataFrame
    """

    query = f"""
        SELECT
            observation_date,
            origin,
            destination,
            airline,
            lead_days,
            total_fare
        FROM {FARES_TABLE}
        WHERE
            observation_date >= :start_date
            AND observation_date <= :end_date
            AND total_fare IS NOT NULL
            AND total_fare > 0
    """

    params = {
        "start_date": start_date,
        "end_date": end_date,
    }

    # --------------------------------------------------------
    # OPTIONAL ROUTE FILTER
    # --------------------------------------------------------

    if routes:

        route_conditions = []

        for i, route in enumerate(routes):

            origin, destination = route.split("-")

            route_conditions.append(
                f"(origin = :origin_{i} "
                f"AND destination = :destination_{i})"
            )

            params[f"origin_{i}"] = origin
            params[f"destination_{i}"] = destination

        query += " AND (" + " OR ".join(route_conditions) + ")"


    # --------------------------------------------------------
    # OPTIONAL LEAD-TIME FILTER
    # --------------------------------------------------------

    if lead_days:

        placeholders = []

        for i, value in enumerate(lead_days):

            placeholder = f":lead_{i}"

            placeholders.append(placeholder)

            params[f"lead_{i}"] = value

        query += f" AND lead_days IN ({', '.join(placeholders)})"


    # --------------------------------------------------------
    # EXECUTE QUERY
    # --------------------------------------------------------

    with engine.connect() as connection:

        result = connection.execute(
            text(query),
            params
        )

        rows = result.fetchall()

        columns = result.keys()


    if not rows:

        return pl.DataFrame()


    return pl.DataFrame(
        rows,
        schema=list(columns),
        orient="row"
    )


# ============================================================
# CALCULATE PRICE RELATIVES
# ============================================================

def calculate_price_relatives(
    base_df: pl.DataFrame,
    current_df: pl.DataFrame,
) -> pl.DataFrame:
    """
    Calculates current price / base price.

    Prices are first averaged for each:
        route + airline + lead_days

    This keeps the comparison consistent.
    """

    if base_df.is_empty() or current_df.is_empty():
        return pl.DataFrame()


    # --------------------------------------------------------
    # CREATE ROUTE COLUMN
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
    # BASE PERIOD AVERAGE
    # --------------------------------------------------------

    base_prices = (
        base_df
        .group_by(
            [
                "route",
                "airline",
                "lead_days",
            ]
        )
        .agg(
            pl.col("total_fare")
            .mean()
            .alias("base_price")
        )
    )


    # --------------------------------------------------------
    # CURRENT PERIOD AVERAGE
    # --------------------------------------------------------

    current_prices = (
        current_df
        .group_by(
            [
                "route",
                "airline",
                "lead_days",
            ]
        )
        .agg(
            pl.col("total_fare")
            .mean()
            .alias("current_price")
        )
    )


    # --------------------------------------------------------
    # JOIN BASE AND CURRENT
    # --------------------------------------------------------

    merged = current_prices.join(
        base_prices,
        on=[
            "route",
            "airline",
            "lead_days",
        ],
        how="inner",
    )


    # --------------------------------------------------------
    # PRICE RELATIVE
    # --------------------------------------------------------

    merged = merged.with_columns(

        (
            pl.col("current_price")
            / pl.col("base_price")
        ).alias("price_relative")

    )


    # Remove invalid values.

    merged = merged.filter(
        pl.col("price_relative").is_finite()
        & (pl.col("price_relative") > 0)
    )


    return merged


# ============================================================
# JEVONS CALCULATION
# ============================================================

def calculate_jevons(
    base_df: pl.DataFrame,
    current_df: pl.DataFrame,
) -> float | None:
    """
    Calculates the overall Jevons index.

    Returns:
        Index value where 100 = base period.
    """

    relatives = calculate_price_relatives(
        base_df,
        current_df
    )


    if relatives.is_empty():
        return None


    values = relatives["price_relative"].to_list()


    # --------------------------------------------------------
    # GEOMETRIC MEAN
    # --------------------------------------------------------

    log_sum = sum(
        math.log(value)
        for value in values
    )

    geometric_mean = math.exp(
        log_sum / len(values)
    )


    # --------------------------------------------------------
    # INDEX
    # --------------------------------------------------------

    index_value = geometric_mean * 100


    return index_value


# ============================================================
# ROUTE-LEVEL JEVONS
# ============================================================

def calculate_route_jevons(
    base_df: pl.DataFrame,
    current_df: pl.DataFrame,
) -> pl.DataFrame:
    """
    Calculates Jevons index separately for every route.

    Returns:

        route | index
    """

    relatives = calculate_price_relatives(
        base_df,
        current_df
    )


    if relatives.is_empty():
        return pl.DataFrame()


    result = (
        relatives
        .group_by("route")
        .agg(

            (
                pl.col("price_relative")
                .log()
                .mean()
                .exp()
                * 100
            ).alias("jevons_index")

        )
        .sort("route")
    )


    return result