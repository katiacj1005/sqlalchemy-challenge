# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime as dt, timedelta
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# 1. Generate the engine to the correct sqlite file:
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# 2. Use automap_base() and reflect the database schema:
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)
print(Base.classes.keys())

# 3. Save references to the tables in the sqlite file (measurement and station):
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# 4. Create and bind the session between the Python app and database:
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# 5. Display the available routes on the landing page:
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"1. /api/v1.0/precipitation<br/>"
        f"2. /api/v1.0/stations<br/>"
        f"3. /api/v1.0/tobs<br/>"
        f"4. /api/v1.0/&lt;start&gt;<br/>"
        f"5. /api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the most recent date in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()

    # Calculate the date one year ago from the most recent date
    one_year_ago = dt.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)
    
    # Query precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Convert query results to a dictionary with date as key and precipitation as value
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)



@app.route("/api/v1.0/stations")
def get_stations():
    # Query to retrieve list of stations
    results = session.query(Station.station).all()
    
    # Convert query results to a list
    stations = [result[0] for result in results]
    
    # Return the JSON list of stations
    return jsonify(stations)



@app.route("/api/v1.0/tobs")
def get_temperatures():

    # Query the most active station ID
    most_active_station_id = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0] #the [0] is used to access the first element of the result tuple returned by the query.
    
    # Query the most recent date in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()

    # Calculate the date one year ago from the most recent date
    one_year_ago = dt.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)

    # Query temperature observations for the most active station for the previous year
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == most_active_station_id).\
            filter(Measurement.date >= one_year_ago).\
            all()
    
    # Convert query results to a list of dictionaries
    tobs_list = [{"Date": date, "Temperature": tobs} for date, tobs in tobs_data]

    return jsonify(tobs_list)



@app.route("/api/v1.0/<start>")
def calc_temps_start(start):
    # Query the minimum, average, and maximum temperatures for dates greater than or equal to the start date
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            all()

    # Extract the temperature statistics from the query result
    min_temp = temp_data[0][0] # Accesses the minimum temp from the temp_data
    avg_temp = temp_data[0][1] # Accesses the avg temp from the temp_data
    max_temp = temp_data[0][2] # Accesses the max temp from the temp_data

    # Convert query results to a dictionary
    temp_dict = {"Minimum Temperature": min_temp, "Average Temperature": avg_temp, "Maximum Temperature": max_temp}

    return jsonify(temp_dict)



@app.route("/api/v1.0/<start>/<end>")
def calc_temps_start_end(start, end):
    # Query the minimum, average, and maximum temperatures for dates between the start and end dates
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).\
            all()
    # Extract the temperature statistics from the query result
    min_temp = temp_data[0][0]
    avg_temp = temp_data[0][1]
    max_temp = temp_data[0][2]

    # Create a dictionary to hold the temperature statistics
    temp_dict = {"Minimum Temperature": min_temp, "Average Temperature": avg_temp, "Maximum Temperature": max_temp}

    return jsonify(temp_dict)

if __name__ == "__main__":
    app.run(debug=True)