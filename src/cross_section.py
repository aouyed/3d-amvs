#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 12:06:15 2021

@author: aouyed

"""
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
from metpy.interpolate import cross_section
import metpy.calc as mpcalc
from metpy.units import units
import quiver
import cartopy.crs as ccrs
from datetime import datetime
import stats_calculators as sc
import config as c
from parameters import parameters

SCALE = 1e4
scale_g = 1000
PRESSURES = c.PRESSURES
GEODESICS = c.GEODESICS

# month_string=param.month.strftime("%B").lower()


def shear_calc(ds, tag=""):
    u = ds["u" + tag].rolling(plev=3, latitude=3, longitude=3).mean()
    v = ds["v" + tag].rolling(plev=3, latitude=3, longitude=3).mean()
    u_diff = u.differentiate("plev")
    v_diff = v.differentiate("plev")
    p_diff = ds["plev"].differentiate("plev")
    ds["u_shear" + tag] = u_diff / p_diff
    ds["v_shear" + tag] = v_diff / p_diff
    return ds


def shear_two_levels(ds, tag=""):
    u_diff = ds["u" + tag].sel(plev=850, method="nearest") - ds["u" + tag].sel(
        plev=500, method="nearest"
    )
    v_diff = ds["v" + tag].sel(plev=850, method="nearest") - ds["v" + tag].sel(
        plev=500, method="nearest"
    )
    shear = np.sqrt(u_diff**2 + v_diff**2)
    return shear


def cloud_filter(ds, date):

    ds_qc = xr.open_dataset("../data/processed/real_water_vapor_qc.nc")
    ds_snpp = ds_qc.loc[{"satellite": "snpp", "time": "am"}]
    ds_j1 = ds_qc.loc[{"satellite": "j1", "time": "am"}]
    ds_j1 = ds_j1.drop(["day", "satellite", "time"])
    ds_snpp = ds_snpp.drop(["day", "satellite", "time"])
    condition1 = xr.ufuncs.logical_not(xr.ufuncs.isnan(ds_j1["obs_time"]))
    condition2 = xr.ufuncs.logical_not(xr.ufuncs.isnan(ds_snpp["obs_time"]))
    ds = ds.where(condition1 & condition2)
    return ds


def preprocess(ds):

    ds["u_error"] = ds["u"] - ds["u_era5"]
    ds["v_error"] = ds["v"] - ds["v_era5"]
    ds["error_mag"] = np.sqrt(ds["u_error"] ** 2 + ds["v_error"] ** 2)
    ds["squared_error"] = ds["u_error"] ** 2 + ds["v_error"] ** 2
    ds["speed"] = np.sqrt(ds["u"] ** 2 + ds["v"] ** 2)
    ds["speed_era5"] = np.sqrt(ds["u_era5"] ** 2 + ds["v_era5"] ** 2)
    ds["speed_diff"] = ds["speed"] - ds["speed_era5"]
    condition = xr.ufuncs.logical_not(xr.ufuncs.isnan(ds["humidity_overlap"]))
    ds = ds.where(condition)
    return ds


def quiver_ax(ax, ds, title, u, v, xlabel, qkey=5, units="m/s"):
    # ds = ds.coarsen(index=2, plev=2, boundary='trim').mean()
    # ds = ds.rolling(index=2, plev=2).mean()

    X, Y = np.meshgrid(ds[xlabel].values, ds["plev"].values)
    Q = ax.quiver(X, Y, np.squeeze(ds[u].values), np.squeeze(ds[v].values), scale=300)
    ax.quiverkey(
        Q, 0.8, 0.5, qkey, str(qkey) + " m/s", labelpos="E", coordinates="figure"
    )
    # ax.set_ylim(ax.get_ylim()[::-1])

    ax.set_yscale("symlog")
    ax.set_yticklabels(np.arange(1000, 50, -200))
    ax.set_ylim(ds["plev"].max(), ds["plev"].min())
    ax.set_yticks(np.arange(1000, 50, -200))
    # ax.set_ylim(850,400)
    return ax


def inset_plot(geodesic, fig):
    ax_inset = fig.add_axes([0.085, 0.9, 0.25, 0.25], projection=ccrs.PlateCarree())
    start = geodesic[0]
    end = geodesic[1]
    ax_inset.set_global()
    ax_inset.plot(
        [start[1], end[1]], [start[0], end[0]], transform=ccrs.Geodetic(), linewidth=3
    )
    ax_inset.coastlines()
    return ax_inset


def multiple_quiver(
    letters,
    ds,
    title,
    geodesic,
    xlabel,
    thresh,
    tag="",
    qkey=5,
    units="m/s",
    inset=True,
):

    fig, axes = plt.subplots(nrows=2, ncols=1)
    if inset:
        ax_inset = inset_plot(geodesic, fig)

    axlist = axes.flat
    axlist[0] = quiver_ax(
        axlist[0], ds, title, "u" + tag, "v" + tag, xlabel, qkey, units
    )
    axlist[0].set_xlabel(geodesic[2])
    axlist[0].set_ylabel("Pressure [hPa]")
    axlist[0].text(0.02, 0.85, letters[0], transform=axlist[0].transAxes)

    axlist[1] = quiver_ax(
        axlist[1],
        ds,
        title + "_era5",
        "u" + tag + "_era5",
        "v" + tag + "_era5",
        xlabel,
        qkey,
        units,
    )
    axlist[1].text(0.02, 0.85, letters[1], transform=axlist[1].transAxes)
    axlist[0].text(0.8, 1.1, "δ = " + thresh + " m/s", transform=axlist[0].transAxes)
    rmsvd = np.sqrt(sc.weighted_mean_cross(ds["squared_error"]))
    axlist[0].text(
        0.4,
        1.1,
        "RMSVD = " + str(round(rmsvd, 2)) + " m/s",
        transform=axlist[0].transAxes,
    )

    fig.tight_layout()
    plt.savefig(
        "../data/processed/plots/" + title + ".png", bbox_inches="tight", dpi=300
    )
    plt.show()
    plt.close()


def multiple_quiver_map(ds, title, letter, thresh, tag=""):
    fig, axes = plt.subplots(
        nrows=2, ncols=2, subplot_kw={"projection": ccrs.PlateCarree()}
    )
    axlist = axes.flat

    for index, pressure in enumerate(PRESSURES):
        print(axlist[index])
        ds_unit = ds.sel(plev=pressure, method="nearest")
        quiver.quiver_ax_cartopy(
            axlist[index], ds_unit, str(pressure) + " hPa", "u" + tag, "v" + tag
        )

    axlist[0].text(-180, 100, letter)
    axlist[1].text(80, 100, "δ = " + thresh + " m/s")
    fig.tight_layout()
    print("saving " + title)
    plt.savefig(
        "../data/processed/plots/" + title + ".png", bbox_inches="tight", dpi=300
    )
    plt.show()
    plt.close()


def four_panel_quiver_map(ds, title, thresh, pressures):
    fig, axes = plt.subplots(
        nrows=2, ncols=2, subplot_kw={"projection": ccrs.PlateCarree()}
    )
    axlist = axes.flat

    for j, tag in enumerate(("", "_era5")):
        for index, pressure in enumerate(pressures):
            ds_unit = ds.sel(plev=pressure, method="nearest")
            plev_string = ds_unit["plev"].values.item()
            plev_string = str(round(plev_string, 1))
            ds_unit = ds_unit.drop("plev")

            if tag == "":

                ds_unit = ds.sel(plev=pressure, method="nearest")
                ds_unit = ds_unit.drop("plev")
                title_tag = plev_string + " hPa"
            else:
                title_tag = "ERA 5"
            axes[index, j], gl = quiver.quiver_ax_cartopy(
                axes[index, j], ds_unit, title_tag, "u" + tag, "v" + tag
            )
            if tag == "":
                rmsvd = np.sqrt(sc.weighted_mean(ds_unit["squared_error"]))
                print(rmsvd)
                axes[index, j].text(
                    0.5,
                    0.05,
                    "RMSVD = " + str(round(rmsvd, 2)) + " m/s",
                    fontsize=7,
                    c="red",
                    transform=axes[index, j].transAxes,
                )
                gl.xlabels_top = False
                gl.ylabels_right = False
            elif tag == "_era5":
                gl.xlabels_top = False
                gl.ylabels_left = False

    plt.tight_layout()
    fig.subplots_adjust(hspace=0.15)

    print("saving " + title)
    plt.savefig(
        "../data/processed/plots/" + title + ".png", bbox_inches="tight", dpi=500
    )
    plt.show()
    plt.close()


def latlon_uniques(ds):
    lat, lon = np.meshgrid(ds["latitude"].values, ds["longitude"].values)
    ds["lat"] = (["longitude", "latitude"], lat)
    ds["lon"] = (["longitude", "latitude"], lon)
    condition1 = xr.ufuncs.logical_not(xr.ufuncs.isnan(ds["humidity_overlap"]))
    ds_test = ds.where(condition1)
    var = ds_test["lat"].values
    uniques = np.unique(var[~np.isnan(var)])
    print("lat unique")
    print(uniques)
    var = ds_test["lon"].values
    uniques = np.unique(var[~np.isnan(var)])
    print("lon unique")
    print(uniques)
    var = ds_test["humidity_overlap"].values
    uniques = np.unique(var[~np.isnan(var)]).shape
    print("humidity_overlap")
    print(uniques)


def cross_sequence(ds, thresh, time, param):

    # ds=ds.drop(['obs_time','obs_time_tai93'])
    ds = ds.metpy.assign_crs(
        grid_mapping_name="latitude_longitude", earth_radius=6371229.0
    )
    data = ds.metpy.parse_cf().squeeze()
    latlon_uniques(data.copy())
    tag = "_t" + str(thresh)
    for geokey in GEODESICS:
        geodesic = GEODESICS[geokey]
        start = geodesic[0]
        end = geodesic[1]
        xlabel = geodesic[2]
        cross = cross_section(data, start, end, interp_type="nearest").set_coords(
            ("latitude", "longitude")
        )
        cross = cross.reindex(plev=list(reversed(cross.plev)))
        multiple_quiver(
            ["(a)", "(b)"],
            cross,
            param.tag + "_quiver_" + time + "_" + geokey + tag,
            geodesic,
            xlabel,
            str(thresh),
            qkey=5,
        )
        multiple_quiver(
            ["(c)", "(d)"],
            cross,
            param.tag + "_quiver_" + time + "_" + geokey + tag + "_noinset",
            geodesic,
            xlabel,
            str(thresh),
            qkey=5,
            inset=False,
        )


def main(param):
    time = "am"
    dsdate = param.month.strftime("%m_%d_%Y")
    for thresh in [10]:
        # time='am0'

        param.set_thresh(thresh)
        file_name = "../data/processed/" + param.tag + ".nc"
        ds = xr.open_dataset(file_name)
        date = param.month
        ds = ds.loc[{"day": date, "time": time, "satellite": "snpp"}].squeeze()
        ds = ds.drop(["day", "time", "satellite"])
        ds["humidity_overlap"] = scale_g * ds["humidity_overlap"]
        # time='am0'

        ds = preprocess(ds)

        ds = ds.drop("obs_time")

        cross_sequence(ds, thresh, time, param)
        four_panel_quiver_map(ds, "quiver_p1_" + param.tag, str(thresh), [850, 700])
        four_panel_quiver_map(ds, "quiver_p2_" + param.tag, str(thresh), [500, 400])


if __name__ == "__main__":
    param = parameters()
    param.set_alg("tvl1")
    param.set_Lambda(0.15)
    param.set_month(datetime(2020, 7, 1))
    main(param)
