#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 31 15:22:15 2022

@author: aouyed
"""

from parameters import parameters
import datetime
import pandas as pd
import xarray as xr


def main(param):

    dates = param.dates
    ds_total = xr.Dataset()
    for day in dates:
        print(day)
        ds_unit = xr.Dataset()
        for time in ("am", "pm"):
            dsdate = day.strftime("%m_%d_%Y")
            ds = xr.open_dataset(
                "../data/processed/" + param.tag + "_" + dsdate + "_" + time + ".nc"
            )
            if not ds_unit:
                ds_unit = ds
            else:
                ds_unit = xr.concat([ds_unit, ds], "time")
        if not ds_total:
            ds_total = ds_unit
        else:
            ds_total = xr.concat([ds_total, ds_unit], "day")
    print(ds_total)
    ds_total.to_netcdf("../data/processed/" + param.tag + ".nc")


if __name__ == "__main__":
    param = parameters()
    param.set_thresh(100)
    param.set_alg("tvl1")
    param.set_month(datetime.datetime(2020, 1, 1))
    main(param)
    param.set_month(datetime.datetime(2020, 7, 1))
    main(param)
