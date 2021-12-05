#imports
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.pool import StaticPool
import datetime as dt
from flask import Flask, jsonify

 # create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
#reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)
 # Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#create app
app = Flask(__name__)

#flask routes
@app.route("/")
def home():
    return (
        f'Weather Data:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f"/api/v1.0/start(yyyy-mm-dd)<br/>"
        f"/api/v1.0/start(yyyy-mm-dd)/end(yyyy-mm-dd)<br/>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #date range
    # Convert query results to a dictionary using date as the key and prcp as the value
    # Return the JSON representation of your dictionary
    date_minus_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    date_minus_year 
    # Perform a query to retrieve the date and precipitation 
    data = session.query(Measurement.date, func.avg(Measurement.prcp)).\
            filter(Measurement.date.between (date_minus_year, dt.date(2017, 8, 23))).group_by('date')
    # Close Session
    session.close()
     #convert data into a dicionary
    precipitation_data = []
    for date, prcp in data:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation (in)"] = round(prcp,3)
        precipitation_data.append(prcp_dict)
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #retrieve station names
    active_stations = session.query(Station.station, Station.name).all()
  # Close Session
    session.close()
    #convert data into a dicionary
    station_data = []
    for station, name in active_stations:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_data.append(station_dict)

    return jsonify(station_data)

#temp obv data ("TOB")
# Using the most active station id
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #date range - last 12 months
    # Convert query results to a dictionary using date as the key and prcp as the value
    # Return the JSON representation of your dictionar
    date_minus_year = dt.date(2017, 8, 23) - dt.timedelta(days=365*1)
    date_minus_year 
    # Perform a query to retrieve the date and temp 
    data = session.query(Measurement.date, func.avg(Measurement.tobs)).\
    filter(Measurement.station == "USC00519281").filter(Measurement.date.between (date_minus_year, dt.date(2017, 8, 23))).group_by('date')
    # Close Session
    session.close()
    #convert data
    tobs_data = []
    for date, tobs in data:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperature (F)"] = round(tobs, 2)
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

#step 2 - Climate App; Used Flask to create routes
@app.route("/api/v1.0/<start_date>")
def start(start_date):
    date_temp = []
    if len(start_date) == 10:
        # Create our session (link) from Python to the DB
        session = Session(engine)
        # query TMIN, TAVG, and TMAX from the start and end date
        tobs_calc = session.query(Measurement.date.label("Date"), func.min(Measurement.tobs).label("TMIN"),\
        func.avg(Measurement.tobs).label("TAVG"), func.max(Measurement.tobs).label("TMAX")).\
        filter(Measurement.date >= start_date).\
        group_by(Measurement.date).all()
       # Close Session
        session.close()
        #insert temp data into list
        for t in tobs_calc:
            date_temp.append(f'Start date: {t.Date}, min temperature:{t.TMIN}, avg temperature:{round(t.TAVG,2)}, max temperature: {t.TMAX}')
    else:
       date_temp.append(f'Please use YYYY-MM-DD format to return results.')
    return jsonify(date_temp)

#flask route
@app.route("/api/v1.0/<start_date>/<end_date>")
def range(start_date,end_date):
    #When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    date_temp = []
    if len(start_date) == 10 and len(end_date) == 10 :
       # Create our session (link) from Python to the DB
        session = Session(engine)
        # Perform a query to retrieve the temp data 
        tobs_calc = session.query(Measurement.date.label("Date"), func.min(Measurement.tobs).label("TMIN"),\
        func.avg(Measurement.tobs).label("TAVG"), func.max(Measurement.tobs).label("TMAX")).\
        filter(Measurement.date.between(start_date,end_date)).\
        group_by(Measurement.date).all()
        # Close Session
        session.close()
    
        for t in tobs_calc:
            date_temp.append(f'Start date: {t.Date}, min temperature:{t.TMIN}, avg temperature:{round(t.TAVG,2)}, max temperature: {t.TMAX}')       
    else:
        date_temp.append(f'Excuse me, error! Use the appropriate date formatting! (YYYY-MM-DD). Thank you!')
    return jsonify(date_temp)

if __name__ == "__main__":
    app.run(debug=True)


#hint: Use Flask jsonify to convert your API data into a valid JSON response object.