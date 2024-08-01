# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import pandas as pd
import datetime as dt


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine('sqlite:///hawaii.sqlite')

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# Home route
@app.route('/')
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

# Precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_datetime = pd.to_datetime(most_recent_date)
    one_year_ago = most_recent_datetime - pd.DateOffset(years=1)
    one_year_ago_str = one_year_ago.strftime('%Y-%m-%d')

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago_str).all()
    session.close()

    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

# Stations route
@app.route('/api/v1.0/stations')
def stations():
    results = session.query(Station.station).all()
    session.close()

    stations = [station[0] for station in results]
    return jsonify(stations)

# TOBS route
@app.route('/api/v1.0/tobs')
def tobs():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_datetime = pd.to_datetime(most_recent_date)
    one_year_ago = most_recent_datetime - pd.DateOffset(years=1)
    one_year_ago_str = one_year_ago.strftime('%Y-%m-%d')

    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago_str).all()
    session.close()

    tobs_data = {date: tobs for date, tobs in results}
    return jsonify(tobs_data)

# Start route
@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)
    results = session.query(
        func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()
    session.close()

    temps = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    return jsonify(temps)

# Start-End route
@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    session = Session(engine)
    results = session.query(
        func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temps = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)