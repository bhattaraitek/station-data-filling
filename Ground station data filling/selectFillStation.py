import numpy as np
import pandas as pd
from math import sin, cos, sqrt, atan2, radians
import warnings
#import normalAnnualPr as nap

from IPython.display import display

warnings.filterwarnings("ignore")
#stations_info = pd.DataFrame(pd.read_excel('StationsInfo.xlsx'))

#normal_rainfall = pd.DataFrame(pd.read_csv('NormalAnnualRainfall.csv'))

#normal_rainfall.index = normal_rainfall['Station']

#normal_rainfall = normal_rainfall.drop('Station',1)


def geoDistance(lat1, long1, lat2, long2):  # Haversine formula
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    long1 = radians(long1)
    lat2 = radians(lat2)
    long2 = radians(long2)

    dlong = long2 - long1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlong / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

def distBetStations(stations_info):
    # prefilled_data = pd.DataFrame(pd.read_csv('PrefilledData.csv'))

    # normal_rainfall = nap.normalAnnualPrecip(prefilled_data)

    # stations_info = pd.merge(stations_info, normal_rainfall, how='left', on=['Station'])

    dict_stations_info = stations_info.set_index('Station').T.to_dict()

    row_count = stations_info.shape[0]
    station_index = list(stations_info['Station'])

    distanceSummary = pd.DataFrame(columns=station_index)


    for one_stn in range(0, row_count):
        dist_one = []
        for other_stn in range(0, row_count):
            distance = geoDistance(dict_stations_info[station_index[one_stn]]['Lat'],
                                   dict_stations_info[station_index[one_stn]]['Long'],
                                   dict_stations_info[station_index[other_stn]]['Lat'],
                                   dict_stations_info[station_index[other_stn]]['Long']).__round__(2)

            dist_one.append(distance)

        distanceSummary.loc[len(distanceSummary)] = dist_one
    distanceSummary.index = station_index
    return distanceSummary

def calculateDiff(stations_info, data):
    row_count = stations_info.shape[0]
    station_index = list(stations_info['Station'])
    diff_summary = pd.DataFrame(columns=station_index)
    for one_stn in range(0, row_count):
        diff_one = []
        for other_stn in range(0, row_count):
            diff = abs(data.iloc[:, 0][station_index[one_stn]] -
                                data.iloc[:, 0][station_index[other_stn]])
            diff_one.append(diff)

        diff_summary.loc[len(diff_summary)] = diff_one
    diff_summary.index = station_index
    return diff_summary

def replaceDiff(stations_info, data, tolerance, rep1, rep2):
    row_count = stations_info.shape[0]
    station_index = list(stations_info['Station'])
    i = 1
    #print(tolerance)
    for one_stn in range(0, row_count):
        diff_one_rep = data.loc[:,[station_index[one_stn]]]
        diff_one_rep[station_index[one_stn]] = np.where(diff_one_rep[station_index[one_stn]] <= tolerance,rep1,
                                                        diff_one_rep[station_index[one_stn]])
        diff_one_rep[station_index[one_stn]] = np.where(diff_one_rep[station_index[one_stn]] > tolerance,rep2,
                                                        diff_one_rep[station_index[one_stn]])
        if (i == 1):
            diff_summary_rep = diff_one_rep
        else:
            diff_summary_rep = diff_summary_rep.join(diff_one_rep)
        i = 2
    return diff_summary_rep

def stationSelection(stations_info, stations_score):
    row_count = stations_info.shape[0]
    station_index = list(stations_info['Station'])
    filling_stations = pd.DataFrame()
    for one_stn in range(0, row_count):
        score_one = stations_score.loc[:,[station_index[one_stn]]]
        sort_score = score_one.sort_values(by = [station_index[one_stn]], ascending = False)
        eligible_stns = list(sort_score.index.values)
        eligible_stns.remove(station_index[one_stn])
        eligible_stns = eligible_stns[0:5]
        filling_stations[station_index[one_stn]] = eligible_stns
    return filling_stations


def fillStationSelect(stations_info, normal_rainfall):
    print('Selecting filling stations for Normal Ration Method!')
    
    normal_rainfall.index = normal_rainfall['Station']
    normal_rainfall = normal_rainfall.drop(columns = 'Station')

    distance_matrix = distBetStations(stations_info) #calculating distance between stations
    diff_nrainfall = calculateDiff(stations_info, normal_rainfall) #difference between normall rainfall of stations

    # extraction elevation from stations_info
    stations_elev = stations_info.loc[:, ['Station', 'RL']]
    stations_elev.index = stations_elev['Station']
    stations_elev = stations_elev.drop(columns ='Station')
    #difference between stations elevation
    diff_elev = calculateDiff(stations_info, stations_elev)

    #assinging score based on difference criteria
    diff_elev_score = replaceDiff(stations_info, diff_elev, 400, 1, 0)
    diff_nrainfall_score = replaceDiff(stations_info, diff_nrainfall, 300, 1, 0)
    diff_distance_score = replaceDiff(stations_info, distance_matrix, 50, 0.5, 0)

    #total score
    combined_score = diff_nrainfall_score + diff_elev_score + diff_distance_score

    #station selected for filling missing data
    selected_stations = stationSelection(stations_info, combined_score)
    return selected_stations

#stations = fillStationSelect(stations_info = stations_info,normal_rainfall = normal_rainfall)

#stations.to_csv('selected stations.csv')

