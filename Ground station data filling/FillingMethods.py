from cmath import nan
import numpy as np
import pandas as pd
import warnings
from datetime import datetime, date
warnings.filterwarnings("ignore")

#prefilled_data = pd.DataFrame(pd.read_csv('PrefilledData.csv'))
#stations_info = pd.DataFrame(pd.read_excel('StationsInfo.xlsx'))
#normal_rainfall = pd.DataFrame(pd.read_csv('NormalAnnualRainfall.csv'))
#filling_stations = pd.DataFrame(pd.read_csv('selected stations.csv'))

def LongTermDailyAvg(prefilled_data):
    #row_count = stations_info.shape[0]
    station_index = list(prefilled_data.columns)
    station_index.remove('Date')
    number_of_stations = len(station_index)
    ltavg_day_all = pd.DataFrame({'DOY': range(1,367) })
    for one_stn in range(0, number_of_stations):

        one_stn_prefilled = prefilled_data[['Date', station_index[one_stn]]]
        one_stn_prefilled = one_stn_prefilled.dropna()
        one_stn_prefilled = one_stn_prefilled.replace('DNA', np.NAN)
        one_stn_prefilled['doy'] = pd.to_datetime(one_stn_prefilled['Date']).dt.dayofyear

        one_stn_prefilled = one_stn_prefilled.drop(columns= 'Date')
        one_stn_prefilled = one_stn_prefilled.dropna()
        one_stn_prefilled[station_index[one_stn]] = pd.to_numeric(one_stn_prefilled[station_index[one_stn]])
        
        ltavg_day = one_stn_prefilled.groupby('doy').mean()
        ltavg_day['DOY'] = ltavg_day.index
        ltavg_day = ltavg_day[['DOY',station_index[one_stn]]]
        ltavg_day_all = pd.merge(left=ltavg_day_all,right=ltavg_day,left_on='DOY',right_on='DOY',how='outer')
        ltavg_day_all.set_index('DOY',inplace=True)
        print('Longterm Daily Average:'+" "+ station_index[one_stn])

    return ltavg_day_all


def NormalRatioMethod(prefilled_data, normal_rainfall, filling_stations):

    dict_nr = normal_rainfall.set_index('Station').T.to_dict()
    station_index = list(prefilled_data.columns)
    station_index.remove('Date')
    number_of_stations = len(station_index)
    filled_data = pd.DataFrame(
        {'Date': pd.date_range(start = min(prefilled_data['Date']), end = max(prefilled_data['Date']))})

    ltavg_daily = LongTermDailyAvg(prefilled_data)
    print('Long term daily average calculated!')
    print('Filling Started...Please Wait...')
    for one_stn in range(0, number_of_stations):

        one_stn_prefilled = prefilled_data[['Date', station_index[one_stn]]]
        one_stn_prefilled = one_stn_prefilled.dropna()
        one_stn_prefilled = one_stn_prefilled.replace('DNA', np.NAN)
        filler_list = list(filling_stations[station_index[one_stn]])
        filler_list.insert(0, 'Date')

        to_be_filled = one_stn_prefilled[one_stn_prefilled[station_index[one_stn]].isnull()]

        remaining_data = one_stn_prefilled.dropna()
        remaining_data = remaining_data[['Date', station_index[one_stn]]]

        others_for_filling = prefilled_data[filler_list].replace('DNA', np.NaN)

        merged_temp = pd.merge(
            left=to_be_filled, right=others_for_filling, left_on="Date", right_on="Date")

        merged_temp['DOY'] = pd.to_datetime(merged_temp['Date']).dt.dayofyear

        merged_temp.reset_index(drop=True,inplace=True)

        for i in range(0, merged_temp.shape[0]):
            total = 0.00
            stn_count = 0

            for j in range(1, len(filler_list)):
                if pd.isna(merged_temp[filler_list[j]][i]):
                    continue
                else:
                    sum = float(merged_temp[filler_list[j]][i]) * (float(dict_nr[station_index[one_stn]]
                                                                        ["NormalAnnualRainfall"])/float(dict_nr[filler_list[j]]['NormalAnnualRainfall']))
                    stn_count = stn_count + 1
                    total = total + sum

            if stn_count > 1: 
                merged_temp[station_index[one_stn]][i] = total/stn_count
            else:
                doy = merged_temp['DOY'][i]
                merged_temp[station_index[one_stn]][i] = ltavg_daily[station_index[one_stn]][doy]

        merged_temp = merged_temp[['Date', station_index[one_stn]]]

        filled_temp = pd.concat([remaining_data, merged_temp])
        filled_temp['Date'] = pd.to_datetime(filled_temp['Date'])
        filled_temp = filled_temp.sort_values(by="Date")
        filled_temp.fillna('DNA')

        filled_data = pd.merge(left=filled_data, right=filled_temp,
                            left_on='Date', right_on='Date', how='outer')
        print(station_index[one_stn]+" "+'Filled')
    return filled_data


def LongTermAvgMethod(prefilled_data):

    station_index = list(prefilled_data.columns)
    station_index.remove('Date')
    number_of_stations = len(station_index)
    filled_data = pd.DataFrame(
        {'Date': pd.date_range(start = min(prefilled_data['Date']), end = max(prefilled_data['Date']))})

    ltavg_daily = LongTermDailyAvg(prefilled_data)

    for one_stn in range(0, number_of_stations):

        one_stn_prefilled = prefilled_data[['Date', station_index[one_stn]]]
        one_stn_prefilled = one_stn_prefilled.dropna()
        one_stn_prefilled = one_stn_prefilled.replace('DNA', np.NAN)

        to_be_filled = one_stn_prefilled[one_stn_prefilled[station_index[one_stn]].isnull()]

        remaining_data = one_stn_prefilled.dropna()
        remaining_data = remaining_data[['Date', station_index[one_stn]]]

        to_be_filled['DOY'] = pd.to_datetime(to_be_filled['Date']).dt.dayofyear
        to_be_filled.reset_index(drop = True, inplace = True)

        for i in range(0, to_be_filled.shape[0]):
            doy = to_be_filled['DOY'][i]
            to_be_filled[station_index[one_stn]][i] = ltavg_daily[station_index[one_stn]][doy]
        
        to_be_filled = to_be_filled[['Date', station_index[one_stn]]]
        filled_temp = pd.concat([remaining_data, to_be_filled])
        filled_temp['Date'] = pd.to_datetime(filled_temp['Date'])
        filled_temp = filled_temp.sort_values(by="Date")
        filled_temp.fillna('DNA')

        filled_data = pd.merge(left=filled_data, right=filled_temp,
                                left_on='Date', right_on='Date', how='outer')

        print(station_index[one_stn]+" "+'Filled')

    return filled_data



