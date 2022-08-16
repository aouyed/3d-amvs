#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 11 16:56:44 2022

@author: aouyed
"""

import wind_collocator as wc
import igra_collocator as ic
import vertical_coarsening as vc
from parameters import parameters
from datetime import datetime 
import concatenator 
import main 
import radiosonde_plotter as rp

param= parameters()
param.set_alg('deepflow')
param.set_plev_coarse(5)
param.set_timedelta(1)
for Lambda in [0.313]:
    param.set_Lambda(Lambda)
    for month in [1]:
        param.set_month(datetime(2020,month,1))
        #main.main(param)
        for thresh in [10]:
            param.set_thresh(thresh)
            vc.main(param)
            concatenator.main(param)
            ic.main(param)
            wc.main(param)
            rp.main(param)
