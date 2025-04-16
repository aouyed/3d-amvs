"""
Spyder Editor

This is a temporary script file.
"""

import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import pandas as pd
import glob
from natsort import natsorted


def line_plotter(df0, values, title):
    fig, ax = plt.subplots()

    df = df0[df0.exp_filter == "exp2"]
    ax.plot(df["latlon"], df["rmse"], "-o", label="UA")

    df = df0[df0.exp_filter == "ground_t"]
    ax.plot(df["latlon"], df["rmse"], "-o", label="model error")

    df = df0[df0.exp_filter == "df"]
    ax.plot(df["latlon"], df["rmse"], "-o", label="UA First Stage")

    df = df0[df0.exp_filter == "jpl"]
    ax.plot(df["latlon"], df["rmse"], "-o", label="JPL")

    ax.legend(frameon=None)
    ax.set_ylim(0, ERROR_MAX)
    ax.set_xlabel("Region")
    ax.set_ylabel("RMSVD [m/s]")
    ax.set_title(title)
    directory = "../data/processed/density_plots"
    plt.savefig(values + ".png", bbox_inches="tight", dpi=300)
    plt.close()


def weighted_mean(da):
    """Calculates regional cosine weighted means from dataset"""

    weights = np.cos(np.deg2rad(da.latitude))
    weights.name = "weights"

    da_weighted = da.weighted(weights)
    w_mean = da_weighted.mean(list(da.coords), skipna=True)
    return w_mean.item()


def weighted_mean_cross(da):
    """Calculates regional cosine weighted means from dataset"""

    weights = np.cos(np.deg2rad(da.latitude))
    weights.name = "weights"

    da_weighted = da.weighted(weights)
    w_mean = da_weighted.mean(skipna=True)
    return w_mean.item()


def weighted_sum(da):
    """Calculates regional cosine weighted means from dataset"""

    weights = np.cos(np.deg2rad(da.latitude))
    weights.name = "weights"
    da_weighted = da.weighted(weights)
    w_sum = da_weighted.sum(("longitude", "latitude"), skipna=True)
    condition = xr.ufuncs.logical_not(xr.ufuncs.isnan(da))
    weights = weights.where(condition)
    return w_sum.item()


def weights_sum(da):
    """Calculates regional cosine weighted means from dataset"""

    weights = np.cos(np.deg2rad(da.latitude))
    weights.name = "weights"
    condition = xr.ufuncs.logical_not(xr.ufuncs.isnan(da))
    weights = weights.where(condition)
    return weights.sum().item()


def sorting_latlon(df0):
    df0.edges[df0.edges == "-70,-30"] = "(1) 70°S,30°S"
    df0.edges[df0.edges == "-30,30"] = "(2) 30°S,30°N"
    df0.edges[df0.edges == "30,70"] = "(3) 30°N,70°N"
    df0.sort_values(by=["edges"], inplace=True)
    return df0


def rmse_calc(ds, thresh):
    ds = ds.sel(plev=850, method="nearest")
    rmse_dict = {"edges": [], "rmse": [], "shear": [], "shear_era5": []}
    edges = [[-30, 30], [30, 60], [60, 90], [-60, -30], [-90, -60]]

    for edge in edges:
        ds_unit = ds.sel(latitude=slice(edge[1], edge[0]))
        rmse = np.sqrt(weighted_mean(ds_unit["error_mag"]))
        shear = weighted_mean(ds_unit["shear_two_levels"])
        shear_era5 = weighted_mean(ds_unit["shear_two_levels_era5"])
        edge = coord_to_string(edge)
        rmse_dict["edges"].append(str(edge[0]) + "," + str(edge[1]))
        rmse_dict["rmse"].append(rmse)
        rmse_dict["shear"].append(shear)
        rmse_dict["shear_era5"].append(shear_era5)
    df = pd.DataFrame(data=rmse_dict)
    df.to_csv("../data/interim/dataframes/t" + str(thresh) + ".csv")
    print(df)
    return df


def coord_to_string(coord):
    if coord[1] < 0:
        uplat = str(abs(coord[1])) + "°S"
    else:
        uplat = str(coord[1]) + "°N"

    if coord[0] < 0:
        lowlat = str(abs(coord[0])) + "°S"
    else:
        lowlat = str(coord[0]) + "°N"
    stringd = str(str(lowlat) + "," + str(uplat))
    return stringd
