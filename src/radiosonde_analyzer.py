#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 12:46:41 2022

@author: aouyed
"""

import radiosonde_plotter as rp
import pandas as pd
from parameters import parameters
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
from tqdm import tqdm


def compute(ds):
    ds["speed"] = np.sqrt(ds.u**2 + ds.v**2)
    ds["speed_era5"] = np.sqrt(ds.u_era5**2 + ds.v_era5**2)
    ds["speed_diff"] = ds.speed - ds.speed_era5
    ds["u_error"] = ds["u"] - ds["u_era5"]
    ds["v_error"] = ds["v"] - ds["v_era5"]
    ds["error_mag"] = np.sqrt(ds["u_error"] ** 2 + ds["v_error"] ** 2)
    ds["error_square"] = ds["u_error"] ** 2 + ds["v_error"] ** 2
    return ds


def plot(df):
    fig, axes = plt.subplots(nrows=2, ncols=1)
    axlist = axes.flat
    axlist[0].plot(df["lambda"], df["rmsvd"], label="rmsvd")
    axlist[0].plot(df["lambda"], df["rmsvd_era5"], label="rmsvd_era5")
    axlist[0].set_ylabel("m/s")
    axlist[0].set_xlabel("lambda")
    axlist[1].plot(df["lambda"], df["speed_bias"], label="speed_bias")
    axlist[1].plot(
        df["lambda"], df["speed_bias_era5"], label="speed_bias_era5", c="orange"
    )

    axlist[0].legend()
    axlist[1].legend()

    fig.tight_layout()
    plt.savefig("../data/processed/plots/lambda_test.png", dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()


def rs_plots():

    param = parameters()
    df_jan = pd.read_pickle(
        "../data/processed/dataframes/"
        + param.month_string
        + "_winds_rs_model_"
        + param.tag
        + ".pkl"
    )
    breakpoint()
    means = {
        "lambda": [],
        "rmsvd": [],
        "speed_bias": [],
        "speed_bias_era5": [],
        "rmsvd_era5": [],
    }
    for Lambda in tqdm((0.15, 0.25, 0.2725, 0.3, 0.325, 0.45, 0.6, 1)):
        param.set_Lambda(Lambda)
        file = "../data/processed/" + param.tag + ".nc"
        ds = xr.open_dataset(file)
        ds = compute(ds)
        means["speed_bias_era5"].append(ds["speed_diff"].mean().item())
        rmsvd_era5 = np.sqrt(ds["error_square"].mean().item())
        means["rmsvd_era5"].append(rmsvd_era5)

        df = pd.read_csv("../data/processed/df_pressure_" + param.tag + ".csv")
        means["lambda"].append(Lambda)
        means["rmsvd"].append(df["rmsvd"].mean())
        means["speed_bias"].append(df["speed_bias"].mean())

    df_total = pd.DataFrame(data=means)
    plot(df_total)


def main():
    rs_plots()


if __name__ == "__main__":
    main()
