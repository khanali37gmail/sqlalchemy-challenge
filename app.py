# Import the dependencies.
import numpy as np
import datetime as dt
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
Base.prepare(autoload_with=engine)


# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station


# Create our session (link) from Python to the DB

session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

#1)start homepage / list all the avaliable routes



app = Flask(__name__)

# Route to display all available routes
@app.route('/')
def home():
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

#1
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year ago from the most recent date
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago).all()

    # Convert results to dictionary
    precipitation_dict = {}
    for date, prcp in results:
        precipitation_dict[date] = prcp

    return jsonify(precipitation_dict)

    

#2
@app.route('/api/v1.0/stations')
def stations():
    # Query distinct station IDs
    station_ids = session.query(measurement.station).distinct().all()

    # Convert the query results into a list
    stations_list = [station_id[0] for station_id in station_ids]

    # Return the JSON representation of the list
    return jsonify(stations_list)


#3
@app.route('/api/v1.0/tobs')
def tobs():
    # Determine the most-active station
    most_active_station = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count().desc()).first()[0]

    # Calculate the date one year ago from the most recent date
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the dates and temperature observations for the most-active station for the previous year
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).\
        filter(measurement.date >= one_year_ago).all()
    
 # Convert the query results into a list of dictionaries
    temperature_data = [{'Date': date, 'Temperature': tobs} for date, tobs in results]

    # Return the JSON representation of the list
    return jsonify(temperature_data)







if __name__ == '__main__':
    app.run(debug=True)
