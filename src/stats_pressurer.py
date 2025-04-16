# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import pandas as pd
import stats_calculators as sc
import glob
from natsort import natsorted
from matplotlib.pyplot import cm
import config as c
from tqdm import tqdm
import amv_calculators as ac
from datetime import timedelta
from parameters import parameters
from datetime import datetime
import histograms

THRESHOLDS = [10, 100]


def calc_days(thresh, days, tag):

    ds_total = xr.open_dataset("../data/processed/" + tag + ".nc")
    ds_total = histograms.compute(ds_total)
    error_square_mean = sc.weighted_mean(ds_total["error_square"])
    rmsvd = np.sqrt(error_square_mean)

    for day in tqdm(days):
        for time in ("am", "pm"):
            d = {
                "pressure": [],
                "error_sum": [],
                "speed_sum": [],
                "denominator": [],
                "angle_sum": [],
                "angle_denominator": [],
                "yield": [],
            }
            file_name = (
                day.strftime("../data/processed/" + tag + "_%m_%d_%Y")
                + "_"
                + time
                + ".nc"
            )
            ds = ds_total.sel(satellite="snpp", day=day, time=time)
            ds["angle"] = abs(ds["angle"])
            for pressure in ds["plev"].values:
                ds_unit = ds.sel(plev=pressure, method="nearest")
                error_sum = sc.weighted_sum(ds_unit["error_square"])
                speed_sum = sc.weighted_sum(ds_unit["speed"])
                angle_sum = sc.weighted_sum(ds_unit["angle"])

                data = ds_unit["error_square"].values
                counts = np.count_nonzero(~np.isnan(data))

                denominator = sc.weights_sum(ds_unit["error_square"])
                angle_denominator = sc.weights_sum(ds_unit["angle"])

                pressure = int(round(pressure))
                d["pressure"].append(pressure)
                d["error_sum"].append(error_sum)
                d["angle_sum"].append(angle_sum)
                d["speed_sum"].append(speed_sum)
                d["denominator"].append(denominator)
                d["angle_denominator"].append(angle_denominator)
                d["yield"].append(counts)
            df = pd.DataFrame(data=d)
            df.set_index("pressure", drop=True)
            df.to_csv(
                "../data/interim/dataframes/t"
                + str(thresh)
                + "_"
                + day.strftime("%m_%d_%Y_")
                + time
                + tag
                + ".csv"
            )
    return df["pressure"].values, rmsvd


def calc_means(thresh, days, tag):

    file_name = day.strftime("../data/processed/" + tag + ".nc")
    ds = xr.open_dataset(file_name)
    ds = ds.loc[{"satellite": "snpp"}]
    ds = histograms.compute(ds)
    ds["angle"] = abs(ds["angle"])

    error_sum = sc.weighted_sum(ds_unit["error_square"])
    speed_sum = sc.weighted_sum(ds_unit["speed"])
    angle_sum = sc.weighted_sum(ds_unit["angle"])

    data = ds_unit["error_square"].values
    counts = np.count_nonzero(~np.isnan(data))

    denominator = sc.weights_sum(ds_unit["error_square"])
    angle_denominator = sc.weights_sum(ds_unit["angle"])

    d["error_sum"] = error_sum
    d["angle_sum"] = angle_sum
    d["speed_sum"] = speed_sum
    d["denominator"] = denominator
    d["angle_denominator"] = angle_denominator
    d["yield"] = counts

    return d


