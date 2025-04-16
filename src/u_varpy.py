#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 13:29:33 2023

@author: aouyed
"""

import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def map_plotter_cartopy(da, filename, title, units_label=""):
    values = da
    fig = plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    ax.gridlines()
    im = ax.imshow(
        values,
        cmap="viridis",
        extent=[
            ds["longitude"].min(),
            ds["longitude"].max(),
            ds["latitude"].min(),
            ds["latitude"].max(),
        ],
        vmin=0,
        vmax=15,
        origin="lower",
    )
    ax.gridlines(draw_labels=True, x_inline=False, y_inline=False)
    ax.set_title(title)
    # ax.scatter(df.longitude, df.latitude)
    # plt.title(label)
    cbar_ax = fig.add_axes([0.1, 0.05, 0.78, 0.05])
    fig.colorbar(im, cax=cbar_ax, orientation="horizontal", pad=0.5, label=units_label)
    plt.savefig(
        "../data/processed/plots/" + filename + ".png", bbox_inches="tight", dpi=300
    )
    plt.show()
    plt.close()


def ax_cartopy(da, ax, title, units_label=""):
    values = da.values
    ax.coastlines()
    im = ax.imshow(
        values,
        cmap="viridis",
        extent=[
            ds["longitude"].min(),
            ds["longitude"].max(),
            ds["latitude"].min(),
            ds["latitude"].max(),
        ],
        vmin=0,
        vmax=15,
        origin="lower",
    )
    gl = ax.gridlines(draw_labels=True, x_inline=False, y_inline=False)
    ax.set_title(title)
    return im, gl


def multiple_plots(diff, filename):
    fig, axes = plt.subplots(
        nrows=2, ncols=1, subplot_kw={"projection": ccrs.PlateCarree()}
    )
    axlist = axes.flat
    diff_h = diff.sel(level=850, time=diff["time"].values[1], method="nearest")
    print(diff["time"].values[1])
    press = diff_h["level"].item()
    press = round(press, 2)
    mean = diff_h.mean().item()
    mean = round(mean, 2)
    std = diff_h.std().item()
    std = round(std, 2)
    title = (
        "P = "
        + str(press)
        + " hPa, mean = "
        + str(mean)
        + " m/s,  std = "
        + str(std)
        + " m/s"
    )
    level = diff_h["level"].values
    level = str(int(level.item()))
    _, gl = ax_cartopy(diff_h, axlist[0], title, "m/s")
    gl.xlabels_bottom = False
    gl.xlabels_top = False
    gl.ylabels_right = False

    diff_h = diff.sel(level=200, time=diff["time"].values[1], method="nearest")
    press = diff_h["level"].item()
    press = round(press, 2)
    mean = diff_h.mean().item()
    mean = round(mean, 2)
    std = diff_h.std().item()
    std = round(std, 2)
    title = (
        "P = "
        + str(press)
        + " hPa, mean = "
        + str(mean)
        + " m/s,  std = "
        + str(std)
        + " m/s"
    )
    level = diff_h["level"].values
    level = str(int(level.item()))
    im, gl = ax_cartopy(diff_h, axlist[1], title, "m/s")
    gl.xlabels_top = False
    gl.ylabels_right = False
    cbar_ax = fig.add_axes([0.12, -0.07, 0.77, 0.05])

    fig.colorbar(im, cax=cbar_ax, orientation="horizontal", label="ΔU [m/s]")

    fig.tight_layout()
    plt.savefig(
        "../data/processed/plots/" + filename + ".png", bbox_inches="tight", dpi=300
    )
    plt.show()
    plt.close()


ds = xr.open_dataset("../data/interim/model_01_01_2020.nc")

print(ds["level"].values)

ds = ds.sel(level=slice(200, 900))

u_min = ds["v"].coarsen(longitude=4, latitude=4, time=2, level=1, boundary="trim").min()
u_max = ds["v"].coarsen(longitude=4, latitude=4, time=2, level=1, boundary="trim").max()

diff = u_max - u_min

multiple_plots(diff, "u_test")
