"""
Created on Tue May 17 11:14:22 2022

@author: aouyed
"""

import datetime
import pandas as pd


class parameters:

    def __init__(self):
        self.tag = None
        self.dates = None
        self.alg = "tvl1"
        self.coll_dt = 1.5
        self.coll_dx = 1
        self.timedelta = 6
        self.Lambda = 0.15
        self.plev_coarse = 5
        self.thresh = 10
        self.month = datetime.datetime(2020, 1, 1)
        self.month_string = self.month.strftime("%B").lower()
        self.geodesics = {
            "swath": [(-35.4, 28.75), (49.74, 66.13), "latitude"],
            "equator": [(-36.5, -127.7), (55.5, -95.5), "latitude"],
        }
        self.pressures = [850, 700, 500, 400]
        self.set_tag(
            self.plev_coarse,
            self.thresh,
            self.month_string,
            self.alg,
            self.timedelta,
            self.Lambda,
        )
        self.set_date_list(self.month, self.timedelta)

    def set_date_list(self, month, timedelta):
        start = month
        end = start + datetime.timedelta(days=timedelta)
        self.dates = pd.date_range(start=start, end=end, freq="d")

    def set_plev_coarse(self, n_layers):
        self.plev_coarse = n_layers
        self.set_tag(
            self.plev_coarse,
            self.thresh,
            self.month_string,
            self.alg,
            self.timedelta,
            self.Lambda,
        )

    def set_thresh(self, thresh):
        self.thresh = thresh
        self.set_tag(
            self.plev_coarse,
            self.thresh,
            self.month_string,
            self.alg,
            self.timedelta,
            self.Lambda,
        )

    def set_tag(self, plev_coarse, thresh, month_string, alg, timedelta, Lambda):
        self.tag = (
            alg
            + "_coarse_"
            + month_string
            + "_"
            + str(plev_coarse)
            + "_t"
            + str(thresh)
            + "_tdelta_"
            + str(timedelta)
            + "_Lambda_"
            + str(Lambda)
        )

    def set_month(self, date):
        self.month = date
        self.month_string = self.month.strftime("%B").lower()
        self.set_date_list(self.month, self.timedelta)

        self.set_tag(
            self.plev_coarse,
            self.thresh,
            self.month_string,
            self.alg,
            self.timedelta,
            self.Lambda,
        )

    def set_alg(self, alg):
        self.alg = alg
        self.set_tag(
            self.plev_coarse,
            self.thresh,
            self.month_string,
            self.alg,
            self.timedelta,
            self.Lambda,
        )

    def set_Lambda(self, Lambda):
        self.Lambda = Lambda
        self.set_tag(
            self.plev_coarse,
            self.thresh,
            self.month_string,
            self.alg,
            self.timedelta,
            self.Lambda,
        )

    def set_timedelta(self, timedelta):
        self.timedelta = timedelta
        self.set_date_list(self.month, self.timedelta)
        self.set_tag(
            self.plev_coarse,
            self.thresh,
            self.month_string,
            self.alg,
            self.timedelta,
            self.Lambda,
        )
