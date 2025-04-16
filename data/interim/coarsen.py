#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 15:06:32 2023

@author: aouyed
"""

import glob
import xarray as xr


files = glob.glob("coarse_model*.nc")
for file in files:
    print(file)
    ds = xr.open_dataset(file)
    ds = ds.coarsen(level=3, boundary="trim").mean()
    ds.to_netcdf("vc_" + file)
