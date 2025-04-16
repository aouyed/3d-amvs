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
from parameters import parameters

pd.options.mode.chained_assignment = None  # default='warn'

QC = c.QC


ALG = "farneback"


R = 6371000

drad = np.deg2rad(1)
dx = R * drad
scale_x = dx
dy = R * drad
scale_y = dy
swath_hours = 24


LABEL = "specific_humidity_mean"


def ds_closer(date, ds, time, param):
    date = pd.to_datetime(str(date))
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    print(ds)
    ds.to_netcdf(
        "../data/processed/"
        + param.alg
        + "_"
        + "lambda_"
        + str(param.Lambda)
        + "_"
        + month
        + "_"
        + day
        + "_"
        + year
        + "_"
        + time
        + ".nc"
    )


def model_closer(date):
    date = pd.to_datetime(str(date))
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    os.remove("../data/interim/model_" + month + "_" + day + "_" + year + ".nc")


def model_loader(date, pressure):
    date = pd.to_datetime(str(date))
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    ds_model = xr.open_dataset(
        "../data/interim/coarse_model_" + month + "_" + day + "_" + year + ".nc"
    )
    ds_model = ds_model.sel(level=pressure, method="nearest")
    ds_model = ds_model.drop("level")
    # ds_model['vort_era5_smooth']=  ds_model['vo'].rolling(
    #    latitude=5, longitude=5, center=True).mean()
    # ds_model['div_era5_smooth']=  ds_model['d'].rolling(
    #   latitude=5, longitude=5, center=True).mean()
    ds_model = ds_model.assign_coords(
        longitude=(((ds_model.longitude + 180) % 360) - 180)
    )
    ds_model = ds_model.reindex(longitude=np.sort(ds_model["longitude"].values))
    return ds_model


def ds_unit_calc(ds, day, pressure, time, param):
    ds = ds.loc[{"day": day, "plev": pressure, "time": time}]
    ds = ds.drop(["day", "plev", "time"])
    ds = calc.prepare_ds(ds)
    ds_model = model_loader(day, pressure)
    df = ds.to_dataframe()
    swathes = calc.swath_initializer(ds, 5, swath_hours)
    for swath in swathes:
        ds_snpp = ds.loc[{"satellite": "snpp"}]
        ds_j1 = ds.loc[{"satellite": "j1"}]
        start = swath[0]
        end = swath[1]
        ds_merged, ds_snpp, ds_j1, df_snpp = calc.prepare_patch(
            ds_snpp, ds_j1, ds_model, start, end
        )

        if df_snpp.shape[0] > 100:
            df, ds_snpp_p, ds_j1_p, ds_model_p = calc.amv_calculator(
                ds_merged, df, param
            )

    ds = xr.Dataset.from_dataframe(df)

    return ds


def serial_loop(ds, param):
    for day in tqdm(param.dates):
        print(day)
        # ed.downloader(day)
        for time in ds["time"].values:
            ds_total = xr.Dataset()
            for pressure in tqdm(ds["plev"].values):
                ds_unit = ds_unit_calc(ds, day, pressure, time, param)
                ds_unit = ds_unit.expand_dims("day").assign_coords(day=np.array([day]))
                ds_unit = ds_unit.expand_dims("time").assign_coords(
                    time=np.array([time])
                )
                ds_unit = ds_unit.expand_dims("plev").assign_coords(
                    plev=np.array([pressure])
                )

                if not ds_total:
                    ds_total = ds_unit
                else:
                    ds_total = xr.concat([ds_total, ds_unit], "plev")

            ds_closer(day, ds_total, time, param)
        # model_closer(day)


def main(param):
    month_string = param.month_string
    ds = xr.open_dataset(
        "../data/processed/real_water_vapor_noqc_" + month_string + ".nc"
    )
    # ds=ds.sel(plev=[850,700,500,400], method='nearest')
    print(ds)
    # ds=xr.open_dataset('../data/processed/jan_28_climcaps.nc')
    # ds=ds.sel(plev=ds['plev'].values[-1:])
    serial_loop(ds, param)


if __name__ == "__main__":
    param = parameters()
    # param.set_alg('farneback')
    param.set_plev_coarse(5)
    param.set_alg("tvl1")
    param.set_Lambda(0.15)
    param.set_timedelta(6)
    print(param.Lambda)
    start_time = time.time()
    main(param)
    print("--- %s seconds ---" % (time.time() - start_time))
