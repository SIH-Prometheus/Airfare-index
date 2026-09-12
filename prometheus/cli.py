import typer
from prometheus.config import settings

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

if __name__ == "__main__":
    app()
