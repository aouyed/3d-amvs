#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 15:15:56 2021

@author: aouyed
"""
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
import numpy as np
import config as c
import cartopy.crs as ccrs
from parameters import parameters
from datetime import datetime

THRESH = 10
TAGS = [["filtered_thick_plev_tlv1", 10], ["filtered_4_thick_plev_tlv1", 4]]


def scatter(x, y):
    fig, ax = plt.subplots()
    ax.scatter(x, y)
    ax.set_xlabel("Radiosonde [m/s]")
    ax.set_ylabel("ERA 5 [m/s]")
    ax.set_title("Magnitude of Vector Difference")
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 20)
    plt.show()
    plt.close()


def pressure_df(df):
    plevs = df["plev"].unique()
    d = {
        "plev": [],
        "rmsvd": [],
        "rmsvd_era5": [],
        "u_error": [],
        "v_error": [],
        "u_error_era5": [],
        "v_error_era5": [],
        "angle": [],
        "angle_era5": [],
        "angle_bias": [],
        "angle_bias_era5": [],
        "speed_bias": [],
        "speed_rmse": [],
        "speed_bias_era5": [],
        "speed_rmse_era5": [],
        "N": [],
    }
    for plev in plevs:

        df_unit = df[df.plev == plev]
        n_points = (
            df_unit[
                [
                    "lat_rs",
                    "lon_rs",
                    "stationid",
                    "u_wind",
                    "v_wind",
                    "u",
                    "v",
                    "plev",
                    "date_amv",
                ]
            ]
            .drop_duplicates()
            .dropna()
            .shape[0]
        )
        # n_points=df_unit[['lat_rs','lon_rs','stationid','u_wind','v_wind','u','v','plev','date_amv']].drop_duplicates().dropna().shape[0]

        rmsvd = np.sqrt(df_unit["error_square"].mean())
        u_error = df_unit["u_error"].mean()
        u_error_era5 = df_unit["u_error_era5"].mean()

        v_error = df_unit["v_error"].mean()
        v_error_era5 = df_unit["v_error_era5"].mean()

        angle = df_unit["angle"].mean()
        angle_era5 = df_unit["angle_era5"].mean()
        angle_bias = df_unit["signed_angle"].mean()
        angle_bias_era5 = df_unit["signed_angle_era5"].mean()
        speed_bias = df_unit["speed_error"].mean()
        speed_rmse = np.sqrt((df_unit["speed_error"] ** 2).mean())
        speed_rmse_era5 = np.sqrt((df_unit["speed_error_era5"] ** 2).mean())

        speed_bias_era5 = df_unit["speed_error_era5"].mean()

        rmsvd_era5 = np.sqrt(df_unit["error_square_era5"].mean())
        d["plev"].append(plev)
        d["rmsvd"].append(rmsvd)
        d["rmsvd_era5"].append(rmsvd_era5)
        d["u_error"].append(u_error)
        d["u_error_era5"].append(u_error_era5)

        d["v_error"].append(v_error)
        d["v_error_era5"].append(v_error_era5)

        d["angle"].append(angle)
        d["angle_era5"].append(angle_era5)

        d["speed_bias"].append(speed_bias)
        d["speed_bias_era5"].append(speed_bias_era5)

        d["speed_rmse"].append(speed_rmse)
        d["speed_rmse_era5"].append(speed_rmse_era5)

        d["angle_bias"].append(angle_bias)
        d["angle_bias_era5"].append(angle_bias_era5)
        d["N"].append(n_points)

    df_pressure = pd.DataFrame(data=d)
    df_pressure = df_pressure.sort_values(by=["plev"])
    return df_pressure


def means_d(df_unit):
    d = {}
    n_points = (
        df_unit[
            [
                "lat_rs",
                "lon_rs",
                "stationid",
                "u_wind",
                "v_wind",
                "u",
                "v",
                "plev",
                "date_amv",
            ]
        ]
        .drop_duplicates()
        .dropna()
        .shape[0]
    )

    rmsvd = np.sqrt(df_unit["error_square"].mean())
    u_error = df_unit["u_error"].mean()
    u_error_era5 = df_unit["u_error_era5"].mean()

    v_error = df_unit["v_error"].mean()
    v_error_era5 = df_unit["v_error_era5"].mean()

    angle = df_unit["angle"].mean()
    angle_era5 = df_unit["angle_era5"].mean()
    angle_bias = df_unit["signed_angle"].mean()
    angle_bias_era5 = df_unit["signed_angle_era5"].mean()
    speed_bias = df_unit["speed_error"].mean()
    speed_bias_era5 = df_unit["speed_error_era5"].mean()

    rmsvd_era5 = np.sqrt(df_unit["error_square_era5"].mean())
    d["rmsvd"] = rmsvd
    d["rmsvd_era5"] = rmsvd_era5
    d["u_error"] = u_error
    d["u_error_era5"] = u_error_era5
    d["v_error"] = v_error
    d["v_error_era5"] = v_error_era5
    d["angle"] = angle
    d["angle_era5"] = angle_era5
    d["speed_bias"] = speed_bias
    d["speed_bias_era5"] = speed_bias_era5
    d["angle_bias"] = angle_bias
    d["angle_bias_era5"] = angle_bias_era5
    d["N"] = n_points

    return d


def pressure_ax(ax, param, rmsvd_label, xlabel, xlim):
    sample_stats = pd.DataFrame()
    month_string = param.month_string
    param.set_thresh(10)

    df = pd.read_pickle(
        "../data/processed/dataframes/"
        + month_string
        + "_winds_rs_model_"
        + param.tag
        + ".pkl"
    )
    df = df.drop_duplicates()

    df = preprocess(df)

    df_pressure_era = pressure_df(df)
    df_pressure_era.round(2).to_csv(
        "../data/processed/df_pressure_era_" + param.tag + ".csv"
    )

    thresh = THRESH
    param.set_thresh(thresh)
    df_unit = pd.read_pickle(
        "../data/processed/dataframes/"
        + month_string
        + "_winds_rs_model_"
        + param.tag
        + ".pkl"
    )
    df_unit = preprocess(df_unit)
    # n_points=df[['lat_rs','lon_rs','stationid','date']].drop_duplicates().dropna().shape[0]
    n_points = (
        df_unit[
            [
                "lat_rs",
                "lon_rs",
                "lat",
                "lon",
                "stationid",
                "u_wind",
                "v_wind",
                "u",
                "v",
                "plev",
                "date_amv",
            ]
        ]
        .drop_duplicates()
        .dropna()
        .shape[0]
    )
    df_pressure = pressure_df(df_unit)
    df_pressure.round(2).to_csv("../data/processed/df_pressure_" + param.tag + ".csv")
    means = df_pressure[rmsvd_label].mean()
    means_era5 = df_pressure["rmsvd_era5"].mean()
    ax.plot(
        df_pressure[rmsvd_label], df_pressure.plev, label="δ = " + str(thresh) + " m/s"
    )
    ax.plot(df_pressure_era[rmsvd_label + "_era5"], df_pressure_era.plev, label="ERA 5")
    if rmsvd_label == "rmsvd":
        ax.axvspan(5.93, 8.97, alpha=0.25, color="grey")
    if rmsvd_label == "speed_bias":
        ax.axvspan(-1.79, 1.79, alpha=0.25, color="grey")
    if rmsvd_label == "angle_bias":
        ax.axvspan(-14.61, 14.61, alpha=0.25, color="grey")

    ax.text(0.6, 0.05, "N = " + str(n_points), transform=ax.transAxes)
    mean_string = str(round(means, 2))
    mean_string_era5 = str(round(means_era5, 2))

    if rmsvd_label == "rmsvd":
        ax.text(0.5, 0.25, "RMSVD = " + mean_string, transform=ax.transAxes)
        ax.text(0.5, 0.1, "RMSVD_ERA5 = " + mean_string_era5, transform=ax.transAxes)

    else:
        ax.text(0.7, 0.25, "μ = " + mean_string, transform=ax.transAxes)

    ax.set_xlabel(xlabel)
    ax.set_ylabel("Pressure [hPa]")
    ax.set_xlim(xlim[0], xlim[1])
    ax.set_yscale("symlog")
    ax.set_yticklabels(np.arange(900, 50, -125))
    ax.set_ylim(df["plev"].max(), df["plev"].min())
    ax.set_yticks(np.arange(900, 50, -125))
    return ax


def scatter_plot_cartopy(ax, title, x, y):
    ax.coastlines()
    ax.scatter(x, y, s=20)
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    gl = ax.gridlines(draw_labels=True, x_inline=False, y_inline=False)

    return ax, gl


def four_panel_plot(
    fname,
    param,
    var1="rmsvd",
    var2="angle",
    xlabel1="RMSVD [m/s]",
    xlabel2="Angle [deg]",
    xlim1=(0, 15),
    xlim2=(10, 60),
):
    fig, axes = plt.subplots(nrows=2, ncols=2)
    axlist = axes.flat

    two_radiosonde_panels(axlist[:2], var1, xlabel1, xlim1, param)
    two_radiosonde_panels(axlist[2:], var2, xlabel2, xlim2, param)
    axlist[0].legend(frameon=False, loc="upper left")

    axlist[0].text(0.05, 0.05, "(a)", transform=axlist[0].transAxes)
    axlist[1].text(0.05, 0.05, "(b)", transform=axlist[1].transAxes)
    axlist[2].text(0.05, 0.05, "(c)", transform=axlist[2].transAxes)
    axlist[3].text(0.05, 0.05, "(d)", transform=axlist[3].transAxes)

    fig.tight_layout()
    plt.savefig(
        "../data/processed/plots/" + param.tag + fname + ".png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.show()
    plt.close()


def n_points_plot(param):

    param.set_thresh(10)
    param.set_month(datetime(2020, 1, 1))
    df_jan = pd.read_pickle(
        "../data/processed/dataframes/"
        + param.month_string
        + "_winds_rs_model_"
        + param.tag
        + ".pkl"
    )
    df_jan = preprocess(df_jan)
    df_pressure_jan = pressure_df(df_jan)

    param.set_month(datetime(2020, 1, 1))
    df_july = pd.read_pickle(
        "../data/processed/dataframes/"
        + param.month_string
        + "_winds_rs_model_"
        + param.tag
        + ".pkl"
    )
    df_july = preprocess(df_july)
    df_pressure_july = pressure_df(df_july)

    fig, ax = plt.subplots()
    ax.plot(df_pressure_jan["N"], df_pressure_jan.plev, label="january")
    ax.plot(df_pressure_july["N"], df_pressure_july.plev, label="july")
    ax.set_xlabel("Number of AMVs")
    ax.set_ylabel("Pressure [hPa]")
    ax.set_yscale("symlog")
    ax.set_yticklabels(np.arange(900, 50, -125))
    ax.set_ylim(df_jan["plev"].max(), df_jan["plev"].min())
    ax.set_yticks(np.arange(900, 50, -125))
    ax.legend(frameon=False)

    fig.tight_layout()
    plt.savefig(
        "../data/processed/plots/n_points" + param.tag + ".png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.show()
    plt.close()


def two_radiosonde_panels(axlist, label, xlabel, xlim, param):
    param.set_month(datetime(2020, 1, 1))
    axlist[0] = pressure_ax(axlist[0], param, label, xlabel, xlim)
    param.set_month(datetime(2020, 7, 1))
    axlist[1] = pressure_ax(axlist[1], param, label, xlabel, xlim)


def location_plot(fname, param):

    fig, axes = plt.subplots(
        nrows=2, ncols=1, subplot_kw={"projection": ccrs.PlateCarree()}
    )
    axlist = axes.flat
    param.set_month(datetime(2020, 1, 1))
    df = pd.read_pickle(
        "../data/processed/dataframes/"
        + param.month_string
        + "_winds_rs_model_"
        + param.tag
        + ".pkl"
    )
    df = preprocess(df)
    df = df[["stationid", "lat_rs", "lon_rs", "date"]].drop_duplicates().dropna()
    nstations = df.shape[0]
    df = df[["stationid", "lat_rs", "lon_rs"]].drop_duplicates().dropna()
    axlist[0], gl = scatter_plot_cartopy(
        axlist[0], "rs_coords", df["lon_rs"], df["lat_rs"]
    )
    gl.xlabels_bottom = False
    gl.ylabels_right = False
    axlist[0].text(0.05, 0.1, str(nstations), transform=axlist[0].transAxes)

    param.set_month(datetime(2020, 7, 1))
    df = pd.read_pickle(
        "../data/processed/dataframes/"
        + param.month_string
        + "_winds_rs_model_"
        + param.tag
        + ".pkl"
    )
    df = preprocess(df)
    df = df[["stationid", "lat_rs", "lon_rs", "date"]].drop_duplicates()
    nstations = df.shape[0]
    df = df[["stationid", "lat_rs", "lon_rs"]].drop_duplicates()
    axlist[1], gl = scatter_plot_cartopy(
        axlist[1], "rs_coords", df["lon_rs"], df["lat_rs"]
    )
    gl.xlabels_top = False
    gl.ylabels_right = False
    axlist[1].text(0.05, 0.1, str(nstations), transform=axlist[1].transAxes)

    fig.tight_layout()
    plt.savefig(
        "../data/processed/plots/location_" + param.tag + fname + ".png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.show()
    plt.close()


def angle(df, ulabel, vlabel, angle_label):
    dot = df[ulabel] * df["u_wind"] + df[vlabel] * df["v_wind"]
    mags = np.sqrt(df[ulabel] ** 2 + df[vlabel] ** 2) * np.sqrt(
        df["u_wind"] ** 2 + df["v_wind"] ** 2
    )
    c = dot / mags
    df[angle_label] = np.arccos(c)
    df[angle_label] = df[angle_label] / np.pi * 180
    df["neg_function"] = df[ulabel] * df["v_wind"] - df[vlabel] * df["u_wind"]
    neg_function = df["neg_function"].values
    neg_function[neg_function < 0] = -1
    neg_function[neg_function > 0] = 1

    df[angle_label] = neg_function * df[angle_label]
    return df


def preprocess(df):
    df = df[df.u_wind > -1000]
    udiff = df.u - df.u_wind
    vdiff = df.v - df.v_wind
    df["u_error"] = udiff
    df["v_error"] = vdiff
    df["speed"] = np.sqrt(df.u**2 + df.v**2)
    df["speed_era5"] = np.sqrt(df.u_coarse_era5**2 + df.v_coarse_era5**2)
    df["speed_wind"] = np.sqrt(df.u_wind**2 + df.v_wind**2)
    df["speed_error"] = df.speed - df.speed_wind

    df["speed_error_era5"] = df.speed_era5 - df.speed_wind
    df["u_error_era5"] = df.u_coarse_era5 - df.u_wind
    df["v_error_era5"] = df.v_coarse_era5 - df.v_wind

    # df['error_mag']=np.sqrt((df.u-df.u_coarse_era5)**2+(df.v-df.v_coarse_era5)**2)
    df["error_square"] = udiff**2 + vdiff**2
    df["error_square_era5"] = (df.u_wind - df.u_coarse_era5) ** 2 + (
        df.v_wind - df.v_coarse_era5
    ) ** 2
    df = angle(df, "u", "v", "signed_angle")
    df = angle(df, "u_era5", "v_era5", "signed_angle_era5")
    df["angle"] = abs(df["signed_angle"])
    df["angle_era5"] = abs(df["signed_angle_era5"])

    return df


def two_panel_plot(
    fname, param, var1="speed_rmse", xlabel1="RMSE [m/s]", xlim1=(0, 15)
):
    fig, axes = plt.subplots(nrows=1, ncols=2)
    axlist = axes.flat

    two_radiosonde_panels(axlist[:2], var1, xlabel1, xlim1, param)
    axlist[0].legend(frameon=False, loc="upper left")

    fig.tight_layout()
    plt.savefig(
        "../data/processed/plots/" + param.tag + fname + ".png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.show()
    plt.close()


def main(param):
    four_panel_plot(
        "rmsvd_bias",
        param,
        var1="rmsvd",
        var2="speed_bias",
        xlabel1="RMSVD [m/s]",
        xlabel2="Speed bias [m/s]",
        xlim2=(-5, 5),
    )
    four_panel_plot(
        "angle",
        param,
        var1="angle",
        var2="angle_bias",
        xlabel1="RMSVD [m/s]",
        xlabel2="Speed bias [m/s]",
        xlim2=(-5, 5),
    )

    n_points_plot(param)
    location_plot("test", param)


if __name__ == "__main__":
    param = parameters()
    param.set_alg("tvl1")
    param.set_Lambda(0.15)
    param.set_month(datetime(2020, 7, 1))
    param.set_timedelta(6)
    param.set_plev_coarse(5)
    main(param)
