from datetime import datetime
import pandas as pd
import xarray as xr
from datetime import timedelta
import numpy as np
import igra
import time
from tqdm import tqdm
import os.path
import config as c
import amv_calculators as ac
from siphon.simplewebservice.igra2 import IGRAUpperAir
from parameters import parameters
import pickle

PATH = "../data/interim/rs_dataframes/"

HOURS = 1.5
import pickle as pkl


def daterange(start_date, end_date, dhour):
    date_list = []
    delta = timedelta(hours=dhour)
    while start_date <= end_date:
        date_list.append(start_date)
        start_date += delta
    return date_list


def preprocess(ds):
    ds = ds.drop(["day", "satellite", "time", "flowx", "flowy"])
    ds["u_error"] = ds["u"] - ds["u_era5"]
    ds["v_error"] = ds["v"] - ds["v_era5"]
    ds["error_mag"] = np.sqrt(ds["u_error"] ** 2 + ds["v_error"] ** 2)
    return ds


def space_time_collocator(days, deltat, param):
    df = pd.DataFrame()
    for day in days:
        print(day)
        for time in ("am", "pm"):
            dsdate = day.strftime("%m_%d_%Y")
            ds = xr.open_dataset("../data/processed/" + param.tag + ".nc")
            ds = ds.sel(satellite="snpp", day=day, time=time)

            # ds = xr.open_dataset('../data/processed/'+param.tag+'_'+ dsdate+'_'+time+'.nc')
            # ds=ds.sel(satellite='snpp')
            df_unit = ds[["obs_time", "u"]].to_dataframe()
            df_unit = df_unit.reset_index()
            df_unit = df_unit[["latitude", "longitude", "obs_time", "u", "time"]]
            first_rao = datetime(day.year, day.month, day.day, 0)
            second_rao = datetime(day.year, day.month, day.day, 12)
            condition1 = df_unit["obs_time"].between(
                first_rao - deltat, first_rao + deltat
            )
            condition2 = df_unit["obs_time"].between(
                second_rao - deltat, second_rao + deltat
            )
            df_unit = df_unit.loc[condition1 | condition2]
            df_unit = df_unit.dropna()
            df_unit = df_unit[["latitude", "longitude", "obs_time", "time"]]
            df_unit = df_unit.drop_duplicates()

            if df.empty:
                df = df_unit
            else:
                df = df.append(df_unit)
    df = df.reset_index(drop=True)
    df = df.drop_duplicates()
    return df


def collocate_igra(stations, lat, lon, param):

    condition1 = stations["lat"].between(lat - param.coll_dx, lat + param.coll_dx)
    condition2 = stations["lon"].between(lon - param.coll_dx, lon + param.coll_dx)
    condition3 = condition1 & condition2
    condition4 = stations["end"] >= 2020
    stations = stations.loc[condition3 & condition4]
    return stations


def collocated_igra_ids(df, param):
    df = df.reset_index(drop=True)
    start_time = time.time()
    stations = igra.download.stationlist("/tmp")

    station_dict = {
        "lat": [],
        "lon": [],
        "lon_rs": [],
        "lat_rs": [],
        "stationid": [],
        "obs_time": [],
        "orbit": [],
    }
    for latlon in tqdm(df.values):
        lat, lon, obs_time, orbit = latlon
        df_unit = collocate_igra(stations, lat, lon, param)
        if not df_unit.empty:

            ids = df_unit.index.values.tolist()
            station_dict["lat"].append(lat)
            station_dict["lon"].append(lon)
            station_dict["lat_rs"].append(df_unit["lat"].values[0])
            station_dict["lon_rs"].append(df_unit["lon"].values[0])
            station_dict["stationid"].append(ids[0])
            station_dict["obs_time"].append(obs_time)
            station_dict["orbit"].append(orbit)

    output_df = pd.DataFrame(data=station_dict)
    print("--- %s seconds ---" % (time.time() - start_time))
    print(output_df)
    return output_df


def igra_downloader(df, days, month_string):
    dud_fname = PATH + month_string + "_duds.pkl"
    if os.path.isfile(dud_fname):
        with open(dud_fname, "rb") as handle:
            print("loading pickle")
            dud_database = pickle.load(handle)
    else:
        dud_database = {"date": [np.nan], "stationid": [np.nan]}

    station_list = np.unique(df["stationid"].values)
    for station in tqdm(station_list):

        fname = PATH + month_string + "_" + station + ".pkl"
        if not os.path.isfile(fname):
            df_total = pd.DataFrame()

            for day in days:

                first_rao = datetime(day.year, day.month, day.day, 0)
                second_rao = datetime(day.year, day.month, day.day, 12)
                for date in (first_rao, second_rao):
                    tic = time.process_time()
                    df_dud = pd.DataFrame(data=dud_database)
                    dud_is = (
                        df_dud.loc[
                            (df_dud["date"] == date) & (df_dud["stationid"] == station)
                        ]
                        .any()
                        .all()
                    )
                    if not dud_is:
                        try:
                            df_unit, header = IGRAUpperAir.request_data(date, station)
                            df_unit["date"] = date
                            df_unit["stationid"] = station

                            if df_total.empty:
                                df_total = df_unit
                            else:
                                df_total = df_total.append(df_unit)
                            print("succesful retrieval")

                        except ValueError as ve:
                            print(ve)
                            print("value error")
                            dud_database["date"].append(date)
                            dud_database["stationid"].append(station)
                            with open(dud_fname, "wb") as handle:
                                pickle.dump(
                                    dud_database,
                                    handle,
                                    protocol=pickle.HIGHEST_PROTOCOL,
                                )

                        except Exception as e:
                            print(e)

                            pass

            if not df_total.empty:
                df_total.to_pickle(
                    "../data/interim/rs_dataframes/"
                    + month_string
                    + "_"
                    + station
                    + ".pkl"
                )


def main(param):
    deltat = timedelta(hours=param.coll_dt)
    start_date = param.month
    days = param.dates
    month_string = param.month_string
    df = space_time_collocator(days, deltat, param)
    df = df.reset_index(drop=True)
    df = df.drop_duplicates()
    df = collocated_igra_ids(df, param)
    df.to_pickle("../data/interim/dataframes/" + param.tag + "_igra_id.pkl")
    df = pd.read_pickle("../data/interim/dataframes/" + param.tag + "_igra_id.pkl")
    print(df)
    igra_downloader(df, days, month_string)


if __name__ == "__main__":
    param = parameters()
    param.set_month(datetime(2020, 1, 1))
    param.set_Lambda(0.3)
    main(param)
