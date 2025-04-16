from datetime import datetime

# MONTH=datetime(2020,7,1)
MONTH = datetime(2020, 1, 1)
month_string = MONTH.strftime("%B").lower()
QC = "noqc"
THRESHOLDS = [100]
# GEODESICS={'swath':[(-47.5, -60), (45, -30),'latitude'],
# 'equator':[(6.5, -149.5),(6.5, 4.5),'longitude']}
# GEODESICS={'swath':[(-50, -130), (46, -91),'latitude'],
#          'equator':[(6.5, -149.5),(6.5, 4.5),'longitude']}

# GEODESICS={'swath':[(-35.4, 28.75), (49.74, 66.13),'latitude'],
#          'equator':[(-36.5, -127.7),(55.5, -95.5),'latitude']}
GEODESICS = {
    "swath": [(-52.4, -127.6), (46.3, -89.4), "latitude"],
    "equator": [(-36.5, -127.7), (55.5, -95.5), "latitude"],
}
PRESSURES = [850, 700, 500, 400]
# TAG='full_thick_plev_tlv1'
TAG = "filtered_thick_plev_tlv1"
# TAG='filtered_4_thick_plev_tlv1'

# TAG='full_nn_tlv1'
