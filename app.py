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
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation  (Last 12 month)</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations  ( List of Stations)</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs   (Date and Temperature of most Active Stations previous year)</a><br/>"
        f"<a href='/api/v1.0/start-end'>/api/v1.0/start-end  (MIN,AVG,MAX temperature)</a><br/>"
    )

#2
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

    

#3
@app.route('/api/v1.0/stations')
def stations():
    # Query distinct station IDs
    station_ids = session.query(measurement.station).distinct().all()

    # Convert the query results into a list
    stations_list = [station_id[0] for station_id in station_ids]

    # Return the JSON representation of the list
    return jsonify(stations_list)


#4
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



#5
@app.route('/api/v1.0/start-end')
def start_end():
    """Retrieve the TMIN, TAVG, and TMAX for a specified start and end date"""

    # Specify the start and end dates
    start_date = '2017-04-21'
    end_date = '2017-06-23'

    # Query to retrieve TMIN, TAVG, and TMAX for the specified date range
    temp_stats = session.query(func.min(measurement.tobs),
                               func.avg(measurement.tobs),
                               func.max(measurement.tobs)).\
        filter(measurement.date >= start_date,
               measurement.date <= end_date).all()

    # Close the session
    session.close()

    # Extract the temperature statistics from the query results
    tmin, tavg, tmax = temp_stats[0]

    # Construct the JSON response
    response = {
        "start_date": start_date,
        "end_date": end_date,
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    }

    # Return the JSON response
    return jsonify(response)




if __name__ == '__main__':
    app.run(debug=True)
