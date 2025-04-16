#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 16:40:11 2021
@author: aouyed
"""
import cv2
import xarray as xr
import numpy as np
from scipy.interpolate import griddata
from scipy import ndimage as nd


def drop_nan(frame):
    mask = np.isnan(frame)
    mask = np.uint8(mask)
    frame = np.nan_to_num(frame)
    frame = np.float32(frame)
    frame = cv2.inpaint(frame, mask, inpaintRadius=10, flags=cv2.INPAINT_NS)
    return frame


def interpol_nan(ds, label):
    X, Y = np.meshgrid(ds["longitude"].values, ds["latitude"].values)
    values = np.squeeze(ds[label].values)
    values[values == 0] = np.nan
    mask = np.isnan(values)
    frame = fill(values)
    ds[label + "_inpainted"] = (["latitude", "longitude"], frame)

    return ds


def fill(data, invalid=None):
    """
    Replace the value of invalid 'data' cells (indicated by 'invalid')
    by the value of the nearest valid data cell
    Input:
        data:    numpy array of any dimension
        invalid: a binary array of same shape as 'data'.
                 data value are replaced where invalid is True
                 If None (default), use: invalid  = np.isnan(data)
    Output:
        Return a filled array.
    """
    if invalid is None:
        invalid = np.isnan(data)

    ind = nd.distance_transform_edt(
        invalid, return_distances=False, return_indices=True
    )
    return data[tuple(ind)]


def inpainter_loop(ds, label):
    # label='specific_humidity_mean'
    # ds=xr.open_dataset('../data/processed/real_water_vapor_noqc.nc')
    print(ds)
    ds[label + "_inpainted"] = xr.full_like(ds[label], fill_value=np.nan)
    for pressure in ds["plev"].values:
        print(pressure)

        ds_unit = ds.loc[{"plev": pressure}]
        ds_unit = interpol_nan(ds_unit, label)
        ds[label + "_inpainted"].loc[{"plev": pressure}] = ds_unit[label + "_inpainted"]
    return ds


def main():
    inapinter_loop()


if __name__ == "__main__":
    main()
