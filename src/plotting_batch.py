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
import cross_section as cc
import stats_pressurer as sp

param = parameters()
param.set_alg("tvl1")
param.set_timedelta(6)
# param.coll_dt=2
# param.coll_dx=3

param.coll_dt = 1.5
param.coll_dx = 1

for date in (datetime(2020, 7, 1), datetime(2020, 1, 1)):
    param.set_month(date)
    # ic.main(param)
    wc.main(param)
    rp.main(param)
    cc.main(param)
    # sp.main(param)
