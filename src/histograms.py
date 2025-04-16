#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 12:06:15 2021

@author: aouyed

"""
import matplotlib.pyplot as plt
import xarray as xr
from datetime import datetime
from datetime import timedelta
import numpy as np
import cv2
from dateutil.parser import parse
import main as fsa
import cartopy.crs as ccrs
import amv_calculators as calc
import config as c
import pandas as pd
from tqdm import tqdm
import inpainter
from parameters import parameters


def map_plotter_cartopy(ds, title, label, color, units_label=""):
    values = np.squeeze(ds[label].values)
    fig = plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    ax.gridlines()
    im = ax.imshow(
        values,
        cmap=color,
        extent=[
            ds["longitude"].min(),
            ds["longitude"].max(),
            ds["latitude"].min(),
            ds["latitude"].max(),
        ],
    )
    ax.gridlines(draw_labels=True, x_inline=False, y_inline=False)
    # ax.scatter(df.longitude, df.latitude)
    # plt.title(label)
    cbar_ax = fig.add_axes([0.1, 0.05, 0.78, 0.05])
    fig.colorbar(im, cax=cbar_ax, orientation="horizontal", pad=0.5, label=units_label)
    plt.savefig(
        "../data/processed/plots/" + title + ".png", bbox_inches="tight", dpi=300
    )
    plt.show()
    plt.close()


def map_plotter(ds, title, label, units_label="", color="viridis"):
    values = np.squeeze(ds[label].values)
    fig, ax = plt.subplots()
    im = ax.imshow(
        values,
        cmap=color,
        extent=[
            ds["longitude"].min(),
            ds["longitude"].max(),
            ds["latitude"].min(),
            ds["latitude"].max(),
        ],
    )
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.04)
    cbar.set_label(units_label)
    plt.xlabel("lon")
    plt.ylabel("lat")
    plt.savefig(
        "../data/processed/plots/" + title + ".png", bbox_inches="tight", dpi=300
    )
    plt.title(label)
    plt.show()
    plt.close()


def map_plotter_vmax(
    ds, title, label, vmin=0, vmax=10, units_label="", color="viridis"
):
    values = np.squeeze(ds[label].values)
    fig = plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    ax.gridlines()
    im = ax.imshow(
        values,
        cmap=color,
        extent=[
            ds["longitude"].min(),
            ds["longitude"].max(),
            ds["latitude"].min(),
            ds["latitude"].max(),
        ],
        vmin=vmin,
        vmax=vmax,
    )
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.04)
    cbar.set_label(units_label)
    ax.gridlines(draw_labels=True, x_inline=False, y_inline=False)
    plt.title(title)

    plt.xlabel("lon")
    plt.ylabel("lat")
    plt.savefig(
        "../data/processed/plots/" + title + ".png", bbox_inches="tight", dpi=300
    )
    plt.show()
    plt.close()


def corr(ds, thresh):
    ds["speed"] = np.sqrt(ds.u**2 + ds.v**2)
    ds["speed_era5"] = np.sqrt(ds.u_era5**2 + ds.v_era5**2)
    ds["u_error"] = ds["u"] - ds["u_era5"]
    ds["v_error"] = ds["v"] - ds["v_era5"]
    ds["error_mag"] = np.sqrt(ds["u_error"] ** 2 + ds["v_error"] ** 2)
    ds["error_square"] = ds["u_error"] ** 2 + ds["v_error"] ** 2
    ds = ds.where(ds.error_mag < thresh)
    print(np.sqrt(sc.weighted_mean(ds["error_square"])))

    df = ds.to_dataframe()
    df = df.reset_index().dropna()
    print(df[["u", "u_era5"]].corr())


def compute(ds):
    ds["speed"] = np.sqrt(ds.u**2 + ds.v**2)
    ds["speed_era5"] = np.sqrt(ds.u_era5**2 + ds.v_era5**2)
    ds["speed_diff"] = ds.speed - ds.speed_era5
    ds["u_error"] = ds["u"] - ds["u_era5"]
    ds["v_error"] = ds["v"] - ds["v_era5"]
    ds["error_mag"] = np.sqrt(ds["u_error"] ** 2 + ds["v_error"] ** 2)
    ds["error_square"] = ds["u_error"] ** 2 + ds["v_error"] ** 2
    ds = angle(ds)
    ds["dqdx"] = ds["humidity_overlap"].differentiate("longitude")
    ds["dqdy"] = ds["humidity_overlap"].differentiate("latitude")
    ds["grad_q"] = np.sqrt(ds.dqdx**2 + ds.dqdy**2)
    ds = angle_grad_q(ds)

    return ds


def patch_plotter():
    time = "am"
    ds = xr.open_dataset("../data/processed/07_01_2020_" + time + ".nc")
    ds_map = ds.loc[{"time": time, "satellite": "snpp"}]
    ds_map = ds_map.sel(plev=706, method="nearest")
    map_plotter_cartopy(
        ds_map, "humidity_overlap_map_" + time, "humidity_overlap", "[g/kg]"
    )

    print(ds_map)


def single_overlap():
    time = "am"
    ds = xr.open_dataset("../data/processed/inpaint_07_01_2020_am.nc")

    ds_whole = ds.loc[{"time": "am", "satellite": "snpp"}]
    ds_whole = ds_whole.sel(plev=900, method="nearest")

    # corr(ds_map, 10)
    start = np.datetime64("2020-01-01T00:00")
    start = start + np.timedelta64(140, "m")
    start = start + np.timedelta64(5, "m")
    # start=ds_map['obs_time'].min(skipna=True).values+ np.timedelta64(95, 'm')
    # end=start + np.timedelta64(10, 'm')
    end = start + np.timedelta64(5, "m")

    ds_map = ds_whole.where((ds_whole.obs_time >= start) & (ds_whole.obs_time <= end))
    df = ds_map.to_dataframe().reset_index()
    df = df.dropna()
    df = df.set_index(["latitude", "longitude"])
    ds_unit = xr.Dataset.from_dataframe(df)
    frame = ds_unit["humidity_overlap"].values
    frame = calc.fill(frame)
    ds_unit["inpainted"] = (["latitude", "longitude"], frame)
    map_plotter_cartopy(ds_unit, "snpp", "humidity_overlap", "viridis")
    map_plotter(ds_unit, "snpp_nomap", "humidity_overlap", "viridis")
    map_plotter(ds_unit, "inpainted", "inpainted", "viridis")
    map_plotter(ds_whole, "u_nomap", "u_era5", "viridis")
    map_plotter(ds_whole, "u_era5", "u", "viridis")


def concatenate_ds():
    start = c.MONTH
    end = c.MONTH + timedelta(days=6)
    dates = pd.date_range(start, end, freq="D")
    ds_total = xr.Dataset()
    for date in tqdm(dates):
        dsdate = date.strftime("%m_%d_%Y")
        ds_time = xr.Dataset()
        for time in ("am", "pm"):
            ds = xr.open_dataset(
                "../data/processed/" + dsdate + "_" + time + "_thick_plev.nc"
            )
            if not ds_time:
                ds_time = ds
            else:
                ds_time = xr.concat([ds_time, ds], "time")
        if not ds_total:
            ds_total = ds_time
        else:
            ds_total = xr.concat([ds_total, ds_time], "day")
    print(ds_total)
    ds_total.to_netcdf("../data/processed/july_thick_plev.nc")


def angle(ds):
    dot = ds["u"] * ds["u_era5"] + ds["v"] * ds["v_era5"]
    mags = np.sqrt(ds["u"] ** 2 + ds["v"] ** 2) * np.sqrt(
        ds["u_era5"] ** 2 + ds["v_era5"] ** 2
    )
    c = dot / mags
    ds["angle"] = np.arccos(c)
    ds["angle"] = ds.angle / np.pi * 180
    ds["neg_function"] = ds["u"] * ds["v_era5"] - ds["v"] * ds["u_era5"]
    neg_function = ds["neg_function"].values
    neg_function[neg_function < 0] = -1
    neg_function[neg_function > 0] = 1

    # ds['neg_function']=np.positive( ds['neg_function'])
    ds["signed_angle"] = neg_function * ds["angle"]
    return ds


def angle_grad_q(ds):
    """Calculates angle between moisture and wind velocity."""
    dot = ds["u"] * ds["dqdx"] + ds["v"] * ds["dqdy"]
    mags = np.sqrt(ds["u"] ** 2 + ds["v"] ** 2) * np.sqrt(
        ds["dqdx"] ** 2 + ds["dqdy"] ** 2
    )
    c = dot / mags
    ds["angle_q"] = np.arccos(c)
    ds["angle_q"] = ds.angle_q / np.pi * 180
    ds["neg_function"] = ds["u"] * ds["dqdy"] - ds["v"] * ds["dqdx"]
    neg_function = ds["neg_function"].values
    neg_function[neg_function < 0] = -1
    neg_function[neg_function > 0] = 1

    # ds['neg_function']=np.positive( ds['neg_function'])
    ds["angle_q"] = neg_function * ds["angle_q"]
    return ds


def histogram(values, ax, thresh):
    values = values[~np.isnan(values)]
    h, edges = np.histogram(values, bins=50, density=True)
    ax.stairs(h, edges, fill=True, label="δ = " + str(thresh) + " m/s", alpha=0.5)
    return ax


def multi_histogram_ax(param, label, xlabel, ax, letter, plev):
    print(label)
    print(param.month_string)
    for thresh in [10]:
        param.set_thresh(thresh)
        print(thresh)
        file = "../data/processed/" + param.tag + ".nc"
        ds_unit = xr.open_dataset(file)
        ds_unit = compute(ds_unit)
        if plev > 0:
            ds_unit = ds_unit.sel(plev=plev, method="nearest")
        histogram(ds_unit[label].values, ax, thresh)
        if thresh == 10:
            mean_string = ds_unit[label].mean().item()
            if label == "signed_angle":
                unit = "deg"
            else:
                unit = "m/s"
            ax.text(
                0.1,
                0.1,
                str(round(mean_string, 2)) + " " + unit,
                transform=ax.transAxes,
            )
    ax.set_xlabel(xlabel)
    if label is not "signed_angle":
        ax.set_xlim(-35, 35)
    ax.text(0.1, 0.8, letter, transform=ax.transAxes)

    return ax


def four_panel_histogram(param, label, plev):
    fig, axes = plt.subplots(nrows=2, ncols=2)
    axlist = axes.flat
    axlist[0] = multi_histogram_ax(
        param, "u_error", "U error [m/s]", axlist[0], "(a)", plev
    )
    axlist[1] = multi_histogram_ax(
        param, "v_error", "V error [m/s]", axlist[1], "(b)", plev
    )
    axlist[2] = multi_histogram_ax(
        param, "speed_diff", "Speed error [m/s]", axlist[2], "(c)", plev
    )
    axlist[3] = multi_histogram_ax(
        param, "signed_angle", "Angle [deg]", axlist[3], "(d)", plev
    )
    # axlist[0].legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0.)
    axlist[0].legend(bbox_to_anchor=(0, 1.07), loc="lower left")
    fig.tight_layout()
    plt.savefig(
        "../data/processed/plots/hist_" + label + "_" + str(plev) + param.tag + ".png",
        dpi=300,
    )
    plt.show()
    plt.close()


def three_panel_histogram(param, label, plev):
    fig, axes = plt.subplots(nrows=3, ncols=1)
    axlist = axes.flat
    axlist[0] = multi_histogram_ax(param, "u", "U [m/s]", axlist[0], "(a)", plev)
    axlist[1] = multi_histogram_ax(param, "v", "V  [m/s]", axlist[1], "(b)", plev)
    axlist[2] = multi_histogram_ax(
        param, "speed", "Speed [m/s]", axlist[2], "(c)", plev
    )
    # axlist[0].legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0.)
    axlist[0].legend(bbox_to_anchor=(0, 1.07), loc="lower left")
    fig.tight_layout()
    plt.savefig(
        "../data/processed/plots/hist_values_"
        + label
        + "_"
        + str(plev)
        + param.tag
        + ".png",
        dpi=300,
    )
    plt.show()
    plt.close()


def histograms(param):
    for plev in [0]:

        param.set_month(datetime(2020, 1, 1))
        four_panel_histogram(param, "jan_four_panel", plev)
        three_panel_histogram(param, "jan_four_panel", plev)

        # param.set_month(datetime(2020,7,1))
        # four_panel_histogram(param, 'july_four_panel',plev)
        # three_panel_histogram(param, 'july_four_panel',plev)


def main(param):
    histograms(param)
    # error_maps()
    # patch_plotter()
    # swaths=calc.swath_initializer()


if __name__ == "__main__":
    param = parameters()
    # param.set_alg('farneback')
    param.set_Lambda(0.313)
    param.set_plev_coarse(5)
    param.set_alg("tvl1")
    param.set_timedelta(1)
    main(param)
