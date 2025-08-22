"""Paquete analisis de clima en Isla Guadalupe"""

__version__ = "0.2.2"
from .get_outliers import remove_outliers_for_column, get_tukey_fences_by_daily_means  # noqa
from .cli import cli  # noqa
from .plot_weather_variables import *  # noqa
from .get_weather_data import *  # noqa
