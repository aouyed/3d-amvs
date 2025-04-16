from datetime import datetime
import pandas as pd
import xarray as xr
from datetime import timedelta
import numpy as np


def ds_test(tag, orbit, obs_time):
    ds_path_total = "../data/processed/" + tag + ".nc"
    ds_path = (
        obs_time.strftime("../data/processed/" + tag + "_%m_%d_%Y")
        + "_"
        + orbit
        + ".nc"
    )

    dsdate = obs_time.strftime("%m_%d_%Y")
    ds = xr.open_dataset(ds_path)
    ds = ds.sel(time=orbit)
    # ds=ds.sel(day=obs_time, method='nearest')
    ds = ds.sel(satellite="snpp")
    ds = ds.squeeze()

    ds_total = xr.open_dataset(ds_path_unit)
    ds_total = ds_total.sel(time=orbit)
    ds_total = ds_total.sel(day=obs_time, method="nearest")
    ds_total = ds_total.sel(satellite="snpp")

    a1 = ds[["u", "v"]].values
    a2 = ds_total[["u", "v"]].values
    np.testing.assert_array_equal(a1, a2)
