import httplib, urllib, base64, ast

from datetime import datetime

import sys
sys.path.append("../../")

from app import cred

from app import models
from app import db

import constants

from ingest_rail_information import get_station_codes, connect_wmata

from sqlalchemy import distinct, func

headers = {
    # Request headers
    'api_key': cred.API_KEY,
}

params = urllib.urlencode({
    # Request parameters
    'Route': '{string}',
})


def ingest_predictions():
    data = connect_wmata("/StationPrediction.svc/json/GetPrediction/All")
    now = datetime.now()
    for t in data["Trains"]:
        train = models.TrainPrediction()
        train.time = str(now)
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


def trains_running():
    lines = {
        "RD": constants.RED_LINE,
        "OR": constants.ORANGE_LINE,
        "YL": constants.YELLOW_LINE,
        "SV": constants.SILVER_LINE,
        "BL": constants.BLUE_LINE,
        "GR": constants.GREEN_LINE,
        "YL-ALT": constants.YELLOW_LINE_RUSH
    }
    station_codes = get_station_codes(reverse=True)
    maxid = 0
    for value in db.session.query(func.max(models.TrainPrediction.id)):
        maxid = value[0]
    lasttrain = models.TrainPrediction.query.filter(models.TrainPrediction.id==maxid)
    date = lasttrain[0].time
    alltrains = models.TrainPrediction.query.filter(models.TrainPrediction.time==date)
    # Key will be station|destination
    previous = {}
    trains = []
    for train in alltrains:
        location_code = train.location_code
        destination_code = train.destination_code
        line = train.line
        pstations = None
        if location_code is not None and destination_code is not None and \
                location_code + "|" + destination_code not in previous:
            if line in lines:
                pstations = find_on_line(lines, line, station_codes,
                    location_code, destination_code)
            previous[location_code + "|" + destination_code] = pstations
        elif location_code is not None and destination_code is not None:
            pstation = previous[location_code + "|" + destination_code]
        if pstations is not None:
            distance = []
            locname = models.Station.query.get(location_code).name
            locations = models.Station.query.filter(models.Station.name==locname)
            for pstation in pstations:
                for loc in locations:
                    tdistance = db.session.query(models.TimeBetweenStations)\
                        .filter(models.TimeBetweenStations.station==str(loc.code),
                            models.TimeBetweenStations.previous_station==str(pstation.code)).all()
                    if len(tdistance) > 0:
                        distance = tdistance
                        break
            if len(distance) == 0:
                trains.append(train)
            else:
                for d in distance:
                    try:
                        if float(train.minutes) - d.time < 0.0:
                            trains.append(train)
                    except:
                        if str(train.minutes) == "ARR" or str(train.minutes) == "BRD":
                            trains.append(train)
    print(len(trains))



def find_on_line(lines, line, station_codes, location_code, destination_code):
    before = False
    next = False
    pstation = None
    found = False
    location = station_codes[location_code]
    destination = station_codes[destination_code]
    revert = get_station_codes()
    final_line = None
    if location in lines[line] and destination in lines[line]:
        final_line = line
    else:
        found = False
        for altline in lines:
            if location in lines[altline] and destination in lines[altline]:
                found = True
                final_line = altline
                break
    locindex = lines[final_line].index(location)
    destindex = lines[final_line].index(destination)
    if locindex > destindex:
        pstation = lines[final_line][locindex+1]
    else:
        pstation = lines[final_line][locindex-1]
    return models.Station.query.filter(models.Station.name==pstation).all()



if __name__ == "__main__":
    trains_running()