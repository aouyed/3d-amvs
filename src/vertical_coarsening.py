#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 15:58:19 2022

@author: aouyed
"""
import xarray as xr
import pandas as pd
import numpy as np
import config
import datetime
from tqdm import tqdm
from parameters import parameters


def compute(ds, thresh):

    u_error = ds["u"] - ds["u_era5"]
    v_error = ds["v"] - ds["v_era5"]
    ds["error_mag"] = np.sqrt(u_error**2 + v_error**2)
    ds = ds.where(ds.error_mag < thresh)
    ds = ds.drop("error_mag")
    return ds


def vertical_coarse(ds, thresh, n_layers):
    ds = ds.reindex(plev=list(reversed(ds.plev)))
    ds = compute(ds, thresh)
    ds_c = (
        ds[["u", "v", "u_era5", "v_era5", "humidity_overlap"]]
        .coarsen(plev=n_layers, boundary="trim")
        .median()
    )
    obs_array = ds["obs_time"].sel(plev=850, method="nearest")
    obs_array = obs_array.values
    obs_array = np.squeeze(obs_array)
    ds_c["obs_time"] = (["latitude", "longitude", "satellite"], obs_array)
    return ds_c


def main(param):
    dates = param.dates

    for date in tqdm(dates):
        date_string = date.strftime("%m_%d_%Y")
        thresh = param.thresh
        for orbit in ("am", "pm"):
            ds = xr.open_dataset(
                "../data/processed/"
                + param.alg
                + "_lambda_"
                + str(param.Lambda)
                + "_"
                + date_string
                + "_"
                + orbit
                + ".nc"
            )
            ds = vertical_coarse(ds, thresh, param.plev_coarse)
            ds.to_netcdf(
                "../data/processed/"
                + param.tag
                + "_"
                + date_string
                + "_"
                + orbit
                + ".nc"
            )


if __name__ == "__main__":
    param = parameters()
    main(param)
