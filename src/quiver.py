# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import pandas as pd
import main as fsa
from datetime import datetime
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
from scipy import fftpack, ndimage
from parameters import parameters
from tqdm import tqdm


def quiver_plot(ds, title, u, v):
    # ds=ds.coarsen(latitude=5, longitude=5, boundary='trim').mean()
    fig, ax = plt.subplots()
    X, Y = np.meshgrid(ds["longitude"].values, ds["latitude"].values)
    ax.set_title(title)
    Q = ax.quiver(X, Y, np.squeeze(ds[u].values), np.squeeze(ds[v].values))
    qk = ax.quiverkey(Q, 0.8, 0.9, 5, r"5 m/s", labelpos="E", coordinates="figure")
    fig.tight_layout()
    plt.savefig(
        "../data/processed/plots/quiver_" + title + ".png", bbox_inches="tight", dpi=300
    )
    plt.show()
    plt.close()


def quiver_ax(ax, ds, title, u, v, letter):
    # ds=ds.coarsen(latitude=5, longitude=5, boundary='trim').mean()
    X, Y = np.meshgrid(ds["longitude"].values, ds["latitude"].values)
    ax.set_title(title)
    Q = ax.quiver(X, Y, np.squeeze(ds[u].values), np.squeeze(ds[v].values), scale=200)
    ax.text(0.25, 0.25, letter, transform=ax.transAxes)
    return Q


def quiver_plot_cartopy(ds, title, u, v):
    ds = ds.coarsen(latitude=5, longitude=5, boundary="trim").mean()
    fig = plt.figure()
    X, Y = np.meshgrid(ds["longitude"].values, ds["latitude"].values)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    Q = ax.quiver(X, Y, np.squeeze(ds[u].values), np.squeeze(ds[v].values), scale=200)
    qk = ax.quiverkey(Q, 0.5, 0.5, 10, r"10 m/s", labelpos="E", coordinates="figure")
    fig.tight_layout()
    plt.savefig(
        "../data/processed/plots/" + title + ".png", bbox_inches="tight", dpi=300
    )
    plt.show()
    plt.close()


def quiver_ax_cartopy(ax, ds, title, u, v):
    ds = ds.coarsen(latitude=5, longitude=5, boundary="trim").mean()
    X, Y = np.meshgrid(ds["longitude"].values, ds["latitude"].values)

    Q = ax.quiver(X, Y, np.squeeze(ds[u].values), np.squeeze(ds[v].values), scale=250)
    qk = ax.quiverkey(Q, 0.5, 0.5, 5, r"5 m/s", labelpos="E", coordinates="figure")
    ax.set_title(title, fontsize=8)
    ax.coastlines()
    gl = ax.gridlines(draw_labels=True, x_inline=False, y_inline=False)
    gl.xlocator = mticker.FixedLocator([-120, -60, 0, 60, 120])

    return ax, gl


def three_panels(title):
    fig, axes = plt.subplots(ncols=1, nrows=3)
    axlist = axes.flat
    ds = xr.open_dataset("../data/processed/tvl1_coarse_january_5_t10_01_01_2020_pm.nc")
    ds = compute(ds)
    _ = quiver_ax(axlist[0], ds, "TV-L1", "u", "v", "(a)")
    Q = quiver_ax(axlist[1], ds, "ERA-5", "u_era5", "v_era5", "(b)")
    qk = axlist[1].quiverkey(Q, 0.4, 0.4, 5, r"5 m/s", labelpos="E", coordinates="axes")
    ds = xr.open_dataset(
        "../data/processed/farneback_coarse_january_5_t10_01_01_2020_pm.nc"
    )
    ds = compute(ds)
    _ = quiver_ax(axlist[2], ds, "Farneback", "u", "v", "(c)")
    fig.tight_layout()
    plt.savefig(
        "../data/processed/plots/" + title + ".png", bbox_inches="tight", dpi=300
    )
    plt.show()
    plt.close()


def two_panels(title, ds):
    fig, axes = plt.subplots(ncols=2, nrows=1)
    axlist = axes.flat
    ds = compute(ds)
    _ = quiver_ax(axlist[0], ds, "TV-L1", "u", "v", "(a)")
    Q = quiver_ax(axlist[1], ds, "ERA-5", "u_era5", "v_era5", "(b)")
    qk = axlist[1].quiverkey(Q, 0.4, 0.4, 5, r"5 m/s", labelpos="E", coordinates="axes")
    fig.tight_layout()
    plt.savefig(
        "../data/processed/plots/" + title + ".png", bbox_inches="tight", dpi=300
    )
    plt.show()
    plt.close()


def compute(ds):
    # ds=xr.open_dataset('../data/processed/inpaint_07_01_2020_pm.nc')
    # ds=ds.sel(plev=700, metho
    # ds=xr.open_dataset('../dad='nearest')
    # ds=ds.sel(plev=850, method='nearest')

    ds = ds.drop("obs_time")
    # ds=ds.rolling(latitude=10, longitude=10).median()
    ds["u_error"] = ds.u - ds.u_era5
    ds["v_error"] = ds.v - ds.v_era5
    ds["error_squared"] = ds.u_error**2 + ds.v_error**2
    ds["error_mag"] = np.sqrt(ds.error_squared)
    # ds=ds.sel(longitude=slice(-34,-6),latitude=slice(-30,-43))
    return ds


def main_figure(param, time):
    ds_total = xr.open_dataset("../data/processed/" + param.tag + ".nc")
    dates = param.dates
    for day in tqdm(dates):
        day_string = day.strftime("%Y_%m_%d")
        ds = ds_total.sel(day=day, time=time)
        ds = ds.sel(plev=850, method="nearest")
        ds = ds.sel(longitude=slice(-7, 27), latitude=slice(30, -25))
        ds = ds.sel(satellite="snpp")
        two_panels("test_" + time + "_" + day_string + "_" + param.tag, ds)


def main(param, time):
    ds_total = xr.open_dataset("../data/processed/" + param.tag + ".nc")
    dates = param.dates
    for day in tqdm(dates[:2]):
        day_string = day.strftime("%Y_%m_%d")
        ds = ds_total.sel(day=day, time=time)
        ds = ds.sel(plev=850, method="nearest")
        # ds=ds.sel(longitude=slice(-7,27),latitude=slice(30,-25))
        ds = ds.sel(satellite="snpp")
        quiver_plot_cartopy(ds, "test", "u", "v")
        quiver_plot_cartopy(ds, "test_era5", "u_era5", "v_era5")

    # three_panels('three_panel')


if __name__ == "__main__":
    param = parameters()
    param.set_Lambda(0.15)
    param.set_plev_coarse(5)
    param.set_alg("tvl1")
    param.set_timedelta(6)
    main(param, "pm")
