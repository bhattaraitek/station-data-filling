'''
This program fill the missing data in precipitation
time series using Normal Ratio Method.
Please format the data according to the sample dataset
provided with this project file.

Author: tek  Date: 2022 May 15
'''
import numpy as np
import pandas as pd
import warnings
import normalAnnualPr as nap
import selectFillStation as sfs
import FillingMethods as fm

from IPython.display import display

warnings.filterwarnings("ignore")

#prefilled_pr = pd.DataFrame(pd.read_csv('PrefilledData.csv'))
#prefilled_temp = pd.DataFrame(pd.read_csv('Prefilled-Temperature_Data.csv'))
#stations_info = pd.DataFrame(pd.read_excel('StationsInfo.xlsx'))

def FillingNormalRatio(prefilled_data, stations_info):
    normal_rainfall = nap.normalAnnualPrecip(prefilled_data)
    filling_stations = sfs.fillStationSelect(stations_info,normal_rainfall)
    filled_pr = fm.NormalRatioMethod(prefilled_data,normal_rainfall,filling_stations)
    return filled_pr

    #filled_pr.to_csv("Filled Rainfall Data_GUI.csv", index=False)

def FillingLongtermAverage(prefilled_data):
    filled_temp = fm.LongTermAvgMethod(prefilled_data)
    return filled_temp

#sFillingNormalRatio(prefilled_data= prefilled_pr, stations_info= stations_info)



