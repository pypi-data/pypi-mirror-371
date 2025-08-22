import typer
import guadalupe_weather as gw

cli = typer.Typer()


@cli.command()
def version():
    print(gw.__version__)
