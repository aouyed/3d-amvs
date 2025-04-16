#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 14:57:31 2022

@author: aouyed
"""


from siphon.simplewebservice.igra2 import IGRAUpperAir
import time
import datetime

tic = time.clock()


# station='AUM00011010'
# date=datetime.datetime(2020,1,1)

date = datetime.datetime(2020, 1, 1)
station = "USM00070026"

try:
    df_unit, header = IGRAUpperAir.request_data(date, station)
    print("passes")
except Exception as e:
    print(e)

toc = time.clock()

delta = toc - tic

print(delta)