def calc_pressure(pressures, thresh, days, tag, param):
    dsdate = param.month.strftime("_m_*_%Y*.csv")
    d = {"pressure": [], "rmsvd": [], "speed": [], "yield": [], "angle": []}

    for pressure in tqdm(pressures):
        error_sum = 0
        speed_sum = 0
        angle_sum = 0
        denominator = 0
        angle_denominator = 0
        yield_sum = 0
        for day in days:
            for time in ("am", "pm"):
                file = (
                    "../data/interim/dataframes/t"
                    + str(thresh)
                    + "_"
                    + day.strftime("%m_%d_%Y_")
                    + time
                    + tag
                    + ".csv"
                )
                df_unit = pd.read_csv(file)
                df_unit = df_unit.set_index("pressure", drop=True)
                error_sum = error_sum + df_unit.loc[pressure, "error_sum"]
                speed_sum = speed_sum + df_unit.loc[pressure, "speed_sum"]
                angle_sum = angle_sum + df_unit.loc[pressure, "angle_sum"]
                yield_sum = yield_sum + df_unit.loc[pressure, "yield"]
                denominator = denominator + df_unit.loc[pressure, "denominator"]
                angle_denominator = (
                    angle_denominator + df_unit.loc[pressure, "angle_denominator"]
                )

        d["pressure"].append(pressure)
        d["speed"].append(speed_sum / denominator)
        d["rmsvd"].append(np.sqrt(error_sum / denominator))
        d["angle"].append(angle_sum / angle_denominator)

        d["yield"].append(yield_sum)

    df = pd.DataFrame(data=d)
    print(df)
    df.set_index("pressure", drop=True)
    print(
        "../data/processed/dataframes/"
        + param.month_string
        + "_rmsvd_t"
        + str(thresh)
        + tag
        + ".csv"
    )
    df.to_csv(
        "../data/processed/dataframes/"
        + param.month_string
        + "_rmsvd_t"
        + str(thresh)
        + tag
        + ".csv"
    )


def plot_rmsvd(ax, df, width, thresh):
    ax.plot(
        df["rmsvd"],
        df["pressure"],
        label="δ = " + str(thresh) + " m/s",
        linewidth=width,
    )
    # ax.plot(df['pressure'], df['speed'], label='speed, δ = '+str(thresh)+' m/s',linestyle='dashed', linewidth=width,color='black')
    ax.set_xlabel("RMSVD [m/s]")
    ax.set_yscale("symlog")
    ax.set_yticklabels(np.arange(1000, 50, -150))
    ax.set_ylim(df["pressure"].max(), df["pressure"].min())
    ax.set_yticks(np.arange(1000, 50, -150))
    ax.set_xticklabels(np.arange(0, 35, 7))
    ax.set_xticks(np.arange(0, 35, 7))


def plot_angle(ax, df, width, thresh):
    ax.plot(
        df["angle"],
        df["pressure"],
        label="δ = " + str(thresh) + " m/s",
        linewidth=width,
    )
    # ax.plot(df['pressure'], df['speed'], label='speed, δ = '+str(thresh)+' m/s',linestyle='dashed', linewidth=width,color='black')
    ax.set_xlabel("Angle [deg]")
    ax.set_yscale("symlog")
    ax.set_yticklabels(np.arange(1000, 50, -150))
    ax.set_ylim(df["pressure"].max(), df["pressure"].min())
    ax.set_yticks(np.arange(1000, 50, -150))
    ax.set_xticklabels(np.arange(0, 70, 15))
    ax.set_xticks(np.arange(0, 70, 15))


def plot_yield(ax, df, width, thresh):
    ax.plot(
        df["yield"] / (7 * 10000),
        df["pressure"],
        label="δ = " + str(thresh) + " m/s",
        linewidth=width,
    )
    ax.set_xlabel("10 000 counts per day")
    ax.set_yscale("symlog")
    ax.set_yticklabels(np.arange(1000, 50, -150))
    ax.set_ylim(df["pressure"].max(), df["pressure"].min())
    ax.set_yticks(np.arange(1000, 50, -150))
    nticks = np.arange(0, 6, 1)
    ax.set_xticklabels(nticks)
    ax.set_xticks(nticks)


