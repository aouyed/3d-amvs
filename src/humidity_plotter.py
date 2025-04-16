#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 11:46:56 2022

@author: aouyed
"""

import matplotlib.pyplot as plt
import xarray as xr
from datetime import datetime
from datetime import timedelta
import numpy as np
import cv2
from dateutil.parser import parse
import cartopy.crs as ccrs
import stats_calculators as sc
import amv_calculators as calc


CONV = 1000


def map_plotter_cartopy(ds, title, label, units_label=""):
    values = np.squeeze(ds[label].values)
    fig = plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    ax.gridlines()
    im = ax.imshow(
        CONV * values,
        cmap="viridis",
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


def map_plotter_vmax(ds, title, label, vmin, vmax, units_label="", color="viridis"):
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
        vmin=vmin,
        vmax=vmax,
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


def overlap(ds):

    ds_snpp = ds.loc[{"satellite": "snpp"}]
    ds_j1 = ds.loc[{"satellite": "j1"}]
    start = ds["obs_time"].min(skipna=True)
    end = start + np.timedelta64(145, "m")
    # 145
    ds_j1 = ds_j1.where((ds_j1.obs_time >= start) & (ds_j1.obs_time <= end))
    start = start + np.timedelta64(50, "m")
    end = end + np.timedelta64(50, "m")
    ds_snpp = ds_snpp.where((ds_snpp.obs_time >= start) & (ds_snpp.obs_time <= end))

    condition1 = xr.ufuncs.logical_not(xr.ufuncs.isnan(ds_j1["obs_time"]))
    condition2 = xr.ufuncs.logical_not(xr.ufuncs.isnan(ds_snpp["obs_time"]))
    ds_j1 = ds_j1[["specific_humidity_mean", "obs_time"]].where(condition1 & condition2)
    ds_snpp = ds_snpp[["specific_humidity_mean", "obs_time"]].where(
        condition1 & condition2
    )
    return ds_snpp, ds_j1


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


def patch_plotter():
    time = "pm"
    ds = xr.open_dataset(
        "../data/processed/tvl1_coarse_july_5_t10_tdelta_6_Lambda_0.15.nc"
    )
    ds_map = ds.loc[{"time": time, "satellite": "snpp"}]
    ds_map = ds_map.sel(plev=706, method="nearest")
    ds_map = ds_map.sel(day=ds_map["day"].values[0])
    map_plotter_cartopy(
        ds_map, "humidity_overlap_map_" + time, "humidity_overlap", "[g/kg]"
    )

    print(ds_map)


def single_overlap():
    time = "pm"
    ds = xr.open_dataset("../data/processed/real_water_vapor_noqc_july.nc")
    ds_map = ds.loc[{"day": datetime(2020, 7, 1), "time": time, "satellite": "j1"}]
    ds_map = ds_map.sel(plev=706, method="nearest")

    # corr(ds_map, 10)
    start = np.datetime64("2020-07-01T01:00")
    # start=ds_map['obs_time'].min(skipna=True).values+ np.timedelta64(95, 'm')
    # end=start + np.timedelta64(10, 'm')
    end = start + np.timedelta64(5, "m")

    ds_map = ds_map.where((ds_map.obs_time >= start) & (ds_map.obs_time <= end))
    ds_unit = ds_map
    df = ds_map.to_dataframe()
    df = df.reset_index().dropna()
    df = df.set_index(["latitude", "longitude"])
    print(ds_unit)
    ds
    plt.show()
    plt.close()
    map_plotter_cartopy(
        ds_unit,
        df,
        "humidity_overlap_map_test_" + time,
        "specific_humidity_mean",
        "[g/kg]",
    )

    print(ds_map)


def patch_tester():
    ds = xr.open_dataset("../data/processed/real_water_vapor_noqc_july.nc")
    ds = xr.open_dataset("../data/processed/real_water_vapor_noqc_july.nc")

    ds_map = ds.loc[{"day": datetime(2020, 7, 1), "time": "am", "satellite": "snpp"}]
    ds_map = ds_map.sel(plev=700, method="nearest")
    map_plotter(ds_map, "snpp", "specific_humidity_mean")

    # ds_map=ds.loc[{'day':datetime(2020,7,1),'time':'am'}]
    # ds_map=ds_map.sel(plev=706, method='nearest')
    # ds_snpp, ds_j1=overlap(ds_map)
    # map_plotter(ds_snpp, 'snpp', 'specific_humidity_mean')
    single_overlap()


def main():
    # patch_tester()
    patch_plotter()
    # swaths=calc.swath_initializer()


if __name__ == "__main__":
    main()
