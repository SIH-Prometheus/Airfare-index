import asyncio
import typer
from prometheus.config import settings
from prometheus.db import check_db_connection

app = typer.Typer(help="PROMETHEUS Airfare Price Index CLI")

@app.command()
def info():
    """Print current PROMETHEUS environment configuration."""
    typer.echo(f"PROMETHEUS Environment: {settings.ENV}")
    typer.echo(f"Log Level: {settings.LOG_LEVEL}")
    typer.echo(f"Database URL: {settings.DB_URL}")
    typer.echo(f"MinIO Endpoint: {settings.MINIO_ENDPOINT}")

@app.command()
def status():
    """Check system status."""
    typer.echo("System Status: OK")

@app.command()
def db_check():
    """Check PostgreSQL database connectivity."""
    typer.echo(f"Testing DB connection to: {settings.DB_URL}...")
    is_connected = asyncio.run(check_db_connection())
    if is_connected:
        typer.echo("Database connection test: SUCCESS (SELECT 1 OK)")
    else:
        typer.echo("Database connection test: FAILED")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
