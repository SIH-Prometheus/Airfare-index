"""
database/connection.py

Creates and manages the PostgreSQL database connection.

All other modules should import `engine` from this file
instead of creating their own database connections.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

# TODO:
# Add the following variables to your .env file:
#
# DATABASE_URL=postgresql://username:password@localhost:5432/airfare
#
# Example:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/airfare_db

DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set. "
        "Please add DATABASE_URL to your .env file."
    )


# ============================================================
# CREATE DATABASE ENGINE
# ============================================================

engine: Engine = create_engine(
    DATABASE_URL,

    # TODO:
    # Adjust these according to your deployment.
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


# ============================================================
# TEST CONNECTION
# ============================================================

def test_connection():
    """
    Tests whether PostgreSQL is reachable.
    """

    try:
        with engine.connect() as connection:
            print("PostgreSQL connection successful.")

    except Exception as e:
        print("PostgreSQL connection failed.")
        print(f"Error: {e}")


# Uncomment when testing manually:
#
# if __name__ == "__main__":
#     test_connection()