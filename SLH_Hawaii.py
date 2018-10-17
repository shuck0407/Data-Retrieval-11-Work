import numpy as np
import pandas as pd
import datetime as dt
from datetime import timedelta, datetime
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f" Retrieves precipitation and temp for all weather stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"Returns a list of weather stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Returns a list of Temperature Observations (tobs) for the previous year<br/>"
        f"<br/>"
        f"/api/v1.0/startdate/<start><br/>"
        f"If you enter a start date (format YYYY-MM-DD) it returns a JSON list of the minimum,<br/>"
        f"  maximum and average temp for that date.<br/>"
        f"<br/>"
        f"/api/v1.0/startend/<start>/<end><br/>"
        f"Enter a start date and an end date (format YYYY-MM-DD) and it returns a JSON list of the <br/>"
        f" minimum, maximum and average temps between those dates.")

@app.route("/api/v1.0/precipitation")
def precipitation():

    results = engine.execute('SELECT max(date) from Measurement').fetchall()

    max_date = results[0][0]    

    end_date = datetime.strptime(max_date, '%Y-%m-%d').date()
    first_date = end_date - dt.timedelta(days=365)
    first_date = datetime.strftime(first_date, '%Y-%m-%d')

    precip_results = session.query(Measurement.date, Measurement.station, Measurement.prcp, Measurement.tobs).\
                     filter(Measurement.date > first_date).\
                     filter(Measurement.date < end_date).\
                     order_by(Measurement.date).all()


    # Create a dictionary from the row data and append to a list of all_passengers

    precip_12_months = []

    for x in precip_results:
        precip_dict = {}
        precip_dict["date"] = x.date
        precip_dict["station"] = x.station
        precip_dict["prcp"] = x.prcp
        precip_dict["tobs"] = x.tobs

        precip_12_months.append(precip_dict)

    return jsonify(precip_12_months)

@app.route("/api/v1.0/stations")
def stations():
    unique_stations = engine.execute(
    'SELECT DISTINCT Measurement.station FROM Measurement ORDER BY Measurement.station').fetchall()

    all_stations = []

    for station in unique_stations:
        station_dict = {}
        station_dict["station"] = station.station
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    results = engine.execute('SELECT max(date) from Measurement').fetchall()

    max_date = results[0][0]    

    end_date = datetime.strptime(max_date, '%Y-%m-%d').date()
    first_date = end_date - dt.timedelta(days=365)
    first_date = datetime.strftime(first_date, '%Y-%m-%d')

    tobs_results = session.query(Measurement.date, Measurement.tobs).\
                     filter(Measurement.date > first_date).\
                     filter(Measurement.date < end_date).\
                     order_by(Measurement.date).all()

    temps = []
    for temp in tobs_results:
        row = {}
        row["date"] = temp[0]
        row["tobs"] = temp[1]
        temps.append(row)

    return jsonify(temps)

@app.route("/api/v1.0/startdate/<start>")
def startdate_start(start):

    t = "SELECT MIN(Measurement.tobs), MAX(Measurement.tobs), AVG(Measurement.tobs) FROM Measurement WHERE  Measurement.date = :x"

    start_date_results = engine.execute(t, x=start).fetchall()

    start_stats = []
    for stat in start_date_results:
        row = {}
        row["minimum"] = stat[0]
        row["maximum"] = stat[1]
        row["average"] = round(stat[2], 2)
        start_stats.append(row)

    return jsonify(start_stats)

@app.route("/api/v1.0/startend/<start>/<end>")
def startend_start_end(start, end):

    t = "SELECT MIN(Measurement.tobs), MAX(Measurement.tobs), AVG(Measurement.tobs) FROM Measurement WHERE  Measurement.date > :x AND Measurement.date < :y"

    start_end_results = engine.execute(t, x=start, y=end).fetchall()

    start_end_stats = []
    for stat in start_end_results:
        row = {}
        row["minimum"] = stat[0]
        row["maximum"] = stat[1]
        row["average"] = round(stat[2], 2)
        start_end_stats.append(row)

    return jsonify(start_end_stats)


if __name__ == '__main__':
    app.run(debug=True)