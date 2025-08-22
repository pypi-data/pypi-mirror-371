"""Paquete analisis de clima en Isla Guadalupe"""

__version__ = "0.2.0"
from .get_outliers import remove_outliers_for_column  # noqa
from .cli import cli  # noqa
from .plot_weather_variables import *  # noqa
from .get_weather_data import *  # noqa
