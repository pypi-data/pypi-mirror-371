import typer

from healthcheck_cli.commands.health import app as health_app

app = typer.Typer(help="🩺 API Health Checker - Monitor your APIs with ease")


app.add_typer(health_app, name="health")


if __name__ == "__main__":
    app()
