#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:47:49 2022

@author: aouyed
"""
import xarray as xr
from parameters import parameters
from datetime import datetime
import numpy as np
from tqdm import tqdm
import pandas as pd


def compute_error(ds, thresh):
    ds["u_error"] = ds["u"] - ds["u_era5"]
    ds["v_error"] = ds["v"] - ds["v_era5"]
    ds["error_mag"] = np.sqrt(ds["u_error"] ** 2 + ds["v_error"] ** 2)
    if thresh < 100:
        ds = ds.where(ds.error_mag < thresh)

    return ds


def main_old(param):
    for thresh in tqdm((100, 10, 4)):
        param.set_alg("tvl1")
        param.set_thresh(100)
        file = "../data/processed/" + param.tag + ".nc"
        ds = xr.open_dataset(file)
        u_wind = ds["u"].values
        v_wind = ds["v"].values

        u_random = np.random.uniform(low=-15, high=15, size=u_wind.shape)
        v_random = np.random.uniform(low=-15, high=15, size=u_wind.shape)

        u_random[u_wind == np.nan] = np.nan
        v_random[v_wind == np.nan] = np.nan

        ds["u"] = (
            ["plev", "time", "day", "latitude", "longitude", "satellite"],
            u_random,
        )
        ds["v"] = (
            ["plev", "time", "day", "latitude", "longitude", "satellite"],
            v_random,
        )

        param.set_alg("rand")
        param.set_thresh(thresh)
        ds = compute_error(ds, thresh)
        ds.to_netcdf("../data/processed/" + param.tag + ".nc")


def compute(ds, param):
    u_wind = ds["u"].values
    v_wind = ds["v"].values

    u_random = np.random.uniform(low=-15, high=15, size=u_wind.shape)
    v_random = np.random.uniform(low=-15, high=15, size=u_wind.shape)

    u_random[u_wind == np.nan] = np.nan
    v_random[v_wind == np.nan] = np.nan

    ds["u"] = (["plev", "time", "day", "latitude", "longitude", "satellite"], u_random)
    ds["v"] = (["plev", "time", "day", "latitude", "longitude", "satellite"], v_random)

    return ds


def main(param):
    for thresh in tqdm((100, 10, 4)):
        param.set_alg("tvl1")
        param.set_thresh(100)
        file = "../data/processed/" + param.tag + ".nc"
        ds = xr.open_dataset(file)
        u_wind = ds["u"].values
        v_wind = ds["v"].values

        u_random = np.random.uniform(low=-20, high=20, size=u_wind.shape)
        v_random = np.random.uniform(low=-20, high=20, size=u_wind.shape)

        u_random[u_wind == np.nan] = np.nan
        v_random[v_wind == np.nan] = np.nan

        ds["u"] = (
            ["plev", "time", "day", "latitude", "longitude", "satellite"],
            u_random,
        )
        ds["v"] = (
            ["plev", "time", "day", "latitude", "longitude", "satellite"],
            v_random,
        )

        param.set_alg("rand")
        param.set_thresh(thresh)
        ds = compute_error(ds, thresh)
        ds.to_netcdf("../data/processed/" + param.tag + ".nc")


if __name__ == "__main__":
    param = parameters()
    param.set_alg("tvl1")
    param.set_plev_coarse(5)
    param.set_month(datetime(2020, 1, 1))
    main(param)
    param.set_month(datetime(2020, 7, 1))
    main(param)
