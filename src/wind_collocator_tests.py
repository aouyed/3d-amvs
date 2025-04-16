from datetime import datetime
import pandas as pd
import xarray as xr
from datetime import timedelta
import numpy as np


def collocated_pressure_list(df, plevs):
    df_total = pd.DataFrame()
    for plev in plevs:
        df_unit = df.iloc[(df["pressure"] - plev).abs().argsort()[:1]]
        df_unit = df_unit.reset_index(drop=True)
        df_unit["plev"] = plev

        if df_total.empty:
            df_total = df_unit
        else:
            df_total = df_total.append(df_unit)

    return df_total.reset_index(drop=True)


def ds_test(tag, orbit, obs_time, df_rs, lat, lon):
    ds_path_total = "../data/processed/" + tag + ".nc"
    ds_path = (
        obs_time.strftime("../data/processed/" + tag + "_%m_%d_%Y")
        + "_"
        + orbit
        + ".nc"
    )
    obs_time = obs_time.replace(hour=0, minute=0, second=0)
    dsdate = obs_time.strftime("%m_%d_%Y")
    ds = xr.open_dataset(ds_path)
    ds = ds.sel(time=orbit)
    # ds=ds.sel(day=obs_time, method='nearest')
    ds = ds.sel(satellite="snpp")
    ds = ds.squeeze()

    ds_total = xr.open_dataset(ds_path_total)
    ds_total = ds_total.sel(time=orbit)
    ds_total = ds_total.sel(day=obs_time, method="nearest")
    ds_total = ds_total.sel(satellite="snpp")

    a1 = ds[["u", "v"]].values
    a2 = ds_total[["u", "v"]].values
    np.testing.assert_array_equal(a1, a2)
    df_rs1 = collocated_pressure_list(df_rs, ds["plev"].values)
    df_rs2 = collocated_pressure_list(df_rs, ds_total["plev"].values)

    ds1 = ds.sel(
        latitude=lat, longitude=lon, plev=df_rs["plev"].values, method="nearest"
    )
    ds2 = ds_total.sel(
        latitude=lat, longitude=lon, plev=df_rs["plev"].values, method="nearest"
    )
    breakpoint()
    return ds_total
