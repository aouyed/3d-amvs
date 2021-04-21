#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 15:21:36 2021

@author: aouyed
"""
import xarray as xr
import xesmf as xe
import numpy as np
from datetime import datetime
from datetime import timedelta

PATH='../data/raw/CLIMCAPS_winds/'
label='specific_humidity_mu'
labels=['specific_humidity_mean','specific_humidity_sdev']
def regridder(ds):
    latmax = ds['latitude'].max().item()
    latmin = ds['latitude'].min().item()
    lonmax = ds['longitude'].max().item()
    lonmin = ds['longitude'].min().item()

    new_lat = np.arange(latmin, latmax+1, 1)
    new_lon = np.arange(lonmin, lonmax+1, 1)
    
    old_lon = np.arange(lonmin, lonmax, 2)
    old_lat = np.arange(latmin, latmax+1, 0.5)
    ds=ds.rename({'Lon':'lat','Lat':'lon'})
    ds['lat']=ds['lat']/2+latmin
    ds['lat']=ds['lat'].astype(np.float32)
    ds['lon']=2*ds['lon']+lonmin
    ds['lon']=ds['lon'].astype(np.float32)
    print(ds)

    ds_out = xr.Dataset(
           {'lat': (['lat'], new_lat), 'lon': ('lon', new_lon)})
   # regridder = xe.Regridder(ds[['lat','lon']], ds_out, 'bilinear', reuse_weights=True)
    ds_t=ds[labels].transpose('plev','lat','lon')
    #ds_r = regridder(ds_t[labels])
    #ds_r['pressure']=(['plev'],ds['pressure'].values)
   #ds_r['obs_time']=(['plev'],ds['pressure'].values)
    return ds

def ds_unit_calc(day,time,satellite):
    day_string=day.strftime("%Y%m%d")
    print(day_string)
    d0=datetime(1993, 1, 1)   
    
    ds=xr.open_dataset(PATH+ 'climcaps_'+ day_string+'_'+time+'_'+satellite+'_gridded_specific_humidity_1deg_noqc.nc')
    
    #ds=regridder(ds)   
    
    df=ds.to_dataframe()
    df=df.reset_index()
    df=df.set_index(['latitude','longitude','plev'])
    ds=xr.Dataset.from_dataframe(df)   
    ds=ds.reindex(latitude=list(reversed(ds.latitude)))
    ds['plev']=np.around(np.sort(np.unique(ds['pressure'].values)),decimals=1)
    ds=ds.drop('Lat')
    ds=ds.drop('Lon')
    ds=ds.drop('pressure')
    dts=ds['obs_time'].values
    mask=np.isnan(dts)
    dts=np.nan_to_num(dts)
    helper = np.vectorize(lambda x: d0 + timedelta(seconds=x))
    dt_sec=helper(dts)
    dt_sec[mask]=np.nan
    ds['obs_time']=(['latitude','longitude','plev'],dt_sec)
    
    #ds=ds.rename({'Lat':'lat','Lon':'lon','plev':'pressure'})
    ds = ds.expand_dims('day').assign_coords(day=np.array([day]))
    ds = ds.expand_dims('time').assign_coords(time=np.array([time]))
    ds = ds.expand_dims('satellite').assign_coords(satellite=np.array([satellite]))
    
    return ds


def satellite_loop(satellites,day,time):
    ds_total=xr.Dataset()
    for satellite in satellites:  
        ds_unit=ds_unit_calc(day, time, satellite)
        if not ds_total:
            ds_total = ds_unit
        else:       
            ds_total = xr.concat([ds_total, ds_unit], 'satellite')
    return ds_total

def time_loop(times, satellites, day):
    ds_total=xr.Dataset()
    for time in times:
        ds_unit=satellite_loop(satellites,day,time)
        if not ds_total:
            ds_total = ds_unit
        else:       
            ds_total = xr.concat([ds_total, ds_unit], 'time')
    return ds_total
        
def main():
    times=['am','pm']
    satellites=['j1','snpp']
    days=[datetime(2020,1,1),datetime(2020,1,2),
    datetime(2020,7,1),datetime(2020,7,3)]

    ds_total=xr.Dataset() 
    for day in days:    
        print(day)
        ds_unit=time_loop(times, satellites, day)
        if not ds_total:
            ds_total = ds_unit
        else:       
            ds_total = xr.concat([ds_total, ds_unit], 'day')
    print(ds_total)
    #ds_total=ds_total.transpose()
    ds_total.to_netcdf('../data/processed/real_water_vapor_noqc.nc')
 
    
if __name__=="__main__":
    main()
    
    
    