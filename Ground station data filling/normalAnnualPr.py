'''
This module calculate the Normal Annual Rainfall of
precipitation stations.
'''

import numpy as np
import pandas as pd
import warnings

from IPython.display import display

warnings.filterwarnings("ignore")

def filterSeasonWise (df,months):
    each_season = df[df['Month'].isin(months)]
    missing_count = each_season.iloc[:].isna().sum()
    missing_days = missing_count[1]
    #print(missing_count)
    return each_season,missing_days

def filterYearWise (df,year):
    each_year = df[df['Year'] == year]
    return each_year

def sumSeason (df,md, tolerance):
    if md <= tolerance:
        sum_season = pd.to_numeric(df.iloc[:,1]).sum(skipna = True)
        #print(sum_season)
    else:
        sum_season = np.NaN
    return sum_season

def normalAnnualPrecip(prefilled_data):

    normalAnnualStn = pd.DataFrame(columns=['Station', 'NormalAnnualRainfall'])
    column_count = prefilled_data.shape[1]
    station_index = list(prefilled_data.columns[1:column_count])

    winter_months = [12, 1, 2]
    premonsoon_months = [3, 4, 5]
    monsoon_months = [6, 7, 8]
    postmonsoon_months = [9, 10, 11]

    print('Calculating Normal Annual Rainfall. Please Wait!')

    for i in range(0, column_count-1):
        each_station_prefilled = pd.DataFrame(prefilled_data[['Date', station_index[i]]])
        each_station_prefilled = each_station_prefilled.dropna()
        each_station_prefilled = each_station_prefilled.replace('DNA', np.NaN)
        each_station_prefilled['Year'] = pd.DatetimeIndex(each_station_prefilled['Date']).year
        each_station_prefilled['Month'] = pd.DatetimeIndex(each_station_prefilled['Date']).month
        each_station_prefilled['Day'] = pd.DatetimeIndex(each_station_prefilled['Date']).day

        date_range = each_station_prefilled['Year'].unique()

        summary_season = pd.DataFrame(columns=['Year', 'Premonsoon', 'Monsoon', 'Postmonsoon', 'Winter'])

        for yr in range(date_range.min(), date_range.max() + 1):
            each_station_year = filterYearWise(df=each_station_prefilled, year=yr)
            premonsoon_pr, pre_md = filterSeasonWise(df=each_station_year, months=premonsoon_months)
            monsoon_pr, mon_md = filterSeasonWise(df=each_station_year, months=monsoon_months)
            postmonsoon_pr, pos_md = filterSeasonWise(df=each_station_year, months=postmonsoon_months)
            winter_pr, win_md = filterSeasonWise(df=each_station_year, months=winter_months)

            sum_mon = sumSeason(df=monsoon_pr, md=mon_md, tolerance=10)
            sum_pre = sumSeason(df=premonsoon_pr, md=pre_md, tolerance=20)
            sum_pos = sumSeason(df=postmonsoon_pr, md=pos_md, tolerance=20)
            sum_win = sumSeason(df=winter_pr, md=win_md, tolerance=40)

            #seasonal_to_append = pd.DataFrame({['Year': yr], 'Premonsoon': sum_pre, 'Monsoon': sum_mon,
                                                    #'Postmonsoon': sum_pos, 'Winter': sum_win})
            
            dict_to_append = {'Year': [yr], 'Premonsoon': [sum_pre], 'Monsoon': [sum_mon],
                                                    'Postmonsoon': [sum_pos], 'Winter': [sum_win]}
            
            summary_season = pd.concat([summary_season, pd.DataFrame(dict_to_append)],ignore_index= True)

            
            '''summary_season = summary_season.append({'Year': yr, 'Premonsoon': sum_pre, 'Monsoon': sum_mon,
                                                    'Postmonsoon': sum_pos, 'Winter': sum_win}, ignore_index=True)'''
            summary_season = summary_season.replace(0, np.NaN)
            summary_season['Sum'] = summary_season['Winter'] + summary_season['Premonsoon'] + summary_season[
                'Postmonsoon'] + summary_season['Monsoon']
            # summary_season['Sum'] = summary_season.iloc[:,1:4].sum(axis=1,skipna = False)
            normal_ann = summary_season.iloc[:, 5].mean(axis=0, skipna=True)


        annual_dict_to_append = {'Station': [station_index[i]],'NormalAnnualRainfall':[normal_ann]} 
        #annual_to_append = pd.DataFrame({'Station': station_index[i], "NormalAnnualRainfall": normal_ann})
        normalAnnualStn = pd.concat([normalAnnualStn,pd.DataFrame(annual_dict_to_append)],ignore_index= True)
        #normalAnnualStn = normalAnnualStn.append({'Station': station_index[i], "NormalAnnualRainfall": normal_ann},
                                                 #ignore_index=True)
        print(station_index[i] + 'Completed')

    return normalAnnualStn


