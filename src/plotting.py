#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 30 17:52:25 2022

@author: aouyed
"""
import xarray as xr
import matplotlib.pyplot as plt
import calculators as calc
import cartopy.crs as ccrs
import numpy as np
import main as m
import datetime


def map_plotter_cartopy(ds, title, label, units_label=""):
    values = np.squeeze(ds[label].values)
    fig = plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    ax.gridlines()
    im = ax.imshow(
        values,
        cmap="viridis",
        extent=[ds["lon"].min(), ds["lon"].max(), ds["lat"].min(), ds["lat"].max()],
        origin="lower",
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


filename = "SNDR.J1.CRIMSS.20210128.D01.L3_CLIMCAPS_QCC.std.v02_38.G.210304093613.nc"


ds = xr.open_dataset("../data/raw/" + filename)
ds_geo = xr.open_dataset(m.NC_PATH + m.FOLDER + "_output.nc")
ds = ds.sel(orbit_pass=ds["orbit_pass"].values[0])
ds["air_pres_h2o"] = ds["air_pres_h2o"] / 100
ds = ds.sel(air_pres_h2o=700, method="nearest")
ds = ds.squeeze()
lon, lat = np.meshgrid(ds["lon"].values, ds["lat"].values, indexing="xy")
ds["lat_coor"] = (["lat", "lon"], lat)
ds["lon_coor"] = (["lat", "lon"], lon)
start = ds["obs_time_tai93"]
dt_sec = 240 * ds["lon_coor"]
dt = dt_sec.values.astype("timedelta64[s]")
obs_time = start.values + dt
ds["obs_time"] = (["lat", "lon"], obs_time)


calc.map_plotter(ds, "spec_hum", "spec_hum", units_label="cm/s", vmin=0, vmax=0)
map_plotter_cartopy(ds, "spec_hum", "spec_hum", units_label="")