def line_plotter(func, ax, month, param):
    colors = cm.tab10(np.linspace(0, 1, len(THRESHOLDS)))
    widths = np.linspace(1, 3, len(THRESHOLDS))
    for i, thresh in enumerate(reversed(THRESHOLDS)):
        param.set_thresh(thresh)
        # color=colors[i]
        width = widths[i]
        df = pd.read_csv(
            "../data/processed/dataframes/"
            + month
            + "_rmsvd_t"
            + str(thresh)
            + param.tag
            + ".csv"
        )
        func(ax, df, width, thresh)
    ax.set_ylabel("Pressure [hPa]")

    return ax


def multiple_lineplots(
    tag, month, title, plot_rmsvd, plot_yield, plot_angle, param, rmsvds
):
    fig, axes = plt.subplots(nrows=1, ncols=2)
    axlist = axes.flat
    axlist[0] = line_plotter(plot_rmsvd, axlist[0], month, param)
    # axlist[1]=line_plotter(plot_angle, axlist[1], month, param)
    axlist[1] = line_plotter(plot_yield, axlist[1], month, param)

    # axlist[0].text(-5,150,tag[0],c='red')
    # axlist[1].text(-5,150,tag[1],c='red')
    axlist[0].legend(frameon=False)

    axlist[0].text(0.5, 0.5, tag[0], transform=axlist[0].transAxes)
    axlist[0].text(
        0.0,
        0.25,
        "RMSVD= " + str(round(rmsvds["10"], 2)),
        transform=axlist[0].transAxes,
    )
    # axlist[0].text(0.0,0.1,'RMSVD= ' + str(round(rmsvds['100'],2)), transform=axlist[0].transAxes)

    axlist[1].text(0.5, 0.5, tag[1], transform=axlist[1].transAxes)
    # axlist[1].text(0.5,0.5,tag[2], transform=axlist[2].transAxes)
    param.set_thresh(10)
    df = pd.read_csv(
        "../data/processed/dataframes/" + month + "_rmsvd_t10" + param.tag + ".csv"
    )
    total_yield = df["yield"].sum() / 1e4 / 7
    axlist[1].text(
        0.0,
        0.25,
        "total yield= " + str(round(total_yield, 2)),
        transform=axlist[1].transAxes,
    )
    param.set_thresh(100)
    df = pd.read_csv(
        "../data/processed/dataframes/" + month + "_rmsvd_t100" + param.tag + ".csv"
    )
    # total_yield=df['yield'].sum()/1e4/7
    # xlist[1].text(0.0,0.1,'total yield= ' + str(round(total_yield,2)), transform=axlist[1].transAxes)

    fig.tight_layout()
    plt.savefig(
        "../data/processed/plots/" + param.tag + "_" + title + ".png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.show()
    plt.close()


def threshold_fun(param):

    days = param.dates
    rmsvds = {}

    for thresh in THRESHOLDS:
        param.set_thresh(thresh)
        tag = param.tag
        pressures, rmsvd = calc_days(thresh, days, tag)
        rmsvds[str(thresh)] = rmsvd
        calc_pressure(pressures, thresh, days, tag, param)
    return rmsvds


def main(param):
    param.set_month(datetime(2020, 1, 1))
    rmsvds = threshold_fun(param)
    multiple_lineplots(
        ["(a)", "(b)"],
        "january",
        "angle_january_pressure_plots",
        plot_rmsvd,
        plot_yield,
        plot_angle,
        param,
        rmsvds,
    )
    param.set_month(datetime(2020, 7, 1))
    rmsvds = threshold_fun(param)
    multiple_lineplots(
        ["(c)", "(d)"],
        "july",
        "angle_july_pressure_plots",
        plot_rmsvd,
        plot_yield,
        plot_angle,
        param,
        rmsvds,
    )


if __name__ == "__main__":
    param = parameters()
    param.set_plev_coarse(5)
    param.set_alg("rand")
    param.set_timedelta(6)
    param.set_Lambda(0.15)
    main(param)
