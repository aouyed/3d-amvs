# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import pandas as pd
import first_stage_amv as fsa
import quiver as q
from datetime import datetime 
import qv_grad as qg
import stats_calculators as sc
import glob
import cross_section as cs
from natsort import natsorted
from matplotlib.pyplot import cm


THRESHOLDS=(5,10,100)


def calc_days(thresh):
    file_names=natsorted(glob.glob('../data/processed/07*20.nc'))
    for file_name in file_names: 
        d={'pressure':[],'error_sum':[],'speed_sum':[],
           'denominator':[],'yield':[]}
        print(file_name)
        ds=xr.open_dataset(file_name)
        ds=ds.loc[{'satellite':'snpp'}]
        ds=cs.preprocess(ds, thresh)      
        for pressure in ds['plev'].values:
            ds_unit=ds.sel(plev=pressure, method='nearest')
            error_sum=sc.weighted_sum(ds_unit['squared_error'])
            speed_sum=sc.weighted_sum(ds_unit['speed'])
            data=ds_unit['squared_error'].values
            counts=np.count_nonzero(~np.isnan(data))

            denominator= sc.weights_sum(ds_unit['squared_error'])
            pressure=int(round(pressure))
            print(pressure)
            d['pressure'].append(pressure)
            d['error_sum'].append(error_sum)
            d['speed_sum'].append(speed_sum)
            d['denominator'].append(denominator)
            d['yield'].append(counts)
        df=pd.DataFrame(data=d)
        df.set_index('pressure', drop=True)
        df.to_csv('../data/interim/dataframes/t'+str(thresh)+'_'+file_name[18:28] + '.csv')
    
def calc_pressure(thresh):
    d={'pressure':[],'rmsvd':[],'speed':[], 'yield': []}
    file_names=natsorted(glob.glob('../data/interim/dataframes/t'+str(thresh)+'_07*20.csv'))
    print(file_names)
    df=pd.read_csv(file_names[0])
    pressures=df['pressure'].values
    df=df.set_index('pressure',drop=True)
    for pressure in pressures:
        error_sum=0
        speed_sum=0
        denominator=0
        yield_sum=0
        for file in file_names:
            df_unit=pd.read_csv(file)
            df_unit=df_unit.set_index('pressure',drop=True)
            error_sum=error_sum+df_unit.loc[pressure,'error_sum']
            speed_sum=speed_sum+df_unit.loc[pressure,'speed_sum']
            yield_sum=yield_sum+df_unit.loc[pressure,'yield']
            denominator=denominator + df_unit.loc[pressure,'denominator']
        d['pressure'].append(pressure)
        d['speed'].append(speed_sum/denominator)
        d['rmsvd'].append(np.sqrt(error_sum/denominator))
        d['yield'].append(yield_sum)

    df=pd.DataFrame(data=d)
    print(df)
    df.set_index('pressure', drop=True)
    df.to_csv('../data/processed/dataframes/rmsvd_t'+str(thresh)+'.csv')
    
        
def  plot_rmsvd(ax, df, color, thresh):
     ax.plot(df['pressure'], df['rmsvd'],  label='RMSVD, δ = '+str(thresh)+' m/s', color=color)
     ax.plot(df['pressure'], df['speed'], label='speed, δ = '+str(thresh)+' m/s',linestyle='dashed', color=color)
     ax.set_ylabel('[m/s]')

def  plot_yield(ax, df, color, thresh):
     ax.plot(df['pressure'], df['yield'],  label='δ = '+str(thresh)+' m/s', color=color)
     ax.set_ylabel('Counts')

    
def line_plotter(func, plot_name):
    fig, ax = plt.subplots()
    colors = cm.tab10(np.linspace(0, 1, len(THRESHOLDS)))
    for i, thresh in enumerate(THRESHOLDS):
        color=colors[i]
        df=pd.read_csv('../data/processed/dataframes/rmsvd_t'+str(thresh)+'.csv')
        func(ax, df, color, thresh)
    ax.legend()
 
    ax.set_xlabel("Pressure [hPa]")
    plt.savefig('../data/processed/plots/'+plot_name+'.png', bbox_inches='tight', dpi=300)

    plt.show()
    plt.close()
    
def threshold_fun():
    for thresh in THRESHOLDS:
        calc_days(thresh)
        calc_pressure(thresh)
    
def main():
    #threshold_fun()
    line_plotter(plot_rmsvd,'rmsvd')
    line_plotter(plot_yield,'yield')

    


if __name__ == '__main__':
    main()
    

