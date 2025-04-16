#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 15:17:31 2021

@author: aouyed
"""
import os
import xarray as xr
import numpy as np
import amv_calculators as calc
import time
import pandas as pd
import era5_downloader as ed
from datetime import datetime
import config as c
from tqdm import tqdm

swath_hours = 24


def overlap(ds, start, end):

    ds_snpp = ds.loc[{"satellite": "snpp"}]
    ds_j1 = ds.loc[{"satellite": "j1"}]

    ds_j1 = ds_j1.where((ds_j1.obs_time >= start) & (ds_j1.obs_time <= end))
    start = start + np.timedelta64(50, "m")
    end = end + np.timedelta64(50, "m")
    ds_snpp = ds_snpp.where((ds_snpp.obs_time >= start) & (ds_snpp.obs_time <= end))
    df_j1 = (
        ds_j1.to_dataframe()
        .dropna(subset=["humidity_overlap"])
        .set_index("satellite", append=True)
    )
    df_snpp = (
        ds_snpp.to_dataframe()
        .dropna(subset=["humidity_overlap"])
        .set_index("satellite", append=True)
    )
    ds_j1 = xr.Dataset.from_dataframe(df_j1)
    ds_snpp = xr.Dataset.from_dataframe(df_snpp)
    if df_snpp.shape[0] > 100:
        shape = np.squeeze(ds_snpp["humidity_overlap"]).shape
        tcount = shape[0] * shape[1]
        count = df_snpp.shape[0]
        ratio = count / tcount
        ds_snpp["ratio"] = ratio

        shape = np.squeeze(ds_j1["humidity_overlap"]).shape
        tcount = shape[0] * shape[1]
        count = df_snpp.shape[0]
        ratio = count / tcount
        ds_j1["ratio"] = ratio
    return ds_j1, ds_snpp, df_j1, df_snpp


def calculate_ratio():
    ds = xr.open_dataset("../data/processed/full_nn_tlv1_01_01_2020_am.nc")
    swathes = calc.swath_initializer(ds, 5, swath_hours)
    ds["ratio"] = xr.full_like(ds["specific_humidity_mean"], fill_value=np.nan)
    for pressure in tqdm(ds["plev"].values):
        ds_unit = ds.sel(plev=pressure)
        for swath in swathes:
            ds_snpp = ds_unit.loc[{"satellite": "snpp"}]
            ds_j1 = ds_unit.loc[{"satellite": "j1"}]
            start = swath[0]
            end = swath[1]
            ds_j1, ds_snpp, df_j1, df_snpp = overlap(ds_unit, start, end)
            if df_snpp.shape[0] > 100:
                # plotter.map_plotter_cartopy(ds_snpp,'swath', 'humidity_overlap','viridis')
                ds["ratio"].loc[
                    {
                        "latitude": ds_snpp["latitude"].values,
                        "longitude": ds_snpp["longitude"].values,
                        "satellite": "snpp",
                        "plev": pressure,
                    }
                ] = ds_snpp["ratio"]

                ds["ratio"].loc[
                    {
                        "latitude": ds_snpp["latitude"].values,
                        "longitude": ds_snpp["longitude"].values,
                        "satellite": "j1",
                        "plev": pressure,
                    }
                ] = ds_j1["ratio"]

    ds.to_netcdf("../data/processed/ratio.nc")


def calculate_corr():
    ds = xr.open_dataset("../data/processed/ratio.nc")
    u_error = ds["u"] - ds["u_era5"]
    v_error = ds["v"] - ds["v_era5"]
    print(ds["ratio"].mean())
    print(ds["ratio"].std())

    ds["error_mag"] = np.sqrt(u_error**2 + v_error**2)
    print(xr.corr(ds.ratio, ds.error_mag) ** 2)


def main():
    calculate_corr()


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
