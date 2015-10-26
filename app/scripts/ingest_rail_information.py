import httplib, urllib, base64, ast

from datetime import datetime

import sys
sys.path.append("../../")

from app import cred

from app import models
from app import db

import constants

headers = {
    # Request headers
    'api_key': cred.API_KEY,
}

params = urllib.urlencode({
    # Request parameters
    'Route': '{string}',
})


def connect_wmata(url):
    conn = httplib.HTTPSConnection('api.wmata.com')
    #conn.request("GET", "/Incidents.svc/json/BusIncidents&%s" % params, "{body}", headers)
    conn.request("GET", url, "{body}", headers)
    response = conn.getresponse()
    results = response.read()
    conn.close()
    results = results.replace("null", "None")
    data = ast.literal_eval(results)
    return data

def ingest_rail():
    data = connect_wmata("/Rail.svc/json/jLines")
    for line in data["Lines"]:
        try:
            linemodel = models.Line()
            linemodel.display_name = line["DisplayName"]
            linemodel.start_station = line["StartStationCode"]
            linemodel.end_station = line["EndStationCode"]
            linemodel.line_code = line["LineCode"]
            linemodel.internal_destination_1 = line["InternalDestination1"]
            linemodel.internal_destination_2 = line["InternalDestination2"]
            db.session.add(linemodel)
        except Exception as e:
            print(e)
    db.session.commit()


def ingest_station():
    data = connect_wmata("/Rail.svc/json/jStations")
    together = {}
    for station in data["Stations"]:
        try:
            address = models.Address()
            adata = station["Address"]
            address.city = adata["City"]
            address.state = adata["State"]
            address.street = adata["Street"]
            address.postal_code = adata["Zip"]
            db.session.add(address)
            db.session.commit()
            stationmodel = models.Station()
            stationmodel.address = address.id
            stationmodel.code = station["Code"]
            stationmodel.lat = station["Lat"]
            stationmodel.lon = station["Lon"]
            stationmodel.line_code_1 = station["LineCode1"]
            stationmodel.line_code_2 = station["LineCode2"]
            stationmodel.line_code_3 = station["LineCode3"]
            stationmodel.line_code_4 = station["LineCode4"]
            stationmodel.name = station["Name"]
            #stationmodel.station_togeter_1 = station["StationTogether1"]
            #stationmodel.station_togeter_2 = station["StationTogether2"]
            station1 = station["StationTogether1"]
            station2 = station["StationTogether2"]
            if station1 is not None or station2 is not None:
                if stationmodel.code not in together:
                    together[stationmodel.code] = set()
                if station1 is not None:
                    together[stationmodel.code].add(station1)
                if station2 is not None:
                    together[stationmodel.code].add(station2)
            db.session.add(stationmodel)
        except Exception as e:
            print(e)
    db.session.commit()
    for station in together:
        for station2 in together[station]:
            if len(station2) > 0:
                tmodel = models.StationTogether()
                tmodel.station1 = station
                tmodel.station2 = station2
                db.session.add(tmodel)
    db.session.commit()


def ingest_predictions():
    data = connect_wmata("/StationPrediction.svc/json/GetPrediction/All")
    for t in data["Trains"]:
        train = models.TrainPrediction()
        train.time = str(datetime.now())
        train.cars = t["Car"]
        train.destination = t["Destination"]
        if t["DestinationCode"] is not None:
            train.destination_code = t["DestinationCode"]
        train.destination_name = t["DestinationName"]
        train.group = t["Group"]
        if t["Line"] is not None and t["Line"] != "No" and t["Line"] != "--":
            train.line = t["Line"]
        train.location_code = t["LocationCode"]
        train.location_name = t["LocationName"]
        train.minutes = t["Min"]
        db.session.add(train)
    db.session.commit()


def ingest_distances():
    station_codes = get_station_codes()
    # Loop through each line and determine the distance between each station
    data = connect_wmata("/Rail.svc/json/jSrcStationToDstStationInfo")
    for d in data["StationToStationInfos"]:
        s2s = models.StationToStation()
        s2s.source = d["SourceStation"]
        s2s.destination = d["DestinationStation"]
        s2s.miles = d["CompositeMiles"]
        s2s.offpeak = d["RailFare"]["OffPeakTime"]
        s2s.senior = d["RailFare"]["SeniorDisabled"]
        s2s.peak = d["RailFare"]["PeakTime"]
        s2s.time = d["RailTime"]
        db.session.add(s2s)
    db.session.commit()


def find_trip_distances():
    station_codes = get_station_codes()
    red = constants.RED_LINE
    orange = constants.ORANGE_LINE
    silver = constants.SILVER_LINE
    blue = constants.BLUE_LINE
    yellow = constants.YELLOW_LINE
    yellow_rush = constants.YELLOW_LINE_RUSH
    green = constants.GREEN_LINE
    lines = [red, orange, silver, blue, yellow, yellow_rush, green]
    for line in lines:
        find_line_distances(line, station_codes)
        find_line_distances(list(reversed(line)), station_codes)


def find_line_distances(line, station_codes):
    for stationint in xrange(len(line)):
        station = station_codes[line[stationint]]
        if stationint != 0:
            previous = station_codes[line[stationint-1]]
            tbs = find_distance(previous, station)
            if tbs is not None:
                db.session.add(tbs)
        if stationint + 1 != len(line):
            next = station_codes[line[stationint+1]]
            tbs = find_distance(next, station)
            if tbs is not None:
                db.session.add(tbs)
    db.session.commit()


def find_distance(previous, station):
    tbs = models.TimeBetweenStations()
    if type(station) == type([]):
        station = station[0]
    if type(previous) == type([]):
        previous = previous[0]
    station = models.Station.query.get(station)
    previous = models.Station.query.get(previous)
    existing = models.TimeBetweenStations.query\
        .filter(models.TimeBetweenStations.station==station.code,
            models.TimeBetweenStations.previous_station==previous.code)
    if len(existing.all()) == 0:
        tbs.station = station.code
        tbs.previous_station = previous.code
        pcode = previous.code
        scode = station.code
        s2ss = models.StationToStation.query.\
            filter(models.StationToStation.source==scode,
                models.StationToStation.destination==pcode)
        for s2s in s2ss.all():
            tbs.distance = s2s.miles
            tbs.time = s2s.time
        return tbs


def get_station_codes(reverse=False):
    # Get the order of the stations
    red = constants.RED_LINE
    orange = constants.ORANGE_LINE
    silver = constants.SILVER_LINE
    blue = constants.BLUE_LINE
    yellow = constants.YELLOW_LINE
    yellowrush = constants.YELLOW_LINE_RUSH
    green = constants.GREEN_LINE
    # Get the codes for the stations
    station_codes = {}
    lines = [red, orange, silver, blue, yellow, yellowrush, green]
    for line in lines:
        station_codes = find_station_codes(line, station_codes)
    if reverse is False:
        return station_codes
    else:
        rev = {}
        for key in station_codes:
            for val in station_codes[key]:
                if val not in rev:
                    rev[str(val)] = str(key)
                else:
                    print "UH OH"
        return rev


def find_station_codes(line, station_codes):
    for station in line:
        if station not in station_codes:
            try:
                found = models.Station.query.filter(models.Station.name==station).all()
                if len(found) > 0:
                    station_codes[str(station)] = [str(x) for x in found]
                else:
                    print(station)
            except Exception as e:
                print e
    return station_codes



if __name__ == "__main__":
    #ingest_rail()
    #ingest_station()
    #ingest_predictions()
    #ingest_distances()
    find_trip_distances()
