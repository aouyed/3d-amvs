#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 15:17:31 2021

@author: aouyed
"""
import cv2
import xarray as xr
import numpy as np
import metpy.calc as mpcalc
from metpy.units import units
import inpainter 
import amv_calculators as calc
import quiver
import plotter
ALG='tvl1'


R = 6371000

drad = np.deg2rad(1)
dx = R*drad
scale_x = dx
dy = R*drad
scale_y = dy


LABEL='specific_humidity_mean'


    
def ds_unit_calc(ds, day,pressure, time):
    ds=ds.loc[{'day':day ,'plev':pressure,'time':time}]
    ds=ds.drop(['day','plev','time'])
    ds=calc.prepare_ds(ds)
    ds_model=xr.open_dataset('../data/raw/reanalysis/07_03_20.nc')
    ds_model=ds_model.sel(level=pressure, method='nearest')
    ds_model=ds_model.drop('level')
    ds_model = ds_model.assign_coords(longitude=(((ds_model.longitude + 180) % 360) - 180))
    ds_model=ds_model.reindex(longitude=np.sort(ds_model['longitude'].values))
    
    df=ds.to_dataframe()
    swathes=calc.swath_initializer(ds,5)
  
    for swath in swathes:
        print(time)
        ds_snpp=ds.loc[{'satellite':'snpp'}]
        ds_j1=ds.loc[{'satellite':'j1'}]
        start=swath[0]
        end=swath[1]
        print(start)
        ds_merged, ds_snpp, ds_j1, df_snpp=calc.prepare_patch(ds_snpp, ds_j1, ds_model, start, end)
   
        if (df_snpp.shape[0]>100):
            condition2=(ds_snpp['longitude'].max()-ds_snpp['longitude'].min())<50
                      
            df, ds_snpp_p,ds_j1_p, ds_model_p=calc.amv_calculator(ds_merged, df)
            ds_model_p1=ds_model_p[['u','v']].loc[{'satellite':'j1'}].drop('satellite')
            ds_model_p_test=ds_model_p[['u','v']].loc[{'satellite':'snpp'}].drop('satellite')
           
            print(ds_snpp_p)
            quiver.quiver_plot(ds_j1_p,'j1_'+str(start),'u','v')
            quiver.quiver_plot(ds_snpp_p,'snpp_'+str(start),'u','v')
            quiver.quiver_plot(ds_model_p1,'model_'+str(start),'u','v')
            plotter.map_plotter(ds_j1_p,'j1_'+str(start),LABEL)
            plotter.map_plotter(ds_snpp_p,'snpp_'+str(start),LABEL)
      

            
    ds=xr.Dataset.from_dataframe(df)
   
    return ds   
        
def main():
    ds=xr.open_dataset('../data/processed/real_water_vapor_noqc.nc')
   
    print(ds)
    ds_total=xr.Dataset()
    for day in [ds['day'].values[3]]:
        print(day)
        ds_unit=xr.Dataset()
        for pressure in [ds['plev'].values[41]]:
            ds_unit1=xr.Dataset()
            for time in ds['time'].values:        
                ds_unit0=ds_unit_calc(ds, day,pressure, time)
                ds_unit0 = ds_unit0.expand_dims('day').assign_coords(day=np.array([day]))
                ds_unit0 = ds_unit0.expand_dims('time').assign_coords(time=np.array([time]))
                ds_unit0 = ds_unit0.expand_dims('plev').assign_coords(plev=np.array([pressure]))
                
                if not ds_unit1:
                    ds_unit1=ds_unit0
                else:
                    ds_unit1=xr.concat([ds_unit1,ds_unit0],'time')
            if not ds_unit:
                ds_unit=ds_unit1
            else:
                ds_unit=xr.concat([ds_unit,ds_unit1], 'plev') 
        if not ds_total:
            ds_total=ds_unit
        else:
            ds_total=xr.concat([ds_total,ds_unit], 'day')
    print(ds_total)
        
        
    ds_total.to_netcdf('../data/processed/real_water_vapor_noqc_test2_'+ALG+'.nc')

if __name__ == '__main__':
    main()
