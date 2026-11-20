"""Check connectivity to the configured PostgreSQL database."""

import asyncio

from sqlalchemy import text

from fraudfirstaid.db.session import engine


async def main() -> None:
    """Connect to PostgreSQL and display server information."""
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT current_database(), version()"))
            database_name, server_version = result.one()

            print(f"Connected to database '{database_name}'")
            print(f"PostgreSQL version: {server_version}")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
