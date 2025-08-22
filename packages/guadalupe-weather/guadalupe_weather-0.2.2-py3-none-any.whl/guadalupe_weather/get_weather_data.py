import numpy as np
import pandas as pd


def get_multiannual_monthly_cumulative_rain(all_data_path, years_list):
    multiannual_data = [
        get_monthly_cumulative_rain_by_year(all_data_path, year) for year in years_list
    ]
    multiannual_average = pd.concat(multiannual_data, axis=1).agg("mean", 1)
    return multiannual_average.sort_index()


def get_multiannual_monthly_temperature(all_data_path, years_list):
    multiannual_data = [get_monthly_temperature_by_year(all_data_path, year) for year in years_list]
    multiannual_average = pd.concat(multiannual_data, axis=1).agg("mean", 1)
    return multiannual_average.sort_index()


def get_monthly_cumulative_rain_by_year(monthly_average_rain_path, year):
    data_by_year = get_data_by_year(monthly_average_rain_path, year)
    return get_monthly_average_cumulative_rain_by_zone(data_by_year)


def get_monthly_temperature_by_year(monthly_average_rain_path, year):
    data_by_year = get_data_by_year(monthly_average_rain_path, year)
    return get_monthly_average_temperature_by_zone(data_by_year)


def get_data_by_year(monthly_average_data, year):
    all_data = pd.read_csv(monthly_average_data)
    data_by_year = all_data[all_data["Year"] == year]
    return data_by_year


def get_monthly_average_cumulative_rain_by_zone(data_by_year):
    return data_by_year.groupby(["Month"])["Cumulative_rain"].mean()


def get_monthly_and_annual_average_cumulative_rain_by_zone(data):
    return data.groupby(["Year", "Month"], as_index=False)["Cumulative_rain"].mean()


def get_monthly_average_temperature_by_zone(data_by_year):
    return data_by_year.groupby(["Month"])["Avg_Temp_Out"].mean()


def get_box_plot_data(monthly_average_rain_path):
    all_data = pd.read_csv(monthly_average_rain_path)
    data_grouped_by_month = all_data.groupby(["Month"])
    box_plot_data = [
        month_data[1]["Cumulative_rain"].to_numpy() for month_data in data_grouped_by_month
    ]
    return box_plot_data


def get_box_plot_data_temperature(monthly_average_rain_path):
    all_data = pd.read_csv(monthly_average_rain_path)
    data_grouped_by_month = all_data.groupby(["Month"])
    box_plot_data = [
        month_data[1]["Avg_Temp_Out"].to_numpy() for month_data in data_grouped_by_month
    ]
    box_plot_data = [month[~np.isnan(month)] for month in box_plot_data]
    return box_plot_data
