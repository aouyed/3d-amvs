from datetime import datetime 

MONTH=datetime(2020,1,1)
month_string=MONTH.strftime("%B").lower()
QC='noqc'
THRESHOLDS=[10,4,100]
GEODESICS={'swath':[(-47.5, -60), (45, -30),'latitude'],
                'equator':[(6.5, -149.5),(6.5, 4.5),'longitude']}
PRESSURES=[850, 700, 500, 400]