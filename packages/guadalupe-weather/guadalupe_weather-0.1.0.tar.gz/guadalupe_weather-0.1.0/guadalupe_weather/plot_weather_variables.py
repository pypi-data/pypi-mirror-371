import calendar
import numpy as np
import matplotlib.pyplot as plt

from geci_plots import geci_plot


def plot_average_rain_by_zone(data_to_plot, box_plot_data, png_path, year_list):
    fontsize = 20
    ticks_positions = np.linspace(1, 12, 12)
    months_labels = get_months_labels_list()
    fig, ax = geci_plot()
    box_plot = ax.boxplot(box_plot_data, patch_artist=True, boxprops=dict(facecolor="white"))
    string_label = get_string_label(year_list)
    ax.plot(
        data_to_plot.index,
        data_to_plot.values,
        "-o",
        linewidth=2,
        markeredgecolor="k",
        markersize=5,
        label=string_label,
    )
    plt.xticks([*ticks_positions, 13], [*months_labels, ""], size=fontsize, rotation=90)
    plt.yticks(size=fontsize)
    plt.ylabel("Monthly rainfall (mm/month)", size=fontsize)
    y_lim_min = -0.1
    y_lim_max = get_y_max_limit(box_plot_data)
    ax.set_ylim(
        y_lim_min,
        y_lim_max,
    )
    handles, labels = ax.get_legend_handles_labels()
    plt.legend(
        [*handles, box_plot["boxes"].pop()], [*labels, "Rain typical year"], fontsize=fontsize
    )
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)


def plot_average_temperature_by_zone(data_to_plot, box_plot_data, png_path, year_list):
    fontsize = 20
    ticks_positions = np.linspace(1, 12, 12)
    months_labels = get_months_labels_list()
    fig, ax = geci_plot()
    box_plot = ax.boxplot(box_plot_data, patch_artist=True, boxprops=dict(facecolor="white"))
    string_label = get_string_label_temperature(year_list)
    ax.plot(
        data_to_plot.index,
        data_to_plot.values,
        "-o",
        linewidth=2,
        markeredgecolor="k",
        markersize=5,
        label=string_label,
    )
    plt.xticks([*ticks_positions, 13], [*months_labels, ""], size=fontsize, rotation=90)
    plt.yticks(size=fontsize)
    plt.ylabel(r"Temperature ($^{\circ}C$)", size=fontsize)
    y_lim_min = -0.1
    y_lim_max = 30
    ax.set_ylim(
        y_lim_min,
        y_lim_max,
    )
    handles, labels = ax.get_legend_handles_labels()
    plt.legend(
        [*handles, box_plot["boxes"].pop()],
        [*labels, "Temperature typical year"],
        fontsize=fontsize,
    )
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)


def get_y_max_limit(all_years_data):
    return 50


def get_string_label_temperature(years):
    if isinstance(years, list):
        return f"Temperature in {*years, }"
    return f"Temperature in {years}"


def get_string_label(years):
    if isinstance(years, list):
        return f"Rain in {*years, }"
    return f"Rain in {years}"


def get_months_labels_list() -> list:
    return list(calendar.month_name[1:])
