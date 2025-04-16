#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 12:30:39 2022

@author: aouyed
"""

import xarray as xr
import numpy as np
import amv_calculators as ac
import time
import quiver as q
import pandas as pd
import datetime
from tqdm import tqdm
import matplotlib.pyplot as plt

THETA = 0.0625
R = ac.R
PATH = "/Volumes/reserarchDi/12_16_20/experiments/jpl/july/"
FACTORS = [16, 8, 4, 1]
dt = 3600
dt_inv = 1 / dt


def prepare_ds(ds, factor):
    ds1 = ds.sel(pressure=500, method="nearest")
    ds1 = ds1.sel(lat=slice(-70, 70))

    ds1 = ds1.coarsen(lat=factor, lon=factor, boundary="trim").mean()
    return ds1


def main():
    speed_biases = {
        "date": [],
        "resolution": [],
        "speed_bias": [],
        "rmsvd": [],
        "square_error_mu": [],
    }

    alg = "deepflow"

    start = datetime.datetime(2006, 7, 1)
    end = datetime.datetime(2006, 7, 3, 18)
    dates = pd.date_range(start=start, end=end, freq="6h")
    deltat = datetime.timedelta(minutes=30)

    for date in tqdm(dates):
        for factor in FACTORS:
            res = factor * THETA
            drad = np.deg2rad(res)
            dx = R * drad
            scale_x = dx
            dy = R * drad
            scale_y = dy

            date1 = date - deltat
            date2 = date + deltat
            date_string1 = date1.strftime("%Y%m%d_%H%M")
            date_string2 = date2.strftime("%Y%m%d_%H%M")

            ds = xr.open_dataset(PATH + "NRData_" + date_string1 + ".nc")
            ds1 = prepare_ds(ds, factor)
            frame0 = np.squeeze(ds1["qv"].values)
            ds = xr.open_dataset(PATH + "NRData_" + date_string2 + ".nc")
            ds2 = prepare_ds(ds, factor)
            frame = np.squeeze(ds2["qv"].values)

            flowx, flowy = ac.calc(frame0, frame, 0.15, alg)

            ds = (ds1 + ds2) * 0.5

            ds["flowx"] = (["lat", "lon"], flowx)
            ds["flowy"] = (["lat", "lon"], flowy)

            dx_conv = abs(np.cos(np.deg2rad(ds.lat)))
            ds["utrack"] = scale_x * dx_conv * dt_inv * ds["flowx"]
            ds["vtrack"] = scale_y * dt_inv * ds["flowy"]
            ds["speed"] = np.sqrt(ds.u**2 + ds.v**2)
            ds["speed_track"] = np.sqrt(ds.utrack**2 + ds.vtrack**2)
            ds["speed_bias"] = ds.speed_track - ds.speed
            ds["u_error"] = ds.utrack - ds.u
            ds["v_error"] = ds.vtrack - ds.v
            ds["square_error"] = ds.u_error**2 + ds.v_error**2

            square_error_mu = ds["square_error"].mean().item()
            rmsvd = np.sqrt(square_error_mu)
            speed_bias = ds["speed_bias"].mean().item()
            speed_biases["resolution"].append(res)
            speed_biases["speed_bias"].append(speed_bias)
            speed_biases["rmsvd"].append(rmsvd)
            speed_biases["square_error_mu"].append(square_error_mu)
            speed_biases["date"].append(date)

            # ds=ds.rename({'lat':'latitude','lon':'longitude'})
            # q.quiver_plot_cartopy(ds,'res_test'+alg +str(factor),'utrack','vtrack')
            # q.quiver_plot_cartopy(ds,'nr_test'+str(factor),'u','v')

    df = pd.DataFrame(data=speed_biases)
    print(df)
    df.to_pickle("../data/processed/july_deepflow.pkl")


def df_loop(df):
    plot_data = {"resolution": [], "speed_bias": [], "rmsvd": []}
    for factor in FACTORS[::-1]:
        res = factor * THETA
        speed_bias = df.loc[df.resolution == res, ["speed_bias"]].mean().item()
        rmsvd = np.sqrt(df.loc[df.resolution == res, ["square_error_mu"]].mean().item())
        plot_data["resolution"].append(res)
        plot_data["speed_bias"].append(speed_bias)
        plot_data["rmsvd"].append(rmsvd)

    df_mean = pd.DataFrame(data=plot_data)
    return df_mean


def df_plot(df1, df2, variable="speed_bias", labels=["january", "july"]):
    fig, ax = plt.subplots()
    ax.plot(df1["resolution"], df1[variable], label=labels[0], marker=".")
    ax.plot(df2["resolution"], df2[variable], label=labels[1], marker=".")
    ax.set_xlabel("Resolution [deg]")
    ax.set_ylabel(variable + " [m/s]")
    ax.legend()
    plt.savefig(
        "../data/processed/plots/"
        + labels[0]
        + "_"
        + labels[1]
        + "_"
        + variable
        + "_res.png",
        dpi=300,
    )
    plt.show()
    plt.close()


def df_mean():
    df_jan = pd.read_pickle("../data/processed/january_deepflow.pkl")
    df_jan = df_loop(df_jan)
    df_july = pd.read_pickle("../data/processed/july_deepflow.pkl")
    df_july = df_loop(df_july)
    breakpoint()
    df_plot(df_jan, df_july)
    df_plot(df_jan, df_july, variable="rmsvd")
    df_tvl1 = pd.read_pickle("../data/processed/january_tvl1.pkl")
    df_tvl1 = df_loop(df_tvl1)
    df_plot(df_jan, df_tvl1, variable="rmsvd", labels=["deepflow", "tvl1"])
    df_plot(df_jan, df_tvl1, variable="speed_bias", labels=["deepflow", "tvl1"])


if __name__ == "__main__":
    # main()
    df_mean()
