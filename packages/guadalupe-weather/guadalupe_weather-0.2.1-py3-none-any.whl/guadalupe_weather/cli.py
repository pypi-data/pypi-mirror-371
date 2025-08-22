import typer
from typing_extensions import Annotated
import pandas as pd
from guadalupe_weather.get_outliers import remove_outliers_for_column
import guadalupe_weather as gw

cli = typer.Typer()


@cli.command()
def remove_outliers(
    input_path: Annotated[str, typer.Option()],
    column_name: Annotated[str, typer.Option()],
    output_path: Annotated[str, typer.Option()],
):
    data = pd.read_csv(input_path)
    no_outliers_df = remove_outliers_for_column(data, column_name)
    no_outliers_df.to_csv(output_path, index=False)


@cli.command()
def version():
    print(gw.__version__)
