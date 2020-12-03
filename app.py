import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Setup Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Engine
session = Session(engine)

# Setup Flask app
app = Flask(__name__)

# Setup Flask Routes
@app.route("/")
def homepage():
    """List of all returnable API routes."""
    return(
        f"Welcome to my Hawaiian Vacation Weather API<br/>"
        f"(Note: The most recent available date is 2017-08-23 while the earliest is 2010-01-01).<br/>"
        f"<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- Returns a JSON list of precipitation levels for the prior year (2016-08-23 to 2017-08-23).  <br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- Returns a JSON list of stations. <br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- Returns a JSON list of Temperature Observations (tobs) for the prior year (2016-08-23 to 2017-08-23). <br/>"
        f"<br/>"
        f"/api/v1.0/yyyy-mm-dd/<br/>"
        f"- Returns an Average, Max, and Min temperature from the given date to the most recent available date (2017-08-23).<br/>"
        f"<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd/<br/>"
        f"- Returns an Aveage Max, and Min temperature for given period.<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return Dates and Precipitation from the last year."""
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= "2016-08-23").all()
    
    session.close()

    # Create the JSON objects
    precipitation_list = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation_list.append(precipitation_dict)

    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    # Query stations
    results = session.query(Station)

    # Create JSON results
    station_data = []
    for station in results:
        station_dict = {}
        station_dict["Station"] = station.station
        station_dict["Name"] = station.name
        station_data.append(station_dict)

    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def temp_obs():
    """Return a list of tobs for the year before the final date"""
    results = session.query(Station.name, Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= "2016-08-23").all()

    # Create JSON results
    tobs_list = []
    for result in results:
        row = {}
        row["Date"] = result[1]
        row["Station"] = result[0]
        row["Temperature"] = int(result[2])
        tobs_list.append(row)

    return jsonify(tobs_list)

@app.route('/api/v1.0/<date>/')
def given_date(date):
    """Return the average temp, max temp, and min temp for dates after start date"""
    results = session.query(Measurement.date, func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= date).all()

    # Create JSON results
    data_list = []
    for result in results:
        row = {}
        row['Start Date'] = date
        row['Average Temperature'] = float(result[1])
        row['Highest Temperature'] = float(result[2])
        row['Lowest Temperature'] = float(result[3])
        data_list.append(row)

    return jsonify(data_list)

@app.route('/api/v1.0/<start_date>/<end_date>/')
def query_dates(start_date, end_date):
    """Return the avg, max, min, temp over a specific time period"""
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    # Create JSON results   
    data_list = []
    for result in results:
        row = {}
        row["Start Date"] = start_date
        row["End Date"] = end_date
        row["Average Temperature"] = float(result[0])
        row["Highest Temperature"] = float(result[1])
        row["Lowest Temperature"] = float(result[2])
        data_list.append(row)
    return jsonify(data_list)


if __name__ == '__main__':
    app.run(debug=True)