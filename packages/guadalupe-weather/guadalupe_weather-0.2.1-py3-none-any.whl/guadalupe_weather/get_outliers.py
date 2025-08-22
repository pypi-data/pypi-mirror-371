from guadalupe_weather.get_daily_mean import get_daily_mean

import numpy as np
from typing import Any


def remove_outliers_for_column(data, column_name):
    data_copy = data.copy()
    column_data = data[column_name]
    linf, lsup = get_tukey_fences_by_daily_means(data_copy, column_name)
    outliers = get_outliers(column_data, linf, lsup)
    data_copy[column_name] = column_data.replace(outliers, np.nan)
    return data_copy


def get_tukey_fences_by_daily_means_for_variables_of_interest(data, list_of_variables):
    return [get_tukey_fences_by_daily_means(data, variable) for variable in list_of_variables]


def get_tukey_fences_by_daily_means(data_copy, column_name):
    daily_means = get_daily_mean(data_copy, column_name)
    linf, lsup = get_tukey_limits(daily_means)
    return linf, lsup


def get_outliers(Variable, inferior_limit, superior_limit) -> list[Any]:
    outliers = [x for x in Variable if x < inferior_limit or x > superior_limit]
    return outliers


def get_tukey_limits(Variable):
    Q1 = np.nanpercentile(Variable, 25)
    Q3 = np.nanpercentile(Variable, 75)
    IQR = Q3 - Q1
    linf = Q1 - 1.5 * IQR
    lsup = Q3 + 1.5 * IQR
    return linf, lsup
