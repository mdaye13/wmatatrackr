from app import db

class RailIncident(db.Model):
    incident_id = db.Column(db.Integer, primary_key=True)
    date_updated = db.Column(db.String)
    description = db.Column(db.String)
    incident_type = db.Column(db.String)
    LinesAffected = db.Column(db.String)

    def __repr__(self):
        return incident_id


class Line(db.Model):
    line_code = db.Column(db.String, primary_key=True)
    display_name = db.Column(db.String)
    start_station = db.Column(db.String)
    end_station = db.Column(db.String)
    internal_destination_1 = db.Column(db.String)
    internal_destination_2 = db.Column(db.String)


class Station(db.Model):
    code = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.Integer, db.ForeignKey('address.id'))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    line_code_1 = db.Column(db.String, db.ForeignKey('line.line_code'))
    line_code_2 = db.Column(db.String, db.ForeignKey('line.line_code'))
    line_code_3 = db.Column(db.String, db.ForeignKey('line.line_code'))
    line_code_4 = db.Column(db.String, db.ForeignKey('line.line_code'))

    def __repr__(self):
        return self.code


class StationTogether(db.Model):
    station1 = db.Column(db.String, db.ForeignKey('station.code'), primary_key=True)
    station2 = db.Column(db.String, db.ForeignKey('station.code'), primary_key=True)


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String)
    state = db.Column(db.String)
    street = db.Column(db.String)
    postal_code = db.Column(db.String)


class TrainPrediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String)
    cars = db.Column(db.Integer)
    destination = db.Column(db.String)
    destination_code = db.Column(db.String, db.ForeignKey('station.code'))
    destination_name = db.Column(db.String)
    group = db.Column(db.String)
    line = db.Column(db.String, db.ForeignKey('line.line_code'))
    location_code = db.Column(db.String, db.ForeignKey('station.code'))
    location_name = db.Column(db.String)
    minutes = db.Column(db.String)


class StationToStation(db.Model):
    source = db.Column(db.String, db.ForeignKey('station.code'), primary_key=True)
    destination = db.Column(db.String, db.ForeignKey('station.code'), primary_key=True)
    offpeak = db.Column(db.Float)
    senior = db.Column(db.Float)
    peak = db.Column(db.Float)
    miles = db.Column(db.Float)
    time = db.Column(db.Float)


class TimeBetweenStations(db.Model):
    """The reported time to a station from each of it's neighbor
     stations on a line"""
    station = db.Column(db.String, db.ForeignKey('station.code'),
        primary_key=True)
    previous_station = db.Column(db.String, db.ForeignKey('station.code'),
        primary_key=True)
    distance = db.Column(db.Float)
    time = db.Column(db.Float)
