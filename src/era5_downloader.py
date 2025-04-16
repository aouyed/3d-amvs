import cdsapi
import pandas as pd
import amv_calculators as ac
from datetime import datetime
from datetime import timedelta
import xarray as xr
import config as c
import main as fsa


def downloader(date):

    date = pd.to_datetime(str(date))
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")

    c = cdsapi.Client()

    c.retrieve(
        "reanalysis-era5-pressure-levels",
        {
            "product_type": "reanalysis",
            "format": "netcdf",
            "variable": [
                "u_component_of_wind",
                "v_component_of_wind",
                "divergence",
                "vorticity",
            ],
            "pressure_level": [
                "1",
                "2",
                "3",
                "5",
                "7",
                "10",
                "20",
                "30",
                "50",
                "70",
                "100",
                "125",
                "150",
                "175",
                "200",
                "225",
                "250",
                "300",
                "350",
                "400",
                "450",
                "500",
                "550",
                "600",
                "650",
                "700",
                "750",
                "775",
                "800",
                "825",
                "850",
                "875",
                "900",
                "925",
                "950",
                "975",
                "1000",
            ],
            "year": year,
            "month": month,
            "day": day,
            "time": [
                "00:00",
                "01:00",
                "02:00",
                "03:00",
                "04:00",
                "05:00",
                "06:00",
                "07:00",
                "08:00",
                "09:00",
                "10:00",
                "11:00",
                "12:00",
                "13:00",
                "14:00",
                "15:00",
                "16:00",
                "17:00",
                "18:00",
                "19:00",
                "20:00",
                "21:00",
                "22:00",
                "23:00",
            ],
        },
        "../data/interim/model_" + month + "_" + day + "_" + year + ".nc",
    )


def loader():
    date_list = rc.daterange(datetime(2020, 7, 1), datetime(2020, 7, 7), 24)
    for date in date_list:
        downloader(date)


def main():
    start_date = c.MONTH
    end_date = c.MONTH + timedelta(days=6)
    days = ac.daterange(start_date, end_date, 24)
    for date in [days[0]]:
        downloader(date)
        print(date)
        year = date.strftime("%Y")
        month = date.strftime("%m")
        day = date.strftime("%d")
        # ds=xr.open_dataset('../data/interim/model_'+month+'_'+day+'_'+year+'.nc')
        # ds=ds[['u','v']].coarsen(latitude=4, longitude=4, boundary='trim').mean()
        print(ds)
        # ds.to_netcdf('../data/interim/fine_model_'+month+'_'+day+'_'+year+'.nc')
        # fsa.model_closer(date)


if __name__ == "__main__":
    main()
